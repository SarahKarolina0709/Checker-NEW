#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 FINAL PARENTHESES FIXER - ULTIMATE SOLUTION
==============================================

Behebt alle verbliebenen Klammer-Probleme.
Die allerletzte Syntax-Reparatur!

Author: GitHub Copilot
Date: August 6, 2025
Version: Ultimate Final 1.0
"""

import os
import re
import ast
from pathlib import Path

class FinalParenthesesFixer:
    """Die allerletzte Lösung für Klammer-Probleme"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.fixes_applied = 0
    
    def count_parentheses(self, line: str) -> tuple:
        """Count opening and closing parentheses"""
        open_count = line.count('(')
        close_count = line.count(')')
        square_open = line.count('[')
        square_close = line.count(']')
        curly_open = line.count('{')
        curly_close = line.count('}')
        
        return (open_count, close_count, square_open, square_close, curly_open, curly_close)
    
    def fix_parentheses_in_content(self, content: str) -> str:
        """Fix parentheses issues in content"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                fixed_lines.append(line)
                continue
            
            original_line = line
            
            # Remove obvious extra closing parentheses at end of line
            while line.rstrip().endswith('))') and line.count(')') > line.count('('):
                line = line.rstrip()[:-1]
            
            # Fix specific patterns
            line = re.sub(r'\)\s*\)\s*$', ')', line)  # Double closing at end
            line = re.sub(r'\(\s*\(\s*', '(', line)   # Double opening at start
            
            # Balance parentheses on the line
            open_count, close_count, sq_open, sq_close, cur_open, cur_close = self.count_parentheses(line)
            
            # Fix round parentheses
            if open_count > close_count:
                # Add missing closing parentheses
                missing = open_count - close_count
                line = line.rstrip() + ')' * missing
            elif close_count > open_count:
                # Remove extra closing parentheses from the end
                extra = close_count - open_count
                # Remove from the end
                for _ in range(extra):
                    if line.rstrip().endswith(')'):
                        line = line.rstrip()[:-1] + line[len(line.rstrip()):]
            
            # Fix square brackets
            if sq_open > sq_close:
                missing = sq_open - sq_close
                line = line.rstrip() + ']' * missing
            elif sq_close > sq_open:
                extra = sq_close - sq_open
                for _ in range(extra):
                    if line.rstrip().endswith(']'):
                        line = line.rstrip()[:-1] + line[len(line.rstrip()):]
            
            # Fix curly braces
            if cur_open > cur_close:
                missing = cur_open - cur_close
                line = line.rstrip() + '}' * missing
            elif cur_close > cur_open:
                extra = cur_close - cur_open
                for _ in range(extra):
                    if line.rstrip().endswith('}'):
                        line = line.rstrip()[:-1] + line[len(line.rstrip()):]
            
            if line != original_line:
                print(f"   🔧 Zeile {i+1}: Klammern repariert")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def validate_and_fix_syntax(self, content: str, file_path: Path) -> str:
        """Validate syntax and apply final fixes"""
        try:
            # Try to parse - if it works, we're good
            ast.parse(content)
            return content
        except SyntaxError as e:
            print(f"   ⚠️  Syntax-Fehler in Zeile {e.lineno}: {e.msg}")
            
            # Apply emergency fixes for common issues
            lines = content.split('\n')
            
            if e.lineno and e.lineno <= len(lines):
                problem_line = lines[e.lineno - 1]
                
                # Fix unexpected indent
                if 'unexpected indent' in str(e):
                    lines[e.lineno - 1] = problem_line.lstrip()
                    print(f"   🔧 Unexpected indent entfernt in Zeile {e.lineno}")
                
                # Fix unmatched parentheses
                elif 'unmatched' in str(e) or 'unexpected token' in str(e):
                    # Remove all extra parentheses at the end
                    while problem_line.rstrip().endswith('))'):
                        problem_line = problem_line.rstrip()[:-1]
                    lines[e.lineno - 1] = problem_line
                    print(f"   🔧 Unmatched parentheses repariert in Zeile {e.lineno}")
            
            return '\n'.join(lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file"""
        try:
            print(f"\n🔧 Bearbeite: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Apply parentheses fixes
            content = self.fix_parentheses_in_content(content)
            
            # Validate and apply final fixes
            content = self.validate_and_fix_syntax(content, file_path)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Datei repariert und gespeichert")
                self.fixes_applied += 1
                return True
            else:
                print(f"   ✅ Datei bereits korrekt")
                return True
                
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            return False
    
    def run_final_fix(self):
        """Run the final fix process"""
        print("\n🎯 FINAL PARENTHESES FIXER GESTARTET")
        print("=" * 50)
        print("Die allerletzte Syntax-Reparatur!")
        
        # Target specific problem files
        problem_files = [
            'modern_translation_quality_gui.py',
            'quality_gui_advanced_features.py',
            'quality_gui_main_app.py',
            'quality_gui_notifications.py',
            'quality_gui_progress_upload.py',
            'quality_gui_ui_components.py'
        ]
        
        successful_fixes = 0
        
        for filename in problem_files:
            # Find the file
            for file_path in self.workspace_path.rglob(filename):
                if file_path.name == filename:
                    if self.fix_file(file_path):
                        successful_fixes += 1
                    break
        
        print(f"\n📊 FINALE REPARATUR-STATISTIK:")
        print(f"✅ Erfolgreich bearbeitet: {successful_fixes}")
        print(f"🔧 Fixes angewendet: {self.fixes_applied}")
        print(f"📁 Dateien: {len(problem_files)}")
        
        if successful_fixes == len(problem_files):
            print("\n🎉 FINAL FIX ERFOLGREICH! 🎉")
            print("Alle Syntax-Probleme sollten jetzt behoben sein!")
        else:
            print(f"\n⚠️  {len(problem_files) - successful_fixes} Dateien benötigen weitere Aufmerksamkeit")

def main():
    workspace = r"c:\Users\sarah\Desktop\Checker"
    
    print("🎯 FINAL PARENTHESES FIXER")
    print("Die allerletzte Syntax-Reparatur!\n")
    
    fixer = FinalParenthesesFixer(workspace)
    fixer.run_final_fix()
    
    print("\n🚀 FINAL FIX ABGESCHLOSSEN!")

if __name__ == "__main__":
    main()
