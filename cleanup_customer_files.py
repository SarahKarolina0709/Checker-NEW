#!/usr/bin/env python3
"""
Automatisches Cleanup-Script für redundante Customer-Management Dateien
"""

import os
import shutil
from pathlib import Path

def cleanup_customer_files():
    """Räumt redundante Customer-Dateien auf"""
    
    base_dir = Path("c:/Users/sarah/Desktop/Checker")
    archive_dir = base_dir / "archive"
    
    # Erstelle Archive-Ordner
    archive_dir.mkdir(exist_ok=True)
    print(f"📁 Archive-Ordner erstellt: {archive_dir}")
    
    # Dateien zum Archivieren
    files_to_archive = [
        "customer_section_v2.py",
        "customer_management_integration.py", 
        "customer_management_final_integration.py",
        "welcome_screen_components/customer_section.py",
        "welcome_screen_components/customer_section_v2.py",
        "welcome_screen_components/customer_section_with_calendar.py"
    ]
    
    # Dateien archivieren
    for file_path in files_to_archive:
        source = base_dir / file_path
        if source.exists():
            # Erstelle Unterordner falls nötig
            dest_dir = archive_dir / file_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest = archive_dir / file_path
            shutil.move(str(source), str(dest))
            print(f"📦 Archiviert: {file_path} -> archive/{file_path}")
        else:
            print(f"❌ Nicht gefunden: {file_path}")
    
    print("\n✅ Cleanup abgeschlossen!")
    print("\n📋 Aktive Dateien:")
    print("   - checker_app.py (Hauptapp)")
    print("   - simplified_modern_customer_ui.py (Fallback)")
    print("   - welcome_screen_components/customer_section_complete.py (Haupt-UI)")

if __name__ == "__main__":
    cleanup_customer_files()
