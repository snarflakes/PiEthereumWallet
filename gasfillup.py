import requests
from web3 import Web3
import json
from PIL import Image, ImageDraw, ImageFont
import time
import os
import sys
from datetime import datetime, timedelta
from eth_account.account import Account  # Changed from web3.account
import qrcode

"""
Direct Gas Transfer Integration

This script handles native gas token transfers on supported L2 chains.
Currently supports Polygon, Arbitrum, and Base.


Key concepts:

1. Pre-funding:
   - User pre-loads native gas token on each supported chain
   - Each chain has its own dedicated gas wallet

2. Gas Fill-up Flow:
   - When a wallet needs gas, script does direct transfer from chain's gas wallet
   - Small, fixed amount transferred to minimize risk
   - Simple, direct, and fast transfers

3. Security:
   - Private keys remain secure on Pi's SD card
   - Each transaction only sends minimal amount needed for gas
"""

# Constants for direct transfers
DIRECT_TRANSFER_USD = 0.05  # $0.05 worth of native token per transfer
MIN_DEPOSIT_USD = DIRECT_TRANSFER_USD  # Use same amount for consistency

# Constants for file paths
BOOT_PATH = "/boot"  # Raspberry Pi boot partition
GAS_WALLET_FILE = os.path.join(BOOT_PATH, "gas_wallet.json")
SD_WALLET_FILE = "/mnt/sdcard/wallet.json"

class PriceCache:
    def __init__(self):
        self.price = None
        self.last_update = None
        self.cache_duration = timedelta(minutes=2)  # Cache price for 2 minutes

price_cache = PriceCache()

def get_token_price(chain_id=None):
    """
    Get current token price in USD from CoinGecko API with caching.
    Supports multiple chains/tokens based on active configuration.
    """
    global price_cache
    
    if not chain_id:
        config = load_config()
        chain_id = str(config.L2_chainid)

    # Determine which token to query based on chain
    if chain_id in ['137', '80001']:  # Polygon chains
        token_id = 'matic-network'
    else:  # Default to ETH for other chains
        token_id = 'ethereum'
    
    # Return cached price if still valid
    if (price_cache.price is not None and 
        price_cache.last_update is not None and 
        datetime.now() - price_cache.last_update < price_cache.cache_duration):
        return price_cache.price

    # If cache expired, fetch new price
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'PiSwapL2 Integration'
        }
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 429:  # Rate limit hit
            if price_cache.price:
                return price_cache.price
            raise RuntimeError("Rate limit exceeded and no cached price available")
            
        if response.status_code != 200:
            if price_cache.price:
                return price_cache.price
            raise RuntimeError(f"API returned status code {response.status_code}")

        data = response.json()
        price = float(data[token_id]['usd'])
        
        # Update cache
        price_cache.price = price
        price_cache.last_update = datetime.now()
        
        return price
        
    except Exception as e:
        if price_cache.price:
            return price_cache.price
        raise RuntimeError(f"Failed to fetch token price: {e}")

def calculate_safe_deposit_amount(chain_id=None):
    """Calculate a safe deposit amount"""
    token_price = get_token_price(chain_id)
    deposit_amount = MIN_DEPOSIT_USD / token_price
    return deposit_amount

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

def get_wallet_address():
    """Get wallet address from SD card"""
    try:
        with open("/mnt/sdcard/wallet.json", "r") as f:
            wallet_data = json.load(f)
            address = wallet_data.get("address")
            if not address:
                print("Error: Address is missing from wallet.json")
                return None
            return address
    except (IOError, json.JSONDecodeError) as e:
        print(f"Failed to read or parse wallet.json from SD card: {str(e)}")
        return None

def show_gas_emoji(disp, chain_id=None, message="Filling her up!"):
    """Display gas status screen with chain-appropriate message."""
    try:
        img = Image.new('RGB', (240, 240), 'white')
        draw = ImageDraw.Draw(img)
        
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        message_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        
        token_text = "GAS ✓"
        if chain_id and chain_id in CHAIN_CONFIGS:
            token_text = f"{CHAIN_CONFIGS[chain_id]['token']} ✓"
        
        draw.text((120, 100), token_text, font=title_font, fill="black", anchor="mm")
        draw.text((120, 130), message, font=message_font, fill="black", anchor="mm")
        
        disp.image(img)
    except Exception as e:
        print(f"Failed to show gas status: {e}")

