import json
import config  
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import requests
from PIL import Image, ImageDraw, ImageFont
import qrcode

from config_loader import load_config

try:
    config = load_config() 

except RuntimeError as e: 
    print(e)
    exit(1)  # Exit the program immediately


class HomeScreen:
    def __init__(self, disp, example_d):
        self.disp = disp
        self.example_d = example_d
        self.wallet_data = self.load_wallet_data()

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
        print("Home L2 Wallet Screen")
        
        w3 = Web3(Web3.HTTPProvider(config.infura_url_L2))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        is_connected = w3.isConnected()
        block_number = w3.eth.blockNumber
        print('Connected:', is_connected, 'BlockNumber:', block_number)

        if not self.wallet_data:
            return self.render_error_screen("No ethereum wallet loaded yet")

        wallet = self.wallet_data.get("address")
        secret_key = self.wallet_data.get("private_key")

        # Set up image and drawing context
        brand_color = self.get_brand_color(config.L2_chainid)
        img = Image.new("RGBA", (240, 240), brand_color)
        draw = ImageDraw.Draw(img)

        # Add background image and wallet text
        self.add_background_image(img)
        self.add_wallet_text(draw, config.L2_name, wallet)

        # Get account balances
        acct = Account.from_key(secret_key)
        balance = w3.eth.getBalance(acct.address)
        eth_balance, token_balance = self.get_token_balances(w3, acct.address)

        # Get gas prices
        gas_prices = self.get_gas_prices()

        # Draw balance and gas information
        self.draw_balance_info(draw, balance, eth_balance, token_balance)
        self.draw_gas_info(draw, gas_prices)

        # Add QR code
        self.add_qr_code(img, wallet)

        # Add instruction to return to menu
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
        draw.text((70, 110), f"    {network_name} Wallet", fill="black", anchor="ms", font=font, stroke_width=1, stroke_fill='white')
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
 # Truncate the wallet address
        truncated_address = wallet_address[:8] + '...' + wallet_address[-4:]
        draw.text((120, 20), truncated_address, fill="black", anchor="ms", font=font)

    @staticmethod
    def get_token_balances(w3, address):
        eth_contract = w3.eth.contract(address=config.L2_weth_address, abi=config.L2_weth_contractABI)
        eth_balance = eth_contract.functions.balanceOf(address).call() / config.L2_token_decimal_output

        token_contract = w3.eth.contract(address=config.L2_token_address, abi=config.L2_token_contractABI)
        token_balance = token_contract.functions.balanceOf(address).call() / config.L2_token_decimal

        return eth_balance, token_balance

    @staticmethod
    def get_gas_prices():
        response = requests.get(config.api_L2_scan)
        data = json.loads(response.content)
        
        if "result" in data and "FastGasPrice" in data['result']:
            return data['result']['FastGasPrice']
        elif "result" in data:
            gas_price_wei = int(data['result'], 16)
            return round(gas_price_wei / 10**9, 2)
        else:
            return "N/A"

    @staticmethod
    def draw_balance_info(draw, native_balance, eth_balance, token_balance):
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        
        if config.L2_output_name == "ETH" and config.L2_chainid != "137":
            draw.text((60, 205), f"{config.L2_output_name}: {round(Web3.fromWei(native_balance, 'ether'), 5)}", fill="black", anchor="ms", font=font)
        else:
            draw.text((60, 205), f"{config.L2_output_name}: {round(eth_balance, 4)}", fill="black", anchor="ms", font=font)
        
        draw.text((60, 225), f"{config.L2_token_name}: {round(token_balance, 4)}", fill="black", anchor="ms", font=font)

    @staticmethod
    def draw_gas_info(draw, gas_price):
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        draw.text((170, 70), f"Gas {gas_price}", fill="white", anchor="ms", font=font)

    @staticmethod
    def add_qr_code(img, wallet_address):
        qr = qrcode.QRCode(border=1)
        qr.add_data(wallet_address)
        qr.make()
        qr_img = qr.make_image(fill_color="black", back_color="#FAF9F6")
        qr_img = qr_img.resize((110, 110))
        img.paste(qr_img, (130, 115))

    @staticmethod
    def add_return_instruction(draw):
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        draw.text((120, 235), "Press ← to return to menu", fill="black", anchor="ms", font=font)

