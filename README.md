[![PyPI version](https://img.shields.io/pypi/v/scrape-cli.svg?label=PyPI%20version)](https://pypi.org/project/scrape-cli/)
[![Python Versions](https://img.shields.io/pypi/pyversions/scrape-cli.svg)](https://pypi.org/project/scrape-cli/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/aborruso/scrape-cli)

# scrape cli

It's a **command-line tool** to **extract** HTML elements using an [**XPath**](https://www.w3schools.com/xml/xpath_intro.asp) query or [**CSS3 selector**](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors).

It's based on the great and simple [scraping tool](https://github.com/jeroenjanssens/dsutils/blob/master/scrape) written by [**Jeroen Janssens**](http://jeroenjanssens.com).

- [How does it work?](#how-does-it-work)
- [How to use it in Linux](#how-to-use-it-in-linux)
- [Note on building it](#note-on-building-it)



## Installation

You can install scrape-cli using several methods:

### Using pipx (recommended for CLI tools)

```bash
pipx install scrape-cli
```

### Using uv (modern Python package manager)

```bash
# Install as a global CLI tool (recommended)
uv tool install scrape-cli

# Or install with uv pip
uv pip install scrape-cli

# Or run temporarily without installing
uvx --from scrape-cli scrape --help
```

### Using pip

```bash
pip install scrape-cli
```

Or install from source:

```bash
git clone https://github.com/aborruso/scrape-cli
cd scrape-cli
pip install -e .
```

## Requirements

- Python >=3.8
- requests
- lxml
- cssselect
- xmltodict

## How does it work?

### Using the Test HTML File

In the `resources` directory you'll find a `test.html` file that you can use to test various scraping scenarios.

**Note**: You can also test directly from the URL without cloning the repository:

```bash
scrape -e "h1" https://raw.githubusercontent.com/aborruso/scrape-cli/refs/heads/master/resources/test.html
```

Here are some examples:

1. Extract all table data:

```bash
# CSS
scrape -e "table.data-table td" resources/test.html
# XPath
scrape -e "//table[contains(@class, 'data-table')]//td" resources/test.html
```

2. Get all list items:

```bash
# CSS
scrape -e "ul.items-list li" resources/test.html
# XPath
scrape -e "//ul[contains(@class, 'items-list')]/li" resources/test.html
```

3. Extract specific attributes:

```bash
# CSS
scrape -e "a.external-link" -a href resources/test.html
# XPath
scrape -e "//a[contains(@class, 'external-link')]/@href" resources/test.html
```

4. Check if an element exists:

```bash
# CSS
scrape -e "#main-title" --check-existence resources/test.html
# XPath
scrape -e "//h1[@id='main-title']" --check-existence resources/test.html
```

5. Extract nested elements:

```bash
# CSS
scrape -e ".nested-elements p" resources/test.html
# XPath
scrape -e "//div[contains(@class, 'nested-elements')]//p" resources/test.html
```

6. Get elements with specific attributes:

```bash
# CSS
scrape -e "[data-test]" resources/test.html
# XPath
scrape -e "//*[@data-test]" resources/test.html
```

7. Additional XPath examples:

```bash
# Get all links with href attribute
scrape -e "//a[@href]" resources/test.html

# Get checked input elements
scrape -e "//input[@checked]" resources/test.html

# Get elements with multiple classes
scrape -e "//div[contains(@class, 'class1') and contains(@class, 'class2')]" resources/test.html

# Get text content of specific element
scrape -e "//h1[@id='main-title']/text()" resources/test.html
```

### General Usage Examples

A CSS selector query like this

```bash
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be 'table.wikitable > tbody > tr > td > b > a'
```

**Note:** When using both `-b` and `-e` options together, they must be specified in the order `-be` (body first, then expression). Using `-eb` will not work correctly.

or an XPATH query like this one:

```bash
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be "//table[contains(@class, 'wikitable')]/tbody/tr/td/b/a"
```

gives you back:

```html
<html>
 <head>
 </head>
 <body>
  <a href="/wiki/Afghanistan" title="Afghanistan">
   Afghanistan
  </a>
  <a href="/wiki/Albania" title="Albania">
   Albania
  </a>
  <a href="/wiki/Algeria" title="Algeria">
   Algeria
  </a>
  <a href="/wiki/Andorra" title="Andorra">
   Andorra
  </a>
  <a href="/wiki/Angola" title="Angola">
   Angola
  </a>
  <a href="/wiki/Antigua_and_Barbuda" title="Antigua and Barbuda">
   Antigua and Barbuda
  </a>
  <a href="/wiki/Argentina" title="Argentina">
   Argentina
  </a>
  <a href="/wiki/Armenia" title="Armenia">
   Armenia
  </a>
...
...
 </body>
</html>
```

### Text Extraction

You can extract only the text content (without HTML tags) using the `-t` option, which is particularly useful for LLMs and text processing:

```bash
# Extract all text content from a page
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -t

# Extract text from specific elements
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -te 'table.wikitable td'

# Extract text from headings only
scrape -te 'h1, h2, h3' resources/test.html
```

The `-t` option automatically excludes text from `<script>` and `<style>` tags and cleans up whitespace for better readability.

### JSON Output

Use the `-j`/`--json` flag to get structured JSON natively, with no external tools:

```bash
scrape -je "a.external-link" resources/test.html
```

Output:

```json
{
  "html": {
    "body": {
      "a": {
        "@href": "https://example.com",
        "@class": "external-link",
        "#text": "Example Link"
      }
    }
  }
}
```

Table extraction example:

```bash
scrape -je "table.data-table td" resources/test.html
```

Output:

```json
{
  "html": {
    "body": {
      "td": [
        "Italy",
        "Rome",
        "59",
        "France",
        "Paris",
        "68"
      ]
    }
  }
}
```

`-j` automatically wraps the result in `<html>/<body>` before conversion, so you don't need to pass `-b`. For elements, the output is the same you would get from `scrape -be ... | xq .` (the underlying converter is `xmltodict`, the same library used by `xq`). Expressions that return only strings, such as `//a/@href` or `//p/text()`, give the string in `body` when there is one result and an array when there are more.

Use `--json-array` when a script needs one shape for any number of results. The output is a flat list with no `html`/`body` envelope, one item per result, in the order of the expressions. Strings stay strings and elements become objects with the tag as key, so `scrape --json-array -e "//a/@href" -e "b"` gives `["x", "y", {"b": "tre"}]`, and no results give `[]`. It implies `-j` and has the same limits.

With mixed expressions, each result keeps its own form and its place in the order of the expressions. XPath function values are strings, so `count()` gives `"2"`, not `2`:

```bash
scrape --json-array -e "h1" -e "//a/@href" -e "count(//a)" page.html
# [{"h1": "News"}, "/one", "/two", "2"]
```

The list shape makes `jq` pipelines simple, with the same code for zero, one or many results:

```bash
# Count the results
scrape --json-array -e "a" page.html | jq 'length'

# Loop over attribute values; with no results, the loop does not run
scrape --json-array -e "//a/@href" page.html | jq -r '.[]' | while read -r href; do
  echo "got $href"
done

# Read fields of each element, as TSV
scrape --json-array -e "a" page.html | jq -r '.[].a | [.["@href"], .["#text"]] | @tsv'

# Filter elements by attribute
scrape --json-array -e "a" page.html | jq -c '.[] | select(.a["@class"] == "ext")'

# With mixed expressions, keep only the strings
scrape --json-array -e "h1" -e "//a/@href" page.html | jq -c 'map(strings)'

# Turn a count() into a number
scrape --json-array -e "count(//a)" page.html | jq '.[0] | tonumber'
```

`-j` is mutually exclusive with `-t`, `-x` (`--check-existence`) and `-a` (`--argument`).

`-j` exits with an error when a matched element has an attribute name that is not valid XML, such as `@click` or `:bind`.

Useful for JSON-based pipelines, APIs, databases, and processing with jq/DuckDB.

Some notes on the commands:

- `-e` to set the query
- `-b` to add `<html>`, `<head>` and `<body>` tags to the HTML output
- `-j` to output structured JSON (built-in)
- `-t` to extract only text content (useful for LLMs and text processing)


### Several fields per element

Separate `-e` expressions lose the link between fields: if an article has no date, every following date ends up on the wrong article. Use `--row` to select the elements, and one `--field NAME=EXPR` for each value, relative to the row:

```bash
scrape --row "article" --field "title=h2" --field "url=.//a/@href" --field "date=time/@datetime" page.html
```

```json
[
  {"title": "First story", "url": "/one", "date": "2026-01-01"},
  {"title": "Second story", "url": "/two", "date": null}
]
```

- Every object has the same keys, and every value is a string or `null`. `null` means no match, `""` a match with no text.
- A field gives only its first match. Elements give their cleaned text, and XPath functions a string.
- Field expressions are XPath or CSS, as with `-e`. Write attributes as `.//a/@href`: `a/@href` looks among direct children only, and `//a` is refused because it would read the whole document. In functions, write `string(.//h2)`.
- `--absolute-urls` and `--base-url` apply to `href` and `src` fields.
- `--row` cannot be combined with `-e`, `-t`, `-x`, `-a`, `-b`, `-j` or `--json-array`.

### JSON Lines

Use `--jsonl` to get one JSON value per line: the objects of `--row`, or otherwise the items of `--json-array`. With no results the output is empty. It cannot be combined with `-t`, `-x`, `-a`, `-b` or `-j`.

```bash
scrape --jsonl --row "article" --field "title=h2" --field "date=time/@datetime" page.html
# {"title": "First story", "date": "2026-01-01"}
# {"title": "Second story", "date": null}

# Articles with no date, with jq
scrape --jsonl --row "article" --field "title=h2" --field "date=time/@datetime" page.html \
  | jq -r 'select(.date == null) | .title'

# Query with DuckDB
scrape --jsonl --row "article" --field "title=h2" --field "date=time/@datetime" page.html \
  | duckdb -c "select title, date from read_json('/dev/stdin', format='newline_delimited')"
```

The whole page is read and the output built in memory: `--jsonl` changes the format, not the memory use.

### Absolute URLs

Links and images often have relative values. Use `--absolute-urls` to get absolute `href` and `src` values, in every output mode except `-t`:

```bash
scrape --absolute-urls -e "//a/@href" https://www.iana.org/help/example-domains
```

With stdin or a local file there is no page URL, so pass it with `--base-url`, which implies `--absolute-urls`:

```bash
curl -s https://www.iana.org/help/example-domains \
  | scrape --base-url https://www.iana.org/help/example-domains -e "//a/@href"
```

- The base is the first `<base href>` of the page, resolved against the page URL, as in browsers. With a URL as input, the page URL is the final one after redirects.
- With no absolute base, the command exits with code 1.
- Selection uses the original values, so `a[href^="/"]` still matches.
- Other attributes, such as `srcset`, and XPath functions, such as `string(//a/@href)`, are not changed. Use `//a/@href`.
- `--absolute-urls` and `--base-url` cannot be combined with `-r`, and are ignored with `-t` and `-x`.

## License

[MIT](LICENSE)
