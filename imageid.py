#Created by Snarflakes.
#To Satoshi and Vitalik, saludos amigos.
#GNU General Public License v3.0
#Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, 
#under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. 

import csv
import os
import sys
import logging
import requests
import io
import PIL
from signal import pause
from PIL import Image, ImageOps
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

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
import numpy as np
import argparse
import datetime
from csv import reader
import cv2
import imutils
from csv import reader
import pyzbar.pyzbar as pyzbar

#check internet
import socket

#screen rotate
import pickle

#random
from random import randint

import string
import numpy
import json
import qrcode

#web3
from web3 import Web3 
from eth_account import Account
import secrets
from uniswap import Uniswap

#walletconnect
from logging import basicConfig, DEBUG
basicConfig(level=DEBUG)
from time import sleep
from pywalletconnect.client import WCClient, WCClientInvalidOption

from siwe import SiweMessage

#more web3
from eth_account.messages import encode_defunct
from web3.auto import w3
from eth_account import messages


#connect web3 host/node info
#infura_url = 'https://mainnet.infura.io/v3/aead12b7af1947b19f1b1d9b00d7b9b8'
#infura_url = 'https://eth-mainnet.g.alchemy.com/v2/e2Uyo6jgkqXVx0bYGSyR7XfABGh4xJYT'
infura_url = 'https://mainnet.infura.io/v3/6e3044367252450f96047f6e34833089'
#infura_url = 'https://goerli.infura.io/v3/6e3044367252450f96047f6e34833089' 
web3 = Web3(Web3.HTTPProvider(infura_url))

#Primary Token Pairs: token_address's and ETH(don't forget to set custom ABI if changing USDC to a new token) Token_address is the main displayed token on home screen (needs its own abi for proper wallet amount)
#usdc token_address goerli
#token_address = '0x07865c6E87B9F70255377e024ace6630C1Eaa37F'
#token_address ETH mainnet
token_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
eth = "0x0000000000000000000000000000000000000000"

#example_d = [1,137]
#pickle_out = open("d.pickle","wb")
#pickle.dump(example_d, pickle_out)
#pickle_out.close()

pickle_in = open("d.pickle","rb")
example_d = pickle.load(pickle_in)
print(example_d[0])

#construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="/boot/ethereumwallet.csv", help="path to output CSV file containing qrcode data")
args = vars(ap.parse_args())


#open the output CSV file for writing and initialize the set of qrcodes found thus far
csv2 = open(args["output"], "a")
found = set()

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

print("""
image.py - Display an NFT image weblink on the IPS LCD.

""")

opened_file = open('/boot/ethereumwallet.csv')
read_file = reader(opened_file)
apps_data = list(read_file)


def splash_screen():
    print("drawing splash screen")
    picture_1 = Image.open("nftydaze4.jpg")
    image = picture_1.resize((WIDTH, HEIGHT))
    disp.image(image)



def internet(host="8.8.8.8", port=53, timeout=3):
	"""
	Host: 8.8.8.8 (google-public-dns-a.google.com)
	OpenPort: 53/tcp
	Service: domain (DNS/TCP)
	"""
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except socket.error as ex:
		print(ex)
		return False

def shut_down():
    print("Shutting Down")
    image = Image.open('nftydaze4.jpg')
    image = image.resize((WIDTH, HEIGHT))
    print('Drawing image')
    disp.image(image)
    time.sleep(5)
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    disp.image(img)
    time.sleep(0.25)

    os.system("sudo shutdown -h now")
    while 1:
        time.sleep(1)


def refresh():
    if internet():
        print("Refresh")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        im = Image.new("RGB", (240, 240), (223,255,0))
        d = ImageDraw.Draw(im)
        d.text((120, 90), "Refreshing Wallet", fill="black", anchor="ms", font=font)
        d.text((120, 110), "Info...", fill="black", anchor="ms", font=font)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        d.text((55, 200), "Etherscan", fill="black", anchor="ms", font=font)
        d.text((55, 210), "Transaction", fill="black", anchor="ms", font=font)
        d.text((55, 220), "History", fill="black", anchor="ms", font=font)

# Display qrcode link to etherscan wallet info
        disp.image(im)

        qr = qrcode.QRCode()
        qr.add_data(f"https://etherscan.io/address/{(apps_data[0][1])}")
#    qr.add_data(wallet)
        qr.make()
        imgrender = qr.make_image(fill_color="black", back_color="#FAF9F6")

#it did say WIDTH,HEIGHT)
        imgrender2 = imgrender.resize((120, 120))

#check for bad link
        try:
            disp.image(imgrender2)
#            time.sleep(0.25)            
        except PIL.UnidentifiedImageError:
            print("Bad Link/File")

#        disp.image(im)
        time.sleep(8)
        homescreen()

    else:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        im = Image.new("RGB", (240, 240), "red")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
        d.text((120, 120), "You are out", fill="black", anchor="ms", font=font)
        d.text((120, 140), "of wifi range", fill="black", anchor="ms", font=font)
        d.text((120, 160), "or wifi setup", fill="black", anchor="ms", font=font)
        d.text((120, 180), "went wrong.", fill="black", anchor="ms", font=font)
        d.text((120, 200), "Move closer to router", fill="black", anchor="ms", font=font)
        d.text((120, 220), "__________________", fill="black", anchor="ms", font=font)

