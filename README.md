# scrape cli

It's the Linux command-line version (built using [pyinstaller](http://www.pyinstaller.org/)) of a [great scraping tool](https://github.com/jeroenjanssens/data-science-at-the-command-line/blob/master/tools/scrape) written by [Jeroen Janssens](http://jeroenjanssens.com).

It extracts HTML elements using XPath or CSS selector queries.

Example usage using CSS selector query:

```bash
$ curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be 'table.wikitable > tbody > tr > td > b > a'
```

Example usage using XPATH query:

```bash
curl -L 'https://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
| scrape -be '//table[contains(@class, 'wikitable')]/tbody/tr/td/b/a'
```

`-e` to set the query and `-b` to add `<html>`, `<head>` and `<body>` tags to the HTML output.

It gives you back:

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

# How to install it Linux

```bash
# go to the home folder
cd ~
# download scrape-cli
wget "https://github.com/aborruso/scrape-cli/releases/download/v1.0/scrape"
# move it in a PATH folder as /usr/bin
sudo mv ./scrape /usr/bin
# give it execute permission
sudo chmod +x /usr/bin/scrape
# use it
```

## Note on building

Built in Python 2 environment, using `pyinstaller --onefile scrape.py` command.

For windows it's better to install - using pip - first `cssselector` and then `lxml`.
