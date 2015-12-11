#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template, url_for
from pprint import pprint
import hashlib
import sqlite3

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

def init_db():
	db = sqlite3.connect('main.db3')
	db.execute("""CREATE TABLE IF NOT EXISTS rooms (
		id INTEGER UNIQUE NOT NULL PRIMARY KEY,
		fullname TEXT NOT NULL,
		fullness TEXT NOT NULL,
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
		db = init_db()
		f = request.files['file']
		f.save('static/latest.png')
		query = "REPLACE INTO rooms (id, fullname, fullness, imgpath, lastupdated) VALUES (?,?,?,?,?)"
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
		return render_template('results.html', room=request.form['room'])

	return render_template('index.html')

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
