## ADDED Requirements

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
