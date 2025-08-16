#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 UTILS FOLDERS CLEANUP ANALYSIS
=================================

Spezialisierte Analyse aller utils-Ordner und deren Inhalte
zur Identifikation von redundanten, leeren oder doppelten Dateien.
"""


from pathlib import Path
import hashlib

class UtilsCleanupAnalyzer:
    """🔧 Utils-Ordner Cleanup Analyzer"""

    def __init__(self):
        self.utils_folders = [
            'utils',
            'src/utils',
            'src\\utils',
            'core/utils',
            'core\\utils',
            'app_managers',
            'ui_components'
        ]

        self.analysis_results = {
            'empty_files': [],
            'duplicate_files': [],
            'small_files': [],
            'large_files': [],
            'functional_files': []
        }

    def analyze_all_utils(self):
        """🔍 Analysiere alle utils-Ordner"""
        print("🔧 Starte Utils-Ordner-Analyse...")

        all_files = []

        # Sammle alle Python-Dateien aus utils-Ordnern
        for utils_folder in self.utils_folders:
            utils_path = Path(utils_folder)
            if utils_path.exists():
                print(f"📁 Analysiere: {utils_folder}")

                for py_file in utils_path.glob('*.py'):
                    file_info = self._analyze_file(py_file)
                    if file_info:
                        all_files.append(file_info)

        print(f"📊 Gefunden: {len(all_files)} Python-Dateien in utils-Ordnern")

        # Kategorisiere Dateien
        for file_info in all_files:
            self._categorize_file(file_info)

        # Finde Duplikate
        self._find_duplicates(all_files)

        # Generate Report
        self._generate_utils_report()

    def _analyze_file(self, file_path):
        """🔍 Analysiere eine einzelne Datei"""
        try:
            file_size = file_path.stat().st_size
            file_size_kb = round(file_size / 1024, 2)

            # Zeilen zählen
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
            except:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        lines = len(f.readlines())
                except:
                    lines = 0

            # Hash für Duplikat-Erkennung
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except:
                file_hash = None

            return {
                'name': file_path.name,
                'path': str(file_path),
                'folder': str(file_path.parent),
                'size_kb': file_size_kb,
                'lines': lines,
                'hash': file_hash,
                'is_empty': lines == 0
            }

        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")
            return None

    def _categorize_file(self, file_info):
        """📂 Kategorisiere Datei"""

        # Leere Dateien
        if file_info['is_empty']:
            self.analysis_results['empty_files'].append(file_info)
            return

        # Sehr kleine Dateien (unter 1 KB)
        if file_info['size_kb'] < 1:
            self.analysis_results['small_files'].append(file_info)
            return

        # Große Dateien (über 10 KB)
        if file_info['size_kb'] > 10:
            self.analysis_results['large_files'].append(file_info)
            return

        # Funktionale Dateien
        self.analysis_results['functional_files'].append(file_info)

    def _find_duplicates(self, all_files):
        """🔍 Finde doppelte Dateien basierend auf Hash"""

        hash_groups = {}

        for file_info in all_files:
            if file_info['hash'] and not file_info['is_empty']:
                file_hash = file_info['hash']

                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []

                hash_groups[file_hash].append(file_info)

        # Finde Gruppen mit mehr als einer Datei (Duplikate)
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                self.analysis_results['duplicate_files'].append({
                    'hash': file_hash,
                    'files': files,
                    'size_kb': files[0]['size_kb'],
                    'lines': files[0]['lines']
                })

    def _generate_utils_report(self):
        """📄 Generiere Utils-Cleanup-Report"""

        print(f"\n📊 UTILS-ORDNER ANALYSE-ERGEBNISSE:")

        empty_files = self.analysis_results['empty_files']
        duplicate_groups = self.analysis_results['duplicate_files']
        small_files = self.analysis_results['small_files']
        large_files = self.analysis_results['large_files']
        functional_files = self.analysis_results['functional_files']

        print(f"   📭 Leere Dateien: {len(empty_files)}")
        print(f"   🔄 Duplikat-Gruppen: {len(duplicate_groups)}")
        print(f"   📄 Kleine Dateien: {len(small_files)}")
        print(f"   📦 Große Dateien: {len(large_files)}")
        print(f"   ✅ Funktionale Dateien: {len(functional_files)}")

        # Detaillierte Ausgabe
        print(f"\n🗑️ CLEANUP EMPFEHLUNGEN:")

        # Leere Dateien
        if empty_files:
            print(f"\n📭 LEERE DATEIEN (SOFORT LÖSCHEN):")
            for file_info in empty_files:
                print(f"   ❌ {file_info['path']} (0 Bytes)")

        # Duplikate
        if duplicate_groups:
            print(f"\n🔄 DUPLIKATE (EINES PRO GRUPPE LÖSCHEN):")
            total_saveable = 0
            for group in duplicate_groups:
                files = group['files']
                print(f"\n   🔄 Duplikat-Gruppe ({group['size_kb']} KB, {group['lines']} Zeilen):")
                for i, file_info in enumerate(files):
                    if i == 0:
                        print(f"      ✅ BEHALTEN: {file_info['path']}")
                    else:
                        print(f"      ❌ LÖSCHEN:  {file_info['path']}")
                        total_saveable += group['size_kb']

            print(f"\n   💾 Potentielle Einsparung durch Duplikat-Entfernung: {total_saveable:.1f} KB")

        # Kleine Dateien prüfen
        if small_files:
            print(f"\n📄 KLEINE DATEIEN (PRÜFEN OB NOTWENDIG):")
            for file_info in small_files:
                print(f"   ⚠️ {file_info['path']} ({file_info['size_kb']} KB, {file_info['lines']} Zeilen)")

        # Große Dateien analysieren
        if large_files:
            print(f"\n📦 GROSSE DATEIEN (ANALYSIEREN):")
            for file_info in large_files:
                print(f"   📦 {file_info['path']} ({file_info['size_kb']} KB, {file_info['lines']} Zeilen)")

        # Funktionale Dateien
        if functional_files:
            print(f"\n✅ FUNKTIONALE DATEIEN (BEHALTEN):")
            for file_info in functional_files:
                print(f"   ✅ {file_info['path']} ({file_info['size_kb']} KB, {file_info['lines']} Zeilen)")

        # Cleanup-Kommandos generieren
        self._generate_cleanup_commands()

    def _generate_cleanup_commands(self):
        """🛠️ Generiere Cleanup-Kommandos"""

        print(f"\n🛠️ CLEANUP KOMMANDOS:")

        empty_files = self.analysis_results['empty_files']
        duplicate_groups = self.analysis_results['duplicate_files']

        # Leere Dateien löschen
        if empty_files:
            print(f"\n# Leere Dateien löschen ({len(empty_files)} Stück):")
            for file_info in empty_files:
                print(f"Remove-Item \"{file_info['path']}\" -Force")

        # Duplikate löschen (behalte ersten, lösche Rest)
        if duplicate_groups:
            print(f"\n# Duplikate löschen (behalte ersten pro Gruppe):")
            for group in duplicate_groups:
                files = group['files']
                for i, file_info in enumerate(files):
                    if i > 0:  # Behalte ersten (i=0), lösche Rest
                        print(f"Remove-Item \"{file_info['path']}\" -Force")

        # Statistik
        total_deletable = len(empty_files) + sum(len(group['files']) - 1 for group in duplicate_groups)
        total_files = (len(empty_files) + len(duplicate_groups) +
                      len(self.analysis_results['small_files']) +
                      len(self.analysis_results['large_files']) +
                      len(self.analysis_results['functional_files']))

        if total_files > 0:
            print(f"\n📊 CLEANUP POTENTIAL:")
            print(f"   📁 Löschbar: {total_deletable} von {total_files} Dateien ({total_deletable/total_files*100:.1f}%)")

if __name__ == "__main__":
    print("🔧 UTILS FOLDERS CLEANUP ANALYSIS")
    print("=" * 50)

    analyzer = UtilsCleanupAnalyzer()
    analyzer.analyze_all_utils()

    print("\n✅ Utils-Analyse abgeschlossen!")