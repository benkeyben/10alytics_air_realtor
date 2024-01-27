# import modules
import json
import requests
import pandas as pd
import configparser
from datetime import datetime
from drop_duplicate import del_duplicate
from drop_columns import drop_columns
from request_json_data import request_json_data
from json_normalize import json_normalize
from load_to_s3_bucket import load_to_s3_bucket

def main():
	"""
	main () function regulate all the other functions in the py files
	and load dataframe data to S3 bucket
	"""
	# Read the configuration from config.ini
	config = configparser.ConfigParser()
	config.read('config.ini')

	# Access the rapid api key and aws access id and secret key
	rapid_api_key = config['Credentials']['RAPID_API_KEY']
	aws_access = config['Credentials']['AWS_ACCESS']
	aws_secret = config['Credentials']['AWS_SECRET']

	url = "https://realty-mole-property-api.p.rapidapi.com/randomProperties"
	headers = {
		"X-RapidAPI-Key":rapid_api_key,
		"X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
	}
	querystring = {"limit": "1000000"}
	data = request_json_data(url, headers, querystring )

	# Create a DataFrame from the extracted data
	property_records_df = pd.DataFrame(data)
	property_records_bak = property_records_df.copy()

	# Replace null values with values
	property_records_df.fillna({
		'assessorID': 'Unknown',
		'county': 'Not available',
		'legalDescription': 'Not available',
		'squareFootage': 0,
		'subdivision': 'Not available',
		'yearBuilt': 0,
		'bathrooms': 0,
		'lotSize': 0,
		'propertyType': 'Unknown',
		'lastSalePrice': 0,
		'lastSaleDate': 'Not available',
		'features': 'None',
		'owner': 'Unknown',
		'propertyTaxes': 'Not available',
		'taxAssessment': 'Not available',
		'features': 'Not available',
		'bedrooms': 0,
		'ownerOccupied': 0,
		'zoning': 'Unknown',
	}, inplace=True)

	# flatten nested JSON structures into a tabular format
	features_df = json_normalize('features', property_records_df)
	taxAssessment_df = json_normalize('taxAssessment', property_records_df)
	propertyTaxes_df = json_normalize('propertyTaxes', property_records_df)
	owner_df = json_normalize('owner', property_records_df)

	# Creating column ids in dataframes
	features_df = features_df.assign(features_id=pd.Series(
	range(1, len(features_df)+1), dtype="int"))

	taxAssessment_df = taxAssessment_df.assign(taxAssessment_id=pd.Series(
		range(1, len(taxAssessment_df)+1), dtype="int"))

	propertyTaxes_df = propertyTaxes_df.assign(propertyTaxes_id=pd.Series(
		range(1, len(propertyTaxes_df)+1), dtype="int"))

	owner_df = owner_df.assign(owner_id=pd.Series(
		range(1, len(owner_df)+1), dtype="int"))

	# location table
	location_df = property_records_df[[
	'addressLine1', 'city', 'state', 'zipCode', 'county', 'longitude', 'latitude']]

	# Creating column ids in location table
	location_df = location_df.assign(location_id=pd.Series(
		range(1, len(location_df)+1), dtype="int"))

	# Sale  Table
	sales_df = property_records_df[['lastSalePrice', 'lastSaleDate']]

	# Creating column ids in sales table
	sales_df = sales_df.assign(sales_id=pd.Series(
		range(1, len(sales_df)+1), dtype="int"))

	# Joining a list of names into a string in owner_df
	owner_df['names'] = owner_df['names'].apply(
	lambda x: ','.join(map(str, x)) if isinstance(x, list) else str(x))

	# Replacing missing or null values
	taxAssessment_df.fillna(0, inplace=True)
	propertyTaxes_df.fillna(0, inplace=True)
	features_df.fillna(
		{
			'architectureType': 'Not provided',
			'cooling': 'False',
			'coolingType': 'Not provided',
			'exteriorType': 'Not provided',
			'fireplace': 'False',
			'floorCount': 0,
			'garage': 'False',
			'garageSpaces': 0,
			'garageType': 'Not provided',
			'heating': 'False',
			'heatingType': 'Not provided',
			'roofType': 'Not provided',
			'roomCount': 0,
			'unitCount': 0,
			'foundationType': 'Not provided',
			'pool': 'False',
			'poolType': 'Not provided',
			'viewType': 'Not provided',
			'fireplaceType': 'Not provided'
		}, inplace=True)
	owner_df.fillna('Not provided', inplace=True)
	owner_df['names'].replace('nan', 'Not provided', inplace=True)

	# Drop columns in these dataframes=
	drop_columns(owner_df, ['mailingAddress.id', 'mailingAddress.addressLine2'])

	# Drop duplicate values in dataframes
	del_duplicate(features_df)
	del_duplicate(taxAssessment_df)
	del_duplicate(propertyTaxes_df)

	# Creating  column ids in property_records dataframe
	property_records = property_records_df.assign(property_id=pd.Series(
		range(1, len(property_records_df)+1), dtype="int"))

	columes = [
		'id', 'formattedAddress', 'addressLine2',
		'addressLine1', 'city', 'state', 'zipCode',
		'county', 'lastSalePrice', 'lastSaleDate',
		'latitude', 'longitude', 'features',
		'taxAssessment', 'propertyTaxes', 'owner'
	]

	# Drop columns in property_records_df
	drop_columns(property_records, columes)

	property_fact_df = property_records.assign(property_fact_id=pd.Series(
    range(1, len(property_records)+1), dtype="int"))

	fact_columns = ['assessorID', 'bedrooms', 'legalDescription',
					'ownerOccupied', 'squareFootage',
					'subdivision', 'yearBuilt', 'zoning',
					'bathrooms', 'lotSize', 'propertyType'
					]

	# Columns to be dropped in property_fact_df
	drop_columns(property_fact_df, fact_columns)

	# Create ids in property_fact_df
	property_fact_df['features_id'] = features_df['features_id']
	property_fact_df['propertyTaxes_id'] = propertyTaxes_df['propertyTaxes_id']
	property_fact_df['location_id'] = location_df['location_id']
	property_fact_df['taxAssessment_id'] = taxAssessment_df['taxAssessment_id']
	property_fact_df['sales_id'] = sales_df['sales_id']
	property_fact_df['owner_id'] = owner_df['owner_id']

	# # Save Dataframes to AWS S3 bucket
	load_to_s3_bucket(sales_df, 'sales_df.csv', aws_access, aws_secret)
	load_to_s3_bucket(owner_df, 'owner_df.csv', aws_access, aws_secret)
	load_to_s3_bucket(features_df, 'features_df.csv', aws_access, aws_secret)
	load_to_s3_bucket(location_df, 'location_df.csv', aws_access, aws_secret)
	load_to_s3_bucket(property_records, 'property_records.csv',
					aws_access, aws_secret)
	load_to_s3_bucket(property_fact_df, 'property_fact_df.csv',
					aws_access, aws_secret)
	load_to_s3_bucket(taxAssessment_df, 'taxAssessment_df.csv',
					aws_access, aws_secret)
	load_to_s3_bucket(propertyTaxes_df, 'propertyTaxes_df.csv',
					aws_access, aws_secret)
	load_to_s3_bucket(property_records_bak,
					'property_records_bak.csv', aws_access, aws_secret)

