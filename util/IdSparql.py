# this class makes the correspondence between Wikidata entities and entities in the Wikibase using the external
# identifier for Wikidata
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
import configparser

from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier


class IdSparql:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)

        return class_._instance

    def __init__(self):
        self.mapEntity = {}
        self.mapProperty = {}
        wikibase = pywikibot.Site("my", "my")
        wikibase_repo = wikibase.data_repository()
        wikibase_repo.login()
        identifier = PropertyWikidataIdentifier()
        identifier.get(wikibase_repo)
        self.item_identifier = identifier.itemIdentifier
        self.property_identifier = identifier.propertyIdentifier
        self.app_config = configparser.ConfigParser()
        self.app_config.read('config/application.config.ini')
        self.endpoint = self.app_config.get('wikibase', 'sparqlEndPoint')
        self.load()

    def load(self):
        sparql = SPARQLWrapper(self.endpoint)
        query = """
                            select ?item ?id where {
                                ?item <""" + self.app_config.get('wikibase',
                                                                 'propertyUri') + """/direct/""" + self.item_identifier + """> ?id
                            }
                        """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results['results']['bindings']:
            split = result['item']['value'].split('/')
            id = split[len(split) - 1]
            if id.startswith('Q'):
                self.mapEntity[result['id']['value']] = id
        query = """
                    select ?item ?id where {
                        ?item <""" + self.app_config.get('wikibase',
                                                         'propertyUri') + """/direct/""" + self.property_identifier + """> ?id
                    }
                """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results['results']['bindings']:
            split = result['item']['value'].split('/')
            id = split[len(split) - 1]
            if id.startswith('P'):
                self.mapProperty[result['id']['value']] = id
            else:
                print("This should not happen")

    def get_id(self, id):
        if id.startswith("Q"):
            return self.mapEntity[id]
        elif id.startswith("P"):
            return self.mapProperty[id]
        else:
            raise NameError('This should not happen')

    def save_id(self, id, new_id):
        if id.startswith("Q"):
            self.mapEntity[id] = str(new_id)
        elif id.startswith("P"):
            self.mapProperty[id] = str(new_id)
        else:
            raise NameError('This should not happen')

    def contains_id(self, id):
        if id.startswith("Q"):
            return id in self.mapEntity
        elif id.startswith("P"):
            return id in self.mapProperty
        else:
            print('This should not happen')
