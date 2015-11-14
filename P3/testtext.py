#!/usr/bin/env python
from twilio.rest import TwilioRestClient

client = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')

def sendMessage():
	client.messages.create(to='+15407974693', from_='+15406135061', body="test test message")
	print('Just ran sendMessage', client)


def main():
	sendMessage()

if __name__ == '__main__':
	main()
