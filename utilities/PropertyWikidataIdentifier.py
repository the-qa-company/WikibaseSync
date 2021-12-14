# This class generates an external identifier to Wikidata, i.e. for the entites imported from Wikidata the wikidata
# ID will be indicated
import pywikibot
import re
from utilities import io_worker as iw
from pywikibot.data.api import APIError


class PropertyWikidataIdentifier:
    def __init__(self):
        self.itemIdentifier = None
        self.propertyIdentifier = None

    @staticmethod
    def get_identifier(wikibase_site, wikibase_repo, i_type="QID"):
        # Search identifier
        for page in wikibase_site.search(
            f"Wikidata {i_type}",
            step=1,
            total=1,
            namespaces=wikibase_repo.property_namespace,
        ):
            page = pywikibot.PropertyPage(wikibase_repo, page.title())
            return page.id

        # Create new identifier
        wikibase_item = pywikibot.PropertyPage(wikibase_repo, datatype="external-id")
        try:
            wikibase_item.editEntity(
                {
                    "labels": {"en": f"Wikidata {i_type}"},
                    "descriptions": {"en": f"Corresponding {i_type} in Wikidata"},
                },
                summary="Insert a property to have a wikidata identifier",
            )
            iw.print_status(f"Inserted Wikidata {i_type} --> {wikibase_item.getID()}")
            return str(wikibase_item.getID())
        except (APIError, pywikibot.exceptions.OtherPageSaveError) as e:
            x = re.search(r"\[\[Property:.*\]\]", str(e))
            if x:
                return str(x.group(0).replace("[[Property:", "").split("|")[0])
            else:
                print("This should not happen 1")
        return None

    def get(self, wikibase_site, wikibase_repo):
        self.itemIdentifier = self.get_identifier(
            wikibase_site, wikibase_repo, i_type="QID"
        )
        self.propertyIdentifier = self.get_identifier(
            wikibase_site, wikibase_repo, i_type="PID"
        )
