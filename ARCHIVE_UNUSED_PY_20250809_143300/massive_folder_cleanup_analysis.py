#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗂️ MASSIVE FOLDER CLEANUP ANALYSIS
==================================

Vollständige Analyse aller Ordner und Unterordner im Checker-Projekt
zur Identifikation von redundanten, veralteten oder unnötigen Verzeichnissen.

Ziel: MEGA-Cleanup für VS Code Performance-Optimierung
"""

from datetime import datetime
from pathlib import Path
import os

class MassiveFolderCleanupAnalyzer:
    """
    🗂️ MASSIVE FOLDER CLEANUP ANALYZER
    Systematische Analyse zur Identifikation von Cleanup-Kandidaten
    """

    def __init__(self):
        self.analysis_results = {
            'cache_folders': [],
            'backup_folders': [],
            'redundant_project_folders': [],
            'customer_duplicate_folders': [],
            'empty_folders': [],
            'large_folders': [],
            'safe_to_delete': [],
            'critical_folders': []
        }

        # KRITISCHE Ordner die NIEMALS gelöscht werden dürfen
        self.critical_folders = {
            '.': 'Root Directory - CRITICAL',
            '.git': 'Git Repository - CRITICAL',
            '.vscode': 'VS Code Settings - CRITICAL',
            '.github': 'GitHub Actions - CRITICAL'
        }

        # Patterns für automatische Kategorisierung
        self.folder_patterns = {
            'cache': ['__pycache__', '.ruff_cache', '.pytest_cache', 'cache', '.cache'],
            'backup': ['backup', 'BACKUP', '_backup', '_BACKUP', 'bak'],
            'temp': ['temp', 'tmp', 'temporary', '.temp', '.tmp'],
            'redundant': ['old', 'OLD', 'obsolete', 'deprecated', 'unused'],
            'customer': ['kunde', 'kunden', 'customer', 'customers', 'client'],
            'project': ['projekt', 'projekte', 'project', 'projects']
        }

    def analyze_all_folders(self):
        """🔍 Analyse aller Ordner und Unterordner"""
        print("🔍 Starte umfassende Ordner-Analyse...")

        # Alle Ordner im aktuellen Verzeichnis sammeln
        all_folders = []

        for root, dirs, files in os.walk('.'):
            # Skip .git folder completely
            if '.git' in dirs:
                dirs.remove('.git')

            for dir_name in dirs:
                folder_path = Path(root) / dir_name
                all_folders.append(folder_path)

        print(f"📊 Gefunden: {len(all_folders)} Ordner")

        for folder in all_folders:
            self._analyze_single_folder(folder)

        # Ergebnisse auswerten
        self._evaluate_results()

        # Report generieren
        self._generate_cleanup_report()

    def _analyze_single_folder(self, folder_path):
        """🔍 Analyse eines einzelnen Ordners"""
        try:
            folder_name = folder_path.name
            relative_path = str(folder_path)

            # Ordnergröße berechnen
            folder_size = self._get_folder_size(folder_path)
            folder_size_mb = round(folder_size / (1024 * 1024), 2)

            # Anzahl Dateien zählen
            file_count = len(list(folder_path.rglob('*'))) if folder_path.exists() else 0

            # Letztes Änderungsdatum
            try:
                mod_time = datetime.fromtimestamp(folder_path.stat().st_mtime)
                days_old = (datetime.now() - mod_time).days
            except:
                mod_time = datetime.now()
                days_old = 0

            # Ordner-Info
            folder_info = {
                'name': folder_name,
                'path': relative_path,
                'size_mb': folder_size_mb,
                'file_count': file_count,
                'mod_time': mod_time,
                'days_old': days_old,
                'is_empty': file_count == 0
            }

            # Kategorisierung
            category = self._categorize_folder(folder_name, relative_path, folder_info)

            # In entsprechende Kategorie einordnen
            self.analysis_results[category].append(folder_info)

        except Exception as e:
            print(f"❌ Fehler bei Analyse von {folder_path}: {e}")

    def _categorize_folder(self, folder_name, relative_path, folder_info):
        """📂 Kategorisiere Ordner basierend auf Name und Eigenschaften"""

        # Kritische Ordner (NIEMALS löschen)
        if folder_name in self.critical_folders or relative_path in self.critical_folders:
            return 'critical_folders'

        # Leere Ordner
        if folder_info['is_empty']:
            return 'empty_folders'

        # Pattern-basierte Kategorisierung
        for category, patterns in self.folder_patterns.items():
            if any(pattern.lower() in folder_name.lower() or pattern.lower() in relative_path.lower() for pattern in patterns):
                if category == 'cache':
                    return 'cache_folders'
                elif category == 'backup':
                    return 'backup_folders'
                elif category == 'temp':
                    return 'safe_to_delete'
                elif category == 'redundant':
                    return 'safe_to_delete'
                elif category == 'customer':
                    return 'customer_duplicate_folders'
                elif category == 'project':
                    return 'redundant_project_folders'

        # Größen-basierte Kategorisierung
        if folder_info['size_mb'] > 50:
            return 'large_folders'

        # Spezielle Ordner
        special_folders = {
            'Checker_Projekte': 'redundant_project_folders',
            'src': 'redundant_project_folders',
            'core': 'redundant_project_folders',
            'modules': 'redundant_project_folders',
            'tests': 'safe_to_delete',
            'test': 'safe_to_delete',
            'docs': 'safe_to_delete',
            'documentation': 'safe_to_delete'
        }

        if folder_name in special_folders:
            return special_folders[folder_name]

        # Standard: Als große Ordner markieren wenn über 10 MB
        if folder_info['size_mb'] > 10:
            return 'large_folders'

        return 'safe_to_delete'

    def _get_folder_size(self, folder_path):
        """📏 Berechne Ordnergröße in Bytes"""
        try:
            if not folder_path.exists():
                return 0

            total_size = 0
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except:
                        pass  # Skip files that can't be accessed

            return total_size
        except:
            return 0

    def _evaluate_results(self):
        """📊 Ergebnisse auswerten und Empfehlungen generieren"""

        total_folders = sum(len(folders) for folders in self.analysis_results.values())

        print(f"\n📊 ORDNER-ANALYSE-ERGEBNISSE:")
        print(f"   📁 Gesamt-Ordner: {total_folders}")

        for category, folders in self.analysis_results.items():
            if folders:
                total_size = sum(f['size_mb'] for f in folders)
                print(f"   📂 {category}: {len(folders)} Ordner ({total_size:.1f} MB)")

    def _generate_cleanup_report(self):
        """📄 Detaillierten Cleanup-Report generieren"""

        report_lines = []
        report_lines.append("# 🗂️ MASSIVE FOLDER CLEANUP ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Analysierte Ordner: {sum(len(folders) for folders in self.analysis_results.values())}")
        report_lines.append("")

        # Cache Folders (SOFORT LÖSCHEN)
        report_lines.append("## 🗄️ CACHE FOLDERS (SOFORT LÖSCHEN)")
        report_lines.append("")
        cache_folders = self.analysis_results['cache_folders']
        if cache_folders:
            total_cache_size = sum(f['size_mb'] for f in cache_folders)
            report_lines.append(f"**Speicher-Einsparung: {total_cache_size:.1f} MB**")
            report_lines.append("")
            for folder_info in sorted(cache_folders, key=lambda x: x['size_mb'], reverse=True):
                report_lines.append(f"- {folder_info['path']} ({folder_info['size_mb']} MB, {folder_info['file_count']} files)")

        # Backup Folders (LÖSCHEN EMPFOHLEN)
        report_lines.append("\n## 🗄️ BACKUP FOLDERS (LÖSCHEN EMPFOHLEN)")
        report_lines.append("")
        backup_folders = self.analysis_results['backup_folders']
        if backup_folders:
            total_backup_size = sum(f['size_mb'] for f in backup_folders)
            report_lines.append(f"**Speicher-Einsparung: {total_backup_size:.1f} MB**")
            report_lines.append("")
            for folder_info in sorted(backup_folders, key=lambda x: x['size_mb'], reverse=True):
                report_lines.append(f"- {folder_info['path']} ({folder_info['size_mb']} MB) - {folder_info['days_old']} Tage alt")

        # Empty Folders (LÖSCHEN)
        report_lines.append("\n## 📭 EMPTY FOLDERS (LÖSCHEN)")
        report_lines.append("")
        empty_folders = self.analysis_results['empty_folders']
        if empty_folders:
            report_lines.append(f"**Anzahl leerer Ordner: {len(empty_folders)}**")
            report_lines.append("")
            for folder_info in empty_folders:
                report_lines.append(f"- {folder_info['path']}")

        # Redundant Project Folders (PRÜFEN)
        report_lines.append("\n## 🗂️ REDUNDANT PROJECT FOLDERS (PRÜFEN)")
        report_lines.append("")
        redundant_folders = self.analysis_results['redundant_project_folders']
        if redundant_folders:
            total_redundant_size = sum(f['size_mb'] for f in redundant_folders)
            report_lines.append(f"**Potentielle Speicher-Einsparung: {total_redundant_size:.1f} MB**")
            report_lines.append("")
            for folder_info in sorted(redundant_folders, key=lambda x: x['size_mb'], reverse=True):
                report_lines.append(f"- {folder_info['path']} ({folder_info['size_mb']} MB, {folder_info['file_count']} files)")

        # Large Folders (ANALYSIEREN)
        report_lines.append("\n## 📦 LARGE FOLDERS (ANALYSIEREN)")
        report_lines.append("")
        large_folders = self.analysis_results['large_folders']
        if large_folders:
            for folder_info in sorted(large_folders, key=lambda x: x['size_mb'], reverse=True):
                status = "PRÜFEN" if folder_info['size_mb'] > 100 else "ÜBERWACHEN"
                report_lines.append(f"- {folder_info['path']} ({folder_info['size_mb']} MB) - {status}")

        # Safe to Delete (SICHER LÖSCHBAR)
        report_lines.append("\n## ✅ SAFE TO DELETE (SICHER LÖSCHBAR)")
        report_lines.append("")
        safe_folders = self.analysis_results['safe_to_delete']
        if safe_folders:
            total_safe_size = sum(f['size_mb'] for f in safe_folders)
            report_lines.append(f"**Sichere Speicher-Einsparung: {total_safe_size:.1f} MB**")
            report_lines.append("")
            for folder_info in sorted(safe_folders, key=lambda x: x['size_mb'], reverse=True):
                report_lines.append(f"- {folder_info['path']} ({folder_info['size_mb']} MB)")

        # Critical Folders (NIEMALS LÖSCHEN)
        report_lines.append("\n## 🛡️ CRITICAL FOLDERS (NIEMALS LÖSCHEN)")
        report_lines.append("")
        critical_folders = self.analysis_results['critical_folders']
        if critical_folders:
            for folder_info in critical_folders:
                reason = self.critical_folders.get(folder_info['name'], 'Critical system folder')
                report_lines.append(f"- {folder_info['path']} - {reason}")

        # Gesamte Speicher-Einsparung berechnen
        total_saveable = (
            sum(f['size_mb'] for f in cache_folders) +
            sum(f['size_mb'] for f in backup_folders) +
            sum(f['size_mb'] for f in safe_folders)
        )

        report_lines.append(f"\n## 💾 GESAMTE POTENTIELLE SPEICHER-EINSPARUNG")
        report_lines.append(f"**{total_saveable:.1f} MB** können potentiell eingespart werden")

        # Empfohlene Cleanup-Kommandos
        report_lines.append(f"\n## 🛠️ EMPFOHLENE CLEANUP-KOMMANDOS")
        report_lines.append("")

        if cache_folders:
            report_lines.append("### Cache-Ordner löschen (SICHER):")
            for folder_info in cache_folders:
                report_lines.append(f"Remove-Item \"{folder_info['path']}\" -Recurse -Force")

        if empty_folders:
            report_lines.append("\n### Leere Ordner löschen (SICHER):")
            for folder_info in empty_folders:
                report_lines.append(f"Remove-Item \"{folder_info['path']}\" -Force")

        if backup_folders:
            report_lines.append("\n### Backup-Ordner löschen (EMPFOHLEN):")
            for folder_info in backup_folders:
                report_lines.append(f"Remove-Item \"{folder_info['path']}\" -Recurse -Force")

        # Report speichern
        report_file = f"MASSIVE_FOLDER_CLEANUP_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\n📄 Detaillierter Report gespeichert: {report_file}")

        # Sofortige Empfehlungen ausgeben
        self._print_immediate_recommendations()

    def _print_immediate_recommendations(self):
        """🎯 Sofortige Empfehlungen ausgeben"""

        print(f"\n🎯 SOFORTIGE EMPFEHLUNGEN:")

        cache_folders = self.analysis_results['cache_folders']
        backup_folders = self.analysis_results['backup_folders']
        empty_folders = self.analysis_results['empty_folders']
        safe_folders = self.analysis_results['safe_to_delete']

        if cache_folders:
            cache_size = sum(f['size_mb'] for f in cache_folders)
            print(f"   🗄️ CACHE FOLDERS: {len(cache_folders)} Ordner ({cache_size:.1f} MB) → SOFORT LÖSCHEN")

        if empty_folders:
            print(f"   📭 EMPTY FOLDERS: {len(empty_folders)} Ordner → SOFORT LÖSCHEN")

        if backup_folders:
            backup_size = sum(f['size_mb'] for f in backup_folders)
            print(f"   🗄️ BACKUP FOLDERS: {len(backup_folders)} Ordner ({backup_size:.1f} MB) → EMPFOHLEN LÖSCHEN")

        if safe_folders:
            safe_size = sum(f['size_mb'] for f in safe_folders)
            print(f"   ✅ SAFE TO DELETE: {len(safe_folders)} Ordner ({safe_size:.1f} MB) → SICHER LÖSCHEN")

        total_deletable = len(cache_folders) + len(backup_folders) + len(empty_folders) + len(safe_folders)
        total_folders = sum(len(folders) for folders in self.analysis_results.values())

        print(f"\n📊 CLEANUP POTENTIAL:")
        print(f"   📁 Potentiell löschbar: {total_deletable}/{total_folders} Ordner ({total_deletable/total_folders*100:.1f}%)")

        if cache_folders:
            print(f"\n🚀 NEXT STEP: Cache-Ordner sofort löschen für {sum(f['size_mb'] for f in cache_folders):.1f} MB Einsparung")

if __name__ == "__main__":
    print("🗂️ MASSIVE FOLDER CLEANUP ANALYSIS")
    print("=" * 50)

    analyzer = MassiveFolderCleanupAnalyzer()
    analyzer.analyze_all_folders()

    print("\n✅ Ordner-Analyse abgeschlossen!")
    print("📄 Detaillierter Report wurde erstellt.")