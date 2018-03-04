import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
import requests
import bs4
import re
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pickle
from selenium.webdriver.common.action_chains import ActionChains
import time
import zipcode

URL = "https://www.truepeoplesearch.com/results?name={0}%20{1}&citystatezip={2}&rid=0x0"
# 0 = First Name | 1 = Last Name | 2 = ZIP
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def grabSite(url):
	return requests.get(url, headers=headers)

def extractValues(contentValuePage):
	fullName = contentValuePage.select(".h2")[0].getText().strip()
	age = contentValuePage.select(".pl-md-2 .content-value")[0].getText().strip()
	phoneNumbers = re.findall("phoneno=(\d+)", str(contentValuePage))
	similarNames = []
	previousAddress = []
	relatives = []
	associated = []
	for var in re.findall('data-link-to-more="aka"\shref="/results(.+)', str(contentValuePage)):
		similarNames.append(re.findall("\>(.*?)\<", var)[0])
	for var in contentValuePage.select(".content-value"):
		if 'data-link-to-more="address"' in str(var):
			previousAddress.append(var.getText().strip())
	for var in re.findall('data-link-to-more="relative"\shref="/results(.+)', str(contentValuePage)):
		relatives.append(re.findall("\>(.*?)\<", var)[0])
	for var in re.findall('data-link-to-more="associate"\shref="/results(.+)', str(contentValuePage)):
		associated.append(re.findall("\>(.*?)\<", var)[0])
	return {"Relatives": relatives, "Associated": associated, "Full_Name": fullName, "Age": age, "Phone_Numbers": phoneNumbers, "Similar_Names": similarNames, "Addresses": previousAddress}


def findPerson(firstName, lastName, zipCode):
	totalVals = []
	url = URL.format(firstName.title(), lastName.title(), zipCode)
	print url
	r = grabSite(url)
	page = bs4.BeautifulSoup(r.text, 'lxml')
	print extractValues(page)


def createHeadlessBrowser(proxy=None, XResolution=1024, YResolution=768):
	#proxy = None
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = (
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36')
	if proxy != None:
		service_args = ['--proxy={}'.format(proxy),'--proxy-type=https','--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false',]
		driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)
	else:
		driver = webdriver.PhantomJS(desired_capabilities=dcap)
	driver.set_window_size(XResolution,YResolution)
	driver.set_page_load_timeout(8)
	return driver

