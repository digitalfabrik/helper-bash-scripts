#!/usr/bin/env python3

import requests
import json
import sys

print("Searching for {}".format(sys.argv[1]))
r = requests.get("https://gvz.integreat-app.de/api/searchcounty/{}".format(sys.argv[1]))
text = r.content
regions = json.loads(text)
for region in regions:
    result = {}
    print()
    print("######################################################")
    print("{} ({})".format(region['name'], region['type']))
    print()
    for child in region['children']:
        r = requests.get("https://gvz.integreat-app.de/api/details/{}".format(child['key']))
        text = r.content
        location = json.loads(text)[0]
        if ',' in location['name']:
            location['name'] = location['name'].split(',')[0]
        result[location['name']] = {"longitude": location['longitude'], "latitude": location['latitude']}
    print(json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False)) 
