#!/usr/bin/env python
# Created by: Chris Cox
# Project 2
# ECE 4564
# Description: Created a server on the raspberrypiII that is connected to a breadboard via gpio pins
# when a client connects it can light up LEDs on the breadboard based on the message it receives through RabbitMQ.
# Commented out code is from example code.  I left it so i can follow what is happening in the examples.
import shelve
import time
import pybonjour
import RPi.GPIO as GPIO
import sys
import pika
import json
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='bottle_queue')

# def fib(n):
#     if n == 0:
#         return 0
#     elif n == 1:
#         return 1
#     else:
#         return fib(n-1) + fib(n-2)

# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
LED12 = 12 # Physical pin = 12. GPIO pin = 18
LED13 = 13 # Physical pin = 13. GPIO pin = 27
LED15 = 15 # Physical pin = 15. GPIO pin = 22
LED16 = 16 # Physical pin = 16. GPIO pin = 23

# Setup GPIO as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED12, GPIO.OUT)
GPIO.output(LED12, GPIO.LOW)

GPIO.setup(LED13, GPIO.OUT)
GPIO.output(LED13, GPIO.LOW)

GPIO.setup(LED15, GPIO.OUT)
GPIO.output(LED15, GPIO.LOW)

GPIO.setup(LED16, GPIO.OUT)
GPIO.output(LED16, GPIO.LOW)

FLASH_DELAY = 1 # flash delay in seconds

# This function will control the value outputted on the LEDS.
def binary_led(count):
	if count = 
	# c = 0
	# while True:
	# 	c = 1-c
	# 	if len(is_active) == 0: # empty list means exit, for our purposes
	# 		GPIO.output(LED,GPIO.LOW) # Turn off LED
	# 		break # jump out of this infinite while loop and exit this thread
	# 	if is_active[0]:
	# 		if c:
	# 			GPIO.output(LED,GPIO.HIGH) # Turn on LED
	# 		else:
	# 			GPIO.output(LED,GPIO.LOW) # Turn off LED
	# 	time.sleep(FLASH_DELAY)


print ' [*] Waiting for messages. To exit press CTRL+C'
def callback(ch, method, properties, body):    
	print " [x] Received %r" % (body,)
channel.basic_consume(callback, queue='bottle_queue',no_ack=True)
channel.start_consuming()

# Advertise using ZeroConf
		# Build JSON message
		# epoch_seconds = time.mktime(time.localtime())
		# pebble = {'Action':'push','Author':'tom swift','Age':'21','MsgID':'Team08_'+str(epoch_seconds),'Subject':'weather','Message':'It is foggy at the moment'}
		# print type(pebble)
		# print pebble
		# pebble_json = json.dumps(pebble)
initializing count variable to display count of messages on LEDS
count = 0
# Message from rabbitMQ = incoming_pebble
body = parsed_incoming_pebble # trying to make the body the json pebble im expecting to receive
parsed_incoming_pebble = json.loads(incoming_pebble)
if parsed_incoming_pebble['Action'] == 'push':
# For Push
#	Store in Shelve, sends reply that it pushed pebble
#	When store is executed then update count
# Update LEDs
count++
binary_led(count)
elif parsed_incoming_pebble['Action'] == 'pullr':
# For Pullr
#	Copy message from Shelve send it to pebble pi.
#	When store is executed then update count
# Update LEDs
count = count
binary_led(count)
elif parsed_incoming_pebble['Action'] == 'pull':
# For Pull
#	Remove message from Shelve send it to pebble pi.
#	When store is executed then update count
# Update LEDs
count--
binary_led(count)
else
#Throw error because we didnt receive a correct action

