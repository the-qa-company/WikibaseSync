# this class makes the correspondence between Wikidata entities and entities in the Wikibase using the external
# identifier for Wikidata
import others_config as cf
from utilities.sparql_queries import SparqlEndPoint
from utilities import io_worker as iw


class MapperID:
    def __init__(self, item_identifier, property_identifier):
        self.mapItem = {}
        self.load_map_items(item_identifier, property_identifier)

    def load_map_items(self, item_identifier, property_identifier):
        wc_sparql = SparqlEndPoint(cf.WB_QUERY)
        kwargs_query = {
            "query": "SELECT ?item ?id {{?item wdt:%s ?id} UNION {?item wdt:%s ?id}}"
            % (item_identifier, property_identifier),
            "params": ["item", "id"],
        }
        status, responds = wc_sparql.run(**kwargs_query)
        if status == cf.StatusSPARQL.Success:
            self.mapItem = {wd_id: wb_id.split("/")[-1] for wb_id, wd_id in responds}
            iw.print_status(f"WB2WD Items: {len(self.mapItem)}")

    def get_id(self, id):
        if id.startswith("Q") or id.startswith("P"):
            return self.mapItem.get(id)
        else:
            raise KeyError

    def save_id(self, id, new_id):
        if id.startswith("Q") or id.startswith("P"):
            self.mapItem[id] = str(new_id)
        else:
            raise KeyError

    def contains_id(self, id):
        if id.startswith("Q") or id.startswith("P"):
            return id in self.mapItem
        else:
            raise KeyError
