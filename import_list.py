#configuration for pywikibot
import os
import sys
import pywikibot
from pywikibot import config2

from util.changes import recent_changes

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
from util.util import changeItem, changeProperty, importProperty, importItem

# import a list
filepath = 'list'
with open(filepath) as fp:
    line = fp.readline()
    while line:
        print("Importing " + line.replace("\n", ""))
        if not line.startswith("#"):
            if (line.startswith("Q")):
                wikidata_item = pywikibot.ItemPage(wikidata_repo, line)
                wikidata_item.get()
                changeItem(wikidata_item, wikibase_repo, True)
            elif (line.startswith("P")):
                wikidata_property = pywikibot.PropertyPage(wikidata_repo, line)
                wikidata_property.get()
                changeProperty(wikidata_property, wikibase_repo, True)

        line = fp.readline()








