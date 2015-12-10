#!/usr/bin/env python3

from flask import Flask, request, flash, redirect, url_for, render_template
from pprint import pprint
import hashlib

app = Flask(__name__)

@app.route('/rooms')
def rooms():
	pprint(request)
	with open('index.html') as f:
		index_html = '\n'.join(f.readlines())
	return index_html

@app.route('/rooms/upload', methods=['GET','POST'])
def upload():
	pprint(request)
	if request.method == 'POST':
		f = request.files['latest.png']
		f.save('/img/latest.png')

@app.route('/rooms/validate', methods=['GET','POST'])
def validate():
	if request.method == 'POST':
		with open('hash.txt','r') as f:
			hash_s = f.readlines()[0]
		hash_f = hashlib.new('sha256')
		hash_f.update(bytes(request.form['password'],'UTF-8'))
		if hash_f.hexdigest() != hash_s:
			return render_template('index.html',error='Invalid password')

		flash('Authentication successful')
		return redirect(url_for('/rooms/display'))
	return render_template('index.html',error='Invalid password')

@app.route('/rooms/display', methods=['GET'])
def display():
	pprint(request)
	with open('results.html') as f:
		results_html = '\n'.join(f.readlines())
	return results_html

def main():
	app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
	main()
