#configuration for pywikibot
import os
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
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

sparql = SPARQLWrapper("http://query.linkedopendata.eu/bigdata/namespace/wdq/sparql")
query = """
           select distinct ?id where {
                ?s <https://linkedopendata.eu/prop/direct/P1> ?id .
                ?s ?p ?o .                                     
                FILTER(STRSTARTS(STR(?p), "https://linkedopendata.eu/prop/direct/") && ?p != <https://linkedopendata.eu/prop/direct/P1> && STRSTARTS(STR(?s), "https://linkedopendata.eu/entity/Q"))
            } order by desc(?id) offset 6489
        """
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
count = 1
for result in results['results']['bindings']:
    print(count,"/",len(results['results']['bindings']))
    count=count+1
    split = result['id']['value'].split('/')
    id = split[len(split)-1]
    print("Changing ",id)
    wikidata_item = pywikibot.ItemPage(wikidata_repo, id)
    try:
        wikidata_item.get()
        changeItem(wikidata_item, wikibase_repo, True)
    except pywikibot.exceptions.IsRedirectPage as e:
        print("THIS IS A REDIRECT PAGE "+id)
        print(e)

