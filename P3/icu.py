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
import pygame

try:
	import RPi.GPIO as GPIO
	GPIO_AVAILABLE = True
except ImportError:
	GPIO_AVAILABLE = False

CLIENT = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')
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

def sendMessage():
	CLIENT.messages.create(to='+15407974693', from_='+15406135061', body="Playing Hello Mister Gopher", media_url="http://www.bassmaster.com/sites/default/files/imagecache/slideshow_image/06DeanRojas_Record.jpg")
	print('Sent Text Message')
	pygame.mixer.init()
	pygame.mixer.music.load("hello_mister_gopher.wav")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy() == True:
	    continue
	print('Finished Playing WAV File')

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

def is_clear(lat, lon, t_epoch):
	"""
	Given a set of coordinates and a time, returns True if the weather will be clear at that time.
	Uses a shelf cache to minimize API access.
	Uses the OpenWeatherMap API: http://openweathermap.org/api
	"""
	t_epoch = int(t_epoch) # just in case

	weathershelf = shelve.open('weather')

	if len(weathershelf) != 0:
		mintime = min([abs(t_epoch - int(wt_epoch)) for wt_epoch in weathershelf.keys() if wt_epoch != 'last-update'])

	if 'last-update' not in weathershelf or \
		time.mktime(time.localtime()) > (weathershelf['last-update'] + 3*60*60) or \
		mintime > 3*60*60:

		log("Updating weather cache")
		with open(TOKEN_FILE) as f:
			token = f.readlines()[0].strip()
		params = {'lat':lat,'lon':lon, 'mode':'json', 'appid':token}
		headers = {'token':token}
		response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=params, headers=headers).json()['list']
		for item in response:
			weathershelf[str(item['dt'])] = (item['weather'][0]['main'] == 'Clear')
		weathershelf['last-update'] = time.mktime(time.localtime())
		weathershelf.sync()

	mintime = min([abs(t_epoch - int(wt_epoch)) for wt_epoch in weathershelf.keys() if wt_epoch != 'last-update'])

	besttime = [wt_epoch for wt_epoch in weathershelf.keys()
		if wt_epoch != 'last-update' and abs(t_epoch - int(wt_epoch)) == mintime][0]

	is_clear = weathershelf[besttime]
	weathershelf.close()
	return is_clear

def is_dark(lat, lon, t_epoch):
	"""
	Given a date/time, return a Boolean: true if it's dark outside at that time.
	Uses a shelf cache to minimize API access.
	Uses the Sunrise-Sunset API: http://sunrise-sunset.org/api
	"""
	t_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_epoch))
	t_date = t_datetime.split(' ')[0]
	t_time = t_datetime.split(' ')[1].strip()
	time.strptime(t_time,'%H:%M:%S')
	darkshelf = shelve.open('dark')
	#darkshelf.clear()
	if t_date not in darkshelf:
		log("Updating sunset cache")
		params = {'formatted':'0','lat':lat,'lng':lon,'date':t_date}
		response = requests.get('http://api.sunrise-sunset.org/json', params=params).json()
		darkshelf[t_date] = response
	dark = darkshelf[t_date]['results']
	darkshelf.close()
	print(dark)
	sunrise = calendar.timegm(time.strptime(dark['sunrise'], "%Y-%m-%dT%H:%M:%S+00:00"))
	sunset = calendar.timegm(time.strptime(dark['sunset'], "%Y-%m-%dT%H:%M:%S+00:00"))
	isdark = t_epoch < sunrise-60*60 or t_epoch > sunset+60*60
	return isdark

def get_transit_times(sat, observer, ts_epoch):
	"""
	Given a pyephem satellite, pyephem observer, and array of epoch times,
	return a set of all the transit times for that satellite from that observer
	on each of the days containing the times in the given array.
	"""
	print("given datetimes:", ts_epoch)
	transits = set()
	for t_epoch in ts_epoch:
		t_datetime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(t_epoch))
		print("Checking date: %s" % t_datetime)
		observer.date = t_datetime
		sat.compute(observer)
		transits.add(observer.next_pass(sat))
	ret = list(transits)
	ret.sort()
	print(ret)
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
	todaystart = time.mktime(time.localtime())//86400*86400
	times = [todaystart + 60*hour + 86400*day for day in range(5) for hour in range(24)]

	for t_epoch in get_transit_times(sat, observer, times):
		# for each: is it clear? is it dark?
		#clear = is_clear(lat, lon, t_epoch)
		if clear == None:
			log("Error: zip code not found: %s" % args.zip)
			return
		#dark = is_dark(lat, lon, t_epoch)
		if clear and dark:
			alert()

if __name__ == '__main__':
	# print(is_dark('37.2','-80.4',1447537740))
	# print(is_clear('37.2','-80.4',1447537740))
	main()
