#!/usr/bin/env python3
from PIL import Image, ImageFilter, ImageChops
from imgurpython import ImgurClient
import picamera
import math, operator
import time
import socket
import requests

TCP_IP = requests.get('http://jenna.xen.prgmr.com:5281/pissh/pull?id=camera_pi')
TCP_PORT = 45678
camera = picamera.PiCamera()
#testing
#put all in a while loop, always wait for a signal to take another photo and process again
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
while (1):
	(conn, addr) = s.accept()
	recv_data = ord(conn.recv(1))
	if (recv_data == 0):
		camera.capture('dump.jpg')
		time.sleep(3)
		camera.capture('orig.jpg') #"empty room"
		time.sleep(3)
		camera.capture('update.jpg') #capture new image whenever there is a change

		img1 = Image.open('orig.jpg')
		img2 = Image.open('update.jpg')
		toSend = img2.resize((400, 400), Image.ANTIALIAS)

		img1 = img1.filter(ImageFilter.FIND_EDGES)
		img1.save('orig.jpg')
		img2 = img2.filter(ImageFilter.FIND_EDGES)
		img2.save('update.jpg')

		diff = ImageChops.subtract(img2, img1)
		diff.save('diff.jpg')

		diff = Image.open("diff.jpg").convert('1')
		black, white = diff.getcolors()

		print black[0] #number of black pixels
		print white[0] #number of white pixels

		if (white[0] < 3500):
			print "relatively empty"
		elif (white[0] <5000):
			print "kind of full"
		else:
			print "full"
