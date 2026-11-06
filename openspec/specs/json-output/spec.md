# json-output Specification

## Purpose

Define the `-j`/`--json` output of scrape-cli, which converts extraction results to structured JSON with no external tool. This spec records the behaviour as of version 1.3.1.
## Requirements
### Requirement: Element results

The CLI SHALL convert element results with `xmltodict`, wrapped in `html` and `body`, without requiring `-b`.

#### Scenario: One element

- **WHEN** `scrape -je "a"` matches a single element
- **THEN** `html.body.a` is an object, with attributes as `@name` and text as `#text`

#### Scenario: Several elements

- **WHEN** the expression matches several elements with the same tag
- **THEN** that tag's value in `html.body` is an array

#### Scenario: No results

- **WHEN** the expression matches nothing
- **THEN** `html.body` is `null` and the exit code is 0

### Requirement: String results

The CLI SHALL return results that are only strings, such as `@attr`, `text()` or XPath functions, directly in `html.body`, ignoring whitespace-only strings.

#### Scenario: One string

- **WHEN** `scrape -je "string(//h1)"` produces one string
- **THEN** `html.body` is that string

#### Scenario: Several strings

- **WHEN** `scrape -je "//a/@href"` produces several strings
- **THEN** `html.body` is an array of strings

#### Scenario: Special characters

- **WHEN** a string contains `&` or `<`
- **THEN** the string appears unchanged in the JSON

#### Scenario: Elements and strings together

- **WHEN** an expression returns both elements and strings
- **THEN** the strings are joined in `html.body.#text`

### Requirement: Conversion errors

The CLI SHALL exit with code 1 and a one-line error on stderr when the results cannot be converted, leaving stdout empty.

#### Scenario: Attribute name that is not valid XML

- **WHEN** a matched element has an attribute such as `@click` or `:bind`
- **THEN** the CLI prints an error starting with `Error:` and shows no traceback

### Requirement: Flag combinations

The CLI SHALL reject `-j` combined with `-t`, `-x` or `-a`, and SHALL reject the argument `-ej` with a message pointing to `-je`.

#### Scenario: Conflicting flag

- **WHEN** `-j` is used with `-t`, `-x` or `-a`
- **THEN** the CLI exits with code 1 and an error on stderr

#### Scenario: Wrong flag order

- **WHEN** an argument is exactly `-ej`
- **THEN** the CLI exits with code 1 and suggests `-je`

#### Scenario: Letters inside other arguments

- **WHEN** a filename or selector contains `-ej`, such as `page-ej.html`
- **THEN** the order check does not trigger

### Requirement: Always-a-list output

The CLI SHALL, with `--json-array`, print a flat top-level JSON list with one item per result, in the order of the expressions, and with no `html` or `body` envelope.

#### Scenario: No results

- **WHEN** `scrape --json-array -e "p.none"` matches nothing
- **THEN** the output is `[]` and the exit code is 0

#### Scenario: One result

- **WHEN** the expression produces one result
- **THEN** the output is a list with one item

#### Scenario: Several results

- **WHEN** the expressions produce several results
- **THEN** the output is a list with one item for each result

#### Scenario: Elements and strings together

- **WHEN** `scrape --json-array -e "//a/@href" -e "b"` matches two attributes and one element
- **THEN** the output is `["x", "y", {"b": "tre"}]`, and swapping the expressions swaps the items

### Requirement: Items of the list

The CLI SHALL represent strings as JSON strings and elements as objects with the tag as key, converted as in `-j`, and SHALL NOT produce an item for empty strings, comments or processing instructions.

#### Scenario: Element

- **WHEN** `<a href="x">l</a>` is matched
- **THEN** the item is `{"a": {"@href": "x", "#text": "l"}}`

#### Scenario: Text following an element

- **WHEN** `b` matches the `<b>` in `<p>a <b>x</b> coda</p>`
- **THEN** the output is `[{"b": "x"}]`

#### Scenario: XPath function

- **WHEN** `count(//p)` evaluates to 2
- **THEN** the output is `["2"]`

#### Scenario: Empty string

- **WHEN** `string(//none)` evaluates to an empty string
- **THEN** the output is `[]`

#### Scenario: Comment

- **WHEN** `//comment()` matches a comment
- **THEN** the output is `[]`

### Requirement: Always-a-list flag combinations

The CLI SHALL treat `--json-array` as `-j` for flag combinations and conversion errors.

#### Scenario: Used without -j

- **WHEN** `--json-array` is used without `-j`
- **THEN** the output is JSON

#### Scenario: Conflicting flag

- **WHEN** `--json-array` is used with `-t`, `-x` or `-a`
- **THEN** the CLI exits with code 1 and an error on stderr

#### Scenario: Attribute name that is not valid XML

- **WHEN** a matched element has an attribute such as `@click` or `:bind`
- **THEN** the CLI exits with code 1, prints an error starting with `Error:`, and leaves stdout empty

