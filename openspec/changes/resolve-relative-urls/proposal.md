## Why

Links and images extracted from a page often have relative values: `//a/@href` on `https://www.iana.org/help/example-domains` returns `/domains`. Out of the page's context such a value cannot be used, and today each script must rebuild the URL on its own, usually ignoring `<base href>`.

## What Changes

- New `--absolute-urls` flag: `href` and `src` values in the output become absolute URLs.
- New `--base-url URL` option: sets the page URL for stdin and local files, and implies `--absolute-urls`.
- With a URL as input, the page URL is the final one, after redirects.
- `<base href>` is honoured as in the HTML standard.
- Selection does not change: expressions still see the original values, so `a[href^="/"]` keeps matching.
- Output without these flags does not change.

## Capabilities

### New Capabilities

- `url-resolution`: which values become absolute, from which base, and what happens when no base exists.

### Modified Capabilities

None. The JSON shapes in `json-output` do not change, only the attribute values inside them.

## Impact

- `scrape_cli/scrape.py`: two options, base calculation, resolution at output time.
- `tests/test_scrape.py`: new tests.
- `--help`, `README.md`, `manual.html`, `LOG.md`, `CHANGELOG.md`.
- No new dependencies: `urllib.parse.urljoin` is in the standard library.
