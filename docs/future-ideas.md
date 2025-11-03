# Future Ideas for scrape-cli

## Current Strengths

- **Solid and stable**: single-file CLI, well tested
- **Dual query language**: XPath and CSS with intelligent auto-detection
- **Text extraction**: excellent for LLMs (`-t` flag)
- **Encoding handling**: charset detection + fallback
- **Input flexibility**: stdin, file, URL

## Ideas for Future Releases

### 1. Structured data extraction (v1.3.0)

**Current solution**: HTML to structured JSON already works with `xq`:

```bash
# This already works today
scrape -be "table.data-table td" file.html | xq .
# Output: {"html": {"body": {"td": ["1", "John Doe", "john@example.com", ...]}}}

scrape -be "a.external-link" file.html | xq .
# Output: {"html": {"body": {"a": {"@href": "...", "@class": "...", "#text": "..."}}}}
```

`xq` already provides:
- HTML → structured JSON conversion
- Attributes as `@attr`
- Text content as `#text`
- Arrays for multiple elements

**What could still be useful** (lower priority now):

```bash
# Table rows → CSV with headers auto-detection
scrape -e "table" --format csv --auto-headers file.html

# Multiple queries in one pass (performance)
scrape --extract '{title: "//h1", links: "//a/@href"}' file.html

# JSONL for streaming/big data
scrape -e "//article" --format jsonl feed.html
```

**Benefits**:
- CSV output for direct import in spreadsheets/databases
- Multi-query avoids re-parsing same HTML
- JSONL for streaming large datasets

### 2. Multi-query batch mode (v1.3.0)

```bash
# File with multiple queries
scrape --queries queries.txt file.html

# queries.txt:
# title=//title/text()
# links=//a/@href
# images=//img/@src
```

**Benefits**: single parsing for N extractions

### 3. Streaming/chunked processing (v1.4.0)

```bash
# Large HTML, limited memory
scrape -e "//article" --stream large.html
```

**Use case**: huge files, enormous RSS feeds

### 4. Built-in selectors library (v1.4.0)

```bash
# Preset common patterns
scrape --preset og-tags file.html  # OpenGraph
scrape --preset schema-org file.html  # Schema.org
scrape --preset tables file.html  # All tables as CSV
```

### 5. Template output (v1.5.0)

```bash
# Jinja2-style templates
scrape --template "{{title}}: {{//meta[@name='description']/@content}}" file.html
```

### 6. Validation/filtering (v1.5.0)

```bash
# Integrated post-processing
scrape -e "//a/@href" --filter "https://*" --unique file.html
scrape -e "//td" --regex "\d{4}-\d{2}-\d{2}" file.html
```

### 7. JavaScript rendering (v2.0.0 - breaking)

```bash
# With playwright/selenium headless
scrape -e "article" --render-js spa-site.html
```

**Trade-off**: heavy dependencies, optional

### 8. Plugin system (v2.0.0)

```python
# Custom extractors
scrape -e "table" --plugin extract_pandas file.html
```

### 9. Quick wins (v1.2.1)

- **Colorized output** for TTY (optional)
- **Progress indicator** for URL fetch
- **Retry logic** with backoff for URLs
- **User-agent customization**: `--user-agent "..."`
- **Headers support**: `--header "Authorization: Bearer ..."`
- **Cookies support**: `--cookie-file cookies.txt`

### 10. Developer experience (v1.3.0)

- **Verbose mode**: `-v` shows compiled XPath, timing, stats
- **Dry-run mode**: `--dry-run` validates query without executing
- **Examples generator**: `scrape --examples URL` suggests queries

## Suggested Priorities

### v1.2.1 (quick wins)

- User-agent, headers, cookies
- Retry logic
- Progress indicator

### v1.3.0 (medium effort, high value)

- Structured data extraction (tables, lists, key-value)
- Multi-query batch
- Verbose mode

### v1.4.0 (advanced)

- Streaming
- Built-in presets
- Validation/filtering

### v2.0.0 (major)

- JS rendering
- Plugin system

## Compatibility with Existing Workflow

Everything backward-compatible. Users continue to use:

```bash
curl URL | scrape -e "query"
```

New features are opt-in via flags.
