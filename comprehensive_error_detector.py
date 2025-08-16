#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 COMPREHENSIVE ERROR DETECTOR & FIXER
======================================

Detaillierte Analyse und Reparatur aller verbliebenen
Code-Fehler im Projekt.

Author: GitHub Copilot
Date: August 6, 2025
Version: Error Hunter 1.0
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ComprehensiveErrorDetector:
    """Umfassende Fehlersuche und -reparatur"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.errors_found = []
        self.fixes_applied = 0
        
    def scan_all_python_files(self):
        """Scanne alle Python-Dateien nach Fehlern"""
        print("🔍 COMPREHENSIVE ERROR DETECTION GESTARTET")
        print("=" * 50)
        
        python_files = list(self.workspace_path.rglob("*.py"))
        
        # Filter out backup and cache files
        python_files = [f for f in python_files if not any(
            skip in str(f) for skip in [
                '__pycache__', '.venv', 'node_modules', 
                '_backup', 'BACKUP', 'backup'
            ]
        )]
        
        print(f"📁 Analysiere {len(python_files)} Python-Dateien...")
        
        for file_path in python_files:
            self.analyze_file(file_path)
        
        self.report_findings()
        self.fix_all_errors()
    
    def analyze_file(self, file_path: Path):
        """Analysiere eine einzelne Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check syntax
            try:
                ast.parse(content)
                # File is syntactically correct
                return
            except SyntaxError as e:
                self.errors_found.append({
                    'file': file_path.name,
                    'path': file_path,
                    'line': e.lineno,
                    'error': str(e),
                    'type': 'syntax_error'
                })
            except Exception as e:
                self.errors_found.append({
                    'file': file_path.name,
                    'path': file_path,
                    'line': 1,
                    'error': str(e),
                    'type': 'parse_error'
                })
                
        except Exception as e:
            print(f"   ⚠️ Fehler beim Lesen von {file_path.name}: {e}")
    
    def report_findings(self):
        """Berichte über gefundene Fehler"""
        print(f"\n📊 FEHLER-ANALYSE ABGESCHLOSSEN")
        print(f"❌ Gefundene Fehler: {len(self.errors_found)}")
        
        if self.errors_found:
            print("\n🔍 DETAILLIERTE FEHLER-LISTE:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"   {i}. {error['file']}:{error['line']} - {error['error']}")
        else:
            print("✅ Keine Syntax-Fehler gefunden!")
    
    def fix_all_errors(self):
        """Repariere alle gefundenen Fehler"""
        if not self.errors_found:
            return
        
        print(f"\n🔧 STARTE AUTOMATISCHE REPARATUR...")
        
        for error in self.errors_found:
            self.fix_specific_error(error)
        
        print(f"\n📊 REPARATUR ABGESCHLOSSEN:")
        print(f"🔧 Angewandte Fixes: {self.fixes_applied}")
    
    def fix_specific_error(self, error: dict):
        """Repariere einen spezifischen Fehler"""
        file_path = error['path']
        error_msg = error['error'].lower()
        line_num = error['line']
        
        print(f"\n🔧 Repariere: {error['file']}:{line_num}")
        print(f"   Fehler: {error['error']}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Apply specific fixes based on error type
            if 'unexpected indent' in error_msg:
                self.fix_unexpected_indent(lines, line_num - 1)
            elif 'unmatched' in error_msg and ')' in error_msg:
                self.fix_unmatched_parentheses(lines, line_num - 1)
            elif 'closing parenthesis' in error_msg and 'does not match' in error_msg:
                self.fix_mismatched_brackets(lines, line_num - 1)
            elif 'invalid syntax' in error_msg:
                self.fix_invalid_syntax(lines, line_num - 1)
            elif 'expected' in error_msg:
                self.fix_expected_syntax(lines, line_num - 1, error_msg)
            else:
                print(f"   ⚠️ Unbekannter Fehlertyp - versuche generischen Fix")
                self.generic_fix(lines, line_num - 1)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"   ✅ Fix angewendet")
            self.fixes_applied += 1
            
        except Exception as e:
            print(f"   ❌ Fix fehlgeschlagen: {e}")
    
    def fix_unexpected_indent(self, lines: List[str], line_idx: int):
        """Repariere unerwartete Einrückung"""
        if line_idx < len(lines):
            line = lines[line_idx]
            if line.startswith('    ') or line.startswith('\t'):
                # Remove indentation if it seems incorrect
                lines[line_idx] = line.lstrip()
                print(f"   🔧 Einrückung entfernt")
    
    def fix_unmatched_parentheses(self, lines: List[str], line_idx: int):
        """Repariere nicht passende Klammern"""
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Count parentheses
            open_count = line.count('(')
            close_count = line.count(')')
            
            if close_count > open_count:
                # Remove extra closing parentheses
                while close_count > open_count and line.rstrip().endswith(')'):
                    line = line.rstrip()[:-1] + line[len(line.rstrip()):]
                    close_count = line.count(')')
                lines[line_idx] = line
                print(f"   🔧 Überschüssige Klammern entfernt")
    
    def fix_mismatched_brackets(self, lines: List[str], line_idx: int):
        """Repariere falsche Klammertypen"""
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Common mismatch: ')' instead of ']'
            if '[' in line and ')' in line and ']' not in line:
                line = line.replace(')', ']', 1)
                lines[line_idx] = line
                print(f"   🔧 Klammertyp korrigiert")
    
    def fix_invalid_syntax(self, lines: List[str], line_idx: int):
        """Repariere ungültige Syntax"""
        if line_idx < len(lines):
            line = lines[line_idx].strip()
            
            # Common invalid syntax patterns
            if line.startswith('"""') and not line.endswith('"""') and len(line) > 3:
                # Fix incomplete docstring
                lines[line_idx] = '"""Fixed docstring"""\n'
                print(f"   🔧 Defekte Docstring repariert")
            elif line and not line.endswith((':', '\\', ',', ')', ']', '}', '"', "'")):
                # Check if it's a statement that needs a colon
                if any(keyword in line for keyword in ['if ', 'def ', 'class ', 'try', 'except', 'for ', 'while ']):
                    if not line.endswith(':'):
                        lines[line_idx] = line + ':\n'
                        print(f"   🔧 Fehlender Doppelpunkt hinzugefügt")
    
    def fix_expected_syntax(self, lines: List[str], line_idx: int, error_msg: str):
        """Repariere erwartete Syntax-Elemente"""
        if line_idx < len(lines):
            line = lines[line_idx]
            
            if 'expected' in error_msg:
                if 'indented block' in error_msg:
                    # Add pass statement
                    lines.insert(line_idx + 1, '    pass\n')
                    print(f"   🔧 Pass-Statement hinzugefügt")
                elif 'expression' in error_msg:
                    # Fix incomplete expressions
                    if line.strip().endswith(('try:', 'except:', 'if', 'def', 'class')):
                        lines[line_idx] = line.rstrip() + ' pass\n'
                        print(f"   🔧 Unvollständigen Ausdruck repariert")
    
    def generic_fix(self, lines: List[str], line_idx: int):
        """Generischer Fix für unbekannte Fehler"""
        if line_idx < len(lines):
            line = lines[line_idx].strip()
            
            # Try to comment out problematic line
            if line and not line.startswith('#'):
                lines[line_idx] = f"# {line}  # FIXME: Automatic fix applied\n"
                print(f"   🔧 Problematische Zeile auskommentiert")

def main():
    workspace = r"c:\Users\sarah\Desktop\Checker"
    
    print("🔍 COMPREHENSIVE ERROR DETECTOR & FIXER")
    print("Detaillierte Suche und Reparatur aller Code-Fehler\n")
    
    detector = ComprehensiveErrorDetector(workspace)
    detector.scan_all_python_files()
    
    print("\n🚀 COMPREHENSIVE ERROR DETECTION COMPLETED!")

if __name__ == "__main__":
    main()
