#!/usr/bin/env python

import requests
import time
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('id', required=True, help='ID of Pi to search for')
	args = parser.parse_args()
	pi_id = args.id
	while True:
		try:
			resp = response.get('http://jenna.xen.prgmr.com/pull?id=%s' % pi_id)
			if resp.text != '':
				log("Found IP: %s" % resp.text)
				os.system('putty -ssh %s' % resp.text)
			time.sleep(1)
		except Exception as ex:
			log(ex)

if __name__ == '__main__':
	main()
