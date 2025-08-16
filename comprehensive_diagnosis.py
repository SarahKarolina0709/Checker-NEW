#!/usr/bin/env python3
"""
Comprehensive error detection for Quality GUI
"""

import ast
import sys
import traceback

def check_syntax_errors():
    """Check for Python syntax errors"""
    print("🔍 Checking syntax errors...")

    try:
        with open('modern_translation_quality_gui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse the AST
        ast.parse(content)
        print("✅ AST Parse successful - No syntax errors")
        return True

    except SyntaxError as e:
        print(f"❌ Syntax Error at line {e.lineno}:")
        print(f"   Message: {e.msg}")
        print(f"   Text: {repr(e.text)}")
        print(f"   Offset: {e.offset}")
        return False
    except UnicodeDecodeError as e:
        print(f"❌ UTF-8 Encoding Error:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ Other Error: {e}")
        traceback.print_exc()
        return False

def check_utf8_issues():
    """Check for UTF-8 encoding issues"""
    print("🔍 Checking UTF-8 encoding issues...")

    try:
        # Try different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings_to_try:
            try:
                with open('modern_translation_quality_gui.py', 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Successfully read with {encoding} encoding")

                # Check for problematic characters
                problematic_chars = []
                for i, line in enumerate(content.splitlines(), 1):
                    for j, char in enumerate(line):
                        if ord(char) > 127:  # Non-ASCII character
                            problematic_chars.append((i, j, char, ord(char)))

                if problematic_chars:
                    print(f"⚠️  Found {len(problematic_chars)} non-ASCII characters:")
                    for line_num, char_pos, char, char_code in problematic_chars[:10]:
                        print(f"   Line {line_num}, Pos {char_pos}: '{char}' (U+{char_code:04X})")
                    if len(problematic_chars) > 10:
                        print(f"   ... and {len(problematic_chars) - 10} more")
                else:
                    print("✅ No non-ASCII characters found")

                return True, encoding, problematic_chars

            except UnicodeDecodeError:
                continue

        print("❌ Could not read file with any encoding")
        return False, None, []

    except Exception as e:
        print(f"❌ UTF-8 Check Error: {e}")
        return False, None, []

def check_import_capability():
    """Check if the module can be imported"""
    print("🔍 Checking import capability...")

    try:
        # Remove from sys.modules if already imported
        if 'modern_translation_quality_gui' in sys.modules:
            del sys.modules['modern_translation_quality_gui']

        import modern_translation_quality_gui
        print("✅ Import successful")

        # Check main components
        if hasattr(modern_translation_quality_gui, 'ProfessionalTranslationQualityApp'):
            print("✅ Main class found")
        else:
            print("❌ Main class missing")

        if hasattr(modern_translation_quality_gui, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function missing")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("="*60)
    print("🔍 COMPREHENSIVE ERROR DIAGNOSIS - QUALITY GUI")
    print("="*60)

    # Check syntax
    syntax_ok = check_syntax_errors()
    print()

    # Check UTF-8
    utf8_ok, encoding, problematic_chars = check_utf8_issues()
    print()

    # Check import (only if syntax is OK)
    if syntax_ok:
        import_ok = check_import_capability()
    else:
        import_ok = False
        print("⏭️  Skipping import test due to syntax errors")

    print("\n" + "="*60)
    print("📋 DIAGNOSIS SUMMARY:")
    print(f"   Syntax Check: {'✅ PASSED' if syntax_ok else '❌ FAILED'}")
    print(f"   UTF-8 Check:  {'✅ PASSED' if utf8_ok else '❌ FAILED'}")
    print(f"   Import Check: {'✅ PASSED' if import_ok else '❌ FAILED'}")

    if not syntax_ok or not utf8_ok:
        print("\n❌ ISSUES FOUND - Quality GUI needs repair!")
        if not utf8_ok:
            print("   UTF-8 encoding issues detected")
        if not syntax_ok:
            print("   Python syntax errors detected")
    else:
        print("\n🎉 ALL CHECKS PASSED - Quality GUI is working!")

    print("="*60)

if __name__ == "__main__":
    main()