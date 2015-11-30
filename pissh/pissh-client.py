#!/usr/bin/env python

import requests
import time
import argparse
import os
import configparser

CONFIG_FILE = 'pissh.ini'

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
	parser.add_argument('-id', required=False, help='ID of Pi to search for')
	args = parser.parse_args()

	config = configparser.ConfigParser()
	if args.id == None:
		config.read(CONFIG_FILE)
		if config.sections():
			pi_id = config['defaults']['id']
		else:
			parser.error("Config file %s not found: id argument required" % CONFIG_FILE)
	else:
		pi_id = args.id
		config = configparser.ConfigParser()
		config['defaults'] = { 'id': pi_id }
		with open(CONFIG_FILE, 'w') as configfile:
			config.write(configfile)

	while True:
		try:
			resp = requests.get('http://jenna.xen.prgmr.com:5281/pissh/pull?id=%s' % pi_id)
			if resp.text != '':
				log("Found IP: attempting connection to %s" % resp.text)
				os.system('putty -ssh %s' % resp.text)
				if not 'y' in input("SSH connection closed. Reconnect? (y/n): "):
					print("Exiting")
					return
				print("Attempting reconnection")
		except Exception as ex:
			log(ex)
		time.sleep(1)

if __name__ == '__main__':
	main()
