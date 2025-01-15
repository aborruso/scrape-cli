[![PyPI version](https://badge.fury.io/py/scrape-cli.svg)](https://badge.fury.io/py/scrape-cli)
[![Python Versions](https://img.shields.io/pypi/pyversions/scrape-cli.svg)](https://pypi.org/project/scrape-cli/)

# scrape cli

It's a **command-line tool** to **extract** HTML elements using an [**XPath**](https://www.w3schools.com/xml/xpath_intro.asp) query or [**CSS3 selector**](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors).

It's based on the great and simple [scraping tool](https://github.com/jeroenjanssens/data-science-at-the-command-line/blob/master/tools/scrape) written by [**Jeroen Janssens**](http://jeroenjanssens.com).

- [How does it work?](#how-does-it-work)
- [How to use it in Linux](#how-to-use-it-in-linux)
- [Note on building it](#note-on-building-it)



## Installation

You can install scrape-cli using pip:

### Using pipx (recommended for CLI tools)

```bash
pipx install scrape-cli
```

Using pip

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
scrape -e "table.data-table td" resources/test.html
```

2. Get all list items:
```bash
scrape -e "ul.items-list li" resources/test.html
```

3. Extract specific attributes:
```bash
scrape -e "a.external-link" -a href resources/test.html
```

4. Check if an element exists:
```bash
scrape -e "#main-title" --check-existence resources/test.html
```

5. Extract nested elements:
```bash
scrape -e ".nested-elements p" resources/test.html
```

6. Get elements with specific attributes:
```bash
scrape -e "[data-test]" resources/test.html
```

### General Usage Examples

A CSS selector query like this

```bash
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be 'table.wikitable > tbody > tr > td > b > a'
```

or an XPATH query like this one:

```bash
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be '//table[contains(@class, 'wikitable')]/tbody/tr/td/b/a'
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

Some notes on the commands:

- `-e` to set the query
- `-b` to add `<html>`, `<head>` and `<body>` tags to the HTML output.


## Linux 64 bit precompiled binary

If you are looking for precompiled executables for Linux, please refer to the [Releases](https://github.com/aborruso/scrape-cli/releases) page on GitHub where you can find the latest precompiled binary file.

I have built the `scrape-linux-x86_64` precompiled binary, using [pyinstaller](https://www.pyinstaller.org/) and this command: `pyinstaller --onefile scrape.py`.<br>

Once you have built it, it's an executable, and it's possible to use it Linux 64 bit environment.

## License

[MIT](LICENSE)
