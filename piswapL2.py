#Created by Snarflakes.
#To Satoshi and Vitalik, saludos amigos.
#GNU General Public License v3.0
#Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, 
#under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. 


import os
import sys
import logging
from logging import getLogger
import requests
import io
import glob
import gc
import PIL
from signal import pause
from eth_account import Account

#sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
sys.path.insert(0, '/home/pi/.local/lib/python3.7/site-packages')
sys.path.insert(0, '/home/pi/.local/lib/python3.7/site-packages/pywalletconnect')

#import ST7789 as ST7789

#button code
import subprocess
import board
from gpiozero import Button

#new joystick screen
import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont, ImageFile, ImageOps
import adafruit_rgb_display.st7789 as st7789

#qr code modules
       #import numpy as np
import argparse
import datetime
from csv import reader
       #import cv2
#import imutils
       #import pyzbar.pyzbar as pyzbar

#check internet
import socket

#screen rotate
import pickle

#random
from random import randint

import string
import json
import qrcode

#web3
from web3 import Web3 
from eth_account import Account
import secrets
      #from uniswap import Uniswap
from web3.middleware import geth_poa_middleware

#walletconnect
        #from logging import basicConfig, DEBUG basicConfig(level=DEBUG)
from time import sleep
       #from pywalletconnect.client import WCClient, WCClientInvalidOption
       #from siwe import SiweMessage

#more web3
from eth_account.messages import encode_defunct
from web3.auto import w3
from eth_account import messages

from home_screen import HomeScreen
from walletconnect import wallet_connect

#load and process external variables from config.json
from config_loader import load_config

def get_base_dir():
    """Get the directory where the executable/script is located"""
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # If running as script
        return os.path.dirname(os.path.abspath(__file__))

def initialize_active_chain():
    """Create active.txt with default chain if it doesn't exist"""
    if not os.path.exists('active.txt'):
        base_dir = get_base_dir()
        # Look for available chain directories
        chain_dirs = [d for d in os.listdir(base_dir)
                     if os.path.isdir(os.path.join(base_dir, d)) 
                     and os.path.exists(os.path.join(base_dir, d, 'config.json'))]
        
        if chain_dirs:
            # Use the first available chain as default
            default_chain = chain_dirs[0]
            try:
                # Save with default config.json
                save_active_config(default_chain, 'config.json')
                verify_active_config()
                print(f"Created active.txt with default chain: {default_chain}")
            except Exception as e:
                print(f"Error creating active.txt: {e}")
        else:
            print("No valid chain directories found")

