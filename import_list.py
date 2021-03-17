#configuration for pywikibot
import pywikibot

#connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

#connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()

from util.util import WikibaseImporter
wikibase_importer = WikibaseImporter(wikibase_repo,wikidata_repo)

# import a list
filepath = 'list2'
with open(filepath) as fp:
    line = fp.readline()
    while line:
        print("Importing " + line.replace("\n", ""))
        if not line.startswith("#"):
            if (line.startswith("Q")):
                wikidata_item = pywikibot.ItemPage(wikidata_repo, line)
                wikidata_item.get()
                wikibase_importer.change_item(wikidata_item, wikibase_repo, True)
            elif (line.startswith("P")):
                wikidata_property = pywikibot.PropertyPage(wikidata_repo, line)
                wikidata_property.get()
                wikibase_importer.change_property(wikidata_property, wikibase_repo, True)
        line = fp.readline()








