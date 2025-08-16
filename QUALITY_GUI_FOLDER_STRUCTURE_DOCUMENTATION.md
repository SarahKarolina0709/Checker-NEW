# 📂 QUALITY GUI FOLDER STRUCTURE DOCUMENTATION

## 🎯 ZWECK
Diese Dokumentation definiert die **verbindliche Ordnerstruktur** für die Quality GUI und alle damit verbundenen Upload- und Analyseprozesse.

## 📋 STANDARD-PROJEKTSTRUKTUR

### ✅ VERBINDLICHE UNTERORDNER-HIERARCHIE
```
Checker_Projekte/
├── [Kundenname]/
│   ├── 2025-01-15/
│   │   ├── 01_Ausgangstext/
│   │   │   ├── dokument1.pdf
│   │   │   ├── dokument2.docx
│   │   │   └── vertrag.txt
│   │   ├── 02_Angebot/
│   │   ├── 03_Prüfung/
│   │   └── 04_Finalisierung/
│   └── 2025-01-16/
│       ├── 01_Ausgangstext/
│       ├── 02_Angebot/
│       ├── 03_Prüfung/
│       └── 04_Finalisierung/
```

## 🚨 KRITISCHE INTEGRATION REQUIREMENTS

### ✅ QUALITY GUI MUSS IMMER

- **Automatische Ordnererstellung**: Alle Unterordner werden bei Upload automatisch erstellt
- **Intelligente Dateizuordnung**: Alle Dateien → 01_Ausgangstext/ (vereinfachter Workflow)
- **Strukturvalidierung**: Prüfung ob alle erforderlichen Ordner existieren
- **Konsistente Pfade**: Alle internen Pfade folgen der definierten Struktur
- **Fehlerbehandlung**: Robuste Behandlung fehlender oder beschädigter Ordnerstrukturen

### ✅ UPLOAD-WORKFLOW INTEGRATION

1. **Kundenwahl** → Automatische Ordnererstellung unter Checker_Projekte/[Kundenname]/
2. **Datums-Ordner** → Heutiges Datum (YYYY-MM-DD) wird automatisch erstellt
3. **Workflow-Ordner** → Alle 4 Standard-Ordner (01_Ausgangstext bis 04_Finalisierung) werden erstellt
4. **Datei-Upload** → Alle hochgeladenen Dateien werden automatisch in 01_Ausgangstext/ gespeichert
5. **Struktur-Validierung** → Prüfung der korrekten Ordner-Hierarchie bei jedem Upload

## 🔧 IMPLEMENTIERUNGS-RICHTLINIEN

### 📌 PYTHON IMPLEMENTATION PATTERN:
```python
class QualityGUIFolderManager:
    """Verwaltet die Standard-Ordnerstruktur für Quality GUI"""
    
    STANDARD_PROJECT_STRUCTURE = [
        "01_Ausgangstext",
        "02_Angebot", 
        "03_Prüfung",
        "04_Finalisierung"
    ]
    
    def create_project_structure(self, customer_name, project_date):
        """Erstellt vollständige Projektstruktur"""
        base_path = f"Checker_Projekte/{customer_name}/{project_date}"
        for folder in self.STANDARD_PROJECT_STRUCTURE:
            os.makedirs(os.path.join(base_path, folder), exist_ok=True)
```

### 📌 INTEGRATION IN QUALITY_GUI_MAIN_APP.PY:
```python
def __init__(self):
    # Ordnerstruktur-Manager initialisieren
    self.folder_manager = QualityGUIFolderManager()
    self.project_structure = self.folder_manager.STANDARD_PROJECT_STRUCTURE
    
def _upload_files_with_structure(self, customer_name, files):
    """Upload mit automatischer Ordnererstellung"""
    project_date = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Projektstruktur erstellen
    self.folder_manager.create_project_structure(customer_name, project_date)
    
    # 2. Dateien kategorisieren und einordnen
    for file_path in files:
        if self._is_source_text(file_path):
            target_folder = f"Projekte/{customer_name}/{project_date}_Projekt/01_Input/01_Ausgangstext/"
        elif self._is_translation(file_path):
            target_folder = f"Projekte/{customer_name}/{project_date}_Projekt/01_Input/02_Übersetzung/"
        
        # Datei kopieren
        shutil.copy2(file_path, target_folder)
```

