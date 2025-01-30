import time
import qrcode
from web3 import Web3
from eth_account import Account
from uniswap import Uniswap
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from web3.middleware import geth_poa_middleware
from config_loader import load_config

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

def check_gas_balance(w3, wallet_address, chain_id):
    config = load_config()
    balance = w3.eth.get_balance(wallet_address)
    
    # Define minimum gas amount (in wei)
    min_gas = w3.to_wei(0.00001, 'ether')  # Adjust this value as needed
    
    if balance < min_gas:
        if chain_id in [1, 10, 42161, 8453]:  # Ethereum, Optimism, Arbitrum, Base
            gas_token = "ETH"
        elif chain_id in [137, 80001]:  # Polygon mainnet or testnet
            gas_token = "POL/MATIC"
        else:
            gas_token = "gas token"
        
        return False, f"Insufficient {gas_token} for gas"
    
    return True, None

def display_message(disp, message, is_error=False):
    background_color = "orange" if is_error else "white"
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    im = Image.new("RGB", (240, 240), background_color)
    d = ImageDraw.Draw(im)
    
    # Split the message into words
    words = message.split()
    lines = []
    current_line = []
    
    for word in words:
        if d.textsize(' '.join(current_line + [word]), font=font)[0] <= 220:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total height of text
    total_height = len(lines) * 20  # Assuming 20 pixels per line
    
    # Calculate starting y position to center the text vertically
    start_y = (240 - total_height) // 2
    
    y_position = start_y
    for line in lines:
        d.text((120, y_position), line, fill="black", anchor="mm", font=font)
        y_position += 20
    
    disp.image(im)
    time.sleep(10)  # Display the message for 10 seconds

def swap_tokens(disp, wallet_address, private_key, from_token, to_token, w3):
    amount = 0
    balance = 0
    try:
        # Load config without specifying path - it will use active.txt
        config = load_config()
        if config is None:
            display_message(disp, "Config Error\nFailed to load configuration", is_error=True)
            return None

        uniswap = Uniswap(wallet_address, private_key, version=3, provider=config.infura_url_L2, web3=w3)
        
        # Determine if the input token is native (ETH/MATIC)
        is_native_input = from_token.lower() == '0x0000000000000000000000000000000000000000'
        
        # Determine which token is being used as input (original input token or output token)
        is_output_token_as_input = from_token.lower() == config.L2_output_address.lower()
        
        # Check balance using appropriate ABI based on which token is being used as input
        if is_native_input:
            balance = w3.eth.get_balance(wallet_address)
        else:
            if is_output_token_as_input:
                # Using output token as input, so use output token ABI
                token_contract = w3.eth.contract(address=from_token, abi=config.L2_output_contractABI)
                balance = token_contract.functions.balanceOf(wallet_address).call()
                token_name = config.L2_output_name
                token_decimal = config.L2_token_decimal_output
            else:
                # Using input token as input, so use input token ABI
                token_contract = w3.eth.contract(address=from_token, abi=config.L2_token_contractABI)
                balance = token_contract.functions.balanceOf(wallet_address).call()
                token_name = config.L2_token_name
                token_decimal = config.L2_token_decimal
        
        # Check if balance is zero
        if balance == 0:
            error_message = f"No {token_name if not is_native_input else 'ETH/MATIC'} to swap"
            display_message(disp, error_message, is_error=False)
            print(error_message)  # Print to console for debugging
            return None
        
        # Calculate amount to swap
        if is_native_input:
            amount = int(balance * 0.95)  # Leave some for gas
        else:
            amount = balance  # Use full balance for token swaps
        
        print(f"Token address: {from_token}")
        print(f"Balance: {balance}")
        print(f"Swap amount: {amount}")
        
        # Set slippage tolerance
        slippage = 0.5  # 0.5% slippage tolerance
        
        # Check allowance if it's not a native token input
        if not is_native_input:
            allowance = token_contract.functions.allowance(wallet_address, uniswap.address).call()
            if allowance < amount:
                print(f"Insufficient allowance. Current: {allowance}, Required: {amount}")
                # Optionally, you can add code here to increase the allowance
        
        # Perform the swap
        tx_hash = uniswap.make_trade(from_token, to_token, amount, fee=config.L2_poolfee, slippage=slippage)
        
        return tx_hash
    except Exception as e:
        error_message = "Swap failed:\n"
        error_message += f"{str(e)}\n"
        error_message += f"From: {from_token[:10]}...\n"
        error_message += f"To: {to_token[:10]}...\n"
        error_message += f"Amount: {amount}\n"
        error_message += f"Balance: {balance}"
        display_message(disp, error_message, is_error=True)
        print(error_message)  # Print to console for debugging
        return None

