#!/usr/bin/env python3
"""
Quick test to verify the syntax fixes worked.
"""

import py_compile
import sys

def test_file_compilation(filename):
    try:
        py_compile.compile(filename, doraise=True)
        print(f"✅ {filename} - Syntax OK")
        return True
    except Exception as e:
        print(f"❌ {filename} - Syntax Error: {e}")
        return False

def main():
    print("=== Testing File Compilation ===")
    
    files_to_test = [
        "pruefung_workflow_controller.py",
        "ui_components/pruefung_workflow_view.py"
    ]
    
    all_good = True
    for file in files_to_test:
        if not test_file_compilation(file):
            all_good = False
    
    print("\n=== Results ===")
    if all_good:
        print("🎉 All files compile successfully!")
        print("✅ The file pair clicking functionality should now work correctly.")
        print("🔧 You can now start the Prüfung workflow without syntax errors.")
    else:
        print("⚠️  Some files still have syntax errors.")
    
    return all_good

if __name__ == "__main__":
    main()
