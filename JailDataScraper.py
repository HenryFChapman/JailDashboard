from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import math
import pandas as pd
import os
from datetime import datetime
from datetime import date

def scrapeInmates():
	#JCOOL Inmate Lookup
	url = "http://jccweb.jacksongov.org/InmateSearch/Default.aspx"

	#Loading WebDriver
	options = FirefoxOptions()
	options.headless = True 
	driver = webdriver.Firefox(options = options)
	#Loading Webpage
	driver.get(url)

	#Clicking Search to Get a List of Inmates
	button = driver.find_element_by_css_selector('#btnSearch')
	button.click()

	#Saving Page Content as HTML
	content = driver.page_source
	soup = BeautifulSoup(content, features="lxml")

	#Finds Out How Many Pages of Inmates There Are
	span = soup.body.find("span", attrs={'id':'lblUserMsg'}).text
	numberOfInmates = span.split(":")
	numberOfInmates = numberOfInmates[1]
	numberOfInmates = numberOfInmates.split('.')
	numberOfInmates = numberOfInmates[0]
	numberOfInmates = numberOfInmates.split(' ')
	numberOfInmates = float(numberOfInmates[1])
	numberOfPages = math.ceil(numberOfInmates/10)

	#Creates a List of Clickable Links 
	linkArrayForClicking = []
	for i in range(1, numberOfPages+1):
		if (i-1) % 10 == 0 and i!=1:
			linkArrayForClicking.append("...")
		else:
			linkArrayForClicking.append(str(i))


	#OuterLoop Loops Through Each Individual Page (10 Inmates)
	data = []
	for i in range(1, numberOfPages+1):
		Page = []
		content = driver.page_source
		soup = BeautifulSoup(content, features="lxml")
		table = soup.find_all('table')
		table = table[1]

		inmateNames = table.findAll('tr')
		x = (len(table.findAll('tr'))) - 2

		#InnerLoop Loops through Each Table
		for row in inmateNames[1:x]:
			individualInmateData = []
			col = row.findAll('td')

			#IDNumber
			IDNumber = col[0].getText()
			individualInmateData.append(IDNumber)
			#Last Name
			LastName = col[1].getText()
			individualInmateData.append(LastName)
			#First Name
			FirstName = col[2].getText()
			individualInmateData.append(FirstName)
			#Middle Initial
			MiddleName = col[3].getText()
			individualInmateData.append(MiddleName)

			#DOB
			DOB = col[4].getText()
			individualInmateData.append(DOB)
			#Race
			Race = col[5].getText()
			individualInmateData.append(Race)
			#Sex
			Sex = col[6].getText()
			individualInmateData.append(Sex)
			Page.append(individualInmateData)

		data.append(Page)

		if i < numberOfPages:
			nextLink = driver.find_elements_by_link_text(linkArrayForClicking[i])
			if len(nextLink) > 1:
				nextLink[1].click()
			else:
				nextLink[0].click()

	driver.close()

	listOfRows  = []
	for i in data:
		for j in i:
			listOfRows.append(j)

	df = pd.DataFrame(listOfRows, columns=['InmateNum', "LastName", "FirstName", "MiddleName", "DateOfBirth", "Race", "Sex"])

	df['LastName'] = df['LastName'].str.upper().str.title()
	df['FirstName'] = df['FirstName'].str.upper().str.title()
	df['MiddleName'] = df['MiddleName'].str.upper().str.title()
	df['DateOfBirth'] = pd.to_datetime(df['DateOfBirth'])

	df['MiddleName'] = df['MiddleName'].str.replace(r'[^\x00-\x7f]', '', regex = True)
	df.to_csv( "AllInmates.csv", index=False, encoding='utf-8')

	return df


def combineCSVs():
	dataDirectory = "DataForDashboard\\"

	

	frames = []

	for dataItem in os.listdir(dataDirectory):

		tempDataFrame = pd.read_csv(dataDirectory+dataItem)

		tempDataFrame['DataType'] = dataItem

		if "Individual" in dataItem:
			tempDataFrame['File Number'] = tempDataFrame['File Number'].astype(str)

		frames.append(tempDataFrame)

	combinedDataDF = pd.concat(frames)

	combinedDataDF.to_csv("JailCombinedData.csv", index = False, encoding = 'utf-8')
