import requests
import bs4
PIPL_URL = "https://pipl.com/search/?q={0}+{1}&l={2}%2C+{3}"
# 0 = First Name | 1 = Last Name | 2 = City | 3 = State.split(' ')

def grabSite(url):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	return requests.get(url, headers=headers)




def findPerson(firstName, lastName, city, state):
	res = requests.get(PIPL_URL.format(firstName, lastName, city, state))


if __name__ == '__main__':
	res = grabSite(url)
	page = bs4.BeautifulSoup(res.text, 'lxml')


