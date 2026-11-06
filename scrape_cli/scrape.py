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
import copy
import requests
import xmltodict
from lxml import etree
from cssselect import GenericTranslator
from urllib.parse import urljoin, urlsplit
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


def is_absolute_url(url):
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return bool(parts.scheme and parts.netloc)


def resolve_url(base, value):
    """Return value as an absolute URL, or unchanged if it cannot be parsed."""
    try:
        return urljoin(base, value.strip())
    except ValueError:
        return value


def document_base(document, page_url):
    """Base as in the HTML standard: the first <base href>, against the page URL."""
    hrefs = document.xpath('(//base[@href])[1]/@href')
    if hrefs:
        base = resolve_url(page_url or '', hrefs[0])
        if is_absolute_url(base):
            return base
    return page_url


def with_absolute_urls(el, base):
    """Copy the element, so that later expressions still see the original values."""
    el = copy.deepcopy(el)
    for node in el.xpath('descendant-or-self::*[@href or @src]'):
        for name in ('href', 'src'):
            if name in node.attrib:
                node.set(name, resolve_url(base, node.get(name)))
    return el


def evaluate(context, expression):
    try:
        return context.xpath(expression)
    except etree.XPathError as err:
        print(f"Error: invalid XPath expression '{expression}': {err}", file=sys.stderr)
        sys.exit(1)


def parse_fields(fields):
    """Turn NAME=EXPR strings into {name: XPath}, exiting on invalid ones."""
    parsed = {}
    for field in fields:
        name, _, expression = (part.strip() for part in field.partition('='))
        if not name or not expression:
            print(f"Error: --field must be NAME=EXPR, got '{field}'.", file=sys.stderr)
            sys.exit(1)
        if name in parsed:
            print(f"Error: repeated --field name '{name}'.", file=sys.stderr)
            sys.exit(1)
        if expression.startswith(('/', '(/')):
            print(f"Error: --field '{field}' reads the whole document on each row: "
                  "start the expression with .// instead.", file=sys.stderr)
            sys.exit(1)
        parsed[name] = expression if is_xpath(expression) else convert_css_to_xpath(expression)
    return parsed


def field_value(row, expression, base):
    """String form of the first match in the row, or None if there is none."""
    for item in xpath_result_items(evaluate(row, expression)):
        if isinstance(item, str):
            is_attribute = getattr(item, 'is_attribute', False)
            if base and is_attribute and item.attrname in ('href', 'src'):
                return resolve_url(base, item)
            if is_attribute or item.strip():
                return item.strip()
        elif isinstance(item.tag, str):  # not a comment or processing instruction
            return clean_text(''.join(item.itertext()))
    return None


