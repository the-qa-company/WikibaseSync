import requests
from datetime import datetime, timedelta


def get_wikidata_changes(rccontinue, hours):
    print(rccontinue)
    time = datetime.now() - timedelta(hours=hours)
    S = requests.Session()

    url = "https://wikidata.org/w/api.php"

    parameters = {
        "format": "json",
        "rcprop": "title",
        "list": "recentchanges",
        "action": "query",
        "rclimit": "500",

    }
    if rccontinue is not None:
        parameters['rccontinue'] = rccontinue

    R = S.get(url=url, params=parameters)
    data = R.json()
    S.close()

    date_time_obj = datetime.strptime(data['continue']['rccontinue'].split('|')[0], '%Y%m%d%H%M%S')
    print("time ",time," date_time_obj ",date_time_obj)
    if time < date_time_obj:
        older_changes = get_wikidata_changes(data['continue']['rccontinue'], hours)
        return data['query']['recentchanges'] + older_changes
    else:
        print("Finished")
        return data['query']['recentchanges']