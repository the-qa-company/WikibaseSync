import re
import sys
from decimal import Decimal
import json
import pywikibot
from pywikibot.page import Claim
import configparser

from util.IdSparql import IdSparql
from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier

user_config = __import__("user-config")

languages = ["bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr", "hu", "it", "lb", "lt", "lv", "mt",
             "nl", "pl", "pt", "ro", "sk", "sl", "sv", "tr"]


class WikibaseImporter:
    def __init__(self, wikibase_repo, wikidata_repo):
        self.wikibase_repo = wikibase_repo
        self.wikidata_repo = wikidata_repo
        self.identifier = PropertyWikidataIdentifier()
        self.identifier.get(wikibase_repo)
        self.appConfig = configparser.ConfigParser()
        self.appConfig.read('config/application.config.ini')
        endpoint = self.appConfig.get('wikibase', 'sparqlEndPoint')
        self.id = IdSparql(endpoint, self.identifier.itemIdentifier, self.identifier.propertyIdentifier)
        self.id.load()

    # transforms the json to an item
    def jsonToItem(self, wikibase_repo, json_object):
        y = json.loads(json_object)
        print(y)
        data = {}
        # labels
        labels = {}
        if 'labels' in y:
            for lang in y['labels']:
                if 'removed' not in y['labels'][lang]:  # T56767
                    labels[lang] = y['labels'][lang]['value']

        # descriptions
        descriptions = {}
        if 'descriptions' in y:
            for lang in y['descriptions']:
                descriptions[lang] = y['descriptions'][lang]['value']

        # aliases
        aliases = {}
        if 'aliases' in y:
            for lang in y['aliases']:
                aliases[lang] = []
                for value in y['aliases'][lang]:
                    aliases[lang].append(value['value'])

        # claims
        claims = {}
        if 'claims' in y:
            for pid in y['claims']:
                claims[pid] = []
                for claim in y['claims'][pid]:
                    try:
                        c = Claim.fromJSON(wikibase_repo, claim)
                        # c.on_item = self
                        claims[pid].append(c)
                    except KeyError:
                        print("This can happen when a property was deleted")

        data['labels'] = labels
        data['descriptions'] = descriptions
        data['aliases'] = aliases
        data['claims'] = claims
        return data

    def get_last_label_update(self, revisions, focus_label):
        """
            for a given label, return the last/most recent revision where it was updated
            :arguments
            :revisions - list of revisions on the wikibase item
            :focus_label - current label to get difference for
            :return - the revisions item where the last update was made on the focus label
        """
        index = 0
        # get labels string as dictionary
        # most_recent_label_value = ast.literal_eval(revisions[index]['slots']['main']['*'])['labels'][focus_label]['value']
        most_recent_label_value = json.loads(revisions[index]['slots']['main']['*'])['labels'][focus_label]['value']
        for revision in revisions:
            if index == 0:  # focus revision
                index += 1
            elif index > 0:
                # get revision asterisk string data as dictionary
                revision_asterisk = json.loads(revision['slots']['main']['*'])
                if revision_asterisk['labels'][focus_label]['value'] != most_recent_label_value:
                    # the next revision after this is where a change was made
                    return revisions[index - 1]

                else:
                    index += 1
        return None

    # comparing the labels
    def diffLabels(self, wikidata_item, wikibase_item):
        """
            LOADING REVISION HERE IS EFFICIENT, UPDATES TURN OUT SUCCESSFUL ( but script ends with an exception)
            pywikibot.exceptions.NoPage: Page [[my:Item:-1]] doesn't exist.
        """

        revisions = []
        try:
            revisions_tmp = wikibase_item.revisions(content=True)
            # problem with the revisions_tmp object
            for h in revisions_tmp:
                revisions.append(h)
        except pywikibot.exceptions.NoPage:
            # pywikibot.exceptions.NoPage: Page [[my:Item:-1]] doesn't exist
            # No revision
            pass


        mylabels = {}
        for label in wikidata_item.labels:
            if label in languages:
                # confirm that wikidata label and description do not have the same value before proceeding
                if not (wikidata_item.labels.get(label) == wikidata_item.descriptions.get(label)):
                    if wikibase_item.getID() != str(-1) and label in wikibase_item.labels:
                        if not (wikidata_item.labels.get(label) == wikibase_item.labels.get(label)):

                            if revisions is None or revisions[0] is None:
                                # no update has been done on label, accept remote update
                                mylabels[label] = wikidata_item.labels.get(label)
                            else:
                                if self.appConfig.get('wikibase', 'overwriteLocalChanges').lower() == 'false':
                                    last_update_revision_on_label = self.get_last_label_update(revisions, label)
                                    if last_update_revision_on_label is None:
                                        # no update has been done on label, accept remote update
                                        mylabels[label] = wikidata_item.labels.get(label)
                                    else:
                                        # accept remote update if the last update on the label was made by wikidata updater
                                        # leave current value if update was by a local user/admin
                                        # if last_update_revision_on_label["user"].lower() == self.appConfig.get('wikibase', 'user').lower():
                                        if last_update_revision_on_label["user"].lower() == str(user_config.usernames['my']['my']):
                                            mylabels[label] = wikidata_item.labels.get(label)
                                else:
                                    mylabels[label] = wikidata_item.labels.get(label)
                    else:
                        mylabels[label] = wikidata_item.labels.get(label)
        return mylabels

    def changeLabels(self, wikidata_item, wikibase_item):
        mylabels = self.diffLabels(wikidata_item, wikibase_item)
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
                x = re.search(r"\[\[Property:.*\]\]", str(e))
                if x:
                    return x.group(0).replace("[[Property:", "").split("|")[0]
                else:
                    print("This should not happen 3")

    # comparing the descriptions
    def diffDescriptions(self, wikidata_item, wikibase_item):
        myDescriptions = {}
        for description in wikidata_item.descriptions:
            if description in languages:
                # confirm that wikidata label and description do not have the same value before proceeding
                if not (wikidata_item.labels.get(description) == wikidata_item.descriptions.get(description)):
                    if wikibase_item.getID() != str(-1) and description in wikibase_item.descriptions:
                        if not (wikidata_item.descriptions.get(description) == wikibase_item.descriptions.get(
                                description)):
                            # print("Change", wikidata_item.descriptions.get(description), "----", wikibase_item.descriptions.get(description))
                            myDescriptions[description] = wikidata_item.descriptions.get(description)
                    else:
                        myDescriptions[description] = wikidata_item.descriptions.get(description)
        return myDescriptions

    # comparing the descriptions
    def change_descriptions(self, wikidata_item, wikibase_item):
        myDescriptions = self.diffDescriptions(wikidata_item, wikibase_item)
        # print(myDescriptions)
        if len(myDescriptions) != 0:
            print("Import Descriptions")
            try:
                wikibase_item.editEntity({'descriptions': myDescriptions},
                                         summary='The description in Wikidata changed')
            except pywikibot.exceptions.OtherPageSaveError as e:
                print("Could not set description of ", wikibase_item.getID())
                print(e)
                x = re.search(r'\[\[Item:.*\]\]', str(e))
                if x:
                    return x.group(0).replace("[[Item:", "").split("|")[0]
                else:
                    print("This should not happen 4")
                print("Error probably property or item already existing ", e)

    # diff the aliases
    def diffAliases(self, wikidata_item, wikibase_item):
        mylabels = {}
        for alias in wikidata_item.aliases:
            if alias in languages:
                if wikibase_item.getID() != str(-1) and alias in wikibase_item.aliases:
                    if not (wikidata_item.aliases.get(alias) == wikibase_item.aliases.get(alias)):
                        # print("Change", wikidata_item.aliases.get(alias), "----", wikibase_item.aliases.get(alias))
                        mylabels[alias] = wikidata_item.aliases.get(alias)
                else:
                    mylabels[alias] = wikidata_item.aliases.get(alias)
        return mylabels

    # comparing the aliases
    def changeAliases(self, wikidata_item, wikibase_item):
        myaliases = self.diffAliases(wikidata_item, wikibase_item)
        if len(myaliases) != 0:
            print("Import aliases")
            try:
                wikibase_item.editAliases(myaliases, summary=u'Aliases in wikidata changed')
            except pywikibot.exceptions.OtherPageSaveError as e:
                print("This should not happen ", e)

    # comparing the sitelinks
    def diffSiteLinks(self, wikidata_item, wikibase_item):
        siteLinks = []
        id = wikibase_item.getID()
        for sitelink in wikidata_item.sitelinks:
            for lang in languages:
                if str(sitelink) == lang + "wiki":
                    if id != str(-1) and sitelink in wikibase_item.sitelinks:
                        if not (str(wikidata_item.sitelinks.get(sitelink)) == str(
                                wikibase_item.sitelinks.get(sitelink))):
                            # print("Change", wikidata_item.sitelinks.get(sitelink), "----", wikibase_item.sitelinks.get(sitelink))
                            siteLinks.append({'site': sitelink,
                                              'title': str(wikidata_item.sitelinks.get(sitelink)).replace('[[',
                                                                                                          '').replace(
                                                  ']]', '')})
                    else:
                        # print("Change", wikidata_item.sitelinks.get(sitelink), "----", wikibase_item.sitelinks.get(sitelink))
                        siteLinks.append({'site': sitelink,
                                          'title': str(wikidata_item.sitelinks.get(sitelink)).replace('[[',
                                                                                                      '').replace(
                                              ']]', '')})
        return siteLinks

    # comparing the sitelinks
    def changeSiteLinks(self, wikidata_item, wikibase_item):
        siteLinks = self.diffSiteLinks(wikidata_item, wikibase_item)
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

    def importItem(self, wikidata_item):
        print("Import Entity", wikidata_item.getID() + " from Wikidata")
        wikibase_item = pywikibot.ItemPage(self.wikibase_repo)
        mylabels = self.diffLabels(wikidata_item, wikibase_item)
        myDescriptions = self.diffDescriptions(wikidata_item, wikibase_item)
        myaliases = self.diffAliases(wikidata_item, wikibase_item)
        # mySitelinks = diffSiteLinks(wikidata_item, wikibase_item)
        mySitelinks = [];
        claim = pywikibot.page.Claim(self.wikibase_repo, self.identifier.itemIdentifier, datatype='external-id')
        target = wikidata_item.getID()
        claim.setTarget(target)
        data = {
            'labels': mylabels,
            'descriptions': myDescriptions,
            'aliases': myaliases,
            'sitelinks': mySitelinks,
            'claims': [claim.toJSON()]
        }
        # print(data)
        try:
            wikibase_item.editEntity(data, summary=u'Importing entity ' + wikidata_item.getID() + ' from wikidata')
            self.id.save_id(wikidata_item.getID(), wikibase_item.getID())
            return wikibase_item.getID()
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("Could not set description of ", wikibase_item.getID())
            print("This is the error message ", e)
            x = re.search(r'\[\[Item:.*\]\]', str(e))
            if x:
                return x.group(0).replace("[[Item:", "").split("|")[0]
            else:
                print("This should not happen 5")
            print("Error probably property or item already existing ", e)

    def importProperty(self, wikidata_item):
        print("Import Property", wikidata_item.getID() + " from Wikidata")
        wikibase_item = pywikibot.PropertyPage(self.wikibase_repo, datatype=wikidata_item.type)
        mylabels = self.diffLabels(wikidata_item, wikibase_item)
        myDescriptions = self.diffDescriptions(wikidata_item, wikibase_item)
        myaliases = self.diffAliases(wikidata_item, wikibase_item)
        claim = pywikibot.page.Claim(self.wikibase_repo, self.identifier.propertyIdentifier, datatype='external-id')
        target = wikidata_item.getID()
        claim.setTarget(target)

        data = {
            'labels': mylabels,
            'descriptions': myDescriptions,
            'aliases': myaliases,
            'claims': [claim.toJSON()]
        }
        try:
            wikibase_item.editEntity(data,
                                     summary=u'Importing property ' + wikidata_item.getID() + ' from wikidata')
            self.id.save_id(wikidata_item.getID(), wikibase_item.getID())
            return wikibase_item.getID()
        except pywikibot.exceptions.OtherPageSaveError as e:
            print("Could not set description of ", wikibase_item.getID())
            print(e)
            x = re.search(r'\[\[Item:.*\]\]', str(e))
            if x:
                return x.group(0).replace("[[Item:", "").split("|")[0]
            else:
                print("This should not happen 6")
            print("Error probably property or item already existing ", e)

    # comparing two claims
    def compare_claim(self, wikidata_claim, wikibase_claim, translate):
        found = False
        found_equal_value = False
        wikidata_propertyId = wikidata_claim.get('property')
        wikibase_propertyId = wikibase_claim.get('property')
        if ((translate == True and self.id.get_id(wikidata_propertyId) == wikibase_propertyId) or (
                translate == False and wikidata_propertyId == wikibase_propertyId)):
            found = True
            if wikidata_claim.get('snaktype') == 'somevalue' and wikibase_claim.get('snaktype') == 'somevalue':
                found_equal_value = True
            elif wikidata_claim.get('snaktype') == 'novalue' and wikibase_claim.get('snaktype') == 'novalue':
                found_equal_value = True
            else:
                # WIKIBASE_ITEM
                if wikidata_claim.get('datatype') == 'wikibase-item':
                    if wikibase_claim.get('datatype') == 'wikibase-item':
                        wikidata_objectId = 'Q' + str(
                            wikidata_claim.get('datavalue').get('value').get('numeric-id'))
                        wikibase_objectId = 'Q' + str(
                            wikibase_claim.get('datavalue').get('value').get('numeric-id'))
                        # print(self.id.get_id(wikidata_propertyId),"---", wikibase_propertyId)
                        # print(self.id.get_id(wikidata_objectId),"---",wikibase_objectId)
                        if translate:
                            if self.id.contains_id(wikidata_objectId) and self.id.get_id(
                                    wikidata_objectId) == wikibase_objectId:
                                found_equal_value = True
                        else:
                            if wikidata_objectId == wikibase_objectId:
                                found_equal_value = True
                # WIKIBASE-PROPERTY
                elif wikidata_claim.get('datatype') == 'wikibase-property':
                    if wikibase_claim.get('datatype') == 'wikibase-property':
                        wikidata_objectId = 'P' + str(
                            wikidata_claim.get('datavalue').get('value').get('numeric-id'))
                        wikibase_objectId = 'P' + str(
                            wikibase_claim.get('datavalue').get('value').get('numeric-id'))
                        # print(self.id.get_id(wikidata_propertyId),"---", wikibase_propertyId)
                        # print(self.id.get_id(wikidata_objectId),"---",wikibase_objectId)
                        if translate:
                            if self.id.contains_id(wikidata_objectId) and self.id.get_id(
                                    wikidata_objectId) == wikibase_objectId:
                                found_equal_value = True
                        else:
                            if wikidata_objectId == wikibase_objectId:
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
                        if wikibase_text == wikidata_text and wikibase_language == wikidata_language:
                            found_equal_value = True

                # COMMONS-MEDIA
                elif wikidata_claim.get('datatype') == 'commonsMedia':
                    if wikibase_claim.get('datatype') == 'commonsMedia':
                        wikibase_propertyId = wikibase_claim.get('property')
                        wikibase_text = wikibase_claim.get('datavalue').get('value')
                        wikidata_text = wikidata_claim.get('datavalue').get('value')
                        # print(self.id.get_id(wikidata_propertyId),'--',wikibase_propertyId,'--',wikibase_text, '--- ', wikidata_text,  wikibase_text == wikidata_text)
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
                        if wikibase_latitude == wikidata_latitude and wikibase_longitude == wikidata_longitude and wikibase_globe == wikidata_globe \
                                and wikibase_altitude == wikidata_altitude and (
                                wikibase_precision == wikidata_precision or (
                                wikibase_precision == 1 and wikidata_precision == None)):
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
                        if wikibase_amount == wikidata_amount and wikibase_upperBound == wikidata_upperBound and wikibase_lowerBound == wikidata_lowerBound:
                            if (wikidata_unit == None and wikibase_unit == None) or (
                                    wikidata_unit == '1' and wikibase_unit == '1'):
                                found_equal_value = True
                            else:
                                if ("entity/" in wikidata_unit) and ("entity/" in wikibase_unit):
                                    unit_id = wikibase_unit.split("entity/")[1]
                                    wikidata_unit_id = wikidata_unit.split("entity/")[1]
                                    if translate:
                                        if self.id.contains_id(wikidata_unit_id) and self.id.get_id(
                                                wikidata_unit_id) == unit_id:
                                            found_equal_value = True
                                    else:
                                        if wikidata_unit_id == unit_id:
                                            found_equal_value = True
                        # print("EQUAL ",found_equal_value)

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
                        if wikidata_time == wikibase_time and wikidata_precision == wikibase_precision and wikidata_after == wikibase_after and wikidata_before == wikibase_before and wikidata_timezone == wikibase_timezone \
                                and wikidata_calendermodel == wikibase_calendermodel:
                            found_equal_value = True

                # URL
                elif wikidata_claim.get('datatype') == 'url':
                    if wikibase_claim.get('datatype') == 'url':
                        wikibase_propertyId = wikibase_claim.get('property')
                        wikibase_value = wikibase_claim.get('datavalue').get(
                            'value')[0:500]

                        wikidata_value = wikidata_claim.get('datavalue').get(
                            'value')[0:500]
                        if wikibase_value == wikidata_value:
                            found_equal_value = True
                # STRING
                elif wikidata_claim.get('datatype') == 'string':
                    if wikibase_claim.get('datatype') == 'string':
                        wikibase_value = wikibase_claim.get('datavalue').get(
                            'value')
                        wikidata_value = wikidata_claim.get('datavalue').get(
                            'value')
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
                        if wikibase_value == wikidata_value and wikibase_type == wikidata_type:
                            found_equal_value = True
                # GEOSHAPE
                elif wikidata_claim.get('datatype') == 'geo-shape':
                    if wikibase_claim.get('datatype') == 'geo-shape':
                        wikibase_propertyId = wikibase_claim.get('property')
                        wikibase_value = wikibase_claim.get('datavalue').get('value')
                        wikidata_value = wikidata_claim.get('datavalue').get('value')
                        if wikibase_value == wikidata_value:
                            found_equal_value = True
                # TABULAR-DATA
                elif wikidata_claim.get('datatype') == 'tabular-data':
                    print('tabular-data')
                    # raise NameError('Tabluar data not implemented')
                    # set new claim
                    # claim = pywikibot.page.Claim(
                    #     testsite, 'P30175', datatype='tabular-data')
                    # commons_site = pywikibot.Site('commons', 'commons')
                    # page = pywikibot.Page(commons_site, 'Data:Bea.gov/GDP by state.tab')
                    # target = pywikibot.WbGeoShape(page)
                    # claim.setTarget(target)
                    # item.addClaim(claim)
                else:
                    print('This datatype is not supported ', wikidata_claim.get('datatype'), ' ----  ',
                          wikibase_claim.get('datatype'))
        return found, found_equal_value

    # translate one claim from wikidata in one of wikibase
    def translateClaim(self, wikidata_claim):
        wikidata_propertyId = wikidata_claim.get('property')
        if not self.id.contains_id(wikidata_propertyId):
            wikidata_property = pywikibot.PropertyPage(self.wikidata_repo, wikidata_propertyId,
                                                       datatype=wikidata_claim.get('datatype'))
            wikidata_property.get()
            self.importProperty(wikidata_property)
        if wikidata_claim.get('snaktype') == 'somevalue':
            claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                    datatype=wikidata_claim.get('datatype'))
            claim.setSnakType('somevalue')
            return claim
        elif wikidata_claim.get('snaktype') == 'novalue':
            claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                    datatype=wikidata_claim.get('datatype'))
            claim.setSnakType('novalue')
        else:
            # WIKIBASE-ITEM
            if wikidata_claim.get('datatype') == 'wikibase-item':
                # add the entity to the wiki
                wikidata_objectId = 'Q' + str(
                    wikidata_claim.get('datavalue').get('value').get('numeric-id'))
                if not self.id.contains_id(wikidata_objectId):
                    item = pywikibot.ItemPage(self.wikidata_repo, wikidata_objectId)
                    try:
                        item.get()
                        self.importItem(item)
                    except pywikibot.exceptions.IsRedirectPage:
                        print("We are ignoring this")

                if self.id.contains_id(wikidata_objectId) and (not self.id.get_id(wikidata_objectId) == '-1'):
                    claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                            datatype='wikibase-item')
                    object = pywikibot.ItemPage(self.wikibase_repo, self.id.get_id(wikidata_objectId))
                    claim.setTarget(object)
                    claim.setRank(wikidata_claim.get('rank'))
                    return claim
            # WIKIBASE-PROPERTY
            elif wikidata_claim.get('datatype') == 'wikibase-property':
                wikidata_objectId = 'P' + str(
                    wikidata_claim.get('datavalue').get('value').get('numeric-id'))
                if not self.id.contains_id(wikidata_objectId):
                    item = pywikibot.PropertyPage(self.wikidata_repo, wikidata_objectId)
                    try:
                        item.get()
                        self.importProperty(item)
                    except pywikibot.exceptions.IsRedirectPage:
                        print("We are ignoring this")

                if self.id.contains_id(wikidata_objectId) and (not self.id.get_id(wikidata_objectId) == '-1'):
                    claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                            datatype='wikibase-property')
                    object = pywikibot.PropertyPage(self.wikibase_repo, self.id.get_id(wikidata_objectId))
                    claim.setTarget(object)
                    claim.setRank(wikidata_claim.get('rank'))
                    return claim
            # MONOLINGUALTEXT
            elif wikidata_claim.get('datatype') == 'monolingualtext':
                claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                        datatype='monolingualtext')
                wikidata_text = wikidata_claim.get('datavalue').get('value').get('text')
                wikidata_language = wikidata_claim.get('datavalue').get('value').get('language')
                # HACK
                #
                # print(wikidata_text, "---", wikidata_language)
                target = pywikibot.WbMonolingualText(text=wikidata_text, language=wikidata_language)
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            # GLOBE-COORDINATES
            elif wikidata_claim.get('datatype') == 'globe-coordinate':
                wikidata_latitude = wikidata_claim.get('datavalue').get('value').get('latitude')
                wikidata_longitude = wikidata_claim.get('datavalue').get('value').get('longitude')
                wikidata_altitude = wikidata_claim.get('datavalue').get('value').get('altitude')
                wikidata_globe_uri = wikidata_claim.get('datavalue').get('value').get(
                    'globe').replace("http://www.wikidata.org/entity/", "")
                wikidata_precision = wikidata_claim.get('datavalue').get('value').get('precision')
                wikidata_globe_item = pywikibot.ItemPage(self.wikidata_repo, wikidata_globe_uri)
                wikidata_globe_item.get()
                wikibase_globe_item = self.change_item(wikidata_globe_item, self.wikibase_repo, False)

                ##Note: picking as globe wikidata item for earth, this is the standard in a wikibase even if the entity does not exist
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='globe-coordinate')
                if wikidata_precision != None:
                    target = pywikibot.Coordinate(site=self.wikibase_repo, lat=wikidata_latitude,
                                                  lon=wikidata_longitude,
                                                  alt=wikidata_altitude,
                                                  globe_item="http://www.wikidata.org/entity/Q2",
                                                  precision=wikidata_precision
                                                  )
                else:
                    target = pywikibot.Coordinate(site=self.wikibase_repo, lat=wikidata_latitude,
                                                  lon=wikidata_longitude,
                                                  alt=wikidata_altitude,
                                                  globe_item="http://www.wikidata.org/entity/Q2",
                                                  precision=1
                                                  )
                # print(wikidata_propertyId)
                # print("Property ",self.id.get_id(wikidata_propertyId))
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
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='time')
                target = pywikibot.WbTime.fromTimestr(site=self.wikibase_repo, datetimestr=wikidata_time,
                                                      precision=wikidata_precision,
                                                      after=wikidata_after, before=wikidata_before,
                                                      timezone=wikidata_timezone,
                                                      calendarmodel=wikidata_calendermodel)
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))

                return claim
            # COMMONSMEDIA
            elif wikidata_claim.get('datatype') == 'commonsMedia':
                claim = pywikibot.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
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
                    if not self.id.contains_id(wikidata_objectId):
                        item = pywikibot.ItemPage(self.wikidata_repo, wikidata_objectId)
                        self.change_item(item, self.wikibase_repo, False)
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='quantity')
                # print(wikidata_amount)
                # print(Decimal(wikidata_amount))
                # print(wikidata_upperBound)
                # print(Decimal(wikidata_upperBound)-Decimal(wikidata_amount))
                if wikidata_unit == None or wikidata_unit == '1':
                    if wikidata_upperBound == None:
                        # print("Here 1", '{:f}'.format(Decimal(wikidata_amount)))
                        target = pywikibot.WbQuantity(amount='{:f}'.format(Decimal(wikidata_amount)),
                                                      site=self.wikibase_repo)
                        claim.setTarget(target)
                        claim.setRank(wikidata_claim.get('rank'))
                        return claim
                    else:
                        # print("Here 2", '{:f}'.format(Decimal(wikidata_amount)))
                        target = pywikibot.WbQuantity(amount=Decimal(wikidata_amount), site=self.wikibase_repo,
                                                      error=Decimal(wikidata_upperBound) - Decimal(wikidata_amount))
                        claim.setTarget(target)
                        claim.setRank(wikidata_claim.get('rank'))
                        return claim
                else:
                    if (self.id.contains_id(wikidata_objectId) and not self.id.get_id(wikidata_objectId) == '-1'):
                        if wikidata_upperBound == None:
                            # print("Here 3", '{:f}'.format(Decimal(wikidata_amount)))
                            wikibase_unit = pywikibot.ItemPage(self.wikibase_repo, self.id.get_id(wikidata_objectId))
                            # here this is a hack .......
                            target = pywikibot.WbQuantity(amount=Decimal(wikidata_amount), unit=wikibase_unit,
                                                          site=self.wikibase_repo)
                            claim.setTarget(target)
                            claim.setRank(wikidata_claim.get('rank'))
                        else:
                            # print("Here 4", '{:f}'.format(Decimal(wikidata_amount)))
                            wikibase_unit = pywikibot.ItemPage(self.wikibase_repo, self.id.get_id(wikidata_objectId))
                            target = pywikibot.WbQuantity(amount=Decimal(wikidata_amount), unit=wikibase_unit,
                                                          site=self.wikibase_repo,
                                                          error=Decimal(wikidata_upperBound) - Decimal(
                                                              wikidata_amount))
                            claim.setTarget(target)
                            claim.setRank(wikidata_claim.get('rank'))
                        return claim
            # URL
            elif wikidata_claim.get('datatype') == 'url':
                wikidata_value = wikidata_claim.get('datavalue').get('value')
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='url')
                target = wikidata_value[0:500]
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            # EXTERNAL-ID
            elif wikidata_claim.get('datatype') == 'external-id':
                wikidata_value = wikidata_claim.get('datavalue').get('value')
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='external-id')
                target = wikidata_value
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            # STRING
            elif wikidata_claim.get('datatype') == 'string':
                wikidata_value = wikidata_claim.get('datavalue').get('value')
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='string')
                target = wikidata_value
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            # GEOSHAPE
            elif wikidata_claim.get('datatype') == 'geo-shape':
                claim = pywikibot.page.Claim(self.wikibase_repo, self.id.get_id(wikidata_propertyId),
                                             datatype='geo-shape')
                commons_site = pywikibot.Site('commons', 'commons')
                page = pywikibot.Page(commons_site, wikidata_claim.get('datavalue').get('value'))
                target = pywikibot.WbGeoShape(page)
                claim.setTarget(target)
                claim.setRank(wikidata_claim.get('rank'))
                return claim
            # TABULAR-DATA
            elif wikidata_claim.get('datatype') == 'tabular-data':
                return None
                print('Not implemented yet tabular-data')
                # raise NameError('Tabluar data not implemented')
                # set new claim
                # claim = pywikibot.page.Claim(
                #     testsite, 'P30175', datatype='tabular-data')
                # commons_site = pywikibot.Site('commons', 'commons')
                # page = pywikibot.Page(commons_site, 'Data:Bea.gov/GDP by state.tab')
                # target = pywikibot.WbGeoShape(page)
                # claim.setTarget(target)
                # item.addClaim(claim)
            else:
                print('This datatype is not supported ', wikidata_claim.get('datatype'),
                      ' translating the following claim ', wikidata_claim)
                return None

    # comparing two claims together with their qualifiers and references
    def compare_claim_with_qualifiers_and_references(self, wikidata_claim, wikibase_claim, translate):
        # compare mainsnak
        found = False
        found_equal_value = False
        (claim_found, main_claim_found_equal_value) = self.compare_claim(wikidata_claim.get('mainsnak'),
                                                                         wikibase_claim.get('mainsnak'), translate)
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
                            if self.id.contains_id(wikidata_propertyId):
                                (qualifier_claim_found, qualifier_claim_found_equal_value) = self.compare_claim(
                                    q_wikidata, q_wikibase, translate)
                                if qualifier_claim_found_equal_value == True:
                                    qualifier_equal = True
                    if qualifier_equal == False:
                        qualifiers_equal = False
        if ('qualifiers' in wikidata_claim and not ('qualifiers' in wikibase_claim) or (
                not 'qualifiers' in wikidata_claim) and 'qualifiers' in wikibase_claim):
            qualifiers_equal = False

        # compare references
        references_equal = True

        # print(wikidata_claim.get('references'))
        # print(wikibase_claim.get('references'))
        if ('references' in wikidata_claim) and ('references' in wikibase_claim):
            # print(len(wikidata_claim.get('references')))
            # print()
            # print(len(wikibase_claim.get('references')))
            # if len(wikidata_claim.get('references')) == len(wikibase_claim.get('references')):
            for i in range(0, len(wikidata_claim.get('references'))):
                for q1 in wikidata_claim.get('references')[i].get('snaks'):
                    for q_wikidata in wikidata_claim.get('references')[i].get('snaks').get(q1):
                        reference_equal = False
                        for snak in wikibase_claim.get('references'):
                            for q2 in snak.get('snaks'):
                                for q_wikibase in snak.get('snaks').get(q2):
                                    wikidata_propertyId = q_wikidata.get('property')
                                    if self.id.contains_id(wikidata_propertyId):
                                        # print("Two Qualifiers")
                                        # print("q_wikidata",q_wikidata)
                                        # print("q_wikibase",q_wikibase)
                                        (
                                            references_claim_found,
                                            references_claim_found_equal_value) = self.compare_claim(
                                            q_wikidata,
                                            q_wikibase, translate)
                                        # print("qualifier_claim_found_equal_value", references_claim_found_equal_value)
                                        if references_claim_found_equal_value == True:
                                            # print("Enter here ....")
                                            reference_equal = True
                        if reference_equal == False:
                            references_equal = False
        # else:
        #     references_equal = False
        if ('references' in wikidata_claim and not ('references' in wikibase_claim)) or (
                not ('references' in wikidata_claim) and 'references' in wikibase_claim):
            references_equal = False
        if main_claim_found_equal_value and qualifiers_equal and references_equal and wikidata_claim.get(
                'rank') == wikibase_claim.get('rank'):
            found_equal_value = True
        more_accurate = False
        # print("main_claim_found_equal_value and ('references' not in wikibase_claim) and ('qualifiers' not in wikibase_claim)", main_claim_found_equal_value and ('references' not in wikibase_claim) and ('qualifiers' not in wikibase_claim))
        # print("'references' in wikidata_claim ", 'references' in wikidata_claim )
        # print("len(wikidata_claim.get('references'))>0",'references' in wikidata_claim and len(wikidata_claim.get('references')) > 0)
        # if 'references' in wikidata_claim:
        # print(wikidata_claim.get('references'))
        # print(len(wikidata_claim.get('references')) > 0)
        # print((('references' in wikidata_claim and len(wikidata_claim.get('references'))>0) or ('qualifiers' in wikidata_claim and len(wikidata_claim.get('qualifiers'))>0)))
        if main_claim_found_equal_value and ('references' not in wikibase_claim) and (
                'qualifiers' not in wikibase_claim) and (
                ('references' in wikidata_claim and len(wikidata_claim.get('references')) > 0) or (
                'qualifiers' in wikidata_claim and len(wikidata_claim.get('qualifiers')) > 0)):
            more_accurate = True
        return claim_found, found_equal_value, more_accurate

    # change the claims
    def changeClaims(self, wikidata_item, wikibase_item):
        # check which claims are in wikibase and in wikidata with the same property but different value, and delete them
        claimsToRemove = []
        claim_more_accurate = []
        for wikibase_claims in wikibase_item.claims:
            for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                # print("Trying to find this claim ", wikibase_c)
                alreadyFound = False
                wikibase_claim = wikibase_c.toJSON()
                wikibase_propertyId = wikibase_claim.get('mainsnak').get('property')
                found = False
                found_equal_value = False
                found_more_accurate = False  # tells if the statement to import is better then the existing one, i.e. if it has references and qualifiers for the fact
                for claims in wikidata_item.claims:
                    for c in wikidata_item.claims.get(claims):
                        wikidata_claim = c.toJSON()
                        wikidata_propertyId = wikidata_claim.get('mainsnak').get('property')
                        # if the property is not there then they cannot be at the same time in wikibase and wikidata
                        if self.id.contains_id(wikidata_propertyId):
                            if self.id.get_id(wikidata_propertyId) == wikibase_propertyId:

                                # if wikidata_propertyId == 'P2884':

                                # if self.id.get_id(wikidata_propertyId) == 'P194' and wikidata_propertyId == "P530":
                                # print(wikidata_claim,"---",wikibase_claim)
                                (found_here, found_equal_value_here,
                                 more_accurate_here) = self.compare_claim_with_qualifiers_and_references(wikidata_claim,
                                                                                                         wikibase_claim,
                                                                                                         True)
                                # print('Result ',found_here,found_equal_value_here, more_accurate_here)
                                if found_here == True:
                                    found = True
                                if found_equal_value == True and found_equal_value_here == True:
                                    alreadyFound = True
                                if found_equal_value_here == True:
                                    found_equal_value = True
                                found_more_accurate = more_accurate_here

                if found == True and found_equal_value == False:
                    claimsToRemove.append(wikibase_c)
                    claim_more_accurate.append(found_more_accurate)
                    print("This claim is deleted ", wikibase_claim)
                if alreadyFound == True:
                    claimsToRemove.append(wikibase_c)
                    claim_more_accurate.append(found_more_accurate)
                    print("This claim is deleted it's a duplicate", wikibase_claim)

        # print("CHECK WHO ADDED THE CLAIMS")
        # check that the claims to delete where added by Wikidata Updater, if not, don't delete them
        # get all the edit history
        not_remove = []
        revisions_tmp = wikibase_item.revisions(content=True)
        revisions = []
        # problem with the revisions_tmp object
        for h in revisions_tmp:
            revisions.append(h)
        is_only_wikidata_updater_user = True
        # if only the wikidata updater made changes then it is for sure a deletion in wikidata
        for revision in revisions:
            # print(revision['user'])
            if revision['user'] != "WikidataUpdater":
                is_only_wikidata_updater_user = False
                break
        # print("is_only_wikidata_updater_user",is_only_wikidata_updater_user)
        if not is_only_wikidata_updater_user:
            for i in range(0, len(claimsToRemove)):
                claimToRemove = claimsToRemove[i]
                # print("CHECKING CLAIM ",claimToRemove, "---", claim_more_accurate[i],"---", revisions)
                # go through the history and find the edit where it was added and the user that made that edit
                if claim_more_accurate[
                    i] == False:  # if the claim is more accurate it is better to cancel the existing one
                    edit_where_claim_was_added = len(revisions) - 1
                    for i in range(0, len(revisions)):
                        # print("new revision ",revisions[i]['user'])
                        item_revision = self.jsonToItem(self.wikibase_repo, revisions[i]['text'])
                        found = False
                        for claims_revision in item_revision['claims']:
                            if found == False:
                                for c_revision in item_revision['claims'].get(claims_revision):
                                    if found == False:
                                        (found_here, found_equal_value_here,
                                         more_accurate) = self.compare_claim_with_qualifiers_and_references(
                                            claimToRemove.toJSON(), c_revision.toJSON(), False)
                                        # print(claimToRemove.toJSON(), "----", c_revision.toJSON())
                                        # print("found_equal_value_here",found_equal_value_here, " more_accurate", more_accurate)
                                        if found_equal_value_here == True:
                                            found = True
                        if found == False:
                            edit_where_claim_was_added = i - 1
                            break
                    # print("User that added this claim ", revisions[edit_where_claim_was_added]['user'])
                    if revisions[edit_where_claim_was_added]['user'] != self.appConfig.get('wikibase', 'user'):
                        not_remove.append(claimToRemove)
        for c in not_remove:
            claimsToRemove.remove(c)
        print("claimsToRemove ", claimsToRemove)
        if len(claimsToRemove) > 0:
            for claimsToRemoveChunk in chunks(claimsToRemove, 50):
                wikibase_item.get()
                wikibase_item.removeClaims(claimsToRemoveChunk,
                                           summary="Removing this statements since they changed in Wikidata")
        # check which claims are in wikidata and not in wikibase and import them
        # refetch the wikibase entity since some statements may hav been deleted
        if wikibase_item.getID().startswith("Q"):
            wikibase_item = pywikibot.ItemPage(self.wikibase_repo, wikibase_item.getID())
        else:
            wikibase_item = pywikibot.PropertyPage(self.wikibase_repo, wikibase_item.getID())
        wikibase_item.get()
        newClaims = []
        for claims in wikidata_item.claims:
            for c in wikidata_item.claims.get(claims):
                wikidata_claim = c.toJSON()
                found_equal_value = False
                wikidata_propertyId = wikidata_claim.get('mainsnak').get('property')
                print(wikidata_propertyId)
                if wikibase_item.getID().startswith("Q") or wikibase_item.getID().startswith("P"):
                    for wikibase_claims in wikibase_item.claims:
                        for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                            wikibase_claim = wikibase_c.toJSON()
                            if self.id.contains_id(wikidata_propertyId):
                                (claim_found, claim_found_equal_value,
                                 more_accurate) = self.compare_claim_with_qualifiers_and_references(wikidata_claim,
                                                                                                    wikibase_claim,
                                                                                                    True)
                                if (claim_found_equal_value == True):
                                    found_equal_value = True
                    print(found_equal_value)
                    if found_equal_value == False:
                        # print("This claim is added ", wikidata_claim)
                        # import the property if it does not exist
                        if wikidata_claim.get('mainsnak').get('snaktype') == 'value':
                            # the claim is added
                            claim = self.translateClaim(wikidata_claim.get('mainsnak'))
                            if claim is not None:
                                claim.setRank(wikidata_claim.get('rank'))
                                if 'qualifiers' in wikidata_claim:
                                    for key in wikidata_claim.get('qualifiers'):
                                        for old_qualifier in wikidata_claim.get('qualifiers').get(key):
                                            new_qualifier = self.translateClaim(old_qualifier)
                                            if new_qualifier != None:
                                                claim.addQualifier(new_qualifier)
                                if 'references' in wikidata_claim:
                                    for snak in wikidata_claim.get('references'):
                                        for key in snak.get('snaks'):
                                            new_references = []
                                            for old_reference in snak.get('snaks').get(key):
                                                # print('old',old_reference)
                                                new_reference = self.translateClaim(old_reference)
                                                # print(new_reference)
                                                # this can happen if the object entity has no label in any given language
                                                if new_reference != None:
                                                    new_references.append(new_reference)
                                            if len(new_references) > 0:
                                                claim.addSources(new_references)
                                newClaims.append(claim.toJSON())
                                # print("wikidata claim ",wikidata_claim)
                                # data = {}
                                # data['claims'] = [claim.toJSON()]
                                # print("Data ", json.dumps(data))
                                # wikibase_item.editEntity(data)

                            else:
                                print('The translated claim is None ', wikidata_claim.get('mainsnak'))
                        elif wikidata_claim.get('mainsnak').get('snaktype') == 'novalue':
                            print("Claims with no value not implemented yet")
                        else:
                            print('This should not happen ', wikidata_claim.get('mainsnak'))
        print("claimsToAdd ", newClaims)
        if len(newClaims) > 0:
            for claimsToAdd in chunks(newClaims, 20):
                data = {}
                data['claims'] = claimsToAdd

                import json
                print("Data ", json.dumps(data))
                try:
                    wikibase_item.editEntity(data,
                                             summary="Adding these statements since they where added in Wikidata")
                except (pywikibot.data.api.APIError, pywikibot.exceptions.OtherPageSaveError) as e:
                    print(e)

    def wikidata_link(self, wikibase_item, wikidata_item):
        # make a link to wikidata if it does not exist
        found = False
        if hasattr(wikibase_item, "claims"):
            for wikibase_claims in wikibase_item.claims:
                for wikibase_c in wikibase_item.claims.get(wikibase_claims):
                    wikibase_claim = wikibase_c.toJSON()
                    wikibase_propertyId = wikibase_claim.get('mainsnak').get('property')
                    if wikibase_propertyId == self.identifier.itemIdentifier:
                        found = True
        if found == False:
            claim = pywikibot.page.Claim(self.wikibase_repo, self.identifier.itemIdentifier, datatype='external-id')
            target = wikidata_item.getID()
            claim.setTarget(target)
            wikibase_item.addClaim(claim)

    def change_item(self, wikidata_item, wikibase_repo, statements):
        try:
            item = wikidata_item.get()
        except pywikibot.exceptions.UnknownSite as e:
            print("There is a problem fetching an entity, this should ideally not occur")
            return
        print("Change Entity ", wikidata_item.getID())
        if not self.id.contains_id(wikidata_item.getID()):
            new_id = self.importItem(wikidata_item)
            wikibase_item = pywikibot.ItemPage(wikibase_repo, new_id)
            wikibase_item.get()
        else:
            print("This entity corresponds to ", self.id.get_id(wikidata_item.getID()))
            wikibase_item = pywikibot.ItemPage(wikibase_repo, self.id.get_id(wikidata_item.getID()))
            wikibase_item.get()
            self.changeLabels(wikidata_item, wikibase_item)
            self.changeAliases(wikidata_item, wikibase_item)
            self.change_descriptions(wikidata_item, wikibase_item)
            self.wikidata_link(wikibase_item, wikidata_item)
        if statements:
            self.changeSiteLinks(wikidata_item, wikibase_item)
            self.changeClaims(wikidata_item, wikibase_item)
        return wikibase_item

    def change_item_given_id(self, wikidata_item, id, wikibase_repo, statements):
        print("This entity corresponds to ", id)
        wikibase_item = pywikibot.ItemPage(wikibase_repo, id)
        wikibase_item.get()
        self.changeLabels(wikidata_item, wikibase_item)
        self.changeAliases(wikidata_item, wikibase_item)
        self.change_descriptions(wikidata_item, wikibase_item)
        self.wikidata_link(wikibase_item, wikidata_item)
        if statements:
            self.changeSiteLinks(wikidata_item, wikibase_item)
            self.changeClaims(wikidata_item, wikibase_item)

    def change_property(self, wikidata_item, wikibase_repo, statements):
        print("Change Property", wikidata_item.getID())
        wikidata_item.get()
        wikibase_item = None
        if not self.id.contains_id(wikidata_item.getID()):
            new_id = self.importProperty(wikidata_item)
            wikibase_item = pywikibot.PropertyPage(wikibase_repo, new_id, datatype=wikidata_item.type)
            wikibase_item.get()
        else:
            print("Entering here")
            wikibase_item = pywikibot.PropertyPage(wikibase_repo, self.id.get_id(wikidata_item.getID()),
                                                   datatype=wikidata_item.type)
            wikibase_item.get()
            new_id = wikibase_item.getID()
            self.changeLabels(wikidata_item, wikibase_item)
            self.changeAliases(wikidata_item, wikibase_item)
            self.change_descriptions(wikidata_item, wikibase_item)
        if statements:
            self.changeClaims(wikidata_item, wikibase_item)
        return wikibase_item


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
