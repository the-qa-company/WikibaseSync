import re
from decimal import Decimal

import pywikibot
from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier
from util.IdSparql import IdSparql

languages = ["bg","cs","da","de","el","en","es","et","fi","fr","ga","hr","hu","it","lb","lt","lv","mt","nl","pl","pt","ro","sk","sl","sv","tr"]



wikidata = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata.data_repository()

wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()

#find the external identifier for wikidata
property_wikidata_identifier = PropertyWikidataIdentifier()
wikidata_identifier = property_wikidata_identifier.get(wikibase_repo)
print('wikidata_identifier',wikidata_identifier)

endpoint = "http://localhost:8989/bigdata/namespace/wdq/sparql"
id = IdSparql(endpoint, wikidata_identifier)
id.load()

#comparing the labels
def diffLabels(wikidata_item,wikibase_item):
    mylabels = {}
    for label in wikidata_item.labels:
        if label in languages:
        #if label != "nqo":
            if wikibase_item.getID() != str(-1) and label in wikibase_item.labels:
                if not (wikidata_item.labels.get(label) == wikibase_item.labels.get(label)):
                    #print("Change", wikidata_item.labels.get(label), "----", wikibase_item.labels.get(label))
                    mylabels[label] = wikidata_item.labels.get(label).replace("\'"," ")
            else:
                mylabels[label] = wikidata_item.labels.get(label).replace("\'"," ")
    return mylabels

def changeLabels(wikidata_item, wikibase_item):
    mylabels = diffLabels(wikidata_item,wikibase_item)
    if len(mylabels) != 0:
        print("Import labels")
        # wikibase_item.editLabels(mylabels, summary=u'Label in wikidata changed')
        try:
            wikibase_item.editLabels(mylabels, summary=u'Label in wikidata changed')
            return wikibase_item.getID()
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("Could not set labels of ", wikibase_item.getID())
            print(e)
            # this happens when a property with the same label already exists
            x = re.search("\[\[Property:.*\]\]", str(e))
            if x:
                return x.group(0).replace("[[Property:", "").split("|")[0]
            else:
                print("This should not happen")


# comparing the descriptions
def diffDescriptions(wikidata_item, wikibase_item):
    myDescriptions = {}
    for description in wikidata_item.descriptions:
        if description in languages:
            if wikibase_item.getID() != str(-1) and description in wikibase_item.descriptions:
                if not (wikidata_item.descriptions.get(description) == wikibase_item.descriptions.get(description)):
                    #print("Change", wikidata_item.descriptions.get(description), "----", wikibase_item.descriptions.get(description))
                    myDescriptions[description] = wikidata_item.descriptions.get(description)
            else:
                myDescriptions[description] = wikidata_item.descriptions.get(description)
    return myDescriptions

# comparing the descriptions
def changeDescriptions(wikidata_item, wikibase_item):
    myDescriptions = diffDescriptions(wikidata_item,wikibase_item)
    if len(myDescriptions) != 0:
        print("Import Descriptions")
        try:
            wikibase_item.editDescriptions(myDescriptions, summary=u'Description in wikidata changed')
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("Could not set description of ", wikibase_item.getID())
            print(e)
            x = re.search("\[\[Item:.*\]\]", str(e))
            if x:
                return x.group(0).replace("[[Item:", "").split("|")[0]
            else:
                print("This should not happen")
            print("Error probably property or item already existing ", e)


# diff the aliases
def diffAliases(wikidata_item,wikibase_item):
    mylabels = {}
    for alias in wikidata_item.aliases:
        if alias in languages:
            if wikibase_item.getID() != str(-1) and alias in wikibase_item.aliases:
                if not (wikidata_item.aliases.get(alias) == wikibase_item.aliases.get(alias)):
                    #print("Change", wikidata_item.aliases.get(alias), "----", wikibase_item.aliases.get(alias))
                    mylabels[alias] = wikidata_item.aliases.get(alias)
            else:
                mylabels[alias] = wikidata_item.aliases.get(alias)
    return mylabels


# comparing the aliases
def changeAliases(wikidata_item,wikibase_item):
    myaliases = diffAliases(wikidata_item,wikibase_item)
    if len(myaliases) != 0:
        print("Import aliases")
        try:
            wikibase_item.editAliases(myaliases, summary=u'Aliases in wikidata changed')
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("This should not happen ",e)


# comparing the sitelinks
def diffSiteLinks(wikidata_item, wikibase_item):
    siteLinks = []
    id = wikibase_item.getID()
    for sitelink in wikidata_item.sitelinks:
        for lang in languages:
            if str(sitelink) == lang+"wiki":
                if id != str(-1) and sitelink in wikibase_item.sitelinks:
                    if not (str(wikidata_item.sitelinks.get(sitelink)) == str(wikibase_item.sitelinks.get(sitelink))):
                        # print("Change", wikidata_item.sitelinks.get(sitelink), "----", wikibase_item.sitelinks.get(sitelink))
                        siteLinks.append({'site': sitelink, 'title': str(wikidata_item.sitelinks.get(sitelink)).replace('[[','').replace(']]','')})
                else:
                    #print("Change", wikidata_item.sitelinks.get(sitelink), "----", wikibase_item.sitelinks.get(sitelink))
                    siteLinks.append({'site': sitelink, 'title': str(wikidata_item.sitelinks.get(sitelink)).replace('[[','').replace(']]','')})
    return siteLinks

