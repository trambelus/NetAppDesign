#!/usr/bin/env python

import requests
import time
import argparse
import os

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	try:
		with open(LOGFILE, 'a') as f:
			f.write(output + '\n')
	except:
		return

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-id', default='T25Pi', help='ID of Pi to search for')
	args = parser.parse_args()
	pi_id = args.id
	while True:
		try:
			resp = requests.get('http://jenna.xen.prgmr.com:5000/pissh/pull?id=%s' % pi_id)
			if resp.text != '':
				log("Found IP: attempting connection to %s" % resp.text)
				os.system('putty -ssh %s' % resp.text)
				return
		except Exception as ex:
			log(ex)
		time.sleep(1)

if __name__ == '__main__':
	main()
