from flask import Flask, request, jsonify, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response
import os
import time
import peopleSearch

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/addCode/<code>')
def index(code):
	return render_template("index.html")

def extractLastName(code):
	# /add/%40%0A%1EANSI+636005050001DL003100272DCAD%0ADCBU%0ADCD%0ADBA06102020%0ADCSLAMBERT%0ADACCHRISTOPHER%0ADADROBERT%0ADBD04092015%0ADBB06101999%0ADBC1%0ADAU075+in%0ADAG17+ENGEL+DR%0ADAIGREENVILLE%0ADAJSC%0ADAK296177209%0ADAQ103659059%0ADCF1036590590409201510%0ADCGUSA%0ADDEU%0ADDFU%0ADDGU%0ADCU%0ADAW240%0ADCRU+-+Conditional+%2FProvisional++++++++++++++++++++++%C2%85%C2%85/glutenFree
	return code.split("DCS")[1].partition("%")[0].title()

def extractZipCode(code):
	return code.split("DAK")[1][:5]

def extractFirstName(code):
	return code.split("DAC")[1].partition("%")[0].title()

def convertCode(code):
	pass

@app.route('/searchUser/<firstName>/<lastName>/<zipCode>', methods=["POST", "GET"])
def searchUser(firstName, lastName, zipCode):
	return jsonify(peopleSearch.searchPerson(firstName, lastName, zipCode))


if __name__ == "__main__":
	app.run()
