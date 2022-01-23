#!/usr/bin/bash
# This script is intended to start up the sensor script and the 
# concurrent server program which delivers sensor data from a file
# to remote clients. It needs to be set to executable via 
# chmod +x <filename>
# 
# Necessary packages for Adafruit-compatible sensors:
# $ sudo apt-get install build-essential python-dev python-openssl git
# $ pip3 install adafruit-circuitpython-dht
# $ sudo apt-get install libgpiod2

echo $(date)
echo $BASH
READ_INTERVAL_SECONDS=60
WLAN_PI4B=192.168.1.158
PORT=80

# check if NGINX active, start if necessary?
# ... 

# start the script in a new terminal window
gnome-terminal --tab -- /bin/bash -c "python3 sensors.py $READ_INTERVAL_SECONDS $WLAN_PI4B; exec bash"

# initiate ngrok tunnelling in a new terminal window
gnome-terminal --tab -- /bin/bash -c "ngrok http http://$WLAN_PI4B:$PORT -host-header=\"$WLAN_PI4B:$PORT\"; exec bash"
