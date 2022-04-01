from JailDataScraper import scrapeInmates, combineCSVs
from DefendantDemographics import runInmateDemographicAnalysis
from CurrentJailDefendantCases import getDefendantCaseInformation
from DefendantCaseStatistics import runDefendantCaseStatistics
from DataUploaderRunner import DataUploaderRunner
from CaseHistoryCollector import caseHistoryCollector
import pandas as pd 

#Scrape Jail Data
#print("Scrape Inmates")
#inmatesDataFrame = scrapeInmates()
inmatesDataFrame = pd.read_csv("AllInmates.csv", encoding = 'utf-8')

print("Get Updated Karpel Data")
updatedDFs = caseHistoryCollector()

#Run Jail Inmate Demographics
print("Run Jail Inmate Demographics")
runInmateDemographicAnalysis(inmatesDataFrame)

print("Match Jail Inmates to Cases")
#Match Jail Inmates to Cases
filedCasesDF = getDefendantCaseInformation(inmatesDataFrame, updatedDFs)

print("Run Defendant Case Statistics")
runDefendantCaseStatistics(filedCasesDF)

#Export to Combined CSV
combineCSVs()

#Upload to ArcGIS
DataUploaderRunner()