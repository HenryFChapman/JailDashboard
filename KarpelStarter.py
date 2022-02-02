import pandas as pd 
import os
from openpyxl import load_workbook
import sys, os
sys.path.append('C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Jail Dashboard')

#This gets the latest date (or most recent file) from the Karpel Weekly Data Drop
def getNewestFile(weeklyUpload):

	#Initializes Blank List 
	allDates = []

	#Loops through the Weekly Data Drop Folder
	for item in os.listdir(weeklyUpload):

		#Pulls the Date from Each File in the Folder
		date = int(item.split("_")[1])

		#Appends it to a list
		allDates.append(date)

	#Removes all the duplicates
	allDates = list(set(allDates))

	#Sorts the List without Duplicates
	allDates.sort()

	#Grabs the most recent file
	mostRecent = str(allDates[-1])

	#Returns that most recent file. 
	return mostRecent

#This loads the most recent file. It renames columns so they are all standard accross the three types of case categories.
#It also consolidates every address column into one address
def loadMostRecentFile(newestFile, weeklyUpload):

	#Loads Weekly Upload Folder
	directoryList = os.listdir(weeklyUpload)

	#Sorts Folder So Newest Are Up Front
	directoryList.sort(reverse=True)

	i = 0
	updatedCompleteDFs = []
	fixedRowlabels = pd.ExcelFile('FixedRowLabels.xlsx')

	#Loops Through Weekly Upload Directory
	for item in directoryList:

		#Checking if it's the most recent file (Received,Disposed,Filed)
		#Change Here When Adding Case Dispositions
		if newestFile in item and ("Disp" in item or "Rcvd" in item or "Fld" in item) and ("_1800" in item):

			#Load the Most Recent File as a DataFrame
			tempUpdatedDF = pd.read_csv(weeklyUpload + item)

			#Fix the Misspelled/Incorrect Column Headers/Standardize Column Headers
			fixedRowLabel = pd.read_excel(fixedRowlabels, sheet_name = fixedRowlabels.sheet_names[i])
			fixedRowLabelDict = pd.Series(fixedRowLabel['New Name'].values,index=fixedRowLabel['Original Name']).to_dict()
			tempUpdatedDF = tempUpdatedDF.rename(columns=fixedRowLabelDict)

			#Concatenates Address Field into One Field, and drops the old fields that we don't need. 
			tempUpdatedDF["Def. Street Address"] = tempUpdatedDF["Def. Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Street Address2"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. City"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. State"].fillna('').astype(str) + ", " + tempUpdatedDF["Def. Zipcode"].fillna('').astype(str)
			tempUpdatedDF["Offense Street Address"] = tempUpdatedDF["Offense Street Address"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense Street Address 2"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense City"].fillna('').astype(str) + ", " + tempUpdatedDF["Offense State"].fillna('').astype(str) + ", " + tempUpdatedDF["Off. Zipcode"].fillna('').astype(str)
			tempUpdatedDF = tempUpdatedDF.drop(columns=["Def. Street Address2", "Def. City", "Def. State", "Def. Zipcode", "Offense Street Address 2", "Offense City", "Offense State", "Off. Zipcode", "Def. SSN"])

			updatedCompleteDFs.append(tempUpdatedDF)
			i = i + 1

	return updatedCompleteDFs

#This Performs Basic Cleanings and Filters the Data so we just get 2021 data.
def cleanDataSet(updatedCompleteDFs):
	update2021DFs = []
	fileNames = os.listdir("RawData")

	i = 0

	for caseType in updatedCompleteDFs:

		#Drop All the Defendants Named Bogus
		caseTypeClean = caseType[~caseType['Def. Name'].str.contains("Bogus", na=False)]
		caseTypeClean = caseTypeClean.reset_index()

		#If it's a received case, it filters by only 2021 file numbers
		if 'Received' in fileNames[i]:
			caseTypeClean = caseTypeClean[caseTypeClean['File #'] >= 95462456]

		#If it's a filed case, we only look at cases that have a 2021 file date
		if 'Filed' in fileNames[i]:
			caseTypeClean["Filing Dt."] = pd.to_datetime(caseTypeClean["Filing Dt."])
			caseTypeClean = caseTypeClean[(caseTypeClean['Filing Dt.'] > '2021-1-1')]

		if 'Disposed' in fileNames[i]:
			caseTypeClean["Disp. Dt."] = pd.to_datetime(caseTypeClean["Disp. Dt."])
			caseTypeClean = caseTypeClean[(caseTypeClean['Disp. Dt.'] > '2021-1-1')]
		update2021DFs.append(caseTypeClean)
		
		i = i + 1

	return update2021DFs
def karpelStarter():
	weeklyUpload = "H:\\Units Attorneys and Staff\\01 - Units\\DT Crime Strategies Unit\\Weekly Update\\"
	newestFile = getNewestFile(weeklyUpload)
	updatedCompleteDFs = loadMostRecentFile(newestFile, weeklyUpload)
	update2021DFs = cleanDataSet(updatedCompleteDFs)

	return update2021DFs
