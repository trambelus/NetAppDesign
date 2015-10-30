#!/usr/bin/env python3
# pebble.py
# Author: John McDouall
# ECE 4564

import argparse
import json
import pika
import sys
import shelve
import time
import zeroconf

LOGFILE = 'pebble.log'

def log(*msg, additional='', console_only=False):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	print(output + additional)
	if not console_only:
		with open(LOGFILE, 'a') as f:
			f.write(output + '\n')

def push(msg):
	pass

def pull():
	pass

def pullr():
	pass

def process_args(argv):
	parser = argparse.ArgumentParser(description='Sends and receives messages to/from a bottle')
	parser.add_argument('-a', dest='action', choices=['push','pull','pullr'], required=True)
	parser.add_argument('-s', dest='subject', nargs='+')
	parser.add_argument('-m', dest='message', nargs='+')
	parser.add_argument('-Qm', dest='messageQ', nargs='+')
	parser.add_argument('-Qs', dest='subjectQ', nargs='+')
	parser.add_argument('-Qa', dest='ageQ')
	args = parser.parse_args(argv)
	if args.action == 'push':
		if not (args.subject and args.message):
			parser.error("the following arguments are required for push: -s, -m")
		args.subject = ' '.join(args.subject)
		args.message = ' '.join(args.message)
	if args.action == 'pull' or args.action == 'pullr':
		if not (args.messageQ or args.subjectQ or args.ageQ):
			parser.error("one of the following arguments is required for %s: -Qm, -Qs, Qa" % args.action)
	return args

		
def main():
	args = process_args(sys.argv[1:])
	log("Valid")
	print(args)

if __name__ == '__main__':
	main()