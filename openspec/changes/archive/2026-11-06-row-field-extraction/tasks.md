## 1. Tests

- [x] 1.1 Add tests for each scenario in `specs/row-extraction/spec.md`, and confirm that they fail

## 2. Code

- [x] 2.1 Recognize a leading `./` in `is_xpath`
- [x] 2.2 Add `--row`, `--field` and `--jsonl`, with all the checks on invalid use
- [x] 2.3 Add the row extraction path, using the `--absolute-urls` base when present
- [x] 2.4 Print the list or the JSON Lines
- [x] 2.5 Confirm that all tests pass and that output without the new options is unchanged

## 3. Documentation

- [x] 3.1 Update `--help`, with a test for the new text
- [x] 3.2 Update `README.md` and `manual.html`, with a `jq` and a DuckDB example, both run
- [x] 3.3 Update `LOG.md`

## 4. Release

- [x] 4.1 Bump the version and update `CHANGELOG.md`, after confirmation
- [x] 4.2 Archive this change after the release
