#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# scrape: Extract HTML elements using an XPath query or CSS3 selector.
#
# Example usage:
# $ curl 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
# | scrape -e 'table.wikitable > tbody > tr > td > b > a'
#
# Dependencies: lxml, cssselect, requests, xmltodict
#
# Author: http://jeroenjanssens.com

import os
import sys
import re
import json
import argparse
import requests
import xmltodict
from lxml import etree
from cssselect import GenericTranslator
from xml.parsers.expat import ExpatError
from xml.sax.saxutils import escape

# Read version from __init__.py
init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
with open(init_file) as f:
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", f.read())
    __version__ = version_match.group(1) if version_match else "unknown"

from sys import exit

def clean_text(text):
    """
    Clean text by:
    - Removing multiple consecutive empty lines (max 1 empty line)
    - Replacing multiple spaces with single space
    - Removing leading whitespace from lines
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace any sequence of 3 or more newlines with just 2 newlines (max 1 empty line)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace newlines with whitespace followed by more newlines with just 2 newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    # Remove leading and trailing whitespace from each line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # Remove trailing whitespace at the end
    text = text.strip()
    return text

def convert_css_to_xpath(expression):
    try:
        return GenericTranslator().css_to_xpath(expression)
    except Exception as e:
        print(f"Error converting CSS selector to XPath: {e}", file=sys.stderr)
        sys.exit(1)

def xpath_result_items(result):
    """XPath functions return a single string, number or boolean instead of a node list."""
    if isinstance(result, list):
        return result
    if isinstance(result, bool):
        return ['true' if result else 'false']
    if isinstance(result, float):
        return [str(int(result)) if result.is_integer() else str(result)]
    return [result] if result else []


def wrap_in_body(results):
    return "<!DOCTYPE html>\n<html>\n<body>\n" + "".join(r + "\n" for r in results) + "</body>\n</html>\n"


def is_xpath(expression):
    """
    Check if the expression is XPath by looking for common XPath patterns:
    - Starts with / or //
    - Contains XPath axes (::)
    - Contains node tests with parentheses
    - Contains predicates with square brackets
    - Contains position functions like last() or position()
    - Expressions wrapped in parentheses that contain XPath syntax
    """
    expr = expression.strip()

    # Direct XPath patterns
    if expr.startswith('/') or expr.startswith('//'):
        return True
    if '::' in expr:
        return True

    # Handle expressions wrapped in parentheses
    if expr.startswith('(') and expr.endswith(')'):
        # Remove outer parentheses and check inner content
        inner_expr = expr[1:-1].strip()
        if inner_expr.startswith('/') or inner_expr.startswith('//'):
            return True
        if '::' in inner_expr:
            return True

    # Additional XPath indicators
    # Check for XPath-specific patterns that CSS doesn't have
    if '//' in expr or expr.startswith('/'):
        return True
    if re.search(r'@[\w-]+', expr):  # attribute predicates like @class
        return True
    if re.search(r'\[\d+\]', expr):  # position predicates like [1]
        return True
    if re.search(r'\b(text|node|comment|processing-instruction)\(\)', expr):  # XPath functions
        return True
    if re.search(r'\b(ancestor|descendant|following|preceding|parent|child)::', expr):  # XPath axes
        return True

    return False

def main():
    # Command line argument parser definition
    parser = argparse.ArgumentParser(
        description=(
            'Extract parts of an HTML page using an XPath query or CSS3 selector.\n'
            'Reads static HTML and does not run JavaScript: content built in the\n'
            'browser is not there. Never prompts for input.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
examples:
  scrape -e "//h1" file.html            XPath: matching elements as HTML
  scrape -e "h1.title" file.html        CSS selector, detected automatically
  scrape -e "//a/@href" file.html       attribute values as plain text
  scrape -e "//a" -a href file.html     same, elements without href skipped
  scrape -e "count(//a)" file.html      XPath function: one value (string,
                                        number, true/false)
  scrape -t file.html                   all body text, no script or style
  scrape -te "//article" file.html      text of the matching elements
  scrape -je "a" file.html              JSON
  scrape -be "//article" file.html      wrap output in <html><body>
  scrape -x -e "//h1" file.html         test only: exit code, no output
  scrape -e "//h1" https://example.com  fetch from URL
  cat file.html | scrape -e "//h1"      read from stdin

output:
  default  one result after the other, on stdout: elements as HTML, strings
           (@attr, text(), XPath functions) as plain text
  -e       repeated: results follow the order of the expressions
  -j       always {"html": {"body": ...}}, where body is:
             elements  attributes as @name, text as #text; one match of a tag
                       is an object, several are a list
             strings   one is a string, several are a list
             nothing   null

exit codes:
  0  success, also when nothing matches: empty output, or null body with -j
  1  error, with a message on stderr; with -x, no match, with stderr empty
  2  invalid usage: unknown option or missing option value

notes:
  - No match is not an error: use -x to test for it.
  - With short flags together, -e goes last: -be, -je, -te. As an argument on
    its own, -eb or -ej is rejected, because -e would take "b" or "j" as value.
  - -x evaluates only the first -e.
  - -t with -e includes the text of any script or style inside the matches.
  - -j fails with exit 1 on attribute names that are not valid XML, such as
    @click or :bind. Use -e without -j on those pages.
  - URLs: 30 s timeout, HTTP errors (4xx, 5xx) exit 1.
  - Charset: from the meta tag, otherwise UTF-8. Other encodings need the meta
    tag, or characters come out wrong.
'''
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    # Check for incorrect argument order (-eb instead of -be, -ej instead of -je)
    for wrong, right in (('-eb', '-be'), ('-ej', '-je')):
        if wrong in sys.argv[1:]:
            print(f"Error: use {right} not {wrong}.\n  scrape {right} \"//article\" file.html", file=sys.stderr)
            sys.exit(1)
    # Defines the HTML input argument (can be a file, URL or stdin)
    parser.add_argument('html', nargs='?', type=str, default='',
                        help="HTML input: local file or http(s) URL. Stdin if omitted", metavar="HTML")
    # Defines the optional argument to extract from the tag
    parser.add_argument('-a', '--argument', default="",
                        help="Output the value of this attribute instead of the element. "
                             "Elements without it are skipped")
    # Option to include the result within HTML and BODY tags
    parser.add_argument('-b', '--body', action='store_true', default=False,
                        help="Wrap the output in a <!DOCTYPE html><html><body> document. "
                             "Ignored with -t and -j")
    # Option to extract only text content
    parser.add_argument('-t', '--text', action='store_true', default=False,
                        help="Output text only, with whitespace cleaned. "
                             "Without -e, all body text except script and style")
    # Option to output structured JSON (built-in, no external xq needed)
    parser.add_argument('-j', '--json', action='store_true', default=False,
                        help="Output structured JSON, see below. Not with -t, -x, -a")
    # Allows to specify one or more XPath or CSS3 selector expressions
    parser.add_argument('-e', '--expression', default=[], action='append',
                        help="XPath query or CSS3 selector, detected automatically. Repeatable")
    # Option to verify the existence of elements matching the expression
    parser.add_argument('-x', '--check-existence', dest='check_existence', action='store_true', default=False,
                        help="Output nothing, exit 0 if the first expression matches, 1 if not")
    # Option to avoid initial HTML parsing, useful in specific cases like CData
    parser.add_argument('-r', '--rawinput', action='store_true', default=False,
                        help="Parse the input as strict XML instead of HTML (useful for CData). "
                             "Malformed input is an error")
    parser.add_argument('-u', '--user-agent', default=None,
                        help="User-Agent for URL requests")
    args = parser.parse_args()

    # JSON flag is mutually exclusive with -t, -x, -a
    if args.json and args.text:
        print("Error: --json and --text are mutually exclusive.", file=sys.stderr)
        sys.exit(1)
    if args.json and args.check_existence:
        print("Error: --json and --check-existence are mutually exclusive.", file=sys.stderr)
        sys.exit(1)
    if args.json and args.argument:
        print("Error: --json cannot be combined with -a/--argument.", file=sys.stderr)
        sys.exit(1)

    # Check that at least one expression is provided by the user (unless using -t option)
    if not args.expression and not args.text:
        print(
            "Error: no expression specified. Use -e \"//selector\" or -t.\n"
            "  scrape -e \"//h1\" file.html\n"
            "  scrape -t file.html",
            file=sys.stderr
        )
        sys.exit(1)

    # Determine the source of the input: URL, file, or stdin
    if args.html:
        if args.html.startswith('http://') or args.html.startswith('https://'):
            # If the input is a URL, download the HTML content
            try:
                ua = args.user_agent or "Mozilla/5.0 (compatible; scrape-cli/1.0)"
                headers = {"User-Agent": ua}
                response = requests.get(args.html, headers=headers, timeout=30)
                response.raise_for_status()
                inp = response.content
            except requests.RequestException as e:
                print(f"Error downloading HTML: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # If the input is a local file, try to open it
            try:
                inp = open(args.html, 'rb').read()
            except FileNotFoundError:
                print(f"Error: The file '{args.html}' was not found.", file=sys.stderr)
                sys.exit(1)
            except OSError as e:
                print(f"Error: cannot read '{args.html}': {e.strerror}", file=sys.stderr)
                sys.exit(1)
    else:
        # If the input is from stdin
        try:
            inp = sys.stdin.buffer.read()
            if not inp:
                print("Error: No input received from stdin", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error reading input: {e}", file=sys.stderr)
            sys.exit(1)

    # Check for empty or invalid input
    if not inp:
        print("Error: Input is empty or invalid", file=sys.stderr)
        sys.exit(1)

    # Convert CSS selectors to XPath if necessary
    if args.text and not args.expression:
        # If -t is used without expressions, default to body text excluding scripts and styles
        expression = ['//body//text()[not(ancestor::script) and not(ancestor::style)]']
    else:
        expression = [e if is_xpath(e) else convert_css_to_xpath(e) for e in args.expression]

    # Create an HTML parser with options for error recovery
    html_parser = etree.HTMLParser(encoding='utf-8', recover=True)

    def detect_charset(html_bytes):
        """Try to detect charset from meta tag"""
        try:
            # Look for charset in first 1024 bytes to be efficient
            head = html_bytes[:1024].decode('ascii', errors='ignore').lower()
            meta = re.search(r'<meta[^>]+charset=["\']?([\w-]+)', head)
            if meta:
                return meta.group(1)
        except Exception:
            pass
        return None

    # Try to parse the HTML input
    try:
        # First try to detect charset from meta tag
        charset = detect_charset(inp)
        if charset:
            try:
                inp = inp.decode(charset).encode('utf-8')
            except (UnicodeDecodeError, LookupError):
                # If detected charset fails, fall back to default behavior
                pass

        # Try UTF-8 first, fallback to ISO-8859-1 if that fails
        try:
            if args.rawinput:
                document = etree.fromstring(inp)
            else:
                document = etree.fromstring(inp, html_parser)
        except UnicodeDecodeError:
            # If UTF-8 fails, try ISO-8859-1
            inp = inp.decode('iso-8859-1').encode('utf-8')
            if args.rawinput:
                document = etree.fromstring(inp)
            else:
                document = etree.fromstring(inp, html_parser)
    except (etree.XMLSyntaxError, UnicodeDecodeError) as e:
        # Print an error in case of syntax issues in the HTML
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    string_results = []
    # For each expression, perform the search in the parsed HTML
    for e in expression:
        try:
            result = document.xpath(e)
        except etree.XPathError as err:
            print(f"Error: invalid XPath expression '{e}': {err}", file=sys.stderr)
            sys.exit(1)

        # If check-existence is enabled, return 0 or 1 depending on the existence of elements
        if args.check_existence:
            sys.exit(0 if result else 1)

        els = xpath_result_items(result)

        # Extract the text or content of the found elements
        for el in els:
            if isinstance(el, str):
                # If the element is a string, use the text directly
                text = el
                # Clean the text when using -t option
                if args.text:
                    text = clean_text(text)
                # Strings are plain text, but -j parses the results as XML
                if args.json:
                    string_results.append(text.strip())
                    text = escape(text)
            elif args.text:
                # If -t option is used, extract only text content
                if hasattr(el, 'text_content'):
                    text = el.text_content()
                else:
                    text = ''.join(el.itertext())
                # Clean the text when using -t option
                text = clean_text(text)
            elif not args.argument:
                # If no attribute is specified, return the element as HTML string
                text = etree.tostring(el, pretty_print=True).decode('utf-8')
            else:
                # Otherwise, extract the specified attribute
                text = el.get(args.argument)
            if text is not None:
                results.append(text.strip())

    # Apply final cleaning when using -t option
    if args.text and results:
        final_text = '\n'.join(results)
        final_text = clean_text(final_text)
        results = [final_text] if final_text else []

    # Output handling
    if args.json:
        values = [s for s in string_results if s]
        if values and len(string_results) == len(results):
            # Only strings (@attr, text()): XML conversion would merge them into one
            parsed = {"html": {"body": values[0] if len(values) == 1 else values}}
        else:
            try:
                parsed = xmltodict.parse(wrap_in_body(results))
            except ExpatError as e:
                print(f"Error: cannot convert result to JSON, it is not valid XML ({e}). "
                      "Attribute names like @click or :bind are not supported by -j.", file=sys.stderr)
                sys.exit(1)
        sys.stdout.write(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n")
    elif args.body and not args.text:
        sys.stdout.write(wrap_in_body(results))
    else:
        # Normal output (or text-only output when -t is used)
        for result in results:
            sys.stdout.write(result + "\n")

        sys.stdout.flush()

if __name__ == "__main__":
    exit(main())
