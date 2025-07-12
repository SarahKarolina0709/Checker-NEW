#!/usr/bin/env python3
"""
Analyse der doppelten/redundanten Python-Dateien
Erstellt eine Übersicht und Empfehlungen für Aufräumarbeiten
"""

import os
import time
from pathlib import Path

def analyze_duplicate_files():
    """Analysiert doppelte Customer-Management Dateien"""
    
    print("🔍 Analyse doppelter Customer-Management Dateien")
    print("=" * 60)
    
    # Kategorien definieren
    categories = {
        "AKTIV IN VERWENDUNG": {
            "files": [
                "checker_app.py",
                "simplified_modern_customer_ui.py",
                "welcome_screen_components/customer_section_complete.py"
            ],
            "status": "✅ BEHALTEN",
            "description": "Diese Dateien sind aktiv in der App integriert"
        },
        
        "LEGACY VERSIONEN": {
            "files": [
                "welcome_screen_components/customer_section.py",
                "welcome_screen_components/customer_section_v2.py", 
                "welcome_screen_components/customer_section_with_calendar.py",
                "customer_section_v2.py"
            ],
            "status": "⚠️ PRÜFEN/ARCHIVIEREN",
            "description": "Ältere Versionen, möglicherweise redundant"
        },
        
        "INTEGRATION DATEIEN": {
            "files": [
                "customer_management_integration.py",
                "customer_management_final_integration.py"
            ],
            "status": "⚠️ PRÜFEN/LÖSCHEN",
            "description": "Integration bereits in checker_app.py abgeschlossen"
        },
        
        "TEST/DEMO DATEIEN": {
            "files": [
                "test_modern_customer_ui.py",
                "test_customer_management.py",
                "demo_customer_section_calls.py",
                "live_test_customer_section.py",
                "test_customer_section_integration.py",
                "customer_section_test_utils.py"
            ],
            "status": "📋 TEST-DATEIEN",
            "description": "Test- und Demo-Dateien (können behalten oder archiviert werden)"
        }
    }
    
    # Analyse ausgeben
    for category, info in categories.items():
        print(f"\n📁 {category}")
        print(f"   Status: {info['status']}")
        print(f"   Info: {info['description']}")
        print("   Dateien:")
        
        for file_path in info['files']:
            full_path = os.path.join("c:\\Users\\sarah\\Desktop\\Checker", file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                mtime = time.ctime(os.path.getmtime(full_path))
                print(f"   ✅ {file_path} ({size} bytes, {mtime})")
            else:
                print(f"   ❌ {file_path} (nicht gefunden)")
    
    print("\n" + "=" * 60)
    print("📋 EMPFEHLUNGEN:")
    print("\n🎯 AKTUELLE ARCHITEKTUR:")
    print("   1. checker_app.py -> Haupteinstiegspunkt")
    print("   2. show_customer_menu() -> Prioritätssystem:")
    print("      - Priorität 1: CustomerSectionComplete")
    print("      - Priorität 2: SimplifiedModernCustomerUI") 
    print("      - Priorität 3: ui_modernizer fallback")
    
    print("\n🧹 AUFRÄUM-EMPFEHLUNGEN:")
    print("   ✅ BEHALTEN:")
    print("      - checker_app.py (Hauptapp)")
    print("      - simplified_modern_customer_ui.py (Fallback UI)")
    print("      - customer_section_complete.py (Haupt Customer UI)")
    
    print("\n   📦 ARCHIVIEREN (in 'archive/' Ordner):")
    print("      - customer_section*.py (Legacy Versionen)")
    print("      - customer_management_*.py (Veraltete Integration)")
    
    print("\n   🗑️ LÖSCHEN (Test-Dateien bei Bedarf):")
    print("      - demo_*.py, test_*.py, live_test_*.py")
    print("      - (Nur wenn Tests nicht mehr benötigt)")
    
    print("\n💡 NÄCHSTE SCHRITTE:")
    print("   1. Archive-Ordner erstellen")
    print("   2. Legacy-Dateien verschieben")
    print("   3. Integration testen")
    print("   4. Quick-Commands für Aufräumen erstellen")

def create_cleanup_script():
    """Erstellt ein Cleanup-Script"""
    
    cleanup_script = '''#!/usr/bin/env python3
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
    
    print("\\n✅ Cleanup abgeschlossen!")
    print("\\n📋 Aktive Dateien:")
    print("   - checker_app.py (Hauptapp)")
    print("   - simplified_modern_customer_ui.py (Fallback)")
    print("   - welcome_screen_components/customer_section_complete.py (Haupt-UI)")

if __name__ == "__main__":
    cleanup_customer_files()
'''
    
    with open("cleanup_customer_files.py", "w", encoding="utf-8") as f:
        f.write(cleanup_script)
    
    print("\n✅ Cleanup-Script erstellt: cleanup_customer_files.py")

if __name__ == "__main__":
    analyze_duplicate_files()
    create_cleanup_script()
