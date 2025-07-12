# 🧹 AUTOMATISCHER CLEANUP SCRIPT

import os
import shutil
import glob
from pathlib import Path

def cleanup_checker_project():
    """
    Automatische Bereinigung des Checker Projekts
    """
    base_path = Path("c:/Users/sarah/Desktop/Checker")
    
    # Backup-Ordner erstellen
    backup_path = base_path / "BACKUP_BEFORE_CLEANUP"
    backup_path.mkdir(exist_ok=True)
    
    # Kategorien von Dateien zum Löschen
    patterns_to_delete = [
        "*_backup.py",
        "*_old.py", 
        "*_broken.py",
        "*_restored.py",
        "temp_*.py",
        "quick_*.py",
        "debug_*.py",
        "verify_*.py",
        "test_*_old.py",
        "test_*_broken.py",
        "test_*_backup.py",
        "*_test_*.py",
        "nuclear_*.py",
        "emergency_*.py",
        "ultimate_*.py",
        "create_*.py",
        "recreate_*.py",
        "fix_*.py",
        "patch_*.py",
        "show_*.py",
        "simple_*.py",
        "minimal_*.py",
        "lite_*.py",
        "direct_*.py",
        "final_*.py",
        "corrected_*.py",
        "enhanced_*.py",
        "additional_*.py",
        "comprehensive_*.py",
        "complete_*.py",
        "absolute_*.py",
        "geometry_*.py",
        "height_*.py",
        "enforce_*.py",
        "ensure_*.py",
        "apply_*.py",
        "update_*.py",
        "window_*.py",
        "scaling_*.py",
        "anti_*.py",
        "accessibility_*.py",
        "ctk_*.py",
        "syntax_*.py",
        "validation_*.py",
        "launch_*.py",
        "start_*.py",
        "run_*.py",
        "safe_*.py",
        "START.py",
        "LAUNCH_*.py",
        "PRODUCTION_*.py",
        "COMPLETE_*.py",
        "MODERN_*.py",
        "ICON_*.py",
        "missing_*.py",
        "FEHLENDE_*.py",
        "dummy_*.py",
        "poppler_*.py",
        "premium_*.py",
        "fluent_icons_manager_*.py",
        "icon_demo.py",
        "icon_converter.py",
        "icon_customization_*.py",
        "icon_improvement_*.py",
        "icon_generator.py",
        "optimized_icon_*.py",
        "theme_*.py",
        "toolbar_*.py",
        "tooltip.py",
        "ctk_tooltip.py",
        "tool_config.py",
        "realtime_*.py",
        "ml_*.py",
        "performance_*.py",
        "smart_*.py",
        "keyboard_*.py",
        "drag_drop_*.py",
        "internationalization.py",
        "language_*.py",
        "workflow_refactoring_*.py",
        "workflow_integration_*.py",
        "workflow_orchestrator.py",
        "workflow_utils.py",
        "pdf_export.py",
        "generate_*.py",
        "export.py",
        "import_*.py",
        "ocr_*.py",
        "pruefung_workflow_controller_*.py",
        "memory_*.py",
        "thread_*.py",
        "state_*.py",
        "project_data_*.py",
        "app_logger.py",
        "error_handlers.py",
        "file_operations.py",
        "folder_*.py",
        "field_*.py",
        "config_manager.py",
        "button_manager.py",
        "cleanup_plan.py",
        "optimization_analyzer.py",
        "ui_optimization_*.py",
        "verbesserungsanalyse.py",
        "text_analyzer.py",
        "angebot_*.py",
        "angebots_*.py",
        "autocomplete_*.py",
        "base_ui_*.py",
        "enhanced_*.py",
        "advanced_*.py",
        "animation_*.py",
        "ui_animations.py",
        "modern_ui_enhancements.py",
        "workflow_manager.py",
        "animation_engine.py",
        "accessibility_extensions.py",
        "workflow_integration_optimizer.py",
        "pruefung_workflow_restored.py",
        "ultra_modern_welcome_screen_v2.py",
        "ultra_modern_welcome_screen_grid_only.py",
        "simple_welcome_screen.py",
        "simplified_checker.py",
        "ctkimage_*.py",
        "integration_test_*.py",
        "validation_*.py",
        "verification_*.py",
        "prüfung.py"
    ]
    
    # Dateien identifizieren und ins Backup verschieben
    files_to_backup = []
    for pattern in patterns_to_delete:
        matches = list(base_path.glob(pattern))
        files_to_backup.extend(matches)
    
    # Duplikate entfernen
    files_to_backup = list(set(files_to_backup))
    
    print(f"🔍 Gefundene Dateien zum Aufräumen: {len(files_to_backup)}")
    
    # Dateien ins Backup verschieben
    moved_count = 0
    for file_path in files_to_backup:
        if file_path.is_file():
            try:
                backup_file = backup_path / file_path.name
                # Wenn Backup-Datei bereits existiert, nummerieren
                counter = 1
                while backup_file.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    backup_file = backup_path / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(file_path), str(backup_file))
                moved_count += 1
                print(f"✅ Verschoben: {file_path.name}")
            except Exception as e:
                print(f"❌ Fehler beim Verschieben von {file_path.name}: {e}")
    
    print(f"\n🎉 Bereinigung abgeschlossen!")
    print(f"📦 {moved_count} Dateien ins Backup verschoben")
    print(f"📂 Backup-Ordner: {backup_path}")
    
    # Statistiken nach Bereinigung
    remaining_py_files = list(base_path.glob("*.py"))
    remaining_test_files = list(base_path.glob("test_*.py"))
    remaining_icon_files = list(base_path.glob("*icon*.py"))
    
    print(f"\n📊 NACH BEREINIGUNG:")
    print(f"🐍 Python-Dateien: {len(remaining_py_files)}")
    print(f"🧪 Test-Dateien: {len(remaining_test_files)}")
    print(f"🎨 Icon-Dateien: {len(remaining_icon_files)}")
    
    # Core-Dateien identifizieren, die bleiben sollten
    core_files = [
        "checker_app.py",
        "ui_theme.py",
        "modern_ui_components.py",
        "modern_animations.py",
        "advanced_visual_effects.py",
        "modern_dashboard.py",
        "gui_improvements_integration.py",
        "ultra_modern_welcome_screen_simplified.py",
        "test_modern_gui.py",
        "ki_module.py",
        "kunden_manager.py",
        "pruefung_workflow_controller.py",
        "pruefung_workflow.py",
        "projekt_workflow.py",
        "fluent_icons_manager.py",
        "icon_manager.py",
        "theme.py"
    ]
    
    print(f"\n🎯 EMPFOHLENE KERN-DATEIEN:")
    for core_file in core_files:
        if (base_path / core_file).exists():
            print(f"✅ {core_file}")
        else:
            print(f"❌ {core_file} - NICHT GEFUNDEN!")
    
    # Ordner-Struktur vorschlagen
    print(f"\n📁 EMPFOHLENE ORDNER-STRUKTUR:")
    suggested_structure = {
        "core/": ["checker_app.py", "ki_module.py", "kunden_manager.py"],
        "ui/": ["modern_ui_components.py", "ui_theme.py", "theme.py"],
        "animations/": ["modern_animations.py", "advanced_visual_effects.py"],
        "workflows/": ["pruefung_workflow.py", "projekt_workflow.py", "pruefung_workflow_controller.py"],
        "screens/": ["ultra_modern_welcome_screen_simplified.py", "modern_dashboard.py"],
        "icons/": ["fluent_icons_manager.py", "icon_manager.py"],
        "tests/": ["test_modern_gui.py"],
        "integration/": ["gui_improvements_integration.py"]
    }
    
    for folder, files in suggested_structure.items():
        print(f"📂 {folder}")
        for file in files:
            if (base_path / file).exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} - NICHT GEFUNDEN")
    
    return moved_count

if __name__ == "__main__":
    print("🧹 CHECKER PROJECT CLEANUP SCRIPT")
    print("=" * 50)
    
    # Sicherheitsabfrage
    response = input("\n⚠️  WARNUNG: Dieser Script wird viele Dateien verschieben!\n"
                    "Alle Dateien werden in einen Backup-Ordner verschoben.\n"
                    "Möchten Sie fortfahren? (ja/nein): ")
    
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        moved_count = cleanup_checker_project()
        print(f"\n🎉 Bereinigung erfolgreich abgeschlossen!")
        print(f"📦 {moved_count} Dateien wurden ins Backup verschoben.")
        print(f"\n💡 NÄCHSTE SCHRITTE:")
        print("1. Testen Sie die verbleibenden Dateien")
        print("2. Implementieren Sie die vorgeschlagene Ordner-Struktur")
        print("3. Teilen Sie große Dateien auf (besonders checker_app.py)")
        print("4. Konsolidieren Sie die verbleibenden Module")
    else:
        print("❌ Bereinigung abgebrochen.")
