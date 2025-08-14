# GitHub Copilot Instructions for scrape-cli

## Project Overview

scrape-cli is a command-line tool for extracting HTML elements using XPath queries or CSS3 selectors. It's designed to be simple, efficient, and useful for web scraping tasks, data extraction, and HTML processing workflows.

**Key Features:**
- Extract HTML elements using XPath or CSS selectors
- Support for multiple input sources (files, URLs, stdin)
- Text-only extraction mode for LLM-friendly output
- Element existence checking with exit codes
- Raw HTML output with body wrapping option
- Automatic charset detection and encoding handling

## Architecture & Code Structure

### Project Layout
```
scrape-cli/
├── scrape_cli/           # Main package directory
│   ├── __init__.py       # Package metadata and version
│   └── scrape.py         # Core implementation
├── setup.py              # Package configuration
├── README.md             # User documentation
├── CHANGELOG.md          # Version history
├── resources/            # Test files and examples
└── release_update.md     # Release process guide
```

### Core Dependencies
- **lxml**: HTML/XML parsing and XPath evaluation
- **cssselect**: CSS selector to XPath conversion
- **requests**: HTTP client for URL fetching

## Coding Patterns & Conventions

### Command-Line Interface
- Uses `argparse` for CLI argument parsing
- Follows Unix conventions (stdin/stdout, exit codes)
- Supports both short (`-e`) and long (`--expression`) options
- Validates argument combinations and provides helpful error messages

### HTML Processing Pipeline
1. **Input handling**: Detect source type (file, URL, stdin)
2. **Charset detection**: Parse HTML meta tags for encoding
3. **Selector conversion**: Convert CSS selectors to XPath if needed
4. **Element extraction**: Use lxml for XPath evaluation
5. **Output formatting**: Clean text and format results

### Key Functions

#### `is_xpath(expression)`
Detects if a selector is XPath by looking for patterns:
- Starts with `/` or `//`
- Contains axis specifiers (`::`), predicates (`[]`), functions, or attributes (`@`)

#### `convert_css_to_xpath(expression)`
Converts CSS selectors to XPath using cssselect.GenericTranslator with error handling.

#### `clean_text(text)`
Normalizes text output by:
- Removing multiple consecutive spaces
- Limiting consecutive empty lines to maximum of 1
- Stripping whitespace from line beginnings/ends

#### `detect_charset(html_bytes)`
Attempts to detect charset from HTML meta tags in first 1024 bytes.

### Error Handling Patterns
- Catch and provide user-friendly error messages for common failures
- Use appropriate exit codes (0 for success, 1 for errors, special codes for existence checks)
- Validate input early and fail fast with helpful messages
- Handle network errors, file not found, and parsing errors gracefully
- Specific validation: Check for invalid argument combinations like `-eb` (should be `-be`)
- Always call `sys.exit(1)` for error conditions, not just `return`

### Input/Output Patterns
- **Multiple input sources**: URLs (http/https), file paths, or stdin
- **Flexible output**: Raw HTML, text-only, or wrapped in HTML/body tags
- **Encoding handling**: UTF-8 default with fallback to detected charset or ISO-8859-1
- **Streaming**: Read from stdin buffer, write to stdout with flush
- **Version reading**: Dynamically read version from `__init__.py` using regex
- **Buffer handling**: Use `sys.stdin.buffer.read()` for binary input, `sys.stdout.write()` for output

## Common Development Tasks

### Adding New CLI Options
1. Add argument to parser in `main()` function
2. Handle the option in the processing logic
3. Update help text and examples
4. Test with various input combinations
5. Consider interactions with existing options (e.g., `-eb` validation)

### Extending Selector Support
- Modify `is_xpath()` to recognize new XPath patterns
- Ensure `convert_css_to_xpath()` handles edge cases
- Test with complex selectors and nested elements
- Remember that CSS selectors are converted to XPath internally

### Improving Text Processing
- Modify `clean_text()` for new text normalization needs
- Consider impact on existing output formats  
- Test with various HTML structures and content types
- When using `-t` flag, default XPath is `//body//text()[not(ancestor::script) and not(ancestor::style)]`

## Testing Approach
- Use `resources/test.html` for manual testing
- Test CLI options and combinations
- Verify output formats and error handling
- Check encoding detection with various HTML files

### Manual Testing Examples
```bash
# Test basic CSS selector
scrape -e "table.data-table td" resources/test.html

# Test XPath expression  
scrape -e "//table[contains(@class, 'data-table')]//td" resources/test.html

# Test URL input
scrape -e "title" https://example.com

# Test text extraction
scrape -t -e "//body" resources/test.html

# Test existence checking
scrape -e "//div[@id='nonexistent']" -x resources/test.html; echo $?
```

## Release Process
- Update version in both `setup.py` and `scrape_cli/__init__.py`
- Update `CHANGELOG.md` with new features/fixes
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Use release guides in `release_update.md` and `releasing.md`

## Code Style Guidelines
- Follow PEP 8 Python style guide
- Use descriptive variable names and function names
- Include docstrings for non-trivial functions
- Handle errors gracefully with informative messages
- Prefer explicit imports over wildcards
- Keep functions focused and single-purpose
- **Import conventions**: Standard library first, then third-party, then local imports
- **Version handling**: Read version dynamically from `__init__.py` using regex pattern matching
- **Late imports**: `from sys import exit` is done after version reading to avoid conflicts

## Common Pitfalls to Avoid
- Don't assume input encoding - always detect or handle multiple encodings
- Validate XPath/CSS expressions before processing
- Handle empty or malformed HTML gracefully
- Be careful with regex patterns in `is_xpath()` - test edge cases
- Consider memory usage for large HTML documents
- Maintain backward compatibility in CLI interface changes

## Integration Patterns
This tool is designed to work well in Unix pipelines:
```bash
curl -s https://example.com | scrape -e "//title" | head -1
cat *.html | scrape -e ".error-message" | sort | uniq
```

When extending functionality, maintain this pipeline-friendly design.