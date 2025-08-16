#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗂️ DEEP FOLDER ANALYSIS - ALLE UNTERORDNER
==========================================

Tiefgehende Analyse ALLER Ordner und Unterordner im Checker-Projekt
zur Identifikation versteckter redundanter Strukturen.
"""

from pathlib import Path
import os

class DeepFolderAnalyzer:
    """Tiefgehende Ordner-Analyse"""

    def __init__(self):
        self.all_folders = []
        self.analysis_results = {
            'empty_folders': [],
            'cache_folders': [],
            'backup_folders': [],
            'redundant_folders': [],
            'large_folders': [],
            'deep_nested_folders': []
        }

    def analyze_all_folders_deep(self):
        """🔍 Analysiere ALLE Ordner rekursiv"""
        print("🔍 Starte TIEFGEHENDE Ordner-Analyse...")

        # Sammle ALLE Ordner
        for root, dirs, files in os.walk('.'):
            # Skip .git
            if '.git' in dirs:
                dirs.remove('.git')

            for dir_name in dirs:
                folder_path = Path(root) / dir_name
                self.all_folders.append(folder_path)

        print(f"📊 Gefunden: {len(self.all_folders)} Ordner total")

        # Analysiere jeden Ordner
        for folder in self.all_folders:
            self._analyze_folder_deep(folder)

        self._generate_deep_report()

    def _analyze_folder_deep(self, folder_path):
        """🔍 Tiefgehende Analyse eines Ordners"""
        try:
            folder_name = folder_path.name
            relative_path = str(folder_path)

            # Ordnergröße berechnen
            folder_size = self._get_folder_size(folder_path)
            folder_size_mb = round(folder_size / (1024 * 1024), 2)

            # Dateien und Unterordner zählen
            if folder_path.exists():
                all_items = list(folder_path.rglob('*'))
                file_count = len([item for item in all_items if item.is_file()])
                subfolder_count = len([item for item in all_items if item.is_dir()])
            else:
                file_count = 0
                subfolder_count = 0

            # Verschachtelungstiefe
            nesting_level = len(folder_path.parts) - 1

            folder_info = {
                'name': folder_name,
                'path': relative_path,
                'size_mb': folder_size_mb,
                'file_count': file_count,
                'subfolder_count': subfolder_count,
                'nesting_level': nesting_level,
                'is_empty': file_count == 0 and subfolder_count == 0
            }

            # Kategorisierung
            self._categorize_folder_deep(folder_info)

        except Exception as e:
            print(f"❌ Fehler bei {folder_path}: {e}")

    def _categorize_folder_deep(self, folder_info):
        """📂 Kategorisiere Ordner"""

        path = folder_info['path']
        name = folder_info['name']

        # Leere Ordner
        if folder_info['is_empty']:
            self.analysis_results['empty_folders'].append(folder_info)
            return

        # Cache Ordner
        if any(cache in name.lower() for cache in ['__pycache__', 'cache', '.cache', '.ruff_cache']):
            self.analysis_results['cache_folders'].append(folder_info)
            return

        # Backup Ordner
        if any(backup in path.lower() for backup in ['backup', 'bak', '_backup']):
            self.analysis_results['backup_folders'].append(folder_info)
            return

        # Tief verschachtelt (>4 Ebenen)
        if folder_info['nesting_level'] > 4:
            self.analysis_results['deep_nested_folders'].append(folder_info)
            return

        # Große Ordner
        if folder_info['size_mb'] > 10:
            self.analysis_results['large_folders'].append(folder_info)
            return

        # Redundante Strukturen
        redundant_patterns = ['old', 'obsolete', 'unused', 'deprecated', 'legacy', 'archive']
        if any(pattern in path.lower() for pattern in redundant_patterns):
            self.analysis_results['redundant_folders'].append(folder_info)
            return

    def _get_folder_size(self, folder_path):
        """📏 Berechne Ordnergröße"""
        try:
            if not folder_path.exists():
                return 0

            total_size = 0
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except:
                        pass
            return total_size
        except:
            return 0

    def _generate_deep_report(self):
        """📄 Generiere tiefgehenden Report"""

        print(f"\n📊 TIEFGEHENDE ORDNER-ANALYSE:")

        total_folders = len(self.all_folders)

        for category, folders in self.analysis_results.items():
            if folders:
                total_size = sum(f['size_mb'] for f in folders)
                print(f"   📂 {category}: {len(folders)} Ordner ({total_size:.1f} MB)")

        # Detaillierte Ausgabe für wichtige Kategorien
        print(f"\n🗑️ CLEANUP EMPFEHLUNGEN:")

        # Leere Ordner
        empty_folders = self.analysis_results['empty_folders']
        if empty_folders:
            print(f"\n📭 LEERE ORDNER ({len(empty_folders)} Stück):")
            for folder in empty_folders[:10]:  # Zeige erste 10
                print(f"   - {folder['path']}")
            if len(empty_folders) > 10:
                print(f"   ... und {len(empty_folders) - 10} weitere")

        # Cache Ordner
        cache_folders = self.analysis_results['cache_folders']
        if cache_folders:
            print(f"\n🗄️ CACHE ORDNER ({len(cache_folders)} Stück):")
            for folder in cache_folders:
                print(f"   - {folder['path']} ({folder['size_mb']} MB)")

        # Tief verschachtelte Ordner
        deep_folders = self.analysis_results['deep_nested_folders']
        if deep_folders:
            print(f"\n🕳️ TIEF VERSCHACHTELTE ORDNER ({len(deep_folders)} Stück):")
            for folder in deep_folders[:5]:  # Zeige erste 5
                print(f"   - {folder['path']} (Ebene {folder['nesting_level']})")

        # Cleanup Kommandos generieren
        self._generate_cleanup_commands()

    def _generate_cleanup_commands(self):
        """🛠️ Generiere Cleanup-Kommandos"""

        print(f"\n🛠️ CLEANUP KOMMANDOS:")

        # Leere Ordner löschen
        empty_folders = self.analysis_results['empty_folders']
        if empty_folders:
            print(f"\n# Leere Ordner löschen ({len(empty_folders)} Stück):")
            for folder in empty_folders:
                print(f"Remove-Item \"{folder['path']}\" -Force")

        # Cache Ordner löschen
        cache_folders = self.analysis_results['cache_folders']
        if cache_folders:
            print(f"\n# Cache Ordner löschen ({len(cache_folders)} Stück):")
            for folder in cache_folders:
                print(f"Remove-Item \"{folder['path']}\" -Recurse -Force")

        # Backup Ordner löschen
        backup_folders = self.analysis_results['backup_folders']
        if backup_folders:
            print(f"\n# Backup Ordner löschen ({len(backup_folders)} Stück):")
            for folder in backup_folders:
                print(f"Remove-Item \"{folder['path']}\" -Recurse -Force")

        # Statistik
        total_deletable = len(empty_folders) + len(cache_folders) + len(backup_folders)
        total_folders = len(self.all_folders)

        print(f"\n📊 CLEANUP POTENTIAL:")
        print(f"   📁 Löschbar: {total_deletable}/{total_folders} Ordner ({total_deletable/total_folders*100:.1f}%)")

if __name__ == "__main__":
    print("🗂️ DEEP FOLDER ANALYSIS")
    print("=" * 50)

    analyzer = DeepFolderAnalyzer()
    analyzer.analyze_all_folders_deep()

    print("\n✅ Tiefgehende Analyse abgeschlossen!")