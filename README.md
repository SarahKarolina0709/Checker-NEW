# Qualitäts-Framework

Professionelle Qualitätskontrolle für Übersetzungen.

## Starten

```bash
pip install -r requirements.txt
python nicegui_app/main.py
```

Die App öffnet sich im Browser unter `http://localhost:8111`.

## Features

- **Upload**: PDF, DOCX, TXT, Bilder (OCR)
- **Auto-Pairing**: Quell- und Zieldateien automatisch zuordnen
- **4 Prüfphasen**: Zahlen/Formate, Inhalt/Konsistenz, Grammatik/Stil, KI (Ollama)
- **Glossar**: CSV/XLSX/JSON laden oder manuell eingeben
- **25 Sprachen**: Automatische Erkennung oder manuell wählen
- **Export**: TXT, PDF, Excel, Korrekturpaket (ZIP)
- **Kundenmanagement**: Projekte pro Kunde organisieren
- **Kalender**: Projekte nach Datum anzeigen
- **Session**: Letzte Analyse automatisch speichern/wiederherstellen
- **Netzwerk**: Kollegen können die App im Browser öffnen

## Projektstruktur

```
nicegui_app/                      # Hauptanwendung (NiceGUI)
├── main.py                       # UI + Routing (~3.200 Zeilen)
├── severity.py                   # Severity-Konstanten + Score-Berechnung
├── customers.py                  # Kunden- & Projekt-Verzeichnis-Logik
├── session.py                    # Session-Persistierung (atomar)
├── exports.py                    # TXT/Excel/PDF/ZIP-Exporte
└── text_extraction.py            # DOCX/PDF/OCR-Text-Extraktion

quality_gui_phase1_checkers.py    # Phase 1: Zahlen, URLs, Klammern
quality_gui_phase2_checkers.py    # Phase 2: Firmennamen, Glossar, Terminologie
quality_gui_phase3_checkers.py    # Phase 3: Grammatik, Lesbarkeit, Stil
quality_gui_phase4_ki_checker.py  # Phase 4: KI-Prüfung (Ollama)
quality_gui_grammar.py            # Grammatik-Backend (LanguageTool)
quality_gui_consistency_checker.py # Konsistenz-Prüfung
quality_gui_ocr_checker.py        # OCR-spezifische Prüfungen
quality_gui_pairing_manager.py    # Pairing-Manager (UI-nah)
neutral_pairing_service.py        # Smart File Pairing (UI-frei)
neutral_upload_service.py         # Upload-Service
ki_module.py                      # Ollama KI-Integration
quality_gui_ollama_suggestions.py # KI-Korrekturvorschläge
```

## Tests

```bash
python -m pytest tests/ -q
```

230+ Tests decken alle Backend-Module ab (Phase-Checker, Severity, Customers,
Session, Exports, Pairing, Glossary, Text-Extraction).

## Netzwerk-Nutzung

Die App ist unter `http://<IP>:8111` für alle Rechner im Netzwerk erreichbar.
Jeder Kollege öffnet die URL im Browser — keine Installation nötig.
