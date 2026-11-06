## Context

`-j` joins all results in one document and passes it to `xmltodict`. That step groups elements by tag, merges strings into `#text`, and adds to `body` any text that follows a matched element. A list with one item per result cannot go through it.

## Goals / Non-Goals

**Goals:**

- One output shape for any number of results.
- Results in the order of the expressions, also when elements and strings are mixed.

**Non-Goals:**

- Changing the shape of `-j`. The text following an element is removed from all output modes as a separate bug fix, so `-j` no longer shows it in `#text`.
- Telling which `-e` produced a result: the list is flat, by decision of the maintainer.
- Typed values: `count()` stays `"2"`, as in `-j`.
- Handling HTML input that parses to no document, which is a separate fix.

## Decisions

**Each element is converted on its own.** The element is serialized with `with_tail=False` and passed to `xmltodict.parse`, which gives the object with the tag as key. The alternative, `force_list` on the joined document, keeps the grouping by tag and loses the order.

**Strings and element markup share one list until output.** Markup is kept as `bytes` and strings as `str`, and the conversion happens in the output step, inside the existing `ExpatError` handling. The error for attribute names such as `@click` stays the same.

**Comments and processing instructions are skipped.** `//comment()` returns nodes whose `tag` is not a string, and they have no object form. `-j` drops them too.

**`--json-array` sets `args.json`.** The existing checks against `-t`, `-x` and `-a` then apply with no new code.

## Risks / Trade-offs

- [Scripts that abbreviate `--json` as `--js` or `--jso` get an ambiguous option error] → The documented forms `-j` and `--json` keep working.
- [The tag as key forces scripts to read `.a` on each item] → It is what tells an `<a>` from a `<p>` with several `-e`.
