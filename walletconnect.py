import cv2
import pyzbar.pyzbar as pyzbar
import time
from PIL import Image, ImageDraw, ImageFont
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct, encode_structured_data
from pywalletconnect import WCClient
import logging
import os
import sys
import json
from web3.middleware import geth_poa_middleware
from textwrap import wrap
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account.signers.local import LocalAccount
from eth_utils import to_checksum_address

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_base_dir():
    """Get the directory where the executable/script is located"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_active_config_path():
    """Get the active chain directory and config file"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            if ':' not in content:
                logger.error("Invalid format in active.txt")
                return None
            chain_dir, config_file = content.split(':')
            base_dir = get_base_dir()
            full_path = os.path.join(base_dir, chain_dir, config_file)
            if not os.path.exists(full_path):
                logger.error(f"Config file not found: {full_path}")
                return None
            return full_path
    except FileNotFoundError:
        logger.error("active.txt not found")
        return None
    except Exception as e:
        logger.error(f"Error reading active.txt: {e}")
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

def wallet_connect(disp, example_d, get_private_key, get_address, buttonL):
    wallet_address = get_address()
    if not wallet_address:
        logger.error("Failed to retrieve wallet address")
        display_message(disp, "Failed to retrieve wallet address")
        return

    private_key = get_private_key()
    if not private_key:
        logger.error("Failed to retrieve private key")
        display_message(disp, "Failed to retrieve private key")
        return

    wallet_chain_id = example_d[0]

    WCClient.set_project_id("338d2404fafcd317347e4da1c3de72b5")

    qr_code_data = capture_qr_code(disp, buttonL)
    if not qr_code_data:
        logger.info("QR code scanning cancelled or failed")
        return

    logger.info(f"QR code data: {qr_code_data}")
    wclient = WCClient.from_wc_uri(qr_code_data)

    try:
        print("Opening WalletConnect session...")
        session_data = wclient.open_session()
        print(f"Session data: {session_data}")
        display_message(disp, f"WalletConnect request from {session_data[2]['name']}", "Connecting...")
        wclient.reply_session_request(session_data[0], wallet_chain_id, wallet_address)
        print("Connected to Dapp")
        display_message(disp, "Connected. Waiting for Dapp messages...", color="salmon")

        while True:
            try:
                read_data = wclient.get_message()
                if read_data[0] is not None:
                    print(f"Received WalletConnect message: {read_data}")

                    if check_disconnect(read_data):
                        print("Disconnect signal received. Closing session...")
                        break

                    handle_wallet_connect_message(disp, wclient, read_data, private_key, wallet_address)

                if buttonL.is_pressed:
                    print("Disconnect button pressed")
                    display_message(disp, "Disconnecting...")
                    wclient.disconnect()  # Explicitly disconnect
                    break

            except KeyboardInterrupt:
                print("KeyboardInterrupt received")
                wclient.disconnect()  # Explicitly disconnect
                break

    except Exception as e:
        print(f"Connection Failed: {str(e)}")
        display_message(disp, f"Connection Failed: {str(e)}")

    finally:
        print("Closing WalletConnect session")
        wclient.close()
        display_message(disp, "Disconnected from Dapp")


def capture_qr_code(disp, buttonL):
    display_message(disp, "Scan WalletConnect QR Code")
    cap = cv2.VideoCapture(-1)

    while True:
        _, frame = cap.read()
        decoded_objects = pyzbar.decode(frame)
        for obj in decoded_objects:
            qr_code_data = obj.data.decode("utf-8")
            cap.release()
            return qr_code_data

        if buttonL.is_pressed:
            cap.release()
            return None

        time.sleep(0.1)  # Small delay to reduce CPU usage

    cap.release()
    return None

