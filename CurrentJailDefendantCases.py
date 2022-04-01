import pandas as pd 
import os
import fuzzymatcher
from datetime import datetime
from datetime import date
import datetime


def matchInmatesToCases(inmatesDataFrame, concatenatedDataFrames):
	inmatesDataFrame['ColToMatch'] = inmatesDataFrame["LastName"] + ", " +inmatesDataFrame["FirstName"]+ ", " + inmatesDataFrame['DateOfBirth'].astype(str) + ", (" + inmatesDataFrame['Race'] + "/" + inmatesDataFrame['Sex'] + ")"
	inmateDatesOfBirth = list(set(inmatesDataFrame['DateOfBirth'].tolist()))
	#jailInmateLibrary = pd.DataFrame()


	frames = []
	for caseType in concatenatedDataFrames:
		tempCaseType = caseType.drop_duplicates(subset=['File #']).reset_index(drop=True)

		tempCaseType['Def. DOB'] = pd.to_datetime(tempCaseType['Def. DOB'], errors = 'coerce', infer_datetime_format=True)

		tempCaseType['Def. DOB'] = tempCaseType['Def. DOB'].dt.strftime('%Y-%m-%d')

		tempCaseType = tempCaseType[tempCaseType['Def. DOB'].isin(inmateDatesOfBirth)]

		tempCaseType = tempCaseType.dropna(subset=['Def. DOB'])
		tempCaseType['Def. Name'] = tempCaseType['Def. Name'].str.strip()
		tempCaseType['Def. Last Name'] = tempCaseType['Def. Name'].str.split(",").str[0]
		tempCaseType['Def. First Name'] = tempCaseType['Def. Name'].str.split(",").str[1]
		tempCaseType['Def. First Name'] = tempCaseType['Def. First Name'].str.split(" ").str[1]
		tempCaseType['ColToMatch'] = tempCaseType['Def. Last Name'] + ", " + tempCaseType['Def. First Name'] + ", " + tempCaseType['Def. DOB'] + ", (" + tempCaseType['Def. Race'] + "/" + tempCaseType['Def. Sex'] + ")"

		tempCaseType = fuzzymatcher.fuzzy_left_join(tempCaseType, inmatesDataFrame, left_on="ColToMatch", right_on="ColToMatch")

		tempCaseType = tempCaseType[tempCaseType['best_match_score']>.3]
		tempCaseType = tempCaseType[['File #', "best_match_score", 'InmateNum', "ColToMatch_right"]]

		frames.append(tempCaseType)

	jailInmateLibrary = pd.concat(frames)
	jailInmateLibrary = jailInmateLibrary.drop_duplicates(subset=["File #"]).reset_index(drop=True)

	jailInmateLibrary.to_csv("JailInmateLibrary.csv", encoding='utf-8', index = False)
	return concatenatedDataFrames

def matchCasesBackToInmates(inmatesDataFrame, concatenatedDataFrames):
	jailInmateLibrary = pd.read_csv("JailInmateLibrary.csv", encoding = 'utf-8')
	chargesDictionary = pd.read_csv("ChargeCodeCategories.csv", encoding = 'utf-8')
	bondDictionary = pd.read_csv("C:\\Users\\hchapman\\OneDrive - Jackson County Missouri\\Documents\\Dashboards\\BondGatherer\\AllBonds.csv")
	destinationFolder = 'CaseDataForAnalysis\\'
	caseTypeLabels = ['Received', 'Filed', 'Disposed']

	disposedCases = list(set(concatenatedDataFrames[2]['File #'].tolist()))

	i = 0
	for caseType in concatenatedDataFrames:
		tempCaseType = caseType.merge(jailInmateLibrary, how='left', on = "File #")
		tempCaseType = tempCaseType.dropna(subset=['InmateNum']).reset_index(drop=True)
		tempCaseType = tempCaseType.merge(chargesDictionary, how='left', on='Ref. Charge Code')
		tempCaseType = tempCaseType.merge(bondDictionary, how = 'left', on = 'File #')
		tempCaseType = tempCaseType[~tempCaseType['File #'].isin(disposedCases)]

		if caseTypeLabels[i] == "Filed":
			filedCasesDF = tempCaseType

		tempCaseType.to_csv(destinationFolder + "Jail Defendants - " +str(i+1) + " - " + caseTypeLabels[i]+".csv", encoding = 'utf-8', index = False)
		i = i + 1
	return filedCasesDF

def getDefendantCaseInformation(inmatesDataFrame, currentCases):

	matchInmatesToCases(inmatesDataFrame, currentCases)
	filedCasesDF = matchCasesBackToInmates(inmatesDataFrame, currentCases)
	
	return filedCasesDF
