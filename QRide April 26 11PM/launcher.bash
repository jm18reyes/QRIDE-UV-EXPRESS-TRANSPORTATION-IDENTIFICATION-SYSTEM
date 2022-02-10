#!/bin/bash
#launcher.bash


export XAUTHORITY=/home/pi/.Xauthority
export LD_LIBRARY_PATH=/home/pi/Desktop/QRide-v5/QRide.py
export DISPLAY=:0.0
source /home/pi/.profile
workon cv2
cd /home/pi/Desktop/QRide-v5
/usr/bin/python3.7 /home/pi/Desktop/QRide-v5/QRide.py
