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
Gas.zip Direct Deposit Integration

This script automates cross-chain gas funding using Gas.zip's Direct Deposit contract.
Key concepts:

1. Pre-funding:
   - User pre-loads ETH on Optimism into the wallet stored on the Pi
   - We specifically use Optimism as our source chain for all gas funding
   - While Gas.zip supports other source chains, we standardize on Optimism for:
     * Lower gas costs
     * Faster transaction finality
     * Consistent user experience

2. Gas Fill-up Flow:
   - When a wallet on any chain (Polygon, Arbitrum, etc.) needs gas:
     a. Script sends small amount of ETH from Optimism to Gas.zip's Direct Deposit contract
     b. Transaction includes calldata (from Gas.zip API) specifying destination chain/address
     c. Gas.zip handles cross-chain bridging and token conversion (e.g., ETH → MATIC)

3. Security:
   - Private keys remain secure on Pi's SD card
   - Each transaction only sends minimal amount needed for gas
"""

# Constants for Gas.zip Direct Deposit
DIRECT_DEPOSIT_ADDRESS = '0x391E7C679d29bD940d63be94AD22A25d25b5A604'
DEPOSIT_CHAIN_ID = 10  # Using Optimism as our source chain for all gas funding
MIN_DEPOSIT_USD = 0.25
MAX_DEPOSIT_USD = 50.00
DIRECT_TRANSFER_USD = 0.05  # $0.05 worth of ETH for direct Optimism transfers

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

def get_eth_price():
    """
    Get current ETH price in USD from CoinGecko API with caching
    to respect rate limits (free tier: ~30 calls/minute)
    """
    global price_cache
    
    # Return cached price if still valid
    if (price_cache.price is not None and 
        price_cache.last_update is not None and 
        datetime.now() - price_cache.last_update < price_cache.cache_duration):
        return price_cache.price

    # If cache expired, fetch new price
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'GasZip Integration Script'  # Being nice to the API
        }
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
            headers=headers,
            timeout=10  # 10 second timeout
        )
        
        if response.status_code == 429:  # Rate limit hit
            if price_cache.price:  # Use cached price if available
                return price_cache.price
            raise RuntimeError("Rate limit exceeded and no cached price available")
            
        if response.status_code != 200:
            if price_cache.price:  # Use cached price if available
                return price_cache.price
            raise RuntimeError(f"API returned status code {response.status_code}")

        data = response.json()
        price = float(data['ethereum']['usd'])
        
        # Update cache
        price_cache.price = price
        price_cache.last_update = datetime.now()
        
        return price
        
    except Exception as e:
        if price_cache.price:  # Use cached price if available
            return price_cache.price
        raise RuntimeError(f"Failed to fetch ETH price: {e}")

def calculate_safe_deposit_amount():
    """Calculate a safe deposit amount (default to $0.25 worth of ETH)"""
    eth_price = get_eth_price()
    # Changed from 1.2 multiplier (0.30) to just using the minimum (0.25)
    deposit_eth = MIN_DEPOSIT_USD / eth_price  # $0.25 worth of ETH
    return deposit_eth

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

def show_gas_emoji(disp, message="Filling her up!"):
    """
    Display gas status screen with appropriate gas token name for target chain.
    While transaction is always in ETH on Optimism, we show the relevant
    gas token name for the target chain (e.g., MATIC for Polygon).
    """
    try:
        # Get the appropriate gas token name from config
        config = load_config()
        # List of chains that use "GAS" terminology
        eth_chains = ["ETH", "OPTIMISM", "ARBITRUM", "BASE"]
        
        # Determine display text based on target chain
        if config.L2_output_name.upper() in eth_chains:
            display_text = "GAS ✓"
        elif config.L2_output_name.upper() in ["MATIC", "POLYGON"]:
            display_text = "MATIC ✓"
        else:
            display_text = f"{config.L2_output_name} ✓"
        
        img = Image.new('RGB', (240, 240), 'white')
        draw = ImageDraw.Draw(img)
        
        # More appropriate font sizes
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        message_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        
        # Draw the appropriate text centered
        draw.text((120, 100), display_text, font=title_font, fill="black", anchor="mm")
        
        # Draw message below
        draw.text((120, 130), message, font=message_font, fill="black", anchor="mm")
        
        # Display the image
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
            
        print(f"Created new gas wallet in {GAS_WALLET_FILE}")
        print(f"IMPORTANT: Fund this address with ETH on Optimism: {account.address}")
        
        return wallet_data
        
    except Exception as e:
        raise RuntimeError(f"Failed to get/create gas wallet: {e}")

def check_gas_wallet_balance(w3, gas_wallet_address):
    """Check if gas wallet has sufficient balance on Optimism"""
    try:
        balance = w3.eth.get_balance(gas_wallet_address)
        eth_price = get_eth_price()
        
        # Calculate minimum deposit amount
        min_deposit_eth = MIN_DEPOSIT_USD / eth_price
        min_deposit_wei = w3.to_wei(min_deposit_eth, 'ether')
        
        # Estimate gas cost (approximate)
        gas_price = w3.eth.gas_price
        estimated_gas = 200000  # Safe estimate for Gas.zip deposit
        gas_cost = gas_price * estimated_gas
        
        # Total required = deposit amount + gas cost
        required_balance = min_deposit_wei + gas_cost
        
        return balance >= required_balance, w3.from_wei(balance, 'ether')
    except Exception as e:
        raise RuntimeError(f"Failed to check gas wallet balance: {e}")

def show_empty_gas_wallet_screen(disp, gas_wallet_address, current_balance):
    """Display QR code and instructions when gas wallet needs funding"""
    try:
        img = Image.new('RGB', (240, 240), 'white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        
        # Draw title
        draw.text((120, 20), "Gas Wallet Empty!", fill="red", anchor="mm", font=title_font)
        
        # Show current balance
        balance_text = f"Balance: {current_balance:.6f} ETH"
        draw.text((120, 45), balance_text, fill="black", anchor="mm", font=normal_font)
        
        # Instructions
        draw.text((120, 65), "Fund on Optimism:", fill="black", anchor="mm", font=normal_font)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(gas_wallet_address)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize and center QR code
        qr_size = 120
        qr_img = qr_img.resize((qr_size, qr_size))
        qr_pos = ((240 - qr_size) // 2, 85)
        img.paste(qr_img, qr_pos)
        
        # Draw wallet address
        addr_text = f"{gas_wallet_address[:10]}...{gas_wallet_address[-8:]}"
        draw.text((120, 215), addr_text, fill="black", anchor="mm", font=normal_font)
        
        # Draw minimum requirement
        min_text = f"Min Required: ${MIN_DEPOSIT_USD:.2f}"
        draw.text((120, 235), min_text, fill="black", anchor="mm", font=normal_font)
        
        disp.image(img)
        time.sleep(30)  # Display for 10 seconds
        
    except Exception as e:
        print(f"Failed to show empty gas wallet screen: {e}")

def get_gaszip_chain_info():
    """Get chain information from Gas.zip API"""
    try:
        response = requests.get("https://backend.gas.zip/v2/chains")
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get Gas.zip chain info: {response.text}")
        
        data = response.json()
        return {str(chain['chain']): chain for chain in data['chains']}
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Gas.zip chain info: {e}")

def monitor_gas_deposit(tx_hash, disp=None):
    """Monitor Gas.zip deposit status and corresponding outbound transactions."""
    try:
        api_url = f"https://backend.gas.zip/v2/deposit/{tx_hash}"
        max_attempts = 30  # 5 minutes maximum monitoring (10 second intervals)
        attempt = 0

        while attempt < max_attempts:
            response = requests.get(api_url)
            if response.status_code != 200:
                print(f"Warning: Unexpected status code {response.status_code}: {response.text}")
                time.sleep(10)
                continue
            
            try:
                data = response.json()
                print(f"Debug: Gas.zip API response: {data}")  # Temporary debug logging
                
                # More lenient checking - if we see any successful status, consider it done
                if isinstance(data, dict):
                    # Check deposit status
                    deposit = data.get('deposit', {})
                    if isinstance(deposit, dict) and deposit.get('status') == 'CONFIRMED':
                        if disp:
                            show_gas_emoji(disp, "Gas delivery complete! ⛽")
                            time.sleep(2)
                        return {
                            'success': True,
                            'deposit': deposit,
                            'outbound_txs': data.get('txs', [])
                        }
                    
                    # Show status if available
                    if disp and isinstance(deposit, dict):
                        status_message = {
                            'SEEN': 'Transaction seen...',
                            'PENDING': 'Processing deposit...',
                            'CONFIRMED': 'Deposit confirmed!',
                            'PRIORITY': 'Priority processing...',
                            'CANCELLED': 'Transaction cancelled'
                        }.get(deposit.get('status', 'UNKNOWN'), 'Processing...')
                        show_gas_emoji(disp, status_message)

            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse API response: {e}")
                
            time.sleep(10)
            attempt += 1

        # If we get here but the transaction was successful, don't raise an error
        print("Warning: Monitoring timed out, but transaction might be successful")
        return {'success': True, 'note': 'Monitoring timed out but transaction may be successful'}

    except Exception as e:
        print(f"Warning: Monitoring error but transaction might be successful: {e}")
        return {'success': True, 'note': 'Monitoring failed but transaction may be successful'}

def execute_gas_fillup(provider_url, disp=None):
    """Execute gas fillup using direct transfer for Optimism, Gas.zip for other chains."""
    try:
        # Get gas wallet first
        gas_wallet = get_gas_wallet()
        
        # Check balance BEFORE showing any screens
        w3 = Web3(Web3.HTTPProvider(provider_url))
        has_balance, current_balance = check_gas_wallet_balance(w3, gas_wallet['address'])
        
        if not has_balance:
            if disp:
                show_empty_gas_wallet_screen(disp, gas_wallet['address'], current_balance)
            raise RuntimeError(f"Insufficient balance in gas wallet: {current_balance} ETH")

        # Get destination address from SD card wallet
        dest_address = get_wallet_address()
        if not dest_address:
            raise RuntimeError("Failed to get destination wallet address from SD card")
        
        # Load config to get target chain
        config = load_config()
        target_chain_id = str(config.L2_chainid)

        # Check if both source and target are Optimism
        if str(DEPOSIT_CHAIN_ID) == target_chain_id:
            return execute_direct_transfer(w3, gas_wallet, dest_address, disp)
        else:
            # Get chain information from Gas.zip
            chain_info = get_gaszip_chain_info()
            return execute_gaszip_fillup(w3, gas_wallet, dest_address, target_chain_id, chain_info, disp)

    except Exception as e:
        error_str = str(e)
        if "insufficient funds" in error_str.lower():
            if disp:
                show_empty_gas_wallet_screen(disp, gas_wallet['address'], current_balance)
        else:
            # For other errors, show error message briefly before raising
            if disp:
                show_gas_emoji(disp, f"Error: {str(e)}")
                time.sleep(2)
        raise RuntimeError(f"Gas fillup error: {error_str}")

def execute_direct_transfer(w3, gas_wallet, dest_address, disp=None):
    """Execute direct transfer on Optimism."""
    if disp:
        show_gas_emoji(disp, "Direct Optimism transfer...")
    
    # Calculate smaller amount for direct transfer
    eth_price = get_eth_price()
    transfer_eth = DIRECT_TRANSFER_USD / eth_price
    transfer_wei = w3.to_wei(transfer_eth, 'ether')

    # Build direct transfer transaction
    tx = {
        'to': dest_address,
        'value': transfer_wei,
        'chainId': DEPOSIT_CHAIN_ID,
        'nonce': w3.eth.get_transaction_count(gas_wallet['address']),
        'gasPrice': w3.eth.gas_price
    }

    # Estimate gas for direct transfer
    gas_estimate = w3.eth.estimate_gas(tx)
    tx['gas'] = gas_estimate

    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, gas_wallet['private_key'])
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for transaction confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        if disp:
            show_gas_emoji(disp, "Transfer complete!")
            time.sleep(2)
        return {
            'success': True,
            'tx_hash': tx_hash.hex(),
            'direct_transfer': True
        }
    else:
        raise RuntimeError("Direct transfer failed")

def execute_gaszip_fillup(w3, gas_wallet, dest_address, target_chain_id, chain_info, disp=None):
    """Execute gas fillup using Gas.zip for cross-chain transfers."""
    try:
        # Show initial screen
        if disp:
            show_gas_emoji(disp, "Starting Gas.zip fillup...")
            time.sleep(5)  # Show for 5 seconds

        # Get chain information from Gas.zip
        chain_info = get_gaszip_chain_info()
        
        # Only verify target chain since we know source is always Optimism
        if target_chain_id not in chain_info:
            raise RuntimeError(f"Target chain {target_chain_id} not supported by Gas.zip")

        # Calculate deposit amount
        deposit_eth = calculate_safe_deposit_amount()
        deposit_wei = w3.to_wei(deposit_eth, 'ether')

        # Build Gas.zip API URL (source always Optimism)
        api_url = (
            f"https://backend.gas.zip/v2/quotes/{DEPOSIT_CHAIN_ID}/"
            f"{deposit_wei}/{target_chain_id}"
            f"?from={gas_wallet['address']}&to={dest_address}"
        )

        # Get quote from Gas.zip
        response = requests.get(api_url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get Gas.zip quote: {response.text}")
        
        quote_data = response.json()
        
        if disp:
            target_chain = chain_info[target_chain_id]
            show_gas_emoji(disp, f"Filling {target_chain['name']} {target_chain['symbol']}...")

        # Execute transaction on Optimism
        tx = {
            'to': DIRECT_DEPOSIT_ADDRESS,
            'value': deposit_wei,
            'data': quote_data['calldata'],
            'chainId': DEPOSIT_CHAIN_ID,
            'nonce': w3.eth.get_transaction_count(gas_wallet['address']),
            'gasPrice': w3.eth.gas_price
        }

        # Estimate gas
        gas_estimate = w3.eth.estimate_gas(tx)
        tx['gas'] = gas_estimate

        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, gas_wallet['private_key'])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Monitor deposit status
        result = monitor_gas_deposit(tx_hash.hex(), disp)
        
        return result

    except Exception as e:
        error_str = str(e)
        if "insufficient funds" in error_str.lower():
            if disp:
                show_empty_gas_wallet_screen(disp, gas_wallet['address'], current_balance)
        else:
            # For other errors, show error message briefly before raising
            if disp:
                show_gas_emoji(disp, f"Error: {str(e)}")
                time.sleep(2)
        raise RuntimeError(f"Gas fillup error: {error_str}")
