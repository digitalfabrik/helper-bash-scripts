#!/usr/bin/env python3

import json
import sys
import requests

print("Searching for {}".format(sys.argv[-1]))
r = requests.get("https://gvz.integreat-app.de/api/searchcounty/{}".format(sys.argv[-1]))
regions = json.loads(r.content)
for region in regions:
    result = {}
    print()
    print("######################################################")
    print("{} ({})".format(region['name'], region['type']))
    print()
    for child in region['children']:
        r = requests.get("https://gvz.integreat-app.de/api/details/{}".format(child['key']))
        location = json.loads(r.content)[0]
        if ',' in location['name']:
            location['name'] = location['name'].split(',')[0]
        result[location['name']] = {"longitude": location['longitude'], "latitude": location['latitude']}
    if '--pretty' in sys.argv:
        print(json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))
