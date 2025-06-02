# scrape-cli Documentation

scrape-cli is a command‑line tool designed to extract HTML elements from input documents using either XPath queries or CSS3 selectors. It uses Python libraries such as lxml and cssselect to parse and query the HTML content. The tool accepts input from a URL, file, or standard input (stdin) and outputs the matching elements in plain text or wrapped within standard HTML tags.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Command-Line Arguments](#command-line-arguments)
   - [Input Types](#input-types)
4. [Examples](#examples)
5. [How It Works Internally](#how-it-works-internally)
   - [Parsing the Input HTML](#parsing-the-input-html)
   - [Selector Processing](#selector-processing)
   - [Output Generation](#output-generation)
6. [Error Handling and Exit Codes](#error-handling-and-exit-codes)
7. [Development and Packaging](#development-and-packaging)
8. [License and Authors](#license-and-authors)

---

## Overview

scrape-cli provides a simple yet powerful way to query HTML documents directly from the command line. Its primary features include:

- **Selector Flexibility:** Use XPath for complex queries or CSS3 selectors that are automatically converted to XPath.
- **Multiple Input Sources:** Accepts input from a URL, file, or standard input.
- **Optional HTML Wrapping:** Ability to wrap extracted content in HTML `<html>` and `<body>` tags.
- **Attribute Extraction:** Optionally extract specific attributes from selected elements.
- **Error Checking:** Option to verify if any matching elements exist, returning a corresponding exit code.

---

## Installation

To install scrape-cli, you can use `pip` after obtaining it from [PyPI](https://pypi.org) or install directly from the source repository on GitHub.

### Using pip

If you have the package published on PyPI or an accessible repository:
  
```bash
pip install scrape-cli
```

### From Source

Clone the repository and install:

```bash
git clone https://github.com/aborruso/scrape-cli.git
cd scrape-cli
pip install .
```

The tool’s setup is defined in the [setup.py](./setup.py) file which also details dependencies like `lxml` and `cssselect`.

---

## Usage

Once installed, you can run scrape-cli as a command-line executable using the command `scrape`.

### Command-Line Arguments

scrape-cli uses several command-line arguments to control its behavior:

- **Positional Argument: HTML Input**
  - Specifies the HTML source.
  - Can be a URL, a file path, or omitted to read from stdin.
  
  Example:
  
  ```bash
  scrape https://example.com
  ```

- **-e / --expression**
  - One or more XPath queries or CSS3 selectors.
  - At least one expression must be provided.
  
  Example:
  
  ```bash
  scrape myfile.html -e "//div[@class='content']"
  ```
  
  Since CSS3 selectors are supported, if a CSS selector is used (i.e., not starting with “//”), it will be automatically translated to an XPath expression.

- **-a / --argument**
  - Specifies an attribute to extract from the matching HTML element(s).
  
  Example:
  
  ```bash
  scrape myfile.html -e "img" -a "src"
  ```

- **-b / --body**
  - When enabled, wraps the output results within standard HTML `<html>` and `<body>` tags.
  
  Example:
  
  ```bash
  scrape myfile.html -e "p" -b
  ```

- **-x / --check_existence**
  - Exits with a code indicating whether any matching elements were found (0 for found, 1 for not found). Useful for scripting.
  
  Example:
  
  ```bash
  scrape myfile.html -e "//h1" -x
  ```

- **-r / --rawinput**
  - Bypasses HTML parsing by lxml before processing the XPath queries. This is helpful in cases where the HTML includes special content (e.g., CDATA) that you do not wish to have altered during parsing.
  
  Example:
  
  ```bash
  scrape myfile.html -r -e "body > script"
  ```

> **Note:** An error message will be triggered if the arguments `-eb` (body then expression) are provided in the wrong order. Always ensure that the options are passed as `-be` (argument order matters for certain configurations).

### Input Types

scrape-cli can accept three types of input:

1. **URL:** When an HTML source starts with `http://` or `https://`, the tool fetches the HTML via the `requests` library.
2. **File:** If the argument is a local file path, the file is opened and its content read as binary.
3. **Standard Input (stdin):** If no HTML source is provided, the tool reads from stdin. This is useful when piping content from other commands:

   ```bash
   curl -s https://example.com | scrape -e "//header"
   ```

---

## Examples

Below are several practical examples that illustrate common usage scenarios:

### Example 1: Extracting Element HTML

Extract all `<a>` tags from a remote URL:

```bash
scrape https://en.wikipedia.org/wiki/List_of_sovereign_states -e "a"
```

### Example 2: Extracting an Attribute

Extract the `href` attribute from each `<a>` tag in a local HTML file:

```bash
scrape page.html -e "a" -a "href"
```

### Example 3: Using CSS Selectors

Use a CSS selector to extract bold text within a table:

```bash
scrape https://en.wikipedia.org/wiki/List_of_sovereign_states -e "table.wikitable > tbody > tr > td > b > a"
```

> The tool automatically converts CSS selectors into XPath queries.

### Example 4: Wrapping Output with HTML Tags

Wrap the output in a full HTML document:

```bash
scrape page.html -e "p" -b
```

### Example 5: Check Element Existence

Exit with a status code indicating element presence:

```bash
scrape page.html -e "//div[@id='content']" -x
```

If the element is found, the exit code will be 0; otherwise, it will be 1.

---

## How It Works Internally

scrape-cli is implemented with a focus on flexibility and error recovery. Below is an explanation of its core components:

### Parsing the Input HTML

1. **Input Detection and Retrieval:**
   - If the input is a URL, the tool sends a GET request using the `requests` library.
   - If the input is a file path, it opens and reads the content in binary mode.
   - Otherwise, reads the input from stdin.

2. **Charset Detection:**
   - The tool inspects the first 1024 bytes of the HTML input to detect a charset from any meta tag.
   - If a charset is found, it attempts to re-encode the input to UTF-8; otherwise, it defaults to UTF-8 or falls back to ISO-8859-1.

3. **HTML Parsing:**
   - Uses lxml's `HTMLParser` with recovery enabled (`recover=True`) to handle malformed HTML gracefully.
   - The `-r/--rawinput` option bypasses any pre-parsing, directly handing the input to `etree.fromstring()`.

### Selector Processing

1. **Determining Selector Type:**
   - The tool distinguishes between XPath expressions and CSS selectors based on the prefix (expressions starting with "//" are considered XPath).
   - CSS selectors are converted to XPath using the `cssselect.GenericTranslator`.

2. **Error Handling in Conversion:**
   - If the CSS to XPath conversion fails, the program prints a descriptive error message and exits.

### Output Generation

1. **XPath Evaluation:**
   - For each provided expression, the tool evaluates the XPath expression on the parsed HTML document.
   
2. **Result Extraction:**
   - If no attribute is specified, the entire HTML string of the matching element is output.
   - If an attribute is specified, the value of that attribute is extracted and output.
   - Strips any leading and trailing whitespace from each result.

3. **HTML Wrapping:**
   - If the `-b/--body` flag is enabled, the results are wrapped in a simple HTML document structure.

4. **Output Delivery:**
   - Writes results to `stdout` line-by-line.
   - Flushes the output to ensure complete output delivery.

---

## Error Handling and Exit Codes

scrape-cli handles various error scenarios gracefully:

- **Incorrect Argument Usage:**
  - If no expression is provided with `-e`, the tool will print an error and display the help message.
  - Specific checks (such as an incorrect order with `-eb`) generate an immediate exit with an error message.

- **Input Errors:**
  - Non-existent file paths and network errors when fetching URLs are caught, and a descriptive message is printed.
  
- **HTML Parsing Errors:**
  - Parsing errors caused by malformed HTML raise an exception which is caught, printed, and the tool exits with an error code.

- **Exit Codes:**
  - When using the `-x/--check_existence` option, the tool exits with:
    - Code 0 if matching elements are found.
    - Code 1 if no matching elements are found.

---

## Development and Packaging

The project is structured as follows:

- **setup.py:**
  - Specifies package metadata, dependencies, and defines the console script entry point (`scrape=scrape_cli.scrape:main`) which makes the command `scrape` available.
  
- **scrape_cli/\_\_init\_\_.py:**
  - Contains package metadata such as version, author, and exposes the main function.
  
- **scrape_cli/scrape.py:**
  - The main script that implements all the functionality described above.

To contribute or modify the tool, you can clone the repository, make changes, and test locally before packaging and potentially publishing the updated version.

---

## License and Authors

scrape-cli is licensed under the MIT License.  

- **Author:** Andrea Borruso  
- **Contact:** aborruso@gmail.com  
- **Source Code Repository:** [https://github.com/aborruso/scrape-cli](https://github.com/aborruso/scrape-cli)

---

This documentation provides an extensive overview of scrape-cli’s features, internals, and usage. For further questions or contributions, please refer to the repository or reach out to the maintainer. Enjoy scraping!
