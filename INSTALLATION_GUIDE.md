# 🚀 Checker-App Installation Guide

## Voraussetzungen
- **Python 3.8+** (empfohlen: Python 3.12)
- **Windows 10/11** (primär getestet)
- **Mindestens 4GB RAM** für GUI-Performance

## 📦 Installation

### 1. Python prüfen/installieren
```bash
# Python-Version prüfen
py --version
# oder
python --version

# Falls Python nicht installiert:
# Download von https://www.python.org/downloads/
# Bei Installation: "Add Python to PATH" aktivieren
```

### 2. Abhängigkeiten installieren
```bash
# Im Checker-Projektordner
cd "C:\Users\sarah\Desktop\Checker"

# Alle Dependencies installieren
pip install -r requirements.txt

# Alternative: einzeln installieren
pip install customtkinter Pillow PyMuPDF langdetect tkinterdnd2-universal
```

### 3. Zusätzliche System-Dependencies

#### OCR (Tesseract) - Für Texterkennung
```bash
# Download Tesseract von: https://github.com/UB-Mannheim/tesseract/wiki
# Standard-Installationspfad: C:\Program Files\Tesseract-OCR
# Nach Installation: Tesseract zu PATH hinzufügen
```

#### Poppler (für PDF-Konvertierung) - Optional
```bash
# Download von: https://blog.alivate.com.au/poppler-windows/
# Entpacken nach: C:\poppler-xx\bin
# poppler/bin zu PATH hinzufügen
```

## 🎯 Schnell-Start

### Minimal Test
```bash
# Einfacher Welcome Screen Test
python -c "from common_imports import GUI_AVAILABLE; print('GUI Ready:', GUI_AVAILABLE)"
```

### Hauptanwendung starten
```bash
# Welcome Screen (empfohlen)
python core/app_simple.py

# Oder Quality GUI direkt
python quality_gui_main_app.py
```

### Tests ausführen
```bash
# Pytest Suite
python -m pytest -q

# VS Code Task verwenden
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Run Welcome Screen Test"
```

## 🔧 Konfiguration

### Wichtige Config-Dateien
- `config.json` - Hauptkonfiguration (🚨 NICHT ÄNDERN)
- `checker_config.json` - Projektpfade anpassen
- `design_system.py` - UI-Styling (Light Mode only)

### Projektpfade anpassen
```json
// checker_config.json
{
    "projects_base_path": "C:\\Users\\sarah\\Desktop\\Checker_Projekte"
}
```

## 🛠️ Entwicklung

### Code Quality Tools
```bash
# Code formatieren
black .

# Code-Style prüfen
ruff check .

# Tests mit Coverage
python -m pytest --cov=. --cov-report=html
```

### VS Code Tasks verfügbar
- "Run Welcome Screen Test" - Haupttest
- "Run Python Tests (pytest)" - Vollständige Tests
- "Backup all .py files" - Backup erstellen

## 📋 Module-Übersicht

### GUI Framework
- **customtkinter** - Moderne GUI-Widgets
- **tkinter** - Standard GUI (eingebaut)
- **tkinterdnd2** - Drag & Drop Support

### Dokumentverarbeitung  
- **PyMuPDF** - PDF-Lesen/Bearbeitung
- **python-docx** - Word-Dokumente
- **openpyxl** - Excel-Dateien
- **Pillow** - Bildverarbeitung

### Qualitätsprüfung
- **language-tool-python** - Grammatik/Rechtschreibung
- **langdetect** - Spracherkennung
- **pytesseract** - OCR (optional)

### System & Performance
- **psutil** - Systemüberwachung
- **aiofiles** - Async Datei-Operationen

## ⚠️ Bekannte Probleme & Lösungen

### Python nicht gefunden
```bash
# Microsoft Store Python deaktivieren
# Settings -> Apps -> Advanced app settings -> App execution aliases
# "App Installer" für python.exe/python3.exe deaktivieren
```

### CustomTkinter Import Error
```bash
pip install --upgrade customtkinter
```

### Tesseract OCR Error
- Tesseract installieren und zu PATH hinzufügen
- Oder in `pytesseract.pytesseract.tesseract_cmd` den Pfad setzen

### Performance Issues
- Mindestens 4GB RAM verfügbar
- Windows Defender Echtzeitschutz für Projektordner ausschließen

## 🔒 Wichtige Hinweise

- **Light Mode Only** - Dark Mode ist deaktiviert
- **Deutsche UI** - Alle Labels auf Deutsch
- **Kritische Dateien** - Siehe `CRITICAL_FILES_REGISTRY.json`
- **Design System** - Immer `design_system.py` verwenden für Styling

## 📞 Support

Bei Problemen:
1. `python dependency_check.py` ausführen
2. Log-Dateien in `logs/` prüfen  
3. VS Code Task "Run Welcome Screen Test" verwenden