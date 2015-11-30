#!/usr/bin/env python3

from flask import Flask, request
from pprint import pprint

app = Flask(__name__)

fob_html = """<meta name="viewport" content="width=device-width, initial-scale=1">
<img src=http://i.imgur.com/lm1WSXT.png style='max-width:100%;max-height:100%'>
"""

@app.route('/') # Just as a quick test
def fallout_boy():
	return fob_html

def main():
	app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
	main()
