# Ethereum Hardware Starter Wallet for Raspberry Pi and ST7789 IPS Display:

For $30 (+ cost of microSD cards) you can make your own: Physically Transferrable MicroSDcard based cold ETH wallets! Load and gift small cold wallets to friends and family.

Don't want the tax implications of sending your ETH?  Just send USDC. 
Hand the hardware to your 💘 crypto noob/student/child, they press and hold the physical button, it instantly routes a uniswap transaction to convert all the USDC to ETH!
![bank](https://user-images.githubusercontent.com/75555569/191143990-8c33be18-0b7e-4569-9f18-d8284ca2c219.jpg)

Available on ETH L1 or quickly convert code to any EVM based chain and its uniswap v2 market variant!

On device start, a ETH wallet will be created and saved as a .csv file called ETHEREUMWALLET.csv in the boot drive. Wallet address and private key will be easily viewable in that file on any computer with a microSD card adapter. If you want to onboard a bunch of people, just bring copies of your preloaded microSD card and when you pop a new one in, it will generate a new wallet and be ready for onboarding and the recipient can walk away with a microSD card with their private key safely stored.

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

after above completed steps proceed below. 

Make sure you have the following dependencies (modules):

````
sudo apt-get update
sudo apt-get install python-rpi.gpio python-spidev python-pip python-pil python-numpy
````

Install this library by running:

````
sudo pip3 install st7789
````

Prerequisites
(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running pip and has Python3 installed)

If you are running the Pi headless, connect to your Raspberry Pi using ssh.

Install & Run
Copy the files from this repository onto the Pi, or clone using:

```````````
cd ~
git clone https://github.com/snarflakes/ethereumwallets.git
cd ganpunks
```````````

Run the script using (must run as root):

`````````````
sudo python3 image.py
`````````````

# Add as a service: How to have the EthereumWallet Program run whenever the Pi Boots Up 

In order to have a command or program run when the Pi boots, you can add it as a service. Once this is done, you can start/stop enable/disable from the linux prompt.
Follow these instructions: (make sure you set USER: root for both copies)
https://www.raspberrypi.org/documentation/linux/usage/systemd.md

# For extra security in public places? Make these mods to your OS.

Change your user logon to be a very strong 10 digit password with symbol/upper/lowercase letter/numbers.  Also you can reduce the rate of incorrect authentication attempts with https://www.fail2ban.org/wiki/index.php/Main_Page
