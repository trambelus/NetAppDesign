import socket
import tweepy
import sys
import re
import time

USERNAME = 'Trambelus'
OAUTHFILE = 'oauth.txt'
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

# Get key, secret, token, and token secret from external file
# (Not gonna hardwire them here)
def get_credentials():
	with open(OAUTHFILE,'r') as f:
		stuff = f.readlines()
		ret = [i.rstrip() for i in next(x[1:] for x in [t.split('\t') for t in stuff] if x[0] == USERNAME)]
		return ret

def process(command):
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
	sock.send(bytes(led_on))
	resp = sock.recv(1)
	if resp != 0:
		log("Remote Pi returned error code %d" % resp)
	return

def main():
	# Initialize
	cred = get_credentials()
	auth = tweepy.OAuthHandler(cred[0], cred[1])
	auth.set_access_token(cred[2], cred[3])
	api = tweepy.API(auth)
	# Monitor
	while True:
		mentions = api.mentions_timeline(count=1)
		for mention in mentions:
			log("%s: %s" % (mention.text, mention.user.screen_name))
			commands = re.search(VALID_PAT, mention.text)
			if commands:
				process(commands.group(0))

if __name__ == '__main__':
	#process("#172.30.42.72_LED03_ON")
	main()