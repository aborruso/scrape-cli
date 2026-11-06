# agent-help Specification

## Purpose
Define what `scrape --help` documents and the error behaviour it promises, so that an agent can use the CLI without reading other documents.

## Requirements
### Requirement: Help documents the usage contract

`scrape --help` SHALL exit 0 and document on stdout the examples, the output of each mode, the exit codes and the known edge cases, so that no other document is needed to use the tool.

#### Scenario: Sections are present

- **WHEN** `scrape --help` runs
- **THEN** the exit code is 0 and stdout contains the sections `examples:`, `output:`, `exit codes:` and `notes:`

#### Scenario: Limits are stated

- **WHEN** an agent reads the help
- **THEN** it states that JavaScript is not run, that no match is not an error, that `-x` evaluates only the first `-e`, and that `-j` fails on attribute names that are not valid XML

### Requirement: Exit codes match the help

The CLI SHALL exit 0 on success, also with no match, SHALL exit 1 on errors and on no match with `-x`, and SHALL exit 2 on invalid usage.

#### Scenario: No match

- **WHEN** `scrape -e "//nothing"` matches nothing
- **THEN** the exit code is 0 and stdout is empty

#### Scenario: No match with check existence

- **WHEN** `scrape -x -e "//nothing"` matches nothing
- **THEN** the exit code is 1 and stderr has no error message

#### Scenario: First expression only with check existence

- **WHEN** `scrape -x -e "//nothing" -e "//h1"` runs on a page with an `h1`
- **THEN** the exit code is 1

#### Scenario: Unknown option

- **WHEN** an unknown option is passed
- **THEN** the exit code is 2

### Requirement: Foreseeable failures give a clean error

The CLI SHALL report an invalid XPath expression and unreadable input with a message on stderr and exit code 1, with no traceback.

#### Scenario: Invalid XPath

- **WHEN** `scrape -e "//[bad"` runs
- **THEN** the exit code is 1, stderr contains `Error: invalid XPath` and no traceback

#### Scenario: Input is a directory

- **WHEN** the input path is a directory
- **THEN** the exit code is 1, stderr contains `Error: cannot read` and no traceback

### Requirement: Successful output does not change

The rewrite of the help SHALL NOT change flags or the stdout of successful runs.

#### Scenario: Same output as the previous version

- **WHEN** `-e`, `-a`, `-b`, `-t` and `-j` run on `resources/test.html`
- **THEN** stdout is the same as in version 1.3.2

