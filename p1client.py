import socket
import tweepy
import sys
import re
import time

USERNAME = 'Trambelus'
OAUTHFILE = 'oauth.txt'
WATCHING = 'VTNetApps'
PORT = 45678

VALID_PAT = re.compile(r"#\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}_LED\d\d_(OFF|ON)")
IP_PAT = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

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
	ip = re.search(IP_PAT, command).group(0)
	led_idx = command.find("LED")
	led = int(command[led_idx+3:led_idx+5])
	led_on = 255 if 'ON' in command else 0
	log("Attempting connection to %s" % ip)
	sock.connect((ip, PORT))
	log("Connection successful")
	sock.send(bytes(led))
	sock.send(bytes(led_on))
	resp = sock.recv(1)
	if resp != 0:
		log("Remote Pi returned error code %d" % resp)
	return

def main():
	# Initialize
	cred = get_credentials()
	auth = tweepy.OAuthHandler(cred['key'], cred['secret'])
	auth.set_access_token(cred['token'], cred['token_secret'])
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
	process("#172.30.42.72_LED03_ON")
	#main()