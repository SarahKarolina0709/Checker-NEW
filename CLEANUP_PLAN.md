# Repo Cleanup Plan (Safe & Reversible)

Ziel: Unbenutzte/alte Python-Dateien sicher archivieren, ohne Funktionsverlust.

Schritte:

1. Analyse ausführen (bereits getan)

- python_files_cleanup_analysis.py → Kategorien
- comprehensive_duplicate_analysis.py → leere Dateien, exakte/ähnliche Duplikate

1. Sicheres Archivieren statt Löschen

- PowerShell: safe_archive_unused_files.ps1
- Verschiebt Kandidaten in ARCHIVE_UNUSED_PY_[timestamp]
- Optionaler Trockenlauf via -WhatIf

1. Kandidaten (erste Tranche)

- Leere Dateien (22): dark_professional_gui.py, demo_*.py, test_*.py, ultra_professional_gui.py, welcome_screen_components/header_section.py
- Exakte Duplikate: quality_gui_notifications_repaired.py (Original behalten: quality_gui_notifications.py)
- Backup/Altvarianten: welcome_screen.py.backup_*, welcome_screen_original.py

1. Nicht anfassen (kritisch):

- welcome_screen.py
- integrated_startup.py
- modern_translation_quality_gui.py
- design_system.py
- async_file_operations.py
- config.json / CRITICAL_FILES_REGISTRY.json / ui_theme.py

1. Nachlauf (optional):

- Weitere Demo-/Diagnose-Dateien prüfen: `test_*` / `diagnose_*` / `ui_components_showcase.py`
- Wenn keine Referenzen/Imports/Tasks → zweite Archiv-Tranche

Rollback:

- Dateien jederzeit aus Archiv-Ordner zurück verschiebbar.

Hinweis:

- Kein Dark Mode-Code reaktivieren (Policy)
- Keine Icons/Emojis in UI-Dateien einführen (Policy)
- Design-System-APIs bevorzugen
