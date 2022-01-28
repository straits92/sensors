# temperature and humidity sensor reading and storing as json

import os # os.path may be needed
import time
import datetime
import json
import re # for regular expressions

# libraries for the sensors
import adafruit_dht
import board

# command line args
import sys

# Network and directory info; local server or tunneling to internet. 
# WLAN_IP = "192.168.1.157" # static IP for Raspberry Pi Zero W
WLAN_IP_4B = sys.argv[2] # static IP for Raspberry Pi 4B
PICO_LOG = sys.argv[3]

subdir = "/sensordata"
prefix = "/sensordata_"
local_link_hourly = WLAN_IP_4B+prefix+"hourly.json"
local_link_instant = WLAN_IP_4B+prefix+"instant.json"
local_link_12hr = WLAN_IP_4B+prefix+"12hr.json"

# time constants
arg_1 = sys.argv[1] # interval for reading the sensor, in seconds
READ_INTERVAL_SECONDS = int(arg_1) # every 1 minutes
CORRECTION_INTERVAL = 5 # if failed, try 5 seconds later
TIMEZONE = "+01:00"

print("User input for interval: {}, WLAN IP: {}".format(arg_1, WLAN_IP_4B))

# housekeeping for successful sensor reading
HOURLY_FAILURE_COUNT = 0
total_failure_count = 0

# for GPIO4. Also, pulseio may be needed for raspberry
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False) 

### function definitions ###
# scan list of data points for hour; delete points beyond period
# not implemented
def check_response_age(period, current_time, filename):

	return

# helper for reading the pico log file
def read_last_line_csv(csvfilename):
	final_line=""
	with open(csvfilename, "r", encoding="utf-8", errors="ignore") as csv:
			final_line = csv.readlines()[-1]	
	# print(final_line)
	return final_line

# extract numbers out of line
def extract_floats(string_line):
	array = []
	array = re.findall("\d+\.\d+", string_line)
	# print("0th elem: {}, 1st elem: {}".format(array[0], array[1]))
	return array

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
	if (os.path.isfile(filename)) is not True:
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
	print("The following path does not exist: {}".format(abspath))
	try: 
		os.mkdir(abspath)
	except OSError:
		print("Creation of the directory failed: {}".format(abspath))
	else:
		print("Successfully created the directory: {}".format(abspath))

# sensor query and json write loop 
current_hour = 0
time.sleep(20) # let the pico generate a file for reading first
print("Start looping.")
while True:
	# read the pico log file
	try: 
		measurements = []
		pico_last_line= read_last_line_csv(PICO_LOG)
		measurements = extract_floats(pico_last_line)
		temperature = measurements[1]
		humidity = measurements[0]
		print("Pico logged temp {}*C, humidity {}%".format(temperature, humidity))
	except:
		print("Failed to read pico log.")
		time.sleep(CORRECTION_INTERVAL)
		continue;
	
	# query the sensor when directly wired to Pi 4 B
	# ~ try: 
		# ~ temperature_raw = dhtDevice.temperature
		# ~ humidity_raw = dhtDevice.humidity
		# ~ humidity = round(humidity_raw, 1)
		# ~ temperature = round(temperature_raw, 1)
		# ~ print("Raw temperature {}*C, raw humidity {}%".format(temperature_raw, humidity_raw))
	# ~ except:
		# ~ total_failure_count = total_failure_count + 1
		# ~ print("Sensor reading failed. Retry in {} secs. Total failure count: {}".format(CORRECTION_INTERVAL, total_failure_count))
		# ~ time.sleep(CORRECTION_INTERVAL)
		# ~ continue;

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
		print("Date [{}], epoch hour [{}], exact time [{}]".format(date_extended, epoch_time_hour, hms))

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
