#configuration for pywikibot
import os
import pywikibot

from util.get_wikidata_changes import get_wikidata_changes

from util.IdSparql import IdSparql
from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier
import configparser
app_config = configparser.ConfigParser()
app_config.read('config/application.config.ini')

#connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

#connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()
wikibase_repo.login()

from util.util import WikibaseImporter
wikibase_importer = WikibaseImporter(wikibase_repo,wikidata_repo)

identifier = PropertyWikidataIdentifier()
identifier.get(wikibase_repo)
print('Wikidata Item Identifier',identifier.itemIdentifier)

idSparql = IdSparql()

#grab all entities that changed
recent = get_wikidata_changes(None, 15)
for rc in recent:
    print(str(rc['title']))
    if idSparql.contains_id(str(rc['title'])):
        print("This entity ...", idSparql.get_id(str(rc['title']))," corresponding to Wikidata entity "+str(rc['title'])+" has changed and will be sync!")
        wikidata_item = pywikibot.ItemPage(wikidata_repo, str(rc['title']))
        #check if the entity has some statements
        wikibase_item = pywikibot.ItemPage(wikibase_repo, idSparql.get_id(str(rc['title'])))
        wikibase_item.get()
        count = 0
        for wikibase_claims in wikibase_item.claims:
            for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                count=count+1
        if count > 1:
            wikibase_importer.change_item(wikidata_item, wikibase_repo, True)
        else:
            print("Change only the labels")
            wikibase_importer.change_item(wikidata_item, wikibase_repo, False)
