# 2026-02-22

- [1.2.1] Added automated pytest coverage for XPath/CSS detection and CLI options, including URL/file/stdin input paths and error handling.
- Hardened runtime behavior by adding `timeout=30` to URL fetches and replacing a bare `except:` with `except Exception` in charset detection.
- Raised `requires-python` to `>=3.8`, removed legacy `setup.py`, and expanded `.gitignore` for local test/venv artifacts.

# 2025-09-07

- [1.2.0] Fixed XPath detection for expressions wrapped in parentheses: XPath expressions like `(//div[@class='coordinate lat'])[1]` are now correctly recognized as XPath instead of being incorrectly treated as CSS selectors.
- Enhanced the `is_xpath` function with additional pattern recognition for XPath-specific syntax including attribute predicates, position predicates, and XPath functions.

# 2025-08-14

- [1.1.9] Improved distinction between XPath and CSS selectors: CSS selectors like `a[href*="/talk/"]` are now handled correctly and no longer cause errors.
- Updated the `is_xpath` function to prevent false positives.

# 2025-06-02

- Added the option `-t` to extract only text content from HTML

# 2025-05-04

- Improved XPath detection with support for complex expressions (predicates, functions, and axes)

# 2025-05-02

- Added charset detection from HTML meta tags
- Added support for ISO-8859-1 encoding fallback
- Improved HTML parsing with better encoding handling

# 2020-05-05

- First version of website