def searchFacebook(searchQuery):
	profileURLs = []
	mainURL = ""
	driver = createHeadlessBrowser()
	cookies = pickle.load(open("../cookies.pkl", "rb"))
	try:
		driver.get("https://m.facebook.com/")
	except Exception:
		actions = ActionChains(driver)
		actions.send_keys(Keys.CONTROL +'Escape').perform()

	for cookie in cookies:
		driver.add_cookie(cookie)
	try:
		driver.get("https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format(searchQuery.replace(" ", "%20")))
	except:
		actions = ActionChains(driver)
		actions.send_keys(Keys.CONTROL +'Escape').perform()
	#driver.find_element_by_css_selector("div.cd").click()
	a = str(driver.page_source)
	mainURL = "https://m.facebook.com/profile.php?id=" + re.findall("profile.php\?id=(\d+)", a)[0]
	for var in list(set(re.findall("profile.php\?id=(\d+)", a))):
		url = "https://m.facebook.com/profile.php?id=" + str(var)
		profileURLs.append(url)
	driver.save_screenshot('static.png')
	return {"Profile_Address": mainURL, "Possible_Profiles": profileURLs}

def getLinkedInProfile(searchQuery):
	info = []
	profileURLs = []
	mainURL = ""
	driver = createHeadlessBrowser()
	driver.get("https://www.linkedin.com/")
	cookies = pickle.load(open("../licookies.pkl", "rb"))
	try:
		driver.get("https://www.linkedin.com/feed/")
	except Exception:
		actions = ActionChains(driver)
		actions.send_keys(Keys.CONTROL +'Escape').perform()
	for cookie in cookies:
		if cookie['domain'][0] != '.':
			cookie['domain'] = '.' + cookie['domain']
		driver.add_cookie(cookie)
	try:
		driver.get("https://www.linkedin.com/search/results/index/?keywords={}&origin=TYPEAHEAD_ESCAPE_HATCH".format(searchQuery.replace(" ", "%20")))
		time.sleep(5)
	except:
		actions = ActionChains(driver)
		actions.send_keys(Keys.CONTROL +'Escape').perform()
	driver.save_screenshot('static.png')
	page = bs4.BeautifulSoup(driver.page_source, 'lxml')
	subLine = [f.getText().strip() for f in page.select(".subline-level-1")]
	subLine2 = [f.getText().strip() for f in page.select(".subline-level-2")]
	profileName = [f.getText().strip() for f in page.select(".actor-name")]
	for i in range(len(subLine)):
		e = {}
		try:
			e['Profile'] = profileName[i]
		except:
			e['Profile'] = ""
		try:
			e['Subheader'] = subLine[i]
		except:
			e["Subheader"] = ""
		try:
			e['Location'] = subLine2[i]
		except:
			e['Location'] = ""
		e['Rank'] = i
		info.append(e)
	return info

def convertState(abbrState):
	states = {
	        'AK': 'Alaska',
	        'AL': 'Alabama',
	        'AR': 'Arkansas',
	        'AS': 'American Samoa',
	        'AZ': 'Arizona',
	        'CA': 'California',
	        'CO': 'Colorado',
	        'CT': 'Connecticut',
	        'DC': 'District of Columbia',
	        'DE': 'Delaware',
	        'FL': 'Florida',
	        'GA': 'Georgia',
	        'GU': 'Guam',
	        'HI': 'Hawaii',
	        'IA': 'Iowa',
	        'ID': 'Idaho',
	        'IL': 'Illinois',
	        'IN': 'Indiana',
	        'KS': 'Kansas',
	        'KY': 'Kentucky',
	        'LA': 'Louisiana',
	        'MA': 'Massachusetts',
	        'MD': 'Maryland',
	        'ME': 'Maine',
	        'MI': 'Michigan',
	        'MN': 'Minnesota',
	        'MO': 'Missouri',
	        'MP': 'Northern Mariana Islands',
	        'MS': 'Mississippi',
	        'MT': 'Montana',
	        'NA': 'National',
	        'NC': 'North Carolina',
	        'ND': 'North Dakota',
	        'NE': 'Nebraska',
	        'NH': 'New Hampshire',
	        'NJ': 'New Jersey',
	        'NM': 'New Mexico',
	        'NV': 'Nevada',
	        'NY': 'New York',
	        'OH': 'Ohio',
	        'OK': 'Oklahoma',
	        'OR': 'Oregon',
	        'PA': 'Pennsylvania',
	        'PR': 'Puerto Rico',
	        'RI': 'Rhode Island',
	        'SC': 'South Carolina',
	        'SD': 'South Dakota',
	        'TN': 'Tennessee',
	        'TX': 'Texas',
	        'UT': 'Utah',
	        'VA': 'Virginia',
	        'VI': 'Virgin Islands',
	        'VT': 'Vermont',
	        'WA': 'Washington',
	        'WI': 'Wisconsin',
	        'WV': 'West Virginia',
	        'WY': 'Wyoming'
	}
	return states[abbrState]

class getInfo(object):
	def __init__(self, firstName, lastName, zipCode):
		self.firstName = firstName
		self.lastName = lastName
		self.zipCode = zipCode
		self.relatives = []
		self.associates = []
		self.occupation = []
		self.address = []
		self.previousAddress = []
		self.age = []
		self.generalArea = []
		myzip = zipcode.isequal(zipCode)
		self.fbProfile = ""
		self.similarFBProfile = []
		self.state = myzip.state
		self.city = str(myzip.city).title()
		self.fullState = convertState(self.state)


	def searchFB(self):
		searchQuery = "{} {} {}".format(self.firstName, self.lastName, self.city)
		fbInfo = searchFacebook(searchQuery)
		self.fbProfile = fbInfo["Profile_Address"]
		self.similarFBProfile = fbInfo["Possible_Profiles"]

	def searchLI(self):
		liInfo = []
		query1 = "{} {}".format(self.firstName, self.lastName)
		query2 = "{} {} {}".format(self.firstName, self.lastName, self.fullState)
		query3 = "{} {} {}".format(self.firstName, self.lastName, self.city)
		getLinkedInProfile(


if __name__ == '__main__':
	#print(getLinkedInProfile(['chris', 'christopher'], 'lambert', 'greenville', 'south carolina'))
	print(getLinkedInProfile('christopher lambert'))
