#!/usr/bin/env python
from twilio.rest import TwilioRestClient
import pygame

client = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')

def sendMessage():
	client.messages.create(to='+15407974693', from_='+15406135061', body="Playing Hello Mister Gopher")
	print('Just ran sendMessage', client)
	pygame.mixer.init()
	pygame.mixer.music.load("hello_mister_gopher.wav")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy() == True:
	    continue


def main():
	sendMessage()

if __name__ == '__main__':
	main()
