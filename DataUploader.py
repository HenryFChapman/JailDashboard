import os
import json
import arcgis
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from arcgis.features import FeatureLayerCollection

def main():
	print("Starting upload")
	gis = GIS("home")

	print("Jail Dashboard")
	feature_layer_item = gis.content.search("fd2d8bbf202042ce87381dd582ab1054")[0]
	print(feature_layer_item)
	flayers = feature_layer_item.tables
	flayer = flayers[0]
	flayer.manager.truncate()
	data_file_location = r'C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Jail Dashboard\JailCombinedData.csv'
	flayerNew = FeatureLayerCollection.fromitem(feature_layer_item)
	flayerNew.manager.overwrite(data_file_location)

if __name__ == "__main__":
	main()