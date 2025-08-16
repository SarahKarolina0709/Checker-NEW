#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧹 PYTHON FILES CLEANUP ANALYSIS
===============================

Systematische Analyse aller 94 Python-Dateien im Checker-Projekt
zur Identifikation von redundanten, veralteten oder unnötigen Dateien.

Ziel: Project Cleanup und Performance-Optimierung
"""


from datetime import datetime, timedelta
from pathlib import Path

class PythonFilesCleanupAnalyzer:
    """
    🧹 PYTHON FILES CLEANUP ANALYZER
    Systematische Analyse zur Identifikation von Cleanup-Kandidaten
    """

    def __init__(self):
        self.analysis_results = {
            'essential_files': [],
            'backup_files': [],
            'test_files': [],
            'demo_files': [],
            'diagnostic_files': [],
            'redundant_files': [],
            'deprecated_files': [],
            'cleanup_candidates': []
        }

        # Essential files die NIEMALS gelöscht werden dürfen
        self.essential_files = {
            # Core Application Files
            'welcome_screen.py': 'Modular Orchestrator - CRITICAL',
            'welcome_screen_main.py': 'Core UI Module - CRITICAL',
            'welcome_screen_upload.py': 'Upload Module - CRITICAL',
            'welcome_screen_customer.py': 'Customer Module - CRITICAL',
            'welcome_screen_utils.py': 'Utils Module - CRITICAL',
            'modern_translation_quality_gui.py': 'Main GUI Application - CRITICAL',

            # Core System Files
            'design_system.py': 'Central Design System - CRITICAL',
            'ui_theme.py': 'Theme Management - CRITICAL',
            'template_manager.py': 'Template System - CRITICAL',
            'customer_manager.py': 'Customer Management - CRITICAL',

            # Essential Utilities
            'async_file_operations.py': 'Async Operations - IMPORTANT',
            'async_quality_analysis.py': 'Quality Analysis - IMPORTANT',
            'universal_light_mode_fallback.py': 'Light Mode Enforcement - IMPORTANT',

            # Startup & Launcher
            'main.py': 'Main Entry Point - IMPORTANT',
            'integrated_startup.py': 'Integrated Startup - IMPORTANT'
        }

        # Patterns für automatische Kategorisierung
        self.file_patterns = {
            'backup': ['_BACKUP_', '_BEFORE_', '_OLD_', '_ORIGINAL_'],
            'test': ['test_', '_test', 'unittest_', 'pytest_'],
            'demo': ['demo_', '_demo', 'example_', 'sample_'],
            'diagnostic': ['diagnose_', 'check_', 'analyze_', 'debug_'],
            'fix': ['fix_', '_fix', 'cleanup_', 'repair_'],
            'phase': ['phase', 'p1_', 'p2_', 'p3_', 'p4_', 'p5_', 'p6_'],
            'optimization': ['optimize_', 'optimization_', 'performance_'],
            'temporary': ['temp_', '_temp', 'tmp_', '_tmp']
        }

    def analyze_all_files(self):
        """🔍 Analyse aller Python-Dateien"""
        print("🔍 Starte umfassende Python-Dateien-Analyse...")

        # Alle Python-Dateien sammeln
        python_files = list(Path('.').glob('*.py'))

        print(f"📊 Gefunden: {len(python_files)} Python-Dateien")

        for py_file in python_files:
            self._analyze_single_file(py_file)

        # Ergebnisse auswerten
        self._evaluate_results()

        # Report generieren
        self._generate_report()

    def _analyze_single_file(self, file_path):
        """🔍 Analyse einer einzelnen Python-Datei"""
        try:
            file_name = file_path.name
            file_size = file_path.stat().st_size
            file_size_kb = round(file_size / 1024, 2)

            # Zeilen zählen
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
            except:
                lines = 0

            # Letztes Änderungsdatum
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            days_old = (datetime.now() - mod_time).days

            # Datei-Info
            file_info = {
                'name': file_name,
                'size_kb': file_size_kb,
                'lines': lines,
                'mod_time': mod_time,
                'days_old': days_old,
                'path': str(file_path)
            }

            # Kategorisierung
            category = self._categorize_file(file_name, file_info)

            # In entsprechende Kategorie einordnen
            self.analysis_results[category].append(file_info)

        except Exception as e:
            print(f"❌ Fehler bei Analyse von {file_path}: {e}")

    def _categorize_file(self, file_name, file_info):
        """📂 Kategorisiere Datei basierend auf Name und Eigenschaften"""

        # Essential Files (NIEMALS löschen)
        if file_name in self.essential_files:
            return 'essential_files'

        # Pattern-basierte Kategorisierung
        for category, patterns in self.file_patterns.items():
            if any(pattern in file_name for pattern in patterns):
                if category == 'backup':
                    return 'backup_files'
                elif category == 'test':
                    return 'test_files'
                elif category == 'demo':
                    return 'demo_files'
                elif category == 'diagnostic':
                    return 'diagnostic_files'
                elif category in ['fix', 'optimization', 'temporary']:
                    return 'cleanup_candidates'
                elif category == 'phase':
                    return 'demo_files'  # Phase-Dateien sind meist Demo/Test

        # Größen-basierte Kategorisierung
        if file_info['size_kb'] > 200:
            return 'cleanup_candidates'  # Große Dateien prüfen

        # Alter-basierte Kategorisierung
        if file_info['days_old'] > 30 and file_info['size_kb'] < 5:
            return 'cleanup_candidates'  # Alte, kleine Dateien

        # Spezielle Dateinamen
        special_files = {
            'vscode_crash_analysis.py': 'diagnostic_files',
            'critical_files_watcher.py': 'essential_files',
            'protect_critical_files.py': 'essential_files'
        }

        if file_name in special_files:
            return special_files[file_name]

        # Standard: Als potenziell redundant markieren
        return 'redundant_files'

    def _evaluate_results(self):
        """📊 Ergebnisse auswerten und Empfehlungen generieren"""

        total_files = sum(len(files) for files in self.analysis_results.values())

        print(f"\n📊 ANALYSE-ERGEBNISSE:")
        print(f"   📁 Gesamt-Dateien: {total_files}")

        for category, files in self.analysis_results.items():
            if files:
                total_size = sum(f['size_kb'] for f in files)
                print(f"   📂 {category}: {len(files)} Dateien ({total_size:.1f} KB)")

    def _generate_report(self):
        """📄 Detaillierten Cleanup-Report generieren"""

        report_lines = []
        report_lines.append("# 🧹 PYTHON FILES CLEANUP ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Analysierte Dateien: {sum(len(files) for files in self.analysis_results.values())}")
        report_lines.append("")

        # Essential Files (BEHALTEN)
        report_lines.append("## ✅ ESSENTIAL FILES (NIEMALS LÖSCHEN)")
        report_lines.append("")
        essential_files = self.analysis_results['essential_files']
        if essential_files:
            for file_info in sorted(essential_files, key=lambda x: x['size_kb'], reverse=True):
                reason = self.essential_files.get(file_info['name'], 'Core functionality')
                report_lines.append(f"- **{file_info['name']}** ({file_info['size_kb']} KB, {file_info['lines']} lines)")
                report_lines.append(f"  Grund: {reason}")

        # Backup Files (LÖSCHEN EMPFOHLEN)
        report_lines.append("\n## 🗄️ BACKUP FILES (LÖSCHEN EMPFOHLEN)")
        report_lines.append("")
        backup_files = self.analysis_results['backup_files']
        if backup_files:
            total_backup_size = sum(f['size_kb'] for f in backup_files)
            report_lines.append(f"**Speicher-Einsparung: {total_backup_size:.1f} KB**")
            report_lines.append("")
            for file_info in sorted(backup_files, key=lambda x: x['size_kb'], reverse=True):
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB) - {file_info['days_old']} Tage alt")

        # Test Files (PRÜFEN)
        report_lines.append("\n## 🧪 TEST FILES (PRÜFEN)")
        report_lines.append("")
        test_files = self.analysis_results['test_files']
        if test_files:
            for file_info in sorted(test_files, key=lambda x: x['size_kb'], reverse=True):
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB)")

        # Demo Files (OPTIONAL LÖSCHEN)
        report_lines.append("\n## 🎬 DEMO FILES (OPTIONAL LÖSCHEN)")
        report_lines.append("")
        demo_files = self.analysis_results['demo_files']
        if demo_files:
            total_demo_size = sum(f['size_kb'] for f in demo_files)
            report_lines.append(f"**Mögliche Speicher-Einsparung: {total_demo_size:.1f} KB**")
            report_lines.append("")
            for file_info in sorted(demo_files, key=lambda x: x['size_kb'], reverse=True):
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB)")

        # Diagnostic Files (SITUATIONSABHÄNGIG)
        report_lines.append("\n## 🔍 DIAGNOSTIC FILES (SITUATIONSABHÄNGIG)")
        report_lines.append("")
        diagnostic_files = self.analysis_results['diagnostic_files']
        if diagnostic_files:
            for file_info in sorted(diagnostic_files, key=lambda x: x['size_kb'], reverse=True):
                status = "BEHALTEN" if file_info['days_old'] < 7 else "OPTIONAL LÖSCHEN"
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB) - {status}")

        # Cleanup Candidates (DRINGEND PRÜFEN)
        report_lines.append("\n## 🧹 CLEANUP CANDIDATES (DRINGEND PRÜFEN)")
        report_lines.append("")
        cleanup_candidates = self.analysis_results['cleanup_candidates']
        if cleanup_candidates:
            total_cleanup_size = sum(f['size_kb'] for f in cleanup_candidates)
            report_lines.append(f"**Potentielle Speicher-Einsparung: {total_cleanup_size:.1f} KB**")
            report_lines.append("")
            for file_info in sorted(cleanup_candidates, key=lambda x: x['size_kb'], reverse=True):
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB, {file_info['lines']} lines) - {file_info['days_old']} Tage alt")

        # Redundant Files (GENAU PRÜFEN)
        report_lines.append("\n## ⚠️ REDUNDANT FILES (GENAU PRÜFEN)")
        report_lines.append("")
        redundant_files = self.analysis_results['redundant_files']
        if redundant_files:
            for file_info in sorted(redundant_files, key=lambda x: x['size_kb'], reverse=True):
                report_lines.append(f"- {file_info['name']} ({file_info['size_kb']} KB)")

        # Gesamte Speicher-Einsparung berechnen
        total_saveable = (
            sum(f['size_kb'] for f in backup_files) +
            sum(f['size_kb'] for f in demo_files) +
            sum(f['size_kb'] for f in cleanup_candidates)
        )

        report_lines.append(f"\n## 💾 GESAMTE POTENTIELLE SPEICHER-EINSPARUNG")
        report_lines.append(f"**{total_saveable:.1f} KB** können potentiell eingespart werden")

        # Empfohlene Cleanup-Kommandos
        report_lines.append(f"\n## 🛠️ EMPFOHLENE CLEANUP-KOMMANDOS")
        report_lines.append("")

        if backup_files:
            report_lines.append("### Backup-Dateien löschen (SICHER):")
            for file_info in backup_files:
                report_lines.append(f"Remove-Item \"{file_info['name']}\" -Force")

        if demo_files:
            report_lines.append("\n### Demo-Dateien löschen (OPTIONAL):")
            for file_info in demo_files:
                report_lines.append(f"# Remove-Item \"{file_info['name']}\" -Force")

        # Report speichern
        report_file = f"PYTHON_FILES_CLEANUP_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\n📄 Detaillierter Report gespeichert: {report_file}")

        # Sofortige Empfehlungen ausgeben
        self._print_immediate_recommendations()

    def _print_immediate_recommendations(self):
        """🎯 Sofortige Empfehlungen ausgeben"""

        print(f"\n🎯 SOFORTIGE EMPFEHLUNGEN:")

        backup_files = self.analysis_results['backup_files']
        demo_files = self.analysis_results['demo_files']
        cleanup_candidates = self.analysis_results['cleanup_candidates']

        if backup_files:
            backup_size = sum(f['size_kb'] for f in backup_files)
            print(f"   🗄️ BACKUP FILES: {len(backup_files)} Dateien ({backup_size:.1f} KB) → SOFORT LÖSCHEN")

        if demo_files:
            demo_size = sum(f['size_kb'] for f in demo_files)
            print(f"   🎬 DEMO FILES: {len(demo_files)} Dateien ({demo_size:.1f} KB) → OPTIONAL LÖSCHEN")

        if cleanup_candidates:
            cleanup_size = sum(f['size_kb'] for f in cleanup_candidates)
            print(f"   🧹 CLEANUP CANDIDATES: {len(cleanup_candidates)} Dateien ({cleanup_size:.1f} KB) → PRÜFEN & LÖSCHEN")

        essential_files = self.analysis_results['essential_files']
        print(f"   ✅ ESSENTIAL FILES: {len(essential_files)} Dateien → NIEMALS LÖSCHEN")

        total_deletable = len(backup_files) + len(demo_files) + len(cleanup_candidates)
        total_files = sum(len(files) for files in self.analysis_results.values())

        print(f"\n📊 CLEANUP POTENTIAL:")
        print(f"   📁 Potentiell löschbar: {total_deletable}/{total_files} Dateien ({total_deletable/total_files*100:.1f}%)")

        if backup_files:
            print(f"\n🚀 NEXT STEP: Backup-Dateien sofort löschen für {sum(f['size_kb'] for f in backup_files):.1f} KB Einsparung")

if __name__ == "__main__":
    print("🧹 PYTHON FILES CLEANUP ANALYSIS")
    print("=" * 50)

    analyzer = PythonFilesCleanupAnalyzer()
    analyzer.analyze_all_files()

    print("\n✅ Analyse abgeschlossen!")
    print("📄 Detaillierter Report wurde erstellt.")