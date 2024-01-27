# import modules
import requests
import logging

def request_json_data(url, headers, querystring):
	"""
		request_json_data - Fucntion to retrieve data from api
		from the specified URL
		url - Api url
		headers - headers of the api
		querystring - Additional information from the api
		returns json data or none
	"""
	try:
		response = requests.get(url, headers=headers, params=querystring)
		data = response.json()
		return data
	except Exception as e:
		logging.error(
			f"An error occurred while retrieving data from {url}: {e}")
		return None
