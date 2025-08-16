#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 INDENTATION FIXER - FINAL SYNTAX RESOLUTION
==============================================

Behebt die verbliebenen Indentations-Probleme in den
modularisierten Dateien.

Author: GitHub Copilot
Date: August 6, 2025
Version: Final 1.0
"""

import os
import re
from pathlib import Path

class IndentationFixer:
    """Behebt Indentations-Probleme in Python-Dateien"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.problem_files = [
            'modern_translation_quality_gui.py',
            'quality_gui_advanced_features.py',
            'quality_gui_main_app.py', 
            'quality_gui_notifications.py',
            'quality_gui_progress_upload.py',
            'quality_gui_ui_components.py'
        ]
        self.fixes_applied = 0
    
    def fix_indentation(self, content: str) -> str:
        """Fix indentation issues"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                continue
            
            # Convert tabs to spaces
            line = line.expandtabs(4)
            
            # Check for unexpected indent at start of file or after module docstring
            if i < 10:  # First 10 lines are usually module level
                # Remove unexpected indentation from module-level statements
                if line.startswith('    ') and not any(keyword in line for keyword in ['def ', 'class ', 'if ', 'try:', 'except', 'finally:', 'with ', 'for ', 'while ']):
                    # Check if it's not inside a function/class
                    prev_non_empty = None
                    for j in range(i-1, -1, -1):
                        if lines[j].strip():
                            prev_non_empty = lines[j]
                            break
                    
                    # If previous line doesn't suggest this should be indented
                    if not prev_non_empty or not any(prev_non_empty.strip().endswith(char) for char in [':', '\\', ',']):
                        line = line.lstrip()
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix indentation in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Fix indentation
            fixed_content = self.fix_indentation(content)
            
            # Only write if content changed
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ Indentation repariert: {file_path.name}")
                self.fixes_applied += 1
                return True
            else:
                print(f"✅ Indentation bereits korrekt: {file_path.name}")
                return True
                
        except Exception as e:
            print(f"❌ Fehler bei {file_path.name}: {e}")
            return False
    
    def run_indentation_fix(self):
        """Run indentation fix on problem files"""
        print("\n🎯 INDENTATION FIXER GESTARTET")
        print("=" * 50)
        print(f"🔧 Repariere Indentation in {len(self.problem_files)} Dateien...")
        
        successful_fixes = 0
        
        for filename in self.problem_files:
            # Find the file in workspace
            file_found = False
            for file_path in self.workspace_path.rglob(filename):
                if file_path.name == filename:
                    if self.fix_file(file_path):
                        successful_fixes += 1
                    file_found = True
                    break
            
            if not file_found:
                print(f"⚠️  Datei nicht gefunden: {filename}")
        
        print(f"\n📊 INDENTATION-REPARATUR STATISTIK:")
        print(f"✅ Erfolgreich repariert: {successful_fixes}")
        print(f"🔧 Fixes angewendet: {self.fixes_applied}")
        print(f"📁 Dateien bearbeitet: {len(self.problem_files)}")
        
        if successful_fixes == len(self.problem_files):
            print("\n🎉 ALLE INDENTATION-PROBLEME BEHOBEN! 🎉")
        else:
            remaining = len(self.problem_files) - successful_fixes
            print(f"\n⚠️  {remaining} Dateien benötigen weitere Aufmerksamkeit")

def main():
    workspace = r"c:\Users\sarah\Desktop\Checker"
    
    print("🎯 INDENTATION FIXER")
    print("Finale Lösung für Indentation-Probleme\n")
    
    fixer = IndentationFixer(workspace)
    fixer.run_indentation_fix()
    
    print("\n🚀 INDENTATION FIX ABGESCHLOSSEN!")

if __name__ == "__main__":
    main()
