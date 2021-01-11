#!/usr/bin/env python3

import os
import dateutil.parser
import requests
import configparser

regions = configparser.ConfigParser()
regions.read(os.path.join(os.getenv("HOME"), ".coronainfo", 'config.ini'))

corona_url = "https://api.corona-zahlen.org/districts"
r = requests.get(corona_url).json()
meta = r["meta"]
data = r["data"]
last_update = dateutil.parser.parse(meta["lastUpdate"]).strftime('%Y-%m-%d')
for region in regions:
    if region == "DEFAULT" or not regions[region]["ags"] or not regions[region]["token"]:
        continue
    incidence = round(float(data[regions[region]["ags"]]["weekIncidence"]), 2)
    content = "<p style=\"text-align: center;\">7-Tage-Inzidenz: <strong>{}</strong> | Zuletzt aktualisiert: {}</p>".format(incidence, last_update)
    data = {"token": regions[region]["token"], "content": content}
    url = "https://cms.integreat-app.de/"+region+"/wp-json/extensions/v3/pushpage"
    p = requests.post(url, json=data)