# comparing the sitelinks
def changeSiteLinks(wikidata_item, wikibase_item):
    siteLinks = diffSiteLinks(wikidata_item, wikibase_item)
    if len(siteLinks) != 0:
        print("Import sitelinks")
        try:
            wikibase_item.setSitelinks(siteLinks, summary=u'Sitelinks in wikidata changed')
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("Could not set sitelinks of ", wikibase_item.getID())
            print(e)
        except pywikibot.exceptions.UnknownSite as e:
            print("Could not set sitelinks of ", wikibase_item.getID())
            print(e)

def importEntity(wikidata_item, wikibase_item):
    mylabels = diffLabels(wikidata_item, wikibase_item)
    myDescriptions = diffDescriptions(wikidata_item, wikibase_item)
    myaliases = diffAliases(wikidata_item, wikibase_item)
    mySitelinks = diffSiteLinks(wikidata_item, wikibase_item)
    claim = pywikibot.page.Claim(wikibase_repo, wikidata_identifier.getID(), datatype='external-id')
    target = wikidata_item.getID()
    claim.setTarget(target)
    data = {
        'labels': mylabels,
        'descriptions': myDescriptions,
        'aliases': myaliases,
        'sitelinks': mySitelinks,
        'claims': [claim.toJSON()]
           }
    try:
        wikibase_item.editEntity(data, summary=u'Importing new entity')
        id.save_id(wikidata_item.getID(), wikibase_item.getID())
        return wikibase_item.getID()
    except pywikibot.exceptions.OtherPageSaveError as e:
        print("Could not set description of ", wikibase_item.getID())
        print("This is the error message ",e)
        x = re.search("\[\[Item:.*\]\]", str(e))
        if x:
            return x.group(0).replace("[[Item:", "").split("|")[0]
        else:
            print("This should not happen")
        print("Error probably property or item already existing ", e)

def importProperty(wikidata_item, wikibase_item):
    mylabels = diffLabels(wikidata_item, wikibase_item)
    myDescriptions = diffDescriptions(wikidata_item, wikibase_item)
    myaliases = diffAliases(wikidata_item, wikibase_item)
    claim = pywikibot.page.Claim(wikibase_repo, wikidata_identifier.getID(), datatype='external-id')
    target = wikidata_item.getID()
    claim.setTarget(target)

    data = {
        'labels': mylabels,
        'descriptions': myDescriptions,
        'aliases': myaliases,
        'claims': [claim.toJSON()]
           }
    try:
        wikibase_item.editEntity(data, summary=u'Importing new entity')
        id.save_id(wikidata_item.getID(), wikibase_item.getID())
        return wikibase_item.getID()
    except pywikibot.exceptions.OtherPageSaveError as e:
        print("Could not set description of ", wikibase_item.getID())
        print(e)
        x = re.search("\[\[Item:.*\]\]", str(e))
        if x:
            return x.group(0).replace("[[Item:", "").split("|")[0]
        else:
            print("This should not happen")
        print("Error probably property or item already existing ", e)