#        im = im.rotate()
        disp.image(im)
        print("no internet available")
 
 
def no_NFT():
    global apps_data
    opened_file = open('/boot/ethereumwallet.csv')
    read_file = reader(opened_file)
    apps_data = list(read_file)
    if (len(apps_data)) == 0:
        print("No wallet stored")
        if internet():
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            im = Image.new("RGB", (240, 240), "antiquewhite")
            d = ImageDraw.Draw(im)
            d.text((120, 100), "Hi! Generating...", fill="black", anchor="ms", font=font)
            d.text((120, 120), "A New ETH Wallet!", fill="black", anchor="ms", font=font)
            d.text((120, 200), "Unit shuts down if", fill="black", anchor="ms", font=font)
            d.text((120, 220), "no internet.", fill="black", anchor="ms", font=font)

#       im = im.rotate()
            disp.image(im)
            time.sleep(20)

# generate a wallet
            priv = secrets.token_hex(32)
            private_key = "0x" + priv
            print ("SAVE BUT DO NOT SHARE THIS:", private_key)
            acct = Account.from_key(private_key)
            print(acct)
            print("Address:", acct.address)
            time.sleep(0.25)

# print current account value
            balance = web3.eth.getBalance(acct.address)
            print('Account Balance: ', (web3.fromWei(balance, 'Ether')))

#store address in ethereumwallet.csv
            csv2.write("{},{},{}\n".format(datetime.datetime.now(), acct.address, private_key))
            csv2.flush()

##Screen to Confirm User Scanned
            print("Stored Keys Successfully")
            opened_file = open('/boot/ethereumwallet.csv')
            read_file = reader(opened_file)
            apps_data = list(read_file)

        else:
            print("still no internet")
        #cut and paste internet issue below? Turn into a function probably
            time.sleep(40)
            print("shutting down")
            shutdown()

def push_button2():
    start_time=time.time()
    hold_time = 4
    diff=0

    while button2.is_active and (diff <hold_time) :
        now_time=time.time()
        diff=-start_time+now_time

    if diff < hold_time :
        print("login")
        qr_capture()
    else:
        flip_screen()
#        print("show private key")
#        showkey()


def push_button():
    start_time=time.time()
    hold_time = 2
    diff=0

    while button3.is_active and (diff <hold_time) :
        now_time=time.time()
        diff=-start_time+now_time

    if diff < hold_time :
        refresh()

    else:
        transactions()

def transactions():

    print("transaction button pressed")
    if internet():
        print("internet")
        
    else:
       print("no internet available")

    try:
        wallet = apps_data[0][1]
        secretkey = apps_data[0][2]

    except IndexError:
        print("Empty data")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        im = Image.new("RGB", (240, 240), "red")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
        d.text((120, 120), "No ethereum wallet", fill="black", anchor="ms", font=font)
        d.text((120, 140), "are loaded yet", fill="black", anchor="ms", font=font)
        d.text((120, 160), "Shutting Down", fill="black", anchor="ms", font=font)
        d.text((120, 180), "Turn on unit again", fill="black", anchor="ms", font=font)
        d.text((120, 200), "when you are ready", fill="black", anchor="ms", font=font)
        d.text((120, 220), "to scan a QRcode", fill="black", anchor="ms", font=font)
        disp.image(im)
        time.sleep(20)
        shut_down()

#transparency for boxes(gas costs?)
    TINT_COLOR = (0, 0, 0)  # Black
    TRANSPARENCY = .3  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    img = Image.new("RGBA", (240, 240), "white")
    d = ImageDraw.Draw(img)

#add in a image layer ontop of white background, way of eliminated transparent layer too
    picture_1 = Image.open("nftydaze4.jpg").convert('RGBA')
    image = picture_1.resize((50, 50))
    img.paste(image, (50, 50))
    d.text((80, 100), "USDC->ETH", fill="black", anchor="ms", font=font)
    d.text((84, 120), "  Transaction Sent...", fill="black", anchor="ms", font=font)
    disp.image(img)

#run different function that just generates blank screen with name on it

# Make a blank image the same size as the image for the rectangle, initialized
# to a fully transparent (0% opaque) version of the tint color, then draw a
# semi-transparent version of the square on it.
    overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
#    draw.rectangle(((10, 200), (100, 240)), fill=TINT_COLOR+(OPACITY,))
    draw.rounded_rectangle(((10, 140), (100, 220)), fill=TINT_COLOR+(OPACITY,), outline="black", width=1, radius=3)

#draw.rounded_rectangle((50, 50, 150, 150), fill="blue", outline="yellow", width=3, radius=7)

#write on screen and pull up Ethereum account value
    acct = Account.from_key(secretkey)
    print(acct)
    print("Address:", acct.address)
    print(wallet)
    time.sleep(0.25)
# print current ETH account value
    balance = web3.eth.getBalance(acct.address)
    print('Account Balance: ', (web3.fromWei(balance, 'Ether')))

