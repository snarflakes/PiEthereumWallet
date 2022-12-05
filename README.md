# A Permissionless Self-Banking (Ethereum) and Currency Trading Device
A Decentralized Ethereum Hardware Wallet (Raspberry Pi inside) with contract direct token Swap and physically transferrable private key.

Bringing the blockchain to physical life, using swappable private key containing microSD cards, clicky buttons, open source code, and a bright informative display, this device makes for a great way to educate others, onboard, build, and swap tokens. Super easy build! no coding experience needed!

For $30 (+ cost of microSD cards) you can make your own! Load and gift small cold wallets to friends and family.

Don't want the tax implications of sending your ETH?  Just send USDC + gas. 
Hand the hardware to your 💘 crypto noob/student/child, they press and hold the physical button, it instantly routes a contract direct uniswap transaction to convert all the USDC to ETH(easily customize this swap to a token of your choosing)!

PART List: 
raspberry pi zero WH (needs header pins): https://www.pishop.us/product/raspberry-pi-zero-wireless-wh-pre-soldered-header/
(stock info) https://www.nowinstock.net/computers/developmentboards/raspberrypi/
ST screen: https://a.co/d/iT952LE
microSD card (can go smaller size and generic to reduce costs):https://a.co/d/50a2JCb
battery pack (optional) - https://a.co/d/fKbBJRV

![image](https://user-images.githubusercontent.com/75555569/198359213-da0b4a9d-303e-4461-a70e-165fd8b24b97.png)

Available on ETH L1 and Polygon L2 and quickly convert tokens info or tokenswaps to any EVM based chain and its uniswap market variant!

On device start, a ETH wallet will be created and saved as a .csv file called ETHEREUMWALLET.csv in the boot drive. Wallet address and private key will be easily viewable in that file on any computer with a microSD card adapter. If you want to onboard a bunch of people, just bring copies of your preloaded microSD card (original should have saved wifi credentials prior to copying) and when you pop a new one in, it will generate a new wallet and be ready for onboarding and the recipient can walk away with a microSD card with their private key safely stored.

Plus there are a ton more buttons available to come up with your own essential wallet interactions!

✅ digital signature?
✅ send an ETH transaction out?
✅ wallet watcher with custom alerts to phone?
✅ gas price watcher with alerts?

Device Demonstration Videos including Private Key Management can be viewed here: https://www.youtube.com/channel/UCEF_x9fTZcyoEAE-GllaJ8w

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