# comparing two claims
def compare_claim(wikidata_claim, wikibase_claim):
    found = False
    found_equal_value = False
    wikidata_propertyId = wikidata_claim.get('property')
    # WIKIBASE_ITEM
    if wikidata_claim.get('datatype') == 'wikibase-item':
        if wikibase_claim.get('datatype') == 'wikibase-item':
            wikidata_objectId = 'Q' + str(
                wikidata_claim.get('datavalue').get('value').get('numeric-id'))
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_objectId = 'Q' + str(
                wikibase_claim.get('datavalue').get('value').get('numeric-id'))
            # print(id.get_id(wikidata_propertyId),"---", wikibase_propertyId)
            # print(id.get_id(wikidata_objectId),"---",wikibase_objectId)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if id.contains_id(wikidata_objectId) and id.get_id(
                    wikidata_objectId) == wikibase_objectId:
                    found_equal_value = True
    # MONOLINGUALTEXT
    elif wikidata_claim.get('datatype') == 'monolingualtext':
        if wikibase_claim.get('datatype') == 'monolingualtext':
            wikibase_propertyId = wikibase_claim.get('property')

            wikibase_text = wikibase_claim.get('datavalue').get('value').get(
                'text')
            wikibase_language = wikibase_claim.get('datavalue').get(
                'value').get('language')

            wikidata_text = wikidata_claim.get('datavalue').get('value').get(
                'text')
            wikidata_language = wikidata_claim.get('datavalue').get(
                'value').get('language')

            # if wikibase_propertyId == "P8":
            #     print(wikibase_propertyId)
            #     print(wikibase_text , "---", wikidata_text)
            #     print(wikibase_language, "---", wikidata_language)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_text == wikidata_text and wikibase_language == wikidata_language:
                    found_equal_value = True
    # COMMONS-MEDIA
    elif wikidata_claim.get('datatype') == 'commonsMedia':
        if wikibase_claim.get('datatype') == 'commonsMedia':
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_text = wikibase_claim.get('datavalue').get('value')
            wikidata_text = wikidata_claim.get('datavalue').get('value')
            # print(id.get_id(wikidata_propertyId),'--',wikibase_propertyId,'--',wikibase_text==wikidata_text,'--',wikibase_language==wikidata_language)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_text == wikidata_text:
                    found_equal_value = True
    # GLOBAL-COORDINATE
    elif wikidata_claim.get('datatype') == 'globe-coordinate':
        if wikibase_claim.get('datatype') == 'globe-coordinate':
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_latitude = wikibase_claim.get('datavalue').get(
                'value').get('latitude')
            wikibase_longitude = wikibase_claim.get('datavalue').get(
                'value').get('longitude')
            wikibase_altitude = wikibase_claim.get('datavalue').get(
                'value').get('altitude')
            wikibase_precision = wikibase_claim.get('datavalue').get(
                'value').get('precision')
            wikibase_globe = wikibase_claim.get('datavalue').get('value').get(
                'globe')
            wikidata_latitude = wikidata_claim.get('datavalue').get(
                'value').get('latitude')
            wikidata_longitude = wikidata_claim.get('datavalue').get(
                'value').get('longitude')
            wikidata_altitude = wikidata_claim.get('datavalue').get(
                'value').get('altitude')
            wikidata_precision = wikidata_claim.get('datavalue').get(
                'value').get('precision')
            wikidata_globe = wikidata_claim.get('datavalue').get('value').get(
                'globe')
            if id.get_id(
                    wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_latitude == wikidata_latitude and wikibase_longitude == wikidata_longitude and wikibase_globe == wikidata_globe\
                        and wikibase_altitude == wikidata_altitude and wikibase_precision == wikidata_precision :
                    found_equal_value = True
    # QUANTITY
    elif wikidata_claim.get('datatype') == 'quantity':
        if wikibase_claim.get('datatype') == 'quantity':
            wikibase_propertyId = wikibase_claim.get('property')

            wikibase_amount = wikibase_claim.get('datavalue').get('value').get(
                'amount')
            wikibase_upperBound = wikibase_claim.get('datavalue').get(
                'value').get('upperBound')
            wikibase_lowerBound = wikibase_claim.get('datavalue').get(
                'value').get('lowerBound')
            wikibase_unit = wikibase_claim.get('datavalue').get('value').get(
                'unit')

            wikidata_amount = wikidata_claim.get('datavalue').get('value').get(
                'amount')
            wikidata_upperBound = wikidata_claim.get('datavalue').get(
                'value').get('upperBound')
            wikidata_lowerBound = wikidata_claim.get('datavalue').get(
                'value').get('lowerBound')
            wikidata_unit = wikidata_claim.get('datavalue').get('value').get(
                'unit')
            # print("Compare")
            # print(wikibase_amount, "--", wikidata_amount)
            # print(wikibase_upperBound, "--", wikidata_upperBound)
            # print(wikibase_lowerBound, "--", wikidata_lowerBound)
            # print(wikibase_unit, "--", wikidata_unit)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_amount == wikidata_amount and wikibase_upperBound == wikidata_upperBound and wikibase_lowerBound == wikidata_lowerBound:
                    if (wikidata_unit == None and wikibase_unit == None) or (wikidata_unit == '1' and  wikibase_unit == '1'):
                        found_equal_value = True
                    else:
                        if ("entity/" in wikidata_unit) and ("entity/" in wikibase_unit) :
                            unit_id = wikibase_unit.split("entity/")[1]
                            wikidata_unit_id = wikidata_unit.split("entity/")[1]
                            if id.contains_id(wikidata_unit_id) and id.get_id(wikidata_unit_id) == unit_id:
                                found_equal_value = True

    # TIME
    elif wikidata_claim.get('datatype') == 'time':
        if wikibase_claim.get('datatype') == 'time':

            wikibase_propertyId = wikibase_claim.get('property')

            wikidata_time = wikidata_claim.get('datavalue').get('value').get('time')
            wikidata_precision = wikidata_claim.get('datavalue').get('value').get(
                'precision')
            wikidata_after = wikidata_claim.get('datavalue').get('value').get(
                'after')
            wikidata_before = wikidata_claim.get('datavalue').get('value').get(
                'before')
            wikidata_timezone = wikidata_claim.get('datavalue').get('value').get(
                'timezone')
            wikidata_calendermodel = wikidata_claim.get('datavalue').get(
                'value').get(
                'calendarmodel')

            wikibase_time = wikibase_claim.get('datavalue').get('value').get('time')
            wikibase_precision = wikibase_claim.get('datavalue').get('value').get(
                'precision')
            wikibase_after = wikibase_claim.get('datavalue').get('value').get(
                'after')
            wikibase_before = wikibase_claim.get('datavalue').get('value').get(
                'before')
            wikibase_timezone = wikibase_claim.get('datavalue').get('value').get(
                'timezone')
            wikibase_calendermodel = wikibase_claim.get('datavalue').get(
                'value').get(
                'calendarmodel')

            # print(wikidata_time , "---" , wikibase_time)
            # print(wikidata_precision , "---" , wikibase_precision)
            # print(wikidata_after , "---" , wikibase_after)
            # print(wikidata_before , "---" , wikibase_before)
            # print(wikidata_timezone , "---" , wikibase_timezone)
            # print(wikidata_calendermodel , "---" , wikibase_calendermodel)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikidata_time == wikibase_time and wikidata_precision == wikibase_precision and wikidata_after == wikibase_after and wikidata_before == wikibase_before and wikidata_timezone == wikibase_timezone \
                        and wikidata_calendermodel == wikibase_calendermodel:
                        found_equal_value = True

    # URL
    elif wikidata_claim.get('datatype') == 'url':
        if wikibase_claim.get('datatype') == 'url':
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_value = wikibase_claim.get('datavalue').get(
                'value')

            wikidata_value = wikidata_claim.get('datavalue').get(
                'value')
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_value == wikidata_value:
                    found_equal_value = True
    # STRING
    elif wikidata_claim.get('datatype') == 'string':
        if wikibase_claim.get('datatype') == 'string':
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_value = wikibase_claim.get('datavalue').get(
                'value')
            wikidata_value = wikidata_claim.get('datavalue').get(
                'value')
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                # print(wikibase_value , " --- ", wikidata_value)
                if wikibase_value == wikidata_value:
                    found_equal_value = True
    # EXTERNAL ID
    elif wikidata_claim.get('datatype') == 'external-id':
        if wikibase_claim.get('datatype') == 'external-id':
            wikibase_propertyId = wikibase_claim.get('property')

            wikibase_value = wikibase_claim.get('datavalue').get(
                'value')
            wikibase_type = wikibase_claim.get('datavalue').get(
                'type')

            wikidata_value = wikidata_claim.get('datavalue').get(
                'value')
            wikidata_type = wikidata_claim.get('datavalue').get(
                'type')
            # print(wikidata_propertyId)
            # if wikidata_propertyId == "P523":
            # print(wikibase_value, " --- ", wikidata_value)
            # print(wikibase_type, " --- ", wikidata_type)
            # print(id.get_id(wikidata_propertyId), " --- ", wikibase_propertyId)
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_value == wikidata_value and wikibase_type == wikidata_type:
                    found_equal_value = True
    # GEOSHAPE
    elif wikidata_claim.get('datatype') == 'geo-shape':
        if wikibase_claim.get('datatype') == 'geo-shape':
            wikibase_propertyId = wikibase_claim.get('property')
            wikibase_value = wikibase_claim.get('datavalue').get('value')
            wikidata_value = wikidata_claim.get('datavalue').get('value')
            if id.get_id(wikidata_propertyId) == wikibase_propertyId:
                found = True
                if wikibase_value == wikidata_value:
                    found_equal_value = True
    # TABULAR-DATA
    elif wikidata_claim.get('datatype') == 'tabular-data':
        print('tabular-data')
        #raise NameError('Tabluar data not implemented')
        # set new claim
        # claim = pywikibot.page.Claim(
        #     testsite, 'P30175', datatype='tabular-data')
        # commons_site = pywikibot.Site('commons', 'commons')
        # page = pywikibot.Page(commons_site, 'Data:Bea.gov/GDP by state.tab')
        # target = pywikibot.WbGeoShape(page)
        # claim.setTarget(target)
        # item.addClaim(claim)
    else:
        print('This datatype is not supported ',wikidata_claim.get('datatype'))
    return found, found_equal_value

# translate one claim from wikidata in one of wikibase
def translateClaim(wikidata_claim):
    wikidata_propertyId = wikidata_claim.get('property')
    if not id.contains_id(wikidata_propertyId):
        print("Not Found")
        wikidata_property = pywikibot.PropertyPage(wikidata_repo, wikidata_propertyId,
                                                   datatype=wikidata_claim.get('datatype'))
        wikidata_property.get()
        wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype=wikidata_property.type)
        importProperty(wikidata_property, wikibase_item)
    # WIKIBASE-ITEM
    if wikidata_claim.get('datatype') == 'wikibase-item':
        # add the entity to the wiki
        wikidata_objectId = 'Q' + str(
            wikidata_claim.get('datavalue').get('value').get('numeric-id'))
        if not id.contains_id(wikidata_objectId):
            item = pywikibot.ItemPage(wikidata_repo, wikidata_objectId)
            changeItem(item, wikibase_repo, False)
        if id.contains_id(wikidata_objectId) and (not id.get_id(wikidata_objectId) == '-1'):
            claim = pywikibot.Claim(wikibase_repo, id.get_id(wikidata_propertyId), datatype='wikibase-item')
            object = pywikibot.ItemPage(wikibase_repo, id.get_id(wikidata_objectId))
            claim.setTarget(object)
            claim.setRank(wikidata_claim.get('rank'))
            return claim

    # MONOLINGUALTEXT
    elif wikidata_claim.get('datatype') == 'monolingualtext':
        claim = pywikibot.Claim(wikibase_repo, id.get_id(wikidata_propertyId), datatype='monolingualtext')
        wikidata_text = wikidata_claim.get('datavalue').get('value').get('text')
        wikidata_language = wikidata_claim.get('datavalue').get('value').get('language')
        #HACK
        if wikidata_language in languages:
            # print(wikidata_text, "---", wikidata_language)
            target = pywikibot.WbMonolingualText(text=wikidata_text, language=wikidata_language)
            claim.setTarget(target)
            claim.setRank(wikidata_claim.get('rank'))
            return claim
        else:
            return None
    # GLOBE-COORDINATES
    elif wikidata_claim.get('datatype') == 'globe-coordinate':
        wikidata_latitude = wikidata_claim.get('datavalue').get('value').get('latitude')
        wikidata_longitude = wikidata_claim.get('datavalue').get('value').get('longitude')
        wikidata_altitude = wikidata_claim.get('datavalue').get('value').get('altitude')
        wikidata_globe_uri = wikidata_claim.get('datavalue').get('value').get(
            'globe').replace("http://www.wikidata.org/entity/", "")
        wikidata_precision = wikidata_claim.get('datavalue').get('value').get('precision')
        wikidata_globe_item = pywikibot.ItemPage(wikidata_repo, wikidata_globe_uri)
        wikidata_globe_item.get()
        wikibase_globe_item = changeItem(wikidata_globe_item, wikibase_repo, False)

        ##Note: picking as globe wikidata item for earth, this is the standard in a wikibase even if the entity does not exist
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='globe-coordinate')
        if wikidata_precision!= None:
            target = pywikibot.Coordinate(site=wikibase_repo, lat=wikidata_latitude, lon=wikidata_longitude,
                                          alt=wikidata_altitude,
                                          globe_item="http://www.wikidata.org/entity/Q2",
                                          precision=wikidata_precision
                                          )
        else:
            target = pywikibot.Coordinate(site=wikibase_repo, lat=wikidata_latitude, lon=wikidata_longitude,
                                          alt=wikidata_altitude,
                                          globe_item="http://www.wikidata.org/entity/Q2",
                                          precision = 1
                                          )
        # print(wikidata_propertyId)
        # print("Property ",id.get_id(wikidata_propertyId))
        # print("My traget ",target)
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # TIME
    elif wikidata_claim.get('datatype') == 'time':
        wikidata_time = wikidata_claim.get('datavalue').get('value').get('time')
        wikidata_precision = wikidata_claim.get('datavalue').get('value').get(
            'precision')
        wikidata_after = wikidata_claim.get('datavalue').get('value').get(
            'after')
        wikidata_before = wikidata_claim.get('datavalue').get('value').get(
            'before')
        wikidata_timezone = wikidata_claim.get('datavalue').get('value').get(
            'timezone')
        wikidata_calendermodel = wikidata_claim.get('datavalue').get('value').get(
            'calendarmodel')

        ##Note: picking as claender wikidata, this is the standard in a wikibase even if the entity does not exist
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='time')
        target = pywikibot.WbTime.fromTimestr(site=wikibase_repo, datetimestr=wikidata_time,
                                              precision=wikidata_precision,
                                              after=wikidata_after, before=wikidata_before, timezone=wikidata_timezone,
                                              calendarmodel=wikidata_calendermodel)
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))

        return claim
    # COMMONSMEDIA
    elif wikidata_claim.get('datatype') == 'commonsMedia':
        claim = pywikibot.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                datatype='commonsMedia')
        wikidata_text = wikidata_claim.get('datavalue').get('value')
        commonssite = pywikibot.Site('commons', 'commons')
        imagelink = pywikibot.Link(wikidata_text, source=commonssite,
                                   default_namespace=6)
        image = pywikibot.FilePage(imagelink)
        if image.isRedirectPage():
            image = pywikibot.FilePage(image.getRedirectTarget())

        if not image.exists():
            pywikibot.output("{} doesn't exist so I can't link to it"
                             .format(image.title(as_link=True)))
            return

        claim.setTarget(image)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # QUANTITY
    elif wikidata_claim.get('datatype') == 'quantity':
        wikidata_amount = wikidata_claim.get('datavalue').get('value').get('amount')
        wikidata_upperBound = wikidata_claim.get('datavalue').get('value').get(
            'upperBound')
        wikidata_lowerBound = wikidata_claim.get('datavalue').get('value').get(
            'lowerBound')
        wikidata_unit = wikidata_claim.get('datavalue').get('value').get('unit')
        wikidata_objectId = wikidata_unit.replace("http://www.wikidata.org/entity/", "")
        # add unit if not in the wiki
        if not (wikidata_unit == None or wikidata_unit == '1'):
            if not id.contains_id(wikidata_objectId):
                item = pywikibot.ItemPage(wikidata_repo, wikidata_objectId)
                changeItem(item, wikibase_repo, False)
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='quantity')
        # print(wikidata_amount)
        # print(wikidata_upperBound)
        # print(Decimal(wikidata_upperBound)-Decimal(wikidata_amount))
        if wikidata_unit == None or wikidata_unit == '1':
            if wikidata_upperBound == None:
                target = pywikibot.WbQuantity(amount=wikidata_amount, site=wikibase_repo)
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            else:
                target = pywikibot.WbQuantity(amount=wikidata_amount, site=wikibase_repo,
                                              error=Decimal(wikidata_upperBound) - Decimal(wikidata_amount))
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
        else:
            if (not id.get_id(wikidata_objectId) == '-1'):
                if wikidata_upperBound == None:
                    wikibase_unit = pywikibot.ItemPage(wikibase_repo, id.get_id(wikidata_objectId))
                    #here this is a hack .......
                    target = pywikibot.WbQuantity(amount=wikidata_amount, unit=wikibase_unit,
                                                  site=wikibase_repo)
                    claim.setTarget(target)
                    claim.setRank(wikidata_claim.get('rank'))
                else:
                    wikibase_unit = pywikibot.ItemPage(wikibase_repo, id.get_id(wikidata_objectId))
                    target = pywikibot.WbQuantity(amount=wikidata_amount, unit=wikibase_unit,
                                                  site=wikibase_repo,
                                                  error = Decimal(wikidata_upperBound) - Decimal(wikidata_amount))
                    claim.setTarget(target)
                    claim.setRank(wikidata_claim.get('rank'))
                return claim
    # URL
    elif wikidata_claim.get('datatype') == 'url':
        wikidata_value = wikidata_claim.get('datavalue').get('value')
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='url')
        target = wikidata_value
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # EXTERNAL-ID
    elif wikidata_claim.get('datatype') == 'external-id':
        wikidata_value = wikidata_claim.get('datavalue').get('value')
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='external-id')
        target = wikidata_value
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # STRING
    elif wikidata_claim.get('datatype') == 'string':
        wikidata_value = wikidata_claim.get('datavalue').get('value')
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId),
                                     datatype='string')
        target = wikidata_value
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # GEOSHAPE
    elif wikidata_claim.get('datatype') == 'geo-shape':
        claim = pywikibot.page.Claim(wikibase_repo, id.get_id(wikidata_propertyId), datatype='geo-shape')
        commons_site = pywikibot.Site('commons', 'commons')
        page = pywikibot.Page(commons_site, wikidata_claim.get('datavalue').get('value'))
        target = pywikibot.WbGeoShape(page)
        claim.setTarget(target)
        claim.setRank(wikidata_claim.get('rank'))
        return claim
    # TABULAR-DATA
    elif wikidata_claim.get('datatype') == 'tabular-data':
        print(wikidata_claim)
        return None
        print('Not implemented yet tabular-data')
        #raise NameError('Tabluar data not implemented')
        # set new claim
        # claim = pywikibot.page.Claim(
        #     testsite, 'P30175', datatype='tabular-data')
        # commons_site = pywikibot.Site('commons', 'commons')
        # page = pywikibot.Page(commons_site, 'Data:Bea.gov/GDP by state.tab')
        # target = pywikibot.WbGeoShape(page)
        # claim.setTarget(target)
        # item.addClaim(claim)
    elif wikidata_claim.get('datatype') == 'wikibase-property':
        print('Not implemented yet wikibase-property')
    else:
        print('This datatype is not supported ',wikidata_claim.get('datatype'), ' translating the following claim ',wikidata_claim)
        return None


