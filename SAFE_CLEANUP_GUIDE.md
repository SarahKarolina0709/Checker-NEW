# Sichere Backup & Cleanup Optionen für Customer-Management Dateien

## 🛡️ Sicheres Cleanup mit vollständigem Backup

### Option 1: Vollständiges Backup + Cleanup (EMPFOHLEN)
```powershell
# Erstellt timestamped Backup + kategorisierte Archive
python safe_cleanup_customer_files.py
```

**Was passiert:**
- ✅ Vollständiges Backup mit Timestamp (z.B. `backup_customer_files_20250711_150230/`)
- ✅ Kategorisierte Archive (`archive/legacy_versions/`, `archive/integration_files/`)  
- ✅ Backup-Manifest mit Datei-Infos
- ✅ Automatisches Restore-Script
- ✅ Archiv-Übersicht mit Dokumentation

### Option 2: Nur Test-Dateien archivieren (optional)
```powershell
# Erstelle Test-Archiv
mkdir archive\test_files
move demo_customer_section_calls.py archive\test_files\
move live_test_customer_section.py archive\test_files\
move test_customer_section_integration.py archive\test_files\
move customer_section_test_utils.py archive\test_files\
move test_modern_customer_ui.py archive\test_files\
move test_customer_management.py archive\test_files\
```

### Option 3: Status prüfen (jederzeit)
```powershell
python analyze_duplicate_files.py
```

## 🔄 Restore-Optionen

### Kompletter Restore
```powershell
# Alle Dateien aus Backup wiederherstellen
python backup_customer_files_[timestamp]\restore_customer_files.py
```

### Einzelne Datei aus Archiv
```powershell
# Beispiel: Legacy Version reaktivieren  
copy archive\legacy_versions\customer_section_v2.py welcome_screen_components\
```

### Archiv durchsuchen
```powershell
# Zeige Archiv-Inhalt
dir archive\legacy_versions\
dir archive\integration_files\
type archive\ARCHIVE_OVERVIEW.md
```

## 📊 Backup-Struktur

```
backup_customer_files_20250711_150230/
├── backup_manifest.json          # Datei-Verzeichnis
├── restore_customer_files.py     # Automatisches Restore-Script
├── customer_section_v2.py        # Original-Struktur beibehalten
├── customer_management_*.py
└── welcome_screen_components/
    ├── customer_section.py
    ├── customer_section_v2.py
    └── customer_section_with_calendar.py

archive/
├── ARCHIVE_OVERVIEW.md           # Dokumentation
├── legacy_versions/
│   ├── customer_section.py
│   ├── customer_section_v2.py
│   └── customer_section_with_calendar.py
└── integration_files/
    ├── customer_management_integration.py
    └── customer_management_final_integration.py
```

## ✅ Nach dem Cleanup - Saubere Architektur

**Aktive Dateien (3 Dateien):**
- `checker_app.py` -> Haupteinstiegspunkt mit ViewStack
- `simplified_modern_customer_ui.py` -> Fallback Customer UI  
- `customer_section_complete.py` -> Haupt Customer Management mit Projekt-Auswahl

**Prioritätssystem bleibt intakt:**
1. CustomerSectionComplete (Haupt-UI)
2. SimplifiedModernCustomerUI (Fallback)
3. ui_modernizer (Emergency Fallback)

## 🎯 Empfehlung

**SICHER:** Führen Sie Option 1 aus - das Script erstellt vollständige Backups und Sie können jederzeit alles wiederherstellen!

```powershell
python safe_cleanup_customer_files.py
```
