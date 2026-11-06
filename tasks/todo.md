# Rilascio 1.3.7

Pubblicata il 2026-11-06, change archiviate in `openspec/changes/archive/`.

- [x] Errori con `--json-array` che nominano il flag → commit c692307
- [x] Documentazione di `--json-array`: espressioni miste, `count()`, esempi `jq` → esempi eseguiti su una pagina di prova
- [x] URL assoluti: change `resolve-relative-urls` implementata → 77 test, output senza flag uguale alla 1.3.6, prova reale su IANA
- [x] Campi associati e JSON Lines: change `row-field-extraction` implementata → 101 test, output senza flag uguale alla 1.3.6, prove reali su Hacker News e python.org, esempi `jq` e DuckDB eseguiti
- [x] `CHANGELOG.md` e versione 1.3.7

Idee da valutare in `docs/future-ideas.md`: richieste HTTP (14), idee minori (15). Avviso per i campi sempre `null`: si aspetta di vedere se serve nell'uso.

Scelte confermate per `row-field-extraction`: primo risultato per campo, `--jsonl` nella stessa change, nomi `--row`, `--field`, `--jsonl`.

# Testo dopo l'elemento (2026-11-06)

- [x] `-e`, `-b` e `-j` non includono più il testo dopo l'elemento selezionato → riprodotto su 1.3.5 installata, test falliti prima del fix, verdi dopo

# Opzione --json-array (2026-11-06)

Rilasciato in 1.3.6 il 2026-11-06. Change archiviata in `openspec/changes/archive/`.

Scelte confermate il 2026-11-06: lista piatta, tag come chiave, nome `--json-array`. Change in `openspec/changes/json-array-output/`.

Output previsto: lista piatta in cima al JSON, senza `html`/`body`, un elemento per risultato, nell'ordine delle espressioni. Le stringhe restano stringhe, gli elementi diventano oggetti con il tag come chiave.

```
scrape --json-array -e '//a/@href' -e b page.html
["x", "y", {"b": "tre"}]
```

Fase 1, spec
- [x] Change OpenSpec con `/opsx:propose`, delta su `json-output` → `openspec validate --strict` passato

Fase 2, codice e test
- [x] Test prima del codice: zero, uno e più risultati danno `[]`, `[r]`, `[r1, r2]`; elementi e stringhe mescolati in ordine; testo dopo un elemento non incluso → verify: i test nuovi falliscono
- [x] `--json-array` implica `-j` e ha gli stessi vincoli con `-t`, `-x`, `-a` → verify: test verdi
- [x] Forma di `-j` invariata → test esistenti di `-j` verdi senza modifiche

Fase 3, documenti
- [x] `--help`, `README.md`, `manual.html`, `LOG.md` → test sull'help verde
- [x] `CHANGELOG.md` e versione 1.3.6

# Messaggio di errore con -r (2026-11-06)

- [x] `Error parsing XML:` con `-r` → test nuovo fallito prima del fix, suite verde dopo
- [x] Input HTML di soli spazi o commenti: errore di una riga con codice 1 → test fallito prima del fix, verde dopo

# Issue 29, Windows-1252 senza meta tag (2026-11-06)

- [x] Prima Windows-1252, poi ISO-8859-1 → test nuovi falliti prima del fix, verdi dopo

# Migrazione OpenSpec (2026-11-06)

- [x] Commit della migrazione al flusso `opsx`; tenute tutte le cartelle, perché claude, codex, opencode e copilot sono installati
- [x] Contesto in `openspec/config.yaml`, tolto `openspec/project.md`
- [x] Extra `dev` in `pyproject.toml`

# Ripiego ISO-8859-1 (2026-11-06)

- [x] Input HTML non UTF-8 senza meta tag convertito da ISO-8859-1 → 39/39 test; XML con `-r` e UTF-8 invariati; output uguale alla 1.3.3 in 5 casi.
- Limite noto: senza meta tag i byte windows-1252 come `€` (0x80) restano caratteri di controllo.

Rilascio 1.3.4 e alias `scrape-cli` confermati il 2026-11-06.

# Help per gli agenti (2026-11-06)

Rilasciato in 1.3.3 il 2026-11-06. Change archiviata in `openspec/changes/archive/`.

# CI e documentazione (2026-11-06)

- [x] Workflow pytest in `.github/workflows/tests.yml` → test locali verdi su Python 3.8-3.14, commit e push il 2026-11-06
- [x] `-j` in `manual.html` e `index.html`, requisito Python `>=3.8` nei documenti

# Rilievi residui della review (2026-11-06)

