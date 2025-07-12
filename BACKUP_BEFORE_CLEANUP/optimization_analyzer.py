"""
Checker App - Optimierungsanalyse und Empfehlungen
==================================================
Analyse der aktuellen Projektstruktur und Optimierungsmöglichkeiten.
"""

import os
import sys
import glob
from collections import defaultdict
import re


class CheckerOptimizationAnalyzer:
    """Analysiert die Checker-App auf Optimierungsmöglichkeiten."""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.analysis_results = {}
        
    def analyze_project_structure(self):
        """Analysiert die Projektstruktur."""
        print("🔍 CHECKER APP - OPTIMIERUNGSANALYSE")
        print("=" * 50)
        
        # Dateistatistiken
        self._analyze_file_statistics()
        
        # Code-Duplikate
        self._analyze_code_duplicates()
        
        # Import-Abhängigkeiten
        self._analyze_import_dependencies()
        
        # Ungenutzter Code
        self._analyze_unused_files()
        
        # Modulorganisation
        self._analyze_module_organization()
        
        # Optimierungsempfehlungen
        self._generate_optimization_recommendations()
        
    def _analyze_file_statistics(self):
        """Analysiert Dateistatistiken."""
        print("\n📊 DATEISTATISTIKEN:")
        print("-" * 30)
        
        py_files = glob.glob(os.path.join(self.project_path, "*.py"))
        test_files = [f for f in py_files if "test_" in os.path.basename(f)]
        debug_files = [f for f in py_files if "debug_" in os.path.basename(f)]
        temp_files = [f for f in py_files if any(x in os.path.basename(f) for x in ["temp", "backup", "old", "copy"])]
        
        print(f"📄 Gesamt Python-Dateien: {len(py_files)}")
        print(f"🧪 Test-Dateien: {len(test_files)}")
        print(f"🐛 Debug-Dateien: {len(debug_files)}")
        print(f"⚠️  Temporäre/Backup-Dateien: {len(temp_files)}")
        
        # Dateigröße
        large_files = []
        total_lines = 0
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    
                    if lines > 500:
                        large_files.append((os.path.basename(file_path), lines))
            except:
                pass
        
        print(f"📝 Gesamtzeilen Code: {total_lines:,}")
        print(f"🔍 Große Dateien (>500 Zeilen): {len(large_files)}")
        
        if large_files:
            print("\n📋 Größte Dateien:")
            for filename, lines in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {filename}: {lines:,} Zeilen")
        
        self.analysis_results['file_stats'] = {
            'total_files': len(py_files),
            'test_files': len(test_files),
            'debug_files': len(debug_files),
            'temp_files': len(temp_files),
            'large_files': large_files,
            'total_lines': total_lines
        }
    
    def _analyze_code_duplicates(self):
        """Analysiert potenzielle Code-Duplikate."""
        print("\n🔄 CODE-DUPLIKATE ANALYSE:")
        print("-" * 30)
        
        # Häufige Dateinamen-Muster
        py_files = glob.glob(os.path.join(self.project_path, "*.py"))
        basename_patterns = defaultdict(list)
        
        for file_path in py_files:
            basename = os.path.basename(file_path)
            
            # Ähnliche Namen finden
            base_name = re.sub(r'(_\d+|_old|_new|_copy|_backup|_test)', '', basename)
            basename_patterns[base_name].append(basename)
        
        duplicates = {k: v for k, v in basename_patterns.items() if len(v) > 1}
        
        if duplicates:
            print("⚠️  Potenzielle Duplikate gefunden:")
            for base, files in duplicates.items():
                if len(files) > 1:
                    print(f"   • {base}: {', '.join(files)}")
        else:
            print("✅ Keine offensichtlichen Datei-Duplikate gefunden")
        
        self.analysis_results['duplicates'] = duplicates
    
    def _analyze_import_dependencies(self):
        """Analysiert Import-Abhängigkeiten."""
        print("\n🔗 IMPORT-ABHÄNGIGKEITEN:")
        print("-" * 30)
        
        py_files = glob.glob(os.path.join(self.project_path, "*.py"))
        import_counts = defaultdict(int)
        local_imports = defaultdict(list)
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    filename = os.path.basename(file_path)
                    
                    # Standard-Imports zählen
                    for line in content.split('\n'):
                        if line.strip().startswith(('import ', 'from ')):
                            import_counts[line.strip()] += 1
                            
                            # Lokale Imports identifizieren
                            if any(local_file.replace('.py', '') in line for local_file in [os.path.basename(f) for f in py_files]):
                                local_imports[filename].append(line.strip())
            except:
                pass
        
        # Häufigste Imports
        most_common = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("📦 Häufigste Imports:")
        for imp, count in most_common:
            print(f"   • {imp[:50]}... ({count}x)")
        
        # Dateien mit vielen lokalen Imports
        heavy_deps = {k: v for k, v in local_imports.items() if len(v) > 5}
        if heavy_deps:
            print(f"\n🔗 Dateien mit vielen lokalen Abhängigkeiten:")
            for filename, deps in heavy_deps.items():
                print(f"   • {filename}: {len(deps)} lokale Imports")
        
        self.analysis_results['imports'] = {
            'most_common': most_common,
            'heavy_dependencies': heavy_deps
        }
    
    def _analyze_unused_files(self):
        """Analysiert potenziell ungenutzte Dateien."""
        print("\n❌ POTENZIELL UNGENUTZTE DATEIEN:")
        print("-" * 30)
        
        py_files = glob.glob(os.path.join(self.project_path, "*.py"))
        all_content = ""
        
        # Alle Dateiinhalte sammeln
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except:
                pass
        
        # Prüfen, welche Dateien nicht importiert werden
        potentially_unused = []
        
        for file_path in py_files:
            filename = os.path.basename(file_path).replace('.py', '')
            
            # Überspringen von offensichtlich wichtigen Dateien
            if filename in ['checker_app', '__init__', 'main']:
                continue
                
            # Prüfen, ob Dateiname in anderen Dateien vorkommt
            import_count = all_content.count(filename)
            
            if import_count <= 2:  # Nur eigene Definition
                potentially_unused.append(filename)
        
        if potentially_unused:
            print("⚠️  Potenziell ungenutzte Dateien:")
            for filename in potentially_unused[:10]:  # Zeige nur erste 10
                print(f"   • {filename}.py")
            
            if len(potentially_unused) > 10:
                print(f"   ... und {len(potentially_unused) - 10} weitere")
        else:
            print("✅ Alle Dateien scheinen verwendet zu werden")
        
        self.analysis_results['unused'] = potentially_unused
    
    def _analyze_module_organization(self):
        """Analysiert die Modulorganisation."""
        print("\n📁 MODULORGANISATION:")
        print("-" * 30)
        
        py_files = glob.glob(os.path.join(self.project_path, "*.py"))
        
        # Kategorisierung nach Dateinamen
        categories = {
            'ui': [],
            'workflow': [],
            'icon': [],
            'test': [],
            'debug': [],
            'modern': [],
            'nuclear': [],
            'core': [],
            'temp': [],
            'other': []
        }
        
        for file_path in py_files:
            filename = os.path.basename(file_path).lower()
            
            if any(x in filename for x in ['ui', 'component', 'theme', 'animation']):
                categories['ui'].append(filename)
            elif 'workflow' in filename:
                categories['workflow'].append(filename)
            elif 'icon' in filename:
                categories['icon'].append(filename)
            elif 'test_' in filename:
                categories['test'].append(filename)
            elif 'debug_' in filename:
                categories['debug'].append(filename)
            elif 'modern' in filename:
                categories['modern'].append(filename)
            elif 'nuclear' in filename:
                categories['nuclear'].append(filename)
            elif filename.startswith('core'):
                categories['core'].append(filename)
            elif any(x in filename for x in ['temp', 'backup', 'old', 'copy']):
                categories['temp'].append(filename)
            else:
                categories['other'].append(filename)
        
        for category, files in categories.items():
            if files:
                print(f"📂 {category.upper()}: {len(files)} Dateien")
        
        self.analysis_results['organization'] = categories
    
    def _generate_optimization_recommendations(self):
        """Generiert Optimierungsempfehlungen."""
        print("\n🚀 OPTIMIERUNGSEMPFEHLUNGEN:")
        print("=" * 50)
        
        recommendations = []
        
        # 1. Aufräumen von temporären Dateien
        temp_files = self.analysis_results['organization']['temp']
        if temp_files:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Cleanup',
                'title': 'Temporäre Dateien entfernen',
                'description': f'{len(temp_files)} temporäre/Backup-Dateien können gelöscht werden',
                'files': temp_files[:5],
                'action': 'DELETE'
            })
        
        # 2. Code-Duplikate zusammenführen
        duplicates = self.analysis_results['duplicates']
        if duplicates:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Refactoring',
                'title': 'Code-Duplikate zusammenführen',
                'description': f'{len(duplicates)} potenzielle Duplikate gefunden',
                'files': list(duplicates.keys())[:5],
                'action': 'MERGE'
            })
        
        # 3. Modulorganisation verbessern
        if self.analysis_results['file_stats']['total_files'] > 100:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Structure',
                'title': 'Modulstruktur verbessern',
                'description': 'Dateien in thematische Ordner organisieren',
                'files': ['ui/', 'workflows/', 'icons/', 'tests/', 'utils/'],
                'action': 'REORGANIZE'
            })
        
        # 4. Große Dateien aufteilen
        large_files = self.analysis_results['file_stats']['large_files']
        very_large = [f for f in large_files if f[1] > 1000]
        if very_large:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Refactoring',
                'title': 'Große Dateien aufteilen',
                'description': f'{len(very_large)} sehr große Dateien (>1000 Zeilen)',
                'files': [f[0] for f in very_large[:3]],
                'action': 'SPLIT'
            })
        
        # 5. Test-Coverage verbessern
        test_files = self.analysis_results['file_stats']['test_files']
        total_files = self.analysis_results['file_stats']['total_files']
        test_ratio = test_files / total_files if total_files > 0 else 0
        
        if test_ratio < 0.1:  # Weniger als 10% Tests
            recommendations.append({
                'priority': 'LOW',
                'category': 'Testing',
                'title': 'Test-Coverage erhöhen',
                'description': f'Nur {test_files} von {total_files} Dateien sind Tests',
                'files': ['Haupt-Module testen'],
                'action': 'CREATE_TESTS'
            })
        
        # Empfehlungen ausgeben
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            print(f"\n{i}. {priority_icon[rec['priority']]} {rec['title']} ({rec['priority']})")
            print(f"   📋 {rec['description']}")
            if rec['files']:
                print(f"   📁 Betroffen: {', '.join(rec['files'])}")
            print(f"   🔧 Aktion: {rec['action']}")
        
        return recommendations
    
    def generate_cleanup_script(self):
        """Generiert ein Cleanup-Script."""
        print("\n🧹 CLEANUP-SCRIPT GENERIEREN:")
        print("-" * 30)
        
        script_content = """#!/usr/bin/env python3
'''
Checker App - Automatisches Cleanup Script
==========================================
ACHTUNG: Führen Sie dieses Script nur nach einem Backup aus!
'''

import os
import shutil
from pathlib import Path

def cleanup_checker_app():
    '''Räumt die Checker-App auf.'''
    
    # Temporäre und Backup-Dateien
    temp_patterns = [
        '*_old.py', '*_backup.py', '*_copy.py', '*_temp.py',
        '*_test.py.bak', '*.pyc', '__pycache__'
    ]
    
    # Debug-Dateien (nach Überprüfung)
    debug_files = [
        'debug_*.py', 'test_*.py'  # Nur nach Bestätigung
    ]
    
    print("🧹 Starte Cleanup...")
    
    # 1. Temporäre Dateien entfernen
    for pattern in temp_patterns:
        for file_path in Path('.').glob(pattern):
            print(f"❌ Entferne: {file_path}")
            # file_path.unlink()  # Auskommentiert für Sicherheit
    
    # 2. Leere Ordner entfernen
    for dir_path in Path('.').iterdir():
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            print(f"📁 Entferne leeren Ordner: {dir_path}")
            # dir_path.rmdir()  # Auskommentiert für Sicherheit
    
    print("✅ Cleanup abgeschlossen!")

if __name__ == "__main__":
    print("⚠️  WARNUNG: Dieses Script löscht Dateien!")
    print("   Erstellen Sie ein Backup vor der Ausführung!")
    # cleanup_checker_app()  # Auskommentiert für Sicherheit
"""
        
        with open(os.path.join(self.project_path, 'cleanup_script.py'), 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("✅ Cleanup-Script erstellt: cleanup_script.py")
        print("⚠️  WARNUNG: Script vor Verwendung anpassen und testen!")


def main():
    """Hauptfunktion für die Optimierungsanalyse."""
    project_path = r"C:\Users\sarah\Desktop\Checker"
    
    if not os.path.exists(project_path):
        print(f"❌ Projektpfad nicht gefunden: {project_path}")
        return
    
    analyzer = CheckerOptimizationAnalyzer(project_path)
    analyzer.analyze_project_structure()
    analyzer.generate_cleanup_script()
    
    print("\n" + "=" * 50)
    print("📊 ZUSAMMENFASSUNG:")
    print("✅ Analyse abgeschlossen")
    print("📋 Empfehlungen generiert")
    print("🧹 Cleanup-Script erstellt")
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("1. Backup der gesamten Anwendung erstellen")
    print("2. Temporäre Dateien nach Überprüfung löschen")
    print("3. Module in thematische Ordner organisieren")
    print("4. Code-Duplikate zusammenführen")
    print("5. Performance-Tests durchführen")


if __name__ == "__main__":
    main()
