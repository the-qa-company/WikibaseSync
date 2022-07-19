import socket
import sys

import requests
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from threading import Thread

from util.util import import_one

user_config = __import__("user-config")

app = Flask(__name__)
CORS(app)

api = Api(app)

class Index(Resource):
    def get(self):
        return {"data": "Welcome to the index"}

# class that imports all statements from Wikidata
class Sync(Resource):
    def get(self):
        q_id = request.args.get('q_id')
        api_key = request.args.get('api_key')
        if is_authorised(api_key):
            import_one(q_id).getID()
            payload = {"status_code": 200, "completed": True, "message": "Import process complete"}
        else:
            payload = {"status_code": 403, "completed": False, "message": "Unauthorised Access"}
        return payload

# import one
class ImportOne(Resource):
    def get(self):
        q_id = request.args.get('q_id')
        api_key = request.args.get('api_key')

        if is_authorised(api_key):
            response = import_one(q_id, import_statements = False).getID()
            #   print(response)
            if response:
                payload = {"status_code": 200, "message": "Import successful", "pid": response}
            else:
                payload = {"status_code": 500,
                           "message": "Import could not be completed"}
        else:
            payload = {"status_code": 403, "completed": False, "message": "Unathorised Access"}
        return payload


class WikiDataQuery(Resource):
    def get(self):
        query_string = request.args.get('query_string')
        query_type = request.args.get('query_type')
        api_key = request.args.get('api_key')

        url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + \
              query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=" + query_type

        if is_authorised(api_key):
            response = requests.get(url)
            response = response.json()
            if response:
                payload = {"status_code": 200, "response": response}
            else:
                payload = {"status_code": 500,
                           "message": "Import could not be completed"}
        else:
            payload = {"status_code": 403, "completed": False, "message": "Unathorised Access"}
        return payload


def is_authorised(api_key):
    if str(user_config.apiKey) == api_key:
        return True
    else:
        return False


# ROUTES
api.add_resource(Index, "/")
api.add_resource(Sync, "/sync")
api.add_resource(ImportOne, "/import-wikidata-item")
api.add_resource(WikiDataQuery, "/remote-wikidata-query")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
