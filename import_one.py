#configuration for pywikibot
import os
import sys
import pywikibot
from pywikibot import config2

family = 'my'
mylang = 'my'
familyfile=os.path.relpath("./config/my_family.py")
if not os.path.isfile(familyfile):
  print ("family file %s is missing" % (familyfile))
config2.register_family_file(family, familyfile)
config2.password_file = "user-password.py"
config2.usernames['my']['my'] = 'WikidataUpdater'

#connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()

#connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()

#import an item
from util.util import changeItem, changeProperty, importProperty

#import a single item or property
arg = sys.argv[1]
print(f"Importing {arg}")
if arg.startswith("Q"):
    print("before get")
    wikidata_item = pywikibot.ItemPage(wikidata_repo, arg)
    wikidata_item.get()
    print("after get")
    changeItem(wikidata_item, wikibase_repo, True)
elif arg.startswith("P"):
    wikidata_property = pywikibot.PropertyPage(wikidata_repo, arg)
    wikidata_property.get()
    changeProperty(wikidata_property, wikibase_repo, True)
