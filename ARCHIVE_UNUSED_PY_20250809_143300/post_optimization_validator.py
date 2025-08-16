#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 POST-OPTIMIZATION VALIDATION
===============================

Validiert alle durchgeführten Optimierungen und analysiert
die manuellen Änderungen des Benutzers zur Bestimmung
der nächsten optimalen Schritte.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
import subprocess

class PostOptimizationValidator:
    """🔍 Validiert Post-Optimierungs-Status"""

    def __init__(self):
        self.validation_results = {
            'current_stats': {},
            'syntax_status': {},
            'file_changes': {},
            'recommendations': []
        }

    def validate_optimization_status(self):
        """🔍 Validiere aktuellen Optimierungs-Status"""
        print("🔍 POST-OPTIMIZATION VALIDATION GESTARTET!")
        print("=" * 50)

        # 1. Aktuelle Projekt-Statistiken
        self._analyze_current_stats()

        # 2. Syntax-Validierung nach manuellen Edits
        self._validate_syntax_status()

        # 3. Prüfe kritische Dateien
        self._check_critical_files()

        # 4. Performance-Status
        self._check_performance_status()

        # 5. Empfehlungen generieren
        self._generate_next_recommendations()

        # 6. Final Report
        self._create_validation_report()

        print("\n✅ POST-OPTIMIZATION VALIDATION ABGESCHLOSSEN!")

    def _analyze_current_stats(self):
        """📊 Analysiere aktuelle Projekt-Statistiken"""
        print("\n📊 AKTUELLE PROJEKT-STATISTIKEN:")

        stats = {
            'python_files': 0,
            'total_size_kb': 0,
            'large_files': [],
            'folders': 0,
            'syntax_errors': 0
        }

        # Zähle Python-Dateien und Größen
        for root, dirs, files in os.walk('.'):
            if '.git' in dirs:
                dirs.remove('.git')

            stats['folders'] += len(dirs)

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        size = file_path.stat().st_size
                        size_kb = size / 1024
                        stats['python_files'] += 1
                        stats['total_size_kb'] += size_kb

                        if size_kb > 50:  # Große Dateien >50KB
                            stats['large_files'].append({
                                'path': str(file_path.relative_to('.')),
                                'size_kb': round(size_kb, 1)
                            })
                    except Exception:
                        continue

        # Sortiere große Dateien
        stats['large_files'].sort(key=lambda x: x['size_kb'], reverse=True)

        self.validation_results['current_stats'] = stats

        print(f"   📁 Python-Dateien: {stats['python_files']}")
        print(f"   💾 Gesamt-Größe: {stats['total_size_kb']:.1f} KB")
        print(f"   🗂️ Ordner: {stats['folders']}")
        print(f"   📏 Große Dateien (>50KB): {len(stats['large_files'])}")

        if stats['large_files']:
            print(f"\n   📏 TOP 5 GRÖßTE DATEIEN:")
            for i, file_info in enumerate(stats['large_files'][:5], 1):
                print(f"      {i}. {file_info['path']} ({file_info['size_kb']} KB)")

    def _validate_syntax_status(self):
        """🔍 Validiere Syntax-Status nach manuellen Edits"""
        print(f"\n🔍 SYNTAX-VALIDIERUNG:")

        syntax_results = {
            'valid_files': 0,
            'syntax_errors': [],
            'import_errors': []
        }

        python_files = []
        for root, dirs, files in os.walk('.'):
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        print(f"   🔍 Prüfe {len(python_files)} Python-Dateien...")

        for file_path in python_files:
            try:
                # Syntax-Check mit ast
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                import ast
                try:
                    ast.parse(content)
                    syntax_results['valid_files'] += 1
                except SyntaxError as e:
                    syntax_results['syntax_errors'].append({
                        'file': str(file_path.relative_to('.')),
                        'error': str(e),
                        'line': getattr(e, 'lineno', 'unknown')
                    })

            except Exception as e:
                syntax_results['import_errors'].append({
                    'file': str(file_path.relative_to('.')),
                    'error': str(e)
                })

        self.validation_results['syntax_status'] = syntax_results

        print(f"   ✅ Valide Dateien: {syntax_results['valid_files']}")
        print(f"   ❌ Syntax-Fehler: {len(syntax_results['syntax_errors'])}")
        print(f"   ⚠️ Import-Probleme: {len(syntax_results['import_errors'])}")

        if syntax_results['syntax_errors']:
            print(f"\n   ❌ SYNTAX-FEHLER DETAILS:")
            for error in syntax_results['syntax_errors'][:5]:  # Zeige nur die ersten 5
                print(f"      - {error['file']}:{error['line']} - {error['error']}")

    def _check_critical_files(self):
        """🔍 Prüfe kritische Dateien"""
        print(f"\n🔍 KRITISCHE DATEIEN STATUS:")

        critical_files = [
            'modern_translation_quality_gui.py',
            'welcome_screen.py',
            'welcome_screen_main.py',
            'ui_theme.py',
            'design_system.py',
            'src/ui/smart_upload_calendar.py'
        ]

        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    size = os.path.getsize(file_path) / 1024
                    print(f"   ✅ {file_path}: {size:.1f} KB")

                    if size > 100:
                        print(f"      ⚠️ WARNUNG: Noch über 100KB (VS Code Risk)")
                except Exception:
                    print(f"   ❌ {file_path}: Fehler beim Lesen")
            else:
                print(f"   ❓ {file_path}: Nicht gefunden")

    def _check_performance_status(self):
        """⚡ Prüfe Performance-Status"""
        print(f"\n⚡ PERFORMANCE-STATUS:")

        # Prüfe auf häufige Performance-Probleme
        performance_issues = []

        # Große Dateien (>100KB)
        large_files = [f for f in self.validation_results['current_stats']['large_files']
                      if f['size_kb'] > 100]

        if large_files:
            performance_issues.append(f"🔥 {len(large_files)} Dateien >100KB (VS Code Risk)")

        # Syntax-Fehler
        syntax_errors = len(self.validation_results['syntax_status']['syntax_errors'])
        if syntax_errors > 0:
            performance_issues.append(f"❌ {syntax_errors} Syntax-Fehler behindern Performance")

        # Gesamtprojekt-Größe
        total_size = self.validation_results['current_stats']['total_size_kb']
        if total_size > 2000:  # >2MB
            performance_issues.append(f"💾 Projekt-Größe {total_size:.1f}KB - erwäge weitere Optimierung")

        if performance_issues:
            print(f"   ⚠️ PERFORMANCE-WARNUNGEN:")
            for issue in performance_issues:
                print(f"      - {issue}")
        else:
            print(f"   ✅ Performance-Status: OPTIMAL")

    def _generate_next_recommendations(self):
        """💡 Generiere nächste Empfehlungen"""
        print(f"\n💡 NÄCHSTE EMPFEHLUNGEN:")

        recommendations = []

        # Basierend auf aktuellen Statistiken
        large_files = [f for f in self.validation_results['current_stats']['large_files']
                      if f['size_kb'] > 100]

        if large_files:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Modularisiere große Dateien',
                'details': f"Noch {len(large_files)} Dateien >100KB vorhanden",
                'files': [f['path'] for f in large_files[:3]]
            })

        # Syntax-Probleme
        syntax_errors = self.validation_results['syntax_status']['syntax_errors']
        if syntax_errors:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Repariere Syntax-Fehler',
                'details': f"{len(syntax_errors)} Syntax-Fehler blockieren Funktionalität",
                'files': [e['file'] for e in syntax_errors[:3]]
            })

        # Weitere Optimierungen
        if not large_files and not syntax_errors:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Implementiere Lazy Loading',
                'details': 'Projekt ist optimiert - erweitere mit Lazy Loading',
                'files': []
            })

            recommendations.append({
                'priority': 'LOW',
                'action': 'Füge Unit Tests hinzu',
                'details': 'Stabilisiere Code mit Tests',
                'files': []
            })

        self.validation_results['recommendations'] = recommendations

        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {'CRITICAL': '🚨', 'HIGH': '🔥', 'MEDIUM': '⚡', 'LOW': '💡'}
            emoji = priority_emoji.get(rec['priority'], '📋')

            print(f"   {i}. {emoji} [{rec['priority']}] {rec['action']}")
            print(f"      {rec['details']}")
            if rec['files']:
                print(f"      Dateien: {', '.join(rec['files'])}")

    def _create_validation_report(self):
        """📄 Erstelle Validierungs-Report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report_content = []

        report_content.extend([
            "# 🔍 POST-OPTIMIZATION VALIDATION REPORT",
            "=" * 50,
            "",
            f"**Datum:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            f"**Validator:** Post-Optimization Validation System",
            "",
            "## 📊 AKTUELLE PROJEKT-STATISTIKEN:",
            ""
        ])

        stats = self.validation_results['current_stats']
        report_content.extend([
            f"- **Python-Dateien:** {stats['python_files']}",
            f"- **Gesamt-Größe:** {stats['total_size_kb']:.1f} KB",
            f"- **Ordner-Anzahl:** {stats['folders']}",
            f"- **Große Dateien (>50KB):** {len(stats['large_files'])}",
            ""
        ])

        # Syntax-Status
        syntax = self.validation_results['syntax_status']
        report_content.extend([
            "## 🔍 SYNTAX-VALIDATION:",
            "",
            f"- **Valide Dateien:** {syntax['valid_files']}",
            f"- **Syntax-Fehler:** {len(syntax['syntax_errors'])}",
            f"- **Import-Probleme:** {len(syntax['import_errors'])}",
            ""
        ])

        # Empfehlungen
        report_content.extend([
            "## 💡 NÄCHSTE SCHRITTE:",
            ""
        ])

        recommendations = self.validation_results['recommendations']
        for i, rec in enumerate(recommendations, 1):
            report_content.extend([
                f"### {i}. [{rec['priority']}] {rec['action']}",
                f"**Details:** {rec['details']}",
                ""
            ])

            if rec['files']:
                report_content.append("**Betroffene Dateien:**")
                for file in rec['files']:
                    report_content.append(f"- {file}")
                report_content.append("")

        # Schlussbewertung
        if not syntax['syntax_errors'] and len(stats['large_files']) == 0:
            report_content.extend([
                "## 🎯 BEWERTUNG: EXZELLENT",
                "",
                "✅ **Keine Syntax-Fehler**",
                "✅ **Keine kritischen großen Dateien**",
                "✅ **Projekt optimal strukturiert**",
                "✅ **VS Code Performance optimal**"
            ])
        elif len(syntax['syntax_errors']) > 0:
            report_content.extend([
                "## ⚠️ BEWERTUNG: KRITISCHE PROBLEME",
                "",
                "❌ **Syntax-Fehler müssen behoben werden**",
                "⚡ **Sofortige Aktion erforderlich**"
            ])
        else:
            report_content.extend([
                "## 📈 BEWERTUNG: GUTER FORTSCHRITT",
                "",
                "✅ **Syntax clean**",
                "⚡ **Weitere Optimierung empfohlen**"
            ])

        report_content.extend([
            "",
            "---",
            "*Generiert vom Post-Optimization Validator*"
        ])

        # Schreibe Report
        report_file = f"POST_OPTIMIZATION_VALIDATION_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))

        print(f"\n📄 Validierungs-Report erstellt: {report_file}")

if __name__ == "__main__":
    print("🔍 POST-OPTIMIZATION VALIDATION SYSTEM")
    print("=" * 50)

    validator = PostOptimizationValidator()
    validator.validate_optimization_status()
