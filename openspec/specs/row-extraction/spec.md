# row-extraction Specification

## Purpose
TBD - created by archiving change row-field-extraction. Update Purpose after archive.
## Requirements
### Requirement: Rows and fields

The CLI SHALL, with `--row` and at least one `--field NAME=EXPR`, print a JSON list with one object per element selected by `--row`, in document order, with one key per field in the order given. Field expressions SHALL be evaluated relative to the row, and SHALL accept XPath or CSS as `-e` does.

#### Scenario: All fields present

- **WHEN** `scrape --row "article" --field "title=h2" --field "url=.//a/@href"` matches two articles
- **THEN** the output is a list of two objects, each with the keys `title` and `url`, in that order

#### Scenario: Missing field

- **WHEN** the second of two articles has no date
- **THEN** its `date` is `null`, and the first article keeps its own date

#### Scenario: No rows

- **WHEN** `--row` matches nothing
- **THEN** the output is `[]` and the exit code is 0

#### Scenario: Row with no field

- **WHEN** a row matches none of the fields
- **THEN** the row is an object with all values `null`

### Requirement: Field values

The CLI SHALL give each field the string form of its first match, or `null` if there is none.

#### Scenario: Element

- **WHEN** the field selects `<h2><a href="/1">One</a></h2>`
- **THEN** the value is `One`

#### Scenario: Attribute

- **WHEN** the field is `.//a/@href` and matches `/1`
- **THEN** the value is `/1`

#### Scenario: XPath function

- **WHEN** the field is `count(.//a)` and the row has two links
- **THEN** the value is `"2"`

#### Scenario: Several matches

- **WHEN** the field matches several elements
- **THEN** the value comes from the first

#### Scenario: Match with no text

- **WHEN** the field selects an empty `<h2></h2>`
- **THEN** the value is `""`

#### Scenario: Absolute URLs

- **WHEN** `--absolute-urls` is used and the field is `.//a/@href`
- **THEN** the value is an absolute URL

### Requirement: JSON Lines

The CLI SHALL, with `--jsonl`, print one JSON value per line and nothing else: the objects with `--row`, otherwise the items of `--json-array`.

#### Scenario: Rows

- **WHEN** `--jsonl` is used with `--row` matching two elements
- **THEN** the output has two lines, each a JSON object

#### Scenario: Items

- **WHEN** `scrape --jsonl -e "//a/@href"` matches two values
- **THEN** the output has two lines, each a JSON string

#### Scenario: No results

- **WHEN** nothing matches
- **THEN** the output is empty and the exit code is 0

#### Scenario: Non-ASCII text

- **WHEN** a value contains `è`
- **THEN** the line contains `è`, not an escape sequence

### Requirement: Relative XPath with a leading dot

The CLI SHALL treat an expression starting with `./` as XPath.

#### Scenario: Expression with -e

- **WHEN** `scrape -e "./body/h1"` is used on a page with that structure
- **THEN** the element is selected and the CLI shows no CSS error

### Requirement: Invalid use

The CLI SHALL exit with code 1 and a one-line error on stderr, leaving stdout empty, when rows and fields cannot be honoured.

#### Scenario: Field without row, or row without field

- **WHEN** `--field` is used without `--row`, or `--row` without `--field`
- **THEN** the CLI exits with code 1

#### Scenario: Conflicting flag

- **WHEN** `--row` is used with `-e`, `-t`, `-x`, `-a`, `-b`, `-j` or `--json-array`
- **THEN** the CLI exits with code 1

#### Scenario: Malformed field

- **WHEN** a field has no `=`, or its name or expression is empty
- **THEN** the CLI exits with code 1 and the error shows the field

#### Scenario: Repeated name

- **WHEN** two fields have the same name
- **THEN** the CLI exits with code 1

#### Scenario: Absolute XPath in a field

- **WHEN** a field expression starts with `/` or `(/`, such as `title=//h2`
- **THEN** the CLI exits with code 1 and the error suggests `.//`

#### Scenario: Row that does not select elements

- **WHEN** `--row` selects strings, such as `//a/@href`
- **THEN** the CLI exits with code 1

#### Scenario: Invalid expression

- **WHEN** a row or field expression is not valid XPath or CSS
- **THEN** the CLI exits with code 1 and shows no traceback

#### Scenario: JSON Lines with other output modes

- **WHEN** `--jsonl` is used with `-t`, `-x`, `-a`, `-b` or `-j`
- **THEN** the CLI exits with code 1

