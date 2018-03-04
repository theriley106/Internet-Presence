from flask import Flask, request, jsonify, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response
import os
import time
import peopleSearch

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/searchUser/<firstName>/<lastName>/<zipCode>', methods=["POST", "GET"])
def searchUser(firstName, lastName, zipCode):
	return jsonify(peopleSearch.searchPerson(firstName, lastName, zipCode))


if __name__ == "__main__":
	app.run()
