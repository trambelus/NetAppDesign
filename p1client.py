#!/usr/bin/env python3.4
# Client for Project 1, ECE 4564
# Author: John McDouall

import socket
import tweepy
import sys
import re
import time

USERNAME = 'Trambelus'
OAUTHFILE = 'oauth.txt'
STARTEDFILE = 'started.txt'
WATCHING = 'VTNetApps'
PORT = 45678

VALID_PAT = re.compile(r"#ECE4564_\d{1,3}_\d{1,3}_\d{1,3}_\d{1,3}_\d{1,5}_LED(OFF|ON|FLASH)")
IP_PAT = re.compile(r"_\d{1,3}_\d{1,3}_\d{1,3}_\d{1,3}_\d{1,5}")

LOGFILE = 'p1client.log'

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')


def get_credentials():
	"""
	Get key, secret, token, and token secret from external file
	"""
	# (Not gonna hardwire them here)
	with open(OAUTHFILE,'r') as f:
		stuff = f.readlines()
		ret = [i.rstrip() for i in next(x[1:] for x in [t.split('\t') for t in stuff] if x[0] == USERNAME)]
		return ret

def process(command):
	"""
	Given a command in hashtag format (string), send the appropriate command
	to remote Pi and generate confirmation message.
	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ip_port = re.search(IP_PAT, command).group(0)
	ip = ip_port[:ip_port.rfind("_")].replace('_','.')[1:]
	port = int(ip_port[ip_port.rfind("_")+1:])
	led_on = 0
	if 'FLASH' in command:
		led_on = 2
	elif 'ON' in command:
		led_on = 1
	log("Attempting connection to %s on port %d" % (ip, port))
	sock.connect((ip, port))
	log("Connection successful")
	sock.send(bytes(chr(led_on), 'UTF-8'))
	resp = int.from_bytes(sock.recv(1), byteorder='little')
	log("Remote Pi responded with code %d" %  resp)
	return "ACK %s" % (command)

def monitor():
	"""
	Initializes tweepy; loops through and parses username mentions; calls process(); posts responses
	"""
	# Initialize
	cred = get_credentials()
	auth = tweepy.OAuthHandler(cred[0], cred[1])
	auth.set_access_token(cred[2], cred[3])
	api = tweepy.API(auth)
	log("Initialization successful")
	# Monitor
	with open(STARTEDFILE, 'r') as f:
		started = [int(s.strip()) for s in f.readlines()]

	while True:
		try:
		mentions = api.mentions_timeline(count=1)
			for mention in mentions:
				if mention.id in started:
					time.sleep(5)
					continue
				started.append(mention.id)
				with open(STARTEDFILE, 'a') as f:
					f.write('\n'+str(mention.id))
				log("%s: %s" % (mention.text, mention.user.screen_name))
				commands = re.search(VALID_PAT, mention.text)
				if commands:
					response = process(commands.group(0))
					status = "@%s %s" % (mention.user.screen_name, response)
					log("Posting status %s (len=%d)" % (status, len(status)))
					# This update_status call doesn't work 100% of the time.
					# Sometimes there are 403 or 429 responses.
					# Tweepy isn't the most robust library; nothing to be done for it.
					try:
						api.update_status(status=status)
					except tweepy.error.TweepError as ex:
						log("Tweepy error: %s" % str(ex))
		except tweepy.error.TweepError as ex:
			# Too many requests, probably
			sleep(30)

def main():
	if len(sys.argv) == 1:
		monitor()

if __name__ == '__main__':
	main()