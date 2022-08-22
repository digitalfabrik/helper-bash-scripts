#!/usr/bin/env python3
"""
This script takes the XML export file from WordPress and creates a CSV form
"""
import xml.etree.ElementTree as ET

WP_NAMESPACE = "http://wordpress.org/export/1.2/"

XML_FILE = "PATH to XML file"

TREE = ET.parse(XML_FILE).getroot()

CHANNEL = TREE.find("./channel")

ITEMS = CHANNEL.findall("item")

with open("feedback.txt", "w") as f:
    for item in ITEMS:
        title = item[0].text
        comments = item.findall(f"./{{{WP_NAMESPACE}}}comment")
        for comment in comments:
            comment_id = comment[0].text
            meta = comment[13]
            commentary = meta[1].text
            f.writelines(title + "\n")
            f.writelines(commentary + "\n")
            f.writelines("\n")
