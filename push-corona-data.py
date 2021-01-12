#!/usr/bin/env python3

import os
import configparser
import dateutil.parser
import requests

TRANSLATION = {
    "de": {
        "incidence": "7-Tage-Inzidenz",
        "update": "Zuletzt aktualisiert",
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten."
    },
    "ar": {
        "incidence": "حدوث 7 أيام",
        "lastUpdate": "التغيير الأخير",
    },
    "en": {
        "incidence": "7 Day Incidence Rate",
        "update": "Last update",
        "info": "The pages below contain information about rules associated to incidence rates."
    },
    "es": {
        "incidence": "Incidencia de 7 días",
        "lastUpdate": "Última modificación",
    },
    "fa": {
        "incidence": "بروز 7 روز",
        "lastUpdate": "آخرین تغییرات",
    },
    "fr": {
        "incidence": "Incidence sur 7 jours",
        "lastUpdate": "Dernière modification",
    },
    "hr": {
        "incidence": "7-dnevna incidencija",
        "lastUpdate": "Zadnja promjena",
    },
    "ku": {
        "incidence": "Bûyera 7-rojî",
        "lastUpdate": "Guhertinên herî dawî",
    },
    "pl": {
        "incidence": "7-dniowa częstotliwość występowania",
        "lastUpdate": "Ostania zmiana",
    },
    "ps": {
        "incidence": "بروز 7 روز",
        "lastUpdate": "آخري تغیر",
    },
    "ro": {
        "incidence": "Incidență de 7 zile",
        "lastUpdate": "Ultima modificare",
    },
    "ru": {
        "incidence": "7-дневная заболеваемость",
        "lastUpdate": "Последнее изменение",
    },
    "so": {
        "incidence": "Dhacdooyinka 7-maalin",
        "lastUpdate": "Bedelkii ugu dambeeyay",
    },
    "sr": {
        "incidence": "Стопа инциденце од 7 дана",
        "lastUpdate": "Zadnja promena",
    },
    "ti": {
        "incidence": "ናይ 7 መዓልቲ ክስተት",
        "lastUpdate": "ናይ መወዳእታ እዋን ለውጢ፥",
    },
    "tr": {
        "incidence": "7 günlük insidans",
        "lastUpdate": "Son değişiklik",
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
