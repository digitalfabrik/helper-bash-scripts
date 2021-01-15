#!/usr/bin/env python3

import os
import configparser
import datetime
import requests
import dateutil.parser
import pandas as pd
from openpyxl import load_workbook

TRANSLATION = {
    "de": {
        "incidence": "7-Tage-Inzidenz",
        "update": "Zuletzt aktualisiert",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten."
    },
    "de-si": {
        "incidence": "7-Tage-Inzidenz",
        "update": "Zuletzt aktualisiert",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten."
    },
    "ar": {
        "incidence": "حدوث 7 أيام",
        "update": "التغيير الأخير",
    },
    "en": {
        "incidence": "7 Day Incidence Rate",
        "update": "Last update",
        "info": "The pages below contain information about rules associated to incidence rates."
    },
    "el": {
        "incidence": "Ποσοστό επίπτωσης 7 ημερών",
        "update": "τελευταία ενημέρωση",
    },
    "es": {
        "incidence": "Incidencia de 7 días",
        "update": "Última modificación",
    },
    "fa": {
        "incidence": "بروز 7 روز",
        "update": "آخرین تغییرات",
    },
    "fr": {
        "incidence": "Incidence sur 7 jours",
        "update": "Dernière modification",
    },
    "hr": {
        "incidence": "7-dnevna incidencija",
        "update": "Zadnja promjena",
    },
    "it": {
        "incidence": "Tasso di incidenza di 7 giorni",
        "update": "Ultimo aggiornamento",
    },
    "ku": {
        "incidence": "Bûyera 7-rojî",
        "update": "Guhertinên herî dawî",
    },
    "pl": {
        "incidence": "7-dniowa częstotliwość występowania",
        "update": "Ostania zmiana",
    },
    "ps": {
        "incidence": "بروز 7 روز",
        "update": "آخري تغیر",
    },
    "ro": {
        "incidence": "Incidență de 7 zile",
        "update": "Ultima modificare",
    },
    "ru": {
        "incidence": "7-дневная заболеваемость",
        "update": "Последнее изменение",
    },
    "so": {
        "incidence": "Dhacdooyinka 7-maalin",
        "update": "Bedelkii ugu dambeeyay",
    },
    "sr": {
        "incidence": "Стопа инциденце од 7 дана",
        "update": "Zadnja promena",
    },
    "ti": {
        "incidence": "ናይ 7 መዓልቲ ክስተት",
        "update": "ናይ መወዳእታ እዋን ለውጢ፥",
    },
    "tr": {
        "incidence": "7 günlük insidans",
        "update": "Son değişiklik",
    }
}

REGIONS = configparser.ConfigParser()
REGIONS.read(os.path.join(os.getenv("HOME"), ".coronainfo", 'config.ini'))

def parse_rki_xlsx():
    CORONA_URL = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Fallzahlen_Kum_Tab.xlsx?__blob=publicationFile"
    RESPONSE = requests.get(CORONA_URL, allow_redirects=True)
    open('data.xlsx', 'wb').write(RESPONSE.content)
    workbook = load_workbook(filename = 'data.xlsx')
    worksheet = workbook["7Tage_LK"]
    LAST_UPDATE = datetime.datetime.strptime(worksheet["A2"].value, 'Stand: %d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d')
    DATA = {}
    for row in range(1, 450):
        if worksheet["D"+str(row)].value and worksheet["D"+str(row)].value != "Inzidenz":
            DATA[worksheet["B"+str(row)].value] = worksheet["D"+str(row)].value
    return LAST_UPDATE, DATA

def parse_corona_zahlen():
    CORONA_URL = "https://api.corona-zahlen.org/districts"
    RESPONSE = requests.get(CORONA_URL).json()
    LAST_UPDATE = dateutil.parser.parse(RESPONSE["meta"]["lastUpdate"]).strftime('%Y-%m-%d')
    DATA = {}
    for region in RESPONSE["data"]:
        DATA[region] = RESPONSE["data"][region]["ags"]
    return LAST_UPDATE, DATA

try:
    LAST_UPDATE, DATA = parse_rki_xlsx()
    print("Using official RKI data.")
except:
    LAST_UPDATE, DATA = parse_corona_zahlen()
    pritn("Use secondary source.")

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
    incidence = round(DATA[REGIONS[region]["ags"]], 1)
    request_data = {"token": REGIONS[region]["token"], "content": create_message(region, incidence)}
    url = "https://cms.integreat-app.de/"+region+"/wp-json/extensions/v3/pushpage"
    p = requests.post(url, json=request_data)
    print(region + p.text)
