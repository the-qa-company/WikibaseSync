# this class makes the correspondence between Wikidata entities and entities in the Wikibase using the external
# identifier for Wikidata
from SPARQLWrapper import SPARQLWrapper, JSON


class IdSparql:
    def __init__(self, endpoint, item_identifier, property_identifier):
        self.mapEntity = {}
        self.mapProperty = {}
        self.endpoint = endpoint
        self.item_identifier = item_identifier
        self.property_identifier = property_identifier

    def load(self):
        sparql = SPARQLWrapper(self.endpoint)
        query = """
                    select ?item ?id where {
                        ?item <https://linkedopendata.eu/prop/direct/""" + self.item_identifier + """> ?id
                    }
                """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results['results']['bindings']:
            split = result['item']['value'].split('/')
            id = split[len(split)-1]
            if id.startswith('Q'):
                self.mapEntity[result['id']['value']] = id
        query = """
                            select ?item ?id where {
                                ?item <https://linkedopendata.eu/prop/direct/""" + self.property_identifier + """> ?id
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

    def get_id(self,id):
        if id.startswith("Q"):
            return self.mapEntity[id]
        elif id.startswith("P"):
            return self.mapProperty[id]
        else:
            raise NameError('This should not happen')

    def save_id(self,id,new_id):
        if id.startswith("Q"):
            self.mapEntity[id] = str(new_id)
        elif id.startswith("P"):
            self.mapProperty[id] = str(new_id)
        else:
            raise NameError('This should not happen')

    def contains_id(self,id):
        if id.startswith("Q"):
            return id in self.mapEntity
        elif id.startswith("P"):
            return id in self.mapProperty
        else:
            print('This should not happen')