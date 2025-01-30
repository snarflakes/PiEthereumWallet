import os
import sys
import json
import config
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import requests
from PIL import Image, ImageDraw, ImageFont
import qrcode

def get_base_dir():
    """Get the directory where the executable/script is located"""
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # If running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_active_config_path():
    """Get the active chain directory and config file"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            if ':' not in content:
                print("Invalid format in active.txt")
                return None
            chain_dir, config_file = content.split(':')
            base_dir = get_base_dir()
            full_path = os.path.join(base_dir, chain_dir, config_file)
            if not os.path.exists(full_path):
                print(f"Config file not found: {full_path}")
                return None
            return full_path
    except FileNotFoundError:
        print("active.txt not found")
        return None
    except Exception as e:
        print(f"Error reading active.txt: {e}")
        return None

def load_config():
    config_path = get_active_config_path()
    if not config_path:
        raise RuntimeError("No active config found")
    
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return type('Config', (), config_data)()
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}")

class HomeScreen:
    def __init__(self, disp, example_d):
        self.disp = disp
        self.example_d = example_d
        self.wallet_data = self.load_wallet_data()
        try:
            self.config = load_config()
        except RuntimeError as e:
            print(e)
            exit(1)

    def load_wallet_data(self):
        try:
            with open("/mnt/sdcard/wallet.json", "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            print("Failed to read or parse wallet.json from SD card.")
            return None

    def render(self):
        if self.example_d[0] != 1:
            self.render_home_screen_l2()
        else:
            self.render_home_screen_eth()

    def render_home_screen_l2(self):
        # Set up image and drawing context
        brand_color = self.get_brand_color(self.config.L2_chainid)
        img = Image.new("RGBA", (240, 240), brand_color)
        draw = ImageDraw.Draw(img)

        # Create a cleaner layout with better spacing
        if not self.wallet_data:
            return self.render_error_screen("No ethereum wallet loaded yet")

        wallet = self.wallet_data.get("address")
        secret_key = self.wallet_data.get("private_key")

        # Get account data
        w3 = Web3(Web3.HTTPProvider(self.config.infura_url_L2))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        acct = Account.from_key(secret_key)
        balance = w3.eth.get_balance(acct.address)
        token1_balance, token2_balance = self.get_token_balances(w3, acct.address)
        gas_prices = self.get_gas_prices()

        # Draw network indicator at the top
        self.draw_network_indicator(draw, self.config.L2_name)
        
        # Draw wallet address with custom background
        self.draw_wallet_section(draw, wallet)
        
        # Draw balances in a card-like container
        self.draw_balance_card(draw, token1_balance, token2_balance)
        
        # Draw gas info in a subtle way
        self.draw_gas_info(draw, gas_prices)
        
        # Add QR code in a better position
        self.add_qr_code(img, wallet)
        
        # Add subtle navigation hint
        self.add_return_instruction(draw)

        self.disp.image(img.convert("RGB"))

    def render_home_screen_eth(self):
        # Implement Ethereum mainnet home screen here
        # This will be similar to render_home_screen_l2 but with Ethereum-specific details
        pass

    @staticmethod
    def render_error_screen(message):
        img = Image.new("RGB", (240, 240), "red")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        draw.text((120, 120), message, fill="black", anchor="ms", font=font)
        return img

    @staticmethod
    def get_brand_color(chain_id):
        colors = {
            "137": "#8247e5",  # Polygon
            "10": "red",       # Optimism
            "42161": "blue",   # Arbitrum
            "8453": "dodgerblue", #Base
        }
        return colors.get(chain_id, "white")

    @staticmethod
    def add_background_image(img):
        background = Image.open("nftydaze4.jpg").convert('RGBA')
        background = background.resize((50, 50))
        img.paste(background, (50, 50))

    @staticmethod
    def add_wallet_text(draw, network_name, wallet_address):
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 20)
        draw.text((70, 110), f"       {network_name} Wallet", fill="black", anchor="ms", font=font, stroke_width=1, stroke_fill='white')

        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
 # Truncate the wallet address
        truncated_address = wallet_address[:8] + '...' + wallet_address[-4:]
        draw.text((120, 20), truncated_address, fill="black", anchor="ms", font=font)

    def get_token_balances(self, w3, address):
        # List of native token names for different chains
        native_tokens = ["ETH", "MATIC", "POLY", "POLYGON"]
        
        # Get first token balance
        if self.config.L2_output_name.upper() in native_tokens:
            token1_balance = w3.eth.get_balance(address) / 10**18
        else:
            token1_contract = w3.eth.contract(address=self.config.L2_output_address, abi=self.config.L2_output_contractABI)
            token1_balance = token1_contract.functions.balanceOf(address).call() / self.config.L2_token_decimal_output

        # Get second token balance
        token2_contract = w3.eth.contract(address=self.config.L2_token_address, abi=self.config.L2_token_contractABI)
        token2_balance = token2_contract.functions.balanceOf(address).call() / self.config.L2_token_decimal

        return token1_balance, token2_balance

    def format_token_balance(self, balance, token_name):
        """Format token balance consistently based on token type"""
        if token_name.upper() == "WBTC":
            if balance < 0.00001:
                return f"{balance:.2e}"  # Only WBTC uses scientific notation for small amounts
            return f"{round(balance, 8)}"  # Normal BTC amounts with 8 decimals
        elif token_name.upper() in ["USDC", "USDT", "DAI"]:
            if balance == 0:
                return "0.0000"  # Show 4 decimal places even for zero
            return f"{balance:.4f}"  # Stablecoins show 4 decimals
        else:
            if balance == 0:
                return "0.00000"  # Show 5 decimal places even for zero
            return f"{balance:.5f}"  # All other tokens (including ETH/MATIC) show 5 decimals

    def get_gas_prices(self):
        response = requests.get(self.config.api_L2_scan)
        data = json.loads(response.content)

        if "result" in data and "FastGasPrice" in data['result']:
            return data['result']['FastGasPrice']
        elif "result" in data:
            gas_price_wei = int(data['result'], 16)
            return round(gas_price_wei / 10**9, 2)
        else:
            return "N/A"

    def draw_network_indicator(self, draw, network_name):
        """Draw network name in a pill-shaped container at the top"""
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        text_width = font.getlength(network_name)
        
        # Draw pill shape
        x1, y1 = 120 - (text_width/2 + 10), 5
        x2, y2 = 120 + (text_width/2 + 10), 25
        draw.rounded_rectangle([x1, y1, x2, y2], radius=10, fill="white", outline="black")
        
        # Draw network name
        draw.text((120, 15), network_name, font=font, fill="black", anchor="mm")

    def draw_wallet_section(self, draw, wallet_address):
        """Draw wallet address in a cleaner way"""
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        truncated_address = wallet_address[:6] + '...' + wallet_address[-4:]
        
        # Draw subtle background
        draw.rounded_rectangle([20, 35, 220, 65], radius=5, fill=(255, 255, 255, 180))
        draw.text((120, 50), truncated_address, font=font, fill="black", anchor="mm")

    def draw_balance_card(self, draw, token1_balance, token2_balance):
        """Draw balances in a card-like container with smaller size"""
        # Draw card background - reduced height from 75-145 to 75-125
        draw.rounded_rectangle([20, 75, 220, 125], radius=10, fill="white", outline="black")
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        
        # Format balances
        token1_display = self.format_token_balance(token1_balance, self.config.L2_output_name)
        token2_display = self.format_token_balance(token2_balance, self.config.L2_token_name)
        
        # Draw token names and balances with tighter spacing
        y_start = 85  # Slightly reduced from 90
        spacing = 20  # Reduced from 25
        
        for token_name, balance in [
            (self.config.L2_output_name, token1_display),
            (self.config.L2_token_name, token2_display)
        ]:
            draw.text((35, y_start), token_name, font=font, fill="black", anchor="lm")
            draw.text((205, y_start), balance, font=font_bold, fill="black", anchor="rm")
            y_start += spacing

    def draw_gas_info(self, draw, gas_price):
        """Draw gas information to the left of QR code"""
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        text = f"Gas:\n{gas_price}\nGwei"
        # Positioned to the left of the QR code
        draw.text((20, 175), text, font=font, fill="black", anchor="lm", align="center")

    def add_qr_code(self, img, wallet_address):
        """Add larger QR code"""
        qr = qrcode.QRCode(border=1)
        qr.add_data(wallet_address)
        qr.make()
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((110, 110))  # Increased from 80x80
        
        # Create circular mask for rounded corners
        mask = Image.new('L', (110, 110), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, 109, 109], radius=10, fill=255)
        
        # Apply mask and paste
        output = Image.new('RGBA', (110, 110), (0, 0, 0, 0))
        output.paste(qr_img, (0, 0))
        output.putalpha(mask)
        
        # Centered horizontally, moved up slightly due to smaller balance card
        img.paste(output, (65, 130), output)

    def add_return_instruction(self, draw):
        """Add subtle navigation hint"""
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        draw.text((230, 230), "← Menu", font=font, fill="black", anchor="rm")
