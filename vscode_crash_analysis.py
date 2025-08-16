#!/usr/bin/env python3
"""
🚨 VS CODE CRASH ANALYSIS - Diagnose VS Code Abstürze
Analysiert potentielle Ursachen für VS Code Crashes im Checker-Projekt
"""


from pathlib import Path
import json
import traceback

import psutil

class VSCodeCrashAnalyzer:
    def __init__(self):
        self.project_path = Path(".")
        self.analysis_results = {}

    def analyze_file_sizes(self):
        """🔍 Analysiere Dateigrößen - Große Dateien können VS Code überlasten"""
        print("🔍 DATEIGRÖSSEN-ANALYSE:")
        python_files = list(self.project_path.glob("*.py"))

        large_files = []
        total_size = 0

        for file in python_files:
            size_kb = file.stat().st_size / 1024
            total_size += size_kb

            if size_kb > 200:  # Dateien über 200KB
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for _ in f)
                large_files.append({
                    'file': file.name,
                    'size_kb': round(size_kb, 1),
                    'lines': lines
                })

        large_files.sort(key=lambda x: x['size_kb'], reverse=True)

        print(f"📊 Gesamt Python-Code: {round(total_size/1024, 2)} MB")
        print(f"📄 Anzahl Python-Dateien: {len(python_files)}")

        if large_files:
            print("\n🚨 KRITISCH GROSSE DATEIEN:")
            for file in large_files[:5]:
                print(f"   {file['file']}: {file['size_kb']} KB ({file['lines']} Zeilen)")
                if file['size_kb'] > 400:
                    print(f"   ⚠️  SEHR GROSS - kann VS Code überlasten!")

        self.analysis_results['file_sizes'] = {
            'total_size_mb': round(total_size/1024, 2),
            'large_files': large_files,
            'total_files': len(python_files)
        }

        return large_files

    def analyze_memory_patterns(self):
        """🧠 Analysiere Memory-intensive Code-Pattern"""
        print("\n🧠 MEMORY-PATTERN ANALYSE:")

        memory_issues = []

        # Prüfe auf potentielle Memory-Leaks
        patterns_to_check = [
            ("Global Variables", r"^[A-Z_]+ = ", "Globale Variablen können Memory-Leaks verursachen"),
            ("Large Data Structures", r".*\[.*\].*=.*\[.*\]", "Große Listen/Dicts ohne cleanup"),
            ("Threading ohne Cleanup", r"threading\.Thread.*", "Threads ohne proper cleanup"),
            ("Async ohne await", r"async def.*", "Async-Funktionen ohne proper handling"),
            ("File Handles", r"open\(.*\)", "File-Handles ohne with-statement"),
            ("Event Bindings", r"\.bind\(.*\)", "Event-Bindings ohne unbind")
        ]

        python_files = [f for f in self.project_path.glob("*.py") if f.stat().st_size < 1024*1024]  # Nur Dateien unter 1MB

        for pattern_name, pattern, description in patterns_to_check:
            count = 0
            files_with_pattern = []

            for file in python_files:
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        import re
                        matches = re.findall(pattern, content, re.MULTILINE)
                        if matches:
                            count += len(matches)
                            files_with_pattern.append(file.name)
                except Exception:
                    continue

            if count > 0:
                memory_issues.append({
                    'pattern': pattern_name,
                    'count': count,
                    'files': files_with_pattern,
                    'description': description
                })

        if memory_issues:
            print("🚨 POTENTIELLE MEMORY-PROBLEME:")
            for issue in memory_issues:
                print(f"   {issue['pattern']}: {issue['count']} Vorkommen")
                print(f"   📝 {issue['description']}")
                if len(issue['files']) <= 3:
                    print(f"   📄 Dateien: {', '.join(issue['files'])}")
                print()

        self.analysis_results['memory_patterns'] = memory_issues
        return memory_issues

    def analyze_vs_code_load(self):
        """⚡ Analysiere VS Code Belastung"""
        print("⚡ VS CODE BELASTUNGS-ANALYSE:")

        try:
            # Prüfe VS Code Prozesse
            vscode_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                if 'code' in proc.info['name'].lower():
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    vscode_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': round(memory_mb, 1)
                    })

            total_memory = sum(proc['memory_mb'] for proc in vscode_processes)

            print(f"🖥️  VS Code Prozesse: {len(vscode_processes)}")
            print(f"💾 Gesamt VS Code Memory: {round(total_memory, 1)} MB")

            if total_memory > 2000:  # Über 2GB
                print("🚨 KRITISCH: VS Code verwendet sehr viel Speicher!")
            elif total_memory > 1000:  # Über 1GB
                print("⚠️  WARNUNG: VS Code Memory-Verbrauch hoch")

            # Prüfe System-Memory
            system_memory = psutil.virtual_memory()
            memory_usage_percent = (total_memory / (system_memory.total / 1024 / 1024)) * 100

            print(f"📊 VS Code Memory-Anteil: {round(memory_usage_percent, 1)}% vom System")

            self.analysis_results['vscode_load'] = {
                'processes': len(vscode_processes),
                'total_memory_mb': round(total_memory, 1),
                'memory_percentage': round(memory_usage_percent, 1)
            }

        except Exception as e:
            print(f"❌ Fehler bei VS Code Analyse: {e}")
            self.analysis_results['vscode_load'] = {'error': str(e)}

    def check_extension_conflicts(self):
        """🔌 Prüfe auf Extension-Konflikte"""
        print("\n🔌 EXTENSION-KONFLIKT ANALYSE:")

        # Prüfe auf bekannte problematische Pattern
        conflict_indicators = [
            "Multiple Python Language Servers",
            "Competing Linters (pylint + flake8 + black)",
            "Heavy Extensions (AI-Assistants multiple)",
            "Auto-Save mit großen Dateien"
        ]

        print("📋 Bekannte problematische Extension-Kombinationen:")
        for indicator in conflict_indicators:
            print(f"   ⚠️  {indicator}")

        print("\n💡 EMPFOHLENE EXTENSION-OPTIMIERUNGEN:")
        print("   ✅ Nur eine Python Language Server aktivieren")
        print("   ✅ Auto-Save für große Dateien deaktivieren")
        print("   ✅ Heavy AI-Extensions temporär deaktivieren")
        print("   ✅ File Watcher für große Ordner limitieren")

    def generate_recommendations(self):
        """💡 Generiere Lösungsempfehlungen"""
        print("\n💡 CRASH-PREVENTION EMPFEHLUNGEN:")

        recommendations = []

        # Basierend auf Dateigrößen
        large_files = self.analysis_results.get('file_sizes', {}).get('large_files', [])
        if large_files:
            for file in large_files[:3]:
                if file['size_kb'] > 400:
                    recommendations.append(f"🔧 {file['file']} ({file['size_kb']} KB) in Module aufteilen")

        # Basierend auf Memory-Pattern
        memory_issues = self.analysis_results.get('memory_patterns', [])
        if memory_issues:
            for issue in memory_issues:
                if issue['count'] > 10:
                    recommendations.append(f"🧠 {issue['pattern']}: Cleanup-Pattern implementieren")

        # VS Code spezifische Empfehlungen
        vscode_load = self.analysis_results.get('vscode_load', {})
        if vscode_load.get('total_memory_mb', 0) > 1500:
            recommendations.append("⚡ VS Code neustarten (hoher Memory-Verbrauch)")
            recommendations.append("🔌 Heavy Extensions temporär deaktivieren")

        # Allgemeine Empfehlungen
        recommendations.extend([
            "📁 Große Dateien in kleinere Module aufteilen",
            "🧹 Regelmäßig VS Code neustarten bei großen Projekten",
            "⚙️ TypeScript/JavaScript Language Server für Python deaktivieren",
            "💾 Auto-Save Intervall erhöhen oder deaktivieren",
            "🔍 File Watcher für große Verzeichnisse limitieren"
        ])

        print("\n🎯 SOFORT-MASSNAHMEN:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")

        return recommendations

    def create_crash_report(self):
        """📄 Erstelle detaillierten Crash-Report"""
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"vscode_crash_analysis_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Crash-Report gespeichert: {report_file}")
        return report_file

    def run_full_analysis(self):
        """🚀 Führe komplette Crash-Analyse durch"""
        print("🚨 VS CODE CRASH ANALYSIS - CHECKER PROJECT")
        print("=" * 60)

        try:
            self.analyze_file_sizes()
            self.analyze_memory_patterns()
            self.analyze_vs_code_load()
            self.check_extension_conflicts()
            self.generate_recommendations()

            report_file = self.create_crash_report()

            print("\n✅ ANALYSE COMPLETE")
            print(f"📊 Report: {report_file}")

        except Exception as e:
            print(f"❌ Fehler bei Analyse: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    analyzer = VSCodeCrashAnalyzer()
    analyzer.run_full_analysis()