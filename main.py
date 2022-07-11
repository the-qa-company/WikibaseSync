import socket
import sys

import requests
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from threading import Thread

user_config = __import__("user-config")

app = Flask(__name__)
CORS(app)

api = Api(app)


# RESOURCES: CONTROLLERS AND ACTIONS
class Index(Resource):
    def get(self):
        return {"data": "Welcome to the index"}


# dummy
class Sync(Resource):
    def import_thread_spinner(self, query_id):
        def handle():
            from api_import_one import mth_import_one, mth_import_one_without_statements
            response = mth_import_one(query_id)
        t = Thread(target=handle)
        return t

    def get(self, q_id, api_key):
        if is_authorised(api_key):
            t = self.import_thread_spinner(q_id)
            t.start()
            t.join()
            payload = {"status_code": 200, "completed": True, "message": "Import process complete"}
        else:
            payload = {"status_code": 403, "completed": False, "message": "Unathorised Access"}
        return payload


# import one
class ImportOne(Resource):

    def import_thread_spinner(self, query_id):
        def handle():
            from api_import_one import mth_import_one, mth_import_one_without_statements
            response = mth_import_one_without_statements(query_id)
        t = Thread(target=handle)
        return t
    def get(self, q_id, api_key):
        # #from api_import_one import mth_import_one
        # self.import_thread_spinner(q_id).start()
        # #response = mth_import_one(q_id)

        if is_authorised(api_key):
            from api_import_one import mth_import_one, mth_import_one_without_statements
            response = mth_import_one_without_statements(q_id)
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
    def get(self, query_string, query_type, api_key):

        # general english
        # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + \
        #       query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=property"
        url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + \
              query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=" + query_type

        # british english
        # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + query_string + "&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property"
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

class WikibaseQuery(Resource):
    def get(self, query_string, api_key):

        # general english
        url = "http://localhost/w/api.php?action=wbsearchentities&search=" + \
              query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=property"
        if is_authorised(api_key):
            # british english
            # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + query_string + "&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property"

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
api.add_resource(Sync, "/sync/<string:q_id>/<string:api_key>")
api.add_resource(ImportOne, "/import-wikidata-item/<string:q_id>/<string:api_key>")
api.add_resource(WikiDataQuery, "/remote-wikidata-query/<string:query_string>/<string:query_type>/<string:api_key>")
api.add_resource(WikibaseQuery, "/local-wikibase-query/<string:query_string>/<string:api_key>")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
