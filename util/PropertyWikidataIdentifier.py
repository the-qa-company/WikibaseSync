# This class generates an external identifier to Wikidata, i.e. for the entites imported from Wikidata the wikidata
# ID will be indicated
import pywikibot
import re

from pywikibot.data.api import APIError
from pywikibot.data import api


def wikiitemexists(wikibase_repo, label):
    params = {'action': 'wbsearchentities', 'format': 'json',
              'language': 'en', 'type': 'property', 'limit':1,
              'search': label}
    request = api.Request(site=wikibase_repo, parameters=params)
    result = request.submit()
    return result['search']

class PropertyWikidataIdentifier:

    def __init__(self):
        self.itemIdentifier = None
        self.propertyIdentifier = None

    def get(self, wikibase_repo):
        if len(wikiitemexists(wikibase_repo, "Wikidata QID"))>0:
            self.itemIdentifier = str(wikiitemexists(wikibase_repo, "Wikidata QID")[0]['id'])
        else:
            wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype='external-id')
            data = {}
            mylabels = {"en": "Wikidata QID"}
            mydescriptions = {"en": "Corresponding QID in Wikidata"}
            data['labels'] = mylabels
            data['descriptions'] = mydescriptions
            wikibase_item.editEntity(data, summary=u'Insert a property to have a wikidata identifier')
            self.itemIdentifier = str(wikibase_item.getID())
        if len(wikiitemexists(wikibase_repo, "Wikidata PID"))>0:
            self.propertyIdentifier = str(wikiitemexists(wikibase_repo, "Wikidata PID")[0]['id'])
        else:
            wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype='external-id')
            data = {}
            mylabels = {"en": "Wikidata PID"}
            mydescriptions = {"en": "id in wikidata of the corresponding properties"}
            data['labels'] = mylabels
            data['descriptions'] = mydescriptions
            wikibase_item.editEntity(data, summary=u'Insert a property to have a wikidata identifier')
            self.propertyIdentifier = str(wikibase_item.getID())
