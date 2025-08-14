[![PyPI version](https://img.shields.io/pypi/v/scrape-cli.svg?label=PyPI%20version)](https://pypi.org/project/scrape-cli/)
[![Python Versions](https://img.shields.io/pypi/pyversions/scrape-cli.svg)](https://pypi.org/project/scrape-cli/)

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
uvx scrape-cli --help
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

- Python >=3.6
- requests
- lxml
- cssselect

## How does it work?

### Using the Test HTML File

In the `resources` directory you'll find a `test.html` file that you can use to test various scraping scenarios. Here are some examples:

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

Some notes on the commands:

- `-e` to set the query
- `-b` to add `<html>`, `<head>` and `<body>` tags to the HTML output
- `-t` to extract only text content (useful for LLMs and text processing)


## License

[MIT](LICENSE)
