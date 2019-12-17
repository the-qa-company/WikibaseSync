#This class generates an external identifier to Wikidata, i.e. for the entites imported from Wikidata the wikidata ID will be indicated
import pywikibot
import re


class PropertyWikidataIdentifier:

    def __init__(self):
        self.property = None

    def get(self, wikibase_repo):
        if self.property != None:
            return self.property
        else:
            wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype='external-id')
            try:
                mylabels = {}
                mylabels["en"] = "Wikidata ID"
                wikibase_item.editLabels(mylabels, summary=u'Insert a property to have a wikidata identifier')
                self.property = wikibase_item.getID()
                return wikibase_item
            except pywikibot.exceptions.OtherPageSaveError as e:
                print("Could not set labels of ", wikibase_item.getID())
                # this happens when a property with the same label already exists
                x = re.search("\[\[Property:.*\]\]", str(e))
                if x:
                    self.property = x.group(0).replace("[[Property:", "").split("|")[0]
                    return pywikibot.PropertyPage(wikibase_repo, x.group(0).replace("[[Property:", "").split("|")[0])
                else:
                    print("This should not happen")
