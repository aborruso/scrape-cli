# LOG

## 2026-11-06

- v1.3.7 su PyPI, CI verde su Python 3.8-3.14; change `resolve-relative-urls` e `row-field-extraction` archiviate
- v1.3.7: rilascio con `--row`, `--field`, `--jsonl`, `--absolute-urls`, `--base-url`
- `--row` e `--field`: un oggetto JSON per elemento, con le stesse chiavi; `--jsonl`: un valore JSON per riga (change OpenSpec `row-field-extraction`)
- `./h2` ora è riconosciuto come XPath, prima dava un errore CSS
- Proposta OpenSpec `row-field-extraction`: campi associati con `--row` e `--field`, `--jsonl`
- `--absolute-urls` e `--base-url`: `href` e `src` assoluti in output, con `<base href>` (change OpenSpec `resolve-relative-urls`)
- Proposta OpenSpec `resolve-relative-urls`; nuove idee in `docs/future-ideas.md`
- `--json-array`: documentati espressioni miste, `count()` come stringa ed esempi con `jq`; URL relativi in `docs/future-ideas.md`
- Gli errori con `--json-array` nominano `--json-array`, non `--json` o `-j`
- v1.3.6 su PyPI, CI verde su Python 3.8-3.14; change `json-array-output` archiviata
- v1.3.6: rilascio con `--json-array` e le correzioni qui sotto
- HTML senza elementi (soli spazi o commenti): errore di una riga con codice 1, prima traceback
- `--json-array`: lista piatta, un elemento per risultato, nell'ordine delle espressioni; `-j` invariato salvo la correzione qui sotto (change OpenSpec `json-array-output`)
- Il testo che segue un elemento selezionato non finisce più nell'output con `-e`, `-b` e `-j`
- Con `-r` su XML non valido il messaggio ora dice `Error parsing XML:`
- v1.3.5: rilascio con la correzione Windows-1252
- HTML non UTF-8 senza meta tag: prima Windows-1252, poi ISO-8859-1 (issue #29)
- Migrazione OpenSpec al flusso `opsx`; contesto da `openspec/project.md` a `openspec/config.yaml`
- Extra `dev` con pytest in `pyproject.toml`
- v1.3.4: `scrape-cli` come secondo nome del comando `scrape`
- Ripiego su ISO-8859-1 ora attivo per HTML non UTF-8 senza meta tag; era codice che non scattava mai
- `--help` riscritto per gli agenti: output per modalità, codici di uscita, casi limite, esempi commentati (change OpenSpec `agent-friendly-help`)
- Errore di una riga su XPath non valido e input non leggibile, prima traceback
- CI: `actions/checkout` e `actions/setup-python` a v7
- CI GitHub Actions: pytest su Python 3.8-3.14
- `-j` documentato in `manual.html` e `index.html`; requisito Python corretto a `>=3.8` nei documenti
- v1.3.2: fix XPath con risultato singolo
- XPath con risultato singolo: `string()` non si spezza più per carattere, `count()` e `boolean()` non vanno più in traceback; `-x` segue il valore della funzione
- `releasing.md`: file aggiunti per nome invece di `git add -A`, pytest nello script, tag con `v`
- Spec di `-j` in `openspec/specs/json-output/`
- v1.3.1: `-j` su sole stringhe (`@attr`, `text()`) dà un array se i risultati sono più di uno, invece di una stringa unita da `\n`
- `-j`: niente più traceback con `&`/`<` nelle stringhe; attributi non XML (`@click`, `:bind`) danno errore di una riga
- Guardie `-eb`/`-ej` sul token esatto: non bloccano più file e selettori che contengono quelle lettere

## 2026-04-30

- v1.3.0: native `-j`/`--json` output (built-in `xmltodict`, no external `xq` needed, no `-b` required)
- `-j` mutually exclusive with `-t`, `-x`, `-a`; explicit `-ej` order check (use `-je`)

## 2026-04-16

- Uniformato stile errori: `-eb` detection ora usa `print(stderr)+sys.exit(1)` invece di `sys.exit(string)`
- `--check-existence` ora è il flag primario (kebab-case); rimosso alias duplicato `--check_existence`

## 2026-04-06

- Agent-friendly CLI: all errors now go to stderr; concise error on missing `-e`; `--help` extended with examples for all major use cases

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
