# 2026-11-06

- [1.3.7] Added `--row` and `--field NAME=EXPR`: one JSON object per element, with the same keys and each value a string or `null`, so fields stay together when one is missing. Added `--jsonl`: one JSON value per line. Added `--absolute-urls` and `--base-url`: absolute `href` and `src` values in the output, honouring `<base href>`. Errors with `--json-array` now name that flag. Expressions starting with `./` are now recognized as XPath.
- [1.3.6] Added `--json-array`: always a flat JSON list, one item per result, in the order of the expressions. Text following a selected element no longer appears in the output of `-e`, `-b` and `-j`: scripts that relied on it need updating. With `-r`, malformed input now gives `Error parsing XML:`. HTML with no elements, such as only spaces or comments, gives a one-line error instead of a traceback.
- [1.3.5] HTML that is not valid UTF-8 and has no usable meta charset is now read as Windows-1252, then ISO-8859-1, so `€` and curly quotes come out correct (#29).
- [1.3.4] HTML that is not valid UTF-8 and has no usable meta charset is now read as ISO-8859-1: the previous fallback never ran, so characters came out wrong with no error. Added `scrape-cli` as a second name for the `scrape` command.
- [1.3.3] `--help` rewritten so that agents and scripts need no other document: output per mode, exit codes, edge cases, commented examples. Invalid XPath expressions and unreadable input now give a one-line error instead of a traceback.
- [1.3.2] XPath functions returning a single value now work: `string()` and `normalize-space()` no longer split the text one character per line, `count()` and `boolean()` no longer crash with a traceback, and `-x` follows the function's value.
- [1.3.1] `-j`: expressions returning only strings (`@attr`, `text()`) now give an array when there are multiple results, instead of one string joined by newlines. Fixed a traceback on strings containing `&` or `<`; attribute names that are not valid XML (`@click`, `:bind`) now give a one-line error. `-eb`/`-ej` order checks no longer trigger on filenames and selectors containing those letters.

# 2026-04-30

- [1.3.0] Added native `-j`/`--json` flag to output structured JSON without needing `-b` or piping through external `xq`. Internally uses `xmltodict` (the same converter `xq` uses), so the output is identical. `-j` is mutually exclusive with `-t`, `-x` (`--check-existence`), and `-a` (`--argument`).

# 2026-04-16

- [1.2.4] Uniformato stile errori: `-eb` usa ora `print(stderr)+sys.exit(1)`; `--check-existence` è ora il flag primario (kebab-case), rimosso alias duplicato `--check_existence`.

# 2026-04-06

- [1.2.3] Agent-friendly CLI improvements: all error messages now go to stderr; `--help` extended with examples for all major use cases; missing `-e` error replaced with a concise actionable message.

# 2026-02-23

- [1.2.2] Added `-u`/`--user-agent` option for HTTP requests; set a default browser-like User-Agent to avoid 403 errors on sites like Wikipedia.

# 2026-02-22

- [1.2.1] Added automated pytest coverage for XPath/CSS detection and CLI options, including URL/file/stdin input paths and error handling.
- Hardened runtime behavior by adding `timeout=30` to URL fetches and replacing a bare `except:` with `except Exception` in charset detection.
- Raised `requires-python` to `>=3.8`, removed legacy `setup.py`, and expanded `.gitignore` for local test/venv artifacts.

# 2025-09-07

- [1.2.0] Fixed XPath detection for expressions wrapped in parentheses: XPath expressions like `(//div[@class='coordinate lat'])[1]` are now correctly recognized as XPath instead of being incorrectly treated as CSS selectors.
- Enhanced the `is_xpath` function with additional pattern recognition for XPath-specific syntax including attribute predicates, position predicates, and XPath functions.

# 2025-08-14

- [1.1.9] Improved distinction between XPath and CSS selectors: CSS selectors like `a[href*="/talk/"]` are now handled correctly and no longer cause errors.
- Updated the `is_xpath` function to prevent false positives.

# 2025-06-02

- Added the option `-t` to extract only text content from HTML

# 2025-05-04

- Improved XPath detection with support for complex expressions (predicates, functions, and axes)

# 2025-05-02

- Added charset detection from HTML meta tags
- Added support for ISO-8859-1 encoding fallback
- Improved HTML parsing with better encoding handling

# 2020-05-05

- First version of website
