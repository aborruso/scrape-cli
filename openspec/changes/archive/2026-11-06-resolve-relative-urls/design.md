## Context

All output modes read attribute values from elements selected by XPath. The input can be a URL, a local file or stdin, and only the first has a page URL. In the HTML standard, the base of a document is its first `<base>` with an `href`, itself resolved against the document URL.

## Goals / Non-Goals

**Goals:**

- Absolute `href` and `src` in default, `-b`, `-a`, `-j` and `--json-array` output.
- The same base a browser would use.
- A clear error when no base exists, rather than relative values that look resolved.

**Non-Goals:**

- `srcset`, `action`, `poster`, `data-*` and URLs inside CSS. They can come later if real cases ask for them.
- URL normalization beyond what `urljoin` does.
- `-r` input: `<base>` is an HTML concept, and XML has its own `xml:base`.

## Decisions

**Resolve at output time, not on the parsed document.** Rewriting the document first would be shorter, but `a[href^="/"]` and `//a[starts-with(@href, "/go")]` would then silently match nothing. Selected elements are copied before rewriting, so an element matched by two `-e` is not changed under the second one.

**Recognize attribute results through lxml.** XPath attribute results carry `is_attribute` and `attrname`, also in unions. `//a/@href` and `//img/@src` are resolved, `//a/@id` is not.

**Function results are not resolved.** `string(//a/@href)` and `concat()` return a value with `is_attribute` false, so nothing tells that it is a URL. The help says so, and `//a/@href` is the form to use.

**`--base-url` takes the place of the document URL, not of `<base href>`.** This matches the standard and gives the same result for `scrape URL` and `curl URL | scrape --base-url URL`. The alternative, overriding `<base href>`, would make the two differ.

**No base is an error, even when all values happen to be absolute.** Exit code 1 and a message pointing to `--base-url`. The outcome then depends on the command, not on the content of the page. A `<base href>` that is absolute on its own is a valid base.

**`-r` is rejected, `-t` and `-x` ignore the flag.** With `-r` the request cannot be honoured, so it fails. `-t` and `-x` print no attribute values, and this follows how `-b` is ignored with `-t`.

**Values `urljoin` cannot parse stay as they are.** `http://[bad` raises `ValueError`. One bad link does not lose the whole page.

**Values are stripped before joining.** `urljoin` keeps surrounding spaces, as tested: `"  /y  "` gives `https://e.org/y  `. Browsers remove them.

## Risks / Trade-offs

- [Scripts that abbreviate `--argument` as `--a` get an ambiguous option error] → The forms `-a` and `--argument` keep working.
- [A relative `<base href>` with no page URL gives an error, though the absolute links on the page would be fine] → Same rule as no base at all; `--base-url` solves it.
- [`#frag` and an empty `href` become the page URL plus fragment, or the page URL itself] → It is what a browser does, and these values stop being recognizable as internal links. The original is available without the flag.
