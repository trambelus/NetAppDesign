#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for
from pprint import pprint
import hashlib
import sqlite3
import time

places = {'00000':'Design Studio'}

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

def init_db():
	db = sqlite3.connect('main.db3')
	db.execute("""CREATE TABLE IF NOT EXISTS rooms (
		id INTEGER UNIQUE NOT NULL PRIMARY KEY,
		fullname TEXT NOT NULL,
		status TEXT NOT NULL,
		imgpath TEXT NOT NULL,
		lastupdated DATE NOT NULL
	);""")
	return db

@app.route('/')
def main():
	return "<img src='%s'></img>" % url_for('static',filename='main.png')

@app.route('/rooms/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		id = '00000'
		db = init_db()

		if 'file' in request.files:
			print('Updating file')
			recv_file = request.files['file']
			filename = '%s_%s.png' % (id, time.strftime('%Y%m%d%H%M%S'))
			recv_file.save('static/%s' % filename)
			#query = "REPLACE INTO rooms (id, fullname, status, imgpath, lastupdated) VALUES (?,?,?,?,?)"
			query = "UPDATE rooms SET imgpath='%s' WHERE id='%s'" % (id, filename)
			db.execute(query)

		if 'status' in request.form:
			print('Updating status')
			status = request.form['status']
			query = "UPDATE rooms SET status='%s' WHERE id='%s'" % (id, status)
			db.execute(query)

		lastupdated = time.strftime('%Y-%m-%d %H:%M:%S UTC')
		query = "UPDATE ROOMS SET lastupdated='%s' WHERE id='%s'" % (id, lastupdated)
		db.execute(query)
		db.close()

		return ''

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
		db = init_db()
		id = '00000'
		data = db.execute("SELECT * FROM rooms WHERE id = '%s'" % id).fetchall()
		status = data[2]
		filename = data[3]
		lastupdated = data[4]
		return render_template('results.html', status=status, filename=filename, lastupdated=lastupdated)

	return render_template('index.html')

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
