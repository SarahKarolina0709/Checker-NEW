---
applyTo: 'always run on all issues'
---

# CHECKER INSTRUCTURE — Verbindliche Regeln

## Architektur
- **NiceGUI Web-App** — Hauptanwendung in `nicegui_app/main.py`
- **Backend-Module** im Root: `quality_gui_phase*.py`, `ki_module.py`, etc.
- **Kein CustomTkinter** — alte App liegt in `_legacy/` (nicht anfassen)
- Start: `python nicegui_app/main.py` (Browser öffnet sich automatisch)

## Kommunikation
- Immer auf Deutsch antworten (Du-Form). Technische Fachbegriffe dürfen Englisch bleiben.
- Antworten kurz, sachlich, professionell. Keine Füllwörter.

## UI-Regeln
- **Icons erlaubt** — NiceGUI Material Icons verwenden (`ui.icon('name')`)
- Alle UI-Texte auf Deutsch
- Styling über Tailwind CSS Klassen (`.classes('...')`)
- Farbschema: Blau-800 Header, weiße Cards, grauer Hintergrund
- Responsive Design (funktioniert bei 1200px und 1920px Breite)

## Code-Regeln
- Alle Datei-Operationen mit `encoding='utf-8'`
- Fehlende Dependencies graceful behandeln (`try/except ImportError`)
- Keine neuen Dateien im Root erstellen — nur bestehende Module ändern
- Backend-Logik (Checker, Pairing, OCR) NICHT in `nicegui_app/main.py` — gehört in eigene Module

## Konfiguration
- `config.json` — App-Konfiguration (geschützt)
- `checker_config.json` — Benutzer-Einstellungen (editierbar)
- `customers.json` — Kundendaten

## Tests
- `python -m pytest tests/ -q` — 62 Checker-Tests
- Neue Features brauchen Tests in `tests/`

## Verzeichnisse
- `nicegui_app/` — Hauptanwendung
- `Checker_Projekte/` — Kundenprojekte
- `glossaries/` — Glossar-Dateien
- `reports/` — Analyse-Berichte
- `_legacy/` — Alte CustomTkinter-App (archiviert, nicht ändern)
