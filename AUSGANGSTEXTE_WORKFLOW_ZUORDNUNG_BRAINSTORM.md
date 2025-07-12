# 📋 Ausgangstexte-Workflow Zuordnung - Brainstorming

## 🎯 Ziel
Jeder Workflow (Angebot, Prüfung, Finalisierung) muss den korrekten Ausgangstexten zugeordnet werden, um eine lückenlose Nachverfolgbarkeit und Qualitätssicherung zu gewährleisten.

## 📁 Erweiterte Ordnerstruktur mit Ausgangstexten

```
Checker_Projekte/
├── [Kunde_Name]/
│   ├── Ausgangstexte/
│   │   ├── 2025-01-15_Projekt_A/
│   │   │   ├── source_document.docx
│   │   │   ├── reference_material.pdf
│   │   │   ├── metadata.json
│   │   │   └── upload_info.txt
│   │   ├── 2025-01-20_Projekt_B/
│   │   │   ├── original_text.txt
│   │   │   ├── images/
│   │   │   └── metadata.json
│   │   └── ...
│   ├── Angebot/
│   │   ├── 2025-01-15_Projekt_A_Angebot/
│   │   │   ├── angebot.pdf
│   │   │   ├── analyse_ergebnis.json
│   │   │   └── VERKNUEPFT_MIT: 2025-01-15_Projekt_A
│   │   └── ...
│   ├── Pruefung/
│   │   ├── 2025-01-15_Projekt_A_Pruefung/
│   │   │   ├── gepruefre_dateien/
│   │   │   ├── pruef_bericht.pdf
│   │   │   └── VERKNUEPFT_MIT: 2025-01-15_Projekt_A
│   │   └── ...
│   └── Finalisierung/
│       ├── 2025-01-15_Projekt_A_Final/
│       │   ├── finalisierte_dateien/
│       │   ├── lieferschein.pdf
│       │   └── VERKNUEPFT_MIT: 2025-01-15_Projekt_A
│       └── ...
```

## 🔗 Verknüpfungsmechanismen

### 1. **Metadaten-basierte Verknüpfung**
```json
// In jedem Workflow-Ordner: verknuepfung.json
{
  "ausgangstext_ordner": "2025-01-15_Projekt_A",
  "ausgangstext_pfad": "Ausgangstexte/2025-01-15_Projekt_A",
  "kunde": "Musterfirma_AG",
  "projekt_id": "PROJ_2025_001",
  "erstellt_am": "2025-01-15T10:30:00",
  "workflow_typ": "angebot|pruefung|finalisierung",
  "status": "in_bearbeitung|abgeschlossen|archiviert",
  "dateien_anzahl": 3,
  "original_dateien": [
    "source_document.docx",
    "reference_material.pdf"
  ]
}
```

### 2. **Namenskonvention für eindeutige Zuordnung**
```
Ausgangstexte: YYYY-MM-DD_Projektname
Angebot:       YYYY-MM-DD_Projektname_Angebot
Prüfung:       YYYY-MM-DD_Projektname_Pruefung
Finalisierung: YYYY-MM-DD_Projektname_Final
```

### 3. **Workflow-Status-Tracking**
```json
// projekt_status.json pro Ausgangstext-Ordner
{
  "projekt_name": "2025-01-15_Projekt_A",
  "workflows": {
    "angebot": {
      "status": "abgeschlossen",
      "ordner": "Angebot/2025-01-15_Projekt_A_Angebot",
      "erstellt_am": "2025-01-15T11:00:00",
      "abgeschlossen_am": "2025-01-15T14:30:00"
    },
    "pruefung": {
      "status": "in_bearbeitung",
      "ordner": "Pruefung/2025-01-15_Projekt_A_Pruefung",
      "erstellt_am": "2025-01-16T09:00:00",
      "abgeschlossen_am": null
    },
    "finalisierung": {
      "status": "wartend",
      "ordner": null,
      "erstellt_am": null,
      "abgeschlossen_am": null
    }
  }
}
```

## 🎮 UI/UX Integration - Workflow-Starter mit Ausgangstexte-Auswahl

### **Erweiterte Welcome Screen Sektion:**
```
┌─────────────────────────────────────────────────┐
│ 📁 Ausgangstexte & Workflows                    │
├─────────────────────────────────────────────────┤
│ Kunde: [Musterfirma AG ▼]                      │
│                                                 │
│ 📋 Verfügbare Ausgangstexte:                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ ✅ 2025-01-15_Projekt_A                    │ │
│ │    Status: Angebot ✅ | Prüfung 🔄 | Final ⏸️ │ │
│ │ ✅ 2025-01-20_Projekt_B                    │ │
│ │    Status: Angebot ✅ | Prüfung ✅ | Final ⏸️  │ │
│ │ 📄 2025-01-25_Neue_Texte                   │ │
│ │    Status: Keine Workflows                  │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [📤 Ausgangstexte hochladen]                   │
│                                                 │
│ 🔄 Workflow starten für ausgewähltes Projekt:  │
│ [💰 Angebot] [✅ Prüfung] [🎯 Finalisierung]   │
└─────────────────────────────────────────────────┘
```

