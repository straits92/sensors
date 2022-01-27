#!/usr/bin/bash
# This script is intended to start up the sensor script and the 
# concurrent server program which delivers sensor data from a file
# to remote clients. 

echo $(date)
echo $BASH
READ_INTERVAL_SECONDS=60
WLAN_PI4B=192.168.1.158
PORT=80
PICO_WEATHER_LOG=picolog.txt

# 1) build the pico UF2 file:
# change to the build directory /home/pi/Desktop/sensors/pico/build
# set the sdk path via 
# "export PICO_SDK_PATH=/home/pi/Desktop/pico_dir/pico/pico-sdk"
# then from the build directory, execute "cmake .. ; make "

# 2) mount the script onto the Pico:
# press BOOTSEL on the Pico and plug the USB cable connecting it to Pi 4
# copy the compiled UF2 file for sensor reading, into the Pico

# 3) start the logging of the Pico sensor readings into a known filename
# enter the name of the log file to which Pi Pico will write DHT reading
# then start the pico minicom, in another tab?
# ...
# minicom -b 115200 -o -D /dev/ttyACM0 > $(PICO_WEATHER_LOG)

# 4) check if NGINX process active, start if necessary

# 5) start the sensor formatting script in a new terminal window
gnome-terminal --tab -- /bin/bash -c "python3 sensors.py $READ_INTERVAL_SECONDS $WLAN_PI4B; exec bash"

# 6) initiate ngrok tunnelling in a new terminal window
gnome-terminal --tab -- /bin/bash -c "ngrok http http://$WLAN_PI4B:$PORT -host-header=\"$WLAN_PI4B:$PORT\"; exec bash"
