import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
from flask import Flask, request, jsonify, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response
import os
import urllib
import time
import peopleSearch
import logging
import threading
from time import strftime
import traceback

app = Flask(__name__)

app = Flask(__name__,template_folder="templates/",static_url_path='/static')

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/results',methods=['GET','POST'] )
def loading():
	return redirect(url_for('searchUser', firstName=request.form['first name'], lastName=request.form['last name'], zipCode=request.form['location']))
	#return render_template('results.html', info=info)


@app.errorhandler(404)
def page_not_found(e):
	print(request)
	ts = strftime('[%Y-%b-%d %H:%M]')
	tb = traceback.format_exc()
	print(urllib.quote_plus(str(request.full_path)))
	code = str(urllib.quote_plus(str(request.full_path))).partition("+-+")[0].replace("\n", "")[:-3]
	print extractZipCode(code)
	return redirect(url_for('searchUser', firstName=extractFirstName(code), lastName=extractLastName(code), zipCode=extractZipCode(code)))
	#return tb +  + str(request.full_path)

def extractLastName(code):
	# /add/%40%0A%1EANSI+636005050001DL003100272DCAD%0ADCBU%0ADCD%0ADBA06102020%0ADCSLAMBERT%0ADACCHRISTOPHER%0ADADROBERT%0ADBD04092015%0ADBB06101999%0ADBC1%0ADAU075+in%0ADAG17+ENGEL+DR%0ADAIGREENVILLE%0ADAJSC%0ADAK296177209%0ADAQ103659059%0ADCF1036590590409201510%0ADCGUSA%0ADDEU%0ADDFU%0ADDGU%0ADCU%0ADAW240%0ADCRU+-+Conditional+%2FProvisional++++++++++++++++++++++%C2%85%C2%85/glutenFree
	return code.split("DCS")[1].partition("%")[0].title().partition("\n")[0]

def extractZipCode(code):
	return code.split("DAK")[1][:5]

def extractFirstName(code):
	return code.split("DAC")[1].partition("%")[0].title().partition("\n")[0]

def convertCode(code):
	return {"ZipCode": extractZipCode(code), "FirstName": extractFirstName(code), "LastName": extractLastName(code)}

@app.route('/searchUser/<firstName>/<lastName>/<zipCode>', methods=["POST", "GET"])
def searchUser(firstName, lastName, zipCode):
	return render_template('results.html', info=peopleSearch.searchPerson(firstName, lastName, zipCode))


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000)
