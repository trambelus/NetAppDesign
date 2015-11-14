#!/usr/bin/env python3

from flask import Flask, request
import shelve
from pprint import pprint

app = Flask(__name__)
shelf = shelve.open('pissh')

@app.route('/pissh/push')
def update_ip():
	shelf[request.args['id']] = request.args['ip']
	shelf.sync()
	return 'Success'

@app.route('/pissh/pull')
def show_ip():
	requested_id = request.args['id']
	try:
		return shelf[requested_id]
	except KeyError as ex:
		return ''

def main():
	app.run(host='0.0.0.0')

if __name__ == '__main__':
	main()