def get_gas_wallet():
    """Get or create the gas wallet from boot partition"""
    try:
        # If wallet exists, return it
        if os.path.exists(GAS_WALLET_FILE):
            with open(GAS_WALLET_FILE, 'r') as f:
                return json.load(f)
                
        # Create new wallet if it doesn't exist
        account = Account.create()
        wallet_data = {
            "address": account.address,
            "private_key": account.key.hex()
        }
        
        # Ensure boot directory is writable
        if not os.access(BOOT_PATH, os.W_OK):
            raise RuntimeError(f"Cannot write to {BOOT_PATH}. Check permissions.")
            
        # Save to boot partition
        with open(GAS_WALLET_FILE, 'w') as f:
            json.dump(wallet_data, f, indent=4)
        
        # Get current chain info for the message
        chain_id = get_current_chain_id()
        chain_name = CHAIN_CONFIGS[chain_id]['chain_name']
        token = CHAIN_CONFIGS[chain_id]['token']
            
        print(f"IMPORTANT: Fund this address with {token} on {chain_name}: {account.address}")
        
        return wallet_data
        
    except Exception as e:
        raise RuntimeError(f"Failed to get/create gas wallet: {e}")

def check_gas_wallet_balance(w3, address, chain_id):
    """Check if gas wallet has sufficient balance"""
    try:
        balance_wei = w3.eth.get_balance(address)
        balance = w3.from_wei(balance_wei, 'ether')
        
        # Get current token price
        token_price = get_token_price(chain_id)
        
        # Calculate minimum required balance in native token
        min_balance = DIRECT_TRANSFER_USD / token_price
        
        # Add 20% for gas costs
        min_balance_with_gas = min_balance * 1.2
        
        return balance >= min_balance_with_gas, balance
        
    except Exception as e:
        raise RuntimeError(f"Failed to check gas wallet balance: {e}")

