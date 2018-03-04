from flask import Flask, render_template, request, json, Blueprint
from flask_oauth import OAuth
import requests
from requests_oauthlib import OAuth1
import ConfigParser
import peopleSearch

app = Flask(__name__,template_folder="templates/",static_url_path='/static')

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/results',methods=['GET','POST'] )
def loading():
	print(request.form['first name'])
	print(request.form['last name'])
	print(request.form['location'])
	info = searchPerson(request.form['first name'],request.form['last name'],request.form['location'])
	return render_template('results.html',info=info)

@app.route('/results',methods=['GET'])
def results():
	#return render_template('results.html',form=form)
	return render_template('results.html')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000)
