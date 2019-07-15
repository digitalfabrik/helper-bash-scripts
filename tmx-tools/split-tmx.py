#!/usr/bin/env python3

import sys
import os
from lxml import etree
import copy

def generate_tmx(args):
	old_tree = etree.parse(os.path.join(os.getcwd(), args.input))
	old_body = old_tree.xpath('/tmx/body')[0]

	for old_tu in old_tree.xpath('/tmx/body/tu'):
		segments = get_segments(old_tu)
		if segments is not None and segments is not False:
			segments.set("changeid", "Integreat")
			old_body.append(segments)

	outfile = os.path.join(os.getcwd(), args.output)
	old_tree.write(outfile)

def get_segments(old_tu):
	bpt = old_tu.xpath("./tuv/seg/bpt")
	if len(bpt) > 0:
		elem = old_tu.xpath("./tuv/seg/bpt")
		return False

	new_translation = {}
	modified = False
	new_tu = copy.deepcopy(old_tu)
	for tuv in new_tu.findall("./tuv"):
		lang = tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']
		seg = tuv.findall("./seg")[0]
		# bad: <ph>&lt;br class="xliff-newline" /&gt;</ph>
		start = True
		text = ""
		for element in seg.iter():
			element, start, text, modified = test_element(element, start, text, modified)
		seg.text = text.strip()
	if modified:
		return new_tu
	else:
		return False

def test_element(element, start, text, modified, reverse=False):
	if start and element.tag == "ph":
		if element.tail is not None and element.tail.strip() != "":
			start = False
			text = text + element.tail
			delete_end(element)
		element.getparent().remove(element)
		modified = True
	elif element.tag == "seg":
		text = text + (element.text if element.text is not None else "")
	elif element.tag != "ph":
		start = False
	elif element.tag == "ph":
		delete_end(element)
	else:
		pass
	return element, start, text, modified

def delete_end(element):
	if element.tag == "ph" and element.getnext() == None:
		prev = element.getprevious()
		element.getparent().remove(element)
		if prev is not None:
			delete_end(prev)


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