def show_empty_gas_wallet_screen(disp, wallet_address, current_balance, chain_id):
    """Show empty gas wallet screen with QR code"""
    try:
        img = Image.new('RGB', (240, 240), 'white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        
        # Get chain name from CHAIN_CONFIGS
        chain_name = CHAIN_CONFIGS[chain_id]['chain_name']
        
        # Draw title
        title_text = f"Gas Wallet Empty"
        draw.text((120, 30), title_text, fill="black", anchor="mm", font=title_font)
        
        # Draw funding instruction with correct chain name
        fund_text = f"Fund on {chain_name}:"
        draw.text((120, 50), fund_text, fill="black", anchor="mm", font=normal_font)
        
        # Generate and draw QR code
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(wallet_address)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize and center QR code
        qr_size = 120
        qr_img = qr_img.resize((qr_size, qr_size))
        qr_pos = ((240 - qr_size) // 2, 70)  # Moved QR code down slightly
        img.paste(qr_img, qr_pos)
        
        # Draw current balance (moved down to avoid overlap)
        balance_text = f"Current: {current_balance:.8f} {CHAIN_CONFIGS[chain_id]['token']}"
        draw.text((120, 195), balance_text, fill="black", anchor="mm", font=normal_font)  # Moved down
        
        # Draw wallet address (shortened)
        addr_text = f"{wallet_address[:6]}...{wallet_address[-4:]}"
        draw.text((120, 215), addr_text, fill="black", anchor="mm", font=normal_font)
        
        # Draw minimum requirement
        min_text = f"Min Required: ${DIRECT_TRANSFER_USD:.2f}"
        draw.text((120, 235), min_text, fill="black", anchor="mm", font=normal_font)
        
        disp.image(img)
        
    except Exception as e:
        print(f"Failed to show empty gas wallet screen: {e}")

def get_native_token(chain_id):
    """Get native token symbol for a given chain ID"""
    native_tokens = {
        '137': 'POLY',    # Polygon
        '42161': 'ETH',    # Arbitrum
        '10': 'ETH',       # Optimism
        '8453': 'ETH',     # Base
    }
    return native_tokens.get(str(chain_id), 'ETH')  # Default to ETH if chain not found

def get_chain_configs():
    """Dynamically build chain configurations from available config files"""
    chain_configs = {}
    base_dir = get_base_dir()
    
    try:
        # Read all chain directories
        for chain_dir in os.listdir(base_dir):
            chain_path = os.path.join(base_dir, chain_dir)
            if not os.path.isdir(chain_path):
                continue
                
            # Look for config files in each chain directory
            for config_file in os.listdir(chain_path):
                if not config_file.endswith('.json'):
                    continue
                    
                config_path = os.path.join(chain_path, config_file)
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        chain_id = str(config.get('L2_chainid'))
                        if chain_id:
                            chain_configs[chain_id] = {
                                'chain_name': config.get('L2_name'),
                                'token': get_native_token(chain_id),
                                'config_path': config_path
                            }
                            print(f"DEBUG: Loaded config for chain {chain_id}: {chain_configs[chain_id]}")  # Debug print
                except Exception as e:
                    print(f"Failed to load config from {config_path}: {e}")
                    
        return chain_configs
        
    except Exception as e:
        print(f"DEBUG: Error in get_chain_configs: {e}")  # Debug print
        raise RuntimeError(f"Failed to get chain configurations: {e}")

# Replace the static CHAIN_CONFIGS with dynamic loading
CHAIN_CONFIGS = get_chain_configs()

def get_current_chain_id():
    """Get current chain ID from active config"""
    config_path = get_active_config_path()
    if not config_path:
        print("DEBUG: No active config path found")  # Debug print
        raise RuntimeError("No active config found")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            chain_id = str(config.get('L2_chainid'))
            print(f"DEBUG: Read chain_id from config: {chain_id}")  # Debug print
            return chain_id
    except Exception as e:
        print(f"DEBUG: Error reading chain ID from config: {e}")  # Debug print
        raise RuntimeError(f"Failed to get chain ID from active config: {e}")

def execute_gas_fillup(provider_url, disp=None):
    """Execute gas fillup using direct transfer for all supported chains"""
    # Add transaction lock to prevent double execution
    if hasattr(execute_gas_fillup, 'in_progress'):
        if disp:
            show_gas_emoji(disp, "Transfer already in progress...")
            time.sleep(2)
        return {'success': True, 'note': 'Transaction already in progress'}
    
    gas_wallet = None
    current_balance = None
    chain_id = None
        
    try:
        execute_gas_fillup.in_progress = True
        
        # Get current chain ID from active config
        chain_id = get_current_chain_id()
        print(f"DEBUG: Got chain_id: {chain_id}")  # Debug print
        
        if chain_id not in CHAIN_CONFIGS:
            print(f"DEBUG: Chain ID {chain_id} not in CHAIN_CONFIGS: {CHAIN_CONFIGS.keys()}")  # Debug print
            raise RuntimeError(f"Unsupported chain ID: {chain_id}")
            
        # Get gas wallet
        gas_wallet = get_gas_wallet()
        
        # Check balance
        w3 = Web3(Web3.HTTPProvider(provider_url))
        has_balance, current_balance = check_gas_wallet_balance(w3, gas_wallet['address'], chain_id)
        
        if not has_balance:
            print(f"DEBUG: Insufficient balance detected. Balance: {current_balance}")  # Debug print
            print(f"DEBUG: Display object present: {disp is not None}")  # Debug print
            if disp:
                show_empty_gas_wallet_screen(disp, gas_wallet['address'], current_balance, chain_id)
            raise RuntimeError(f"Insufficient balance in gas wallet: {current_balance} {CHAIN_CONFIGS[chain_id]['token']}")

        # Get destination address from SD card wallet
        dest_address = get_wallet_address()
        if not dest_address:
            raise RuntimeError("Failed to get destination wallet address from SD card")
            
        # Execute direct transfer
        return execute_direct_transfer(w3, gas_wallet, dest_address, chain_id, disp)

    except Exception as e:
        error_str = str(e)
        print(f"DEBUG: Error caught: {error_str}")  # Debug print
        if gas_wallet and chain_id:  # Make sure we have the necessary objects
            if "insufficient" in error_str.lower() or "balance" in error_str.lower():
                print(f"DEBUG: Showing empty wallet screen")  # Debug print
                if disp:
                    show_empty_gas_wallet_screen(disp, gas_wallet['address'], current_balance, chain_id)
                    time.sleep(30)  # Single delay here
                    show_gas_emoji(disp, chain_id, "Please try again...")  # Show message before returning
                    time.sleep(2)  # Brief pause on the message
        raise RuntimeError(f"Gas fillup error: {error_str}")
        
    finally:
        if hasattr(execute_gas_fillup, 'in_progress'):
            delattr(execute_gas_fillup, 'in_progress')

def execute_direct_transfer(w3, gas_wallet, dest_address, chain_id, disp=None):
    """Execute direct transfer on any supported chain"""
    if disp:
        show_gas_emoji(disp, chain_id, f"Direct transfer on {CHAIN_CONFIGS[chain_id]['chain_name']}...")
    
    # Calculate transfer amount
    token_price = get_token_price(chain_id)
    transfer_amount = DIRECT_TRANSFER_USD / token_price
    transfer_wei = w3.to_wei(transfer_amount, 'ether')

    # Build transfer transaction
    tx = {
        'to': dest_address,
        'value': transfer_wei,
        'chainId': int(chain_id),
        'nonce': w3.eth.get_transaction_count(gas_wallet['address']),
        'gasPrice': w3.eth.gas_price
    }

    # Estimate gas
    gas_estimate = w3.eth.estimate_gas(tx)
    tx['gas'] = gas_estimate

    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, gas_wallet['private_key'])
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for transaction confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        if disp:
            show_gas_emoji(disp, chain_id, "Transfer complete!")
            time.sleep(2)
        return {
            'success': True,
            'tx_hash': tx_hash.hex()
        }
    else:
        raise RuntimeError("Direct transfer failed")
