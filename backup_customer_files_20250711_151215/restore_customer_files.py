#!/usr/bin/env python3
"""
Restore-Script für Customer-Management Backup
Backup erstellt am: 11.07.2025 15:12:15
"""

import os
import shutil
import json
from pathlib import Path

def restore_customer_files():
    """Stellt die gesicherten Customer-Dateien wieder her"""
    
    backup_dir = Path("c:\Users\sarah\Desktop\Checker\backup_customer_files_20250711_151215")
    base_dir = Path("c:\Users\sarah\Desktop\Checker")
    
    if not backup_dir.exists():
        print(f"❌ Backup-Ordner nicht gefunden: {backup_dir}")
        return False
    
    # Lade Manifest
    manifest_path = backup_dir / "backup_manifest.json"
    if not manifest_path.exists():
        print("❌ Backup-Manifest nicht gefunden!")
        return False
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"🔄 Restore Backup vom {manifest['timestamp']}")
    print(f"📁 {len(manifest['files'])} Dateien gefunden")
    
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
                    response = input(f"⚠️ {file_info['original_path']} existiert bereits. Überschreiben? (j/n): ")
                    if response.lower() not in ['j', 'ja', 'y', 'yes']:
                        print(f"   ⏭️ Übersprungen: {file_info['original_path']}")
                        continue
                
                # Restore Datei
                shutil.copy2(str(backup_file), str(restore_dest))
                print(f"   ✅ Restored: {file_info['original_path']}")
                restored += 1
                
            except Exception as e:
                print(f"   ❌ Fehler bei {file_info['original_path']}: {e}")
        else:
            print(f"   ⚠️ Backup-Datei nicht gefunden: {backup_file}")
    
    print(f"\n✅ Restore abgeschlossen: {restored} Dateien wiederhergestellt")
    return True

if __name__ == "__main__":
    restore_customer_files()
