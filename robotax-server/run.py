#!flask/bin/python

from flask import Flask, send_file, make_response, request, send_from_directory
from flask_restful import Resource, Api
from flask_restful import reqparse
import werkzeug
import requests
from requests.auth import HTTPBasicAuth
import time
import config
import json

app = Flask(__name__)
api = Api(app)

# OUR Database :P
documents =  {}


@app.route('/app/<path:path>')
def send_files(path):
    return send_from_directory(config.APP_PATH, path)



class Document(Resource):


	def post(self, document_id):
		#print(request.files['file'])
		print("POST")

		parser = reqparse.RequestParser()
		parser.add_argument('name', type=str)
		parser.add_argument('fileupload', type=werkzeug.datastructures.FileStorage, location='files')

		args = parser.parse_args()
		#print(args)
		self.local_path = config.LOCAL_PATH.format(document_id)

		args['fileupload'].save(self.local_path)

		documents[document_id] = self
		self.document_id = document_id

		r  = requests.post(config.GINI_URL,
						   files={'file': (document_id, open(self.local_path), 'application/octect-stream')},
		 				   auth=HTTPBasicAuth(config.GINI_USER, config.GINI_PASSWD),
						   headers = config.GINI_HEADERS
		)

		self.name = document_id
		self.gini_loc = r.headers['location']
		self.gini_id =  self.gini_loc.split('/')[-1]


		# GET and store extractions and layout
		ext_url = "{}/extractions".format(self.gini_loc)
		print(ext_url)


		time.sleep(3)

		p = requests.get(ext_url,
						 auth=HTTPBasicAuth(config.GINI_USER, config.GINI_PASSWD),
						 headers = config.GINI_HEADERS)
		print(p.status_code)
		self.extractions = p.json()


		self.data = self.process_extractions(self.extractions)

		response =  {'gini_id': self.gini_id,
					 'document_id': self.document_id,
					 'gini_loc': self.gini_loc,
					 'original_file': 'http://api.robo.tax:8080/docs/{}'.format(self.name)
		}


		response.update(self.data)

		return response

	def detect_main_category(self):
		pass

	def process_extractions(self, extractions):
		ext = extractions.get("extractions", {})
		d = {}
		d['paymentRecipient'] =  ext.get('paymentRecipient', {}).get('value', 'UNK')
		d['amountToPay'] = ext.get("amountToPay", {}).get('value','UNK')

		d['docType'] = ext.get("docType", {}).get('value','Other')


		brut = self.try_to_extract_brutto(extractions)

		ap = d['amountToPay']
		if ap != 'UNK':
			ap = float(ap.split(":")[0])
			d['Mwst'] = ap * 0.18
		else:
			d['Mwst'] = 'UNK'

		if brut is not None:
			# Maybe a better approx:
			d['Mwst'] = brut * 0.19

		return d

	def try_to_extract_brutto(self, extractions):
		ext = extractions
		l = ext.get("candidates",{}).get("amounts", [])

		if len(l) < 3: # toal, brutto and shipping
			return None

		values = sorted(map(lambda x: float(x["value"].split(":")[0]), l))
		return values[2]

	def get(self, document_id):
		print('GET HEADERS')
		print(request.headers)
		print(document_id)

		d =  documents.get(document_id, None)
		if d is not None:
			return d.data
		else:
			return None

	# def get_file(self, document_id):
	# 	f = config.LOCAL_PATH.format(document_id)
	# 	response = send_file(f, mimetype='application/octet-stream')
	# 	return response

@api.representation('application/json')
def output_json(data, code, headers=None):
	print("JSON Requested")
	resp = make_response(json.dumps(data), code)
	resp.headers.extend(headers or {})
	return resp

@api.representation('application/octect-stream')
def get_file(data, code, headers=None):
	print("Image requested")
	f = config.LOCAL_PATH.format(data['document_id'])
	response = send_file(f, mimetype='application/octet-stream')
	return response

api.add_resource(Document, '/docs/<path:document_id>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
