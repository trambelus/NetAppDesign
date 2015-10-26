#!/usr/bin/env python
# pebble.py
# Author: John McDouall
# ECE 4564

import sys

class Pebble(object):
	"""Sends messages, receives replies"""
	def __init__(self, arg):
		super(Pebble, self).__init__()
		self.arg = arg
		
def main():
	pebble = Pebble()

if __name__ == '__main__':
	main()