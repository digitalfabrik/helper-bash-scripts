#!/usr/bin/env python3
"""
Search for region in gvz.tuerantuer.org and get all coordinates for child nodes
"""

import json
import sys
import requests

def parse_coordinates(division):
    """
    Parse coordinates and name from division and return dict
    """
    if division["division_category"] == 60:
        if ',' in division['name']:
            division['name'] = division['name'].split(',')[0]
        return {division['name']:
                {"longitude": division['longitude'], "latitude": division['latitude']}}
    return {}


def get_child_coordinates(parent_id):
    """
    Recursively retrieve children and get all leave node coordinates
    """
    json_response = requests.get(
        "https://gvz.tuerantuer.org/api/administrative_divisions/?parent={}".format(
            parent_id)).json()
    result = {}
    for child in json_response['results']:
        result.update(parse_coordinates(child))
        result.update(get_child_coordinates(child["id"]))
    return result


def search():
    """
    Search for user input string
    """
    print("Searching for {}".format(sys.argv[-1]))
    json_response = requests.get(
        "https://gvz.integreat-app.de/api/administrative_divisions/?search={}".format(
            sys.argv[-1])).json()
    for region in json_response["results"]:
        print()
        print("######################################################")
        print("{} ({})".format(region['name'], region['division_type_name']))
        print()
        result = parse_coordinates(region)
        result.update(get_child_coordinates(region["id"]))
        if '--pretty' in sys.argv:
            print(json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))

search()
