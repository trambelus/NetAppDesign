#!/usr/bin/env python
# Created by: Chris Cox
# Project 1
# ECE 4564
# Credit goes to: SHAWNHYMEL
import socket
import time
from threading import Thread
import RPi.GPIO as GPIO

# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
LED = 12

TCP_IP = '172.30.144.131'
# TCP_IP = '192.168.0.12'
# TCP_IP = '0.0.0.0'
TCP_PORT = 45678
BUFFER_SIZE = 2  # Normally 1024, but we want fast response

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
			break # jump out of this infinite while loop and exit this thread
		if is_active[0]:
			if c:
				GPIO.output(LED,GPIO.HIGH) # Turn on LED
			else:
				GPIO.output(LED,GPIO.LOW) # Turn off LED
			print("Flash!") # so you can see what's going on here in this example

		time.sleep(FLASH_DELAY)

try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        while 1:
            is_active = [False] # It's a list because it'll get passed to the thread by reference this way, not by value.
            # If we just passed False as an argument, changing the local variable here wouldn't change the thread's variable.
            # There are many ways to implement this, but I like this list-singleton method. It's simple.
            Thread(target=flash, args=(is_active,)).start() # start the thread
	    # Setup GPIO as output
	    GPIO.setmode(GPIO.BOARD)
	    GPIO.setup(LED, GPIO.OUT)
            conn, addr = s.accept()
            print 'Connection address:', addr
            recv_data = conn.recv(BUFFER_SIZE)
            print "received data: ", recv_data
            if recv_data == '0': # If receive 0 turn LED OFF
                print "INSIDE '0' of IF"
                is_active[0] = Falsh # Turns the flashing off
                GPIO.output(LED,GPIO.LOW)
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            elif recv_data == '1': # If receive 1 turn LED ON
                print "INSIDE '1' of ELIF"
                is_active[0] = Falsh # Turns the flashing off
                GPIO.output(LED,GPIO.HIGH)
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            elif recv_data == '2':           # This is just for now, will need to incorporate thread here; If receive 2 blink LED
                # blinkLED()
                print "INSIDE '2' of ELIF"
                is_active[0] = True # Turns the flashing on
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            # else :
                # print "INSIDE ELSE"
                # GPIO.output(LED,GPIO.HIGH)
                # time.sleep(0.5)
                # GPIO.output(LED,GPIO.LOW)
                # time.sleep(0.5)
                # GPIO.output(LED,GPIO.HIGH)
                # send_data = '1'
                # conn.send(str(send_data))  # Send ACK to RPI1
except KeyboardInterrupt:
        is_active[0] = Falsh # Turns the flashing off
        GPIO.cleanup()
        conn.close() # Close socket connection