def get_active_chain():
    """Get the currently active chain from active.txt"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            return content.split(':')[0]
    except:
        return "unknown"
    
def save_active_config(chain_dir, config_file):
    """Save both chain directory and config file to active.txt"""
    try:
        base_dir = get_base_dir()
        full_config_path = os.path.join(base_dir, chain_dir, config_file)
        print(f"Saving to active.txt: chain_dir={chain_dir}, config_file={config_file}")
        print(f"Full config path: {full_config_path}")
        if not os.path.exists(full_config_path):
            print(f"WARNING: Config file does not exist at {full_config_path}")
            return
        with open('active.txt', 'w') as f:
            f.write(f"{chain_dir}:{config_file}")
    except Exception as e:
        print(f"Error saving active config: {e}")

def verify_active_config():
    """Verify active.txt and corresponding config file"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            print(f"Verification - active.txt contains: {content}")
            
            if ':' not in content:
                print("Invalid format in active.txt - missing separator")
                return False
                
            chain_dir, config_file = content.split(':')
            full_path = os.path.join(get_base_dir(), chain_dir, config_file)
            print(f"Verification - full path: {full_path}")
            
            exists = os.path.exists(full_path)
            print(f"Config file exists: {exists}")
            
            if exists:
                # Try to load the config to verify it's valid
                try:
                    with open(full_path, 'r') as cf:
                        json.load(cf)
                    return True
                except json.JSONDecodeError:
                    print("Config file exists but is not valid JSON")
                    return False
            return False
            
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def initialize_config():
    """Initialize config from active chain and config file"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            if ':' not in content:
                print("Invalid format in active.txt")
                return None
            chain_dir, config_file = content.split(':')
            
            chain_config = load_chain_config(chain_dir, config_file)
            if chain_config:
                return type('Config', (), chain_config)()
            
    except Exception as e:
        print(f"Error initializing config: {e}")
    return None

def load_chain_config(chain_dir, config_file='config.json'):
    """Load config from specified chain directory and config file"""
    try:
        base_dir = get_base_dir()
        config_path = os.path.join(base_dir, chain_dir, config_file)
        print(f"Loading config from: {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config from {chain_dir}/{config_file}: {e}")
        return None
    
def get_active_chain():
    """Get the currently active chain from active.txt"""
    try:
        with open('active.txt', 'r') as f:
            content = f.read().strip()
            return content.split(':')[0]
    except:
        return "unknown"    
    
logger = getLogger(__name__)

# Initialize config at startup
initialize_active_chain()
config = initialize_config()
if config is None:
    # Provide default config or handle error case
    print("Warning: Could not load chain config, using defaults")
    config = type('Config', (), {'L2_chainid': '1', 'L2_token_name': 'ETH', 'L2_output_name': 'USDC'})()

# try:
#     config = load_config() 
# except RuntimeError as e: 
#     print(e)
#     exit(1)  # Exit the program immediately

web3 = Web3(Web3.HTTPProvider(config.infura_url_eth))

#COMMENT OUT THESE FOUR LINES if you want you device to remember the last chain you were on
example_d = [config.L2_chainid, 1]
pickle_out = open("d.pickle","wb")
pickle.dump(example_d, pickle_out)
pickle_out.close()

pickle_in = open("d.pickle","rb")
example_d = pickle.load(pickle_in)
print(example_d[0])




# Create the joystick display
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D27)
BAUDRATE = 24000000
 
spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Turn on the Backlight, can also use to turn off the backlight for power saving
backlight = DigitalInOut(board.D24)
backlight.switch_to_output()
backlight.value = True

WIDTH = disp.width
HEIGHT = disp.height



button_up = Button(20)
button_down = Button(21)
button_select = Button(16)

buttonL = Button(5)
buttonR = Button(26)
buttonU = Button(6) 
buttonD = Button(19)
buttonC = Button(13)

def get_chain_color(chain_id):
    color_map = {
        "137": "#8247e5",  # Polygon (purple)
        "8453": "#0052FF",  # Base (blue)
        "10": "#FF0420",   # Optimism (red)
        "42161": "#28A0F0"  # Arbitrum (royal blue)
    }
    return color_map.get(chain_id, "blue")  # Default to blue if chain_id not found

# Define menu options
MAIN_MENU = ["Balance", "Send", "WalletConnect", "Token Swap", "SD Key Card", "Settings"]
# Update the SD_MENU
SD_MENU = ["View Private Key", "Remove/Swap SD Key", "Shut Down", "Back"]
#swap menu
def get_swap_menu():
    """Dynamically create swap menu with current token names"""
    return [
        f"{config.L2_token_name} to {config.L2_output_name}",
        f"{config.L2_output_name} to {config.L2_token_name}",
        "Back"
    ]

current_menu = MAIN_MENU
selected_index = 0

def get_chain_menu():
    """Dynamically create chain menu by scanning subdirectories"""
    EXCLUDED_DIRS = {'library', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    base_dir = get_base_dir()
    
    try:
        # Get all subdirectories in the executable's directory
        chain_dirs = [d for d in os.listdir(base_dir)
                     if os.path.isdir(os.path.join(base_dir, d)) 
                     and d not in EXCLUDED_DIRS 
                     and os.path.exists(os.path.join(base_dir, d, 'config.json'))]
        
        # Print for debugging
        print(f"Found chain directories: {chain_dirs}")
        
        menu = sorted(chain_dirs) + ["Back"]
        return menu
    except Exception as e:
        print(f"Error scanning chain directories: {e}")
        return ["Error loading chains", "Back"]

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

def get_settings_menu():
    """Dynamically create settings menu with current chain name"""
    active_chain = get_active_chain()
    menu = [
        "Select Chain",
        f"Configure {active_chain}",
        "Back"
    ]
    # Print for debugging
    print(f"Generated settings menu: {menu}")
    return menu


def get_token_pairs_menu():
    """Get available token pairs for the active chain"""
    active_chain = get_active_chain()
    if not active_chain or active_chain == "unknown":
        return [{"display": "Back", "config_file": None}]

    base_dir = get_base_dir()
    chain_path = os.path.join(base_dir, active_chain)
    pairs_menu = []
    
    try:
        # Look for config.json, config2.json, config3.json, etc.
        config_files = sorted([f for f in os.listdir(chain_path) 
                             if f.startswith('config') and f.endswith('.json')],
                            key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)
        
        for config_file in config_files:
            config_path = os.path.join(chain_path, config_file)
            try:
                with open(config_path, 'r') as f:
                    cfg = json.load(f)
                    display_name = f"{cfg['L2_token_name']} and {cfg['L2_output_name']}"
                    pairs_menu.append({
                        'display': display_name,
                        'chain_dir': active_chain,
                        'config_file': config_file
                    })
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                continue
                
    except Exception as e:
        print(f"Error reading directory {chain_path}: {e}")
        return [{"display": "Back", "config_file": None}]

    # Add Back option at the end
    pairs_menu.append({"display": "Back", "config_file": None})
    return pairs_menu

def display_menu():
    # Create a new image with a white background
    img = Image.new('RGB', (WIDTH, HEIGHT), color='white')
    draw = ImageDraw.Draw(img)

    # Load fonts
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    # Get the fill color based on the current L2 chain
    fill_color = get_chain_color(config.L2_chainid)

    # Draw title based on current menu
    if current_menu == MAIN_MENU:
        title = "Pi EVM Wallet"
    elif current_menu == SD_MENU:
        title = "SD Card Menu"
    else:
        title = "Token Swap"

    # Draw the title
    draw.text((WIDTH//2, 15), title, font=font, fill='black', anchor="mm")

    # Draw menu options
    start_y = 45
    spacing = 25
    for i, menu_item in enumerate(current_menu):
        y = start_y + i * spacing
        
        # Get the display text based on whether the item is a string or dict
        if isinstance(menu_item, dict):
            display_text = menu_item['display']
        else:
            display_text = str(menu_item)  # Convert to string in case it's not

        # Draw the selection box if this is the selected item
        if i == selected_index:
            # Draw a filled rectangle for the selected item
            text_bbox = draw.textbbox((10, y), display_text, font=font)
            padding = 5
            draw.rectangle([
                text_bbox[0] - padding,
                text_bbox[1] - padding,
                text_bbox[2] + padding,
                text_bbox[3] + padding
            ], fill=fill_color)
            # Draw the text in white
            draw.text((10, y), display_text, font=font, fill='white')
        else:
            # Draw unselected items in black
            draw.text((10, y), display_text, font=font, fill='black')

    # Draw navigation hints
    draw.text((WIDTH - 98, HEIGHT - 20), "↑↓: Navigate", font=small_font, fill='black')
    draw.text((10, HEIGHT - 20), "→: Select", font=small_font, fill='black')
    draw.text((WIDTH - 70, HEIGHT - 32), "←: Back", font=small_font, fill='black')

    # Display the image on the screen
    disp.image(img)

def handle_button_up():
    global selected_index
    selected_index = (selected_index - 1) % len(current_menu)
    display_menu()

def handle_button_down():
    global selected_index
    selected_index = (selected_index + 1) % len(current_menu)
    display_menu()

def handle_button_select():
    global current_menu, selected_index, config
    
    selected_option = current_menu[selected_index]
    
    # Print for debugging
    print(f"Selected option: {selected_option}")
    print(f"Current menu: {current_menu}")

    if current_menu == MAIN_MENU:
        if selected_option == "Settings":
            current_menu = get_settings_menu()
            selected_index = 0
        elif selected_option == "Token Swap":
            current_menu = get_token_pairs_menu()
            selected_index = 0
        elif selected_option == "SD Key Card":  # Add this condition
            current_menu = SD_MENU
            selected_index = 0
        else:
            execute_menu_option(selected_option)
    
    elif current_menu == SD_MENU:  # Add this condition
        execute_sd_option(selected_option)
    
    elif current_menu == get_settings_menu():  # Settings menu handling
        if selected_option == "Select Chain":
            chain_menu = get_chain_menu()
            if chain_menu:
                current_menu = chain_menu
                selected_index = 0
        elif selected_option == "Back":
            current_menu = MAIN_MENU
            selected_index = 0
    
    elif isinstance(current_menu[selected_index], dict):  # Token pairs menu
        selected_pair = current_menu[selected_index]
        if selected_pair['display'] == "Back":
            current_menu = MAIN_MENU
            selected_index = 0
        else:
            try:
                save_active_config(selected_pair['chain_dir'], selected_pair['config_file'])
                verify_active_config()
                config = initialize_config()
                if config:
                    # Force refresh the menu with new config values
                    current_menu = get_swap_menu()  # This will use the new config values
                    selected_index = 0
                    # Force a menu redraw
                    display_menu()
                else:
                    display_message("Error", "Failed to load configuration")
                    time.sleep(1)
                    # If config failed, go back to token pairs menu
                    current_menu = get_token_pairs_menu()
                    selected_index = 0
            except Exception as e:
                print(f"Error selecting token pair: {e}")
                display_message("Error", "Failed to select token pair")
                time.sleep(1)
                # On error, go back to token pairs menu
                current_menu = get_token_pairs_menu()
                selected_index = 0
    
    elif current_menu == get_swap_menu():  # Swap direction menu
        if selected_option == "Back":
            current_menu = get_token_pairs_menu()
            selected_index = 0
        else:
            execute_swap_option(selected_option)
    
    elif isinstance(current_menu, list) and "Back" in current_menu:  # Chain selection menu
        if selected_option == "Back":
            current_menu = get_settings_menu()
            selected_index = 0
        elif selected_option != "Error loading chains":
            try:
                save_active_config(selected_option, 'config.json')
                verify_active_config()
                config = initialize_config()
                display_message("Chain Updated", f"Switched to {selected_option}")
                time.sleep(1)
                current_menu = get_settings_menu()
                selected_index = 0
            except Exception as e:
                print(f"Error switching chain: {e}")
                display_message("Error", "Failed to switch chain")
                time.sleep(1)

    display_menu()

def execute_swap_option(option):
    from tokenswap import swap_l2_token_to_output, swap_output_to_l2_token
    
    print(f"Executing swap for option: {option}")
    
    try:
        if option == f"{config.L2_token_name} to {config.L2_output_name}":
            result = swap_l2_token_to_output(
                disp=disp,
                get_address=get_address,
                get_private_key=get_private_key
            )
        elif option == f"{config.L2_output_name} to {config.L2_token_name}":
            result = swap_output_to_l2_token(
                disp=disp,
                get_address=get_address,
                get_private_key=get_private_key
            )
        else:
            raise ValueError(f"Invalid swap option: {option}")

        if result['success']:
            display_message(
                "Swap Successful",
                f"Hash: {result['tx_hash'][:10]}...",
                f"Gas used: {result['gas_used']}"
            )
        else:
            display_message("Swap Failed", result.get('message', 'Unknown error'))
        
        time.sleep(2)
        
    except Exception as e:
        print(f"Error during swap execution: {e}")
        display_message("Swap Error", str(e))
        time.sleep(2)
    
    # Return to main menu
    global current_menu, selected_index
    current_menu = MAIN_MENU
    selected_index = 0
    display_menu()

def handle_button_back():
    global current_menu, selected_index
    
    # Print for debugging
    print(f"Back button pressed. Current menu: {current_menu}")
    
    if current_menu == MAIN_MENU:
        # Already at main menu, do nothing
        pass
    elif current_menu == SD_MENU:
        current_menu = MAIN_MENU
        selected_index = 0
    elif current_menu == get_settings_menu():
        current_menu = MAIN_MENU
        selected_index = 0
    elif isinstance(current_menu, list) and "Back" in current_menu:  # Chain menu
        current_menu = get_settings_menu()
        selected_index = 0
    elif isinstance(current_menu[0], dict):  # Token pairs menu
        current_menu = MAIN_MENU
        selected_index = 0
    else:
        current_menu = MAIN_MENU
        selected_index = 0
    
    display_menu()

def execute_menu_option(option):
    if option == "Balance":
        display_loading()
        home_screen = HomeScreen(disp, example_d)
        home_screen.render()
        while True:
            if buttonL.is_pressed:
                break
            time.sleep(0.1)
        display_menu()

    elif option == "Send":
        send_transaction()
    elif option == "WalletConnect":
        try:
            wallet_connect(disp, example_d, get_private_key, get_address, buttonL)
        except ImportError:
            display_message("Error", "WalletConnect not installed", "Please install required modules")
            time.sleep(2)
            display_menu()
    elif option == "Settings":
        open_settings()
    else:
        print(f"Unknown option: {option}")

def send_transaction():
    # Implement send transaction logic here
    print("Initiating send transaction...")
    # This might involve multiple steps like entering recipient,
    # amount, confirming transaction, etc.

def open_settings():
    # Implement settings menu logic here
    print("Opening settings...")
    # This might involve displaying a sub-menu of settings options

def execute_sd_option(option):
    global current_menu, selected_index
    if option == "View Private Key":
        display_private_key()
    elif option == "Remove/Swap SD Key":
        if safe_unmount_sd():
            current_menu = MAIN_MENU
            selected_index = 0
            display_message("SD Card Unmounted", "Safe to remove card", "Insert new card to swap keys")
        else:
            display_message("Unmount Failed", "Please try again", "If still not, Shutdown Device")
    elif option == "Back":
        current_menu = MAIN_MENU
        selected_index = 0
    elif option == "Shut Down":
        shutdown_device()
    else:
        print(f"Unknown SD option: {option}")
    display_menu()

def display_message(title, message, submessage=""):
    img = Image.new('RGB', (WIDTH, HEIGHT), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    draw.text((WIDTH//2, 40), title, font=font, fill='black', anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2), message, font=small_font, fill='black', anchor="mm")
    if submessage:
        draw.text((WIDTH//2, HEIGHT//2 + 30), submessage, font=small_font, fill='black', anchor="mm")
    draw.text((10, HEIGHT - 20), "Press ← to go back", font=small_font, fill='black')

    disp.image(img)

    # Wait for back button press
    while True:
        if buttonL.is_pressed:
            break
        time.sleep(0.1)

    display_menu()  # Return to the menu after pressing back

def shutdown_device():
    display_message("Shutting Down", "Please wait...")
    time.sleep(2)  # Give time for the message to be displayed

    # Attempt to safely unmount the SD card before shutdown
    safe_unmount_sd()

    # Perform the shutdown
    subprocess.run(["sudo", "shutdown", "-h", "now"])

    # This line will only be reached if the shutdown command fails
    display_message("Shutdown Failed", "Please turn off manually")

def display_private_key():
    private_key = get_private_key()
    if private_key:
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)

        # Split key in two
        key_length = len(private_key)
        string1 = private_key[:key_length//2]
        string2 = private_key[key_length//2:]

        draw.text((1, 1), str(string1), (200, 15, 20), font=font)
        draw.text((1, 10), str(string2), (200, 15, 20), font=font)
        draw.text((1, 220), 'Private Key', (200, 15, 20), font=font)
        draw.text((120, 220), 'App Stores', (200, 15, 20), font=font)

        # Private key QR code
        qr = qrcode.QRCode(box_size=3, border=2)
        qr.add_data(private_key)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="white", back_color="black")
        qr_img = qr_img.resize((110, 110))
        img.paste(qr_img, (5, 20))

        # App links QR code
        qr = qrcode.QRCode(box_size=3, border=2)
        applinks = "https://linktr.ee/piethereumwallet"
        qr.add_data(applinks)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="white", back_color="black")
        qr_img = qr_img.resize((110, 110))
        img.paste(qr_img, (125, 20))

        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        draw.text((5, 230), 'Be Extremely Careful with Private Key', (200, 15, 20), font=font)

        disp.image(img)
        print(f"Private key: {private_key}")
        print("Private key QR code and app links displayed on screen.")
        time.sleep(20)  # Display for 20 seconds
    else:
        print("No private key found or failed to retrieve it.")
        display_message("Key Error", "Failed to retrieve key")

    display_menu()  # Return to menu after displaying

def mount_sd(device):
    mount_point = "/mnt/sdcard"
    try:
        subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)
        subprocess.run(["sudo", "mount", device, mount_point], check=True)
        print("SD card mounted successfully.")
#        display_message("SD Card Detected", "Key ready for use2")
        return True
    except subprocess.CalledProcessError:
        print("Failed to mount SD card.")
        return False

def safe_unmount_sd():
    global wallet_data, private_key

    try:
        # Sync to ensure all pending writes are completed
        subprocess.run(["sudo", "sync"], check=True)
        # Unmount the SD card
        subprocess.run(["sudo", "umount", "/mnt/sdcard"], check=True)
        print("SD card safely unmounted.")

        # Clear all variables that might contain sensitive information
        wallet_data = None
        private_key = None

        # Force garbage collection to remove any lingering references
        gc.collect()

        return True
    except subprocess.CalledProcessError:
        print("Failed to safely unmount SD card.")
        display_message("Unmount Failed", "Shutting down for safety")
        time.sleep(5)  # Give user time to read the message
        os.system("sudo shutdown -h now")
        return False

def check_private_key():
    try:
        with open("/mnt/sdcard/wallet.json", "r") as f:
            wallet_data = json.load(f)
            return "private_key" in wallet_data and "address" in wallet_data
    except (IOError, json.JSONDecodeError):
        print("Failed to read or parse wallet.json from SD card.")
    return False

def get_private_key():
    if not validate_wallet_data():
        return None
    try:
        with open("/mnt/sdcard/wallet.json", "r") as f:
            wallet_data = json.load(f)
            private_key = wallet_data.get("private_key")
            if not private_key:
                print("Error: Private key is missing from wallet.json")
                return None
            return private_key
    except (IOError, json.JSONDecodeError) as e:
        print(f"Failed to read or parse wallet.json from SD card: {str(e)}")

def get_address():
    if not validate_wallet_data():
        return None
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

def validate_wallet_data():
    try:
        with open("/mnt/sdcard/wallet.json", "r") as f:
            wallet_data = json.load(f)

        private_key = wallet_data.get("private_key")
        stored_address = wallet_data.get("address")

        if not private_key or not stored_address:
            print("Error: Private key or address is missing from wallet.json")
            return False

        # Derive address from private key
        account = Account.from_key(private_key)
        derived_address = account.address

        if Web3.to_checksum_address(derived_address) != Web3.to_checksum_address(stored_address):
            print("Error: Stored address does not match the address derived from the private key")
            return False

        return True
    except (IOError, json.JSONDecodeError):
        print("Failed to read or parse wallet.json from SD card.")
        return False

def generate_new_key():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    print("SAVE BUT DO NOT SHARE THIS:", private_key)
    acct = Account.from_key(private_key)
    address = acct.address
    print("Address:", address)

    wallet_data = {
        "private_key": private_key,
        "address": address
    }

    try:
        with open("/mnt/sdcard/wallet.json", "w") as f:
            json.dump(wallet_data, f)
        print("Stored Keys Successfully")
        display_message("New Wallet Created", f"Address: {address[:6]}...{address[-4:]}", "Keys stored on SD card")
        return True
    except IOError:
        print("Failed to write new key to SD card.")
        return False

def check_and_setup_sd_card():
    sd_devices = glob.glob('/dev/sd*')
    for device in sd_devices:
        if os.path.exists(device) and device.endswith('1'):
            print(f"SD card detected: {device}")
            if not is_mounted(device):
                if mount_sd(device):
                    if check_private_key():
                        print("Valid private key found on SD card.")
                        return device
                    else:
                        print("No valid private key found. Generating new key...")
                        if generate_new_key():
                            print("New private key generated and saved.")
                            return device
                        else:
                            print("Failed to generate new key.")
                            safe_unmount_sd()
            else:
                print("SD card already mounted.")
                if check_private_key():
                    print("Valid private key found on SD card.")
                    return device
    print("No SD card with valid private key detected.")
    return None

def is_mounted(device):
    try:
        output = subprocess.check_output(["findmnt", "-n", "-o", "TARGET", device]).decode().strip()
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def display_loading():
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    im = Image.new("RGB", (240, 240), "white")
    d = ImageDraw.Draw(im)
    d.text((120, 120), "Loading...", fill="black", anchor="ms", font=font)
    disp.image(im)

def swap_l2_token_to_output(disp, get_address, get_private_key):
    """
    Handles swapping from L2 token to output token
    """
    try:
        # Get user's address and private key
        address = get_address()
        private_key = get_private_key()
        
        if not address or not private_key:
            return {
                'success': False,
                'message': 'Failed to get wallet credentials'
            }

        # Display "Preparing Swap" message
        display_message("Preparing Swap", 
                       f"From: {config.L2_token_name}",
                       f"To: {config.L2_output_name}")
        
        # Initialize Web3 with the appropriate network
        w3 = Web3(Web3.HTTPProvider(config.infura_url_eth))
        
        # Add your swap implementation here
        # This should include:
        # 1. Getting token approvals
        # 2. Getting swap quote
        # 3. Executing the swap
        
        # For now, return a mock success response
        return {
            'success': True,
            'tx_hash': '0x...',
            'block_number': 0,
            'gas_used': 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def swap_output_to_l2_token(disp, get_address, get_private_key):
    """
    Handles swapping from output token to L2 token
    """
    try:
        # Get user's address and private key
        address = get_address()
        private_key = get_private_key()
        
        if not address or not private_key:
            return {
                'success': False,
                'message': 'Failed to get wallet credentials'
            }

        # Display "Preparing Swap" message
        display_message("Preparing Swap", 
                       f"From: {config.L2_output_name}",
                       f"To: {config.L2_token_name}")
        
        # Initialize Web3 with the appropriate network
        w3 = Web3(Web3.HTTPProvider(config.infura_url_eth))
        
        # Add your swap implementation here
        # This should include:
        # 1. Getting token approvals
        # 2. Getting swap quote
        # 3. Executing the swap
        
        # For now, return a mock success response
        return {
            'success': True,
            'tx_hash': '0x...',
            'block_number': 0,
            'gas_used': 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def main_loop():
    global current_menu
    display_menu()
    last_sd_state = False
    while True:
        if button_up.is_pressed:
            handle_button_up()
            time.sleep(0.2)  # Debounce
        elif button_down.is_pressed:
            handle_button_down()
            time.sleep(0.2)  # Debounce
        elif button_select.is_pressed:
            handle_button_select()
            time.sleep(0.2)  # Debounce
        elif buttonL.is_pressed:
            handle_button_back()
            time.sleep(0.2)  # Debounce

        # Check for SD card insertion/removal and valid private key
        current_sd_state = check_and_setup_sd_card() is not None
        if current_sd_state != last_sd_state:
            if current_sd_state:
                print("SD card with valid private key inserted and mounted.")
                display_message("SD Card Detected", "Key ready for use")
                current_menu = MAIN_MENU
                selected_index = 0
            else:
                print("SD card removed or no valid private key found.")
                display_message("SD Card Removed", "Insert card to continue")
                current_menu = SD_MENU
                selected_index = 0
            display_menu()
            last_sd_state = current_sd_state

        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

try:
    main_loop()
except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    print("Safely unmounting SD card before exit...")
    safe_unmount_sd()
    # Clean up code here if needed
    pass
