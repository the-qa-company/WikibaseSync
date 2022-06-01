import socket
import requests
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from threading import Thread

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

    def get(self, q_id):
        self.import_thread_spinner(q_id).start()
        payload = {"status_code": 200, "message": "Import triggered"}
        return payload


# import one
class ImportOne(Resource):

    def import_thread_spinner(self, query_id):
        def handle():
            from api_import_one import mth_import_one, mth_import_one_without_statements
            response = mth_import_one_without_statements(query_id)
        t = Thread(target=handle)
        return t
    def get(self, q_id):
        # #from api_import_one import mth_import_one
        # self.import_thread_spinner(q_id).start()
        # #response = mth_import_one(q_id)

        from api_import_one import mth_import_one, mth_import_one_without_statements
        response = mth_import_one_without_statements(q_id)
        # print(response)
        if response:
            payload = {"status_code": 200, "message": "Import successful", "pid": response}
        else:
            payload = {"status_code": 500,
                       "message": "Import could not be completed"}
        return payload


class WikiDataQuery(Resource):
    def get(self, query_string, query_type):

        # general english
        # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + \
        #       query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=property"
        url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + \
              query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=" + query_type

        # british english
        # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + query_string + "&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property"

        response = requests.get(url)
        response = response.json()
        if response:
            payload = {"status_code": 200, "response": response}
        else:
            payload = {"status_code": 500,
                       "message": "Import could not be completed"}
        return payload

class WikibaseQuery(Resource):
    def get(self, query_string):

        # general english
        url = "http://localhost/w/api.php?action=wbsearchentities&search=" + \
              query_string + "&format=json&errorformat=plaintext&language=en&uselang=en&type=property"

        # british english
        # url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + query_string + "&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property"

        response = requests.get(url)
        response = response.json()
        if response:
            payload = {"status_code": 200, "response": response}
        else:
            payload = {"status_code": 500,
                       "message": "Import could not be completed"}
        return payload


# ROUTES
api.add_resource(Index, "/")
api.add_resource(Sync, "/sync/<string:q_id>")
api.add_resource(ImportOne, "/import-wikidata-item/<string:q_id>")
api.add_resource(WikiDataQuery, "/remote-wikidata-query/<string:query_string>/<string:query_type>")
api.add_resource(WikibaseQuery, "/local-wikibase-query/<string:query_string>")

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
#
#
# @app.route("/syncc")
# def syncc():
#     return "Sync page"
#
# @app.route("/import-one/<string:id>")
# def get(id):
#     from import_one import mth_import_one
#     mth_import_one(id)
#     return {"message": "import complete"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
