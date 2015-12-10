#!/usr/bin/env python3

from flask import Flask, request, flash, redirect,  render_template
from pprint import pprint
import hashlib

app = Flask(__name__)
app.secret_key = 'vOaZrSbR8ZIpCAeU'

@app.route('/rooms/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		f = request.files['latest.png']
		f.save('/img/latest.png')

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
		return redirect('/rooms/display')

	return render_template('index.html')

@app.route('/rooms/display', methods=['GET'])
def display():
	return render_template('results.html',text='SEB')

def main():
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
