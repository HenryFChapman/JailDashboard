from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pandas as pd
from datetime import datetime
from datetime import date
import time
#import pytesseract
#from PIL import Image
#import sys
#import cv2
#import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

def clayCountyScraper():
	#Clay County Inmate Lookup
	url = "https://www.claymosheriff.org/popsheet.php"

	#Loading WebDriver
	options = FirefoxOptions()
	options.headless = True 
	driver = webdriver.Firefox(options = options)
	#Loading Webpage
	driver.get(url)

	clayInmates = pd.read_html(driver.page_source)[0]

	#Make First Row Column Headers
	clayInmates.columns = clayInmates.iloc[0]

	#Drop First Row
	clayInmates = clayInmates.drop([0])

	#Close Webdriver Browser
	driver.close()

	#Drop all the Blank Names
	clayInmates = clayInmates.dropna(subset = ['Name'])

	#Export to CSV
	clayInmates.to_csv("ClayCountyInmates.csv", encoding= 'utf-8')

def wyandotteCountyScraper():
	#Load Inmate URL
	url = 'http://ils.wycosheriff.org/Default.aspx?ID=WCDC2'

	#Loading WebDriver
	options = FirefoxOptions()
	options.headless = False 
	driver = webdriver.Firefox(options = options)
	#Loading Webpage
	driver.get(url)
	time.sleep(5)

	#Get List of Inmates
	inmateList = driver.find_element_by_xpath('//*[@id="inmateList"]').get_attribute('innerHTML')

	#Initialize Beautiful Soup
	soup = BeautifulSoup(inmateList, 'html.parser')
	
	#Get All of the List Tags (For List of Inmates)
	nameList = soup.find_all('li', string=True)

	#Initialize Lists
	firstName = []
	lastName = []
	inmateID = []
	textList = []

	#For Each Name in Name List, grab their first, last, and inmate id number...
	for name in nameList:
		name = str(name)
		splitName = name.split('"')
		firstName.append(splitName[1])
		lastName.append(splitName[5])
		inmateID.append(splitName[3])

	#Construct a DataFrame of Wyandotte County Inmates
	wyandotteCountyInmates = pd.DataFrame()
	wyandotteCountyInmates['InmateNumber'] = inmateID
	wyandotteCountyInmates['lastName'] = lastName
	wyandotteCountyInmates['firstName'] = firstName
	wyandotteCountyInmates = wyandotteCountyInmates.fillna(0)

	print(wyandotteCountyInmates.head())

	wyandotteCountyInmates.to_csv("WyandotteCountyInmates.csv")
	alreadyScraped = wyandotteCountyInmates['InmateNumber'].tolist()

	#Load Current Inmates
	giantInmateDataFrame = pd.read_csv("WyandotteFull.csv", encoding = 'utf-8')
	alreadyScraped = giantInmateDataFrame['InmateNumber'].astype(str).tolist()

	#Filter the Inmate DataFrame to those inmates who haven't been scraped yet
	wyandotteCountyInmatesNew = wyandotteCountyInmates[~wyandotteCountyInmates['InmateNumber'].isin(alreadyScraped)]
	wyandotteCountyInmatesNew = wyandotteCountyInmatesNew[wyandotteCountyInmatesNew['InmateNumber']!='']
	wyandotteCountyInmatesNew = wyandotteCountyInmatesNew.reset_index()

	for i, row in wyandotteCountyInmatesNew.iterrows():
		tempInmateDF = wyandotteCountyInmatesNew[wyandotteCountyInmatesNew['InmateNumber']==row['InmateNumber']]

		element = driver.find_element_by_xpath('//*[@id="' + str(row['InmateNumber']) + '"]')
		element.click()
		time.sleep(5)

		tempTable = driver.find_element_by_xpath('//*[@id="mainInfo"]').get_attribute('outerHTML')
		tempTable = pd.read_html(tempTable)[0]
		tempTable = tempTable.T

		#Make First Row Column Headers
		tempTable.columns = tempTable.iloc[0]

		#Drop First Row
		tempTable = tempTable.drop([0])
		tempTable = tempTable.drop(tempTable.columns[[0]], axis = 1)
		tempTable['InmateNumber'] = [row['InmateNumber']]

		tempInmateDF = tempInmateDF.merge(tempTable, on = 'InmateNumber', how = 'left')
		giantInmateDataFrame = giantInmateDataFrame.append(tempInmateDF)
		giantInmateDataFrame.to_csv("WyandotteFull.csv", encoding= 'utf-8', index = False)
	driver.close()

	#Get Rid of Inmates who are no longer incarcerated
	alreadyScraped = wyandotteCountyInmates['InmateNumber'].tolist()


	print(alreadyScraped)

	giantInmateDataFrame = giantInmateDataFrame[giantInmateDataFrame['InmateNumber'].isin(alreadyScraped)]

	return 0

def main():
	clayCountyScraper()
	wyandotteCountyScraper()

main()

def platteCountyScraper():

	#Clay County Inmate Lookup
	#url = "https://omsweb.public-safety-cloud.com/jtclientweb/(S(0qwneyzqxq3cu0erxplq4lzt))/jailtracker/index/Platte_County_MO"

	#Loading WebDriver
	#options = FirefoxOptions()
	#options.headless = False 
	#driver = webdriver.Firefox(options = options)
	#Loading Webpage
	#driver.get(url)

	#time.sleep(5)


	#wait until user scrapes data

	#Download Image
	#with open('filename.jpg', 'wb') as file:
	#	file.write(driver.find_element_by_xpath('//*[@id="img-captcha"]').screenshot_as_png)

	captcha = AmazonCaptcha('index.jpg')
	solution = captcha.solve()
	print(solution)

	#Use OCR to get characters

	#img = cv2.imread('filename.png')


	#display image in window
	#cv2.imshow('image',img) #@param - windowname, image to be displayed

	#horizontal_inv = cv2.bitwise_not(img)
	#perform bitwise_and to mask the lines with provided mask
	#masked_img = cv2.bitwise_and(img, img, mask=horizontal_inv)
	#reverse the image back to normal
	#masked_img_inv = cv2.bitwise_not(masked_img)

	#kernel = np.ones((5,5),np.uint8)
	#dilation = cv2.dilate(masked_img_inv,kernel,iterations = 3) # to remove blackline noise
	#cv2.imwrite("result1.jpg", dilation)


	#image = cv2.imread("Resampled.png")
	#pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'
	#result = pytesseract.image_to_string(image)

	#print(result)

	#Return Characters to field

	#Press Enter

	#driver.close()
