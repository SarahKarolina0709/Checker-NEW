"""QUALITY GUI – Comprehensive Duplicate Analysis

Originale Implementierung von `comprehensive_duplicate_analysis.py` hierher
verschoben. Alte Datei dient nur noch als Wrapper.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import difflib
import re
from typing import List, Dict, Any

__all__ = [
    "ComprehensiveDuplicateAnalyzer",
]


class ComprehensiveDuplicateAnalyzer:
    """🔍 Umfassender Duplikat-Analyzer"""

    def __init__(self):
        self.all_files: List[Dict[str, Any]] = []
        self.analysis_results = {
            "exact_duplicates": [],
            "similar_files": [],
            "syntax_errors": [],
            "empty_files": [],
            "suspicious_files": [],
        }

    def analyze_all_python_files(self):
        print("🔍 Starte umfassende Duplikat-Analyse…")
        for root, dirs, files in os.walk('.'):
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    file_info = self._analyze_file(file_path)
                    if file_info:
                        self.all_files.append(file_info)
        print(f"📊 Gefunden: {len(self.all_files)} Python-Dateien")
        self._find_exact_duplicates()
        self._find_similar_files()
        self._find_syntax_issues()
        self._generate_duplicate_report()

    def _analyze_file(self, file_path: Path):
        try:
            file_size = file_path.stat().st_size
            file_size_kb = round(file_size / 1024, 2)
            content = None
            encoding_used = None
            lines = 0
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        encoding_used = encoding
                        break
                except Exception:
                    continue
            if content is None:
                return None
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            issues = self._check_syntax_issues(content)
            return {
                'name': file_path.name,
                'path': str(file_path),
                'relative_path': str(file_path.relative_to('.')),
                'folder': str(file_path.parent),
                'size_kb': file_size_kb,
                'lines': lines,
                'hash': file_hash,
                'content': content,
                'encoding': encoding_used,
                'is_empty': lines == 0,
                'has_syntax_issues': issues,
            }
        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")
            return None

    def _check_syntax_issues(self, content: str):
        issues = []
        if 'def ") -> ' in content or 'def ""):' in content:
            issues.append("Unvollständige Funktionsdefinition")
        if content.count('"""') % 2 != 0:
            issues.append("Ungeschlossene Docstrings")
        func_pattern = r'def\s+\w+\([^)]*\):\s*\n\s*$'
        if re.search(func_pattern, content, re.MULTILINE):
            issues.append("Leere Funktionen ohne pass")
        return issues

    def _find_exact_duplicates(self):
        hash_groups: Dict[str, list] = {}
        for file_info in self.all_files:
            if not file_info['is_empty']:
                hash_groups.setdefault(file_info['hash'], []).append(file_info)
        for files in hash_groups.values():
            if len(files) > 1:
                self.analysis_results['exact_duplicates'].append({
                    'hash': files[0]['hash'],
                    'files': files,
                    'size_kb': files[0]['size_kb'],
                    'lines': files[0]['lines'],
                })

    def _find_similar_files(self):
        for i, file1 in enumerate(self.all_files):
            if file1['is_empty'] or file1['lines'] < 10:
                continue
            for file2 in self.all_files[i + 1:]:
                if file2['is_empty'] or file2['lines'] < 10:
                    continue
                if file1['hash'] == file2['hash']:
                    continue
                similarity = self._calculate_similarity(file1['content'], file2['content'])
                if similarity > 0.8:
                    self.analysis_results['similar_files'].append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity,
                    })

    def _calculate_similarity(self, content1: str, content2: str):
        try:
            matcher = difflib.SequenceMatcher(None, content1.splitlines(), content2.splitlines())
            return matcher.ratio()
        except Exception:
            return 0.0

    def _find_syntax_issues(self):
        for file_info in self.all_files:
            if file_info['has_syntax_issues']:
                self.analysis_results['syntax_errors'].append(file_info)
            if file_info['is_empty']:
                self.analysis_results['empty_files'].append(file_info)

    def _generate_duplicate_report(self):
        exact_duplicates = self.analysis_results['exact_duplicates']
        similar_files = self.analysis_results['similar_files']
        syntax_errors = self.analysis_results['syntax_errors']
        empty_files = self.analysis_results['empty_files']
        print("\n📊 UMFASSENDE DUPLIKAT-ANALYSE:")
        print(f"   🔄 Exakte Duplikate: {len(exact_duplicates)} Gruppen")
        print(f"   📋 Ähnliche Dateien: {len(similar_files)} Paare")
        print(f"   ❌ Syntax-Probleme: {len(syntax_errors)} Dateien")
        print(f"   📭 Leere Dateien: {len(empty_files)} Dateien")
        if exact_duplicates:
            print("\n🔄 EXAKTE DUPLIKATE:")
            total_saveable = 0
            for i, group in enumerate(exact_duplicates, 1):
                files = group['files']
                print(f"\n   Gruppe {i} ({group['size_kb']} KB, {group['lines']} Zeilen):")
                for j, file_info in enumerate(files):
                    if j == 0:
                        print(f"      ✅ BEHALTEN: {file_info['relative_path']}")
                    else:
                        print(f"      ❌ LÖSCHEN:  {file_info['relative_path']}")
                        total_saveable += group['size_kb']
            print(f"\n   💾 Potentielle Einsparung: {total_saveable:.1f} KB")
        if similar_files:
            print("\n📋 ÄHNLICHE DATEIEN (>80% ähnlich):")
            for pair in similar_files:
                print(f"   📋 {pair['similarity'] * 100:.1f}% ähnlich:")
                print(f"      - {pair['file1']['relative_path']} ({file1['size_kb']} KB)")
                print(f"      - {pair['file2']['relative_path']} ({file2['size_kb']} KB)")
        if syntax_errors:
            print("\n❌ DATEIEN MIT SYNTAX-PROBLEMEN:")
            for file_info in syntax_errors:
                print(f"   ❌ {file_info['relative_path']}:")
                for issue in file_info['has_syntax_issues']:
                    print(f"      - {issue}")
        if empty_files:
            print("\n📭 LEERE DATEIEN:")
            for file_info in empty_files:
                print(f"   📭 {file_info['relative_path']} (0 Bytes)")
        self._generate_cleanup_commands()

    def _generate_cleanup_commands(self):
        exact_duplicates = self.analysis_results['exact_duplicates']
        empty_files = self.analysis_results['empty_files']
        syntax_errors = self.analysis_results['syntax_errors']
        print("\n🛠️ CLEANUP KOMMANDOS:")
        if empty_files:
            print(f"\n# Leere Dateien löschen ({len(empty_files)} Stück):")
            for file_info in empty_files:
                print(f"Remove-Item \"{file_info['relative_path']}\" -Force")
        if exact_duplicates:
            print("\n# Exakte Duplikate löschen (behalte ersten pro Gruppe):")
            for group in exact_duplicates:
                for i, file_info in enumerate(group['files']):
                    if i > 0:
                        print(f"Remove-Item \"{file_info['relative_path']}\" -Force")
        if syntax_errors:
            print("\n# Dateien mit Syntax-Problemen (MANUELL REPARIEREN):")
            for file_info in syntax_errors:
                print(f"# REPARIEREN: {file_info['relative_path']}")
                for issue in file_info['has_syntax_issues']:
                    print(f"#   Problem: {issue}")
        total_deletable = len(empty_files) + sum(len(g['files']) - 1 for g in exact_duplicates)
        total_files = len(self.all_files)
        if total_files:
            print("\n📊 CLEANUP POTENTIAL:")
            print(f"   📁 Automatisch löschbar: {total_deletable} von {total_files} Dateien ({total_deletable/total_files*100:.1f}%)")
            print(f"   🔧 Manuell zu reparieren: {len(syntax_errors)} Dateien")


def main():  # pragma: no cover
    print("🔍 COMPREHENSIVE DUPLICATE ANALYSIS")
    print("=" * 50)
    analyzer = ComprehensiveDuplicateAnalyzer()
    analyzer.analyze_all_python_files()
    print("\n✅ Umfassende Duplikat-Analyse abgeschlossen!")


if __name__ == "__main__":  # pragma: no cover
    main()
