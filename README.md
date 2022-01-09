# scrape cli

It's a **command-line tool** to **extract** HTML elements using an [**XPath**](https://www.w3schools.com/xml/xpath_intro.asp) query or [**CSS3 selector**](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors).

It's based on the great and simple [scraping tool](https://github.com/jeroenjanssens/data-science-at-the-command-line/blob/master/tools/scrape) written by [**Jeroen Janssens**](http://jeroenjanssens.com).

- [How does it work?](#how-does-it-work)
- [How to use it in Linux](#how-to-use-it-in-linux)
- [Note on building it](#note-on-building-it)

## How does it work?

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

## How to use it in Linux

```bash
# go in example to the home folder
cd ~
# download scrape-cli
wget "https://github.com/aborruso/scrape-cli/releases/download/v1.0/scrape"
# move it in a folder of your PATH as /usr/bin
sudo mv ./scrape /usr/bin
# give it execute permission
sudo chmod +x /usr/bin/scrape
# use it
```

**Please note**: in OSX it seems not to work ([#8](https://github.com/aborruso/scrape-cli/issues/8)).

## Note on building it

The original source is written in Python 2, then I have built it in Python 2 environment.<br>
There are two modules requirements: install in this environment `cssselect` and then `lxml`, in this order (using pip).

I have built it using [pyinstaller](https://www.pyinstaller.org/) and this command: `pyinstaller --onefile scrape.py`.<br>

Once you have built it, it's an executable, and it's possible to use it in any environment.
