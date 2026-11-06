## Context

`scrape` has a single command and nine options. Three CLIs were used as references:

- `opensdmx --help`: commented examples and written constraints in the help itself.
- `mlr`: precise wording on edge cases, and a `help` topic system built for hundreds of verbs.
- `duckdb` 2.0: a dense `.help agent` text, and a `-agent` output mode with row and byte caps, JSON errors and automatic activation from variables such as `AI_AGENT`.

## Goals / Non-Goals

**Goals:**

- One `scrape --help` is enough to use the tool correctly, with no other document.
- Every statement in the help is true and checked by running a command.
- Failures that can be foreseen give one line on stderr.

**Non-Goals:**

- An agent output mode that changes the data on stdout. See Open Questions.
- Help topics, a `which` command, or a dry run: they serve CLIs with many commands or network plans.
- Fixing the ISO-8859-1 fallback. See Open Questions.

## Decisions

**Everything in `--help`, no separate flag.** An agent runs `--help` first, so a `--help-agent` would be found late or never, and it would duplicate the text. Alternative considered: `mlr`-style topics, rejected because one command does not need routing.

**Plain argparse with a raw epilog.** Keeps the single-file CLI with no new dependency. Sections stay within 80 columns. Alternative considered: a richer help library, rejected as a dependency for static text.

**Catch `etree.XPathError` and `OSError`, nothing broader.** These are the foreseeable failures. A generic `except Exception` would hide real bugs behind a clean message.

**Document real behaviour, including limits.** The help states that `-t` with `-e` includes script text, that `-x` evaluates only the first `-e`, and that `-j` fails on attribute names like `@click`. Writing this text exposed the ISO-8859-1 limit below.

## Risks / Trade-offs

- [Help text drifts from behaviour] → Tests cover the help sections and the exit codes it documents. The other statements are not tested automatically.
- [Longer help costs context on each read] → About 70 lines, and a single read is enough.
- [With `-x`, exit 1 means both "no match" and "error"] → Documented: stderr is empty on no match. Changing the code would break existing scripts.

## Open Questions

- **Agent mode like `duckdb -agent`.** Considered and declined on 2026-11-06: it would change the data on stdout, and automatic activation would alter pipelines that run inside an agent.
- **ISO-8859-1 fallback.** The code in `main` that retries with ISO-8859-1 does not run for HTML input: `HTMLParser(encoding='utf-8', recover=True)` does not raise `UnicodeDecodeError`, so an ISO-8859-1 file with no meta tag comes out with wrong characters. Verified on a test input during this work. The help documents what happens. The fix, or the removal of that code, belongs to a separate change.
