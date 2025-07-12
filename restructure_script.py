# 🚀 STRUKTURIERUNGS-SCRIPT

import os
import shutil
from pathlib import Path

def restructure_checker_project():
    """
    Strukturierung des Checker Projekts in logische Ordner
    """
    base_path = Path("c:/Users/sarah/Desktop/Checker")
    
    # Neue Ordner-Struktur definieren
    structure = {
        "core": [
            "checker_app.py",
            "ki_module.py", 
            "kunden_manager.py",
            "config.json",
            "customer_profile.json"
        ],
        "ui": [
            "modern_ui_components.py",
            "ui_theme.py",
            "theme.py",
            "theme_zentrale.py",
            "theme_loader.py",
            "theme_utils.py"
        ],
        "animations": [
            "modern_animations.py",
            "advanced_visual_effects.py",
            "ui_animations.py"
        ],
        "workflows": [
            "pruefung_workflow.py",
            "projekt_workflow.py", 
            "pruefung_workflow_controller.py",
            "finalisierung_workflow2.py"
        ],
        "screens": [
            "ultra_modern_welcome_screen_simplified.py",
            "modern_dashboard.py"
        ],
        "icons": [
            "fluent_icons_manager.py",
            "icon_manager.py",
            "checker_app_icons.json"
        ],
        "tests": [
            "test_modern_gui.py",
            "test_app.py",
            "test_animations.py",
            "test_icons.py"
        ],
        "integration": [
            "gui_improvements_integration.py"
        ],
        "components": [
            "welcome_screen_components/customer_section.py",
            "welcome_screen_components/footer_section.py", 
            "welcome_screen_components/header_section.py",
            "welcome_screen_components/section_header_mixin.py",
            "welcome_screen_components/upload_section.py",
            "welcome_screen_components/workflow_section.py",
            "ui_components/searchable_dropdown.py",
            "ui_components/pruefung_workflow_view.py"
        ],
        "utils": [
            "utils/icon_manager.py",
            "core/workflow_factory.py",
            "core/thread_manager.py",
            "core/state_manager.py", 
            "core/memory_manager.py"
        ],
        "resources": [
            "dummy_ocr_test_image.png",
            "dummy_ocr_test_pdf.pdf",
            "*.ico",
            "*.png"
        ]
    }
    
    print("🏗️  STRUKTURIERUNG STARTET...")
    print("=" * 50)
    
    # Ordner erstellen
    for folder_name in structure.keys():
        folder_path = base_path / folder_name
        folder_path.mkdir(exist_ok=True)
        print(f"📁 Ordner erstellt: {folder_name}/")
    
    # Dateien verschieben
    moved_files = 0
    for folder_name, files in structure.items():
        folder_path = base_path / folder_name
        
        for file_pattern in files:
            # Direkte Datei
            if not file_pattern.startswith("*") and not "/" in file_pattern:
                source_file = base_path / file_pattern
                if source_file.exists():
                    target_file = folder_path / file_pattern
                    if not target_file.exists():
                        shutil.move(str(source_file), str(target_file))
                        print(f"✅ Verschoben: {file_pattern} → {folder_name}/")
                        moved_files += 1
                    else:
                        print(f"⚠️  Bereits vorhanden: {file_pattern}")
            
            # Unterordner-Dateien
            elif "/" in file_pattern:
                source_file = base_path / file_pattern
                if source_file.exists():
                    # Unterordner im Zielordner erstellen
                    subdir = Path(file_pattern).parent
                    target_subdir = folder_path / subdir
                    target_subdir.mkdir(parents=True, exist_ok=True)
                    
                    target_file = folder_path / file_pattern
                    if not target_file.exists():
                        shutil.move(str(source_file), str(target_file))
                        print(f"✅ Verschoben: {file_pattern} → {folder_name}/")
                        moved_files += 1
            
            # Wildcard-Dateien
            elif file_pattern.startswith("*"):
                matching_files = list(base_path.glob(file_pattern))
                for match in matching_files:
                    if match.is_file():
                        target_file = folder_path / match.name
                        if not target_file.exists():
                            shutil.move(str(match), str(target_file))
                            print(f"✅ Verschoben: {match.name} → {folder_name}/")
                            moved_files += 1
    
    # Leere Unterordner entfernen
    for subdir in ["welcome_screen_components", "ui_components", "core", "utils"]:
        subdir_path = base_path / subdir
        if subdir_path.exists() and not any(subdir_path.iterdir()):
            shutil.rmtree(subdir_path)
            print(f"🗑️  Leeren Ordner entfernt: {subdir}")
    
    print(f"\n🎉 STRUKTURIERUNG ABGESCHLOSSEN!")
    print(f"📦 {moved_files} Dateien verschoben")
    
    # Übersicht über neue Struktur
    print(f"\n📊 NEUE PROJEKT-STRUKTUR:")
    for folder_name in structure.keys():
        folder_path = base_path / folder_name
        if folder_path.exists():
            files_in_folder = [f for f in folder_path.rglob("*") if f.is_file()]
            print(f"📂 {folder_name}/ ({len(files_in_folder)} Dateien)")
    
    # Hauptdateien die noch im Root sind
    root_files = [f for f in base_path.glob("*.py") if f.is_file()]
    if root_files:
        print(f"\n⚠️  NOCH IM ROOT-VERZEICHNIS ({len(root_files)} Dateien):")
        for file in root_files[:10]:  # Nur erste 10 anzeigen
            print(f"   📄 {file.name}")
        if len(root_files) > 10:
            print(f"   ... und {len(root_files) - 10} weitere")
    
    return moved_files