# comparing two claims together with their qualifiers and references
def compare_claim_with_qualifiers_and_references(wikidata_claim, wikibase_claim):
    # compare mainsnak
    found = False
    found_equal_value = False
    (claim_found, claim_found_equal_value) = compare_claim(wikidata_claim.get('mainsnak'),wikibase_claim.get('mainsnak'))
    # compare qualifiers
    qualifiers_equal = True
    if ('qualifiers' in wikidata_claim) and ('qualifiers' in wikibase_claim):
        for q1 in wikidata_claim.get('qualifiers'):
            for q_wikidata in wikidata_claim.get('qualifiers').get(q1):
                qualifier_equal = False
                # print("Passing here .... ", q_wikidata)
                # print(qualifier_equal)
                for q2 in wikibase_claim.get('qualifiers'):
                    for q_wikibase in wikibase_claim.get('qualifiers').get(q2):
                        wikidata_propertyId = q_wikidata.get('property')
                        if id.contains_id(wikidata_propertyId):
                            (qualifier_claim_found, qualifier_claim_found_equal_value) = compare_claim(q_wikidata, q_wikibase)

                            if qualifier_claim_found_equal_value == True:
                                qualifier_equal = True
                if qualifier_equal == False:
                    qualifiers_equal = False
                # print("Check now 2 ",qualifiers_equal)
    if ('qualifiers' in wikidata_claim and not('qualifiers' in wikibase_claim) or (not 'qualifiers' in wikidata_claim) and 'qualifiers' in wikibase_claim):
        qualifiers_equal = False
    # print("qualifiers_equal",qualifiers_equal)
    # compare references
    references_equal = True

    # print(wikidata_claim.get('references'))
    # print(wikibase_claim.get('references'))
    if ('references' in wikidata_claim) and ('references' in wikibase_claim):
        # print(len(wikidata_claim.get('references')))
        # print()
        # print(len(wikibase_claim.get('references')))
        #if len(wikidata_claim.get('references')) == len(wikibase_claim.get('references')):
            for i in range(0,len(wikidata_claim.get('references'))):
                for q1 in wikidata_claim.get('references')[i].get('snaks'):
                    for q_wikidata in wikidata_claim.get('references')[i].get('snaks').get(q1):
                        reference_equal = False
                        for snak in wikibase_claim.get('references'):
                            for q2 in snak.get('snaks'):
                                for q_wikibase in snak.get('snaks').get(q2):
                                    wikidata_propertyId = q_wikidata.get('property')
                                    if id.contains_id(wikidata_propertyId):
                                        # print("Two Qualifiers")
                                        # print("q_wikidata",q_wikidata)
                                        # print("q_wikibase",q_wikibase)
                                        (references_claim_found, references_claim_found_equal_value) = compare_claim(q_wikidata,
                                                                                               q_wikibase)
                                        # print("qualifier_claim_found_equal_value", references_claim_found_equal_value)
                                        if references_claim_found_equal_value == True:
                                            # print("Enter here ....")
                                            reference_equal = True
                        if reference_equal == False:
                            references_equal = False
        # else:
        #     references_equal = False
    if ('references' in wikidata_claim and not('references' in wikibase_claim)) or (not('references' in wikidata_claim) and 'references' in wikibase_claim):
        references_equal = False
    # print("references_equal", references_equal)
    if claim_found_equal_value and qualifiers_equal and references_equal and wikidata_claim.get('rank') ==  wikidata_claim.get('rank'):
        found_equal_value = True
    return claim_found, found_equal_value