# USDC ABI in order to print amount of USDC present
    abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationUsed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"}],"name":"Blacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newBlacklister","type":"address"}],"name":"BlacklisterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"burner","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newMasterMinter","type":"address"}],"name":"MasterMinterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"},{"indexed":false,"internalType":"uint256","name":"minterAllowedAmount","type":"uint256"}],"name":"MinterConfigured","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldMinter","type":"address"}],"name":"MinterRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":false,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[],"name":"Pause","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newAddress","type":"address"}],"name":"PauserChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newRescuer","type":"address"}],"name":"RescuerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"}],"name":"UnBlacklisted","type":"event"},{"anonymous":false,"inputs":[],"name":"Unpause","type":"event"},{"inputs":[],"name":"CANCEL_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"RECEIVE_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TRANSFER_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"authorizationState","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"blacklister","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"cancelAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"},{"internalType":"uint256","name":"minterAllowedAmount","type":"uint256"}],"name":"configureMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"currency","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"decrement","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"increment","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"tokenName","type":"string"},{"internalType":"string","name":"tokenSymbol","type":"string"},{"internalType":"string","name":"tokenCurrency","type":"string"},{"internalType":"uint8","name":"tokenDecimals","type":"uint8"},{"internalType":"address","name":"newMasterMinter","type":"address"},{"internalType":"address","name":"newPauser","type":"address"},{"internalType":"address","name":"newBlacklister","type":"address"},{"internalType":"address","name":"newOwner","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"newName","type":"string"}],"name":"initializeV2","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lostAndFound","type":"address"}],"name":"initializeV2_1","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"isBlacklisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"masterMinter","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"minterAllowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pauser","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"receiveWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"removeMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"tokenContract","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"rescueERC20","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rescuer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"transferWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"unBlacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newBlacklister","type":"address"}],"name":"updateBlacklister","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newMasterMinter","type":"address"}],"name":"updateMasterMinter","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newPauser","type":"address"}],"name":"updatePauser","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newRescuer","type":"address"}],"name":"updateRescuer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]')

#Specific Token desired for displaying amount to terminal
#    token_address = '0x07865c6E87B9F70255377e024ace6630C1Eaa37F'
    token_contract = web3.eth.contract(address=token_address, abi=abi) # declaring the token contract
    token_balance = token_contract.functions.balanceOf(acct.address).call() # returns int with balance, without decimals

#need to put .call() at the end to call the smart contract #ALSO need to convert supply to Wei which is 6-18 decimal places)
    print('TokenBalance: ', token_balance/1000000)
#print('Contract Name: ', contract.functions.name().call())
    print('Symbol: ', token_contract.functions.symbol().call())

    req = requests.get('https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=UHM6EST7PIJ9RIKCYVRSA1NEV1TFJB1PYQ')
    t = json.loads(req.content)

#print(t)
    print('SafeGasPrice', t['result']['SafeGasPrice'])
    print('ProposeGasPrice', t['result']['ProposeGasPrice'])
    print('FastGasPrice', t['result']['FastGasPrice'])

    gas = t['result']['FastGasPrice']
    print(type(gas))
    print(gas)

# define the sender address and prints the balance (in ETH)
    balance = web3.eth.get_balance(wallet)
    print("This address has:", web3.fromWei(balance, "ether"), "ETH")

##################check for presence of USDC or defined token_address token
    if token_balance == 0:
        print("Insufficient USDC for transaction to be performed")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        im = Image.new("RGB", (240, 240), "orange")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "Insufficient Funds", fill="black", anchor="ms", font=font)
        d.text((120, 120), "for Transaction:", fill="black", anchor="ms", font=font)
        d.text((120, 160), "USDC amount is 0", fill="black", anchor="ms", font=font)
        d.text((120, 180), "Recheck USDC present", fill="black", anchor="ms", font=font)
        disp.image(im)
        time.sleep(10)
        homescreen()
        return

#############################################################################################transaction
#Swap using uniswap-python module/ address's pulled at top of this function
    version = 3                       # specify which version of Uniswap to use
    uniswap = Uniswap(address=wallet, private_key=secretkey, version=version, provider=infura_url)

#Terminal Display of swap quote
    print("1 usdc value in eth")
#    print(uniswap.get_price_input(token_address, eth, 10**6, fee=500))
    price = (uniswap.get_price_input(token_address, eth, 10**6, fee=500)/ (10 ** 18))
    print('%.08f' % price)

#Actual Swap Code need different "1*10**6" depending on specific token, most are defined as this 1*10**18
    try:
        tx_hash = uniswap.make_trade(token_address, eth, token_balance, fee=500)
        print("USDC to ETH tx sent")
        print(web3.toHex(tx_hash))
        time.sleep(3)
    except ValueError:
        print("Insufficient funds for swap transaction")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        im = Image.new("RGB", (240, 240), "orange")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "Failed Transaction", fill="black", anchor="ms", font=font)
        d.text((120, 120), "Insufficient Gas Funds", fill="black", anchor="ms", font=font)
        d.text((120, 140), "for Swap Transaction:", fill="black", anchor="ms", font=font)
        d.text((120, 160), "Recheck ETH amount(for gas)", fill="black", anchor="ms", font=font)