def handle_wallet_connect_message(disp, wclient, read_data, private_key, wallet_address):
    print(f"Handling WalletConnect message: {read_data}")
    id_request, method, parameters = read_data

    try:
        config = load_config()
        chain_id = int(config.L2_chainid)
    except Exception as e:
        print(f"Failed to load config: {e}")
        display_message(disp, "Failed to load chain configuration")
        return

    if method in ["wc_sessionRequest", "wc_sessionPayload"]:
        if parameters.get("request"):
            method = parameters["request"].get("method")
            parameters = parameters["request"].get("params")

    print(f"Processed method: {method}")
    print(f"Processed parameters: {parameters}")

    if method == "personal_sign":
        handle_personal_sign(disp, wclient, id_request, parameters, private_key, wallet_address)
    elif method == "eth_sendTransaction":
        handle_send_transaction(disp, wclient, id_request, parameters, private_key, chain_id, config)
    elif method == "eth_signTypedData":
        handle_sign_typed_data(disp, wclient, id_request, parameters, private_key)
    elif method == "wallet_switchEthereumChain":
        print(f"Unsupported method: {method}")
        display_message(disp, f"Unsupported method: {method}", color="salmon")
        wclient.close()
    elif method == "wc_sessionDelete":
        print("Received wc_sessionDelete. Disconnecting...")
        wclient.disconnect()

def handle_personal_sign(disp, wclient, id_request, parameters, private_key, wallet_address):
    message = parameters[0][2:]
    message_bytes = bytes.fromhex(message)

    signed_message = Account.sign_message(encode_defunct(message_bytes), private_key=private_key)
    result = signed_message.signature.hex()

    wclient.reply(id_request, result)

    recovered_address = Web3().eth.account.recover_message(encode_defunct(message_bytes), signature=result)
    if recovered_address.lower() == wallet_address.lower():
        display_message(disp, "Message signed successfully", color="salmon")
    else:
        display_message(disp, "Signature verification failed")

def handle_send_transaction(disp, wclient, id_request, parameters, private_key, chain_id, config):
    print("=== Transaction Debug Info ===")
    print(f"Raw parameters from dApp: {parameters}")
    print(f"Our active chain config: {config.L2_name} (Chain ID: {config.L2_chainid})")
    
    try:
        # Get the chain ID requested by the dApp
        tx_params = parameters[0]
        dapp_chain_id = int(tx_params.get('chainId', chain_id))
        print(f"DApp requested chain ID: {dapp_chain_id}")
        
        # Get our wallet's active chain ID from config
        our_chain_id = int(config.L2_chainid)
        print(f"Our wallet's chain ID: {our_chain_id}")

        # Verify chain IDs match
        if dapp_chain_id != our_chain_id:
            error_msg = f"Chain ID mismatch! DApp wants {dapp_chain_id}, but wallet is on {our_chain_id}"
            print(error_msg)
            display_message(disp, error_msg)
            wclient.reject(id_request, error_msg)
            return

        # If we get here, chain IDs match, so process the transaction
        print(f"Processing transaction on {config.L2_name}")
        result = send_transaction_L2(parameters, private_key, config)
        
        wclient.reply(id_request, result)
        display_message(disp, "Transaction sent", color="salmon")
        
    except Exception as e:
        error_msg = f"Transaction failed: {str(e)}"
        print(error_msg)
        display_message(disp, error_msg)
        wclient.reject(id_request, error_msg)

def send_transaction_L2(parameters, private_key, config):
    w3 = Web3(Web3.HTTPProvider(config.infura_url_L2))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Create an account from the private key
    account: LocalAccount = Account.from_key(private_key)
    
    # Add the signing middleware
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    
    # Set the default account
    w3.eth.default_account = account.address

    tx_params = parameters[0]
    
    # Build transaction dict using to_checksum_address from eth_utils
    transaction = {
        'to': to_checksum_address(tx_params['to']),
        'from': to_checksum_address(tx_params['from']),
        'data': tx_params.get('data', '0x'),
        'value': int(tx_params.get('value', '0'), 16) if isinstance(tx_params.get('value'), str) else tx_params.get('value', 0),
        'nonce': w3.eth.get_transaction_count(account.address),
    }

    # Add gas parameters if provided
    if tx_params.get('gas'):
        transaction['gas'] = int(tx_params['gas'], 16) if isinstance(tx_params['gas'], str) else tx_params['gas']
    else:
        # Estimate gas if not provided
        transaction['gas'] = w3.eth.estimate_gas(transaction)

    if tx_params.get('gasPrice'):
        transaction['gasPrice'] = int(tx_params['gasPrice'], 16) if isinstance(tx_params['gasPrice'], str) else tx_params['gasPrice']
    else:
        # Get current gas price if not provided
        transaction['gasPrice'] = w3.eth.gas_price

    # Send the transaction
    tx_hash = w3.eth.send_transaction(transaction)
    return Web3.to_hex(tx_hash)

