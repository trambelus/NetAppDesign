#!/usr/bin/env python

import argparse
import ephem 		# for the orbit calculations
import requests	# to get Celestrak TLEs and NOAA data

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

def parse_args():
	parser = argparse.ArgumentParser(
		prog='ICU',
		description="Given a zip code and satellite code, generates notifications " +
		"15 minutes before that satellite will become visible.\n\nSee http://www.celestrak.com/NORAD/elements/stations.txt " +
		"for a complete list of supported satellites.")
	parser.add_argument('-z', dest='zip', type=int, required=True, help="Zip code for which to check viewable events")
	parser.add_argument('-s', dest='sat', required=True, help="Name of satellite to view")
	return parser.parse_args()