- [x] XPath con risultato singolo (`string()`, `count()`, `boolean()`) → 3 test falliti prima, 32/32 passati dopo
- [x] Duplicazioni: wrapper HTML e guardie `-eb`/`-ej` → output uguale alla 1.3.1 installata in 6 casi; i tre `if` di conflitto restano, i messaggi sono diversi
- [x] `releasing.md`: niente `git add -A`, pytest nello script, tag con `v` → controllato con `grep`; la riscrittura resta nel commit v1.3.0, già pubblico
- [x] Spec di `-j` in `openspec/specs/json-output/` al posto di una proposta retroattiva → `openspec validate --strict` ok

## Esito

- Rilascio 1.3.2 e rimozione del tag `1.3.0` (era `021d443`, stesso commit di `v1.3.0`) confermati il 2026-11-06.

# Fix dalla review di v1.3.0 (2026-11-06)

## Fase 1 - test che riproducono i difetti

- [x] Test per risultati stringa con `&`, errore pulito su attributi non XML, guardie `-eb`/`-ej` → verify: falliscono prima del fix

## Fase 2 - fix in `scrape_cli/scrape.py`

- [x] Escape dei risultati stringa in modalità `-j` → verify: `-je '//p/text()' resources/test.html` rc=0
- [x] `ExpatError` gestito con errore di una riga → verify: niente traceback con `@click`
- [x] Guardie `-eb`/`-ej` sul token esatto, non sulla sottostringa → verify: `-e a file-ej.html` rc=0, `-ej` e `-eb` ancora bloccati

## Fase 3 - documentazione

- [x] `xmltodict` nelle liste delle dipendenze, limite degli attributi nel README, voce in LOG → verify: `grep xmltodict`, `pytest tests/`

## Review

- 4 test falliti prima del fix, 27/27 passati dopo (2026-11-06, `.venv/bin/python -m pytest tests/`). Modifiche non committate.
- Limite noto: le guardie ora controllano solo i token esatti `-eb` e `-ej`; forme come `-xeb` non vengono più intercettate.
- `-e 'string(//h1)'` spezza il testo carattere per carattere anche senza `-j`: difetto preesistente, non toccato.

## Decisioni (2026-11-06, delegate a chi implementa)

- `-j` su `@attr`/`text()`: array se i risultati sono più di uno; con elementi e stringhe insieme le stringhe restano unite in `#text`.
- Attributi `@click`, `:bind`: resta l'errore di una riga.
- `-j` con stdout non UTF-8: invariato.
- Versione 1.3.1 e CHANGELOG aggiornati, commit sul branch `fix-json-1.3.1`.

## Esito rilascio

- Merge su `master`, tag `v1.3.1`, push e PyPI fatti il 2026-11-06: https://pypi.org/project/scrape-cli/1.3.1/
- GitHub release creata il 2026-11-06: https://github.com/aborruso/scrape-cli/releases/tag/v1.3.1

# Agent-friendly CLI improvements

## Analisi dei principi applicabili

La CLI è già non-interattiva e stateless. I miglioramenti utili per gli agenti sono:

| Principio | Stato attuale | Azione |
|-----------|---------------|--------|
| Non-interattiva | ✅ OK | — |
| `--help` con esempi | ✅ OK (v1.2.3) | — |
| Errori su stderr | ✅ OK (v1.2.3) | — |
| Messaggio errore conciso su espressione mancante | ✅ OK (v1.2.3) | — |
| Stdin e pipeline | ✅ OK | — |
| Fail fast con errori azionabili | ✅ OK (v1.2.3) | — |
| Idempotente | ✅ OK (read-only) | — |

## Gap residui dopo v1.2.3

- [x] **1. `-eb` detection** — `sys.exit("Error string")` su riga 119 è inconsistente: usa `print(..., file=sys.stderr); sys.exit(1)` come il resto del codice
- [x] **2. `--check_existence` vs `--check-existence`** — l'help mostra `--check_existence` (underscore), non standard Unix. Unificato in `--check-existence` (kebab-case) come arg primario; rimosso il doppio alias
- [x] **3. Aggiornare LOG.md**

## Review (v1.2.3 completato)

- `scrape.py`: epilog con `RawDescriptionHelpFormatter` + 8 esempi; tutti gli errori su stderr; errore espressione mancante conciso con esempio
- `tests/test_scrape.py`: 3 test aggiornati da `result.stdout` a `result.stderr`
- 18/18 test passati

## Domande aperte

- Vuoi mantenere il vecchio comportamento di stampare l'help completo quando manca `-e`? (i.e., solo per umani)
- Preferisci che i messaggi di errore includano anche un esempio d'uso corretto (es. `scrape -e "//h1" file.html`)?
