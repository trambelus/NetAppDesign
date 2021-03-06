#!/usr/bin/env python3
# coding=UTF-8

# Created by: John McDouall; Chris Cox
# Project 3
# ECE 4564
# Description: Created a satellite tracker on the raspberrypiII that is connected to a breadboard via gpio pins
# When a satellite is visible(weather, sunlight, elevation angle) then the PI sends out alerts via GPIO pins, audio jack, and sends a text message
# 15 minutes before an event is viewable.  Our program uses RESTful requests and responses to and from celestrak/openweathermap.  
# We also used a singleton list to start and stop threaded functions for playing an audio file as well as flashing an LED.
# Code Credits: http://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python

import argparse	# argument parsing
import csv			# to convert zip code to lat/long
import ephem 		# for the orbit calculations
import requests	# to get Celestrak TLEs and NOAA data
import time			# gets the current date
from pprint import pprint # for debugging
import shelve
import calendar
from twilio.rest import TwilioRestClient
from threading import Thread

try:
	import pygame
except ImportError:
	print("Failed importing pygame")

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

R2D = 180/3.14159265

if GPIO_AVAILABLE:
	# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
	LED = 12
	FLASH_DELAY = 1 # flash delay in seconds
	# Setup GPIO as output
	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)
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
		log("Flashing!")

#This funciton sends a text message using Twilio
def sendTextMessage(sat, transit_info):
	textMessage = "Satellite '%s' will be visible in 15 minutes!\nTransit at %s" % (str(sat), transit_info)
	CLIENT.messages.create(to='+15407974693', from_='+15406135061', body=textMessage)
	log('Sent Text Message!')

# This function plays a sound through the audio port of the raspberry pi
def playSound(is_active):
	while True:
		pygame.mixer.init()
		pygame.mixer.music.load("hello_mister_gopher.wav")
		if len(is_active) == 0:
			pygame.mixer.music.stop();
		if is_active[0]:
			log('Sounding Alert!')
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
	parser.add_argument('-s', dest='sat_id', help="NORAD ID of satellite to view")
	parser.add_argument('-n', dest='sat_str', help="Name of satellite to view")
	parser.add_argument('-v', dest='verbose', action='store_true')
	args = parser.parse_args()
	if not (args.sat_id or args.sat_str):
		parser.error("Either -s or -n is required")
	return args

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

def get_tle_from_str(sat_str):
	"""
	Given a string describing a satellite, returns its TLE.
	Uses the Celestrak API (sort of): http://www.celestrak.com/NORAD/elements/visual.txt
	"""
	tle_list = [e.strip() for e in requests.get('http://www.celestrak.com/NORAD/elements/visual.txt').text.split('\n')]
	tle_list = [tle_list[i:i+3] for i in range(0,len(tle_list)-2,3)]
	matching = list(filter(lambda x: sat_str.lower() in x[0].lower(), tle_list))
	if matching == None or len(matching) == 0:
		return None
	elif len(matching) > 1:
		log("Multiple matches found. Select:")
		print('\n'.join(["[%d]: %s" % (i, matching[i][0]) for i in range(len(matching))]))
		selected = int(input(' > '))
		return matching[selected]
	log("Selected satellite: %s" % matching[0][0])
	return matching[0]

def get_tle_from_norad(sat_id):
	"""
	Given a NORAD id, returns a TLE.
	Uses this random website we found: http://www.n2yo.com/satellite
	Also uses some ugly ugly web scraping, please don't look.
	"""
	html = requests.get('http://www.n2yo.com/satellite/?s=%s' % str(sat_id)).text
	#print(html[:100])
	div_loc = html.find('<div id="tle">')
	#print(div_loc)
	if div_loc == -1:
		return None
	tle = [str(sat_id)]
	tle.extend(html[div_loc+23:html.find('</div>',div_loc)-70].split('\r\n'))
	return tle

