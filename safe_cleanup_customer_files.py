#!/usr/bin/env python3
"""
Sicheres Backup und Cleanup-Script für Customer-Management Dateien
Erstellt vollständige Backups bevor Dateien archiviert werden
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def cleanup_customer_files():
    """Räumt redundante Customer-Dateien sicher auf mit vollständigem Backup"""
    
    base_dir = Path("c:/Users/sarah/Desktop/Checker")
    
    # Erstelle Backup-Ordner mit Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_dir / f"backup_customer_files_{timestamp}"
    
    # Erstelle auch allgemeinen Archive-Ordner
    archive_dir = base_dir / "archive"
    legacy_dir = archive_dir / "legacy_versions"
    integration_dir = archive_dir / "integration_files"
    
    # Erstelle alle Ordner
    for directory in [backup_dir, archive_dir, legacy_dir, integration_dir]:
        directory.mkdir(exist_ok=True, parents=True)
    
    print(f"📁 Backup-Ordner erstellt: {backup_dir}")
    print(f"📁 Archive-Ordner erstellt: {archive_dir}")
    
    # Kategorisiere Dateien zum Archivieren
    file_categories = {
        "legacy_versions": [
            "customer_section_v2.py",
            "welcome_screen_components/customer_section.py",
            "welcome_screen_components/customer_section_v2.py",
            "welcome_screen_components/customer_section_with_calendar.py"
        ],
        "integration_files": [
            "customer_management_integration.py", 
            "customer_management_final_integration.py"
        ]
    }
    
    total_archived = 0
    backup_manifest = {"timestamp": timestamp, "files": []}
    
    # Archiviere nach Kategorien
    for category, file_list in file_categories.items():
        category_dir = archive_dir / category
        category_dir.mkdir(exist_ok=True)
        
        print(f"\n📦 Archiviere {category}:")
        
        for file_path in file_list:
            source = base_dir / file_path
            if source.exists():
                try:
                    # 1. Erstelle Backup (komplette Struktur)
                    backup_dest_dir = backup_dir / Path(file_path).parent
                    backup_dest_dir.mkdir(parents=True, exist_ok=True)
                    backup_dest = backup_dir / file_path
                    shutil.copy2(str(source), str(backup_dest))
                    
                    # 2. Archiviere in Kategorie-Ordner
                    archive_dest = category_dir / Path(file_path).name
                    shutil.move(str(source), str(archive_dest))
                    
                    # Zeige Dateigröße
                    size = archive_dest.stat().st_size
                    print(f"   ✅ {file_path} -> {category}/{Path(file_path).name} ({size} bytes)")
                    
                    # Backup-Manifest aktualisieren
                    backup_manifest["files"].append({
                        "original_path": str(file_path),
                        "backup_path": str(backup_dest.relative_to(base_dir)),
                        "archive_path": str(archive_dest.relative_to(base_dir)),
                        "category": category,
                        "size": size
                    })
                    
                    total_archived += 1
                    
                except Exception as e:
                    print(f"   ❌ Fehler bei {file_path}: {e}")
            else:
                print(f"   ⚠️ Nicht gefunden: {file_path}")
    
    # Speichere Backup-Manifest
    manifest_path = backup_dir / "backup_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(backup_manifest, f, ensure_ascii=False, indent=2)
    
    # Erstelle Restore-Script
    create_restore_script(backup_dir, base_dir, backup_manifest)
    
    # Erstelle Archiv-Übersicht
    create_archive_overview(archive_dir, file_categories, total_archived)
    
    print(f"\n✅ Cleanup abgeschlossen!")
    print(f"📊 {total_archived} Dateien archiviert")
    print(f"💾 Vollständiges Backup: {backup_dir}")
    print(f"📋 Kategorisiertes Archiv: {archive_dir}")
    
    print("\n📁 Aktive Dateien (nach Cleanup):")
    print("   - checker_app.py (Hauptapp)")
    print("   - simplified_modern_customer_ui.py (Fallback)")
    print("   - welcome_screen_components/customer_section_complete.py (Haupt-UI)")
    
    print(f"\n🔄 Restore möglich mit: python restore_customer_files.py {backup_dir.name}")
    
    return backup_dir, total_archived

def create_restore_script(backup_dir, base_dir, backup_manifest):
    """Erstellt ein Restore-Script für die gesicherten Dateien"""
    
    restore_script = f'''#!/usr/bin/env python3
"""
Restore-Script für Customer-Management Backup
Backup erstellt am: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
"""

import os
import shutil
import json
from pathlib import Path

def restore_customer_files():
    """Stellt die gesicherten Customer-Dateien wieder her"""
    
    backup_dir = Path("{backup_dir}")
    base_dir = Path("{base_dir}")
    
    if not backup_dir.exists():
        print(f"❌ Backup-Ordner nicht gefunden: {{backup_dir}}")
        return False
    
    # Lade Manifest
    manifest_path = backup_dir / "backup_manifest.json"
    if not manifest_path.exists():
        print("❌ Backup-Manifest nicht gefunden!")
        return False
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"🔄 Restore Backup vom {{manifest['timestamp']}}")
    print(f"📁 {{len(manifest['files'])}} Dateien gefunden")
    
    restored = 0
    
    for file_info in manifest["files"]:
        backup_file = backup_dir / file_info["backup_path"]
        restore_dest = base_dir / file_info["original_path"]
        
        if backup_file.exists():
            try:
                # Erstelle Ziel-Ordner falls nötig
                restore_dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Prüfe ob Datei bereits existiert
                if restore_dest.exists():
                    response = input(f"⚠️ {{file_info['original_path']}} existiert bereits. Überschreiben? (j/n): ")
                    if response.lower() not in ['j', 'ja', 'y', 'yes']:
                        print(f"   ⏭️ Übersprungen: {{file_info['original_path']}}")
                        continue
                
                # Restore Datei
                shutil.copy2(str(backup_file), str(restore_dest))
                print(f"   ✅ Restored: {{file_info['original_path']}}")
                restored += 1
                
            except Exception as e:
                print(f"   ❌ Fehler bei {{file_info['original_path']}}: {{e}}")
        else:
            print(f"   ⚠️ Backup-Datei nicht gefunden: {{backup_file}}")
    
    print(f"\\n✅ Restore abgeschlossen: {{restored}} Dateien wiederhergestellt")
    return True

if __name__ == "__main__":
    restore_customer_files()
'''
    
    restore_path = backup_dir / "restore_customer_files.py"
    with open(restore_path, "w", encoding="utf-8") as f:
        f.write(restore_script)
    
    print(f"📄 Restore-Script erstellt: {restore_path}")

def create_archive_overview(archive_dir, file_categories, total_archived):
    """Erstellt eine Übersicht über das Archiv"""
    
    overview = f"""# Customer-Management Archiv
