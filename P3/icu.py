#!/usr/bin/env python

import argparse	# argument parsing
import csv			# to convert zip code to lat/long
import ephem 		# for the orbit calculations
import requests	# to get Celestrak TLEs and NOAA data
import time			# gets the current date
from pprint import pprint # for debugging
import shelve
import calendar
from twilio.rest import TwilioRestClient

try:
	import pygame
except ImportError:
	pass

try:
	import RPi.GPIO as GPIO
	GPIO_AVAILABLE = True
except ImportError:
	GPIO_AVAILABLE = False

CLIENT = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')
LOGFILE = 'icu.log'
TOKEN_FILE = 'openweathermap.txt' # access token for NOAA API
ZIPS_FILE = 'zip_code_database.csv' # to convert zip code to lat/long

SUN_MIN_ALT = -0.4363319 # about -25 degrees
SUN_MAX_ALT = -0.1745327 # about -10 degrees
SAT_MIN_ALT =  0.4363319 # about +25 degrees

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

#This funciton sends a text message using Twilio
def sendTextMessage():
	CLIENT.messages.create(to='+15407974693', from_='+15406135061', body="Playing Hello Mister Gopher", media_url="http://www.bassmaster.com/sites/default/files/imagecache/slideshow_image/06DeanRojas_Record.jpg")
	print('Sent Text Message!')

# This function plays a sound through the audio port of the raspberry pi
def playSound(is_active):
	while True:
		pygame.mixer.init()
		pygame.mixer.music.load("hello_mister_gopher.wav")
		if len(is_active) == 0:
			pygame.mixer.music.stop();
		if is_active[0]:
			print('Sounding Alert!')
			pygame.mixer.music.play()
			while pygame.mixer.music.get_busy() == True:
				continue
			time.sleep(FLASH_DELAY)

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
	parser.add_argument('--validation', action='store_true')
	return parser.parse_args()

def zip_to_latlong(zipcode):
	"""
	Given a zip code, returns a 3-tuple containing location name, latitude, and longitude, all strings.
	"""
	csvfile = open(ZIPS_FILE,'r')
	r = csv.reader(csvfile)
	loc = [l for l in r if l[0] == str(zipcode)]
	csvfile.close()
	if len(loc) == 0:
		return None
	loc = loc[0]
	return (loc[2], loc[9], loc[10])

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

def is_clear(lat, lon, t_date):
	"""
	Given a set of coordinates and a time, returns True if the weather will be clear at that time.
	Uses a shelf cache to minimize API access.
	Uses the OpenWeatherMap API: http://openweathermap.org/api
	"""

	weathershelf = shelve.open('weather')

	# if it's an empty shelf or it hasn't been updated in at least 3 hours or there's no weather data for this date:
	if 'last-update' not in weathershelf or \
		time.mktime(time.localtime()) > (weathershelf['last-update'] + 3*60*60) or \
		t_date not in weathershelf:

		log("Updating weather cache")
		with open(TOKEN_FILE) as f:
			token = f.readlines()[0].strip()
		params = {'lat':lat,'lon':lon, 'mode':'json', 'appid':token, 'cnt':'16'}
		headers = {'token':token}
		response = requests.get('http://api.openweathermap.org/data/2.5/forecast/daily', params=params, headers=headers).json()['list']
		for item in response:
			i_date = time.strftime('%Y/%m/%d', time.localtime(item['dt']))
			weathershelf[i_date] = item['weather'][0]['main'] == 'Clear'
		weathershelf['last-update'] = time.mktime(time.localtime())
		weathershelf.sync()

	is_clear = weathershelf[t_date]
	weathershelf.close()
	return is_clear

def sun_position_right(obs):
	"""
	Given an observer, return a Boolean: true if the sun is in the right spot at that time.
	"""
	sun = ephem.Sun()
	sun.compute(obs)
	print("At %s: next rise is %s away, previous set is %s away" % (obs.date, obs.next_rising(sun)-obs.date,obs.date-obs.previous_setting(sun)))
	dark = (obs.next_rising(sun) < obs.next_setting(sun) \
		and obs.next_rising(sun) - obs.date > 1/24 \
		and obs.date - obs.previous_setting(sun) > 1/24)
	position = sun.alt > SUN_MIN_ALT and sun.alt < SUN_MAX_ALT
	return dark and position

def get_transit_times(sat, observer, ts_epoch):
	"""
	Given a pyephem satellite, pyephem observer, and array of epoch times,
	return a set of all the transit times for that satellite from that observer
	on each of the days containing the times in the given array.
	"""
	#print("given datetimes:", ts_epoch)
	transits = set()
	for t_epoch in ts_epoch:
		t_datetime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(t_epoch))
		#print("Checking date: %s" % t_datetime)
		observer.date = t_datetime
		sat.compute(observer)
		nextpass = observer.next_pass(sat)[2:4]
		if nextpass[1] > SAT_MIN_ALT: # it's high enough!
			transits.add(str(nextpass[0]))
	ret = list(transits)
	ret.sort()
	return ret

def main():
	args = parse_args()

	# Zip to lat/long
	[loc, lat, lon] = zip_to_latlong(args.zip)
	log("Getting information for %s: %s, %s" % (loc,lat,lon))

	# ephem stuff
	observer = ephem.Observer()
	observer.lat, observer.lon = lat, lon
	tle = get_tle(args.sat)
	if tle == None:
		log("Error: Satellite not found: %s" % args.sat)
		return
	sat = ephem.readtle(*tle)

	# Calculate a range of times and iterate
	times = [time.time() + 60*60*hour + 86400*day for day in range(16) for hour in range(24)]

	for t_datetime in get_transit_times(sat, observer, times):
		# for each: is it clear? is it dark?
		observer.date = t_datetime
		t_date = t_datetime.split(' ')[0]
		sun = sun_position_right(observer)
		clear = is_clear(lat, lon, t_date)
		print("%s: sun:%s, clear:%s" % (t_datetime, sun, clear))

if __name__ == '__main__':
	# print(is_dark('37.2','-80.4',1447537740))
	# print(is_clear('37.2','-80.4',1447537740))
	main()