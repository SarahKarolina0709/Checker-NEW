# Anleitung für Python-Entwicklung

## Framework
- **NiceGUI** für die Web-Oberfläche (nicht CustomTkinter)
- Python 3.12+
- Styling über Tailwind CSS Klassen

## Code-Standards
- Type Hints verwenden
- `encoding='utf-8'` bei allen Datei-Operationen
- `try/except` für optionale Dependencies (pytesseract, reportlab, etc.)
- Logging über `logging` Modul, nicht `print()`

## UI-Entwicklung (NiceGUI)
- Icons erlaubt: `ui.icon('check_circle')` (Material Icons)
- Farben über Tailwind: `.classes('text-blue-700 bg-gray-50')`
- Responsive: `flex-grow`, `w-full`, `gap-4`
- Notifications: `ui.notify('Nachricht', type='positive')`
- Dialoge: `ui.dialog()` mit `.open()`

## Backend-Module
- Checker-Logik in eigenen Modulen (`quality_gui_phase*.py`)
- Keine UI-Elemente in Backend-Modulen
- Rückgabe als `QAIssue` Dataclass oder Dict

## Tests
- Tests in `tests/` Ordner
- `pytest` als Test-Framework
- Checker-Tests testen Logik isoliert (ohne UI)
