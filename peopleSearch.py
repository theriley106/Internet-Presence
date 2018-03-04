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
from pyzipcode import ZipCodeDatabase
import threading

URL = "https://www.truepeoplesearch.com/results?name={0}%20{1}&citystatezip={2}&rid=0x0"
# 0 = First Name | 1 = Last Name | 2 = ZIP
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def grabSite(url):
	return requests.get(url, headers=headers)

def convertAddress(address):
	info = {}
	address = str(address).replace("\n\n\nMap", "")
	dates = str(address).partition("\n\n\n(")[2]
	info['Move_In'] = dates.partition(" - ")[0]
	info['Move_Out'] = dates.partition(" - ")[2].replace("(", "")
	address = str(address).partition("\n\n\n(")[0]
	address = str(address).replace("\n", ", ")
	info["Address"] = address
	return info


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
	return extractValues(page)


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

def shortMonthToNum(shortMonth):
	return {
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'Jun' : 6,
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9,
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
	}[shortMonth]

def numToShortMonth(monthNum):
	monthNum -= 1
	return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][monthNum]

def extractShortMonthFromString(string):
	return string.partition(" ")[0]

def extractYearValFromString(string):
	return re.findall("\d+", str(string.partition(" ")[2]))[0]

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
		self.similarNames = []
		self.age = []
		self.generalArea = []
		zcdb = ZipCodeDatabase()
		myzip = zcdb[int(zipCode)]
		self.fbProfile = ""
		self.similarFBProfile = []
		self.state = myzip.state
		self.city = str(myzip.city).title()
		self.fullState = convertState(self.state)
		self.linkedInProfile = None
		self.fullName = ""
		self.listOfPhoneNumbers = []


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
		def addToInfo(query):
			a = 0
			while a == 0:
				try:
					e = getLinkedInProfile(query)
					for var in e:
						liInfo.append(var)
					a = 1
				except Exception as exp:
					print exp
					pass
		threads = [threading.Thread(target=addToInfo, args=(query,)) for query in [query1, query2, query3]]
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()
		for val in liInfo:
			if val["Profile"][:3] == "{} {}".format(self.firstName, self.lastName)[:3] and val["Profile"][-3:] == "{} {}".format(self.firstName, self.lastName)[-3:]:
				self.linkedInProfile = str(val['Profile'])
				self.generalArea = str(val['Location'])
				self.occupation = str(val['Subheader'])
				break
		else:
			for val in liInfo:
				if val['Rank'] == 1 and liInfo.count(str(val['Subheader'])) > 1:
					self.linkedInProfile = str(val['Profile'])
					self.generalArea = str(val['Location'])
					self.occupation = str(val['Subheader'])
					break
			if self.linkedInProfile == None:
				for val in liInfo:
					if liInfo.count(str(val['Subheader'])) > 1:
						self.linkedInProfile = str(val['Profile'])
						self.generalArea = str(val['Location'])
						self.occupation = str(val['Subheader'])
						break
			if self.linkedInProfile == None:
				for val in liInfo:
					if val['Rank'] == 1:
						self.linkedInProfile = str(val['Profile'])
						self.generalArea = str(val['Location'])
						self.occupation = str(val['Subheader'])
						break

	def findGeneralInfo(self):
		# {"Relatives": relatives, "Associated": associated, "Full_Name": fullName, "Age": age, "Phone_Numbers": phoneNumbers, "Similar_Names": similarNames, "Addresses": previousAddress}
		info = findPerson(self.firstName, self.lastName, self.zipCode)
		self.relatives += info["Relatives"]
		self.associates += info["Associated"]
		self.fullName = info['Full_Name']
		self.age = info['Age']
		self.listOfPhoneNumbers += info["Phone_Numbers"]
		self.similarNames += info["Similar_Names"]
		for var in info["Addresses"]:
			self.previousAddress.append(convertAddress(var))
		for i, vals in enumerate(self.previousAddress):
			if len(vals['Move_In']) == 0:
				self.address = vals['Address']
				nextMonth = extractShortMonthFromString(self.previousAddress[i+1]['Move_Out'])
				nextMonth = shortMonthToNum(nextMonth) + 1
				nextMonth = numToShortMonth(nextMonth)
				if nextMonth != 1:
					nextYear = extractYearValFromString(self.previousAddress[i+1]['Move_Out'])
				else:
					nextYear = extractYearValFromString(self.previousAddress[i+1]['Move_Out']) + 1
				vals["Move_In"] = "{} {}".format(nextMonth, nextYear)
				vals["Move_Out"] = "TBD"


	def ConsolidateInfo(self):
		info = {}
		info["First Name"] = self.firstName
		info["Last Name"] = self.lastName
		info["Zip Code"] = self.zipCode
		info["Relatives"] = self.relatives
		info["People You May Know"] = self.associates
		info["Occupation"] = self.occupation
		info["Address"] = self.address
		info["Previous Address"] = self.previousAddress
		info["Age"] = self.age
		info["Genearal Area"] = self.generalArea
		info["FB Profile"] = self.fbProfile
		info["Similar FB Profile"] = self.similarFBProfile
		info["State"] = self.state
		info["City"] = self.city
		info["Full State"] = self.fullState
		info["LinkedIn Profile Name"] = self.linkedInProfile
		info["Full Name"] = self.fullName
		return info






if __name__ == '__main__':
	a = getInfo("Christopher", "Lambert", "29680")

	thread1 = threading.Thread(target=a.searchFB)
	thread2 = threading.Thread(target=a.searchLI)
	thread3 = threading.Thread(target=a.findGeneralInfo)
	thread1.start()
	thread2.start()
	thread3.start()
	thread1.join()
	thread2.join()
	thread3.join()




	print a.ConsolidateInfo()
	#print(findPerson('kim', 'lambert', '29680'))
	#print(getLinkedInProfile(['chris', 'christopher'], 'lambert', 'greenville', 'south carolina'))
	#print(getLinkedInProfile('christopher lambert'))