def check_disconnect(read_data):
    id_request, method, parameters = read_data

    if method == "wc_sessionUpdate" and parameters[0].get("approved") == False:
        print("User disconnects from Dapp (WC v1).")
        return True

    if method == "wc_sessionDelete":
        reason = parameters.get("message", "Unknown reason")
        code = parameters.get("code", "Unknown code")
        print(f"Dapp initiated disconnect (WC v2). Reason: {reason}, Code: {code}")
        return True

    return False

def display_message(disp, message, title=None, color=None):
    if title is None:
        title = ""
    if color is None:
        color = "lime"

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    img = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(img)

    # Create the rounded rectangle with the specified color
    draw.rounded_rectangle(((10, 50), (230, 190)), fill=color, outline="black", width=0, radius=25)

    if title:
        draw.text((120, 70), title, fill="black", anchor="ms", font=font)

    # Wrap the message text
    wrapped_text = wrap(message, width=20)  # Adjust width as needed
    y_position = 130 - (len(wrapped_text) * 10)  # Center the text block vertically
    for line in wrapped_text:
        draw.text((120, y_position), line, fill="black", anchor="ms", font=small_font)
        y_position += 20  # Adjust line spacing as needed

    disp.image(img)

def handle_sign_typed_data(disp, wclient, id_request, parameters, private_key):
    try:
        # Get the typed data from parameters
        typed_data = parameters[1]  # Usually parameters[1] contains the typed data
        print("Typed Data:", typed_data)
        
        # Convert the typed data to EIP-712 format
        sign_info = TypedDataConvert(
            typed_data['domain'],
            typed_data['types'],
            typed_data['message']
        )
        
        # Encode the structured data
        message = encode_structured_data(sign_info)
        
        # Sign the message
        signed_message = Account.sign_message(message, private_key=private_key)
        result = signed_message.signature.hex()
        
        print("Signature:", result)
        
        # Send the signature back to the dApp
        wclient.reply(id_request, result)
        display_message(disp, "Message signed successfully", color="salmon")
        
    except Exception as e:
        error_msg = f"Failed to sign typed data: {str(e)}"
        print(error_msg)
        display_message(disp, error_msg)
        wclient.reject(id_request, error_msg)

def TypedDataConvert(domain: dict, types: dict, values: dict):
    EIP712DomainMap = {
        'name': {'name': 'name', 'type': 'string'},
        'version': {'name': 'version', 'type': 'string'},
        'chainId': {'name': 'chainId', 'type': 'uint256'},
        'verifyingContract': {'name': 'verifyingContract', 'type': 'address'},
        'salt': {'name': 'salt', 'type': 'bytes32'},
    }
    
    primaryType = _getPrimaryType(types, values)
    newValue = _fix(values.copy(), primaryType, types)
    
    EIP712Domain = []
    for domainKey in domain:
        EIP712Domain.append(EIP712DomainMap[domainKey])
    
    newTypes = types.copy()
    newTypes['EIP712Domain'] = EIP712Domain
    newDomain = _fix(domain, 'EIP712Domain', newTypes)
    
    completedStruct = {
        "types": newTypes,
        "domain": newDomain,
        "message": newValue,
        "primaryType": primaryType,
    }
    return completedStruct

def _getPrimaryType(types: dict, values: dict) -> str:
    primaryType = ''
    for key in types:
        if key != 'EIP712Domain':
            if key.lower() in str(values).lower():
                primaryType = key
                break
    if primaryType == '':
        return None
    return primaryType

def _fix(data: dict, dataType: str, types: dict) -> dict:
    if dataType not in types:
        return data
    
    newData = {}
    for field in types[dataType]:
        value = data.get(field['name'])
        if value is not None:
            if field['type'] == 'uint256' and isinstance(value, str):
                newData[field['name']] = int(value)
            else:
                newData[field['name']] = value
    
    return newData

