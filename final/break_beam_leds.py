#!/usr/bin/env python3
# Created by: Chris Cox
# Final Project
# ECE 4564
# Credit goes to: 
# Description: Created a program that uses break beam LEDs to detect movement.
# It then relays the detection to the camera pi to take a snap shot.
import socket
import time
import RPi.GPIO as GPIO
import sys
import requests

# GPIO pin number of LED according to spec; GPIO pin 17 Phys Pin 11
LED = 11

# TCP_IP = '192.168.0.12'
# TCP_IP = '0.0.0.0'
TCP_PORT = 45675
BUFFER_SIZE = 1
pi_id = 'camera_pi'
led_on = 1
led_off = 0

# Setup GPIO as input
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED, GPIO.IN)

def main():
	print("Starting infinite while loop")
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		resp = requests.get('http://jenna.xen.prgmr.com:5281/pissh/pull?id=%s' % pi_id)
		ip = resp.text
		if ip == '':
			return
		else:
			print(ip)
			s.connect((ip, TCP_PORT))
			while True:
				# not sure where to place this yet
				# conn, addr = s.accept()
				break_beam = GPIO.input(LED)
				if break_beam == 1:
					print('LED beam is connected')
					time.sleep(1)
					print(led_on)
					#s.send(bytes(chr(led_on), 'UTF-8'))  # Send ACK to Camera Pi
				else:
					print('LED beam is broken')
					print(led_off)
					time.sleep(10) # was 60
					s.send(bytes(chr(led_off), 'UTF-8'))  # Send ACK to Camera Pi
					resp = int.from_bytes(s.recv(1), byteorder='little')
					print("Remote Pi responded with code %d" %  resp)
	except KeyboardInterrupt:
			GPIO.cleanup()
			s.close() # Close socket connection

if __name__ == '__main__':
	main()
