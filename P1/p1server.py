#!/usr/bin/env python
# Created by: Chris Cox
# Project 1
# ECE 4564
# Credit goes to: SHAWNHYMEL URL: https://learn.sparkfun.com/tutorials/raspberry-pi-twitter-monitor
# Credit goes to: Scott Mangold URL:  http://www.thirdeyevis.com/pi-page-2.php
# Description: Created a server on the raspberrypiII that is connected to a breadboard via gpio pins
# when a client connects it can light up a LED on the breadboard based on a tweet it receieved.
import socket
import time
from threading import Thread
import RPi.GPIO as GPIO
import sys

# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
LED = 12

# TCP_IP = '192.168.0.12'
# TCP_IP = '0.0.0.0'
TCP_PORT = 45678
BUFFER_SIZE = 1

# Setup GPIO as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

FLASH_DELAY = 1 # flash delay in seconds

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

def main():
	if len(sys.argv) == 1:
		TCP_IP = '172.30.144.131'
	else:
		TCP_IP = sys.argv[1]
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((TCP_IP, TCP_PORT))
		s.listen(1)

		while 1:
			is_active = [False] # It's a list because it'll get passed to the thread by reference this way, not by value.
			# If we just passed False as an argument, changing the local variable here wouldn't change the thread's variable.
			flashthread = Thread(target=flash, args=(is_active,))
			flashthread.daemon = True
			flashthread.start() # start the thread
			# Setup GPIO as output
			GPIO.setmode(GPIO.BOARD)
			GPIO.setup(LED, GPIO.OUT)
			conn, addr = s.accept()
			print 'Connection address:', addr
			recv_data = ord(conn.recv(BUFFER_SIZE))
			print "received data: ", recv_data
			if recv_data == 0: # If receive 0 turn LED OFF
				print "Received LEDOFF"
				is_active[0] = False # Turns the flashing off
				GPIO.output(LED,GPIO.LOW)
				send_data = 0
				conn.send(chr(send_data))  # Send ACK to RPI1
				GPIO.cleanup()
				conn.close() # Close socket connection
			elif recv_data == 1: # If receive 1 turn LED ON
				print "Received LEDON"
				is_active[0] = False # Turns the flashing off
				GPIO.output(LED,GPIO.HIGH)
				send_data = 0
				conn.send(chr(send_data))  # Send ACK to RPI1
				GPIO.cleanup()
				conn.close() # Close socket connection
			elif recv_data == 2:           # If receive two then
				print "Received LEDFLASH"
				is_active[0] = True # Turns the flashing on
				send_data = 0
				conn.send(chr(send_data))  # Send ACK to RPI1
				GPIO.cleanup()
				conn.close() # Close socket connection
			else:
				# Something unexpected happened
				print("Received unexpected data %d" % recv_data)
				conn.send(chr(1))
				GPIO.cleanup()
				conn.close()

	except KeyboardInterrupt:
			is_active.remove(0) # Turns the flashing off
			GPIO.cleanup()
			conn.close() # Close socket connection

if __name__ == '__main__':
	main()