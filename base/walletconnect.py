import cv2
import pyzbar.pyzbar as pyzbar
import time
from PIL import Image, ImageDraw, ImageFont
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from pywalletconnect import WCClient
import logging
from config_loader import load_config
from textwrap import wrap

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    config = load_config() 
except RuntimeError as e: 
    logger.error(f"Failed to load config: {e}")
    exit(1)  # Exit the program immediately

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


def handle_wallet_connect_message(disp, wclient, read_data, private_key, wallet_address, example_d, config):
    logger.info(f"Handling WalletConnect message: {read_data}")

    id_request, method, parameters = read_data

    if method in ["wc_sessionRequest", "wc_sessionPayload"]:
        if parameters.get("request"):
            method = parameters["request"].get("method")
            parameters = parameters["request"].get("params")

    logger.info(f"Processed method: {method}")
    logger.info(f"Processed parameters: {parameters}")

    logger.debug(f"Method: {method}, Parameters: {parameters}")

    if method == "personal_sign":
        handle_personal_sign(disp, wclient, id_request, parameters, private_key, wallet_address)
    elif method == "eth_sendTransaction":
        handle_send_transaction(disp, wclient, id_request, parameters, private_key, example_d, config)
    elif method == "eth_signTypedData":
        handle_sign_typed_data(disp, wclient, id_request, parameters, private_key)
    elif method == "wallet_switchEthereumChain":
        handle_switch_chain(disp, wclient, id_request, parameters)
    else:
        display_message(disp, f"Unsupported method: {method}", color="salmon")

def handle_send_transaction(disp, wclient, id_request, parameters, private_key, example_d, config):
    chain_id = example_d[0]
    if chain_id == int(config['L2_chainid']):  # L2 (e.g., Polygon)
        result = send_transaction_L2(parameters, private_key, config)
    else:
        result = send_transaction_eth(parameters, private_key, config)
    wclient.reply(id_request, result)
    display_message(disp, "Transaction sent", color="salmon")

def send_transaction_L2(parameters, private_key, config):
    w3 = Web3(Web3.HTTPProvider(config['infura_url_L2']))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))

    tx_params = parameters[0]
    tx_hash = w3.eth.send_transaction({
        'to': w3.toChecksumAddress(tx_params['to']),
        'from': w3.toChecksumAddress(tx_params['from']),
        'data': tx_params['data'],
        'value': tx_params.get('value', 0)
    })
    return w3.toHex(tx_hash)

def send_transaction_eth(parameters, private_key, config):
    w3 = Web3(Web3.HTTPProvider(config['infura_url_eth']))
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))

    tx_params = parameters[0]
    tx_hash = w3.eth.send_transaction({
        'to': w3.toChecksumAddress(tx_params['to']),
        'from': w3.toChecksumAddress(tx_params['from']),
        'data': tx_params['data'],
        'value': tx_params.get('value', 0)
    })
    return w3.toHex(tx_hash)


def disconnect_session(wclient):
    try:
        wclient.disconnect()
    except Exception as e:
        print(f"Error during disconnect: {str(e)}")


def handle_wallet_connect_message(disp, wclient, read_data, private_key, wallet_address):
    print(f"Handling WalletConnect message: {read_data}")
    id_request, method, parameters = read_data

    if method in ["wc_sessionRequest", "wc_sessionPayload"]:
        if parameters.get("request"):
            method = parameters["request"].get("method")
            parameters = parameters["request"].get("params")

    print(f"Processed method: {method}")
    print(f"Processed parameters: {parameters}")

    if method == "personal_sign":
        handle_personal_sign(disp, wclient, id_request, parameters, private_key, wallet_address)
    elif method in ["eth_sendTransaction", "eth_signTypedData", "wallet_switchEthereumChain"]:
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