#        im = im.rotate()
        disp.image(im)
        time.sleep(20)
        homescreen()
        return

#draw token values
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
#        im = Image.new("RGB", (150, 50))
    d = ImageDraw.Draw(overlay)                
    d.text((50, 175), " Tx Status in", fill="black", anchor="ms", font=font)
    d.text((50, 195), "QRcode->", fill="black", anchor="ms", font=font)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    d.text((60, 235), "Press Button to Refresh", fill="black", anchor="ms", font=font)

# Alpha composite these two images together to obtain the desired result.
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB") # Remove alpha for saving in jpg format.
    disp.image(img)

# add qrcode to right corner
    qr = qrcode.QRCode()
    qr.add_data(f"https://etherscan.io/tx/{web3.toHex(tx_hash)}")
#    qr.add_data(wallet)
    qr.make()
    imgrender = qr.make_image(fill_color="black", back_color="#FAF9F6")

#it did say WIDTH,HEIGHT)
    imgrender2 = imgrender.resize((120, 120))

#check for bad link
    try:
        disp.image(imgrender2)
#            time.sleep(0.25)            
    except PIL.UnidentifiedImageError:
        print("Bad Link/File")

#def polygon():

#    from subprocess import Popen, PIPE
#    process = Popen(['python3','polygonimage.py'], stdout=PIPE, stderr=PIPE)
#    exit()

def flip_screen():
    example_d[0], example_d[1] = example_d[1], example_d[0]
    print(example_d[0])
    pickle_out = open("d.pickle","wb")
    pickle.dump(example_d, pickle_out)
    pickle_out.close()
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    im = Image.new("RGB", (240, 240), "orange")
    d = ImageDraw.Draw(im)
    d.text((120, 100), "Flip them", fill="black", anchor="ms", font=font)
    d.text((120, 120), "Chains:", fill="black", anchor="ms", font=font)
    d.text((120, 140), "Activated", fill="black", anchor="ms", font=font)
    if example_d[0] == 1:
        d.text((120, 160), "now on ETH...", fill="turquoise", anchor="ms", font=font)
    if example_d[0] ==137:
        d.text((120, 160), "now on Poly...", fill="turquoise", anchor="ms", font=font)

#        im = im.rotate()
    disp.image(im)
    time.sleep(4)
    homescreen()
#    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
#    draw = ImageDraw.Draw(img)
#    disp.image(img)
#    time.sleep(0.25)
#    os.system("sudo systemctl restart myscript.service")

def homescreen():
#might need to move higher so variables are known
    print("Home Wallet Screen")

    try:
        wallet = apps_data[0][1]
        secretkey = apps_data[0][2]

    except IndexError:
        print("Empty data")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        im = Image.new("RGB", (240, 240), "red")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
        d.text((120, 120), "No ethereum wallet", fill="black", anchor="ms", font=font)
        d.text((120, 140), "loaded yet", fill="black", anchor="ms", font=font)
        d.text((120, 160), "Shutting Down", fill="black", anchor="ms", font=font)
        d.text((120, 180), "Turn on unit again", fill="black", anchor="ms", font=font)
        disp.image(im)
        time.sleep(20)
        shut_down()

#transparency for boxes
    TINT_COLOR = (0, 0, 0)  # Black
    TRANSPARENCY = .3  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 22)
    img = Image.new("RGBA", (240, 240), "white")
    d = ImageDraw.Draw(img)

#add in a image layer ontop of white background, way of eliminated transparent layer too
    picture_1 = Image.open("nftydaze4.jpg").convert('RGBA')
    image = picture_1.resize((50, 50))
    img.paste(image, (50, 50))
    d.text((70, 110), "  ETH Wallet ", fill="black", anchor="ms", font=font)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    d.text((120, 20), wallet, fill="black", anchor="ms", font=font)
    disp.image(img)

#run different function that just generates blank screen with name on it

# Make a blank image the same size as the image for the rectangle, initialized
# to a fully transparent (0% opaque) version of the tint color, then draw a
# semi-transparent version of the square on it.
    overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
#    draw.rectangle(((10, 200), (100, 240)), fill=TINT_COLOR+(OPACITY,))
    draw.rounded_rectangle(((5, 185), (118, 240)), fill=TINT_COLOR+(OPACITY,), outline="black", width=1, radius=3)
    draw.ellipse((130, 30, 220, 100), fill = 'blue', outline ='blue')

#write on screen and pull up Ethereum account value
    acct = Account.from_key(secretkey)
    print(acct)
    print("Address:", acct.address)
    print(wallet)
    time.sleep(0.25)
# print current ETH account value
    balance = web3.eth.getBalance(acct.address)
    print('Account Balance: ', (web3.fromWei(balance, 'Ether')))

