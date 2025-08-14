# Copilot Instructions for scrape-cli

## Project Overview
- **scrape-cli** is a Python command-line tool for extracting HTML elements using XPath or CSS3 selectors.
- The tool is inspired by [dsutils/scrape](https://github.com/jeroenjanssens/dsutils/blob/master/scrape) but adds modern packaging, CLI options, and text extraction features.
- Main logic is in `scrape_cli/scrape.py`, with CLI entry defined in `pyproject.toml` (`scrape = "scrape_cli.scrape:main"`).

## Key Files & Structure
- `scrape_cli/scrape.py`: Main CLI logic, argument parsing, selector handling, extraction routines.
- `scrape_cli/__init__.py`: Version and author metadata.
- `pyproject.toml`: Modern Python packaging config (setuptools backend, dependencies, CLI entry point).
- `resources/test.html`: Example HTML for manual and automated tests.
- `README.md`: Usage examples, conventions, and installation instructions.

## Developer Workflows
- **Build**: Use `python3 -m build` to generate wheel and sdist in `dist/`.
- **Test install**: `pip install dist/<package>.whl` or `.tar.gz`.
- **Validate package**: `twine check dist/*` before uploading to PyPI.
- **Release**: Tag with `git tag -a <version> -m "Release <version>"` and push. Manually create a GitHub release after pushing the tag.
- **Update version**: Change in both `pyproject.toml` and `scrape_cli/__init__.py`.
- **Badge update**: After release, update the PyPI badge in `README.md` to reflect the new version.

## Patterns & Conventions
- **Selector handling**: The CLI distinguishes between XPath and CSS selectors. Use `-e` for the query, `-a` for attribute extraction, `-t` for text extraction.
- **Option order**: When combining `-b` and `-e`, use `-be` (body first, then expression) for correct output.
- **Text extraction**: The `-t` option excludes `<script>` and `<style>` tags and cleans whitespace.
- **Manual tests**: Use `resources/test.html` for local testing of selector logic and CLI options.

## External Dependencies
- Relies on `lxml`, `cssselect`, and `requests` for parsing and extraction.
- CLI install recommended via `pipx` or `uv` for isolation.

## Example Commands
- Extract all links: `scrape -e "a" -a href resources/test.html`
- Extract text: `scrape -te 'h1, h2, h3' resources/test.html`
- Check element existence: `scrape -e "#main-title" --check-existence resources/test.html`

## Integration Points
- No external service calls; all extraction is local and synchronous.
- Designed for piping HTML from curl/wget or reading local files.

---

## Language Convention
- All text, including commit messages, documentation, and comments, must be written in English.

**If any section is unclear or missing important project-specific details, please provide feedback so this guide can be improved.**
