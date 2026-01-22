"""Quality GUI Diagnose-Tool (umbenannt von diagnose_quality_gui.py).

Führt Syntax-, Import-, Klassen- und Unicode-Checks für die geschützte GUI-Datei
`modern_translation_quality_gui.py` aus. Aufrufbar direkt als Script.
"""
from __future__ import annotations
import ast
import importlib.util
import os
from pathlib import Path
from typing import Optional

def check_syntax(file_path: str) -> bool:
    print("🔍 SYNTAX-CHECK...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print("✅ Syntax OK")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler: {e}")
        print(f"   Zeile {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Unbekannter Syntax-Fehler: {e}")
        return False

def check_imports(file_path: str) -> bool:
    print("\n📦 IMPORT-CHECK...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        import_lines = [l for l in lines if l.strip().startswith(('import ', 'from '))]
        failed = []
        for line in import_lines[:10]:
            try:
                exec(line.strip(), {})
            except ImportError as e:
                failed.append((line.strip(), str(e)))
            except Exception:
                pass
        if failed:
            print(f"⚠️  {len(failed)} problematische Imports")
            for imp, err in failed:
                print(f"   - {imp}: {err}")
        else:
            print("✅ Alle wichtigen Imports OK")
        return len(failed) == 0
    except Exception as e:
        print(f"❌ Import-Check-Fehler: {e}")
        return False

def check_class_structure(file_path: str) -> bool:
    print("\n🏗️  KLASSEN-STRUKTUR-CHECK...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        print(f"✅ {len(classes)} Klassen gefunden")
        if 'ProfessionalTranslationQualityApp' in classes:
            print("✅ Haupt-Klasse ProfessionalTranslationQualityApp gefunden")
            return True
        print("❌ Haupt-Klasse ProfessionalTranslationQualityApp NICHT gefunden")
        return False
    except Exception as e:
        print(f"❌ Klassen-Check-Fehler: {e}")
        return False

def check_unicode_issues(file_path: str) -> bool:
    print("\n🌍 UNICODE-CHECK...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        problematic = []
        for i, ch in enumerate(content):
            if ord(ch) > 127:
                problematic.append((i, ch, ord(ch)))
        if problematic:
            print(f"⚠️  {len(problematic)} Unicode-Zeichen (erste 5):")
            for pos, ch, code in problematic[:5]:
                line_num = content[:pos].count('\n') + 1
                print(f"   Zeile {line_num}: '{ch}' U+{code:04X}")
        else:
            print("✅ Keine problematischen Unicode-Zeichen")
        return len(problematic) == 0
    except Exception as e:
        print(f"❌ Unicode-Check-Fehler: {e}")
        return False

def _resolve_gui_file() -> Optional[Path]:
    """Ermittelt die zu untersuchende GUI-Datei mit Fallbacks."""
    base = Path.cwd()
    primary = base / "modern_translation_quality_gui.py"
    if primary.exists():
        return primary

    fallback_patterns = [
        "modern_translation_quality_gui.py.*",
        "backups/modern_translation_quality_gui.py*",
        "archive/**/modern_translation_quality_gui.py*",
        "backups/**/modern_translation_quality_gui.py*",
    ]

    candidates: list[tuple[float, Path]] = []
    for pattern in fallback_patterns:
        for match in base.glob(pattern):
            if match.is_file():
                try:
                    mtime = match.stat().st_mtime
                except OSError:
                    mtime = 0
                candidates.append((mtime, match))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def main():
    print("🔍 QUALITY GUI FEHLER-DIAGNOSE")
    print("=" * 50)
    resolved = _resolve_gui_file()
    if not resolved:
        print("❌ Keine modern_translation_quality_gui*.py gefunden")
        print("   Hinweis: Datei ggf. durch Schutzsystem verschoben. Bitte Backup prüfen.")
        return
    file_path = str(resolved)
    if resolved.name != "modern_translation_quality_gui.py":
        print(f"ℹ️  Verwende Fallback: {resolved.name}")

    syntax_ok = check_syntax(file_path)
    imports_ok = check_imports(file_path)
    structure_ok = check_class_structure(file_path)
    unicode_ok = check_unicode_issues(file_path)
    print("\n" + "=" * 50)
    print("📊 ERGEBNIS-ZUSAMMENFASSUNG:")
    print(f"   Syntax: {'✅ OK' if syntax_ok else '❌ FEHLER'}")
    print(f"   Imports: {'✅ OK' if imports_ok else '⚠️  PROBLEME'}")
    print(f"   Struktur: {'✅ OK' if structure_ok else '❌ FEHLER'}")
    print(f"   Unicode: {'✅ OK' if unicode_ok else '⚠️  PROBLEME'}")
    if syntax_ok and structure_ok:
        print("\n🎯 DIAGNOSE: GUI sollte startbar sein!")
        print("💡 Test: python start_ai_quality_gui.py")
    else:
        print("\n❌ DIAGNOSE: GUI hat kritische Probleme!")
        if not syntax_ok:
            print("🔧 Lösung: Syntax-Fehler beheben")
        if not structure_ok:
            print("🔧 Lösung: Klassen-Struktur reparieren")

if __name__ == '__main__':
    main()