# print  USDC or main token_address selected (make sure correct ABI is here)
#ABI for usdc goerli
    abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationUsed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"}],"name":"Blacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newBlacklister","type":"address"}],"name":"BlacklisterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"burner","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newMasterMinter","type":"address"}],"name":"MasterMinterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"},{"indexed":false,"internalType":"uint256","name":"minterAllowedAmount","type":"uint256"}],"name":"MinterConfigured","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldMinter","type":"address"}],"name":"MinterRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":false,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[],"name":"Pause","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newAddress","type":"address"}],"name":"PauserChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newRescuer","type":"address"}],"name":"RescuerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"}],"name":"UnBlacklisted","type":"event"},{"anonymous":false,"inputs":[],"name":"Unpause","type":"event"},{"inputs":[],"name":"CANCEL_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"RECEIVE_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TRANSFER_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"authorizationState","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"blacklister","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"cancelAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"},{"internalType":"uint256","name":"minterAllowedAmount","type":"uint256"}],"name":"configureMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"currency","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"decrement","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"increment","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"tokenName","type":"string"},{"internalType":"string","name":"tokenSymbol","type":"string"},{"internalType":"string","name":"tokenCurrency","type":"string"},{"internalType":"uint8","name":"tokenDecimals","type":"uint8"},{"internalType":"address","name":"newMasterMinter","type":"address"},{"internalType":"address","name":"newPauser","type":"address"},{"internalType":"address","name":"newBlacklister","type":"address"},{"internalType":"address","name":"newOwner","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"newName","type":"string"}],"name":"initializeV2","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lostAndFound","type":"address"}],"name":"initializeV2_1","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"isBlacklisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"masterMinter","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"minterAllowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pauser","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"receiveWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"removeMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"tokenContract","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"rescueERC20","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rescuer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"transferWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"}],"name":"unBlacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newBlacklister","type":"address"}],"name":"updateBlacklister","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newMasterMinter","type":"address"}],"name":"updateMasterMinter","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newPauser","type":"address"}],"name":"updatePauser","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newRescuer","type":"address"}],"name":"updateRescuer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]')
    token_declare = web3.eth.contract(address=token_address, abi=abi) # declaring the token contract
    token_balance = token_declare.functions.balanceOf(acct.address).call() # returns int with balance, without decimals

#need to put .call() at the end to call the smart contract
#convert supply to Wei witch is 18 decimal places)
    print('TokenBalance: ', token_balance/1000000)
#print('Contract Name: ', contract.functions.name().call())
    print('Symbol: ', token_declare.functions.symbol().call())

    req = requests.get('https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=UHM6EST7PIJ9RIKCYVRSA1NEV1TFJB1PYQ')
    t = json.loads(req.content)

#print(t)
    print('SafeGasPrice', t['result']['SafeGasPrice'])
    print('ProposeGasPrice', t['result']['ProposeGasPrice'])
    print('FastGasPrice', t['result']['FastGasPrice'])

#draw token values

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
#        im = Image.new("RGB", (150, 50))
    d = ImageDraw.Draw(overlay)                
    d.text((60, 210), "ETH:  " + str(round(web3.fromWei(balance, 'Ether'), 3)), fill="black", anchor="ms", font=font)
    d.text((60, 230), str(token_declare.functions.symbol().call()) + ":" + str(round(token_balance/1000000, 2)), fill="black", anchor="ms", font=font)
    d.text((170, 70), "Gas " + str(t['result']['FastGasPrice']), fill="white", anchor="ms", font=font)

#        disp.image(resized_img)

# Alpha composite these two images together to obtain the desired result.
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB") # Remove alpha for saving in jpg format.
    disp.image(img)

# add qrcode to right corner
    qr = qrcode.QRCode()
#    qr.add_data(f"https://opensea.io/collection/{slug}")
    qr.add_data(wallet)
    qr.make()
    imgrender = qr.make_image(fill_color="black", back_color="#FAF9F6")

#it did say WIDTH,HEIGHT)
    imgrender2 = imgrender.resize((120, 120))

#check for bad link
    try:
        disp.image(imgrender2)
#            time.sleep(0.25)            
    except PIL.UnidentifiedImageError:
        print("Bad Link/File")

def showkey():

    try:
        wallet = apps_data[0][1]
        secretkey = apps_data[0][2]

    except IndexError:
        print("Empty qrcode data")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        im = Image.new("RGB", (240, 240), "red")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
        d.text((120, 120), "No ethereum wallet", fill="black", anchor="ms", font=font)
        d.text((120, 140), "are loaded yet", fill="black", anchor="ms", font=font)
        d.text((120, 160), "Shutting Down", fill="black", anchor="ms", font=font)
        d.text((120, 180), "Turn on unit again", fill="black", anchor="ms", font=font)
        d.text((120, 200), "when you are ready", fill="black", anchor="ms", font=font)
        d.text((120, 220), "to scan a QRcode", fill="black", anchor="ms", font=font)
        disp.image(im)
        time.sleep(20)
        shut_down()

    im = Image.new("RGB", (240, 240), (0,0,0))
    d = ImageDraw.Draw(im)
    unicode = u"\uE233"
    x = len(secretkey)
