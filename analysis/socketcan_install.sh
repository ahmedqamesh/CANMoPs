#!/bin/bash
# variables
BITRATE=125000
CHANNEL="can0"
#Install python-can
#pip install python-can

# SocketCAN script
echo "CAN hardware OS drivers and config for" $CHANNEL
sudo -S modprobe can
sudo -S modprobe vcan
sudo -S modprobe slcan
sudo -S modprobe can-dev
sudo -S modprobe can-raw
sudo -S modprobe can-bcm
sudo -S modprobe kvaser-usb
sudo -S lsmod | grep can

echo "Configuring the SocketCAN interface to bitrate of" $BITRATE
sudo -S ip link set $CHANNEL type can bitrate $BITRATE
echo "Bringing the driver  up"
sudo -S ip link set up $CHANNEL
ifconfig $CHANNEL
