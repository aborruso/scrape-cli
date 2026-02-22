# LOG

## 2026-02-23

- Add `-u`/`--user-agent` option; set default UA to avoid 403 on sites like Wikipedia

## 2026-02-22

- Remove `setup.py` (superseded by `pyproject.toml`)
- Add `timeout=30` to `requests.get()` in `scrape.py`
- Bump `requires-python` to `>=3.8` in `pyproject.toml`
- Enrich `resources/test.html`: countries table, 6 sections, data attributes, ordered list
- Create `manual.html`: 10 real examples (CSS + XPath + pipeline), all outputs verified

- Created `index.html`: modern standalone landing page (HTML + Tailwind CDN + vanilla JS)
  - Hero with terminal typing animation
  - Why scrape-cli — 4 benefit cards
  - How it works — CSS/XPath tab switcher with 3 real examples
  - Installation — pipx/uv/pip tabs with copy button
  - Practical examples — 4 use-case cards (JSON, LLM text, check-existence, pipeline)
  - Footer with GitHub / MIT / PyPI links
- Fixes #5: added OpenGraph + Twitter Card meta tags to `index.html`; generated `og-image.png` (1200×630)
- Basic accessibility: skip-to-content link, `<main>` landmark, `aria-label` on nav, ARIA tab pattern (`role="tablist/tab"`, `aria-selected`), `focus-visible` ring, `aria-live` on copy button
- Added `nanobanana-output/` to `.gitignore`
- Opened issue #27: tracks the single-page redesign work