def write_json(value, lines):
    """Print a JSON value, or with lines one item of the list per line."""
    if lines:
        for item in value:
            sys.stdout.write(json.dumps(item, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


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
    if expr.startswith('/') or expr.startswith('//') or expr.startswith('./'):
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
  scrape --json-array -e "a" file.html  JSON, always a flat list
  scrape --absolute-urls -e "//a/@href" https://example.org/
                                        absolute href and src values
  curl -s https://example.org/ | scrape --base-url https://example.org/ -e "a"
                                        same, for stdin or a local file
  scrape --row "article" --field "title=h2" --field "url=.//a/@href" file.html
                                        one JSON object per article
  scrape --jsonl -e "//a/@href" file.html
                                        one JSON value per line
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
  --json-array  always a flat list, one item per result, in expression order:
             [] for nothing, strings as strings, elements as {"tag": ...},
             function values as strings: count() gives "2"
  --row    a list with one object per row, one key per --field in the order
           given, each value a string or null (no match); "" is a match with
           no text. Elements give their cleaned text. Rows with no match in
           any field stay in the list.
  --jsonl  one JSON value per line: the objects of --row, otherwise the items
           of --json-array. Nothing at all when there are no results.

exit codes:
  0  success, also when nothing matches: empty output, or null body with -j
  1  error, with a message on stderr; with -x, no match, with stderr empty
  2  invalid usage: unknown option or missing option value

notes:
  - No match is not an error: use -x to test for it.
  - HTML with no elements, such as only spaces or comments, exits 1.
  - With short flags together, -e goes last: -be, -je, -te. As an argument on
    its own, -eb or -ej is rejected, because -e would take "b" or "j" as value.
  - -x evaluates only the first -e.
  - -t with -e includes the text of any script or style inside the matches.
  - -j fails with exit 1 on attribute names that are not valid XML, such as
    @click or :bind. Use -e without -j on those pages.
  - --field is relative to the row and gives only the first match. Write
    .//a/@href: a/@href looks among direct children only, and //a is refused
    because it would read the whole document. In functions, write
    string(.//h2): string(//h2) is not refused and reads the whole document.
  - --row is not allowed with -e, -t, -x, -a, -b, -j, --json-array.
    --jsonl is not allowed with -t, -x, -a, -b, -j.
  - URLs: 30 s timeout, HTTP errors (4xx, 5xx) exit 1.
  - --absolute-urls changes href and src in the output, not in selection:
    a[href^="/"] still matches. Base: the first <base href>, against the page
    URL or --base-url. No absolute base: exit 1. XPath functions such as
    string(//a/@href) are not changed. Not with -r, ignored with -t and -x.
  - Charset: from the meta tag, otherwise UTF-8. If the bytes are not valid
    UTF-8: Windows-1252, then ISO-8859-1. Other encodings need the meta tag.
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
    parser.add_argument('--json-array', action='store_true', default=False,
                        help="Output JSON as a flat list, one item per result, see below. Same limits as -j")
    parser.add_argument('--absolute-urls', action='store_true', default=False,
                        help="Output href and src values as absolute URLs, see notes")
    parser.add_argument('--base-url', default=None, metavar="URL",
                        help="Page URL for stdin and local files. Implies --absolute-urls")
    parser.add_argument('--row', default=None, metavar="EXPR",
                        help="Select the elements that give one JSON object each. Needs --field")
    parser.add_argument('--field', default=[], action='append', metavar="NAME=EXPR",
                        help="Value of a key in each --row object, relative to the row. Repeatable")
    parser.add_argument('--jsonl', action='store_true', default=False,
                        help="Output one JSON value per line, see below. Implies --json-array without --row")
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

    if args.jsonl and (args.text or args.check_existence or args.argument or args.body or args.json):
        print("Error: --jsonl cannot be combined with -t, -x, -a, -b or -j.", file=sys.stderr)
        sys.exit(1)
    if bool(args.row) != bool(args.field):
        print("Error: --row and --field must be used together.", file=sys.stderr)
        sys.exit(1)
    fields = {}
    if args.row:
        if (args.expression or args.text or args.check_existence or args.argument
                or args.body or args.json or args.json_array):
            print("Error: --row cannot be combined with -e, -t, -x, -a, -b, -j or --json-array.", file=sys.stderr)
            sys.exit(1)
        fields = parse_fields(args.field)
    elif args.jsonl:
        args.json_array = True

    # JSON flag is mutually exclusive with -t, -x, -a
    json_flag = '--json-array' if args.json_array else '--json'
    if args.json_array:
        args.json = True
    if args.json and args.text:
        print(f"Error: {json_flag} and --text are mutually exclusive.", file=sys.stderr)
        sys.exit(1)
    if args.json and args.check_existence:
        print(f"Error: {json_flag} and --check-existence are mutually exclusive.", file=sys.stderr)
        sys.exit(1)
    if args.json and args.argument:
        print(f"Error: {json_flag} cannot be combined with -a/--argument.", file=sys.stderr)
        sys.exit(1)

    if args.base_url and not is_absolute_url(args.base_url):
        print(f"Error: --base-url must be an absolute URL, got '{args.base_url}'.", file=sys.stderr)
        sys.exit(1)
    absolute_urls = args.absolute_urls or bool(args.base_url)
    if absolute_urls and args.rawinput:
        print("Error: --absolute-urls and --base-url cannot be combined with -r/--rawinput.", file=sys.stderr)
        sys.exit(1)

    # Check that at least one expression is provided by the user (unless using -t option)
    if not args.expression and not args.text and not args.row:
        print(
            "Error: no expression specified. Use -e \"//selector\" or -t.\n"
            "  scrape -e \"//h1\" file.html\n"
            "  scrape -t file.html",
            file=sys.stderr
        )
        sys.exit(1)

    page_url = args.base_url
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
                page_url = page_url or response.url
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

        if args.rawinput:
            # XML declares its own encoding: leave the bytes to the parser
            document = etree.fromstring(inp)
        else:
            # The recovering parser never fails on bad bytes, so check them here
            try:
                inp.decode('utf-8')
            except UnicodeDecodeError:
                # cp1252 rejects five undefined bytes, iso-8859-1 accepts them all
                try:
                    inp = inp.decode('cp1252').encode('utf-8')
                except UnicodeDecodeError:
                    inp = inp.decode('iso-8859-1').encode('utf-8')
            document = etree.fromstring(inp, html_parser)
    except (etree.XMLSyntaxError, UnicodeDecodeError) as e:
        # Print an error in case of syntax issues in the input
        print(f"Error parsing {'XML' if args.rawinput else 'HTML'}: {e}", file=sys.stderr)
        sys.exit(1)

    if document is None:
        print("Error parsing HTML: no elements found in the input", file=sys.stderr)
        sys.exit(1)

    # -t and -x output no attribute values
    base = None
    if absolute_urls and not args.text and not args.check_existence:
        base = document_base(document, page_url)
        if not base:
            print("Error: no base for --absolute-urls: use --base-url URL, "
                  "or a page with an absolute <base href>.", file=sys.stderr)
            sys.exit(1)

    if args.row:
        row_expression = args.row if is_xpath(args.row) else convert_css_to_xpath(args.row)
        rows = xpath_result_items(evaluate(document, row_expression))
        if any(isinstance(row, str) or not isinstance(row.tag, str) for row in rows):
            print(f"Error: --row must select elements, not values: '{args.row}'.", file=sys.stderr)
            sys.exit(1)
        write_json([{name: field_value(row, expression, base) for name, expression in fields.items()}
                    for row in rows], args.jsonl)
        return

    results = []
    string_results = []
    # --json-array items: str for strings, bytes for element markup
    array_items = []
    # For each expression, perform the search in the parsed HTML
    for e in expression:
        result = evaluate(document, e)

        # If check-existence is enabled, return 0 or 1 depending on the existence of elements
        if args.check_existence:
            sys.exit(0 if result else 1)

        els = xpath_result_items(result)

        # Extract the text or content of the found elements
        for el in els:
            if base:
                if isinstance(el, str):
                    if getattr(el, 'is_attribute', False) and el.attrname in ('href', 'src'):
                        el = resolve_url(base, el)
                elif isinstance(el.tag, str):
                    el = with_absolute_urls(el, base)
            if args.json_array:
                if isinstance(el, str):
                    if el.strip():
                        array_items.append(el.strip())
                elif isinstance(el.tag, str):  # not a comment or processing instruction
                    array_items.append(etree.tostring(el, with_tail=False))
                continue
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
                text = etree.tostring(el, pretty_print=True, with_tail=False).decode('utf-8')
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
        try:
            if args.json_array:
                parsed = [xmltodict.parse(i) if isinstance(i, bytes) else i for i in array_items]
            elif values and len(string_results) == len(results):
                # Only strings (@attr, text()): XML conversion would merge them into one
                parsed = {"html": {"body": values[0] if len(values) == 1 else values}}
            else:
                parsed = xmltodict.parse(wrap_in_body(results))
        except ExpatError as e:
            print(f"Error: cannot convert result to JSON, it is not valid XML ({e}). "
                  f"Attribute names like @click or :bind are not supported by {'--json-array' if args.json_array else '-j'}.", file=sys.stderr)
            sys.exit(1)
        write_json(parsed, args.jsonl)
    elif args.body and not args.text:
        sys.stdout.write(wrap_in_body(results))
    else:
        # Normal output (or text-only output when -t is used)
        for result in results:
            sys.stdout.write(result + "\n")

        sys.stdout.flush()

if __name__ == "__main__":
    exit(main())
