#!/usr/bin/env python
from twilio.rest import TwilioRestClient
import pygame

client = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')

def sendMessage():
	client.messages.create(to='+15407974693', from_='+15406135061', body="Playing Hello Mister Gopher", media_url="http://www.bassmaster.com/sites/default/files/imagecache/slideshow_image/06DeanRojas_Record.jpg")
	print('Just ran sendMessage', client)
	client.messages.create(to='+15407974693', from_='+15406135061', body="Playing Hello Mister Gopher", media_url="http://www.wavsource.com/snds_2015-11-01_1874590815319647/tv/a-team/a-team_intro.wav")
	print('Just ran sendMessage for wav file', client)
	pygame.mixer.init()
	pygame.mixer.music.load("hello_mister_gopher.wav")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy() == True:
	    continue


def main():
	sendMessage()

if __name__ == '__main__':
	main()
