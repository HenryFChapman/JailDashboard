import pandas as pd 
from datetime import datetime
from datetime import date
import datetime
import numpy as np


def getCaseCategories(dataframe):
	caseCategories = pd.DataFrame(columns = ['Category', "Year", "Number"])

	dataframe['Filing Dt.'] = pd.to_datetime(dataframe['Filing Dt.'])
	dataframe['Filing Year'] = pd.DatetimeIndex(dataframe['Filing Dt.']).year
	dataframe = dataframe.dropna(subset = ["Filing Dt."])
	filingYear = list(set(dataframe['Filing Year'].astype(int).tolist()))
	caseCategories = pd.DataFrame(columns = ['Category', "Year", "Number"])

	#get list of categories
	categoryList = list(set(dataframe['Category'].tolist()))

	numberList = []
	for category in categoryList:

		tempBondCategory = dataframe[dataframe['Category'] == category]
		tempBondCategory = tempBondCategory.drop_duplicates(subset = ['File #'])
		tempNumber = len(tempBondCategory['Initial Bond'].index)
		numberList.append(tempNumber)
	
	caseCategories['Year'] = "All"
	caseCategories['Category'] = categoryList
	caseCategories['Number'] = numberList
	caseCategories.reset_index(inplace=False)
	caseCategories.to_csv("DataForDashboard\\JailDefendant - CaseCategories.csv", encoding='utf-8', index=False)

def getBondByCategory(dataframe):
	bondCategory = pd.DataFrame(columns = ['Category', 'Year', 'Number'])

	dataframe = dataframe.dropna(subset = ['Category'])

	#get list of categories
	categoryList = list(set(dataframe['Category'].tolist()))

	medianList = []
	for category in categoryList:

		tempBondCategory = dataframe[dataframe['Category'] == category]
		tempBondCategory = tempBondCategory.drop_duplicates(subset = ['File #'])

		tempMedian = tempBondCategory['Initial Bond'].median()
		medianList.append(tempMedian)

	bondCategory['Year'] = "All"
	bondCategory['Category'] = categoryList
	bondCategory['Number'] = medianList
	bondCategory.to_csv("DataForDashboard\\JailDefendant - InitialBond.csv", encoding = 'utf-8', index = False)

def getReferringAgency(dataframe):
	referringAgency = pd.DataFrame(columns = ['Category', "Year", "Number"] )
	allReferringAgencies = pd.read_excel("PD Agency.xlsx")

	dataframe = dataframe.drop_duplicates(subset = ['File #'])
	dataframe = dataframe.merge(allReferringAgencies, on='Agency')

	dataframe['Filing Dt.'] = pd.to_datetime(dataframe['Filing Dt.'])
	dataframe['Filing Year'] = pd.DatetimeIndex(dataframe['Filing Dt.']).year
	dataframe = dataframe.dropna(subset = ["Filing Dt."])
	filingYear = list(set(dataframe['Filing Year'].astype(int).tolist()))

	#Loop Through Years
	for tempYear in filingYear:
		tempDataFrame = dataframe[dataframe['Filing Year']==tempYear]
		tempReferringAgenciesDF = pd.DataFrame()
		tempReferringAgenciesDF["Number"] = tempDataFrame.groupby(['PD NAME']).size()
		tempReferringAgenciesDF['Year'] = tempYear
		referringAgency = referringAgency.append(tempReferringAgenciesDF)

	#Get All
	allReferringAgenciesDF = pd.DataFrame()
	allReferringAgenciesDF['Number'] = dataframe.groupby(['PD NAME']).size()
	allReferringAgenciesDF['Year'] = "All"

	referringAgency = referringAgency.append(allReferringAgenciesDF)

	referringAgency['Category'] = referringAgency.index
	referringAgency['Number'] = referringAgency['Number'].astype(int)
	referringAgency.reset_index(inplace=False)
	referringAgency.to_csv("DataForDashboard\\JailDefendant - ReferringAgency.csv", encoding='utf-8', index=False)

