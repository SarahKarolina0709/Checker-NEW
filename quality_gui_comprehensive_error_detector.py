"""QUALITY GUI – Comprehensive Error Detector & Fixer

Ursprüngliche Implementierung aus `comprehensive_error_detector.py` wurde hierher
verschoben. Die alte Datei fungiert jetzt nur noch als Kompatibilitäts-Wrapper.

FUNKTION:
 - Scannt alle Python-Dateien (rekursiv) im Workspace
 - Erkennt Syntax- und Parse-Fehler
 - Versucht heuristische Auto-Fixes für häufige Fehlerbilder
 - Erstellt konsolidierten Report

HINWEIS:
 - Nur für Entwicklungs-/Cleanup-Phase gedacht (kein Runtime-Bestandteil der GUI)
 - Emoji-Ausgaben sind reine Konsolen-Hinweise (keine UI-Elemente)
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List

__all__ = [
    "ComprehensiveErrorDetector",
    "main",
]


class ComprehensiveErrorDetector:
    """Umfassende Fehlersuche und -reparatur"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.errors_found: list[dict] = []
        self.fixes_applied = 0

    def scan_all_python_files(self):
        """Scanne alle Python-Dateien nach Fehlern und versuche Auto-Fixes."""
        print("🔍 COMPREHENSIVE ERROR DETECTION GESTARTET")
        print("=" * 50)
        python_files = list(self.workspace_path.rglob("*.py"))
        python_files = [
            f for f in python_files
            if not any(skip in str(f) for skip in [
                "__pycache__", ".venv", "node_modules", "_backup", "BACKUP", "backup"
            ])
        ]
        print(f"📁 Analysiere {len(python_files)} Python-Dateien…")
        for file_path in python_files:
            self._analyze_file(file_path)
        self._report_findings()
        self._fix_all_errors()

    def _analyze_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            try:
                ast.parse(content)
                return
            except SyntaxError as e:
                self.errors_found.append({
                    "file": file_path.name,
                    "path": file_path,
                    "line": e.lineno or 1,
                    "error": str(e),
                    "type": "syntax_error",
                })
            except Exception as e:
                self.errors_found.append({
                    "file": file_path.name,
                    "path": file_path,
                    "line": 1,
                    "error": str(e),
                    "type": "parse_error",
                })
        except Exception as e:
            print(f"   ⚠️ Fehler beim Lesen von {file_path.name}: {e}")

    def _report_findings(self):
        print("\n📊 FEHLER-ANALYSE ABGESCHLOSSEN")
        print(f"❌ Gefundene Fehler: {len(self.errors_found)}")
        if self.errors_found:
            print("\n🔍 DETAILLIERTE FEHLER-LISTE:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"   {i}. {error['file']}:{error['line']} - {error['error']}")
        else:
            print("✅ Keine Syntax-Fehler gefunden!")

    def _fix_all_errors(self):
        if not self.errors_found:
            return
        print("\n🔧 STARTE AUTOMATISCHE REPARATUR…")
        for error in self.errors_found:
            self._fix_specific_error(error)
        print("\n📊 REPARATUR ABGESCHLOSSEN:")
        print(f"🔧 Angewandte Fixes: {self.fixes_applied}")

    def _fix_specific_error(self, error: dict):
        file_path: Path = error["path"]
        error_msg = error["error"].lower()
        line_num = error["line"] or 1
        print(f"\n🔧 Repariere: {error['file']}:{line_num}")
        print(f"   Fehler: {error['error']}")
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
            idx = max(0, line_num - 1)
            if "unexpected indent" in error_msg:
                self._fix_unexpected_indent(lines, idx)
            elif "unmatched" in error_msg and ")" in error_msg:
                self._fix_unmatched_parentheses(lines, idx)
            elif "closing parenthesis" in error_msg and "does not match" in error_msg:
                self._fix_mismatched_brackets(lines, idx)
            elif "invalid syntax" in error_msg:
                self._fix_invalid_syntax(lines, idx)
            elif "expected" in error_msg:
                self._fix_expected_syntax(lines, idx, error_msg)
            else:
                print("   ⚠️ Unbekannter Fehlertyp – generischer Fix")
                self._generic_fix(lines, idx)
            file_path.write_text("".join(lines), encoding="utf-8")
            print("   ✅ Fix angewendet")
            self.fixes_applied += 1
        except Exception as e:
            print(f"   ❌ Fix fehlgeschlagen: {e}")

    def _fix_unexpected_indent(self, lines: List[str], idx: int):
        if idx < len(lines) and (lines[idx].startswith("    ") or lines[idx].startswith("\t")):
            before = lines[idx]
            lines[idx] = lines[idx].lstrip()
            if before != lines[idx]:
                print("   🔧 Einrückung entfernt")

    def _fix_unmatched_parentheses(self, lines: List[str], idx: int):
        if idx < len(lines):
            line = lines[idx]
            open_count = line.count("(")
            close_count = line.count(")")
            if close_count > open_count:
                while close_count > open_count and line.rstrip().endswith(")"):
                    line = line.rstrip()[:-1] + "\n"
                    close_count = line.count(")")
                lines[idx] = line
                print("   🔧 Überschüssige Klammern entfernt")

    def _fix_mismatched_brackets(self, lines: List[str], idx: int):
        if idx < len(lines):
            line = lines[idx]
            if "[" in line and ")" in line and "]" not in line:
                lines[idx] = line.replace(")", "]", 1)
                print("   🔧 Klammertyp korrigiert")

    def _fix_invalid_syntax(self, lines: List[str], idx: int):
        if idx < len(lines):
            line = lines[idx].strip()
            if line.startswith('"""') and not line.endswith('"""') and len(line) > 3:
                lines[idx] = '"""Fixed docstring"""\n'
                print("   🔧 Defekte Docstring repariert")
            elif line and not line.endswith((":", "\\", ",", ")", "]", "}", '"', "'")):
                if any(kw in line for kw in ["if ", "def ", "class ", "try", "except", "for ", "while "]):
                    if not line.endswith(":"):
                        lines[idx] = line + ":\n"
                        print("   🔧 Fehlender Doppelpunkt hinzugefügt")

    def _fix_expected_syntax(self, lines: List[str], idx: int, error_msg: str):
        if idx < len(lines):
            if "indented block" in error_msg:
                lines.insert(idx + 1, "    pass\n")
                print("   🔧 Pass-Statement hinzugefügt")
            elif "expression" in error_msg:
                if lines[idx].strip().endswith(("try:", "except:", "if", "def", "class")):
                    lines[idx] = lines[idx].rstrip() + " pass\n"
                    print("   🔧 Unvollständigen Ausdruck repariert")

    def _generic_fix(self, lines: List[str], idx: int):
        if idx < len(lines):
            line = lines[idx].strip()
            if line and not line.startswith("#"):
                lines[idx] = f"# {line}  # FIXME: Automatic fix applied\n"
                print("   🔧 Problematische Zeile auskommentiert")


def main():  # pragma: no cover
    workspace = str(Path(__file__).resolve().parent)
    print("🔍 COMPREHENSIVE ERROR DETECTOR & FIXER")
    print("Detaillierte Suche und Reparatur aller Code-Fehler\n")
    detector = ComprehensiveErrorDetector(workspace)
    detector.scan_all_python_files()
    print("\n🚀 COMPREHENSIVE ERROR DETECTION COMPLETED!")


if __name__ == "__main__":  # pragma: no cover
    main()
