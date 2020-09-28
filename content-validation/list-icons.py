#!/usr/bin/env python3
import requests
import json
import sys
import hashlib
#from __future__ import print_function

SERVER="https://cms.integreat-app.de"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_sites():
    r = requests.get("{}/wp-json/extensions/v3/sites".format(SERVER), headers={"X-Integreat-Development":"1"})
    for site in r.json():
        if site['live']:
            yield site['path'].strip("/")

def get_pages(site, languages):
    pages = []
    for lang in languages:
        url = "{}/{}/{}/wp-json/extensions/v3/pages".format(SERVER, site, lang)
        eprint("getting " + url)
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

def order_pages(pages):
    pages_level = {}
    level = 0
    empty_level = False
    while True:
        pages_level[level] = {}
        empty_level = True
        for page in pages:
            if level == 0:
                if page['parent']['id'] == 0:
                    pages_level[0][page['id']] = page
                    empty_level = False
            else:
                if page['parent']['id'] in pages_level[level - 1]:
                    pages_level[level][page['id']] = page
                    empty_level = False
        if empty_level:
            return pages_level
        else:
            level = level + 1

def hash_thumbnail(thumbnail_url):
    eprint("hashing " + thumbnail_url)
    r = requests.get(thumbnail_url)
    return hashlib.md5(r.content).hexdigest()

def generate_hash_dict(pages_level, hash_dict):
    for level in pages_level:
        for page_id in pages_level[level]:
            if pages_level[level][page_id]["thumbnail"]:
                hashsum = hash_thumbnail(pages_level[level][page_id]["thumbnail"])
                if hashsum in hash_dict:
                    if pages_level[level][page_id]["thumbnail"] not in hash_dict[hashsum]['urls']:
                        hash_dict[hashsum]['urls'].append(pages_level[level][page_id]["thumbnail"])
                    if level not in hash_dict[hashsum]['levels']:
                        hash_dict[hashsum]['levels'].append(level)
                else:
                    hash_dict[hashsum] = {}
                    hash_dict[hashsum]['urls'] = [pages_level[level][page_id]["thumbnail"]]
                    hash_dict[hashsum]['levels'] = [level]
    return hash_dict


def generate_html(hash_dict):
    print("<html><body><table><tr><th>Image</th><th>Count</th><th>Hash</th><th>Levels</th><th>URLs</th></tr>")
    for hashsum in hash_dict:
        print("<tr><td><img src='{}'></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            hash_dict[hashsum]['urls'][0],
            str(len(hash_dict[hashsum]['urls'])),
            hashsum,
            ', '.join(map(str, hash_dict[hashsum]['levels'])),
            ', '.join(hash_dict[hashsum]['urls'])))
    print("</table></body></html>")

def main():
    sites = [sys.argv[1]] if len(sys.argv) > 1 else get_sites()
    pages = []
    hash_dict = {}
    for site in sites:
        pages = pages + get_pages(site, ['de']) # german might be sufficient
        #pages = pages + get_pages(site, get_languages(site))
        ordered_pages = order_pages(pages)
        pages = []
        hash_dict = generate_hash_dict(ordered_pages, hash_dict)
        ordered_pages = []
    generate_html(hash_dict)
  
if __name__== "__main__":
    main()