# change the claims
def changeClaims(wikidata_item,wikibase_item):
    # check which claims are in wikibase and in wikidata with the same property but different value, and delete them
    claimsToRemove = []
    for wikibase_claims in wikibase_item.claims:
        for wikibase_c in wikibase_item.claims.get(wikibase_claims):
            alreadyFound = False
            wikibase_claim = wikibase_c.toJSON()
            wikibase_propertyId = wikibase_claim.get('mainsnak').get('property')
            found = False
            found_equal_value = False
            for claims in wikidata_item.claims:
                for c in wikidata_item.claims.get(claims):
                    wikidata_claim = c.toJSON()
                    wikidata_propertyId = wikidata_claim.get('mainsnak').get('property')
                    # if the property is not there then they cannot be at the same time in wikibase and wikidata
                    if id.contains_id(wikidata_propertyId):
                        if id.get_id(wikidata_propertyId) == wikibase_propertyId:

                            # if wikidata_propertyId == 'P2884':

                                #if id.get_id(wikidata_propertyId) == 'P194' and wikidata_propertyId == "P530":
                                # print(wikidata_claim,"---",wikibase_claim)
                                (found_here, found_equal_value_here) = compare_claim_with_qualifiers_and_references(wikidata_claim,wikibase_claim)
                                # print(found_here,found_equal_value_here)
                                if found_here == True:
                                    found = True
                                if found_equal_value == True and found_equal_value_here==True:
                                    alreadyFound = True
                                if found_equal_value_here == True:
                                    found_equal_value = True


            if found == True and found_equal_value == False:
                claimsToRemove.append(wikibase_c)
                print("This claim is deleted ",wikibase_claim)
            if alreadyFound == True:
                claimsToRemove.append(wikibase_c)
                print("This claim is deleted it's a duplicate", wikibase_claim)
    if len(claimsToRemove)>0:
        for claimsToRemoveChunk in chunks(claimsToRemove,50):
            print("Problematic chunk",claimsToRemoveChunk)
            wikibase_item.removeClaims(claimsToRemoveChunk)
    print("Claims to remove ",claimsToRemove)
    #check which claims are in wikidata and not in wikibase and import them
    #refetch the wikibase entity since some statements may hav been deleted
    wikibase_item = pywikibot.ItemPage(wikibase_repo, wikibase_item.getID())
    wikibase_item.get()
    newClaims = []
    for claims in wikidata_item.claims:
        for c in wikidata_item.claims.get(claims):
            wikidata_claim = c.toJSON()
            found_equal_value = False
            wikidata_propertyId = wikidata_claim.get('mainsnak').get('property')

            #this is the property for duplicate items
            # if  wikidata_propertyId == "P2884":
                #print("Want to import this ",wikidata_claim)
            for wikibase_claims in wikibase_item.claims:
                for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                    wikibase_claim = wikibase_c.toJSON()
                    wikibase_propertyId = wikibase_claim.get('mainsnak').get('property')
                    #if wikibase_propertyId == "P76":
                    # if the property is not there then it cannot be in the wikibase
                    if id.contains_id(wikidata_propertyId):
                        (claim_found, claim_found_equal_value) = compare_claim_with_qualifiers_and_references(wikidata_claim, wikibase_claim)
                        if (claim_found_equal_value == True):
                            found_equal_value = True
            #print(found_equal_value)
            if found_equal_value == False:
                #print("This claim is added ", wikidata_claim)
                #import the property if it does not exist
                if wikidata_claim.get('mainsnak').get('snaktype') == 'value':
                    # the claim is added
                    claim = translateClaim(wikidata_claim.get('mainsnak'))
                    if claim is not None:
                        if 'qualifiers' in wikidata_claim:
                            for key in wikidata_claim.get('qualifiers'):
                                for old_qualifier in wikidata_claim.get('qualifiers').get(key):
                                    new_qualifier = translateClaim(old_qualifier)
                                    if new_qualifier != None:
                                        claim.addQualifier(new_qualifier)
                        if 'references' in wikidata_claim:
                                for snak in wikidata_claim.get('references'):
                                    for key in snak.get('snaks'):
                                        new_references = []
                                        for old_reference in snak.get('snaks').get(key):
                                            # print('old',old_reference)
                                            new_reference = translateClaim(old_reference)
                                            #this can happen if the object entity has no label in any given language
                                            if new_reference != None:
                                                new_references.append(new_reference)
                                        if len(new_references)>0:
                                            claim.addSources(new_references)
                        newClaims.append(claim.toJSON())
                    else:
                        print('The translated claim is None ', wikidata_claim.get('mainsnak'))
                elif wikidata_claim.get('mainsnak').get('snaktype') == 'novalue':
                    print("Claims with no value not implemented yet")
                else:
                        print('This should not happen ',wikidata_claim.get('mainsnak'))
    data = {}
    data['claims'] = newClaims
    print(data)
    wikibase_item.editEntity(data)