Erstellt am: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
Archivierte Dateien: {total_archived}

## Archiv-Struktur

### 📁 legacy_versions/
Alte Versionen der Customer-Section Komponenten:
- customer_section.py (Original-Version)
- customer_section_v2.py (Erweiterte Version)
- customer_section_with_calendar.py (Version mit Kalender)

### 📁 integration_files/
Veraltete Integration-Dateien:
- customer_management_integration.py (Frühe Integration)
- customer_management_final_integration.py (Vorläufige finale Integration)

## Aktuelle Architektur (nach Cleanup)

✅ **AKTIVE DATEIEN:**
- `checker_app.py` - Hauptanwendung mit integriertem CustomerSectionComplete
- `simplified_modern_customer_ui.py` - Fallback Customer UI
- `welcome_screen_components/customer_section_complete.py` - Haupt Customer Management UI

## Restore-Optionen

### Kompletter Restore
```bash
# Alle Dateien wiederherstellen
python backup_customer_files_[timestamp]/restore_customer_files.py
```

### Einzelne Datei aus Archiv kopieren
```bash
# Beispiel: Legacy Version wiederherstellen
copy archive/legacy_versions/customer_section_v2.py welcome_screen_components/
```

## Backup-Verzeichnis
- Vollständiges Backup mit Original-Struktur in: `backup_customer_files_[timestamp]/`
- Manifest-Datei: `backup_manifest.json`
- Automatisches Restore-Script verfügbar

---
**Hinweis:** Das Archiv kann sicher gelöscht werden, aber die Backup-Ordner sollten 
für mindestens 30 Tage aufbewahrt werden, falls ein Restore notwendig wird.
"""
    
    overview_path = archive_dir / "ARCHIVE_OVERVIEW.md"
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write(overview)
    
    print(f"📄 Archiv-Übersicht erstellt: {overview_path}")

if __name__ == "__main__":
    backup_dir, count = cleanup_customer_files()
    print(f"\n🎯 Backup-Verzeichnis: {backup_dir}")
    print(f"📊 Archivierte Dateien: {count}")
