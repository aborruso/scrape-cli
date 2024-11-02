#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# scrape: Extract HTML elements using an XPath query or CSS3 selector.
#
# Example usage:
# $ curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
# | scrape -e 'table.wikitable > tbody > tr > td > b > a'
#
# Dependencies: lxml, cssselector, requests
#
# Author: http://jeroenjanssens.com

import sys
import argparse
import requests
from lxml import etree
from cssselect import GenericTranslator
from sys import exit

def is_xpath(expression):
    # Check if the provided expression is XPath (instead of a CSS selector)
    return expression.startswith("//")

def main():
    # Command line argument parser definition
    parser = argparse.ArgumentParser(
        description='Extract HTML elements using an XPath query or CSS3 selector.',
        epilog='Example: cat page.html | python scrape.py -e "//a/@href"'
    )
    # Defines the HTML input argument (can be a file, URL or stdin)
    parser.add_argument('html', nargs='?', type=str, default='',
                        help="HTML input (file, URL or stdin, default: stdin)", metavar="HTML")
    # Defines the optional argument to extract from the tag
    parser.add_argument('-a', '--argument', default="",
                        help="Argument to extract from the tag")
    # Option to include the result within HTML and BODY tags
    parser.add_argument('-b', '--body', action='store_true', default=False,
                        help="Include result in HTML and BODY tags")
    # Allows to specify one or more XPath or CSS3 selector expressions
    parser.add_argument('-e', '--expression', default=[], action='append',
                        help="XPath query or CSS3 selector")
    # Option to verify the existence of elements matching the expression
    parser.add_argument('-x', '--check_existence', action='store_true', default=False,
                        help="Returns an exit value indicating existence")
    # Option to avoid initial HTML parsing, useful in specific cases like CData
    parser.add_argument('-r', '--rawinput', action='store_true', default=False,
                        help="Do not parse HTML before passing to etree (useful for CData)")
    parser.add_argument('--check-existence', dest='check_existence', action='store_true')
    args = parser.parse_args()

    # Check that at least one expression is provided by the user
    if not args.expression:
        sys.exit("Error: you must provide at least one XPath query or CSS3 selector using the -e option.")
        parser.print_help()
        sys.exit(1)

    # Determine the source of the input: URL, file, or stdin
    if args.html:
        if args.html.startswith('http://') or args.html.startswith('https://'):
            # If the input is a URL, download the HTML content
            try:
                response = requests.get(args.html)
                response.raise_for_status()
                inp = response.content
            except requests.RequestException as e:
                print(f"Error downloading HTML: {e}")
                sys.exit(1)
        else:
            # If the input is a local file, try to open it
            try:
                inp = open(args.html, 'rb').read()
            except FileNotFoundError:
                print(f"Error: The file '{args.html}' was not found.")
                sys.exit(1)
    else:
        # If the input is from stdin
        inp = sys.stdin.buffer.read()

    # Convert CSS selectors to XPath if necessary
    expression = [e if is_xpath(e) else GenericTranslator().css_to_xpath(e) for e in args.expression]

    # Create an HTML parser with options for error recovery
    html_parser = etree.HTMLParser(encoding='utf-8', recover=True)

    # Try to parse the HTML input
    try:
        if args.rawinput:
            # If rawinput is enabled, do not use the HTML parser
            document = etree.fromstring(inp)
        else:
            document = etree.fromstring(inp, html_parser)
    except etree.XMLSyntaxError as e:
        # Print an error in case of syntax issues in the HTML
        print(f"Error parsing HTML: {e}")
        sys.exit(1)

    results = []
    # For each expression, perform the search in the parsed HTML
    for e in expression:
        els = list(document.xpath(e))

        # If check-existence is enabled, return 0 or 1 depending on the existence of elements
        if args.check_existence:
            sys.exit(1 if len(els) == 0 else 0)

        # Extract the text or content of the found elements
        for el in els:
            if isinstance(el, str):
                # If the element is a string, use the text directly
                text = el
            elif not args.argument:
                # If no attribute is specified, return the element as HTML string
                text = etree.tostring(el, pretty_print=True).decode('utf-8')
            else:
                # Otherwise, extract the specified attribute
                text = el.get(args.argument)
            if text is not None:
                results.append(text.strip())

        # Output handling
        if args.body:
            sys.stdout.write("<!DOCTYPE html>\n<html>\n<body>\n")
            for result in results:
                sys.stdout.write(result + "\n")
            sys.stdout.write("</body>\n</html>\n")
        else:
            # Normal output
            for result in results:
                sys.stdout.write(result + "\n")

        sys.stdout.flush()

if __name__ == "__main__":
    exit(main())
