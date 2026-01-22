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
- Präfix-Konvention: Alle neuen/aktiven GUI‑nahen Tools & Diagnostik beginnen mit `quality_gui_` (alte Dateinamen nur als Wrapper).

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
- Dateinamen: Einheitliches Präfix `quality_gui_` für Grammar, Diagnose & umfassende Analysen

## Präfix-Migration (Stand 25.08.2025)

| Alt (deprecated) | Neuer Modulname | Status | Entfernen nach |
|------------------|-----------------|--------|----------------|
| `grammar_quality.py` | `quality_gui_grammar.py` | Wrapper mit DeprecationWarning | Cleanup-Fenster |
| `diagnose_quality_gui.py` | `quality_gui_diagnose.py` | Wrapper | Cleanup-Fenster |
| `diagnose_quality_gui_startup.py` | `quality_gui_diagnose_startup.py` | Wrapper | Cleanup-Fenster |
| `comprehensive_diagnosis.py` | `quality_gui_comprehensive_diagnosis.py` | Alias/Export | Cleanup-Fenster |
| `comprehensive_error_detector.py` | `quality_gui_comprehensive_error_detector.py` | Wrapper | Cleanup-Fenster |
| `comprehensive_duplicate_analysis.py` | `quality_gui_comprehensive_duplicate_analysis.py` | Wrapper | Cleanup-Fenster |

Hinweis: Nach Ende der Übergangsphase werden die Altmodule entfernt. Neue Imports sofort auf die `quality_gui_` Varianten umstellen.

### Geplanter Entferner-Workflow

1. Phase Warnung (jetzt aktiv): DeprecationWarnings beim Import.
2. Phase Audit: Sicherstellen, dass keine internen Imports mehr auf Altdateien zeigen.
3. Entfernung: Löschen der Wrapper + Update dieser Tabelle.
4. Abschluss: Release-Note mit Breaking Change Hinweis.

## Erweiterung (Best Practices)

- Neue UI‑Sektionen als Orchestrator + kleine Helper aufteilen
- Corner‑Radii ausschließlich über `_cr(...)`; Farben/Fonts/Spacings aus dem Design‑System
- Batch‑Operationen im Kalender/Tages‑Dialog über Quick‑Actions anbinden

## Troubleshooting (bekannt behoben)

- Kalender Fehler „can't multiply sequence by non‑int of type 'float'“ → radii via `_cr(...)` auf int.
- „Weiße Felder“ im Tages‑Dialog → Quick‑Action‑Buttons als Outline‑Chips mit `surface_border`.

## Analyse-Pipeline – Konsistenz & Metriken (Erweiterungen 25.08.2025)

Implementiert in `quality_gui_main_app.py`:

- Numerische Konsistenz: sprachsensitive Normalisierung (Tausender/Dezimal) → `numeric_consistency`.
- Einheiten-Konsistenz: Zahlen+Einheiten-Extraktion (konfigurierbare Patterns) → `unit_consistency`.
- Einheiten-Plausibilität: Warnungen bei gleichem Zahlenwert aber anderer Größenordnung (z.B. `5 km` vs `5 m`) → `unit_plausibility_warnings`.
- Namens-Konsistenz: Kanonisierung (Umlaute, Transliteration-Extras, Monats-/Wochentag-ID) + dynamisches Fuzzy Matching (kurz ≤1, lang ≤2) → `name_consistency`.
- Währungs-Konsistenz: Mapping verschiedener Symbole/Kürzel auf ISO-Code → `currency_consistency`.
- Konsolidierter Report: `summary.consistency_report` liefert Samples (missing/extra) + Plausibilitätswarnungen.

### Paar-Felder (Export)

`numbers_missing`, `numbers_extra`, `names_missing`, `names_extra`, `names_fuzzy_mapped`, `units_missing`, `units_extra`, `unit_plausibility_warnings`, `currencies_missing`, `currencies_extra`.

### Aggregat-Metriken

`unit_consistency`, `currency_consistency`, `unit_consistency_score`, `currency_consistency_score`, `consistency_report`.

### Konfiguration (Auszug)

```jsonc
{
  "analysis": {
    "tgt_lang": "de",
    "numeric": { "normalize": true },
    "names": {
      "enabled": true,
      "affect_score": false,
      "fuzzy": { "short_max_distance": 1, "long_max_distance": 2, "long_length_threshold": 8 },
      "transliteration_extra": { "œ": "oe" },
      "whitelist": [],
      "blacklist": [],
      "product_map": { "produkt": ["product"] }
    },
    "units": {
      "enabled": true,
      "patterns": ["km","km/h","m","cm","mm","kg","g","%","EUR","€","USD","$","h","min","s"],
      "plausibility": {
        "enabled": true,
        "magnitude_map": { "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000, "g": 1, "kg": 1000 }
      }
    },
    "currency": {
      "enabled": true,
      "map": {
        "EUR": ["€","eur","euro"],
        "USD": ["$","usd"],
        "GBP": ["£","gbp"],
        "CHF": ["chf","sfr","fr"]
      }
    }
  }
}
```

Hinweis: Währungs-Score fließt aktuell nicht in `overall_score` ein (Monitoring). Namen nur wenn `affect_score=true`.
