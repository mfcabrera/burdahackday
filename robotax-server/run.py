#!flask/bin/python

from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import werkzeug

app = Flask(__name__)
api = Api(app)

todos = {}
documents =  {}

GINI_CLIENT_ID='burda-hackday-01'
GINI_CLIENT_SECRET='q_NoORwCvgZAqgNQiqlAVSV7QCw'


class TodoSimple(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        todos[todo_id] = request.form['files']
        return {todo_id: todos[todo_id]}

class Document(Resource):
	def post(self, document_id):
		#print(request.files['file'])

		parser = reqparse.RequestParser()
		parser.add_argument('name', type=str)
		parser.add_argument('fileupload', type=werkzeug.datastructures.FileStorage, location='files')

		args = parser.parse_args()
		print(args)
		args['fileupload'].save("files/{}".format(document_id))

		documents[document_id] = request.form
		return {document_id: document_id}




#api.add_resource(TodoSimple, '/<string:todo_id>')
_api.add_resource(Document, '/<path:document_id>')


if __name__ == '__main__':
    app.run(debug=True)
