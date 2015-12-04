#!/usr/bin/env python3
# Created by: Chris Cox
# Final Project
# ECE 4564
# Credit goes to: 
# Description: Created a program that uses break beam LEDs to detect movement.
# It then relays the detection to the camera pi to take a snap shot.
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
GPIO.setup(LED, GPIO.IN)

def main():
	print("Starting infinite while loop")
	try:
		while True:
			break_beam = GPIO.input(LED)
			if break_beam is True:
				print('LED beam is connected')
				time.sleep(1)
			else:
				print('LED beam is broken')
				time.sleep(1)
	except KeyboardInterrupt:
			GPIO.cleanup()
			conn.close() # Close socket connection

if __name__ == '__main__':
	main()