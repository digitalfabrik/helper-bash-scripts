#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys

if len(sys.argv)>1:
    site = sys.argv[1]
else:
    site = None

def get_site_content_size(site, single=False):
    total_size = 0
    lang_size_pdf_int = {}
    lang_size_pdf_ext = {}
    lang_size_img_int = {}
    lang_size_img_ext = {}
    available_permalinks = []

    url = "https://cms.integreat-app.de/{}/de/wp-json/extensions/v3/languages".format(site)
    r = requests.get(url, headers={"X-Integreat-Development":"1"})
    languages = r.json()

    pages = []
    resources = {}
    for lang in languages:
        lang_size_pdf_int[lang['code']] = 0
        lang_size_pdf_ext[lang['code']] = 0
        lang_size_img_int[lang['code']] = 0
        lang_size_img_ext[lang['code']] = 0
        resources[lang['code']] = {}
        r = requests.get("https://cms.integreat-app.de/{}/{}/wp-json/extensions/v3/pages".format(site, lang['code']), headers={"X-Integreat-Development":"1"})
        lang_pages = r.json()
        pages = pages + lang_pages

    for page in pages:
        available_permalinks.append(page['url'])

    for page in pages:
        soup = BeautifulSoup(page['content'], "lxml")
        for elem in soup.find_all('a', href=True) + soup.find_all('img', src=True):
            if elem.name == 'a':
                link = elem['href']
            elif elem.name == 'img':
                link = elem['src']
            else:
                continue
            lang = page['path'].split('/')[2]
            if link in resources[lang]:
                continue
            print((lang, link))
            if (link.endswith(".png") or
                link.endswith(".PNG") or
                link.endswith(".jpg") or
                link.endswith(".JPG") or
                link.endswith(".jpeg") or
                link.endswith(".JPEG") or
                link.endswith(".pdf") or
                link.endswith(".PDF")):
                size = 0
                try:
                    response = requests.head(link)
                    if "content-length" in response.headers:
                        size = int(response.headers['content-length'])
                except:
                    continue
                resources[lang][link] = size
                if(link.startswith('https://cms.integreat-app.de/') and link.endswith(".pdf")):
                    lang_size_pdf_int[lang] = lang_size_pdf_int[lang] + size
                elif(link.endswith(".pdf")):
                    lang_size_pdf_ext[lang] = lang_size_pdf_ext[lang] + size
                elif(link.startswith('https://cms.integreat-app.de/') and (link.endswith(".png") or link.endswith(".PNG") or link.endswith(".jpg") or link.endswith(".JPG") or link.endswith(".jpeg") or link.endswith(".JPEG"))):
                    lang_size_img_int[lang] = lang_size_img_int[lang] + size
                elif(link.endswith(".png") or link.endswith(".PNG") or link.endswith(".jpg") or link.endswith(".JPG") or link.endswith(".jpeg") or link.endswith(".JPEG")):
                    lang_size_img_ext[lang] = lang_size_img_ext[lang] + size
    print("City; Language; PDF internal; PDF external; Images internal; Images external")
    for lang in lang_size_pdf_int:
        print("{}; {}; {}; {}; {}; {}".format(site, lang, round(lang_size_pdf_int[lang]/(1024*1024), 2), round(lang_size_pdf_ext[lang]/(1024*1024), 2), round(lang_size_img_int[lang]/(1024*1024), 2), round(lang_size_img_ext[lang]/(1024*1024), 2)))
    
    if single:
        for lang in resources:
            for resource in resources[lang]:
                print("{}; {}; {}; {}".format(site, lang, resource, resources[lang][resource]))

if site is None:
    r = requests.get("https://cms.integreat-app.de/wp-json/extensions/v3/sites")
    for site in r.json():
        site = site['path'].strip("/")
        if site != "":
            get_site_content_size(site)
else:
    get_site_content_size(site, single=True)
