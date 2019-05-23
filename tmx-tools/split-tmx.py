#!/usr/bin/env python3

import sys
import os
from xml.etree import ElementTree, cElementTree


def generate_tmx(args):
	old_tree = ElementTree.parse(os.path.join(os.getcwd(), args.input))


	new_root = cElementTree.Element("tmx", version="1.4")

	outfile = os.path.join(os.getcwd(), args.output)
	new_tree = cElementTree.ElementTree(new_root)
	new_tree.write(outfile)

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
