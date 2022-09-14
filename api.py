#!/usr/bin/env python3
import json
import mysql.connector
#from styles import Styles
from flask import Flask, render_template, jsonify, request, redirect

#mydb = mysql.connector.connect(user='database',
#                          auth_plugin='mysql_native_password',
#                          password='database',
#                          host='localhost',
#                          database='server-status')

#referenced else where
certs = "../certs/"
#s = Styles()

app = Flask(__name__)
#redirect request
@app.before_request
def before_request():
    if not request.is_secure():
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

#app root
@app.route('/')
def root():
	return render_template('index.html')

#api database get
@app.route('/getstatus/', methods= ["GET"])
def getstatus():
	return jsonify("Database Data")
	#database call with protections

#api database set
@app.route('/setstatus/', methods= ["POST"])
def setstatus():
	return jsonify("Updated Database")
	#database call with protections

if __name__ == "__main__":
	print ("[INFO] Starting Glimpse Service")
	app.run(ssl_context=(certs+'cert.pem', certs+'key.pem')) #change this to abs path

