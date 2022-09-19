# Ethereum Hardware Starter Wallet with ST7789 IPS Display:

For $30 (+ cost of microSD cards) you can make your own: Physically Transferrable MicroSDcard based cold ETH wallets! Load and gift small cold wallets to friends and family.

Don't want the tax implications of sending your ETH?  Just send USDC. 
Hand the hardware to your 💘 crypto noob/student/child, they hold and press the button, it instantly routes a uniswap transaction to convert all the USDC to ETH!

Available on ETH L1 or convert quickly to any EVM based chain and its uniswap v2 variant!

On device start, a ETH wallet will be created and saved as a .csv file called ETHEREUMWALLET.csv in the boot drive. Wallet address and private key will be easily viewable on any computer with a microSD card adapter. If you want to onboard a bunch of people, just bring copies of your preloaded microSD card and each new one will generate a new wallet and be ready for onboarding.

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
