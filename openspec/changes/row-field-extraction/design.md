## Context

`-e` evaluates each expression on the whole document, and the results are flat. CSS expressions are converted to `descendant-or-self::...`, so they already work relative to an element. XPath is relative when written so. Standard CSS cannot select attribute values: `a::attr(href)` is passed as XPath, because of `::`, and fails.

## Goals / Non-Goals

**Goals:**

- Fields of one element stay together, also when one is missing.
- One output shape, whatever the page contains.
- Output ready for `jq` and DuckDB.

**Non-Goals:**

- Nested rows and fields.
- A template or configuration file: fields are command-line options.
- CSS syntax for attributes, such as `::attr()`: XPath covers it, and non-standard selectors would add a third language.
- CSV output: `jq` and DuckDB convert JSON Lines.

## Decisions

**`--row` and repeatable `--field NAME=EXPR`, not a single mini-language.** A single string, such as `"article{title: h2, url: a@href}"`, is shorter, but needs a new parser and a quoting rule inside the shell's quoting. With separate options, each expression stays an ordinary XPath or CSS one, already auto-detected, and the split is on the first `=`, so `t=a[href="x"]` works.

**A field gives the first match, as a string or `null`.** The shape is then known before reading the page. The alternatives are a list for each field, which forces `.[0]` on all of them, or a list only with several matches, which brings back the problem this change wants to solve. Fields with several values can get their own syntax later, without breaking this one.

**Strings for every value.** Elements give cleaned text, as with `-t`; attributes their value; XPath functions the string form, so `count()` gives `"2"`, as in `--json-array`.

**`null` means no match, `""` means a match with no text.** Telling them apart costs nothing, and a script may care.

**Rows with all fields `null` stay in the list.** The number of objects then equals the number of rows.

**Absolute XPath in a field is an error.** A field starting with `/` or `(/` would read the whole document on each row and return the same value everywhere, with no sign of the mistake. Inside functions, as in `string(//h2)`, it is not detected: the help says to write `string(.//h2)`.

**`--jsonl` also works with `--json-array` items.** With `--row` it prints each object on a line. Used alone it implies `--json-array`, so there is one definition of what an item is. Nothing is lost in the list form, and the output is still built in memory: this is about format, not streaming.

**Other flags.** `-e`, `-t`, `-x`, `-a`, `-b`, `-j` and `--json-array` are rejected with `--row`, because each defines a different output. `-r` is allowed, for feeds such as `item` with `title` and `link`.

**`is_xpath` recognizes a leading `./`.** Field expressions make this form common, and today it fails with a CSS error.

## Risks / Trade-offs

- [`a/@href` looks for `a` among direct children, so the field is `null` when the link is deeper] → The help and examples use `.//a/@href`. It is plain XPath, and the alternative of rewriting expressions would make them mean something else here than with `-e`.
- [A field with several matches silently loses the others] → Documented; it is the price of the fixed shape.
- [Scripts that abbreviate `--rawinput` as `--r` get an ambiguous option error] → `-r` and `--rawinput` keep working.
