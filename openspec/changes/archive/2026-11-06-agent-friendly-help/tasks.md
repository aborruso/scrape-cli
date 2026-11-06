## 1. Clean errors

- [x] 1.1 Catch `etree.XPathError` during XPath evaluation, with a one-line error and a test
- [x] 1.2 Catch `OSError` when reading the input file, with a one-line error and a test

## 2. Help

- [x] 2.1 Rewrite the description and the option texts in `scrape_cli/scrape.py`
- [x] 2.2 Add commented examples and the sections `output:`, `exit codes:` and `notes:`
- [x] 2.3 Run a command for the statements in the help, and correct those that fail
- [x] 2.4 Add tests for the help sections and the documented exit codes

## 3. Verification

- [x] 3.1 Compare the stdout of `-e`, `-a`, `-b`, `-t` and `-j` on `resources/test.html` with version 1.3.2
- [x] 3.2 Confirm that the tests pass on all Python versions in CI

## 4. Documentation and release

- [x] 4.1 Update `LOG.md`
- [x] 4.2 Bump the version and update `CHANGELOG.md`
- [x] 4.3 Archive this change after the release
