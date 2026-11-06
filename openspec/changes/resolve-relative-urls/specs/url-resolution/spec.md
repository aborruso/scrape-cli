## ADDED Requirements

### Requirement: Absolute URLs in the output

The CLI SHALL, with `--absolute-urls` or `--base-url`, output `href` and `src` values as absolute URLs in default, `-b`, `-a`, `-j` and `--json-array` output.

#### Scenario: Attribute expression

- **WHEN** `scrape --base-url https://e.org/a/b.html -e "//a/@href"` matches `/x`
- **THEN** the output is `https://e.org/x`

#### Scenario: Attribute option

- **WHEN** `-a src` is used on `<img src="i.png">` with base `https://e.org/a/b.html`
- **THEN** the output is `https://e.org/a/i.png`

#### Scenario: Element output

- **WHEN** an element is selected whose descendants have `href` or `src`
- **THEN** the element and its descendants show absolute values

#### Scenario: JSON output

- **WHEN** `--json-array` selects `<a href="/x">l</a>` with base `https://e.org/`
- **THEN** the item is `{"a": {"@href": "https://e.org/x", "#text": "l"}}`

#### Scenario: Other attributes

- **WHEN** the expression is `//a/@id`
- **THEN** the value does not change

#### Scenario: Values that are already absolute

- **WHEN** the value is `https://o.org/p`, `mailto:a@b.it` or `javascript:void(0)`
- **THEN** the value does not change

#### Scenario: Value that cannot be parsed

- **WHEN** the value is `http://[bad`
- **THEN** the value does not change and the exit code is 0

#### Scenario: Surrounding spaces

- **WHEN** the value is `  /y  ` with base `https://e.org/`
- **THEN** the output is `https://e.org/y`

#### Scenario: Flags not used

- **WHEN** neither `--absolute-urls` nor `--base-url` is used
- **THEN** the output keeps the original values

### Requirement: Selection on original values

The CLI SHALL evaluate expressions on the original attribute values.

#### Scenario: Predicate on a relative value

- **WHEN** `--absolute-urls` is used with `a[href^="/"]` on a page with `<a href="/x">`
- **THEN** the element matches, and its output shows the absolute value

#### Scenario: Element matched by two expressions

- **WHEN** two `-e` match the same element
- **THEN** both give the same output

#### Scenario: XPath function

- **WHEN** the expression is `string(//a/@href)`
- **THEN** the value does not change

### Requirement: Base of the document

The CLI SHALL use as base the first `<base>` with an `href`, resolved against the page URL, or the page URL when there is no such element. The page URL SHALL be the `--base-url` value if given, otherwise the final URL of the request.

#### Scenario: URL input after a redirect

- **WHEN** the input URL redirects to `https://www.e.org/a/`
- **THEN** the page URL is `https://www.e.org/a/`

#### Scenario: Relative base element

- **WHEN** the page has `<base href="/sub/">` and the page URL is `https://e.org/a/b.html`
- **THEN** `i.png` gives `https://e.org/sub/i.png`

#### Scenario: Several base elements

- **WHEN** the page has `<base href="/sub/">` followed by `<base href="/other/">`
- **THEN** only `/sub/` is used

#### Scenario: Option and base element

- **WHEN** `--base-url https://e.org/` is used on a page with `<base href="/sub/">`
- **THEN** `i.png` gives `https://e.org/sub/i.png`

#### Scenario: Base element that cannot be used

- **WHEN** the page has `<base href="http://[bad">` and the page URL is `https://e.org/a/b.html`
- **THEN** `i.png` gives `https://e.org/a/i.png`

#### Scenario: Absolute base element with no page URL

- **WHEN** stdin has `<base href="https://e.org/">` and `--absolute-urls` is used
- **THEN** `/x` gives `https://e.org/x`

### Requirement: Invalid use

The CLI SHALL exit with code 1 and a one-line error on stderr, leaving stdout empty, when it cannot determine an absolute base or when the flags cannot be honoured.

#### Scenario: No base

- **WHEN** `--absolute-urls` is used on stdin or a local file, with no `--base-url` and no absolute `<base href>`
- **THEN** the CLI exits with code 1 and the error mentions `--base-url`

#### Scenario: Base option that is not absolute

- **WHEN** the value of `--base-url` has no scheme and host, such as `page.html`
- **THEN** the CLI exits with code 1

#### Scenario: Raw input

- **WHEN** `--absolute-urls` or `--base-url` is used with `-r`
- **THEN** the CLI exits with code 1

### Requirement: Modes with no attribute output

The CLI SHALL ignore `--absolute-urls` and `--base-url` with `-t` and `-x`.

#### Scenario: Text output

- **WHEN** `--absolute-urls` is used with `-t` on stdin with no base
- **THEN** the output is the text and the exit code is 0
