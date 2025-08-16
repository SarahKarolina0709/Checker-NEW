#!/usr/bin/env python3
"""Präzise Klassenbereichs-Analyse"""

def find_class_end():
    try:
        with open('modern_translation_quality_gui.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_main_class = False
        bracket_depth = 0
        paren_depth = 0
        in_string = False
        string_char = None

        for i, line in enumerate(lines, 1):
            if i >= 1200 and i <= 2050:  # Focus on the area of interest
                stripped = line.strip()

                # Track class start
                if stripped == "class ProfessionalTranslationQualityApp:":
                    print(f"✅ Klasse startet: Zeile {i}")
                    in_main_class = True
                    continue

                if in_main_class:
                    # Check indentation and content
                    indent = len(line) - len(line.lstrip())

                    # Look for problematic lines
                    if indent == 0 and stripped and not stripped.startswith('#'):
                        if not any(stripped.startswith(x) for x in ['@', 'if __name__', 'class ', 'def ', 'import ', 'from ']):
                            print(f"❌ Möglicher Klassenaustritt: Zeile {i}")
                            print(f"   Inhalt: '{stripped[:60]}'")
                            print(f"   Einrückung: {indent}")
                            print(f"   Vollzeile: '{line.rstrip()}'")
                            break

                    # Track specific problematic areas
                    if i >= 2030 and i <= 2040:
                        print(f"🔍 Zeile {i}: Einrückung={indent}, Inhalt='{stripped[:40]}'")

        return True

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    find_class_end()