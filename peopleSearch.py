import requests
import bs4
import re
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pickle

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
	driver.set_page_load_timeout(20)
	return driver

def searchFacebook():
	profileURLs = []
	mainURL = ""
	driver = createHeadlessBrowser()
	cookies = pickle.load(open("../cookies.pkl", "rb"))
	driver.get("https://m.facebook.com/")
	for cookie in cookies:
		driver.add_cookie(cookie)
	driver.get("https://m.facebook.com/search/people/?q=bob%20smith&source=filter&isTrending=0")
	#driver.find_element_by_css_selector("div.cd").click()
	file = open("fileToWrite.txt", "w")
	file.write(str(driver.page_source))
	file.close()
	a = open("fileToWrite.txt").read()
	for var in re.findall('profile.php\?id=(.+)"', a):
		if str(var)[::-1][:9][::-1] == 'ia-label=':
			url = "https://m.facebook.com/" + str(var).partition('"')[0]
			if len(profileURLs) == 0:
				mainURL = url
			profileURLs.append(url)
	driver.save_screenshot('static.png')
	return {"Profile_Address": mainURL, "Possible_Profiles": profileURLs}

if __name__ == '__main__':
	print(searchFacebook())
	#print findPerson('michael', 'lambert', '29644')
