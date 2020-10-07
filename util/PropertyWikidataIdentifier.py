# This class generates an external identifier to Wikidata, i.e. for the entites imported from Wikidata the wikidata
# ID will be indicated
import pywikibot
import re

from pywikibot.data.api import APIError


class PropertyWikidataIdentifier:

    def __init__(self):
        self.itemIdentifier = None
        self.propertyIdentifier = None

    def get(self, wikibase_repo):
        wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype='external-id')
        try:
            mylabels = {"en": "Wikidata Q-ID"}
            wikibase_item.editLabels(mylabels, summary=u'Insert a property to have a wikidata identifier')
            self.itemIdentifier = str(wikibase_item.getID())
        except (APIError, pywikibot.exceptions.OtherPageSaveError) as e:
            # this happens when a property with the same label already exists
            x = re.search(r'\[\[Property:.*\]\]', str(e))
            if x:
                self.itemIdentifier = str(x.group(0).replace("[[Property:", "").split("|")[0])
            else:
                print("This should not happen 1")
        try:
            mylabels = {"en": "Wikidata P-ID"}
            wikibase_item.editLabels(mylabels, summary=u'Insert a property to have a wikidata identifier')
            self.propertyIdentifier = str(wikibase_item.getID())
        except (APIError, pywikibot.exceptions.OtherPageSaveError) as e:
            # this happens when a property with the same label already exists
            x = re.search(r'\[\[Property:.*\]\]', str(e))
            if x:
                self.propertyIdentifier = str(x.group(0).replace("[[Property:", "").split("|")[0])
            else:
                print("This should not happen 2")
