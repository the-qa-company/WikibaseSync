#configuration for pywikibot
import os
import time

import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
from pywikibot import config2
import configparser
app_config = configparser.ConfigParser()
app_config.read('config/application.config.ini')


family = 'my'
mylang = 'my'
familyfile=os.path.relpath("./config/my_family.py")
if not os.path.isfile(familyfile):
  print ("family file %s is missing" % (familyfile))
config2.register_family_file(family, familyfile)
config2.password_file = "user-password.py"
config2.usernames['my']['my'] = app_config.get('wikibase', 'user')

#connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()
wikibase_repo.login()

#connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()

#import an item
from util.util import WikibaseImporter
wikibase_importer = WikibaseImporter(wikibase_repo,wikidata_repo)

sparql = SPARQLWrapper(app_config.get('wikibase', 'sparqlEndPoint'))

query = """
           # select distinct ?id where {
           #      ?s <https://linkedopendata.eu/prop/direct/P1> ?id .
           #      ?s ?p ?o .                                     
           #      FILTER(STRSTARTS(STR(?p), "https://linkedopendata.eu/prop/direct/") && ?p != <https://linkedopendata.eu/prop/direct/P1> && STRSTARTS(STR(?s), "https://linkedopendata.eu/entity/Q"))
           #  } order by desc(?id)
            SELECT ?s1 ?id WHERE {
           ?s1  <"""+app_config.get('wikibase', 'propertyUri')+"""/direct/P1>  ?id .
           {SELECT DISTINCT ?s1  WHERE {         
   ?s1  <"""+app_config.get('wikibase', 'propertyUri')+"""/P35> ?blank . ?blank <"""+app_config.get('wikibase', 'propertyUri')+"""/statement/P35> <"""+app_config.get('wikibase', 'entityUri')+"""/Q196899> .         
   ?s1  <"""+app_config.get('wikibase', 'propertyUri')+"""/direct/P1>  ?id .  
    ?s1 <"""+app_config.get('wikibase', 'propertyUri')+"""/P35> ?blank2 . ?blank2 <"""+app_config.get('wikibase', 'propertyUri')+"""/statement/P35> ?prop
 }  group by ?s1 having(count(?prop) = 1)}}

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
        wikibase_importer.change_item(wikidata_item, wikibase_repo, True)
    except pywikibot.exceptions.IsRedirectPage as e:
        print("THIS IS A REDIRECT PAGE "+id)
        time.sleep(5)
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        query = "select ?id where { <http://www.wikidata.org/entity/"+id+"> <http://www.w3.org/2002/07/owl#sameAs> ?id . }"
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        new_results = sparql.query().convert()
        for new_result in new_results['results']['bindings']:
            newId = new_result['id']['value'].replace("http://www.wikidata.org/entity/","")
            print("SEARCHING THE NEW ID ",newId)
            wikidata_item = pywikibot.ItemPage(wikidata_repo, newId)
            try:
                wikidata_item.get()
                wikibase_importer.change_item_given_id(wikidata_item, result['s1']['value'].replace("https://linkedopendata.eu/entity/",""), wikibase_repo, True)
            except pywikibot.exceptions.IsRedirectPage as e:
                print("THIS SHOULD NOT HAPPEN")

