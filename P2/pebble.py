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
from zeroconf import ServiceBrowser, Zeroconf

LOGFILE = 'pebble.log'
DBFILE = 'pebble'
BOTTLE_Q = 'bottle_queue'

AUTHOR_DEFAULT = 'John'
AGE_DEFAULT = 20
TEAM = 'Team25'
SNAME = "T25bottle"

username = 'john'
password = '12345'
verbose = False

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

def logv(*msg):
	"""
	Exactly the same as log(), if verbose=True. Otherwise does nothing.
	"""
	if verbose:
		log(*msg)

def send(json_msg, channel):
	channel.basic_publish(exchange='', routing_key=BOTTLE_Q, body=json_msg)

def msgid():
	# MsgID format: TeamXX_epochtime
	return TEAM + '_' + str(int(time.mktime(time.gmtime())))

def push(args, channel):
	logv(args.author, args.age, msgid(), args.subject, args.message)
	json_msg = """
		{{
			"Action": "push",
			"Author": "{0}",
			"Age": "{1}",
			"MsgID": "{2}",
			"Subject": "{3}",
			"Message": "{4}" 
		}}
	""".format(args.author, args.age, msgid(), args.subject, args.message)
	log("Sending JSON: \n%s" % json_msg)
	send(json_msg, channel)

	def cb(channel, message, properties, body):
		logv("Response received: ", body)
		log("Server returned status: %s" % json.loads(body.decode('UTF-8'))['Status'])
		# Stop the infinite loop on the channel
		channel.stop_consuming()

	logv("Waiting for response...")
	channel.basic_consume(cb, queue=BOTTLE_Q, no_ack=True)
	channel.start_consuming()

# Handles pull and pullr
def pull(args, channel):
	json_msg = """
		{{
			"Action": "{0}",
			"Message": "{1}",
			"Subject": "{2}",
			"Age": "{3}"
		}}
	""".format(args.action, args.messageQ, args.subjectQ, args.ageQ)
	log("Sending JSON: \n%s" % json_msg)
	send(json_msg, channel)

	def cb(channel, message, properties, body):
		logv("Response: ", body)
		# Stop the infinite loop on the channel
		channel.stop_consuming()
		responses = json.loads(body.decode('UTF-8'))
		if len(responses) == 0:
			log("No matching entries found.")
		else:
			log("Found %d responses:" % len(responses))
			shelf = shelve.open(DBFILE)
			for i in range(len(responses)):
				log("Response %d:\n%s" % (i+1, responses[i]))
				shelf[responses[i]['MsgID']] = responses[i]
			logv("Syncing and closing shelf")
			shelf.sync()
			shelf.close()

	channel.basic_consume(cb, queue=BOTTLE_Q, no_ack=True)
	logv("Waiting for response...")
	channel.start_consuming()

class Listener(object):
	def __init__(cb):
		self.cb = cb

	def add_service(self, zeroconf, type, name):
		info = zeroconf.get_service_info(type, name)
		if SNAME in name:
			cb(name)

def get_host():

	ret = None
   def cb(name):
   	ret = name
   	zeroconf.close()

	zeroconf = Zeroconf()
	listener = Listener(cb)
	browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
	logv("Searching for %s" % SNAME)
	while not ret:
		time.sleep(1)
	return ret


def process_args(argv):
	# Setup and parse
	parser = argparse.ArgumentParser(description='Sends and receives messages to/from a bottle')
	parser.add_argument('-a', dest='action', choices=['push','pull','pullr'], required=True, help='Action to do')
	parser.add_argument('-s', dest='subject', nargs='+', help='Subject to send')
	parser.add_argument('-m', dest='message', nargs='+', help='Message to send')
	parser.add_argument('-Qm', dest='messageQ', nargs='+', help='Message to request (regex)')
	parser.add_argument('-Qs', dest='subjectQ', nargs='+', help='Subject to request (regex)')
	parser.add_argument('-Qa', dest='ageQ')
	parser.add_argument('--age', type=int, default=AGE_DEFAULT, help='Age of author to send')
	parser.add_argument('--author', default=AUTHOR_DEFAULT, help='Author name to send')
	parser.add_argument('--host', help='Hostname of the RabbitMQ server to connect to')
	parser.add_argument('--verbose', action='store_true', help='Verbose mode: print more stuff')
	parser.add_argument('--username', help='Username to use when connecting to RabbitMQ server')
	parser.add_argument('--password', help='Password to use when connecting to RabbitMQ server')
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
		else:
			args.messageQ = ''

		if args.subjectQ:
			args.subjectQ = ' '.join(args.subjectQ)
		else:
			args.subjectQ = ''

		if not args.ageQ:
			args.ageQ = ''

	if args.verbose:
		global verbose; verbose = True
	if args.host:
		global host; host = args.host
	else:
		global host; host = get_host()

	if args.username:
		global username; username = args.username
	if args.password:
		global password; password = args.password

	return args

# Get connected to the RabbitMQ server, and return the connection and channel
def setup_conn():
	logv("Host: %s" % host)

	connected = False # Have we connected yet?
	timeout = 1 # Increase the wait between connection attempts
	while not connected:
		try:
			conn = pika.BlockingConnection(pika.ConnectionParameters(host=host,
				virtual_host='/', credentials=pika.PlainCredentials(username=username, password=password)))
			connected = True
		except pika.exceptions.ConnectionClosed:
			logv("Could not connect to host %s, vhost %s, retrying in %d sec" % (host, '/', timeout))
			time.sleep(int(timeout))
			timeout = timeout + 1 if timeout < 5 else 5

	# Finally connected
	channel = conn.channel()
	channel.queue_declare(queue=BOTTLE_Q)
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
	logv("Finished")

if __name__ == '__main__':
	main()
