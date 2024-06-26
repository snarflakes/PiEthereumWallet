# A Permissionless Self-Banking (Ethereum),Currency Trading Device. Safe.Global MultiSig enabled
A Decentralized Ethereum Hardware Wallet (Raspberry Pi inside) with contract direct token Swap and physically transferrable private key.

Warning: NOT AUDITED. Do not use to store substantial quantities of funds. 
**I had to deactivate the included infura API as it was being spammed. Please generate your own free infura API number via the infura or alchemy websites and replace it in the code at the beginning (infura_url + infura_url_poly variables). While you are at it, generate your own etherscan API, and polygon scan API, and any other L2 blockchain explorer API and replace those in the code. Sorry spammer's make things harder for everyone!

Device Demonstration Videos including Private Key Management can be viewed here: https://www.youtube.com/channel/UCEF_x9fTZcyoEAE-GllaJ8w

Bringing the blockchain to physical life, using swappable private key containing microSD cards, clicky buttons, open source code, and a bright informative display, this device makes for a great way to educate others, onboard, build, and swap tokens. Super easy build! no coding experience needed!

For $30 (+ cost of microSD cards) you can make your own! Load and gift small cold wallets to friends and family.

Don't want the tax implications of sending your ETH?  Just send USDC + gas. 
Hand the hardware to your 💘 crypto noob/student/child, they press and hold the physical button, it instantly routes a contract direct uniswap transaction to convert all the USDC to ETH(easily customize this swap to a token of your choosing)!
Are you a DAO member tasked with signing via a Safe.Global multisig? Take advantage of the always visible notification bar to alert you when a transaction needs signing!

PART List: 
raspberry pi zero WH (needs header pins): https://www.pishop.us/product/raspberry-pi-zero-wireless-wh-pre-soldered-header/
(stock info) https://www.nowinstock.net/computers/developmentboards/raspberrypi/
ST screen: https://a.co/d/iT952LE
microSD card (can go smaller size and generic to reduce costs):https://a.co/d/50a2JCb
battery pack (optional) - https://a.co/d/fKbBJRV
Want WalletConnect?: camera module (optional) -https://a.co/d/3tTFnJs

![image](https://nftydaze.com/wp-content/uploads/2023/04/IMG-1435.jpg)

Available on ETH L1 and Polygon L2 and quickly convert tokens info or tokenswaps to any EVM based chain and its uniswap market variant!

On device start, a ETH wallet will be created and saved as a .csv file called ETHEREUMWALLET.csv in the boot drive. Wallet address and private key will be easily viewable in that file on any computer with a microSD card adapter. If you want to onboard a bunch of people, just bring copies of your preloaded microSD card (original should have saved wifi credentials prior to copying) and when you pop a new one in, it will generate a new wallet and be ready for onboarding and the recipient can walk away with a microSD card with their private key safely stored.

Plus there are a ton more buttons available to come up with your own essential wallet interactions!

✅ digital signature?
✅ send an ETH transaction out?
✅ wallet watcher with custom alerts to phone?
✅ gas price watcher with alerts?


# Installation

A) Basic Raspberry Pi Zero setup for NOOBS.  start here if you have no clue what to do with your hardware or are very security minded.
https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html

OR if you want seemless wifi connectivity at every boot (best option)

B) Homebridge Raspberry Pi Zero setup: add a server for easy wifi connection when traveling around to peoples houses. You need a wifi or mobile phone hotspot connection for the wallet to work.
https://homebridge.io/raspberry-pi-image

Use this disk imager to burn a copy of one of those operating system "images" onto a microSD card: https://sourceforge.net/projects/win32diskimager/

after above completed steps proceed below. 

Make sure you have the following dependencies (modules):

````
sudo apt-get update
or
sudo apt-get update --allow-releaseinfo-change

sudo apt-get -y install python3-pip
````

Install these libraries by running:

````
sudo pip3 install st7789
sudo pip3 install pillow
sudo pip3 install board
sudo pip3 install gpiozero
sudo pip3 install adafruit-blinka
sudo apt-get install libopenjp2-7
sudo pip3 install RPI.GPIO
sudo apt-get install python3-numpy 
sudo pip3 install adafruit-circuitpython-rgb-display
sudo pip3 install qrcode
sudo pip3 install web3
sudo pip3 install uniswap-python
sudo pip3 install spidev
sudo raspberry-config
(enable SPI in menu: go to interface options, go to SPI, enable SPI)
sudo reboot now

````

Prerequisites
(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running pip and has Python3 installed)

If you are running the Pi headless, connect to your Raspberry Pi using ssh.

Install & Run
Copy the files from this repository onto the Pi, or clone using:

```````````
cd ~
git clone https://github.com/snarflakes/PiEthereumWallet.git
cd PiEthereumWallet
```````````

Run the ethereum L1 script using (must run as root):

`````````````
sudo python3 image.py
`````````````
Run the polygon L2 script using (must run as root):

`````````````
sudo python3 polygonimage.py
`````````````

# Add as a service: How to have the Ethereum Wallet Program run whenever the Pi Boots Up 

In order to have a command or program run when the Pi boots, you can add it as a service. Once this is done, you can start/stop enable/disable from the linux prompt.
Follow these instructions: (make sure you set USER: root for both copies!). Also make sure you pick which wallet version file you want to auto-run on boot, image.py for L1, polygonimage.py for L2. Also make sure you don't require the device to be internet connected for the start-up script to start! The wallet program will alert you if there are internet issues.
https://domoticproject.com/creating-raspberry-pi-service/

# For extra security in public places? Make these mods to your OS.

Change your user logon to be a very strong 10 digit password with symbol/upper/lowercase letter/numbers.  Also you can reduce the rate of incorrect authentication attempts with https://www.fail2ban.org/wiki/index.php/Main_Page

# Want more Privacy (hide your IP address)?

Install free opensource software WireguardVPN by following instructions here: https://pivpn.io/

# User Interface Button Flow
![image](https://user-images.githubusercontent.com/75555569/198363554-f76feb38-99e4-48f4-a357-6e68d5ae0b8b.png)


# WalletConnect/Safe.Global Optional Installation Instructions
````
[camera first]
sudo apt-get install python3-opencv
sudo apt-get install libqt4-test python3-sip python3-pyqt5 libqtgui4 libjasper-dev libatlas-base-dev -y

##TURN ON CAMERA navigate through accessories on menu- 
sudo raspi-config

[walletconnect function] imageid.py (only pushes through personal sign) and imageidopen.py (pushes through all transactions and signatures without "warning" user interface) imageidopensafe.py (includes imageidopen AND notification bar alerting users of the presence of a multisig safe transaction needing signing)
sudo apt-get install libssl-dev
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
python3 -m pip install wsproto==1.0.0
pip install cryptography
(or)
sudo apt install python3-cryptography
python3 -m pip install pyWalletConnect

#Take Note Difficulty with installing cryptography module as "sudo", so script has to run through user because sudo doesn't have access
practice from command line: 
sudo -E python3 imageid.py

#work around for sudo -E (when running myscript) see below
added sys.path directions directly into the file so it would point to the location installed under the pi user
(all directories need to be listed, if additional modules are found in subfolders those folders need to be named)
````

# Launch 3 types of Walletconnect PiEthereum Wallet
Run the WalletConnect Wallet with ONLY auto-signed "personal_sign" transactions (auto-signs the simplest safer transactions) script (must run as root):

`````````````
sudo -E python3 imageid.py
or sudo -E python3 daytraderbuttons.py

myscript autostart line:
ExecStart=/usr/bin/python3 -u imageid.py
`````````````
Run the WalletConnect Wallet with all signatures auto-signed (be careful as any transaction you agree to will be auto signed with no confirmation (must run as root):

`````````````
sudo -E python3 imageidopen.py

myscript autostart line:
ExecStart=/usr/bin/python3 -u imageidopen.py
`````````````
Run the WalletConnect Wallet with all signatures auto-signed + special Safe.Global multisig pending transaction notification bar (must run as root):

`````````````
sudo -E python3 imageidopensafe.py

myscript autostart line:
ExecStart=/usr/bin/python3 -u imageidopensafe.py
`````````````
