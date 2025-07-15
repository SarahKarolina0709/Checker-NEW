#!/usr/bin/env python3
"""
Script zum Aktualisieren aller Importe von kunden_manager_v2 zu kunden_manager
"""

import os
import re
import glob

def update_imports_in_file(file_path):
    """Aktualisiert die Importe in einer einzelnen Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Ersetze Import-Statements
        content = re.sub(r'from kunden_manager_v2 import KundenManagerV2', 
                        'from kunden_manager import KundenManager', content)
        content = re.sub(r'import kunden_manager_v2', 
                        'import kunden_manager', content)
        
        # Ersetze Klassennamen
        content = re.sub(r'KundenManagerV2', 'KundenManager', content)
        
        # Ersetze Kommentare
        content = re.sub(r'KundenManagerV2', 'KundenManager', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {file_path}")
            return True
        else:
            print(f"- No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False

def main():
    """Hauptfunktion"""
    base_dir = os.getcwd()
    
    # Finde alle Python-Dateien
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and 'kunden_manager' not in file:
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check...")
    
    updated_count = 0
    for file_path in python_files:
        if update_imports_in_file(file_path):
            updated_count += 1
    
    print(f"\nSummary: Updated {updated_count} files")

if __name__ == "__main__":
    main()
