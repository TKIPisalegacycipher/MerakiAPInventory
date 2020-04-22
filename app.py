from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

# We're only importing this for its ability to convert JSON to XLSX.
import pandas

from meraki_sdk.meraki_sdk_client import MerakiSdkClient
import jsonpickle
import requests


# With the Meraki SDK, we don't need these.
#import requests
#import json

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Api(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(40))
	name = db.Column(db.String(100))
	lastfour = db.Column(db.String(4))
	orgs = db.relationship('OrganizationList', backref='api_key')

class OrganizationList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200))
	key_id = db.Column(db.Integer, db.ForeignKey('api.id'))

# Global variables; these are idential to the variables you might use in Postman for a given collection
outputFilePath = "./static/excel/"

# You don't need these with the Meraki SDK.
# baseUrl = "https://api.meraki.com/api/v0"
# perPage = 1000

# View API keys
@app.route('/', methods=['POST','GET'])
def index():
	if request.method == 'POST':
		key = request.form['apiKey']
		name = request.form['name']
		lastfour = key[len(key)-4:len(key)]

		new_key = Api(
			key = key,
			name = name,
			lastfour = lastfour
			)
		
		try:
			db.session.add(new_key)
			db.session.commit()
			return redirect('/')

		except:
			return "There was an error adding your API key."
		
	else:
		try:
			api_keys = Api.query.order_by(Api.key).all()
			return render_template('index.html', keys=api_keys)
		except:
			return render_template('index.html')


# Delete Key
@app.route('/key/<int:id>/delete')
def delete(id):
	key_to_delete = Api.query.get_or_404(id)

	try:
		db.session.delete(key_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return 'Problem deleting key.'

# View Organizations
@app.route('/key/<int:id>/organizations')
def organizations(id):

	# Connect to the Meraki API.
	x_cisco_meraki_api_key = Api.query.get_or_404(id).key
	client = MerakiSdkClient(x_cisco_meraki_api_key)

	# get all organizations
	orgs = client.organizations.get_organizations()

	try:
		return render_template('organizations.html', organizations = orgs, id = id)
	except:
		return render_template('organizations.html')

# View Inventory
@app.route('/key/<int:id>/organization/<organization_id>/inventory')
def inventory(id, organization_id):

	# Connect to the Meraki API.
	x_cisco_meraki_api_key = Api.query.get_or_404(id).key
	client = MerakiSdkClient(x_cisco_meraki_api_key)

	# An instance of the OrganizationsController class can be accessed from the API Client.
	organizations_controller = client.organizations

	# get_organization_inventory() accepts the organization id as integer input and provides a dictionary as output. Contrary to documentation, get_organization_inventory() does not accept a dictionary as input. 
	#collect = {}
	#collect['organization_id'] = organization_id

	try:
		inventory = organizations_controller.get_organization_inventory(organization_id)

		outputExcel = pandas.read_json(jsonpickle.encode(inventory)).to_excel(outputFilePath + 'Customer Inventory.xlsx')

		return render_template('inventory.html', organization = organization_id, inventory = inventory)

	except Exception as e:
		return(str(e))
	
	

# View Networks
@app.route('/key/<int:id>/organization/<organization_id>/networks')
def networks(id, organization_id):
	# Connect to the Meraki API.
	x_cisco_meraki_api_key = Api.query.get_or_404(id).key
	client = MerakiSdkClient(x_cisco_meraki_api_key)

	# An instance of the NetworksController class can be accessed from the API Client.
	networks_controller = client.networks

	# get_organization_networks() accepts a dictionary as input and provides all networks for that organization
	collect = {}
	collect['organization_id'] = organization_id
	
	try:
		networks = networks_controller.get_organization_networks(collect)

		outputExcel = pandas.read_json(jsonpickle.encode(networks)).to_excel(outputFilePath + 'Customer Networks.xlsx')

		return render_template('networks.html', organization = organization_id, networks = networks)

	except Exception as e:
		return(str(e))


if __name__ == "__main__":
	app.run(debug=True)