def is_clear(zip, lat, lon, t_date):
	"""
	Given a set of coordinates and a date/time, returns True if the weather will be clear at that time.
	Uses a shelf cache to minimize API access.
	Uses the OpenWeatherMap API: http://openweathermap.org/api
	"""

	weathershelf = shelve.open('weather-%d' % zip)

	# if it's an empty shelf or it hasn't been updated in at least 3 hours or there's no weather data for this date:
	if ('last-update' not in weathershelf) or \
		(time.mktime(time.localtime()) > (weathershelf['last-update'] + 3*60*60)) or \
		(t_date not in weathershelf):

		log("Updating weather cache")
		with open(TOKEN_FILE) as f:
			token = f.readlines()[0].strip()

		params = {'lat':lat,'lon':lon, 'mode':'json', 'appid':token, 'cnt':'16'}
		headers = {'token':token}
		response = requests.get('http://api.openweathermap.org/data/2.5/forecast/daily', params=params, headers=headers).json()['list']
		for item in response:
			#print("Adding %s to weathershelf" % time.strftime('%Y/%m/%d', time.localtime(item['dt'])))
			i_date = time.strftime('%Y/%m/%d', time.localtime(item['dt']))
			#print(i_date)
			weathershelf[i_date] = item['weather'][0]['main']

		weathershelf['last-update'] = time.mktime(time.localtime())
		weathershelf.sync()

	try:
		isclear = weathershelf[t_date] == 'Clear'
	except KeyError:
		return None

	weathershelf.close()
	return isclear

def sun_position_right(obs, t_date):
	"""
	Given an observer, return a Boolean: true if the sun is in the right spot at that time.
	"""
	sun = ephem.Sun()
	sun.compute(obs)
	# print("At %s: next rise is %sh away, previous set is %sh away, next set is %sh away" % 
	# 	(obs.date, round(24*(obs.next_rising(sun)-obs.date),2),round(24*(obs.date-obs.previous_setting(sun)),2),
	# 		round(24*(obs.next_setting(sun)-obs.date),2)))
	# print("%s" % obs.date)
	# print("next rise: %s, %s" % (obs.next_rising(sun), obs.next_rising(sun) - obs.date > 1/24))
	# print("next set: %s, night=%s" % (obs.next_setting(sun), obs.next_rising(sun) < obs.next_setting(sun)))
	# print("previous set: %s, %s" % (obs.previous_setting(sun), obs.date - obs.previous_setting(sun) > 1/24))

	isn = (obs.next_rising(sun) < obs.next_setting(sun)) 	# is night
	tcr = (obs.next_rising(sun) - obs.date > 1/24) 			# too close to rise
	tcs = (obs.date - obs.previous_setting(sun) > 1/24) 	# too close to set

	obs.date = t_date
	sun.compute(obs)
	pos = sun.alt > SUN_MIN_ALT and sun.alt < SUN_MAX_ALT # sun pos right
	# print(" %s" % obs.date)
	# print("sun position: %f deg" % (sun.alt*R2D))
	# print("sun azimuth:  %f deg" % (sun.az*R2D))
	# print("position: %s" % position)
	# print("\t\tVISIBLE: %s" % (dark and position))
	return (isn and tcr and tcs, pos)

def get_transit_times(sat, observer, ts_epoch):
	"""
	Given a pyephem satellite, pyephem observer, and array of epoch times,
	return a set of all the transit times for that satellite from that observer
	on each of the days containing the times in the given array.
	"""
	#print("given datetimes:", ts_epoch)
	transits = []
	times = []
	for t_epoch in ts_epoch:
		t_datetime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(t_epoch))
		#print("Checking date: %s" % t_datetime)
		observer.date = t_datetime
		sat.compute(observer)
		nextpass = observer.next_pass(sat)
		if not str(nextpass[2]) in times:
			transits.append(nextpass)
			times.append(str(nextpass[2]))

	ret = list(transits)
	ret = sorted(ret, key=lambda s: s[2])
	return ret

