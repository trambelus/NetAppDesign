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
DBFILE = 'pebble.db'
SERVER_Q = 'bottle_queue'

AUTHOR_DEFAULT = 'John'
AGE_DEFAULT = 20
TEAM = 'Team25'

verbose = False
host = 'localhost'

def log(*msg, additional='', console_only=False):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output + additional)
	if not console_only:
		with open(LOGFILE, 'a') as f:
			f.write(output + '\n')

def logv(*msg, additional='', console_only=False):
	if verbose:
		log(*msg, additional=additional, console_only=console_only)

def send(json_msg, channel):
	channel.basic_publish(exchange='', routing_key=SERVER_Q, body=json_msg)

def msgid():
	# MsgID format: TeamXX_epochtime
	return TEAM + '_' + str(int(time.mktime(time.gmtime())))

def push(args, channel):
	json_msg = """
		{
			"Action": "push",
			"Author": "{0}",
			"Age": "{1}",
			"MsgID": "{2}",
			"Subject": "{3}",
			"Message": "{4}" 
		}
	""".format(args.author, args.age, msgid(), args.subject, args.message)
	logv("Sending JSON: \n%s" % json_msg)
	send(json_msg, channel)

# Handles pull and pullr
def pull(args, channel):
	json_msg = """
		{
			"Action": "{0}",
			"Message": "{1}",
			"Subject": "{2}",
			"Age": "{3}"
		}
	""".format(args.action, args.messageQ, args.subjectQ, args.ageQ)
	logv("Sending JSON: \n%s" % json_msg)
	send(json_msg, channel)
	def cb(channel, message, properties, body):
		log("Response: ", channel, message, properties, body)
		body = json.loads(body)
		channel.stop_consuming()
		shelf = shelve.open(DBFILE)
		shelf[body['MsgID']] = body
		logv("Syncing and closing shelf")
		shelf.sync()
		shelf.close()

	channel.basic_consume(cb, queue=SERVER_Q, no_ack=True)
	logv("Waiting for response...")
	channel.start_consuming()


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
	parser.add_argument('--author', required=False, default=AUTHOR_DEFAULT, help='Author name to send')
	parser.add_argument('--host', help='Hostname of the RabbitMQ server to connect to')
	parser.add_argument('--verbose', action='store_true', help='Verbose mode: print more stuff')
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
	if args.verbose:
		global verbose
		verbose = True
	if args.host:
		global host
		host = args.host
	return args

def setup_conn():
	logv("Host: %s" % host)
	conn = pika.BlockingConnection(pika.ConnectionParameters(host=host,
		virtual_host='/', credentials=pika.PlainCredentials(username='john', password='12345')))
	channel = conn.channel()
	channel.queue_declare(queue=SERVER_Q)
	return (conn, channel)
		
def main():
	args = process_args(sys.argv[1:])
	logv("Valid")
	logv(args)
	logv("Setting up connection")
	(conn, channel) = setup_conn()
	if args.action == "push":
		push(args, channel)
	if args.action == "pull" or args.action == "pullr":
		pull(args, channel)

if __name__ == '__main__':
	main()
