#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 COMPREHENSIVE DUPLICATE ANALYSIS
===================================

Vollständige Analyse ALLER Python-Dateien im Projekt
zur Identifikation von Duplikaten, ähnlichen Dateien und redundanten Code-Blöcken.
"""

from pathlib import Path
import hashlib
import os

import difflib

class ComprehensiveDuplicateAnalyzer:
    """🔍 Umfassender Duplikat-Analyzer"""

    def __init__(self):
        self.all_files = []
        self.analysis_results = {
            'exact_duplicates': [],
            'similar_files': [],
            'syntax_errors': [],
            'empty_files': [],
            'suspicious_files': []
        }

    def analyze_all_python_files(self):
        """🔍 Analysiere ALLE Python-Dateien im Projekt"""
        print("🔍 Starte umfassende Duplikat-Analyse...")

        # Sammle ALLE Python-Dateien
        for root, dirs, files in os.walk('.'):
            # Skip .git
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    file_info = self._analyze_file(file_path)
                    if file_info:
                        self.all_files.append(file_info)

        print(f"📊 Gefunden: {len(self.all_files)} Python-Dateien")

        # Finde exakte Duplikate
        self._find_exact_duplicates()

        # Finde ähnliche Dateien
        self._find_similar_files()

        # Finde Syntax-Probleme
        self._find_syntax_issues()

        # Generate Report
        self._generate_duplicate_report()

    def _analyze_file(self, file_path):
        """🔍 Analysiere eine einzelne Datei"""
        try:
            file_size = file_path.stat().st_size
            file_size_kb = round(file_size / 1024, 2)

            # Versuche Datei zu lesen
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
                except:
                    continue

            if content is None:
                return None

            # Hash für Duplikat-Erkennung
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            # Prüfe auf Syntax-Probleme
            has_syntax_issues = self._check_syntax_issues(content, file_path.name)

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
                'has_syntax_issues': has_syntax_issues
            }

        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")
            return None

    def _check_syntax_issues(self, content, filename):
        """🔍 Prüfe auf Syntax-Probleme"""
        issues = []

        # Prüfe auf unvollständige Funktionsdefinitionen
        if 'def ") -> ' in content or 'def ""):' in content:
            issues.append("Unvollständige Funktionsdefinition")

        # Prüfe auf ungeschlossene Strings
        if content.count('"""') % 2 != 0:
            issues.append("Ungeschlossene Docstrings")

        # Prüfe auf leere Funktionen ohne pass
        import re
        func_pattern = r'def\s+\w+\([^)]*\):\s*\n\s*$'
        if re.search(func_pattern, content, re.MULTILINE):
            issues.append("Leere Funktionen ohne pass")

        return issues

    def _find_exact_duplicates(self):
        """🔍 Finde exakte Duplikate basierend auf Hash"""
        hash_groups = {}

        for file_info in self.all_files:
            if not file_info['is_empty']:
                file_hash = file_info['hash']

                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []

                hash_groups[file_hash].append(file_info)

        # Finde Gruppen mit mehr als einer Datei
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                self.analysis_results['exact_duplicates'].append({
                    'hash': file_hash,
                    'files': files,
                    'size_kb': files[0]['size_kb'],
                    'lines': files[0]['lines']
                })

    def _find_similar_files(self):
        """🔍 Finde ähnliche Dateien (nicht exakte Duplikate)"""

        # Vergleiche Dateien paarweise
        for i, file1 in enumerate(self.all_files):
            if file1['is_empty'] or file1['lines'] < 10:
                continue

            for j, file2 in enumerate(self.all_files[i+1:], i+1):
                if file2['is_empty'] or file2['lines'] < 10:
                    continue

                # Skip wenn bereits exakte Duplikate
                if file1['hash'] == file2['hash']:
                    continue

                # Berechne Ähnlichkeit
                similarity = self._calculate_similarity(file1['content'], file2['content'])

                if similarity > 0.8:  # 80% ähnlich
                    self.analysis_results['similar_files'].append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity
                    })

    def _calculate_similarity(self, content1, content2):
        """📊 Berechne Ähnlichkeit zwischen zwei Dateien"""
        try:
            lines1 = content1.splitlines()
            lines2 = content2.splitlines()

            # Verwende SequenceMatcher für Ähnlichkeitsberechnung
            matcher = difflib.SequenceMatcher(None, lines1, lines2)
            return matcher.ratio()
        except:
            return 0.0

    def _find_syntax_issues(self):
        """🔍 Finde Dateien mit Syntax-Problemen"""
        for file_info in self.all_files:
            if file_info['has_syntax_issues']:
                self.analysis_results['syntax_errors'].append(file_info)

            if file_info['is_empty']:
                self.analysis_results['empty_files'].append(file_info)

    def _generate_duplicate_report(self):
        """📄 Generiere umfassenden Duplikat-Report"""

        print(f"\n📊 UMFASSENDE DUPLIKAT-ANALYSE:")

        exact_duplicates = self.analysis_results['exact_duplicates']
        similar_files = self.analysis_results['similar_files']
        syntax_errors = self.analysis_results['syntax_errors']
        empty_files = self.analysis_results['empty_files']

        print(f"   🔄 Exakte Duplikate: {len(exact_duplicates)} Gruppen")
        print(f"   📋 Ähnliche Dateien: {len(similar_files)} Paare")
        print(f"   ❌ Syntax-Probleme: {len(syntax_errors)} Dateien")
        print(f"   📭 Leere Dateien: {len(empty_files)} Dateien")

        # Detaillierte Ausgabe
        print(f"\n🔍 DETAILLIERTE ANALYSE:")

        # Exakte Duplikate
        if exact_duplicates:
            print(f"\n🔄 EXAKTE DUPLIKATE:")
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

        # Ähnliche Dateien
        if similar_files:
            print(f"\n📋 ÄHNLICHE DATEIEN (>80% ähnlich):")
            for pair in similar_files:
                similarity_percent = pair['similarity'] * 100
                print(f"   📋 {similarity_percent:.1f}% ähnlich:")
                print(f"      - {pair['file1']['relative_path']} ({pair['file1']['size_kb']} KB)")
                print(f"      - {pair['file2']['relative_path']} ({pair['file2']['size_kb']} KB)")

        # Syntax-Probleme
        if syntax_errors:
            print(f"\n❌ DATEIEN MIT SYNTAX-PROBLEMEN:")
            for file_info in syntax_errors:
                print(f"   ❌ {file_info['relative_path']}:")
                for issue in file_info['has_syntax_issues']:
                    print(f"      - {issue}")

        # Leere Dateien
        if empty_files:
            print(f"\n📭 LEERE DATEIEN:")
            for file_info in empty_files:
                print(f"   📭 {file_info['relative_path']} (0 Bytes)")

        # Cleanup-Kommandos generieren
        self._generate_cleanup_commands()

    def _generate_cleanup_commands(self):
        """🛠️ Generiere Cleanup-Kommandos"""

        print(f"\n🛠️ CLEANUP KOMMANDOS:")

        exact_duplicates = self.analysis_results['exact_duplicates']
        empty_files = self.analysis_results['empty_files']
        syntax_errors = self.analysis_results['syntax_errors']

        # Leere Dateien löschen
        if empty_files:
            print(f"\n# Leere Dateien löschen ({len(empty_files)} Stück):")
            for file_info in empty_files:
                print(f"Remove-Item \"{file_info['relative_path']}\" -Force")

        # Exakte Duplikate löschen
        if exact_duplicates:
            print(f"\n# Exakte Duplikate löschen (behalte ersten pro Gruppe):")
            for group in exact_duplicates:
                files = group['files']
                for i, file_info in enumerate(files):
                    if i > 0:  # Behalte ersten, lösche Rest
                        print(f"Remove-Item \"{file_info['relative_path']}\" -Force")

        # Syntax-Probleme reparieren
        if syntax_errors:
            print(f"\n# Dateien mit Syntax-Problemen (MANUELL REPARIEREN):")
            for file_info in syntax_errors:
                print(f"# REPARIEREN: {file_info['relative_path']}")
                for issue in file_info['has_syntax_issues']:
                    print(f"#   Problem: {issue}")

        # Statistik
        total_deletable = len(empty_files) + sum(len(group['files']) - 1 for group in exact_duplicates)
        total_files = len(self.all_files)

        if total_files > 0:
            print(f"\n📊 CLEANUP POTENTIAL:")
            print(f"   📁 Automatisch löschbar: {total_deletable} von {total_files} Dateien ({total_deletable/total_files*100:.1f}%)")
            print(f"   🔧 Manuell zu reparieren: {len(syntax_errors)} Dateien")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE DUPLICATE ANALYSIS")
    print("=" * 50)

    analyzer = ComprehensiveDuplicateAnalyzer()
    analyzer.analyze_all_python_files()

    print("\n✅ Umfassende Duplikat-Analyse abgeschlossen!")