def create_new_main_file():
    """
    Erstellt eine neue, vereinfachte Hauptdatei
    """
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker App - Haupteinstiegspunkt
Modernisierte Version mit strukturierter Architektur
"""

import sys
import os
from pathlib import Path

# Pfad-Setup für neue Struktur
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Core-Imports
from core.checker_app import CheckerApp
from ui.ui_theme import UITheme
from integration.gui_improvements_integration import GuiImprovementsIntegration

def main():
    """
    Haupteinstiegspunkt der Anwendung
    """
    try:
        # Theme initialisieren
        theme = UITheme()
        theme.setup_theme()
        
        # GUI-Verbesserungen laden
        gui_improvements = GuiImprovementsIntegration()
        gui_improvements.initialize()
        
        # Hauptanwendung starten
        app = CheckerApp()
        app.run()
        
    except Exception as e:
        print(f"❌ Fehler beim Starten der Anwendung: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    main_file = Path("c:/Users/sarah/Desktop/Checker/main.py")
    main_file.write_text(main_content, encoding='utf-8')
    print(f"✅ Neue Hauptdatei erstellt: main.py")

if __name__ == "__main__":
    print("🏗️  CHECKER PROJECT RESTRUCTURING SCRIPT")
    print("=" * 50)
    
    # Sicherheitsabfrage
    response = input("\n⚠️  WARNUNG: Dieser Script wird Dateien in neue Ordner verschieben!\n"
                    "Möchten Sie fortfahren? (ja/nein): ")
    
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        moved_count = restructure_checker_project()
        
        # Neue Hauptdatei erstellen
        create_main_response = input("\n💡 Soll eine neue, vereinfachte main.py erstellt werden? (ja/nein): ")
        if create_main_response.lower() in ['ja', 'j', 'yes', 'y']:
            create_new_main_file()
        
        print(f"\n🎉 Strukturierung erfolgreich abgeschlossen!")
        print(f"📦 {moved_count} Dateien wurden organisiert.")
        print(f"\n💡 NÄCHSTE SCHRITTE:")
        print("1. Testen Sie die neue Struktur")
        print("2. Passen Sie Import-Pfade in den Dateien an")
        print("3. Erstellen Sie __init__.py Dateien in den Ordnern")
        print("4. Testen Sie die Anwendung mit: python main.py")
        
    else:
        print("❌ Strukturierung abgebrochen.")
