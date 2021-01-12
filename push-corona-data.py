#!/usr/bin/env python3

import os
import configparser
import dateutil.parser
import requests

TRANSLATION = {}
TRANSLATION["de"]["incidence"] = "7-Tage-Inzidenz"
TRANSLATION["de"]["update"] = "Zuletzt aktualisiert"
TRANSLATION["en"]["incidence"] = "7 Day Incidence Rate"
TRANSLATION["en"]["update"] = "Last update"

REGIONS = configparser.ConfigParser()
REGIONS.read(os.path.join(os.getenv("HOME"), ".coronainfo", 'config.ini'))

CORONA_URL = "https://api.corona-zahlen.org/districts"
RESPONSE = requests.get(CORONA_URL).json()
LAST_UPDATE = dateutil.parser.parse(RESPONSE["meta"]["lastUpdate"]).strftime('%Y-%m-%d')

def create_message(cur_region, cur_incidence):
    language = cur_region.split("/")[1]
    if cur_incidence > 200:
        cur_incidence = str(cur_incidence) + "⚠️"
    content = "<p style=\"text-align: center;\">{}: <strong>{}</strong> | {}: {}</p>".format(
        TRANSLATION[language]["incidence"],
        cur_incidence,
        LAST_UPDATE,
        TRANSLATION[language]["update"])
    return content

for region in REGIONS:
    if region == "DEFAULT" or not REGIONS[region]["ags"] or not REGIONS[region]["token"]:
        continue
    incidence = round(float(RESPONSE["data"][REGIONS[region]["ags"]]["weekIncidence"]), 1)
    request_data = {"token": REGIONS[region]["token"], "content": create_message(region, incidence)}
    url = "https://cms.integreat-app.de/"+region+"/wp-json/extensions/v3/pushpage"
    p = requests.post(url, json=request_data)