def wait_for_transit(t_datetime, sat, transit_info):
	"""
	Given a datetime (yyyy/mm/dd hh:mm:ss), satellite identifier, and info string,
	wait until 15 minutes before the datetime and do all the alert stuff.
	The text message will contain the info string and satellite identifier (string or NORAD ID, whatever).
	The LEDs will flash (if this is running on a Pi) and a sound will loop.
	"""
	t_epoch = calendar.timegm(time.strptime(t_datetime, "%Y/%m/%d %H:%M:%S"))
	# Wait for 15 minutes before
	log("Alerting 15 minutes before %s UTC" % t_datetime)
	log("Sleeping for %d seconds" % (t_epoch - (time.time() + 15*60)))
	while time.time() + 15*60 < t_epoch:
		time.sleep(5)
	# Send text, turn on all the stuff
	is_active = [True]
	Thread(target=flash, args=(is_active,)).start()
	Thread(target=playSound, args=(is_active,)).start()
	sendTextMessage(sat, transit_info)
	# Wait for 5 minutes before
	while time.time() + 5*60 < t_epoch:
		time.sleep(5)
	# Stop all the stuff
	is_active.clear()

def main():
	args = parse_args()

	# Zip to lat/long
	[loc, lat, lon] = zip_to_latlong(args.zip)
	log("Getting information for %s: %s, %s" % (loc,lat,lon))

	# ephem stuff
	observer = ephem.Observer()
	observer.lat, observer.lon = lat, lon

	if args.sat_str:
		tle = get_tle_from_str(args.sat_str)
		args.sat = args.sat_str
		if tle == None:
			log("Error: Satellite name not found: %s" % args.sat_str)
			return
	elif args.sat_id:
		tle = get_tle_from_norad(args.sat_id)
		args.sat = args.sat_id
		if tle == None:
			log("Error: Satellite with ID %s not found" % args.sat_id)
			return

	log("Found TLE:")
	print('\n'.join(tle))
	sat = ephem.readtle(*tle)
	print()

	# Calculate a range of times and iterate
	times = [time.time() + 60*60*hour + 24*60*60*day for day in range(15) for hour in range(24)]
	transits = []
	i = 0

	for [s_t, s_az, pk_datetime, pk_alt, e_t, e_az] in get_transit_times(sat, observer, times):
		# for each: is it clear? is it dark?
		i += 1
		observer.date = pk_datetime
		t_date = str(pk_datetime).split(' ')[0]
		(dark, pos) = sun_position_right(observer, pk_datetime)
		clear = is_clear(args.zip, lat, lon, t_date)

		if clear == None:
			print("Could not get weather information for %s; cutting off here" % t_date)
			break
		sathigh = pk_alt > SAT_MIN_ALT
		#print("%s: sun=%s, clear=%s" % (pk_datetime, sun, clear))
		
		# cdr: Translates an azimuth direction in radians into a cardinal direction
		cdr = lambda x: ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'][round(x/22.5*R2D)%16]

		transits.append((dark, pos, clear, sathigh, "%s peak at %d°, start az %d° (%s), end az %d° (%s), duration %ds" % \
			(pk_datetime, pk_alt*R2D, s_az*R2D, cdr(s_az), e_az*R2D, cdr(e_az), (e_t-s_t)*86400)))
		#print("%s: sun:%s, clear:%s" % (t_datetime, sun, clear))
	selected_transits = [t[-1] for t in transits if all(t[:-1])][:5]
	log("Found %d transits in next 16 days" % (len(selected_transits)))
	print('\n'.join(selected_transits))

	if args.verbose:
		print("\nRejected:")

		def reason(t):
			reasons = []
			if not t[0]:
				reasons.append("not dark enough")
			if not t[1]:
				reasons.append("sun in wrong position")
			if not t[2]:
				reasons.append("not clear enough")
			if not t[3]:
				reasons.append("satellite not high enough")
			return ', '.join(reasons)

		print('\n'.join(["%s \n\t(%s)" % (t[-1],reason(t)) for t in transits if not all(t[:-1])]))

	print("Forecast:")
	weathershelf = shelve.open('weather-%d' % args.zip)
	for k in sorted(weathershelf.keys()):
		if k != 'last-update':
			print("%s: %s" % (k, weathershelf[k]))

	if len(selected_transits) > 0:
		wait_for_transit(' '.join(selected_transits[0].split(' ')[:2]), args.sat, selected_transits[0])
	else:
		log("No transits to wait for; exiting now")

if __name__ == '__main__':
	# print(is_dark('37.2','-80.4',1447537740))
	# print(is_clear('37.2','-80.4',1447537740))
	main()