def wikidata_link(wikibase_item, wikidata_item):
    # make a link to wikidata if it does not exist
    found = False
    if hasattr(wikibase_item, "claims"):
        for wikibase_claims in wikibase_item.claims:
            for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                wikibase_claim = wikibase_c.toJSON()
                wikibase_propertyId = wikibase_claim.get('mainsnak').get('property')
                if wikibase_propertyId == wikidata_identifier.getID():
                    found = True
    if found == False:
        claim = pywikibot.page.Claim(wikibase_repo, wikidata_identifier.getID(), datatype='external-id')
        target = wikidata_item.getID()
        claim.setTarget(target)
        wikibase_item.addClaim(claim)


def changeItem(wikidata_item,wikibase_repo,statements):
    wikibase_item = None

    try:
        item = wikidata_item.get()
    except pywikibot.exceptions.UnknownSite as e:
        print("There is a problem fetching an entity, this should ideally not occur")
        return
    print("Import Entity", wikidata_item.getID())
    if not id.contains_id(wikidata_item.getID()):
        wikibase_item = pywikibot.ItemPage(wikibase_repo)
        new_id = importEntity(wikidata_item, wikibase_item)
    else:
        print("This entity corresponds to ",id.get_id(wikidata_item.getID()))
        wikibase_item = pywikibot.ItemPage(wikibase_repo, id.get_id(wikidata_item.getID()))
        wikibase_item.get()
        new_id = wikibase_item.getID()
        changeLabels(wikidata_item, wikibase_item)
        changeDescriptions(wikidata_item, wikibase_item)
        changeSiteLinks(wikidata_item, wikibase_item)
        wikidata_link(wikibase_item, wikidata_item)
    if (statements == True):
        changeClaims(wikidata_item,wikibase_item)
    return wikibase_item


def changeProperty(wikidata_item, wikibase_repo, statements):
    print("Import Property", wikidata_item.getID())
    wikidata_item.get()
    wikibase_item = None
    if not id.contains_id(wikidata_item.getID()):
        wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype=wikidata_item.type)
        new_id = importProperty(wikidata_item, wikibase_item)
    else:
        wikibase_item = pywikibot.PropertyPage(wikibase_repo, id.get_id(wikidata_item.getID()), datatype=wikidata_item.type)
        wikibase_item.get()
        new_id = wikibase_item.getID()
        changeLabels(wikidata_item,wikibase_item)
        changeDescriptions(wikidata_item,wikibase_item)
        changeSiteLinks(wikidata_item,wikibase_item)
        wikidata_link(wikibase_item, wikidata_item)
    if statements:
        changeClaims(wikidata_item,wikibase_item)
    return wikibase_item


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]