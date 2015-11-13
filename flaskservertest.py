#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "<img width=800 height=600 src=https://www.raspberrypi.org/wp-content/uploads/2015/01/Pi2ModB1GB_-comp.jpeg></img>"

if __name__ == '__main__':
	app.run(debug=True)