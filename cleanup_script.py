#!/usr/bin/env python3
'''
Checker App - Automatisches Cleanup Script
==========================================
ACHTUNG: Führen Sie dieses Script nur nach einem Backup aus!
'''

import os
import shutil
from pathlib import Path

def cleanup_checker_app():
    '''Räumt die Checker-App auf.'''
    
    # Temporäre und Backup-Dateien
    temp_patterns = [
        '*_old.py', '*_backup.py', '*_copy.py', '*_temp.py',
        '*_test.py.bak', '*.pyc', '__pycache__'
    ]
    
    # Debug-Dateien (nach Überprüfung)
    debug_files = [
        'debug_*.py', 'test_*.py'  # Nur nach Bestätigung
    ]
    
    print("🧹 Starte Cleanup...")
    
    # 1. Temporäre Dateien entfernen
    for pattern in temp_patterns:
        for file_path in Path('.').glob(pattern):
            print(f"❌ Entferne: {file_path}")
            # file_path.unlink()  # Auskommentiert für Sicherheit
    
    # 2. Leere Ordner entfernen
    for dir_path in Path('.').iterdir():
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            print(f"📁 Entferne leeren Ordner: {dir_path}")
            # dir_path.rmdir()  # Auskommentiert für Sicherheit
    
    print("✅ Cleanup abgeschlossen!")

if __name__ == "__main__":
    print("⚠️  WARNUNG: Dieses Script löscht Dateien!")
    print("   Erstellen Sie ein Backup vor der Ausführung!")
    # cleanup_checker_app()  # Auskommentiert für Sicherheit
