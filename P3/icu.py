#!/usr/bin/env python

import argparse	# argument parsing
import ephem 		# for the orbit calculations
import requests	# to get Celestrak TLEs and NOAA data
import time			# gets the current date

try:
	import RPi.GPIO as GPIO
	GPIO_AVAILABLE = True
except ImportError:
	GPIO_AVAILABLE = False

NOAA_TOKEN_FILE = 'noaa.txt' # access token for NOAA API

<<<<<<< HEAD
# This is example code from source: http://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python
# This plays a sound through the raspberrypi audio out
	import pygame
	pygame.mixer.init()
	pygame.mixer.music.load("myFile.wav")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy() == True:
	    continue

=======
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
>>>>>>> origin/master

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
		"15 minutes before that satellite will become visible.\n\nSee http://www.celestrak.com/NORAD/elements/stations.txt " +
		"for a complete list of supported satellites."
	)
	parser.add_argument('-z', dest='zip', type=int, required=True, help="Zip code for which to check viewable events")
	parser.add_argument('-s', dest='sat', required=True, help="Name of satellite to view")
	return parser.parse_args()

def get_weather(zipcode):
	# http://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&locationid=ZIP:28801&startdate=2010-05-01&enddate=2010-05-01
	today = time.strftime('%Y-%m-%d')
	with open(NOAA_TOKEN_FILE) as f:
		token = f.readlines()[0].strip()
	params = {'datasetid':'GHCND', 'locationid':'ZIP:%05d'%zipcode, 'startdate':today, 'enddate':today, 'token':token}
	response = requests.get('http://www.ncdc.noaa.gov/cdo-web/api/v2/data', params=params)
	return response.text

def main():
	args = parse_args()
	print(get_weather(args.zip))

if __name__ == '__main__':
	main()
