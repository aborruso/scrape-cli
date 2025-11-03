# Project Context

## Purpose

`scrape-cli` is a command-line tool for extracting HTML elements using XPath queries or CSS3 selectors. It's designed for web scraping, data extraction, and text processing workflows. Originally based on Jeroen Janssens' scraping tool, it has evolved to support:

- XPath and CSS3 selector queries
- Text extraction for LLM processing
- Attribute extraction from HTML elements
- Element existence checking
- URL and file input sources

## Tech Stack

- Python >=3.6
- lxml - HTML/XML parsing and XPath evaluation
- cssselect - CSS selector to XPath translation
- requests - HTTP client for URL fetching
- setuptools - packaging and distribution

## Project Conventions

### Code Style

- Python 3 style with type hints where appropriate
- UTF-8 encoding declaration in headers
- 4-space indentation
- Single-file CLI implementation in `scrape_cli/scrape.py`
- Version managed in `__init__.py` and read dynamically
- Descriptive function names (e.g., `clean_text`, `is_xpath`, `detect_charset`)

### Architecture Patterns

- Single-responsibility functions for parsing, detection, and conversion
- Command-line argument parsing with argparse
- Input flexibility: stdin, files, or URLs
- Graceful error handling with user-friendly messages
- Charset detection with fallback strategies (UTF-8 → ISO-8859-1)

### Testing Strategy

- Test HTML file provided in `resources/test.html`
- Manual testing examples documented in README
- Real-world testing with Wikipedia and other public HTML sources

### Git Workflow

- Main branch: `master`
- Concise commit messages (grammar sacrificed for brevity per user preference)
- LOG.md file for tracking project changes with date-based headings (YYYY-MM-DD)
- Version bumps coordinated with pyproject.toml and __init__.py

## Domain Context

### Web Scraping Domain

- XPath expressions: powerful query language for XML/HTML navigation
- CSS selectors: web-standard way to select elements
- Common patterns: `//`, `::`, `@attribute`, `text()`, predicates `[1]`
- Automatic detection between XPath and CSS selector syntax

### Use Cases

- Extracting structured data from web pages
- Text extraction for LLMs and NLP
- Batch processing HTML documents
- Pipeline integration with curl, wget, and other CLI tools

## Important Constraints

- Python >=3.6 required for compatibility
- Requires valid HTML input (uses lxml's error recovery)
- XPath/CSS selector must be valid syntax
- `-be` flag order requirement (not `-eb`)
- Text mode (`-t`) excludes `<script>` and `<style>` tags automatically

## External Dependencies

### PyPI Packages

- lxml: HTML/XML parsing engine (C-based, high performance)
- cssselect: CSS3 selector to XPath converter
- requests: HTTP library for fetching URLs

### Installation Methods

- pip (traditional)
- pipx (recommended for CLI tools)
- uv (modern package manager)
- Source installation with pip install -e .

### Distribution

- Published to PyPI as `scrape-cli`
- Version badge on README
- Semantic versioning (currently 1.2.0)
