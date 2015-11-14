#!/usr/bin/env python

import argparse	# argument parsing
import csv			# to convert zip code to lat/long
import ephem 		# for the orbit calculations
import requests	# to get Celestrak TLEs and NOAA data
import time			# gets the current date
from pprint import pprint # for debugging

try:
	import RPi.GPIO as GPIO
	GPIO_AVAILABLE = True
except ImportError:
	GPIO_AVAILABLE = False

LOGFILE = 'icu.log'
TOKEN_FILE = 'openweathermap.txt' # access token for NOAA API
ZIPS_FILE = 'zip_code_database.csv' # to convert zip code to lat/long

if GPIO_AVAILABLE:
	# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
	LED = 12
	FLASH_DELAY = 1 # flash delay in seconds
	# Setup GPIO as output
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(LED, GPIO.OUT)
	GPIO.output(LED, GPIO.LOW)

	# This function will be run in the thread.
	def flash(is_active):
		c = 0
		while True:
			c = 1-c
			if len(is_active) == 0: # empty list means exit, for our purposes
				GPIO.output(LED,GPIO.LOW) # Turn off LED
				break # jump out of this infinite while loop and exit this thread
			if is_active[0]:
				if c:
					GPIO.output(LED,GPIO.HIGH) # Turn on LED
				else:
					GPIO.output(LED,GPIO.LOW) # Turn off LED
			time.sleep(FLASH_DELAY)
else:
	def flash(is_active):
		print("Flashing!")

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

def parse_args():
	"""
	Parses input args and returns a namespace with 'zip' and 'sat' containing zip and sat codes.
	"""
	parser = argparse.ArgumentParser(
		prog='ICU',
		description="Given a zip code and satellite code, generates notifications " +
		"15 minutes before that satellite will become visible."
	)
	parser.add_argument('-z', dest='zip', type=int, required=True, help="Zip code for which to check viewable events")
	parser.add_argument('-s', dest='sat', required=True, help="Name of satellite to view")
	return parser.parse_args()

def zip_to_latlong(zipcode):
	"""
	Given a zip code, returns a 3-tuple containing location name, latitude, and longitude. All strings.
	"""
	csvfile = open(ZIPS_FILE,'r')
	r = csv.reader(csvfile)
	loc = [l for l in r if l[0] == str(zipcode)]
	csvfile.close()
	if len(loc) == 0:
		return None
	loc = loc[0]
	return (loc[2], loc[9], loc[10])

def get_weather(lat, lon, loc):
	"""
	Given a zip code, returns a list of times and Booleans: three-hour increments, true if clear at that time.
	Uses the OpenWeatherMap API: http://openweathermap.org/api
	"""
	with open(TOKEN_FILE) as f:
		token = f.readlines()[0].strip()
	log("Getting weather information for %s: %s, %s" % (loc,lat,lon))
	params = {'lat':lat,'lon':lon, 'mode':'json', 'appid':token}
	headers = {'token':token}
	response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=params, headers=headers).json()['list']
	weather = [(response[i]['dt_txt'], response[i]['weather'][0]['main'] == 'Clear') for i in range(len(response))]
	return weather

def get_tle(sat):
	"""
	Given a string describing a satellite, returns its TLE.
	Uses the Celestrak API (sort of): http://www.celestrak.com/NORAD/elements/visual.txt
	"""
	tle_list = [e.strip() for e in requests.get('http://www.celestrak.com/NORAD/elements/visual.txt').text.split('\n')]
	tle_list = [tle_list[i:i+3] for i in range(0,len(tle_list)-2,3)]
	matching = list(filter(lambda x: sat.lower() in x[0].lower(), tle_list))
	if matching == None or len(matching) == 0:
		return None
	elif len(matching) > 1:
		log("Multiple matches found. Select:")
		print('\n'.join(["[%d]: %s" % (i, matching[i][0]) for i in range(len(matching))]))
		selected = int(input(' > '))
		return matching[selected]
	log("Selected satellite: %s" % matching[0][0])
	return matching[0]

def is_dark(lat, lon, times):
	"""
	Given a list of times, return a list of Booleans: true if it's dark outside at that time.
	Uses the Sunrise-Sunset API: http://sunrise-sunset.org/api
	"""
	dates = {}
	for tdatetime in times:
		tdate = tdatetime.split(' ')[0]
		ttime = tdatetime.split(' ')[1].strip()
		time.strptime(ttime,'%H:%M:%S')
		if tdate not in dates:
			params = {'formatted':'0','lat':lat,'lng':lon,'date':tdate}
			response = requests.get('http://api.sunrise-sunset.org/json', params=params).json()
			print(tdate)
			print(response)
			dates[tdate] = response
			time.sleep(1)

def main():
	args = parse_args()
	tle = get_tle(args.sat)
	if tle == None:
		log("Error: Satellite not found: %s" % args.sat)
		return
	tle_c = ephem.readtle(*tle)
	print(tle_c)
	[loc, lat, lon] = zip_to_latlong(args.zip)
	weather = get_weather(lat, lon, loc)
	if weather == None:
		log("Error: zip code not found: %s" % args.zip)
		return
	darktimes = is_dark(lat, lon, [weather[i][0] for i in range(len(weather))])
	print('\n'.join(str(weather[i]) for i in range(len(weather))))

if __name__ == '__main__':
	main()
