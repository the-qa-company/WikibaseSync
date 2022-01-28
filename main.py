from flask import Flask #
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import requests

app = Flask(__name__)
CORS(app)


api = Api(app)


# RESOURCES: CONTROLLERS AND ACTIONS
class Index(Resource):
    def get(self):
        return {"data": "Welcome to the index"}


# dummy
class Sync(Resource):
    def get(self, item_name, id):
        return {"data": "Sync" + item_name}

    def post(self):
        return {"data": "Nothing posted for now "}


# import one
class ImportOne(Resource):
     def get(self, q_id):
        from api_import_one import mth_import_one
        response = mth_import_one(q_id)
        if response:
            payload = {"status_code": 200, "message": "Import successful"}
        else:
            payload = {"status_code": 500, "message": "Import could not be completed"}
        return payload


class WikiDataQuery(Resource):
    def get(self, query_string):
        url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + query_string + "&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property"
        response = requests.get(url)
        response = response.json()
        if response:
            payload = {"status_code": 200, "response": response}
        else:
            payload = {"status_code": 500, "message": "Import could not be completed"}
        return payload


# ROUTES
api.add_resource(Index, "/")
api.add_resource(Sync, "/sync/<string:item_name>/<int:id>")
api.add_resource(ImportOne, "/import-wikidata-item/<string:q_id>")
api.add_resource(WikiDataQuery, "/remote-wikidata-query/<string:query_string>")

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
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
