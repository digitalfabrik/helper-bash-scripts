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
        "info": "Die Seiten unten enthalten Informationen zu geltenden Einschränkungen bei verschiedenen Inzidenz-Raten.",
        "refresh": "Zum Aktualisieren nach unten ziehen.",
    },
    "de-si": {
        "incidence": "In den letzten 7 Tagen sind so viele Menschen vom Corona-Virus krank geworden",
        "update": "am",
        "refresh": "Wischen Sie auf dem Bildschirm nach unten. So sehen Sie die immer die aktuelle Zahl.",
    },
    "am": {
        "incidence": "7 ቀን የመያዝ መጠን",
        "update": "መጋቢት",
        "refresh": "ሪፍረሽ ለማድረግ/ለማደስ ወደ ታች ይጎትቱ።",
    },
    "ar": {
        "incidence": "حدوث 7 أيام",
        "update": "في",
        "refresh": "للتحديث اسحب إلى أسفل.",
    },
    "bg": {
        "incidence": "Честота на инцидентите за 7 дни",
        "update": "на",
        "refresh": "Плъзнете надолу за опресняване.",
    },
    "ckb": {
        "incidence": "7 ڕۆژ ڕێژەی ڕوودانی",
        "update": "",
        "refresh": "بۆ بەڕۆژکردنەوە بۆ لای خوارەوەی دابکێشە."
    },
    "en": {
        "incidence": "7 Day Incidence Rate",
        "update": "on",
        "info": "The pages below contain information about rules associated to incidence rates.",
        "refresh": "Pull down to refresh.",
    },
    "el": {
        "incidence": "Ποσοστό επίπτωσης 7 ημερών",
        "update": "στις",
        "refresh": "Σύρετε προς τα κάτω για ανανέωση περιεχομένου.",
    },
    "es": {
        "incidence": "Incidencia de 7 días",
        "update": "el",
        "refresh": "Deslice hacia abajo para actualizar.",
    },
    "fa": {
        "incidence": "بروز 7 روز",
        "update": "در",
        "refresh": "برای تازه کردن به پایین بکشید.",
    },
    "fr": {
        "incidence": "Incidence sur 7 jours",
        "update": "le",
        "refresh": "Tirer vers le bas pour actualiser.",
    },
    "hr": {
        "incidence": "7-dnevna incidencija",
        "update": "na",
        "refresh": "Da biste ažurirali, povucite prstom prema dolje.",
    },
    "hu": {
        "incidence": "7 napos előfordulási arány",
        "update": "",
        "refresh": "Az aktualizáláshoz húzza le.",
    },
    "it": {
        "incidence": "Tasso di incidenza di 7 giorni",
        "update": "il",
        "refresh": "Trascina verso il basso per aggiornare.",
    },
    "ka": {
        "incidence": "",
        "update": "",
        "refresh": "აქტუალიზირებისათვის ჩამოფურცლეთ ქვემოთ."
    },
    "kmr": {
        "incidence": "Rêjeya bûyerên 7 rojan",
        "update": "",
        "refresh": "Jibo nûkirinê bikişîne xwarê."
    },
    "ku": {
        "incidence": "Bûyera 7-rojî",
        "update": "di",
        "refresh": "Ji bo nûvekêşanê dakêşin.",
    },
    "mk": {
        "incidence": "",
        "update": "",
        "refresh": "За ажурирање повлечете надолу."
    },
    "pes": {
        "incidence": "",
        "update": "",
        "refresh": "برای به روز رسانی به پایین بکشید."
    },
    "pl": {
        "incidence": "7-dniowa częstotliwość występowania",
        "update": "w dniu",
        "refresh": "Aby zaktualizować, przeciągnij w dół.",
    },
    "ps": {
        "incidence": "بروز 7 روز",
        "update": "در",
        "refresh": "د تازه کولو لپاره کښته کیږئ.",
    },
    "ro": {
        "incidence": "Incidență de 7 zile",
        "update": "la",
        "refresh": "Pentru actualizare, trageți în jos.",
    },
    "ru": {
        "incidence": "7-дневная заболеваемость",
        "update": "",
        "refresh": "Для обновления проведите вниз.",
    },
    "so": {
        "incidence": "Dhacdooyinka 7-maalin",
        "update": "markay ahayd",
        "refresh": "Hoos u jiid si aad u nasato.",
    },
    "sq": {
        "incidence": "",
        "update": "",
        "refresh": "Tërhiqeni për ta rifreskuar."
    },
    "sr": {
        "incidence": "Стопа инциденце од 7 дана",
        "update": "",
        "refresh": "За ажурирање превући надоле.",
    },
    "sr-Latn": {
        "incidence": "7-dnevna incidenca",
        "update": "",
        "refresh": "Za ažuriranje prevući nadole."
    },
    "sr-latn": {
        "incidence": "7-dnevna incidenca",
        "update": "",
        "refresh": "Za ažuriranje prevući nadole."
    },
    "ti": {
        "incidence": "ናይ 7 መዓልቲ ክስተት",
        "update": "on",
        "refresh": "ዕረፍቲ ንምርካብ ስጕምቲ ውሰዱ።",
    },
    "tr": {
        "incidence": "7 günlük insidans",
        "update": ",",
        "refresh": "Yenilemek için aşağıya çekin.",
    },
    "uk": {
        "incidence": "7-денна захворюваність",
        "update": ",",
        "refresh": "Перетягніть вниз, щоб оновити.",
    },
    "zh-cn": {
        "incidence": "7天发病率",
        "update": ",",
        "refresh": "下拉刷新。",
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
        DATA[ags] = region["attributes"]["cases7_per_100k"]
        if "last_update" not in region["attributes"] or region["attributes"]["last_update"] == "":
            continue
        LAST_UPDATE = datetime.datetime.strptime(region["attributes"]["last_update"], '%d.%m.%Y, %H:%M Uhr').strftime('%Y-%m-%d')
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
    content = "<p style=\"text-align: center; font-size: 1.6em;\">{}: <strong>{}</strong> {} {}</p><p style=\"text-align: center;\">{}</p>".format(
        TRANSLATION[language]["incidence"],
        cur_incidence,
        TRANSLATION[language]["update"],
        LAST_UPDATE,
        TRANSLATION[language]["refresh"])
    return content

for region in REGIONS:
    if region == "DEFAULT":
        continue
    mon_url = 'https://monitoring.tuerantuer.org/write?db=cms'
    if "token" not in REGIONS[region] or "ags" not in REGIONS[region] or not REGIONS[region]["ags"] or not REGIONS[region]["token"]:
        continue
    incidence = round(DATA[REGIONS[region]["ags"]], 1)
    message = create_message(region, incidence)
    if message is None:
        continue
    try:
        request_data = {"token": REGIONS[region]["token"], "content": message}
        url = "https://cms.integreat-app.de/"+(REGIONS[region]["address"] if "address" in REGIONS[region] else region)+"/wp-json/extensions/v3/pushpage/"
        p = requests.post(url, json=request_data)
        print(region + p.text)
        data_string = 'corona,host=server12,status=success,target={} value={} {}'.format(region, 1 if p.json()["status"]=="success" else 0, str(time.time()).split(".")[0]+"000000000")
        r = requests.post(mon_url, data=data_string, cert=('/etc/pki/client.crt', '/etc/pki/client.key'), verify="/usr/local/share/ca-certificates/ca.crt")
    except:
        try:
            data_string = 'corona,host=server12,status=success,target={} value={} {}'.format(region, 0, str(time.time()).split(".")[0]+"000000000")
            r = requests.post(mon_url, data=data_string, cert=('/etc/pki/client.crt', '/etc/pki/client.key'), verify="/usr/local/share/ca-certificates/ca.crt")
        except:
            pass
        print("Error for {}".format(region))
