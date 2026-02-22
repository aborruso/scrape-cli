# LOG

## 2026-02-22

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
