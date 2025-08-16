# Typography Backup Archivierung

Am 2025-08-08 wurden folgende Backup-/Emergency-Dateien logisch als archiviert markiert:

```text
modern_translation_quality_gui.py.backup_1754277014
modern_translation_quality_gui.py.emergency_backup
quality_gui_main_app.py.backup_colors
quality_gui_main_app.py.backup_typography
quality_gui_main_app.py.emergency_backup
quality_gui_main_app.py.emergency_backup_critical
quality_gui_notifications.py.emergency_backup
quality_gui_notifications_broken_backup.py
quality_gui_progress_upload.py.emergency_backup
quality_gui_ui_components.py.emergency_backup
welcome_screen.py.backup_20250723_105928
welcome_screen.py.backup_ultimate
```

Diese Dateien werden von der CI-Typografie-Analyse ignoriert (Namensmuster: `backup`, `.old`, `.orig`).

Optionale physische Verschiebung (lokal ausführen):

```powershell
New-Item -ItemType Directory -Force -Path ./archive/legacy_backups | Out-Null
Get-ChildItem -Path . -File -Filter *backup* | ForEach-Object { Move-Item $_.FullName ./archive/legacy_backups -Force }
```

Nach erfolgreichem Entfernen des Deprecation-Mappings wird ein Lock-File `TYPOGRAPHY_GOVERNANCE_LOCKED.md` ergänzt.
