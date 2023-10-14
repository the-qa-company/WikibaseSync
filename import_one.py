# configuration for pywikibot
import sys

from util.util import import_one

# connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

# connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()

from util.util import WikibaseImporter

wikibase_importer = WikibaseImporter(wikibase_repo, wikidata_repo)

# import a single item or property
arg = sys.argv[1]
print(f"Importing {arg}")
import_one(arg)
