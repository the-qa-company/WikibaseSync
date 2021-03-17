# coding=utf-8
import configparser
import json
import sys
import time
import traceback
from datetime import timedelta

import pywikibot
from SPARQLWrapper import SPARQLWrapper

from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier
from util.util import WikibaseImporter

# connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikidata = pywikibot.Site("wikidata", "wikidata")

"""
THIS CLASS RUNS FREQUENTLY TO MONITOR THE CHANGES AND IMPORT WIKIDATA CHANGES IF ANY
"""


class MonitorChanges:

    def __init__(self,wikibase,wikidata):
        self.wikibase = wikibase
        self.wikidata = wikidata
        wikibase_repo = wikibase.data_repository()
        self.wikibase_repo = wikibase_repo
        wikidata_repo = wikidata.data_repository()
        self.wikidata_repo = wikidata_repo
        identifier = PropertyWikidataIdentifier()
        identifier.get(wikibase_repo)
        self.wikidata_code_property_id = identifier.itemIdentifier
        self.wikidata_pid_property_id = identifier.propertyIdentifier
        self.wikibase_importer = WikibaseImporter(wikibase_repo,wikidata_repo)

    def get_claim(self, item_id):
        entity = pywikibot.ItemPage(self.wikibase_repo, item_id)
        claims = entity.get(u'claims')  # Get all the existing claims
        return claims

    def check_differences(self, item_id, change):
        if item_id and item_id[0] == 'Q':
            print(f' changed item {item_id} : edit type {change.get("type")}')
            item = pywikibot.ItemPage(self.wikibase_repo, item_id)
            item.get()
            existing_claims = self.get_claim(item.id)
            if (u'' + self.wikidata_code_property_id + '' in existing_claims[u'claims'] and len(
                    list(existing_claims.get('claims'))) > 1):
                rev_text = []
                for x in item.revisions(total=3, content=True):
                    rev_text.append(x.text)
                # RECENT REVISION CONTAINS WIKIDATAQID PROPERTY AND PREVIOUS REVISION DOES NOT CONTAINS THAT PROPERTY
                if (json.loads(rev_text[0]).get('claims').get(self.wikidata_code_property_id, None) is not None and json.loads(rev_text[1]).get(
                        'claims').get(self.wikidata_code_property_id, None) is None):
                    wikidata_qid = existing_claims[u'claims'][self.wikidata_code_property_id][0].toJSON()['mainsnak']['datavalue']['value']
                    print("Entity "+item_id+" has a new link to wikidata id "+wikidata_qid+" importing it ... ")
                    wikidata_item = pywikibot.ItemPage(self.wikidata_repo, wikidata_qid)
                    wikidata_item.get()
                    self.wikibase_importer.change_item(wikidata_item, self.wikibase_repo, True)
                else:
                    return

    # get changes
    def get_changes(self):
        print("Fetching changes ...")
        current_time = self.wikibase.server_time()
        requests=self.wikibase.recentchanges(start=current_time, end=current_time - timedelta(minutes=20))
        response=requests.request.submit()
        changes=response.get('query')['recentchanges']
        for change in changes:
            try:
                if change.get('type') == 'new':
                    item_id=change.get('title').split(':')[-1]
                    self.check_differences(item_id, change)
                elif change.get('type') == 'edit':
                    item_id = change.get('title').split(':')[-1]
                    self.check_differences(item_id, change)
            except Exception as e:
                print(e)
        return response


def start():
    changes = MonitorChanges(wikibase,wikidata)
    while True:
        try:
            res = changes.get_changes()
            print(res)
        except Exception as e:
            print(e)
        print('Wikiwata QID Change Monitor sleeps for 180s')
        time.sleep(180)


start()
exit()



