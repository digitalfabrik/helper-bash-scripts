#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys

site = sys.argv[1]

r = requests.get("https://cms.integreat-app.de/{}/de/wp-json/extensions/v3/languages".format(site))
languages = r.json()

pages = []

def get_all_pages( languages, pages ):
    for lang in languages:
        r = requests.get("https://cms.integreat-app.de/{}/{}/wp-json/extensions/v3/pages".format(site, lang['code']))
        lang_pages = r.json()
        pages = pages + lang_pages
    return pages

pages = get_all_pages(languages, pages)
available_permalinks = []

for page in pages:
    available_permalinks.append(page['url'])

for page in pages:
    soup = BeautifulSoup(page['content'], "lxml")
    invalid = []
    for a in soup.find_all('a', href=True):
        link = a['href']
        if not link.endswith('/'):
            link = link + '/'
        if (link.startswith('https://cms.integreat-app.de/{}/'.format(site)) and
            "/wp-content/uploads/" not in link and
            link not in available_permalinks):
            invalid.append(link)
    if invalid:
        print("")
        print("------")
        print("")
        print("Errors in {}".format(page['title']))
        print("Edit: https://cms.integreat-app.de/{}/wp-admin/post.php?post={}&action=edit&lang=de".format(site, page['id']))
        print("URL: {}".format(page['url']))
        for link in invalid:
            print("  INVALID: {}".format(link))
