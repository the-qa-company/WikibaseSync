from SPARQLWrapper import SPARQLWrapper, JSON

def retrive_eu_entities():
    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    query = query = '''
    select distinct ?item where 
    { 
      # European union and outgoing
      { 
       wd:Q458 ?p ?item .
       ?item schema:version ?value
       FILTER (STRSTARTS(STR(?p),"http://www.wikidata.org/prop/direct/"))
      }
      UNION
      # capitals
      { 
       wd:Q458 wdt:P150 ?o . ?o wdt:P36 ?item .
      } 
      UNION 
      # european institutions
      {
       ?item wdt:P31 wd:Q748720 . 
      }
      UNION
      #Parts of the commission
      {
       ?item wdt:P361 wd:Q8880 . 
      }
      UNION
      #DGs
      {
       ?item wdt:P31 wd:Q1485366 . 
      }
      UNION
      # European parliament and outgoing
      { 
       wd:Q8889 ?p ?item . 
       ?item schema:version ?value
       FILTER (STRSTARTS(STR(?p),"http://www.wikidata.org/prop/direct/"))
      }
      UNION
      # European council and outgoing
      { 
       wd:Q8886 ?p ?item .
       ?item schema:version ?value
       FILTER (STRSTARTS(STR(?p),"http://www.wikidata.org/prop/direct/"))
      }
      UNION
      # head of states of countries
      { 
        wd:Q458 wdt:P150 ?o . 
        ?o wdt:P6 ?item .
      }
      UNION
      # head of goverment of countries
      { 
        wd:Q458 wdt:P150 ?o . 
        ?o wdt:P35 ?item .
      } 
    }
    '''
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    map = set()
    for result in results['results']['bindings']:
        split = result['item']['value'].split('/')
        id = split[len(split)-1]
        if id.startswith('Q'):
            map.add(result['item']['value'].replace('http://www.wikidata.org/entity/',''))
    return map
