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
SERVER_Q = 'bottle_q'

AUTHOR_DEFAULT = 'John'
AGE_DEFAULT = 20
TEAM

def log(*msg, additional='', console_only=False):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	print(output + additional)
	if not console_only:
		with open(LOGFILE, 'a') as f:
			f.write(output + '\n')

def send(json_msg):
	conn = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
	channel = conn.channel()
	channel.queue_declare(queue=SERVER_Q)
	channel.basic_publish(exchange='', routing_key=SERVER_Q, body=json_msg)

def msgid():
	return TEAM + str(int(time.mktime(time.gmtime())))

def push(args):
	json_msg = """
		{
			"Action": "push",
			"Author": "{0}",
			"Age": "{1}",
			"MsgID": "{2}",
			"Subject": "{3}",
			"Message": "{4}" 
		}
	""".format(args.author, args.age, msgid(), args.subject, args.message))
	send(json_msg)

# Handles pull and pullr
def pull(args):
	json_msg = """
		{
			"Action": "{0}",
			"Message": "{1}",
			"Subject": "{2}",
			"Age": "{3}"
		}
	""".format(args.action, args.messageQ, args.subjectQ, args.ageQ)
	send(json_msg)
	

def process_args(argv):
	# Setup and parse
	parser = argparse.ArgumentParser(description='Sends and receives messages to/from a bottle')
	parser.add_argument('-a', dest='action', choices=['push','pull','pullr'], required=True, help='Action to do')
	parser.add_argument('-s', dest='subject', nargs='+', help='Subject to send')
	parser.add_argument('-m', dest='message', nargs='+', help='Message to send')
	parser.add_argument('-Qm', dest='messageQ', nargs='+', help='Message to request (regex)')
	parser.add_argument('-Qs', dest='subjectQ', nargs='+', help='Subject to request (regex)')
	parser.add_argument('-Qa', dest='ageQ')
	parser.add_argument('--age', type=int, required=False, default=AGE_DEFAULT, help='Age of author to send')
	parser.add_argument('--author', type=string, required=False, default=AUTHOR_DEFAULT, help='Author name to send')
	parser.add_argument('--host', default=HOST, help='Hostname of the RabbitMQ server to connect to')
	args = parser.parse_args(argv)
	# Validate and join
	if args.action == 'push':
		if not (args.subject and args.message):
			parser.error("the following arguments are required for push: -s, -m")
		args.subject = ' '.join(args.subject)
		args.message = ' '.join(args.message)
	if args.action == 'pull' or args.action == 'pullr':
		if args.messageQ:
			args.messageQ = ' '.join(args.messageQ)
		if args.subjectQ:
			args.subjectQ = ' '.join(args.subjectQ)
	return args

		
def main():
	args = process_args(sys.argv[1:])
	log("Valid")
	print(args)
	if args.action == "push":
		push(args)
	if args.action == "pull" or args.action == "pullr":
		pull(args)

if __name__ == '__main__':
	main()