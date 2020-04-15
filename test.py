from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import pandas

# Global variables; these are idential to the variables you might use in Postman for a given collection
baseUrl = "https://api.meraki.com/api/v0"
perPage = 1000

id = 537758 
name = "Meraki Launchpad"
apiKey = "093b24e85df15a3e66f1fc359f4c48493eaa1b73"

organization = {
	'id': id,
	'name': name,
	'apiKey': apiKey
}

apiQueryHeaders = {
	'X-Cisco-Meraki-API-Key': organization['apiKey'],
	'Accept': '*/*',
	'Accept-Encoding': 'gzip, deflate, br',
	'Connection': 'keep-alive'
}

apiQueryURI = baseUrl+ "/organizations/" + str(id) + "/inventory"

apiResponse = requests.get(
	apiQueryURI,
	headers=apiQueryHeaders
	)

apiResponseData = apiResponse.json()

for device in apiResponseData:
	count += 1