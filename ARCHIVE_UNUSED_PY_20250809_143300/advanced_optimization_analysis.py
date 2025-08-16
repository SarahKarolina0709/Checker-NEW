#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ADVANCED OPTIMIZATION ANALYSIS
=================================

Erweiterte Analyse zur Identifikation weiterer Optimierungsmöglichkeiten:
- Große Dateien (Performance-Impact)
- Ungenutzte Imports
- Redundante Funktionen
- Code-Komplexität
- Optimierungspotential
"""

from collections import defaultdict, Counter
from pathlib import Path
import ast
import os

class AdvancedOptimizationAnalyzer:
    """🚀 Erweiterte Optimierungs-Analyse"""

    def __init__(self):
        self.analysis_results = {
            'large_files': [],
            'complex_files': [],
            'unused_imports': [],
            'redundant_functions': [],
            'optimization_candidates': [],
            'statistics': {}
        }

    def analyze_project_optimization(self):
        """🔍 Führe umfassende Optimierungs-Analyse durch"""
        print("🚀 Starte erweiterte Optimierungs-Analyse...")

        all_python_files = self._collect_python_files()
        print(f"📊 Analysiere {len(all_python_files)} Python-Dateien...")

        # Verschiedene Analysen durchführen
        self._analyze_file_sizes(all_python_files)
        self._analyze_code_complexity(all_python_files)
        self._analyze_imports(all_python_files)
        self._analyze_functions(all_python_files)
        self._generate_optimization_report()

    def _collect_python_files(self):
        """📁 Sammle alle Python-Dateien"""
        files = []
        for root, dirs, filenames in os.walk('.'):
            if '.git' in dirs:
                dirs.remove('.git')

            for filename in filenames:
                if filename.endswith('.py'):
                    file_path = Path(root) / filename
                    try:
                        size = file_path.stat().st_size
                        files.append({
                            'path': file_path,
                            'relative_path': str(file_path.relative_to('.')),
                            'name': filename,
                            'size_kb': round(size / 1024, 2),
                            'size_bytes': size
                        })
                    except Exception as e:
                        print(f"❌ Fehler bei {file_path}: {e}")

        return files

    def _analyze_file_sizes(self, files):
        """📏 Analysiere Dateigrößen"""
        print("📏 Analysiere Dateigrößen...")

        # Sortiere nach Größe
        large_files = sorted([f for f in files if f['size_kb'] > 20],
                           key=lambda x: x['size_kb'], reverse=True)

        self.analysis_results['large_files'] = large_files

        # Statistiken
        total_size = sum(f['size_kb'] for f in files)
        avg_size = total_size / len(files) if files else 0

        self.analysis_results['statistics']['total_size_kb'] = total_size
        self.analysis_results['statistics']['average_size_kb'] = avg_size
        self.analysis_results['statistics']['total_files'] = len(files)

    def _analyze_code_complexity(self, files):
        """🧮 Analysiere Code-Komplexität"""
        print("🧮 Analysiere Code-Komplexität...")

        complex_files = []

        for file_info in files:
            try:
                complexity = self._calculate_file_complexity(file_info['path'])
                if complexity and complexity['total_complexity'] > 50:
                    file_info['complexity'] = complexity
                    complex_files.append(file_info)
            except Exception as e:
                continue

        # Sortiere nach Komplexität
        complex_files.sort(key=lambda x: x.get('complexity', {}).get('total_complexity', 0), reverse=True)
        self.analysis_results['complex_files'] = complex_files

    def _calculate_file_complexity(self, file_path):
        """📊 Berechne Komplexität einer Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            complexity_data = {
                'lines_of_code': len(content.splitlines()),
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'nested_levels': 0,
                'total_complexity': 0
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity_data['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    complexity_data['classes'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    complexity_data['imports'] += 1
                elif isinstance(node, (ast.For, ast.While, ast.If, ast.Try)):
                    complexity_data['nested_levels'] += 1

            # Berechne Gesamt-Komplexität
            complexity_data['total_complexity'] = (
                complexity_data['lines_of_code'] * 0.1 +
                complexity_data['functions'] * 2 +
                complexity_data['classes'] * 3 +
                complexity_data['nested_levels'] * 1.5
            )

            return complexity_data

        except Exception:
            return None

    def _analyze_imports(self, files):
        """📦 Analysiere Imports"""
        print("📦 Analysiere Imports...")

        import_analysis = {}
        all_imports = Counter()

        for file_info in files:
            try:
                imports = self._extract_imports(file_info['path'])
                if imports:
                    import_analysis[file_info['relative_path']] = imports
                    all_imports.update(imports)
            except Exception:
                continue

        # Finde häufig verwendete Imports
        common_imports = all_imports.most_common(10)

        self.analysis_results['import_analysis'] = {
            'file_imports': import_analysis,
            'common_imports': common_imports,
            'total_unique_imports': len(all_imports)
        }

    def _extract_imports(self, file_path):
        """📦 Extrahiere Imports aus Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return imports
        except Exception:
            return []

    def _analyze_functions(self, files):
        """🔧 Analysiere Funktionen"""
        print("🔧 Analysiere Funktionen...")

        all_functions = defaultdict(list)

        for file_info in files:
            try:
                functions = self._extract_functions(file_info['path'])
                for func in functions:
                    all_functions[func['name']].append({
                        'file': file_info['relative_path'],
                        'line': func['line'],
                        'length': func['length']
                    })
            except Exception:
                continue

        # Finde potentiell redundante Funktionen (gleicher Name)
        redundant_functions = {name: locations for name, locations in all_functions.items()
                             if len(locations) > 1 and not name.startswith('_')}

        self.analysis_results['redundant_functions'] = redundant_functions

    def _extract_functions(self, file_path):
        """🔧 Extrahiere Funktionen aus Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()

            tree = ast.parse(content)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'length': func_length
                    })

            return functions
        except Exception:
            return []

    def _generate_optimization_report(self):
        """📄 Generiere Optimierungs-Report"""
        print(f"\n🚀 ERWEITERTE OPTIMIERUNGS-ANALYSE:")

        stats = self.analysis_results['statistics']
        large_files = self.analysis_results['large_files']
        complex_files = self.analysis_results['complex_files']
        redundant_functions = self.analysis_results['redundant_functions']

        print(f"\n📊 PROJECT STATISTICS:")
        print(f"   📁 Total Dateien: {stats.get('total_files', 0)}")
        print(f"   💾 Gesamt-Größe: {stats.get('total_size_kb', 0):.1f} KB")
        print(f"   📏 Durchschnitt: {stats.get('average_size_kb', 0):.1f} KB/Datei")

        # Große Dateien
        if large_files:
            print(f"\n📏 GROSSE DATEIEN (>20 KB):")
            for i, file_info in enumerate(large_files[:10], 1):  # Top 10
                print(f"   {i:2d}. {file_info['relative_path']:50} {file_info['size_kb']:6.1f} KB")

        # Komplexe Dateien
        if complex_files:
            print(f"\n🧮 KOMPLEXE DATEIEN (>50 Komplexität):")
            for i, file_info in enumerate(complex_files[:10], 1):  # Top 10
                complexity = file_info.get('complexity', {})
                total_complexity = complexity.get('total_complexity', 0)
                lines = complexity.get('lines_of_code', 0)
                functions = complexity.get('functions', 0)
                classes = complexity.get('classes', 0)

                print(f"   {i:2d}. {file_info['relative_path']:50}")
                print(f"       Komplexität: {total_complexity:6.1f} | Zeilen: {lines:4d} | Funktionen: {functions:2d} | Klassen: {classes:2d}")

        # Redundante Funktionen
        if redundant_functions:
            print(f"\n🔧 POTENTIELL REDUNDANTE FUNKTIONEN:")
            for func_name, locations in list(redundant_functions.items())[:10]:  # Top 10
                print(f"   🔧 '{func_name}' gefunden in {len(locations)} Dateien:")
                for location in locations:
                    print(f"      - {location['file']}:{location['line']}")

        # Import-Analyse
        import_analysis = self.analysis_results.get('import_analysis', {})
        common_imports = import_analysis.get('common_imports', [])
        if common_imports:
            print(f"\n📦 HÄUFIG VERWENDETE IMPORTS:")
            for import_name, count in common_imports[:10]:
                print(f"   📦 {import_name:30} ({count} mal verwendet)")

        # Optimierungsempfehlungen
        self._generate_optimization_recommendations()

    def _generate_optimization_recommendations(self):
        """💡 Generiere Optimierungsempfehlungen"""
        print(f"\n💡 OPTIMIERUNGSEMPFEHLUNGEN:")

        large_files = self.analysis_results['large_files']
        complex_files = self.analysis_results['complex_files']
        redundant_functions = self.analysis_results['redundant_functions']

        recommendations = []

        # Große Dateien
        if large_files:
            very_large = [f for f in large_files if f['size_kb'] > 100]
            if very_large:
                recommendations.append(f"🔥 CRITICAL: {len(very_large)} Dateien >100KB können VS Code verlangsamen")
                for file_info in very_large[:5]:
                    recommendations.append(f"   → Modularisiere: {file_info['relative_path']} ({file_info['size_kb']:.1f} KB)")

        # Komplexe Dateien
        if complex_files:
            very_complex = [f for f in complex_files if f.get('complexity', {}).get('total_complexity', 0) > 100]
            if very_complex:
                recommendations.append(f"🧮 REFACTORING: {len(very_complex)} sehr komplexe Dateien")
                for file_info in very_complex[:3]:
                    complexity = file_info.get('complexity', {}).get('total_complexity', 0)
                    recommendations.append(f"   → Vereinfache: {file_info['relative_path']} (Komplexität: {complexity:.1f})")

        # Redundante Funktionen
        if redundant_functions:
            high_redundancy = {k: v for k, v in redundant_functions.items() if len(v) > 2}
            if high_redundancy:
                recommendations.append(f"🔧 CONSOLIDATION: {len(high_redundancy)} Funktionen mehrfach vorhanden")
                for func_name, locations in list(high_redundancy.items())[:3]:
                    recommendations.append(f"   → Konsolidiere '{func_name}' ({len(locations)} Vorkommen)")

        # Performance-Optimierungen
        stats = self.analysis_results['statistics']
        total_size = stats.get('total_size_kb', 0)
        if total_size > 1000:  # >1MB
            recommendations.append(f"⚡ PERFORMANCE: Projekt-Größe {total_size:.1f} KB - erwäge Lazy Loading")

        # Ausgabe der Empfehlungen
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   ✅ Keine kritischen Optimierungen erforderlich!")

        # Nächste Schritte
        self._suggest_next_steps()

    def _suggest_next_steps(self):
        """📋 Schlage nächste Schritte vor"""
        print(f"\n📋 VORGESCHLAGENE NÄCHSTE SCHRITTE:")

        large_files = self.analysis_results['large_files']
        complex_files = self.analysis_results['complex_files']

        steps = []

        if large_files:
            very_large = [f for f in large_files if f['size_kb'] > 50]
            if very_large:
                steps.append("1. 🔧 Modularisiere große Dateien (>50 KB)")
                steps.append(f"   → Starte mit: {very_large[0]['relative_path']}")

        if complex_files:
            steps.append("2. 🧮 Refaktoriere komplexe Dateien")
            steps.append(f"   → Vereinfache Logik und reduziere Verschachtelung")

        steps.append("3. 📦 Prüfe ungenutzte Imports")
        steps.append("4. 🔧 Konsolidiere redundante Funktionen")
        steps.append("5. ⚡ Implementiere Lazy Loading für große Module")
        steps.append("6. 🧪 Füge Unit Tests hinzu")
        steps.append("7. 📖 Aktualisiere Dokumentation")

        for step in steps:
            print(f"   {step}")

if __name__ == "__main__":
    print("🚀 ADVANCED OPTIMIZATION ANALYSIS")
    print("=" * 50)

    analyzer = AdvancedOptimizationAnalyzer()
    analyzer.analyze_project_optimization()

    print("\n✅ Erweiterte Optimierungs-Analyse abgeschlossen!")