## 🔄 Workflow-Starter Logik

### **Intelligente Workflow-Auswahl:**
1. **Angebot-Workflow:**
   - Zeigt nur Ausgangstexte ohne Angebot an
   - Erstellt automatisch verknüpften Angebot-Ordner
   
2. **Prüfung-Workflow:**
   - Zeigt nur Ausgangstexte mit abgeschlossenem Angebot an
   - Lädt Angebot-Daten für Kontext
   
3. **Finalisierung-Workflow:**
   - Zeigt nur Ausgangstexte mit abgeschlossener Prüfung an
   - Lädt Angebot- und Prüfung-Daten für Kontext

### **Workflow-Starter Code Struktur:**
```python
def start_workflow_with_ausgangstexte(self, workflow_type, ausgangstext_ordner):
    """
    Startet einen Workflow mit expliziter Ausgangstext-Zuordnung
    """
    customer_data = {
        'kunde_name': self.selected_customer,
        'ausgangstext_ordner': ausgangstext_ordner,
        'ausgangstext_pfad': f"Ausgangstexte/{ausgangstext_ordner}",
        'workflow_typ': workflow_type,
        'projekt_kontext': self.load_projekt_kontext(ausgangstext_ordner)
    }
    
    self.app.start_workflow(f"{workflow_type}_workflow", customer_data)
```

## 📊 Projekt-Status Dashboard

### **Übersichts-Widget:**
```
┌─────────────────────────────────────────────────┐
│ 📊 Projekt-Status: 2025-01-15_Projekt_A        │
├─────────────────────────────────────────────────┤
│ 📄 Ausgangstexte: 3 Dateien (12.5 MB)          │
│ 💰 Angebot: ✅ Abgeschlossen (15.01.2025)      │
│ ✅ Prüfung: 🔄 In Bearbeitung (seit 16.01.)    │
│ 🎯 Finalisierung: ⏸️ Wartend                    │
│                                                 │
│ [📁 Ausgangstexte öffnen] [📋 Status Details]  │
└─────────────────────────────────────────────────┘
```

## 🎯 Implementierungs-Prioritäten

### **Phase 1: Grundlagen (Sofort)**
- [ ] Erweiterte Ordnerstruktur mit Ausgangstexte
- [ ] Metadaten-System für Verknüpfungen
- [ ] Basis-UI für Ausgangstexte-Upload

### **Phase 2: Workflow-Integration (Nächste Woche)**
- [ ] Workflow-Starter mit Ausgangstexte-Auswahl
- [ ] Automatische Ordner-Verknüpfung
- [ ] Status-Tracking System

### **Phase 3: Erweiterte Features (Optional)**
- [ ] Projekt-Status Dashboard
- [ ] Automatische Workflow-Sequenzierung
- [ ] Erweiterte Suchfunktionen

## 🔧 Technische Umsetzung

### **KundenManager Erweiterungen:**
```python
class KundenManager:
    def get_ausgangstexte_ordner(self, kunde_name):
        """Gibt alle Ausgangstexte-Ordner für einen Kunden zurück"""
        
    def create_ausgangstexte_ordner(self, kunde_name, projekt_name):
        """Erstellt neuen Ausgangstexte-Ordner mit Metadaten"""
        
    def get_projekt_status(self, kunde_name, ausgangstext_ordner):
        """Gibt Status aller Workflows für ein Projekt zurück"""
        
    def link_workflow_to_ausgangstexte(self, workflow_ordner, ausgangstext_ordner):
        """Verknüpft Workflow-Ordner mit Ausgangstexten"""
```

### **Workflow-Module Erweiterungen:**
```python
class AngebotWorkflow:
    def __init__(self, ..., ausgangstext_kontext=None):
        self.ausgangstext_ordner = ausgangstext_kontext.get('ordner')
        self.ausgangstext_dateien = ausgangstext_kontext.get('dateien')
        self.setup_workflow_ordner()
        
    def setup_workflow_ordner(self):
        """Erstellt Workflow-Ordner mit Verknüpfung zu Ausgangstexten"""
```

## 💡 Zusätzliche Features

### **Automatische Dateierkennung:**
- Automatisches Laden der Ausgangstexte in Workflows
- Intelligente Dateityp-Erkennung
- Vorschau-Funktionen für verschiedene Formate

### **Workflow-Verlauf:**
- Vollständige Nachverfolgung aller Bearbeitungsschritte
- Versions-History für jede Datei
- Rollback-Funktionen

### **Kollaborations-Features:**
- Workflow-Status für Teams
- Kommentar-System pro Projekt
- Benachrichtigungen bei Status-Änderungen

---

**Nächste Schritte:** Soll ich anfangen, die Ausgangstexte-Upload Funktionalität zu implementieren oder zuerst die erweiterte Welcome Screen UI mit der Projekt-Auswahl erstellen?
