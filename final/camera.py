#!/usr/bin/env python
from PIL import Image, ImageFilter, ImageChops
from imgurpython import ImgurClient
import picamera
import math, operator
import time
import socket
import requests

TCP_IP = requests.get('http://jenna.xen.prgmr.com:5281/pissh/pull?id=camera_pi')
TCP_PORT = 45674
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
			s.bind((ip, TCP_PORT))
			s.listen(1)
			(conn, addr) = s.accept()
			#testing
			#put all in a while loop, always wait for a signal to take another photo and process again
			while (1):
				recv_data = 5
				print('Infinite while')
				recv_data = ord(conn.recv(1))
				print (recv_data)
				if (recv_data == 0):
					print ("Received Signal")
					camera.capture('dump.jpg')
					time.sleep(3)
					camera.capture('orig.jpg') 
					time.sleep(3)
					camera.capture('update.jpg') #capture new image whenever there is a change

					img1 = Image.open('orig.jpg')
					img2 = Image.open('update.jpg')

					print ("Captured Images")

					toSend = img2.resize((400, 400), Image.ANTIALIAS)
					toSend.save('latest.png')

					img1 = img1.filter(ImageFilter.FIND_EDGES)
					img1.save('orig.jpg')
					img2 = img2.filter(ImageFilter.FIND_EDGES)
					img2.save('update.jpg')

					diff = ImageChops.subtract(img2, img1)
					diff.save('diff.jpg')

					diff = Image.open("diff.jpg").convert('1')
					black, white = diff.getcolors()

					print (black[0]) #number of black pixels)
					print (white[0]) #number of white pixels)
					status = ""
					if (white[0] < 3000):
						status = "relatively empty"
					elif (white[0] <5000):
						status = "kind of full"
					else:
						status = "full"
					print status

					files = {'file': open('latest.png','rb')}
					headers = {'Auth':'8spWsLd38ji08Tpc'}
					myData = {'status': status}
					rsp = requests.post('http://trambel.us/rooms/upload', files=files, data=myData, headers=headers)


					conn.send(chr(0))
					print("sent data back")
	except KeyboardInterrupt:
		s.close() # Close socket connection

if __name__ == '__main__':
	main()