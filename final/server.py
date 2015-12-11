#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for, abort
from pprint import pprint
import hashlib
import sqlite3
import time
import shelve

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

status = ''
lastupdated = ''
lu = ''
# status, lastupdated

@app.route('/')
def main():
	return "<img src='%s'></img>" % url_for('static',filename='main.png')

@app.route('/rooms/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		id = '00000'

		if 'file' in request.files:
			try:
				if request.headers['Auth'] == '8spWsLd38ji08Tpc':
					recv_file = request.files['file']
					filename = 'latest.png'
					recv_file.save('static/%s' % filename)
				else:
					abort(401)
			except KeyError:
				#return "Auth header field required"
				abort(401)

		if 'status' in request.form:
			global status
			status = request.form['status']

		if 'file' not in request.files and 'status' not in request.form:
			abort(400)

		global lastupdated
		global lu
		lastupdated = time.strftime('%Y-%m-%d %H:%M:%S UTC')
		lu = time.strftime('%Y%m%d%H%M%S')
		return ''

	return '<h1>ಠ_ಠ</h1>'

@app.route('/favicon.ico')
def favicon():
	return url_for('static',filename='favicon.ico')

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
		return render_template('results.html', status=status, lastupdated=lastupdated, filename='latest.png', ct=lu)

	return render_template('index.html')

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
