# -*- coding: utf-8 -*-
"""
QUALITY GUI ERROR CHECKER - Umfassende Fehlerprüfung
Testet Syntax, Imports und Startup-Probleme
"""
import os


import ast

def check_syntax(file_path):
    """Prüft Python-Syntax"""
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

def check_imports(file_path):
    """Prüft ob alle Imports verfügbar sind"""
    print("\n📦 IMPORT-CHECK...")

    try:
        # Versuche das Modul zu laden
        spec = importlib.util.spec_from_file_location("quality_gui", file_path)
        module = importlib.util.module_from_spec(spec)

        # Führe nur die Imports aus (nicht den ganzen Code)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]

        failed_imports = []
        for line in import_lines[:10]:  # Teste erste 10 Imports
            try:
                exec(line.strip())
            except ImportError as e:
                failed_imports.append((line.strip(), str(e)))
            except Exception:
                pass  # Ignoriere andere Fehler bei Import-Test

        if failed_imports:
            print(f"⚠️  {len(failed_imports)} problematische Imports gefunden:")
            for imp, error in failed_imports:
                print(f"   - {imp}: {error}")
        else:
            print("✅ Alle wichtigen Imports OK")

        return len(failed_imports) == 0

    except Exception as e:
        print(f"❌ Import-Check-Fehler: {e}")
        return False

def check_class_structure(file_path):
    """Prüft Klassen-Struktur"""
    print("\n🏗️  KLASSEN-STRUKTUR-CHECK...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        print(f"✅ {len(classes)} Klassen gefunden:")
        for cls in classes[:10]:  # Zeige erste 10
            print(f"   - {cls}")

        # Prüfe Haupt-Klasse
        if 'ProfessionalTranslationQualityApp' in classes:
            print("✅ Haupt-Klasse ProfessionalTranslationQualityApp gefunden")
            return True
        else:
            print("❌ Haupt-Klasse ProfessionalTranslationQualityApp NICHT gefunden")
            return False

    except Exception as e:
        print(f"❌ Klassen-Check-Fehler: {e}")
        return False

def check_unicode_issues(file_path):
    """Prüft auf Unicode-Probleme"""
    print("\n🌍 UNICODE-CHECK...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Suche nach problematischen Unicode-Zeichen
        problematic_chars = []
        for i, char in enumerate(content):
            if ord(char) > 127:  # Nicht-ASCII
                problematic_chars.append((i, char, ord(char)))

        if problematic_chars:
            print(f"⚠️  {len(problematic_chars)} Unicode-Zeichen gefunden")
            # Zeige erste 5
            for pos, char, code in problematic_chars[:5]:
                line_num = content[:pos].count('\n') + 1
                print(f"   Zeile {line_num}: '{char}' (U+{code:04X})")

            if len(problematic_chars) > 5:
                print(f"   ... und {len(problematic_chars) - 5} weitere")
        else:
            print("✅ Keine problematischen Unicode-Zeichen")

        return len(problematic_chars) == 0

    except Exception as e:
        print(f"❌ Unicode-Check-Fehler: {e}")
        return False

def main():
    print("🔍 QUALITY GUI FEHLER-DIAGNOSE")
    print("=" * 50)

    file_path = "modern_translation_quality_gui.py"

    if not os.path.exists(file_path):
        print(f"❌ Datei nicht gefunden: {file_path}")
        return

    # Führe alle Checks durch
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
        print("💡 Teste mit: python start_ai_quality_gui.py")
    else:
        print("\n❌ DIAGNOSE: GUI hat kritische Probleme!")
        if not syntax_ok:
            print("🔧 LÖSUNG: Syntax-Fehler beheben")
        if not structure_ok:
            print("🔧 LÖSUNG: Klassen-Struktur reparieren")

if __name__ == "__main__":
    import os
    main()