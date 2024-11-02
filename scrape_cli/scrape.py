#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# scrape: Extract HTML elements using an XPath query or CSS3 selector.
#
# Example usage:
# $ curl 'http://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
# | scrape -be 'table.wikitable > tr > td > b > a'
#
# Dependencies: lxml and cssselector
#
# Author: http://jeroenjanssens.com

import sys
import argparse
from lxml import etree
from cssselect import GenericTranslator
from sys import exit

def main():
    parser = argparse.ArgumentParser(description='Extract HTML elements using an XPath query or CSS3 selector.')
    parser.add_argument('html', nargs='?', type=argparse.FileType('rb'),
                        default=sys.stdin, help="HTML input (default: stdin)", metavar="HTML")
    parser.add_argument('-a', '--argument', default="",
                        help="Argument to extract from tag")
    parser.add_argument('-b', '--body', action='store_true', default=False,
                        help="Enclose output with HTML and BODY tags")
    parser.add_argument('-e', '--expression', default=[], action='append',
                        help="XPath query or CSS3 selector")
    parser.add_argument('-f', '--file', default='',
                        help="File to read input from")
    parser.add_argument('-x', '--check-existence', action='store_true', default=False,
                        help="Process return value signifying existence")
    parser.add_argument('-r', '--rawinput', action='store_true', default=False,
                        help="Do not parse HTML before feeding etree (useful for escaping CData)")
    args = parser.parse_args()

    # Check if the required arguments are provided
    if not args.expression:
        print("Error: You must provide at least one XPath query or CSS3 selector using the -e option.")
        parser.print_help()
        sys.exit(1)

    expression = [e if e.startswith('//') else GenericTranslator().css_to_xpath(e) for e in args.expression]

    html_parser = etree.HTMLParser(encoding='utf-8', recover=True, strip_cdata=True)

    inp = open(args.file, 'rb') if args.file else args.html
    if args.rawinput:
        document = etree.fromstring(inp.read())
    else:
        document = etree.parse(inp, html_parser)

    if args.body:
        sys.stdout.write("<!DOCTYPE html>\n<html>\n<body>\n")

    for e in expression:
        els = list(document.xpath(e))

        if args.check_existence:
            sys.exit(1 if len(els) == 0 else 0)

        for e in els:
            if isinstance(e, str):
                text = e
            elif not args.argument:
                text = etree.tostring(e, pretty_print=True).decode('utf-8')
            else:
                text = e.get(args.argument)
            if text is not None:
                sys.stdout.write(text.strip() + "\n")

    if args.body:
        sys.stdout.write("</body>\n</html>")

    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == "__main__":
    exit(main())
