## Why

Agents usually learn a CLI by running `--help` once, and the current help only lists options. It does not say what a no-match returns, what the exit codes mean, or which flags are rejected, so an agent has to guess or read the README. Two error paths also end in a Python traceback, which costs context and gives no usable message.

## What Changes

- Rewrite the `--help` text: what the tool does and does not do (no JavaScript, no prompts), precise option descriptions, commented examples, output per mode, exit codes, edge cases.
- Report an invalid XPath expression with a one-line error instead of a traceback.
- Report unreadable input, such as a directory, with a one-line error instead of a traceback.
- No flag is added or removed, and the output of a successful run does not change.

## Capabilities

### New Capabilities

- `agent-help`: what `scrape --help` documents, and the error behaviour it promises.

### Modified Capabilities

None. `json-output` keeps its requirements: the help describes that behaviour without changing it.

## Impact

- `scrape_cli/scrape.py`: argparse texts, error handling around XPath evaluation and file reading.
- `tests/test_scrape.py`: tests for help sections, exit codes and the two errors.
- No new dependencies. Scripts that parse the help text would see a different text. Exit codes stay the same, and the two error paths keep exit code 1.
