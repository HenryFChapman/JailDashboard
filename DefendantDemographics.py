import pandas as pd 
from datetime import datetime
from datetime import date
import datetime
import numpy as np

def getDefendantRace(dataframe):
	race = pd.DataFrame()
	race['Number'] = dataframe.groupby(['Race']).size()
	race['Category'] = race.index 
	race['Year'] = "All"

	race = race[['Category', 'Year', "Number"]]
	race['Number'] = race['Number'].astype(int)

	race.reset_index(inplace=False)
	race.to_csv("DataForDashboard\\JailDefendant - RaceDemographics.csv", encoding='utf-8', index=False)

def getDefendantAge(dataframe):
	age = pd.DataFrame()

	dataframe = dataframe.dropna(subset = ['DateOfBirth'])

	dataframe['DateOfBirth'] = pd.to_datetime(dataframe['DateOfBirth'])
	dataframe['Today'] = pd.to_datetime("today")
	dataframe['Age'] = dataframe['Today'] - dataframe['DateOfBirth']
	dataframe['Age'] = dataframe['Age']/np.timedelta64(1, "Y")

	dataframe = dataframe.sort_values('Age')
	bins = np.arange(0, 110, 10)
	ind = np.digitize(dataframe['Age'], bins)

	age["Number"] = dataframe['Age'].value_counts(bins=bins, sort=False)
	age['Number'] = age['Number'].astype(int)
	age['Category'] = age.index
	age['Year'] = "All"

	age = age[['Category', 'Year', "Number"]]
	age.reset_index(inplace=False)
	age.to_csv("DataForDashboard\\JailDefendant - AgeDemographics.csv", encoding='utf-8', index=False)

def getDefendantSex(dataframe):
	sex = pd.DataFrame()
	sex['Number'] = dataframe.groupby(['Sex']).size()
	sex['Number'] = sex['Number'].astype(int)
	sex['Category']  = sex.index 
	sex['Year'] = "All"

	sex = sex[['Category', 'Year', "Number"]]
	sex.reset_index(inplace=False)
	sex.to_csv("DataForDashboard\\JailDefendant - SexDemographics.csv", encoding='utf-8', index=False)

def runInmateDemographicAnalysis(dataframe):
	getDefendantRace(dataframe)
	getDefendantSex(dataframe)
	getDefendantAge(dataframe)