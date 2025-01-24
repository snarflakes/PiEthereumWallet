#Created by Snarflakes.
#To Satoshi and Vitalik, saludos amigos.
#GNU General Public License v3.0
#Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, 
#under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. 


import os
import sys
import logging
from logging import getLogger
import requests
import io
import glob
import PIL
import gc
from signal import pause
from PIL import Image, ImageOps
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from eth_account import Account
from home_screen import HomeScreen
from tokenswap import swap_l2_token_to_output, swap_output_to_l2_token

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
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

#qr code modules
       #import numpy as np
import argparse
import datetime
from csv import reader
       #import cv2
import imutils
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

#walletconnect camera scan
from walletconnect import wallet_connect

#load and process external variables from config.json
from config_loader import load_config

try:
    config = load_config() 

except RuntimeError as e: 
    print(e)
    exit(1)  # Exit the program immediately

logger = getLogger(__name__)

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
MAIN_MENU = ["Balance", "Send", "WalletConnect", f"{config.L2_name} Token Swap", "SD Key Card", "Settings"]
# Update the SD_MENU
SD_MENU = ["View Private Key", "Remove/Swap SD Key", "Shut Down", "Back"]
#swap menu
SWAP_MENU = [f"{config.L2_token_name} to {config.L2_output_name}", f"{config.L2_output_name} to {config.L2_token_name}", "Back"]

current_menu = MAIN_MENU
selected_index = 0

def display_menu():
    # Create a new image with a white background
    img = Image.new('RGB', (WIDTH, HEIGHT), color='white')
    draw = ImageDraw.Draw(img)

    # Load fonts
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    # Get the fill color based on the current L2 chain
    fill_color = get_chain_color(config.L2_chainid)

    # Draw title
    if current_menu == MAIN_MENU:
        title = "Pi EVM Wallet"
    elif current_menu == SWAP_MENU:
        title = f"{config.L2_name} Token Swap"
    else:
        title = "Pi EVM Wallet"  # Default title if menu is not recognized
    draw.text((10, 10), title, font=font, fill='black')


    # Draw menu options
    for i, option in enumerate(current_menu):
        y = 40 + i * 30
        if i == selected_index:
            # Draw a filled rectangle for the selected item
            draw.rectangle([0, y, WIDTH, y + 25], fill=fill_color)
            draw.text((10, y), option, font=font, fill='white')
        else:
            draw.text((10, y), option, font=font, fill='black')

    # Draw navigation hints
    draw.text((WIDTH - 98, HEIGHT - 20), "↑↓: Navigate", font=small_font, fill='black')
    draw.text((10, HEIGHT - 20), "⏎: Select", font=small_font, fill='black')
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
    global current_menu, selected_index
    if current_menu == MAIN_MENU:
        if current_menu[selected_index] == "SD Key Card":
            current_menu = SD_MENU
            selected_index = 0
        elif current_menu[selected_index] == f"{config.L2_name} Token Swap":
            current_menu = SWAP_MENU
            selected_index = 0
        else:
            execute_menu_option(current_menu[selected_index])
    elif current_menu == SD_MENU:
        if current_menu[selected_index] == "Back":
            current_menu = MAIN_MENU
            selected_index = 0
        else:
            execute_sd_option(current_menu[selected_index])
    elif current_menu == SWAP_MENU:
        if current_menu[selected_index] == "Back":
            current_menu = MAIN_MENU
            selected_index = 0
        else:
            execute_swap_option(current_menu[selected_index])
    display_menu()

def execute_swap_option(option):
    if option == f"{config.L2_token_name} to {config.L2_output_name}":
        # Implement swap from L2_token to L2_output
        print(f"Swapping {config.L2_token_name} to {config.L2_output_name}")
        result = swap_l2_token_to_output(disp, get_address, get_private_key)
        if result['success']:
            print(f"Swap completed successfully. Transaction hash: {result['tx_hash']}")
            print(f"Block number: {result['block_number']}, Gas used: {result['gas_used']}")
        else:
            print(f"Swap failed: {result['message']}")

    elif option == f"{config.L2_output_name} to {config.L2_token_name}":
        # Implement swap from L2_output to L2_token
        print(f"Swapping {config.L2_output_name} to {config.L2_token_name}")
        result = swap_output_to_l2_token(disp, get_address, get_private_key)
        if result['success']:
            print(f"Swap completed successfully. Transaction hash: {result['tx_hash']}")
            print(f"Block number: {result['block_number']}, Gas used: {result['gas_used']}")
        else:
            print(f"Swap failed: {result['message']}")

    else:
        print(f"Unknown swap option: {option}")
    
    # After swap operation, return to main menu
    global current_menu, selected_index
    current_menu = MAIN_MENU
    selected_index = 0
    display_menu()

def handle_button_back():
    global current_menu, selected_index
    if current_menu == MAIN_MENU:
        # Already at main menu, do nothing
        pass
    elif current_menu == SD_MENU:
        current_menu = MAIN_MENU
        selected_index = 0
    else:
        # For any other submenu or screen, go back to main menu
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
         wallet_connect(disp, example_d, get_private_key, get_address, buttonL)
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
    return None

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
        
        if Web3.toChecksumAddress(derived_address) != Web3.toChecksumAddress(stored_address):
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