## 🎯 BENUTZER-EXPERIENCE IMPROVEMENTS

### ✅ UI-INTEGRATION REQUIREMENTS:
- **Ordner-Browser**: Visueller Tree-View der Projektstruktur
- **Automatische Navigation**: Ein-Klick-Zugang zu allen Unterordnern
- **Struktur-Validation**: Status-Anzeige der Ordnervollständigkeit
- **Smart-Upload**: Drag & Drop mit automatischer Kategorisierung
- **Ordner-Shortcuts**: Schnellzugriff auf häufig genutzte Ordner

### ✅ QUALITY-ANALYSIS INTEGRATION

- **Automatische Report-Speicherung**: Alle Analysen direkt in 03_Prüfung/ gespeichert
- **Output-Management**: Finale Deliverables in 04_Finalisierung/ organisiert
- **Strukturierte Ablage**: Konsistente Projektorganisation für bessere Nachverfolgung
- **Client-Präsentation**: Professionelle Ordnerstruktur für Kundenpräsentationen

## 🚨 TROUBLESHOOTING & ERROR HANDLING

### ✅ ROBUSTE FEHLERBEHANDLUNG:
- **Ordner-Zugriffsfehler**: Fallback auf temporäre Struktur
- **Unvollständige Struktur**: Automatische Nachbildung fehlender Ordner
- **Dateizuordnungs-Fehler**: Manuelle Kategorisierung mit UI-Dialog
- **Pfad-Längenbegrenzung**: Intelligente Pfadkürzung bei Windows-Limits

### ✅ VALIDATION & RECOVERY:
```python
def validate_project_structure(self, project_path):
    """Validiert und repariert Projektstruktur"""
    missing_folders = []
    for folder in self.STANDARD_PROJECT_STRUCTURE:
        full_path = os.path.join(project_path, folder)
        if not os.path.exists(full_path):
            missing_folders.append(folder)
            os.makedirs(full_path, exist_ok=True)
    
    if missing_folders:
        self.log_structure_repair(missing_folders)
    return len(missing_folders) == 0
```

## 📋 MIGRATION STRATEGY

### ✅ BESTEHENDE PROJEKTE UPGRADEN:
1. **Struktur-Analyse**: Scannen vorhandener Projektordner
2. **Automatische Migration**: Verschieben von Dateien in neue Struktur
3. **Backup-Erstellung**: Sicherung vor Strukturänderungen
4. **Validierung**: Vollständigkeitsprüfung nach Migration
5. **User-Notification**: Bericht über Migrations-Erfolg

## 🎯 BENEFITS DER STRUKTURIERTEN ORDNER-ORGANISATION

### ✅ ENTWICKLER-VORTEILE:
- **Konsistenz**: Einheitliche Struktur in allen Projekten
- **Wartbarkeit**: Einfache Navigation und Dateiverwaltung
- **Skalierbarkeit**: Struktur wächst mit Projekt-Komplexität
- **Automatisierung**: Weniger manuelle Ordnerverwaltung

### ✅ BENUTZER-VORTEILE:
- **Klarheit**: Intuitive Ordnerstruktur mit logischer Hierarchie
- **Effizienz**: Schneller Zugriff auf relevante Dateien
- **Professionalität**: Business-ready Projektorganisation
- **Konsistenz**: Gleiche Struktur für alle Kunden und Projekte

## 🚀 IMPLEMENTATION PRIORITY

### 📌 PHASE 1 (KRITISCH):
- Integration der Ordnerstruktur in quality_gui_main_app.py
- Automatische Erstellung bei Upload-Prozess
- Basis-Validierung und Fehlerbehandlung

### 📌 PHASE 2 (HOCH):
- UI-Integration mit visueller Ordner-Navigation
- Erweiterte Validierung und Auto-Repair
- Migration bestehender Projekte

### 📌 PHASE 3 (MITTEL):
- Erweiterte Analytics und Metrics-Integration
- Automatische Backup-Strategien
- Performance-Optimierungen

---

## ✅ DIESE DOKUMENTATION IST VERBINDLICH FÜR ALLE QUALITY GUI ENTWICKLUNGEN!

Jede Upload-Funktionalität, jeder Analyse-Workflow und jede Dateiverwaltung muss die hier definierte Ordnerstruktur verwenden und respektieren.
