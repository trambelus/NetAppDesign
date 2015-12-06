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

# GPIO pin number of LED according to spec; GPIO pin 17 Phys Pin 11
LED = 11

# TCP_IP = '192.168.0.12'
# TCP_IP = '0.0.0.0'
TCP_PORT = 45678
BUFFER_SIZE = 1

# Setup GPIO as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED, GPIO.IN)

def main():
	if len(sys.argv) == 1:
		TCP_IP = '172.30.144.131'
	else:
		TCP_IP = sys.argv[1]
	print("Starting infinite while loop")
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((TCP_IP, TCP_PORT))
		s.listen(1)
		while True:
			# not sure where to place this yet
			# conn, addr = s.accept()
			break_beam = GPIO.input(LED)
			if break_beam == 1:
				print('LED beam is connected')
				send_data = 1
				conn.send(chr(send_data))  # Send ACK to Camera Pi
				time.sleep(1)
			else:
				print('LED beam is broken')
				send_data = 0
				conn.send(chr(send_data))  # Send ACK to Camera Pi
				time.sleep(1)
	except KeyboardInterrupt:
			GPIO.cleanup()
			conn.close() # Close socket connection

if __name__ == '__main__':
	main()