def display_transaction_info(disp, tx_hash, status_message):
    config = load_config()
    
    # Check if tx_hash is already a string, if not, convert it
    if isinstance(tx_hash, str):
        tx_hash_str = tx_hash
    else:
        tx_hash_str = tx_hash.hex()
    
    # Generate QR code
    tx_url = f"{config.L2_chain_explorer}tx/{tx_hash_str}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(tx_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create a new image with the QR code
    img = Image.new("RGB", (240, 240), color="white")
    qr_img_resized = qr_img.resize((200, 200))
    img.paste(qr_img_resized, (20, 20))  # QR code is placed at (20, 20)
    
    # Add text overlays
    d = ImageDraw.Draw(img)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    
    # Add title (at the top)
    d.text((120, 10), "Transaction Info", fill="black", anchor="mt", font=font_large)
    
    # Add status message (below the QR code)
    d.text((120, 225), status_message, fill="black", anchor="ms", font=font_large)
    
    # Add instruction (at the bottom)
    d.text((120, 235), "Scan QR to view details", fill="black", anchor="ms", font=font_small)
    
    # Display the image
    disp.image(img)
    
    print(f"Transaction URL: {tx_url}")
    print(f"Status: {status_message}")

def perform_swap(disp, get_address, get_private_key, from_token, to_token):
    config = load_config()
    w3 = Web3(Web3.HTTPProvider(config.infura_url_L2))
    
    # Add PoA middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Get the actual address and private key
    wallet_address = get_address()
    private_key = get_private_key()
    
    # Check gas balance
    has_gas, gas_message = check_gas_balance(w3, wallet_address, w3.eth.chain_id)
    if not has_gas:
        display_message(disp, f"No gas in wallet\n{gas_message}", is_error=False)
        return {"success": False, "message": gas_message, "tx_hash": None}
    
    display_message(disp, "Initiating swap...\nPlease wait")
    tx_hash = swap_tokens(disp, wallet_address, private_key, from_token, to_token, w3)
    if tx_hash is None:
        display_message(disp, "Swap initiation failed")
        time.sleep(8)
        return {"success": False, "message": "Swap initiation failed", "tx_hash": None}
    
    # Now we have a valid tx_hash, display it with QR code
    display_transaction_info(disp, tx_hash, "Waiting for confirmation...")
    
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)  # 3 minutes timeout
    except TimeoutError:
        display_transaction_info(disp, tx_hash, "Confirmation timeout")
        time.sleep(10)
        return {"success": False, "message": "Confirmation timeout", "tx_hash": tx_hash.hex()}
    
    if receipt.status == 1:
        display_transaction_info(disp, tx_hash, "Transaction confirmed!")
        time.sleep(10)
        return {
            "success": True,
            "message": "Transaction confirmed",
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }
    else:
        display_transaction_info(disp, tx_hash, "Transaction failed")
        time.sleep(10)
        return {
            "success": False,
            "message": "Transaction failed",
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }

def swap_l2_token_to_output(disp, get_address, get_private_key):
    config = load_config()  # No argument needed
    return perform_swap(disp, get_address, get_private_key, config.L2_token_address, config.L2_output_address)

def swap_output_to_l2_token(disp, get_address, get_private_key):
    config = load_config()  # No argument needed
    return perform_swap(disp, get_address, get_private_key, config.L2_output_address, config.L2_token_address)

def display_message(disp, message, is_error=False):
    background_color = "orange" if is_error else "white"
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    im = Image.new("RGB", (240, 240), background_color)
    d = ImageDraw.Draw(im)
    
    # Split the message into words
    words = message.split()
    lines = []
    current_line = []
    
    for word in words:
        if d.textsize(' '.join(current_line + [word]), font=font)[0] <= 220:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total height of text
    total_height = len(lines) * 20  # Assuming 20 pixels per line
    
    # Calculate starting y position to center the text vertically
    start_y = (240 - total_height) // 2
    
    y_position = start_y
    for line in lines:
        d.text((120, y_position), line, fill="black", anchor="mm", font=font)
        y_position += 20
    
    disp.image(im)
    time.sleep(10)  # Display the message for 10 seconds
