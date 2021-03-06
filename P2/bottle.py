#!/usr/bin/env python
# Created by: Chris Cox
# Project 2
# ECE 4564
# Description: Created a server on the raspberrypiII that is connected to a breadboard via gpio pins
# when a client connects it can light up LEDs on the breadboard based on the message it receives through RabbitMQ.
# Code Credits: http://stackoverflow.com/questions/3430245/how-to-develop-an-avahi-client-server
import shelve
import time
import RPi.GPIO as GPIO
import sys
import pika
import json
import time
import re
import avahi
import dbus

# Global variables
LOGFILE = 'bottle.log'
SHELF_FILE = 'bottle'
shelf = shelve.open(SHELF_FILE)
status_success = {'Status':'success'}
status_failed = {'Status':'failed'}

#initializing count variable to display count of messages on LEDS
message_count = 0
# Setting up rabbitmq connections
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='bottle_queue')


# LED11 = 11 # Physical pin = 11. GPIO pin = 17
# LED12 = 12 # Physical pin = 12. GPIO pin = 18
# LED13 = 13 # Physical pin = 13. GPIO pin = 27
# LED15 = 15 # Physical pin = 15. GPIO pin = 22

LEDs = [11, 12, 13, 15]

# Setup GPIO as output
#included with your kits, these are marked 17, 18, 27, and 22. Change the GPIO accordingly
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LEDs[0], GPIO.OUT)
GPIO.output(LEDs[0], GPIO.LOW)

GPIO.setup(LEDs[1], GPIO.OUT)
GPIO.output(LEDs[1], GPIO.LOW)

GPIO.setup(LEDs[2], GPIO.OUT)
GPIO.output(LEDs[2], GPIO.LOW)

GPIO.setup(LEDs[3], GPIO.OUT)
GPIO.output(LEDs[3], GPIO.LOW)

__all__ = ["ZeroconfService"]

class ZeroconfService:
    """A simple class to publish a network service with zeroconf using
    avahi.

    """

    def __init__(self, name, port, stype="_http._tcp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text

    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g

    def unpublish(self):
        self.group.Reset()


def test():
    service = ZeroconfService(name="T25bottle", port=3000)
    service.publish()


def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

# This is the function for the push request
def push(parsed_incoming_pebble):
	#	Store in Shelve, sends reply that it pushed pebble
	#	When store is executed then update count
	# Adding in here to fix shelving unicode error
	shelf_key_push = parsed_incoming_pebble['MsgID']
	shelf_key_push = shelf_key_push.encode('utf8')
	if shelf_key_push in shelf:
		channel.basic_publish(exchange='', routing_key='bottle_queue', body=json.dumps(status_failed))
	else:
		shelf[shelf_key_push] = json.dumps(parsed_incoming_pebble) # Convert to JSON
		shelf.sync()
		channel.basic_publish(exchange='', routing_key='bottle_queue', body=json.dumps(status_success))
	# Update LEDs
	global message_count 
	message_count += 1
	turn_on_led(message_count)

# This is the function for the pull request
def pull(parsed_incoming_pebble):
	remove_pull = True
	pull_pebble = find_matches(parsed_incoming_pebble['Message'],parsed_incoming_pebble['Subject'],parsed_incoming_pebble['Age'],remove_pull)
	#	Remove message from Shelve send it to pebble pi.
	channel.basic_publish(exchange='', routing_key='bottle_queue', body=json.dumps(pull_pebble))
	#	When store is executed then update count
	# Update LEDs
	global message_count 
	#message_count -= 1
	turn_on_led(message_count)

# This is the function for the pullr request
def pullr(parsed_incoming_pebble):
	remove_pull = False
	pullr_pebble = find_matches(parsed_incoming_pebble['Message'],parsed_incoming_pebble['Subject'],parsed_incoming_pebble['Age'],remove_pull)
	#	Copy message from Shelve send it to pebble pi.
	channel.basic_publish(exchange='', routing_key='bottle_queue', body=json.dumps(pullr_pebble))
	#	When store is executed then update count
	# Update LEDs
	global message_count 
	message_count = message_count
	turn_on_led(message_count)

# This function will control the value outputted on the LEDS.
def turn_on_led(message_count):
	for i in range(4):
		if message_count & 2**i:
			#turn on LED
			GPIO.output(LEDs[i],GPIO.HIGH) # Turn on LED
			print('Turning on LED',LEDs[i])
		else:
			#turn off LED
			GPIO.output(LEDs[i],GPIO.LOW) # Turn off LED
			print('Turning off LED',LEDs[i])


# This function will perform age comparisons
def age_match(pattern,age):
	if pattern == '':
		return True
	if pattern[0] == '>':
		return int(age) > int(pattern[1:])
	if pattern[0] == '<':
		return int(age) < int(pattern[1:])
	return int(age) == int(pattern)

# This function will find all of the matching pebbles
def find_matches(Qm,Qs,Qa,remove_pull):
	ret = []
	if remove_pull == True:
		for key in shelf:
			entry = json.loads(shelf[key]) # Convert to dictionary
			if re.search(Qm,entry['Message']) and re.search(Qs,entry['Subject']) and age_match(Qa,entry['Age']):
				ret.append(entry)
				del shelf[key] # removes from shelf
				global message_count 
				message_count -= 1
		return ret;
	else:
		for key in shelf:
			entry = json.loads(shelf[key]) # Convert to dictionary
			if re.search(Qm,entry['Message']) and re.search(Qs,entry['Subject']) and age_match(Qa,entry['Age']):
				ret.append(entry)
		return ret;

# This is the callback that performs the actions of the bottle
def callback(ch, method, properties, incoming_pebble):
	# Message from rabbitMQ = incoming_pebble
	print(incoming_pebble)
	incoming_pebble = incoming_pebble.encode('ascii')
	parsed_incoming_pebble = json.loads(incoming_pebble) # Convert to dictionary
	if 'Action' not in parsed_incoming_pebble:
		channel.basic_publish(exchange='', routing_key='bottle_queue', body=incoming_pebble)
		time.sleep(5)
		return
	print(parsed_incoming_pebble)
	if parsed_incoming_pebble['Action'] == 'push':
		# For Push
		log("Syncing and closing shelf")
		push(parsed_incoming_pebble)
	elif parsed_incoming_pebble['Action'] == 'pullr':
		# For Pullr
		log("Syncing and closing shelf")
		pullr(parsed_incoming_pebble)
	elif parsed_incoming_pebble['Action'] == 'pull':
		# For Pull
		log("Syncing and closing shelf")
		pull(parsed_incoming_pebble)
		shelf.sync()

def main():
	test()
	global message_count
	message_count  = len(shelf) # Getting the new value for message count if the program is restarted
	channel.basic_consume(callback, queue='bottle_queue',no_ack=True)
	channel.start_consuming()
	shelf.close()
	service.unpublish()

if __name__ == '__main__':
	main()