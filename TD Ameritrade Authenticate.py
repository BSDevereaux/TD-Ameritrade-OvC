from splinter import Browser
from selenium import webdriver
import requests
from accountnumbers import *


### install chromedriver and add file to executable_path ###

#path defined to chrome driver
executable_path = {'executable_path': r'C:\Users\Brian\Desktop\chromedriver_win32\chromedriver'}

# create a new instance of chrome
browser = Browser('chrome', **executable_path, headless = False)

# define the components of the url
method = 'GET'
url = 'https://auth.tdameritrade.com/auth?'
payload = {'response_type': 'code', 'redirect_uri':'http://localhost/test', 'client_id': client_id2}

# build url
built_url = requests.Request(method, url, params = payload).prepare()
built_url = built_url.url

# go to our URL
browser.visit(built_url)

browser.find_by_id('username').fill(username)
browser.find_by_id('password').fill(password)
browser.find_by_id("accept").first.click()


##ADD THIS TO OVC new_url

