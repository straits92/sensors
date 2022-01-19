#!/usr/bin/bash
# This script is intended to start up the sensor script and the 
# concurrent server program which delivers sensor data from a file
# to remote clients. It needs to be set to executable via 
# chmod +x <filename>

echo $(date)
echo $BASH

# check if NGINX active, start if necessary?
# ... 

# start the script in a new terminal window; -e flag deprecated
gnome-terminal --tab -- /bin/bash -c "python3 sensors.py; exec bash"

# initiate ngrok tunnelling in a new terminal window
gnome-terminal --tab -- /bin/bash -c "ngrok http http://192.168.1.158:80 -host-header=\"192.168.1.158:80\"; exec bash"
