#!/usr/bin/env python3

import os
import configparser
import time
import datetime
import requests
import dateutil.parser
import pandas as pd
from openpyxl import load_workbook

TRANSLATION = {
    "de": {
        "incidence": "7-Tage-Inzidenz",
        "update": "am",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten."
    },
    "de-si": {
        "incidence": "7-Tage-Inzidenz",
        "update": "am",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten."
    },
    "am": {
        "incidence": "7 ቀን የመያዝ መጠን",
        "update": "መጋቢት"
    },
    "ar": {
        "incidence": "حدوث 7 أيام",
        "update": "في",
    },
    "bg": {
        "incidence": "Честота на инцидентите за 7 дни",
        "update": "на"
    },
    "en": {
        "incidence": "7 Day Incidence Rate",
        "update": "on",
        "info": "The pages below contain information about rules associated to incidence rates."
    },
    "el": {
        "incidence": "Ποσοστό επίπτωσης 7 ημερών",
        "update": "στις",
    },
    "es": {
        "incidence": "Incidencia de 7 días",
        "update": "el",
    },
    "fa": {
        "incidence": "بروز 7 روز",
        "update": "در",
    },
    "fr": {
        "incidence": "Incidence sur 7 jours",
        "update": "le",
    },
    "hr": {
        "incidence": "7-dnevna incidencija",
        "update": "na",
    },
    "hu": {
        "incidence": "7 napos előfordulási arány",
        "update": ""
    },
    "it": {
        "incidence": "Tasso di incidenza di 7 giorni",
        "update": "il",
    },
    "ku": {
        "incidence": "Bûyera 7-rojî",
        "update": "di",
    },
    "pl": {
        "incidence": "7-dniowa częstotliwość występowania",
        "update": "w dniu",
    },
    "ps": {
        "incidence": "بروز 7 روز",
        "update": "در",
    },
    "ro": {
        "incidence": "Incidență de 7 zile",
        "update": "la",
    },
    "ru": {
        "incidence": "7-дневная заболеваемость",
        "update": "",
    },
    "so": {
        "incidence": "Dhacdooyinka 7-maalin",
        "update": "markay ahayd",
    },
    "sr": {
        "incidence": "Стопа инциденце од 7 дана",
        "update": "",
    },
    "ti": {
        "incidence": "ናይ 7 መዓልቲ ክስተት",
        "update": "on",
    },
    "tr": {
        "incidence": "7 günlük insidans",
        "update": ",",
    }
}

REGIONS = configparser.ConfigParser()
REGIONS.read(os.path.join(os.getenv("HOME"), ".coronainfo", 'config.ini'))

def parse_arcgis():
    CORONA_URL = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=false&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&returnZ=false&returnM=false&returnExceededLimitFeatures=true&f=pjson"
    RESPONSE = requests.get(CORONA_URL).json()["features"]
    DATA = {}
    for region in RESPONSE:
        ags = region["attributes"]["AGS"]
        LAST_UPDATE = datetime.datetime.strptime(region["attributes"]["last_update"], '%d.%m.%Y, %H:%M Uhr').strftime('%Y-%m-%d')
        DATA[ags] = region["attributes"]["cases7_per_100k"]
    return LAST_UPDATE, DATA

def parse_rki_xlsx():
    CORONA_URL = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Fallzahlen_Kum_Tab.xlsx?__blob=publicationFile"
    RESPONSE = requests.get(CORONA_URL, allow_redirects=True)
    XLSX_PATH = "rki-archive/{}.xlsx".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    open(XLSX_PATH, 'wb').write(RESPONSE.content)
    workbook = load_workbook(filename = XLSX_PATH)
    worksheet = workbook["7Tage_LK"]
    LAST_UPDATE = datetime.datetime.strptime(worksheet["A2"].value, 'Stand: %d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d')
    DATA = {}
    for row in range(1, 450):
        if worksheet["D"+str(row)].value and worksheet["D"+str(row)].value != "Inzidenz":
            DATA[worksheet["B"+str(row)].value] = worksheet["D"+str(row)].value
    return LAST_UPDATE, DATA

try:
    LAST_UPDATE, DATA = parse_arcgis()
    print("Using Arcgis")
except:
    LAST_UPDATE, DATA = parse_rki_xlsx()
    print("Using RKI Excel")

def create_message(cur_region, cur_incidence):
    language = cur_region.split("/")[1]
    if language not in TRANSLATION:
        return None
    content = "<p style=\"text-align: center; font-size: 1.6em;\">{}: <strong>{}</strong> {} {}</p>".format(
        TRANSLATION[language]["incidence"],
        cur_incidence,
        TRANSLATION[language]["update"],
        LAST_UPDATE)
    return content

for region in REGIONS:
    if region == "DEFAULT" or not REGIONS[region]["ags"] or not REGIONS[region]["token"]:
        continue
    incidence = round(DATA[REGIONS[region]["ags"]], 1)
    message = create_message(region, incidence)
    if message is None:
        continue
    try:
        request_data = {"token": REGIONS[region]["token"], "content": message}
        url = "https://cms.integreat-app.de/"+(REGIONS[region]["address"] if "address" in REGIONS[region] else region)+"/wp-json/extensions/v3/pushpage"
        p = requests.post(url, json=request_data)
        print(region + p.text)
        url_string = 'https://monitoring.tuerantuer.org/write?db=cms'
        data_string = 'corona,host=server12,status=success,target={} value={} {}'.format(region, 1 if p.json()["status"]=="success" else 0, str(time.time()).split(".")[0]+"000000000")
        r = requests.post(url_string, data=data_string, cert=('/etc/pki/client.crt', '/etc/pki/client.key'), verify="/usr/local/share/ca-certificates/ca.crt")
    except:
        try:
            data_string = 'corona,host=server12,status=success,target={} value={} {}'.format(region, 0, str(time.time()).split(".")[0]+"000000000")
            r = requests.post(url_string, data=data_string, cert=('/etc/pki/client.crt', '/etc/pki/client.key'), verify="/usr/local/share/ca-certificates/ca.crt")
        except:
            pass
        print("Error for {}".format(region))
