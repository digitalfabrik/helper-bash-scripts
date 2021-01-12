#!/usr/bin/env python3

import os
import configparser
import dateutil.parser
import requests

TRANSLATION = {
    "de": {
        "incidence": "7-Tage-Inzidenz",
        "update": "Zuletzt aktualisiert",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiednen Inzidenz-Raten."
    },
    "en": {
        "incidence": "7 Day Incidence Rate",
        "update": "Last update",
        "info": "The pages below contain information about rules associated to incidence rates."
    }
}

REGIONS = configparser.ConfigParser()
REGIONS.read(os.path.join(os.getenv("HOME"), ".coronainfo", 'config.ini'))

CORONA_URL = "https://api.corona-zahlen.org/districts"
RESPONSE = requests.get(CORONA_URL).json()
LAST_UPDATE = dateutil.parser.parse(RESPONSE["meta"]["lastUpdate"]).strftime('%Y-%m-%d')

def create_message(cur_region, cur_incidence):
    language = cur_region.split("/")[1]
    content = "<p style=\"text-align: center; font-size: 1.6em;\">{}: <strong>{}</strong> | {}: {}</p>".format(
        TRANSLATION[language]["incidence"],
        cur_incidence,
        TRANSLATION[language]["update"],
        LAST_UPDATE)
    return content

for region in REGIONS:
    if region == "DEFAULT" or not REGIONS[region]["ags"] or not REGIONS[region]["token"]:
        continue
    incidence = round(float(RESPONSE["data"][REGIONS[region]["ags"]]["weekIncidence"]), 1)
    request_data = {"token": REGIONS[region]["token"], "content": create_message(region, incidence)}
    url = "https://cms.integreat-app.de/"+region+"/wp-json/extensions/v3/pushpage"
    p = requests.post(url, json=request_data)
    print(region + p.text)
