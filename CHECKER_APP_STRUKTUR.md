# Checker App – Struktur & Einstieg

Stand: 12.08.2025

## Einstiegspunkt
- Empfohlener Start: `welcome_screen.py` (QA-/Produktiv‑Einstieg für Desktop‑App)
- Ziel: Schnellzugriff auf Kunden, Uploads, Kalender und Qualitätssichten ab einem zentralen Screen

## High‑Level Architektur
- GUI: CustomTkinter (Light Mode only, global erzwungen über `force_light_mode.py`/`aggressive_anti_dark_mode.py`).
- Design‑System: `design_system.py` – immer `get_color`/`get_typography`/`get_spacing` nutzen (keine Hex‑Farben im Code).
- No‑Icons‑Policy: Keine Icons/Emojis in UI‑Elementen.
- Layout: Root pack(); innerhalb Container konsequent grid(); keine pack/grid‑Mischung im selben Container.

## Hauptkomponenten
- Welcome Screen (`welcome_screen.py`)
  - Suche/Kundenliste inkl. Tastatursteuerung (ESC/Enter)
  - Upload‑UX (Mehrfachauswahl, Dateinamen‑Listing)
  - Toasts: einheitlicher Layout‑Manager (keine pack/place‑Mischung)
  - OS‑agnostisches Öffnen von Pfaden über zentrales `_open_path`

- Kalender (einfach/erweitert) in `welcome_screen.py`
  - Deutsche Lokalisierung: `_format_month_year_de`, `_weekday_headers_de`, `_format_date_de`
  - Grid: `_create_enhanced_calendar_grid(...)` (Wochentage Mo–So, Monats‑Navigation)
  - Tages‑Dialog: `_show_enhanced_day_details(...)` (Statistiken, Projekt‑Karten, Quick‑Actions)
  - UI‑Sicherheit: Corner‑Radii immer via `_cr('borders.radius_*')` → int (keine tuple/float‑Fehler)
  - Quick‑Actions als Outline‑Chips (weiß, Primär‑Text, `surface_border`)

- Datei‑/Projekt‑Management
  - Projektbasis aus `checker_config.json`/`config.json` (sichere Fallbacks)
  - Asynchrone Datei‑Operationen mit synchronem Fallback (`async_file_operations.py`)
  - Kunden-/Projektordner: `Kunde/YYYY‑MM‑DD`

- Konfiguration & Validierung
  - Zentrale Lese-/Fallback‑Logik; Validierung an Konfig‑Werte gebunden
  - Kundendaten: `customers.json`

- Analytics
  - Generischer Event‑Zähler; gebündeltes Schreiben (STATS_FILE)

- Safety/Enforcement
  - `widget_safety_patches.py` (z. B. sichere Typen für Höhen/Radii)
  - `force_light_mode.py`/`aggressive_anti_dark_mode.py` (Light Mode Only)

## Design‑System (Kurzreferenz)
- Farben: `get_color('primary'|'surface'|'surface_border'|'gray_700'|...)`
- Typografie: `get_typography('title'|'heading_sm'|'subheading'|'body'|'small'|'caption'|'micro')`
- Abstände: `get_spacing('sm'|'md'|'lg'|'xl')`

## Start & Tests
- Start (empfohlen): `welcome_screen.py`
- VS Code Task: „Run Welcome Screen Test“ (Smoke‑Test; Light‑Mode/Manager‑Fallback sichtbar)

## Qualitätsrichtlinien (Auszug)
- Light Mode erzwingen; keine Dark‑Mode Toggles
- Keine hartcodierten Hex‑Farben; nur Design‑System
- No‑Icons Policy: UI reiner Text
- Orchestrator‑Pattern: Container/Section‑Helper, Single Responsibility
- Keine pack/grid‑Mischung pro Container

## Erweiterung (Best Practices)
- Neue UI‑Sektionen als Orchestrator + kleine Helper aufteilen
- Corner‑Radii ausschließlich über `_cr(...)`; Farben/Fonts/Spacings aus dem Design‑System
- Batch‑Operationen im Kalender/Tages‑Dialog über Quick‑Actions anbinden

## Troubleshooting (bekannt behoben)
- Kalender Fehler „can't multiply sequence by non‑int of type 'float'“ → radii via `_cr(...)` auf int.
- „Weiße Felder“ im Tages‑Dialog → Quick‑Action‑Buttons als Outline‑Chips mit `surface_border`.