#split key in two
    string1 = slice(0,len(secretkey)//2)
    string2 = slice(len(secretkey)//2,len(secretkey))
    d.text((1,1), str(secretkey[string1]),(200,15,20))
    d.text((1,10), str(secretkey[string2]),(200,15,20))
    d.text((1,140),'Private Key',(200,15,20))
    d.text((180,110),'App Stores',(200,15,20))
    disp.image(im)

#private key qrcode
    qr = qrcode.QRCode()
    print(secretkey)
    qr.add_data(secretkey)
    qr.make()

    imgrender = qr.make_image(fill_color="black", back_color="#FAF9F6")
    imgrender2 = imgrender.resize((120,120))
    im.paste(imgrender2, (0,20))
#    imgrender2.paste

#    disp.image(imgrender2)
##    d = ImageDraw.Draw(imgrender2)

#second qrcode link to wallet phone apps
    qr = qrcode.QRCode()
    applinks = "https://linktr.ee/piethereumwallet"
    print(applinks)
    qr.add_data(applinks)
    qr.make()

    imgrender = qr.make_image(fill_color="black", back_color="#FAF9F6")
    imgrender3 = imgrender.resize((120,120))
    im.paste(imgrender3, (120,120))
    d.text((30,225),'Be Extremely Careful Private Key',(200,15,20))

    try:
        disp.image(im)
        time.sleep(0.25)            
    except PIL.UnidentifiedImageError:
        print("Bad Link/File")

    time.sleep(20)
    homescreen()

camera_on = False
def qr_capture():

    global apps_data
    global x
    global camera_on
    wallet = apps_data[0][1]
    secretkey = apps_data[0][2]


#    cap = cv2.VideoCapture(-1)

    print("Your QR Gan Punk")
#Aim at QR codes; new NFT will flash when captured:  display screen Splash
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    img = Image.new("RGB", (240, 240), "black")

    draw = ImageDraw.Draw(img)  # Create a context for drawing things on it.
    draw.rounded_rectangle(((10, 50), (230, 190)), fill="lime", outline="black", width=0, radius=25)
    disp.image(img)


    d = ImageDraw.Draw(img)
    d.text((120, 100), "Scan WalletConnect", fill="black", anchor="ms", font=font)
    d.text((120, 120), "QR Code", fill="black", anchor="ms", font=font)
#    d.text((120, 120), "from QR Codes", fill="black", anchor="ms", font=font)
#    d.text((120, 140), "Camera is on back", fill="black", anchor="ms", font=font)
#    d.text((120, 160), "of Device", fill="black", anchor="ms", font=font)
#    d.text((120, 180), "Scanning now...", fill="black", anchor="ms", font=font)
#    d.text((120, 200), "Press ExitScan when done!", fill="black", anchor="ms", font=font)
#    d.text((120, 220), "__________________", fill="black", anchor="ms", font=font)

#        im = im.rotate()
    disp.image(img)

#Start QRcode capture
    cap = cv2.VideoCapture(-1)
    font = cv2.FONT_HERSHEY_PLAIN
    while True:
        qrcodeData = 0 
        _, frame = cap.read()
        decodedObjects = pyzbar.decode(frame)
        for obj in decodedObjects:
            print("Data", obj.data)
            print(type(obj.data))
#convertbytes object data to string
            qrcodeData = obj.data.decode("utf-8")
            print(qrcodeData)
##Screen to Confirm User Scanned

            if qrcodeData not in found:
                #csv2.write("{},{}\n".format(datetime.datetime.now(), qrcodeData))
                #csv2.flush()
                found.add(qrcodeData)

                print("Scanned Successfully")
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                img = Image.new("RGB", (240, 240), "black")

#                overlay = Image.new('RGBA', img.size)
                draw = ImageDraw.Draw(img)  # Create a context for drawing things on it.
                draw.rounded_rectangle(((10, 50), (230, 190)), fill="salmon", outline="black", width=0, radius=25)
                disp.image(img)


                d = ImageDraw.Draw(img)
#            d.text((120, 80), "   (°)~(°)_________", fill="black", anchor="ms", font=font)
                d.text((120, 100), "Scanned    ", fill="black", anchor="ms", font=font)
                d.text((120, 120), "Successfully", fill="black", anchor="ms", font=font)
                d.text((120, 140), "Logging into", fill="black", anchor="ms", font=font)
                d.text((120, 160), "DAPP", fill="black", anchor="ms", font=font)
                if example_d[0] == 1:
                    d.text((120, 180), "..ETH..", fill="yellow", anchor="ms", font=font)
                if example_d[0] == 137:
                    d.text((120, 180), "..Polygon..", fill="yellow", anchor="ms", font=font)

#                d.text((120, 200), "..", fill="black", anchor="ms", font=font)
#                d.text((120, 220), ".", fill="black", anchor="ms", font=font)

# Alpha composite these two images together to obtain the desired result.
#                img = Image.alpha_composite(img, overlay)
#                img = img.convert("RGB") # Remove alpha for saving in jpg format.

                disp.image(img)
                time.sleep(5)



                print(" ")
                print(" pyWalletConnect minimal demo")
                print("scanned a Dapp WC URI (v1 or v2) >)")

                cap.release()
                cv2.destroyAllWindows()

                wallet_address = wallet
#                wallet_chain_id = 137
                wallet_chain_id = example_d[0]
                # Required for v2
                WCClient.set_project_id("338d2404fafcd317347e4da1c3de72b5")

                wclient = WCClient.from_wc_uri(qrcodeData)

                print("Connecting with the Dapp ...")
                try:
                    session_data = wclient.open_session()

                    # Waiting for user accept the Dapp request

    #                user_ok = input(
    #                    f"WalletConnect pairing request from {session_data[2]['name']}. Approve? [y/N]>"
    #                )
    #                if user_ok.lower() != "y":
    #                    print("User denied the pairing.")
    #                    wclient.reject_session_request(session_data[0])
    #                    return

                    print("Accepted, continue connecting with the Dapp ...")
                    wclient.reply_session_request(session_data[0], wallet_chain_id, wallet_address)

                    print("Connected.")
                    print(" To quit : Hit CTRL+C, or disconnect from Dapp.")
                    print("Now waiting for dapp messages ...")
                    while True:
                        try:
                            sleep(0.3)
                # get_message return : (id, method, params) or (None, "", [])
                            read_data = wclient.get_message()
                            if read_data[0] is not None:
                                print("\n <---- Received WalletConnect wallet query :")
                                print(read_data)

                                print(read_data[0])
                                print(type(read_data))
                                id_request = read_data[0]
                                print(type(id_request))
                                print(id_request)
                
                                method = read_data[1]
                                print(method)
                                parameters = read_data[2]
                                print(type(parameters))
                                print(parameters)
                                print("message to sign")
                                print(parameters[0])
                                parameters = parameters[0]
                                print(type(parameters))

                                if "personal_sign" == method:
                                    parameters = parameters[2:]
                                    print(parameters)
                                    print('convert from string to signature type')
                                    parameters = bytes.fromhex(parameters)

                                    print("personal sign")
                                    message = messages.encode_defunct(parameters)
                    
                                    print(message)
                                    print(type(message))
                                    signed_message = Account.sign_message(message, private_key=secretkey)
                                    print(signed_message)
                                    print(parameters[1])
                                    result = signed_message.signature.hex()
                    
                                    print(result)
                                    print(type(result))
                                    print(type(result))
                                    print(result)
                                    wclient.reply(id_request, result)

                    
                                    print("verify signature: address should match")
                                    message = messages.encode_defunct(parameters)
                                    print(w3.eth.account.recover_message(message, signature=result))
                                    
                                    if (w3.eth.account.recover_message(message, signature=result)) == wallet_address:
                                    
                                        print("Logged In")
                                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                                        img = Image.new("RGB", (240, 240), "black")

                                        draw = ImageDraw.Draw(img)  # Create a context for drawing things on it.
                                        draw.rounded_rectangle(((10, 50), (230, 190)), fill="lime", outline="black", width=0, radius=25)
                                        disp.image(img)


                                        d = ImageDraw.Draw(img)
                                        d.text((120, 80), "   (°)~(°)_________", fill="black", anchor="ms", font=font)
                                        d.text((120, 100), "Address Authenticated ", fill="black", anchor="ms", font=font)
                                        d.text((120, 120), "with", fill="black", anchor="ms", font=font)
                                        d.text((120, 140), "the", fill="black", anchor="ms", font=font)
                                        d.text((120, 160), "DAPP", fill="black", anchor="ms", font=font)
#                                        d.text((120, 180), "...", fill="black", anchor="ms", font=font)
#                                        d.text((120, 200), "..", fill="black", anchor="ms", font=font)
#                                        d.text((120, 220), ".", fill="black", anchor="ms", font=font)
                                        disp.image(img)
                                        time.sleep(5)

    #                                    break 

                                
                                # Detect quit
                                #  v1 disconnect
                                if (
                                    read_data[1] == "wc_sessionUpdate"
                                    and read_data[2][0]["approved"] == False
                                ):
                                    print("User disconnects from Dapp (WC v1).")
#                                    cap.release()
#                                    cv2.destroyAllWindows()

                                    break
                                if "eth_sendTransaction" == method:
                                    print("logging user out, sendTransaction attempted")
#                                    cap.release()
#                                    cv2.destroyAllWindows()
                                    break

                                if "wallet_switchEthereumChain" == method:
                                    print("logging user out, sendTransaction attempted")
#                                    cap.release()
#                                    cv2.destroyAllWindows()
                                    break


                            #  v2 disconnect
                            if read_data[1] == "wc_sessionDelete" and read_data[2].get("reason"):
                                print("User disconnects from Dapp (WC v2).")
                                print("Reason :", read_data[2]["reason"]["message"])
#                                cap.release()
#                                cv2.destroyAllWindows()

                                break

                        except KeyboardInterrupt:
                            print("Demo interrupted.")
                            break
                    wclient.close()
                    print("WC disconnected.")
                except pywalletconnect.client.WCClientException:

                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                    im = Image.new("RGB", (240, 240), "teal")
                    d = ImageDraw.Draw(im)
#            d.text((120, 80), "   (°)~(°)_________", fill="black", anchor="ms", font=font)
                    d.text((120, 100), "Connection Failed", fill="black", anchor="ms", font=font)
                    d.text((120, 120), "Site has Connection", fill="black", anchor="ms", font=font)
                    d.text((120, 140), "Issues", fill="black", anchor="ms", font=font)
                    d.text((120, 160), "Follow up with site", fill="black", anchor="ms", font=font)
                    d.text((120, 180), "...", fill="black", anchor="ms", font=font)
                    d.text((120, 200), "..", fill="black", anchor="ms", font=font)
                    d.text((120, 220), ".", fill="black", anchor="ms", font=font)
                    disp.image(im)

                    wclient.close()
                    print("session request timeout")
                    break 




##Screen to Show User Next Instructions

                print("HomeScreenTransition")
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                im = Image.new("RGB", (240, 240), "black")


                draw = ImageDraw.Draw(img)  # Create a context for drawing things on it.
                draw.rounded_rectangle(((10, 50), (230, 190)), fill="salmon", outline="black", width=0, radius=25)
                disp.image(img)


                d = ImageDraw.Draw(img)
#    art_checkers(im)

#            d.text((120, 80), "   (°)~(°)_________", fill="black", anchor="ms", font=font)
                d.text((120, 100), "Disconnected from ", fill="black", anchor="ms", font=font)
                d.text((120, 120), "Dapp", fill="black", anchor="ms", font=font)
                d.text((120, 140), "", fill="black", anchor="ms", font=font)
#                d.text((120, 160), "", fill="black", anchor="ms", font=font)
#                d.text((120, 180), "", fill="black", anchor="ms", font=font)
#                d.text((120, 200), "", fill="black", anchor="ms", font=font)
#                d.text((120, 220), "", fill="black", anchor="ms", font=font)
                disp.image(img)
                time.sleep(5)
                homescreen()
                return 0            
#                break
#                cap.release()
#                cv2.destroyAllWindows()

#            if qrcodeData in found:
#                print("already scanned that one")


#set condition if no qrcode Data
#free camera object and exit
    cap.release()
    cv2.destroyAllWindows()
#    homescreen()
    return




button1 = Button(21)
button2 = Button(20)
button3 = Button(16)

buttonL = Button(5)
buttonR = Button(26)
buttonU = Button(6) 
buttonD = Button(19)
buttonC = Button(13)


#start with splash
splash_screen()

#check internet connection
if internet() == False:
    print("can't connect to internet:socket gaierror")

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    im = Image.new("RGB", (240, 240), "blue")
    d = ImageDraw.Draw(im)
    d.text((120, 80), "No internet Connection", fill="black", anchor="ms", font=font)
    d.text((120, 120), 'Re-Pair using Homebridge', fill='black', anchor='ms', font=font) 
    d.text((120, 140), "(re-enter the wifi Psswrd)", fill="black", anchor="ms", font=font)
    d.text((120, 160), "Or move closer to signal", fill="black", anchor="ms", font=font)
    d.text((120, 180), "Or wait and device", fill="black", anchor="ms", font=font)
    d.text((120, 200), "will shut down", fill="black", anchor="ms", font=font)
    d.text((120, 220), "automatically", fill="black", anchor="ms", font=font)

#       im = im.rotate()
    disp.image(im)
    time.sleep(160)

    print("Re-Connect:Auto Shutting Down in 2 minutes")

    if internet() == False:
        print("retry connect internet:can't connect to internet:socket gaierror")

        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        im = Image.new("RGB", (240, 240), "red")
        d = ImageDraw.Draw(im)
        d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
        d.text((120, 120), "Retried internet, Still", fill="black", anchor="ms", font=font)
        d.text((120, 140), "No internet connected", fill="black", anchor="ms", font=font)
        d.text((120, 160), "Shutting Down", fill="black", anchor="ms", font=font)
        d.text((120, 180), "now!", fill="black", anchor="ms", font=font)
#       im = im.rotate()
        disp.image(im)
        time.sleep(10)

        #Shutdown display screen Splash
        image = Image.open('nftydaze4.jpg')
        image = image.resize((WIDTH, HEIGHT))
        print('Drawing image')
        disp.image(image)
        time.sleep(5)
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        disp.image(img)
        time.sleep(0.25)
        os.system("sudo shutdown -h now")
        while 1:
            time.sleep(1)

if internet():
    isConnected = web3.isConnected()
    blocknumber = web3.eth.blockNumber
    print('Connected: ', isConnected, 'BlockNumber: ', blocknumber)

else:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    im = Image.new("RGB", (240, 240), "red")
    d = ImageDraw.Draw(im)
    d.text((120, 100), "User:    ", fill="black", anchor="rs", font=font)
    d.text((120, 120), "You are out", fill="black", anchor="ms", font=font)
    d.text((120, 140), "of wifi range", fill="black", anchor="ms", font=font)
    d.text((120, 160), "or wifi setup", fill="black", anchor="ms", font=font)
    d.text((120, 180), "went wrong.", fill="black", anchor="ms", font=font)
    d.text((120, 200), "Move closer to router", fill="black", anchor="ms", font=font)
    d.text((120, 220), "__________________", fill="black", anchor="ms", font=font)
#        im = im.rotate()
    disp.image(im)
    print("no internet available")

#check if user needs onboarding
no_NFT()
homescreen()


print("""
Your ETH Wallet, Gan Punk
""")

try: 

    button1.when_pressed = shut_down
    button2.when_pressed = push_button2
    button3.when_pressed = push_button
    buttonL.when_pressed = showkey
#    buttonR.when_pressed = polygon
    buttonC.when_pressed = qr_capture
    pause()


finally:
    pass
