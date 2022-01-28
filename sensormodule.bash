#!/usr/bin/bash
MANIFESTO="This script is intended to start up:
- the minicom program which captures Raspberry Pi Pico sensor readings
into a file 
- the sensor script which packages sensor readings into json, 
- the concurrent server tunelling program which delivers sensor data 
from a file to remote clients (ngrok) "

echo $(date)
echo $BASH
echo $MANIFESTO

READ_INTERVAL_SECONDS=30
WLAN_PI4B=192.168.1.158
PORT=80

PICO_LOG="/home/pi/Desktop/sensors/picolog.csv"
BAUD=115200
COMMPORT="/dev/ttyACM0"

# 1) build the pico UF2 file:
# change to the build directory /home/pi/Desktop/sensors/pico/build
# set the sdk path via 
# "export PICO_SDK_PATH=/home/pi/Desktop/pico_dir/pico/pico-sdk"
# then from the build directory, execute "cmake .. ; make "

# 2) mount the script onto the Pico:
# press BOOTSEL on the Pico and plug the USB cable connecting it to Pi 4
# copy the compiled UF2 file for sensor reading, into the Pico

# 3) check if NGINX server active. Edit behaviour via:
# /etc/nginx/sites-enabled/sensortest0

# 4) start logging of Pico sensor readings into a file, delete old file
rm $PICO_LOG
gnome-terminal --tab -- /bin/bash -c "minicom -b $BAUD -o -D $COMMPORT -C $PICO_LOG"

# 5) start the sensor formatting script in a new terminal window
gnome-terminal --tab -- /bin/bash -c "python3 sensors.py $READ_INTERVAL_SECONDS $WLAN_PI4B $PICO_LOG; exec bash"

# 6) initiate ngrok tunnelling in a new terminal window
gnome-terminal --tab -- /bin/bash -c "ngrok http http://$WLAN_PI4B:$PORT -host-header=\"$WLAN_PI4B:$PORT\"; exec bash"
