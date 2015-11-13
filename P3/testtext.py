#!/usr/bin/env python
from twilio.rest import TwilioRestClient

client = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')

def sendMessage():
	client.messages.create(to='+5406135061', from_='+5406135061', body="test test message")


def main():
	sendMessage()

if __name__ == '__main__':
	main()