def getInmateDurationHistogram(dataframe):
	age = pd.DataFrame()

	dataframe = dataframe.drop_duplicates(subset = ['File #'])
	dataframe = dataframe.dropna(subset = ["Filing Dt."])
	filingYear = list(set(dataframe['Filing Year'].astype(int).tolist()))

	dataframe['Today'] = pd.to_datetime('today')
	dataframe['Age of Case (Months)'] = dataframe['Today'] - dataframe['Filing Dt.'] 
	dataframe['Age of Case (Months)'] = dataframe['Age of Case (Months)']/np.timedelta64(1, "M")

	dataframe = dataframe.sort_values('Age of Case (Months)')
	bins = np.arange(0, 66, 6)
	ind = np.digitize(dataframe['Age of Case (Months)'], bins)
	age["Number"] = dataframe['Age of Case (Months)'].value_counts(bins=bins, sort=False)
	age['Year'] = "All"
	age['Category'] = age.index

	age = age[['Category', 'Year', "Number"]]
	age['Number'] = age['Number'].astype(int)
	age.reset_index(inplace=False)
	age.to_csv("DataForDashboard\\JailDefendant - CaseAgeHistogram.csv", encoding='utf-8', index=False)

def inmatesMostRecentFiledCases(dataframe):
	MostRecentDefendants = pd.DataFrame()
	dataframe = dataframe.dropna(subset = ["Filing Dt."])
	dataframe = dataframe.reset_index()
	dataframe['Filing Dt.'] = pd.to_datetime(dataframe['Filing Dt.'])
	MostRecentDefendants = dataframe[dataframe['Filing Dt.'] > datetime.datetime.now() - pd.to_timedelta("60day")].reset_index()
	MostRecentDefendants = MostRecentDefendants.dropna(subset = ["Category"])
	MostRecentDefendants["File #"]= MostRecentDefendants["File #"].astype(str).str.split(".", n = 1, expand = True)

	#Name
	name = pd.DataFrame()
	name = MostRecentDefendants.groupby('File #')['Def. Name'].apply(set).to_frame().reset_index()

	#DOB
	DOB = pd.DataFrame()
	DOB = MostRecentDefendants.groupby('File #')['Def. DOB'].apply(set).to_frame().reset_index()

	#Filing Date
	filingDT = pd.DataFrame()
	filingDT = MostRecentDefendants.groupby('File #')['Filing Dt.'].apply(set).to_frame().reset_index()

	#Categories
	categories = pd.DataFrame()
	categories = MostRecentDefendants.groupby('File #')['Category'].apply(set).to_frame().reset_index()

	display = pd.DataFrame()
	display['File #'] = list(set(MostRecentDefendants['File #'].tolist()))
	display = display.merge(name, on = 'File #', how = 'left')
	display = display.merge(DOB, on = 'File #', how = 'left')
	display = display.merge(filingDT, on = 'File #', how = 'left')
	display = display.merge(categories, on = 'File #', how = 'left')

	display['Def. Name'] =  display['Def. Name'].astype(str).apply(lambda x: x.replace('{','').replace('}','').replace("'", "").replace(",", ";"))
	display['Def. DOB'] =   display['Def. DOB'].astype(str).apply(lambda x: x.replace('{','').replace('}','').replace("'", "").replace("00:00:00.000", "").replace(",", ";"))

	display['Category'] =   display['Category'].astype(str).apply(lambda x: x.replace('{','').replace('}','').replace("'", "").replace(",", ";"))

	display['Filing Dt.'] =   display['Filing Dt.'].astype(str).apply(lambda x: x.replace('{','').replace('}','').replace("Timestamp('", ""))
	display["Filing Dt."]= display["Filing Dt."].astype(str).str.split(",", n = 1, expand = True)
	display['Filing Dt.'] = display['Filing Dt.'].replace("')", "")
	display["Filing Dt."]= display["Filing Dt."].astype(str).str.split(" ", n = 1, expand = True)
	display.to_csv("DataForDashboard\\JailDefendant - MostRecentDefendants.csv", encoding='utf-8', index=False)

def runDefendantCaseStatistics(filedCasesDF):
	#dataframe = pd.read_csv("CaseDataForAnalysis\\Jail Defendants - 2 - Filed.csv", encoding = 'utf-8')

	getCaseCategories(filedCasesDF)
	getBondByCategory(filedCasesDF)
	getReferringAgency(filedCasesDF)
	getInmateDurationHistogram(filedCasesDF)
	inmatesMostRecentFiledCases(filedCasesDF)