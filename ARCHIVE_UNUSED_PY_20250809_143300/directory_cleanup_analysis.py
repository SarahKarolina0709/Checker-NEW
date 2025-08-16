#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧹 DIRECTORY CLEANUP ANALYZER
============================

Systematische Analyse und Cleanup aller Ordner-Strukturen
zur Identifikation von redundanten Ordnern und Speicher-Verschwendung.

Ziel: Massive Ordner-Optimierung für VS Code Performance
"""


from datetime import datetime
from pathlib import Path

class DirectoryCleanupAnalyzer:
    """
    🧹 DIRECTORY CLEANUP ANALYZER
    Systematische Analyse zur Identifikation von Cleanup-Kandidaten
    """

    def __init__(self):
        self.analysis_results = {
            'cache_folders': [],
            'backup_folders': [],
            'redundant_folders': [],
            'large_folders': [],
            'empty_folders': [],
            'customer_folders': [],
            'cleanup_candidates': []
        }

        # Gefährliche Ordner die SOFORT gelöscht werden können
        self.safe_to_delete = {
            '__pycache__': 'Python Cache - SAFE DELETE',
            '.ruff_cache': 'Ruff Linter Cache - SAFE DELETE',
            'PYTHON_BACKUP_20250806_000339': 'Python Backup - SAFE DELETE',
            'MARKDOWN_BACKUP_20250805_150238': 'Markdown Backup - SAFE DELETE',
            'async_test_files': 'Test Files - SAFE DELETE',
            '.benchmarks': 'Benchmark Files - SAFE DELETE'
        }

        # Zu prüfende Ordner
        self.check_folders = {
            'archive': 'Archive - PRÜFEN',
            'logs': 'Log Files - PRÜFEN',
            'tesseract': 'OCR Tool - PRÜFEN (falls nicht benötigt)',
            'poppler': 'PDF Tool - PRÜFEN (falls nicht benötigt)',
            'welcome_screen_components': 'Components - PRÜFEN',
            'ui_components': 'UI Components - PRÜFEN'
        }

        # Essential Ordner die NIEMALS gelöscht werden
        self.essential_folders = {
            '.github': 'GitHub Configuration - ESSENTIAL',
            '.vscode': 'VS Code Configuration - ESSENTIAL',
            'src': 'Source Code - ESSENTIAL',
            'core': 'Core Application - ESSENTIAL',
            'assets': 'Application Assets - ESSENTIAL',
            'config': 'Configuration - ESSENTIAL',
            'customers': 'Customer Data - ESSENTIAL',
            'Checker_Projekte': 'Project Data - ESSENTIAL (aber cleanup möglich)',
            'app_managers': 'Application Managers - ESSENTIAL',
            'tests': 'Test Suite - ESSENTIAL',
            'utils': 'Utilities - ESSENTIAL'
        }

    def analyze_all_directories(self):
        """🔍 Analyse aller Verzeichnisse"""
        print("🔍 Starte umfassende Verzeichnis-Analyse...")

        # Alle Hauptordner sammeln
        main_dirs = [d for d in Path('.').iterdir() if d.is_dir()]

        print(f"📊 Gefunden: {len(main_dirs)} Hauptverzeichnisse")

        for directory in main_dirs:
            self._analyze_single_directory(directory)

        # Spezielle Analysen
        self._analyze_checker_projekte()
        self._analyze_cache_folders()

        # Ergebnisse auswerten
        self._evaluate_results()

        # Report generieren
        self._generate_cleanup_report()

    def _analyze_single_directory(self, dir_path):
        """🔍 Analyse eines einzelnen Verzeichnisses"""
        try:
            dir_name = dir_path.name

            # Größe berechnen
            total_size = 0
            file_count = 0

            try:
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
            except:
                pass

            size_mb = round(total_size / (1024 * 1024), 2)

            # Verzeichnis-Info
            dir_info = {
                'name': dir_name,
                'size_mb': size_mb,
                'file_count': file_count,
                'path': str(dir_path)
            }

            # Kategorisierung
            category = self._categorize_directory(dir_name, dir_info)

            # In entsprechende Kategorie einordnen
            if category in self.analysis_results:
                self.analysis_results[category].append(dir_info)

        except Exception as e:
            print(f"❌ Fehler bei Analyse von {dir_path}: {e}")

    def _categorize_directory(self, dir_name, dir_info):
        """📂 Kategorisiere Verzeichnis"""

        # Safe to delete
        if dir_name in self.safe_to_delete:
            return 'cleanup_candidates'

        # Cache folders
        if 'cache' in dir_name.lower() or dir_name.startswith('.'):
            return 'cache_folders'

        # Backup folders
        if 'backup' in dir_name.lower() or 'BACKUP' in dir_name:
            return 'backup_folders'

        # Large folders (> 50 MB)
        if dir_info['size_mb'] > 50:
            return 'large_folders'

        # Empty or tiny folders
        if dir_info['file_count'] == 0 or dir_info['size_mb'] < 0.1:
            return 'empty_folders'

        # Customer folders
        if dir_name in ['Checker_Projekte', 'customers', 'kunden']:
            return 'customer_folders'

        # Check folders
        if dir_name in self.check_folders:
            return 'redundant_folders'

        # Default
        return 'redundant_folders'

    def _analyze_checker_projekte(self):
        """🎯 Spezielle Analyse von Checker_Projekte"""

        checker_projekte_path = Path('Checker_Projekte')
        if not checker_projekte_path.exists():
            return

        customer_dirs = [d for d in checker_projekte_path.iterdir() if d.is_dir()]

        print(f"📊 Checker_Projekte: {len(customer_dirs)} Kunden-Ordner gefunden")

        # Analysiere Duplikate und Test-Ordner
        test_customers = []
        real_customers = []

        for customer_dir in customer_dirs:
            customer_name = customer_dir.name.lower()

            if any(test_word in customer_name for test_word in ['test', 'demo', 'beispiel', 'muster']):
                test_customers.append(customer_dir.name)
            else:
                real_customers.append(customer_dir.name)

        self.analysis_results['customer_folders'].append({
            'name': 'Checker_Projekte Analysis',
            'total_customers': len(customer_dirs),
            'test_customers': len(test_customers),
            'real_customers': len(real_customers),
            'test_customer_list': test_customers[:10],  # Erste 10
            'size_mb': sum(self._get_dir_size(customer_dir) for customer_dir in customer_dirs)
        })

    def _analyze_cache_folders(self):
        """🗂️ Analyse aller Cache-Ordner"""

        cache_patterns = ['__pycache__', '.ruff_cache', 'node_modules', '.pytest_cache']

        for pattern in cache_patterns:
            cache_dirs = list(Path('.').rglob(pattern))

            if cache_dirs:
                total_size = sum(self._get_dir_size(cache_dir) for cache_dir in cache_dirs)

                self.analysis_results['cache_folders'].append({
                    'pattern': pattern,
                    'count': len(cache_dirs),
                    'size_mb': total_size,
                    'locations': [str(cache_dir) for cache_dir in cache_dirs[:5]]
                })

    def _get_dir_size(self, dir_path):
        """📏 Berechne Ordner-Größe in MB"""
        try:
            total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0

    def _evaluate_results(self):
        """📊 Ergebnisse auswerten"""

        print(f"\n📊 VERZEICHNIS-ANALYSE ERGEBNISSE:")

        # Cache folders
        cache_folders = self.analysis_results['cache_folders']
        if cache_folders:
            total_cache_size = sum(cf['size_mb'] for cf in cache_folders)
            print(f"   🗂️ Cache-Ordner: {total_cache_size:.1f} MB")

        # Backup folders
        backup_folders = self.analysis_results['backup_folders']
        if backup_folders:
            total_backup_size = sum(bf['size_mb'] for bf in backup_folders)
            print(f"   🗄️ Backup-Ordner: {total_backup_size:.1f} MB")

        # Cleanup candidates
        cleanup_candidates = self.analysis_results['cleanup_candidates']
        if cleanup_candidates:
            total_cleanup_size = sum(cc['size_mb'] for cc in cleanup_candidates)
            print(f"   🧹 Cleanup-Kandidaten: {total_cleanup_size:.1f} MB")

    def _generate_cleanup_report(self):
        """📄 Detaillierten Cleanup-Report generieren"""

        report_lines = []
        report_lines.append("# 🧹 DIRECTORY CLEANUP ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Cache Folders (SOFORT LÖSCHEN)
        report_lines.append("## 🗂️ CACHE FOLDERS (SOFORT LÖSCHEN)")
        report_lines.append("")
        cache_folders = self.analysis_results['cache_folders']
        if cache_folders:
            total_cache_size = sum(cf['size_mb'] for cf in cache_folders)
            report_lines.append(f"**Speicher-Einsparung: {total_cache_size:.1f} MB**")
            report_lines.append("")
            for cache_folder in cache_folders:
                report_lines.append(f"- **{cache_folder['pattern']}**: {cache_folder['count']} Ordner, {cache_folder['size_mb']:.1f} MB")
                for location in cache_folder['locations']:
                    report_lines.append(f"  - {location}")

        # Backup Folders (LÖSCHEN EMPFOHLEN)
        report_lines.append("\n## 🗄️ BACKUP FOLDERS (LÖSCHEN EMPFOHLEN)")
        report_lines.append("")
        backup_folders = self.analysis_results['backup_folders']
        if backup_folders:
            total_backup_size = sum(bf['size_mb'] for bf in backup_folders)
            report_lines.append(f"**Speicher-Einsparung: {total_backup_size:.1f} MB**")
            report_lines.append("")
            for backup_folder in backup_folders:
                report_lines.append(f"- {backup_folder['name']} ({backup_folder['size_mb']:.1f} MB)")

        # Cleanup Candidates (PRÜFEN UND LÖSCHEN)
        report_lines.append("\n## 🧹 CLEANUP CANDIDATES (PRÜFEN UND LÖSCHEN)")
        report_lines.append("")
        cleanup_candidates = self.analysis_results['cleanup_candidates']
        if cleanup_candidates:
            total_cleanup_size = sum(cc['size_mb'] for cc in cleanup_candidates)
            report_lines.append(f"**Potentielle Speicher-Einsparung: {total_cleanup_size:.1f} MB**")
            report_lines.append("")
            for cleanup_candidate in cleanup_candidates:
                reason = self.safe_to_delete.get(cleanup_candidate['name'], 'Zu prüfen')
                report_lines.append(f"- {cleanup_candidate['name']} ({cleanup_candidate['size_mb']:.1f} MB) - {reason}")

        # Customer Folders Analysis
        report_lines.append("\n## 👥 CUSTOMER FOLDERS ANALYSIS")
        report_lines.append("")
        customer_folders = self.analysis_results['customer_folders']
        if customer_folders:
            for customer_analysis in customer_folders:
                if 'total_customers' in customer_analysis:
                    report_lines.append(f"**Checker_Projekte Analyse:**")
                    report_lines.append(f"- Gesamt Kunden: {customer_analysis['total_customers']}")
                    report_lines.append(f"- Test/Demo Kunden: {customer_analysis['test_customers']}")
                    report_lines.append(f"- Echte Kunden: {customer_analysis['real_customers']}")
                    report_lines.append(f"- Gesamtgröße: {customer_analysis['size_mb']:.1f} MB")
                    report_lines.append("")
                    report_lines.append("**Test/Demo Kunden (können gelöscht werden):**")
                    for test_customer in customer_analysis['test_customer_list']:
                        report_lines.append(f"  - {test_customer}")

        # Cleanup Commands
        report_lines.append(f"\n## 🛠️ EMPFOHLENE CLEANUP-KOMMANDOS")
        report_lines.append("")

        # Cache cleanup
        if cache_folders:
            report_lines.append("### Cache-Ordner löschen (SICHER):")
            for cache_folder in cache_folders:
                for location in cache_folder['locations']:
                    report_lines.append(f"Remove-Item \"{location}\" -Recurse -Force")

        # Backup cleanup
        if backup_folders:
            report_lines.append("\n### Backup-Ordner löschen (EMPFOHLEN):")
            for backup_folder in backup_folders:
                report_lines.append(f"Remove-Item \"{backup_folder['name']}\" -Recurse -Force")

        # Cleanup candidates
        if cleanup_candidates:
            report_lines.append("\n### Cleanup-Kandidaten löschen (PRÜFEN):")
            for cleanup_candidate in cleanup_candidates:
                report_lines.append(f"Remove-Item \"{cleanup_candidate['name']}\" -Recurse -Force")

        # Report speichern
        report_file = f"DIRECTORY_CLEANUP_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\n📄 Detaillierter Verzeichnis-Report gespeichert: {report_file}")

        # Sofortige Empfehlungen
        self._print_immediate_recommendations()

    def _print_immediate_recommendations(self):
        """🎯 Sofortige Empfehlungen ausgeben"""

        print(f"\n🎯 SOFORTIGE VERZEICHNIS-EMPFEHLUNGEN:")

        cache_folders = self.analysis_results['cache_folders']
        backup_folders = self.analysis_results['backup_folders']
        cleanup_candidates = self.analysis_results['cleanup_candidates']

        if cache_folders:
            cache_size = sum(cf['size_mb'] for cf in cache_folders)
            print(f"   🗂️ CACHE FOLDERS: {cache_size:.1f} MB → SOFORT LÖSCHEN")

        if backup_folders:
            backup_size = sum(bf['size_mb'] for bf in backup_folders)
            print(f"   🗄️ BACKUP FOLDERS: {backup_size:.1f} MB → SOFORT LÖSCHEN")

        if cleanup_candidates:
            cleanup_size = sum(cc['size_mb'] for cc in cleanup_candidates)
            print(f"   🧹 CLEANUP CANDIDATES: {cleanup_size:.1f} MB → PRÜFEN & LÖSCHEN")

        total_saveable = (
            (sum(cf['size_mb'] for cf in cache_folders) if cache_folders else 0) +
            (sum(bf['size_mb'] for bf in backup_folders) if backup_folders else 0) +
            (sum(cc['size_mb'] for cc in cleanup_candidates) if cleanup_candidates else 0)
        )

        print(f"\n📊 TOTAL EINSPARUNG POTENTIAL: {total_saveable:.1f} MB")

        if cache_folders:
            print(f"\n🚀 NEXT STEP: Cache-Ordner löschen für {sum(cf['size_mb'] for cf in cache_folders):.1f} MB Einsparung")

if __name__ == "__main__":
    print("🧹 DIRECTORY CLEANUP ANALYSIS")
    print("=" * 50)

    analyzer = DirectoryCleanupAnalyzer()
    analyzer.analyze_all_directories()

    print("\n✅ Verzeichnis-Analyse abgeschlossen!")
    print("📄 Detaillierter Report wurde erstellt.")