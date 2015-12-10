#!/usr/bin/env python3
from PIL import Image, ImageFilter, ImageChops
from imgurpython import ImgurClient
import picamera
import math, operator
import time
import socket
import requests

TCP_IP = requests.get('http://jenna.xen.prgmr.com:5281/pissh/pull?id=camera_pi')
TCP_PORT = 45679
camera = picamera.PiCamera()

def main():
	try:
		print('Inside of main')
		ip = TCP_IP.text # converting ip to text

		if ip == '': # making sure the ip isnt blank
			print('IP is blank')
			return
		else:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print('Binding socket')
			s.bind((ip, TCP_PORT))
			print('Listening')
			s.listen(1)
			#testing
			#put all in a while loop, always wait for a signal to take another photo and process again
			while (1):
				print('Infinite while')
				(conn, addr) = s.accept()
				recv_data = ord(conn.recv(1))
				print recv_data
				if (recv_data == 0):
					print "Received Signal"
					camera.capture('dump.jpg')
					time.sleep(3)
					camera.capture('orig.jpg') #"empty room"
					time.sleep(3)
					camera.capture('update.jpg') #capture new image whenever there is a change

					img1 = Image.open('orig.jpg')
					img2 = Image.open('update.jpg')

					print "Captured Images"

					toSend = img2.resize((400, 400), Image.ANTIALIAS)
					toSend.save('latest.png')
					files = {'file': ('latest.png', open('latest.png','rb'), {'Expires': '0', 'Auth':'8spWsLd38ji08Tpc'})}
					rsp = requests.post('http://trambel.us/rooms/upload', files=files)

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
					conn.close()
	except KeyboardInterrupt:
		s.close() # Close socket connection

if __name__ == '__main__':
	main()