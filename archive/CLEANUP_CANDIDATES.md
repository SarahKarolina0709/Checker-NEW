# 🗑️ Aggressive Projekt-Bereinigung: Kandidatenliste

## Phase 1: Analyse und Kategorisierung

Basierend auf der vollständigen Dateiliste des Projekts wurden alle Dateien analysiert und in drei Kategorien eingeteilt: **Löschen**, **Archivieren** und **Behalten**.

---

## 🗑️ Kategorie 1: ZU LÖSCHEN (150+ Dateien)

Diese Dateien sind veraltet, redundant oder generierte Artefakte. Sie können sicher entfernt werden, um das Projekt zu bereinigen.

### Backup-Dateien:
- `checker_app_BACKUP_20250713_023925.py`
- `checker_app_broken_backup.py`
- `ctk_patch.py.old`
- `upload_section_backup.py`
- `ultra_modern_welcome_screen_simplified.py.backup`

### Veraltete und Test-Skripte:
- `accessibility_extensions.py`
- `advanced_accessibility.py`
- `advanced_gui_optimizer.py`
- `advanced_performance_monitor.py`
- `advanced_search_system.py`
- `advanced_visual_effects.py`
- `analyze_dependencies.py`
- `analyze_duplicates.py`
- `analyze_duplicate_files.py`
- `animation_engine.py`
- `base_ui_components.py`
- `basispfad_konfigurator.py`
- `calendar_cleanup_summary.py`
- `calendar_demo.py`
- `calendar_extensions.py`
- `calendar_fix_analysis.py`
- `check_pdf2image.py`
- `check_tkinterdnd.py`
- `cleanup_customer_files.py`
- `cleanup_script.py`
- `cleanup_script_automated.py`
- `create_demo_customers.py`
- `final_*.py` (alle 15+ Dateien)
- `test_*.py` (alle 50+ einzelnen Testdateien im Hauptverzeichnis)
- `debug_*.py` (alle 7 Dateien)
- `demo_*.py` (alle 8 Dateien)
- ... und viele weitere einzelne Skripte.

### Log- und Ergebnis-Dateien:
- `*.log` (alle, z.B. `checker_app.log`, `icon_debug.log`)
- `*.txt` (Test-Ergebnisse, z.B. `analyzer_test_results.txt`)
- `pylint_results*.txt`
- `coverage.xml`, `.coverage`

### Generierte Verzeichnisse:
- `__pycache__/` (im gesamten Projekt)
- `htmlcov/`

---

## 🗄️ Kategorie 2: ZU ARCHIVIEREN (100+ Dateien)

Diese Dateien enthalten wertvolle Informationen über den Entwicklungsprozess und sollten in ein `archive/` Verzeichnis verschoben werden.

### Markdown-Dokumentation (`.md`):
- `ACTION_BUTTONS_SUMMARY.md`
- `ADVANCED_IMPROVEMENT_ANALYSIS.md`
- `BEREINIGUNG_ABGESCHLOSSEN.md`
- `CHECKER_APP_REFACTORING_PLAN.md`
- `COMPLETE_IMPROVEMENT_SUMMARY.md`
- `DEPENDENCY_ANALYSIS.md`
- `FINAL_PROJECT_DOCUMENTATION.md`
- `OPTIMIERUNGSPLAN.md`
- ... und alle anderen `.md` Dateien.

---

## ✅ Kategorie 3: ZU BEHALTEN (Kern-Anwendung)

Dies sind die finalen, bereinigten Dateien, die für die Ausführung der Anwendung notwendig sind.

### Kern-Anwendung:
- `checker_app.py`
- `main.py` (falls vorhanden als Haupteinstiegspunkt)
- `requirements.txt`
- `START_CHECKER.bat`, `START_CHECKER.ps1`

### Module und Konfiguration:
- `src/` (das gesamte Verzeichnis mit der neuen modularen Struktur)
- `kunden_manager.py`
- `view_stack.py`
- `ui_theme.py`
- `config.json`, `themes.json`, `kunden_config.json`

### Externe Abhängigkeiten und Ressourcen:
- `assets/`
- `icons/`
- `poppler/`
- `tesseract/`
- `tests/` (das Verzeichnis mit den strukturierten Unit- und Integrationstests)

---

## 🚀 Nächster Schritt

Sollen wir basierend auf dieser Analyse fortfahren und die Bereinigungs-Befehle vorbereiten, um die identifizierten Dateien zu löschen und zu archivieren?
