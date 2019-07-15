#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys

site = sys.argv[1] if len(sys.argv)>1 else None

def get_site_content_size(site):
    total_size = 0
    lang_size = {}
    available_permalinks = []

    url = "https://cms.integreat-app.de/{}/de/wp-json/extensions/v3/languages".format(site)
    r = requests.get(url, headers={"X-Integreat-Development":"1"})
    languages = r.json()

    pages = []
    for lang in languages:
        lang_size[lang['code']] = 0
        r = requests.get("https://cms.integreat-app.de/{}/{}/wp-json/extensions/v3/pages".format(site, lang['code']), headers={"X-Integreat-Development":"1"})
        lang_pages = r.json()
        pages = pages + lang_pages

    for page in pages:
        available_permalinks.append(page['url'])

    for page in pages:
        soup = BeautifulSoup(page['content'], "lxml")
        for a in soup.find_all('a', href=True):
            link = a['href']
            if (link.endswith(".png") or
                link.endswith(".PNG") or
                link.endswith(".jpg") or
                link.endswith(".JPG") or
                link.endswith(".jpeg") or
                link.endswith(".JPEG") or
                link.endswith(".pdf") or
                link.endswith(".PDF") or
                (link.startswith('https://cms.integreat-app.de/{}/'.format(site)) and
                "/wp-content/uploads/" in link)):
                try:
                    response = requests.head(link)
                    lang = page['path'].split('/')[2]
                    if "content-length" in response.headers:
                        #print("{}; {}; {}".format(lang, link, response.headers['content-length']))
                        total_size = total_size + int(response.headers['content-length'])
                        lang_size[lang] = lang_size[lang] + int(response.headers['content-length'])
                except:
                    pass

    for lang in lang_size:
        print("{}; {}; {} MB".format(site, lang, round(lang_size[lang]/(1024*1024), 2)))
    #print("Total; "+str(round(total_size/(1024*1024),2))+" MB")

if site is None:
    r = requests.get("https://cms.integreat-app.de/wp-json/extensions/v3/sites")
    for site in r.json():
        site = site['path'].strip("/")
        if site != "":
            get_site_content_size(site)
else:
    get_site_content_size(site)
