## Why

To get title, link and date for each article of a list, today a script runs one expression per field and pairs the results by position. When an article has no date, every following date ends up on the wrong article, and nothing signals it. The CLI needs a way to extract fields per element, keeping them together.

## What Changes

- New `--row EXPR` option: selects the elements that become one result each.
- New repeatable `--field NAME=EXPR` option: evaluated inside each row.
- The output is a JSON list with one object per row, where every object has the same keys and every value is a string or `null`.
- New `--jsonl` flag: one JSON value per line, with `--row` or instead of the list of `--json-array`.
- `./h2` becomes a recognized XPath expression: today it is treated as a CSS selector and fails.
- Output without these options does not change, and `--json-array` keeps its format.

```bash
scrape --row "article" --field "title=h2" --field "url=.//a/@href" --field "date=time/@datetime" page.html
```

```json
[
  {"title": "One", "url": "/1", "date": "2026-01-01"},
  {"title": "Two", "url": "/2", "date": null}
]
```

## Capabilities

### New Capabilities

- `row-extraction`: syntax of rows and fields, output shape, JSON Lines, invalid use.

### Modified Capabilities

None. `json-output` keeps its requirements: `--jsonl` adds a way to print the same items.

## Impact

- `scrape_cli/scrape.py`: options, a separate extraction path, `is_xpath`.
- `tests/test_scrape.py`: new tests.
- `--help`, `README.md`, `manual.html`, `LOG.md`, `CHANGELOG.md`.
- No new dependencies.
- Interaction with `resolve-relative-urls`: `--absolute-urls` applies to `href` and `src` field values.
