#!/usr/bin/env python3

import sys
import os
#from xml.etree import ElementTree, cElementTree
from lxml import etree
import copy

def generate_tmx(args):
	old_tree = etree.parse(os.path.join(os.getcwd(), args.input))
	old_body = old_tree.xpath('/tmx/body')

	new_tree = copy.deepcopy(old_tree)
	new_body = new_tree.xpath('/tmx/body')

	for old_tu in old_tree.xpath('/tmx/body/tu'):
		segments = get_segments(old_tu)
		#new_tu = etree.SubElement(body, changedate=old_tu.attrib['changedate'])

	outfile = os.path.join(os.getcwd(), args.output)
	new_tree = cElementTree.ElementTree(new_root)
	new_tree.write(outfile)

def get_segments(old_tu):
	bpt = True if old_tu.xpath(".//tuv/seg/bpt") else False

	if not bpt:
		return False
	new_translation = {}
	for old_tuv in old_tu.findall(".//tuv"):
		lang = old_tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']
		print ("")
		print ("--- NEW TUV ---")
		print ("")
		seg = old_tuv.findall(".//seg")[0]
		print("Segment text: {}".format(seg.text))
		for ph in seg.findall(".//ph"):
			print("PH text: {}".format(ph.text))
			print("PH tail: {}".format(ph.tail))

def parse_cli(cliargs=None):
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("input",
						metavar="INPUT",
						help="Input translation memory (tmx) file",
						)
	parser.add_argument("output",
						metavar="OUTPUT",
						help="Output translation memory (tmx) file",
						)
	args = parser.parse_args(args=cliargs)
	return args

if __name__ == "__main__":
	args = parse_cli()
	print(args)
	generate_tmx(args)
