#!/usr/bin/env python3
import requests
import json
import sys
from html.parser import HTMLParser
import re

SERVER="https://cms.integreat-app.de"

class MLStripper(HTMLParser):
    """
    Class for stripping Html Tags
    """
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    #this function takes html string as input and put data in
    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def count_words(html_string):
    word_string = strip_tags(html_string)
    words = re.findall(r'\w+', word_string)
    count = len(words)
    return count

def get_sites():
    r = requests.get("{}/wp-json/extensions/v3/sites".format(SERVER), headers={"X-Integreat-Development":"1"})
    for site in r.json():
        if site['live']:
            yield site['path'].strip("/")

def get_pages(site, languages):
    pages = []
    for lang in languages:
        url = "{}/{}/{}/wp-json/extensions/v3/pages".format(SERVER, site, lang)
        #print("getting " + url)
        r = requests.get(url, headers={"X-Integreat-Development":"1"})
        lang_pages = r.json()
        pages = pages + lang_pages
    return pages

def get_languages(site):
    r = requests.get("{}/{}/de/wp-json/extensions/v3/languages".format(SERVER, site), headers={"X-Integreat-Development":"1"})
    languages = r.json()
    result = []
    for lang in languages:
        yield lang['code']

def words_in_pages(pages):
    sum_content = 0
    for page in pages:
        sum_content = sum_content + count_words(page['content'])
    return sum_content

def main():
    sites = [sys.argv[1]] if len(sys.argv) > 1 else get_sites()
    print("site; words")
    for site in sites:
        pages = get_pages(site, ['de']) # german might be sufficient
        print(str(site) + "; " + str(words_in_pages(pages)))

if __name__== "__main__":
    main()
