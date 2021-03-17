import requests
from datetime import datetime, timedelta,timezone


def recent_changes(rccontinue, minutes, url ="https://wikidata.org/w/api.php"):
    time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    S = requests.Session()



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


    date_time_obj = datetime.strptime(data['continue']['rccontinue'].split('|')[0], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
    date_time_obj = date_time_obj.astimezone(timezone.utc)
    print("time ",time," date_time_obj ",date_time_obj)
    if time < date_time_obj:
        older_changes = recent_changes(data['continue']['rccontinue'], minutes)
        return data['query']['recentchanges'] + older_changes
    else:
        print("Finished")
        return data['query']['recentchanges']

recent_changes(None, 30)