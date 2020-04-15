from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import pandas

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class OrganizationList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	apiKey = db.Column(db.String(40))

	def __repr__(self):
		return '<Organization %r>' % self.id

# Global variables; these are idential to the variables you might use in Postman for a given collection
baseUrl = "https://api.meraki.com/api/v0"
perPage = 1000
outputFilePath = "./static/excel/"

# View Organizations
@app.route('/', methods=['POST','GET'])
def index():
	if request.method == 'POST':
		organizationId = request.form['id']
		organizationName = request.form['name']
		organizationApiKey = request.form['apiKey']
		
		new_organization = OrganizationList(
			id = organizationId, 
			name = organizationName, 
			apiKey = organizationApiKey
			)

		try:
			db.session.add(new_organization)
			db.session.commit()
			return redirect('/')
		except:
			return "There was an error adding your organization."
	else:
		try:
			organizations = OrganizationList.query.order_by(OrganizationList.name).all()
			return render_template('index.html', organizations=organizations)
		except:
			return render_template('index.html')

# Delete Organization
@app.route('/<int:id>/delete')
def delete(id):
	organization_to_delete = OrganizationList.query.get_or_404(id)

	try:
		db.session.delete(organization_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return 'Problem deleting organization.'

# View Inventory
@app.route('/<int:id>/inventory')
def inventory(id):
	organization = OrganizationList.query.get_or_404(id)
	apiQueryHeaders = {
		'X-Cisco-Meraki-API-Key': organization.apiKey,
		'Accept': '*/*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive'
	}

	apiQueryURI = baseUrl + "/organizations/" + str(id) + "/inventory"
	
	apiResponse = requests.get(
		apiQueryURI,
		headers=apiQueryHeaders
		)
	
	apiResponseData = apiResponse.json()

	outputExcel = pandas.read_json(apiResponse.content).to_excel(outputFilePath + 'Customer Inventory.xlsx')
	
	return render_template('inventory.html', apiResponseData = apiResponseData)

# View Networks
@app.route('/<int:id>/networks')
def networks(id):
	organization = OrganizationList.query.get_or_404(id)
	apiQueryHeaders = {
		'X-Cisco-Meraki-API-Key': organization.apiKey,
		'Accept': '*/*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Connection': 'keep-alive'
	}

	apiQueryURI = baseUrl + "/organizations/" + str(id) + "/networks"
	
	apiResponse = requests.get(
		apiQueryURI,
		headers=apiQueryHeaders
		)
	
	apiResponseData = apiResponse.json()

	outputExcel = pandas.read_json(apiResponse.content).to_excel(outputFilePath + 'Customer Networks.xlsx')
	
	return render_template('networks.html', apiResponseData = apiResponseData)


if __name__ == "__main__":
	app.run(debug=True)