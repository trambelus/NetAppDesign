#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for
from pprint import pprint
import hashlib
import sqlite3
import time
import shelve

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

status = ''
lastupdated = ''
# status, lastupdated

@app.route('/')
def main():
	return "<img src='%s'></img>" % url_for('static',filename='main.png')

@app.route('/rooms/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		id = '00000'

		if 'file' in request.files:
			recv_file = request.files['file']
			filename = 'latest.png'
			recv_file.save('static/%s' % filename)
			print("\tAuth: %s" % request.headers['Auth'])

		if 'status' in request.form:
			global status
			status = request.form['status']

		global lastupdated
		lastupdated = time.strftime('%Y-%m-%d %H:%M:%S UTC')

		return ''

	return '<h1>ಠ_ಠ</h1>'

@app.route('/rooms', methods=['GET','POST'])
def rooms():
	if request.method == 'POST':
		with open('hash.txt','r') as f:
			hash_s = f.readlines()[0]
		hash_f = hashlib.new('sha256')
		hash_f.update(bytes(request.form['password'],'UTF-8'))
		if hash_f.hexdigest() != hash_s:
			return render_template('index.html',error='Invalid password')

		flash('Authentication successful')
		print('\t\tstatus="%s", lastupdated="%s"' % (status,lastupdated))
		return render_template('results.html', status=status, lastupdated=lastupdated)

	return render_template('index.html')

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
