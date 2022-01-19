# temperature and humidity sensor reading and storing as json

# Set-up instructions:
# run script from cmdline:
# python3 ~/sensors.py
# manage how the data is served via nginx, in directory: 
# /etc/nginx/sites-enabled/sensortest0
# make nginx server available via ngrok:
# ngrok http http://192.168.1.158:80 -host-header="192.168.1.158:80"
# if needed transfer over to main PC via: 
# "scp pi@192.168.1.158:/home/pi/Desktop/sensors [destination]"

import os # os.path may be needed
import time
import datetime
import json

# for the sensors
# $ sudo apt-get install build-essential python-dev python-openssl git
# $ pip3 install adafruit-circuitpython-dht
# $ sudo apt-get install libgpiod2
import adafruit_dht
import board

# network and directory info; local server or tunneling to internet
WLAN_IP = "192.168.1.157" # static IP for Raspberry Pi Zero W
WLAN_IP_4B = "192.168.1.158" # static IP for Raspberry Pi 4B
subdir = "/sensordata"
prefix = "/sensordata_"
local_link_hourly = WLAN_IP_4B+prefix+"hourly.json"
local_link_instant = WLAN_IP_4B+prefix+"instant.json"
local_link_12hr = WLAN_IP_4B+prefix+"12hr.json"

# time constants
READ_INTERVAL_SECONDS = 60 # every 1 minutes
CORRECTION_INTERVAL = 5 # if failed, try 5 seconds later
TIMEZONE = "+01:00"

# sensors with old library Adafruit_DHT
# DHT_SENSOR = Adafruit_DHT.DHT22
# DHT_PIN = 4

# for GPIO4. Also, pulseio may be needed for raspberry
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False) 

### function definitions ###
# scan list of data points for hour; delete points beyond period
# not implemented
def check_response_age(period, current_time, filename):

	return

# open/overwrite a file with json data 
def overwrite_json(new_data, filename):
	try: 
		# print("Open file for overwriting: "+filename)
		# with open(filename, 'w') as sensorfile:
		with open(filename, 'w', encoding='utf-8') as sensorfile:
			# print("Opened file: "+filename)
			output_data = []
			json.dump(output_data, sensorfile) #ensure_ascii=False
	except:
		print("Failed to open json file: "+filename)
		pass

	# sensorfile = open(filename, 'r+')
	sensorfile = open(filename, 'r+', encoding='utf-8')
	if sensorfile is not None:
		file_data = json.load(sensorfile) # load existing data into dict
		file_data.append(new_data) # append new data to it
		sensorfile.seek(0) # file's current position at offset
		json.dump(file_data, sensorfile) # convert back to json

	return
	
# create/open existing sensordata file; append data point to it
def write_json(new_data, filename):
	if os.path.isfile(filename):
		print("File already open: "+ filename)
		
	else: 
		try: 
			print("File does not exist. Open: "+filename)
			with open(filename, 'w') as sensorfile:
			# with open(filename, 'w', encoding='utf-8') as sensorfile:
				if os.path.getsize(filename) == 0:
					# print("Opened file: "+filename)
					output_data = []
					json.dump(output_data, sensorfile)
		except:
			print("Failed to open json file")
			pass

	sensorfile = open(filename, 'r+')
	# sensorfile = open(filename, encoding='utf-8')
	if sensorfile is not None:
		file_data = json.load(sensorfile) # load existing data into dict
		file_data.append(new_data) # append new data to it
		sensorfile.seek(0) # file's current position at offset
		json.dump(file_data, sensorfile, indent = 4) # convert back to json

	return

def construct_data_point(temperature, humidity, epoch_time, date, hms, link):
	# format the data and pack into json object, then into json array 
	# which should be in destination file.
	formatted_time = '{0}T{1}'.format(date, hms)+TIMEZONE#+'\r\n'
	unit = "C"
	data_point ={
		"DateTime":formatted_time,
		"EpochDateTime":epoch_time,
		"Temperature":{
			"Value":temperature,
			"Unit":unit,
			"UnitType":17
		},
		"RelativeHumidity":humidity,
		"MobileLink":link,
		"Link":link
	}
	return data_point


### Execution starts here ### 
# create subdirectory when and if needed
cwd = os.getcwd()
abspath = cwd+subdir
if (os.path.isdir(abspath)) is not True:
	print("The following path does not exist: "+ abspath)
	try: 
		os.mkdir(abspath)
	except OSError:
		print("Creation of the directory failed: %s" % abspath)
	else:
		print("Successfully created the directory: %s" % abspath)

# sensor query and json write loop 
current_hour = 0
while True:
	# query the sensor
	try: 
		# humidity_raw, temperature_raw = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
		temperature_raw = dhtDevice.temperature
		humidity_raw = dhtDevice.humidity
		humidity = round(humidity_raw, 1)
		temperature = round(temperature_raw, 1)
		print("Raw temperature {}*C, raw humidity {}%".format(temperature_raw, humidity_raw))
	except:
		print("Sensor reading failed. Skip iteration and re-read in a few seconds.")
		time.sleep(CORRECTION_INTERVAL)
		continue;
		# temperature = 10
		# humidity = 50
		# print("Sensor reading failed. Default to placeholder temperature[%d]/humidity[%d]",temperature, humidity)


	if temperature is not None and humidity is not None:
				
		# to avoid time edge cases, get time info here for the iteration
		epoch_time = int(time.time())
		date = time.strftime('%y-%m-%d')
		date_extended = "20{}".format(date);
		hms = time.strftime('%H:%M:%S')
		
		# check hours, to formulate instant, hourly, daily response
		now = datetime.datetime.now()
		past_hour = current_hour
		current_hour = now.hour
		hms_hour = ("{}:00:00").format(current_hour)
		epoch_time_hour = epoch_time - (epoch_time%3600)
		print("The time now is date [{}], hms_hour [{}], epoch hour [{}], actual time [{}]".format(date_extended, hms_hour, epoch_time_hour, hms))

		# construct json object for sensor reading
		data_point = construct_data_point(temperature, humidity, epoch_time, date_extended, hms, local_link_hourly)
		data_point_hourly = construct_data_point(temperature, humidity, epoch_time_hour, date_extended, hms_hour, local_link_hourly)

		
		# formulate filenames, write to files
		filename_rawdata = abspath+prefix+date+TIMEZONE+".json" 
		filename_instant = abspath+prefix+"instant"+".json" 		
		write_json(data_point, filename_rawdata)
		overwrite_json(data_point, filename_instant)
		
		# write to the hourly response file, once an hour
		if past_hour != current_hour: 
			print("Hourly data point being written")
			filename_hourly = abspath+prefix+"hourly"+".json"
			overwrite_json(data_point_hourly, filename_hourly)
			
			# update on hourly basis for a 12/24hr response. wipe entries
			# older than the 12/24hr period, and append this hour's entry
			# check_response_age(period, filename_12hr)
			# check_response_age(period, filename_24hr)


	else: 
		print("Data reading and writing failed.")

	time.sleep(READ_INTERVAL_SECONDS)
