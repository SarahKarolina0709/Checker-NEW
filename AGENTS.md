# AGENTS.md — Hinweise für KI-Coding-Agents

Dieses Dokument richtet sich an automatisierte Coding-Agents (Copilot CLI,
Claude Code, etc.). Es ergänzt `.github/instructions/Checker Instructure.instructions.md`.

## Architektur kurz

NiceGUI Web-App, Python 3.12. Start: `python nicegui_app/main.py`.

```
nicegui_app/
├── main.py            UI + Routing (~3.200 Z., enthält NiceGUI-spezifischen Code)
├── severity.py        Severity-Konstanten + Score-Berechnung (rein, testbar)
├── customers.py       Kunden-/Projekt-Verzeichnis-Logik (rein, testbar)
├── session.py         Session-Persistierung (rein, testbar)
├── exports.py         TXT/Excel/PDF/ZIP (rein, testbar)
└── text_extraction.py DOCX/PDF/OCR (rein, testbar)
```

Backend-Module im Repo-Root: `quality_gui_phase{1,2,3,4}_*.py`,
`neutral_pairing_service.py`, `neutral_upload_service.py`, `ki_module.py`, etc.

## Wichtige Regeln

1. **UI-Texte auf Deutsch.** Tailwind-CSS-Klassen via `.classes('...')`.
2. **Backend-Logik gehört NICHT in `nicegui_app/main.py`.** Neue Hilfsfunktionen
   in `nicegui_app/<modul>.py` als pure functions, dann main.py nur als
   dünner Wrapper auf `settings`/`S()` zugreifen lassen.
3. **Datei-I/O immer mit `encoding='utf-8'`.**
4. **Optionale Dependencies graceful behandeln** (`try/except ImportError`).
5. **Keine neuen Dateien im Root erstellen** — Module gehen in `nicegui_app/`
   oder bleiben in den existierenden Backend-Modulen.
6. **`_legacy/` nicht anfassen** (alte CustomTkinter-App).

## Tests

```bash
python -m pytest tests/ -q
```

230+ Tests, sollten immer 100% grün sein nach Änderungen. Test-Dateien:
- `test_quality_gui_phase{1,2,3}_*.py` — Phase-Checker (62)
- `test_severity.py`, `test_text_extraction.py` (45)
- `test_customers.py`, `test_session.py`, `test_exports.py` (79)
- `test_neutral_pairing_service.py`, `test_glossary.py` (~50)

Bei neuen Hilfsfunktionen: Tests schreiben.

## Severity-Werte (kanonisch)

`'critical'` (8 Pkt) | `'major'` (3) | `'minor'` (1) | `'info'` (1)

Aliase werden in `severity.normalize()` aufgelöst (kritisch→critical,
wichtig→major, error→critical, warning→major, etc.). Findings mit
`meta['hint_only']=True` zählen NICHT zum Score.

## Verzeichnis-Strukturen (für customers.py-Funktionen)

Alle Funktionen in `customers.py` unterstützen 3 Layouts gleichzeitig:
- **A**: `<base>/<YYYY-MM-DD>_<Kunde>/...` (flat)
- **B**: `<base>/<Monatsname>_<YYYY>/<YYYY-MM-DD>_<Kunde>/...` (neu, Standard)
- **C**: `<base>/<Kunde>/<YYYY-MM-DD>/...` (alt)

Beim Erweitern dieser Logik: alle 3 Strukturen mittesten!

## Häufige Bug-Muster (vermieden in der Code-Basis)

- `getattr(x, 'attr', 'default').lower()` greift Default NICHT bei `attr=None`
  → stattdessen: `(getattr(x, 'attr', None) or 'default').lower()`
- `str.replace(suffix, '')` für „Suffix entfernen" frisst Wort-interne Vorkommen
  → stattdessen: `if s.endswith(suffix): s = s[:-len(suffix)]`
- Sprach-Codes als Token-Listen für Source/Target-Erkennung führen zu vertauschten
  Paaren (DE→EN: `de` als source, `en` als translation falsch zugeordnet) → in
  `neutral_upload_service.py` deshalb keine Sprach-Codes!
- Class/Modul-Caches mit unvollständigen Keys → False-Hits

## Konfiguration

- `config.json` — App-Konfig (geschützt)
- `checker_config.json` — User-Einstellungen (editierbar)
- `customers.json` — Kundendaten
- `requirements.txt` — alle Deps mit `>=X,<Y` Pins
