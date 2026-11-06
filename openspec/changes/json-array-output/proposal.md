## Why

The shape of `-j` output depends on the number and kind of results: `null`, a string, an object or a list, always under `html.body`. Scripts must handle each case, and with several `-e` the conversion groups elements by tag and merges strings into `#text`, so the order of the expressions is lost.

## What Changes

- New `--json-array` flag: the output is always a flat top-level JSON list, with no `html`/`body` envelope and one item per result, in the order of the expressions.
- Strings stay strings; elements become objects with the tag as key: `["x", "y", {"b": "tre"}]`.
- `--json-array` implies `-j` and has the same constraints with `-t`, `-x` and `-a`.
- `-j` output does not change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `json-output`: adds the requirements for the always-a-list output. Existing requirements do not change.

## Impact

- `scrape_cli/scrape.py`: new option, collection of the items, output.
- `tests/test_scrape.py`: new tests.
- `README.md`, `manual.html`, `--help`, `LOG.md`, `CHANGELOG.md`.
- No new dependencies.
