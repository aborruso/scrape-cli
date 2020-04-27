# scrape cli

It's the Linux command-line version (built using [pyinstaller](http://www.pyinstaller.org/)) of a great and simple [scraping tool](https://github.com/jeroenjanssens/data-science-at-the-command-line/blob/master/tools/scrape) written by [Jeroen Janssens](http://jeroenjanssens.com).

It extracts HTML elements using [XPath](https://www.w3schools.com/xml/xpath_intro.asp) or [CSS selector](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors) queries.

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

# How to use it Linux

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

# Note on building it

The original source is written in Python 2, then I have built it in Python 2 environment.

It's mandatory to install in this environment `cssselect` and then `lxml`, in this order (using pip).

I have built it using [pyinstaller](https://www.pyinstaller.org/) and this command: `pyinstaller --onefile scrape.py`.<br>
Once you have built it, you can use it as an executable, in any environment
