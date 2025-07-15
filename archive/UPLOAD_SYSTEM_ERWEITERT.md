# Upload-System Erweitert - Dokumentation

## Übersicht

Das Upload-System der Checker-App wurde erweitert, um eine vollständige Integration zwischen Datei-Upload und Kundenmanagement zu bieten. Die wichtigsten Verbesserungen:

### ✅ Neue Features

1. **Automatische Dateiablage mit Datumsorganisation**
   - Dateien werden automatisch in `Kunde/Workflow/YYYY-MM-DD/` abgelegt
   - Beispiel: `Checker_Projekte/Mueller_GmbH/Ausgangstexte/2025-07-09/dokument.pdf`

2. **Fuzzy-Matching für Kunden**
   - Automatische Erkennung ähnlicher Kundennamen
   - Beispiel: "Mueller" findet "Mueller_GmbH" (70% Ähnlichkeit)
   - Benutzer kann Vorschläge annehmen oder ablehnen

3. **Intelligente Kundenvorschläge**
   - Automatische Erkennung von Kundennamen aus Dateinamen
   - Muster: `Kunde_Angebot.pdf`, `Angebot_Kunde.pdf`, `Kunde_2024.pdf`
   - Fuzzy-Matching mit bestehenden Kunden

4. **Verbesserte Benutzerführung**
   - Klare Trennung zwischen Dateiauswahl und Verarbeitung
   - Ergebnisanzeige mit Zielordnern
   - Direkte Ordner-Öffnung möglich

### 🔧 Neue UI-Komponenten

**Upload-Buttons:**
- `Dateien auswählen` - Dateiauswahl
- `Dateien verarbeiten` - Automatische Verarbeitung mit Fuzzy-Matching
- `Kunden-Vorschau` - Zeigt mögliche Kundenzuordnungen
- `Liste löschen` - Löscht Dateiliste
- `Ordner öffnen` - Öffnet Kundenordner im Explorer

**Neue Anzeigebereiche:**
- Upload-Dateiliste
- Verarbeitungs-Ergebnisse mit Zielordnern

### 🚀 Verbesserte Workflows

**Workflow-Integration:**
- Upload-Dateien können direkt in Workflow-Ordner verarbeitet werden
- Beim Starten von Workflows wird automatisch gefragt, ob Upload-Dateien verarbeitet werden sollen
- Nahtlose Integration zwischen Upload und Workflow-Ausführung

## Verwendung

### 1. Datei-Upload mit automatischer Kundenerkennung

```python
# Benutzer wählt Dateien aus
self.select_files()

# Automatische Verarbeitung
self.process_files()
```

**Ablauf:**
1. Benutzer wählt Dateien aus
2. System fragt nach Kunde (mit Fuzzy-Matching)
3. System fragt nach Workflow (Standard: Ausgangstexte)
4. Dateien werden in `Kunde/Workflow/Datum/` gespeichert
5. Ergebnisse werden angezeigt

### 2. Kundenvorschläge aus Dateinamen

```python
# Analyse der Dateinamen
self.preview_customer_suggestions()
```

**Erkannte Muster:**
- `Mueller_Angebot.pdf` → "Mueller"
- `Angebot_Schmidt.pdf` → "Schmidt"  
- `Kunde_2024.pdf` → "Kunde"
- `Firma_001.pdf` → "Firma"

### 3. Workflow-Integration

```python
# Workflow mit automatischer Dateiverarbeitung
self.start_angebots_workflow()
```

**Ablauf:**
1. Benutzer startet Workflow
2. System fragt, ob Upload-Dateien verarbeitet werden sollen
3. Dateien werden automatisch in entsprechenden Workflow-Ordner gespeichert
4. Workflow wird gestartet

## Technische Details

### Fuzzy-Matching

```python
def find_customer_fuzzy(self, search_name, threshold=70):
    """Sucht Kunden mit 70% Ähnlichkeit"""
    existing_customers = self.alle_kunden()
    result = process.extractOne(
        search_name, 
        existing_customers, 
        scorer=fuzz.ratio, 
        score_cutoff=threshold
    )
    return result[0] if result else None
```

### Dateiorganisation

```python
def save_file_to_customer(self, file_path, customer_name, workflow):
    """Speichert Datei mit Datumsorganisation"""
    heute = datetime.date.today().isoformat()
    workflow_ordner = self.customer_manager.get_ordner_fuer_workflow(customer_name, workflow)
    datums_ordner = os.path.join(workflow_ordner, heute)
    os.makedirs(datums_ordner, exist_ok=True)
    # Datei kopieren...
```

### Ordnerstruktur

```
Checker_Projekte/
├── Mueller_GmbH/
│   ├── Ausgangstexte/
│   │   ├── 2025-07-09/
│   │   │   ├── dokument1.pdf
│   │   │   └── dokument2.docx
│   │   └── 2025-07-08/
│   ├── Angebot/
│   │   └── 2025-07-09/
│   ├── Pruefung/
│   └── Finalisierung/
└── Schmidt_AG/
    ├── Ausgangstexte/
    ├── Angebot/
    ├── Pruefung/
    └── Finalisierung/
```

## Vorteile

### ✅ Benutzerfreundlichkeit
- Automatische Kundenerkennung reduziert Tipparbeit
- Intelligente Vorschläge basierend auf Dateinamen
- Klare Rückmeldung über Speicherorte

### ✅ Datenorganisation
- Konsistente Datumsorganisation
- Automatische Ordnerstruktur
- Vermeidung von Duplikaten durch Fuzzy-Matching

### ✅ Workflow-Integration
- Nahtlose Verbindung zwischen Upload und Workflows
- Automatische Dateiverarbeitung bei Workflow-Start
- Zentrale Dateiverwaltung

### ✅ Erweiterbarkeit
- Modularer Aufbau für weitere Features
- Konfigurierbare Fuzzy-Matching-Schwellenwerte
- Einfache Erweiterung der Dateinamen-Muster

## Nächste Schritte

### 🔄 Geplante Verbesserungen
1. **Drag & Drop** für Dateien
2. **Batch-Verarbeitung** für große Datenmengen
3. **Datei-Vorschau** vor dem Upload
4. **Projekt-basierte Organisation** zusätzlich zu Datums-Ordnern
5. **Automatische Backup-Funktion**

### 🎯 Optimierungen
1. **Performance** bei vielen Kunden
2. **Erweiterte Dateinamen-Erkennung**
3. **Konfigurierbare Workflow-Ordner**
4. **Integrierte Suchfunktion**

## Test-Szenarien

### ✅ Erfolgreich getestet
- [x] Neuer Kunde mit Upload
- [x] Bestehender Kunde mit exakter Übereinstimmung
- [x] Fuzzy-Matching für ähnliche Kundennamen
- [x] Datumsorganisation
- [x] Workflow-Integration
- [x] Kundenvorschläge aus Dateinamen
- [x] Ordner-Öffnung

### 🔄 Weitere Tests erforderlich
- [ ] Große Dateimengen (Performance)
- [ ] Spezielle Zeichen in Dateinamen
- [ ] Sehr lange Kundennamen
- [ ] Gleichzeitige Workflows

## Fazit

Das erweiterte Upload-System bietet eine vollständige Integration zwischen Datei-Upload und Kundenmanagement. Die Fuzzy-Matching-Funktionalität und automatische Datumsorganisation reduzieren den manuellen Aufwand erheblich und sorgen für eine konsistente Datenorganisation.

Die modulare Struktur ermöglicht einfache Erweiterungen und Anpassungen für zukünftige Anforderungen.
