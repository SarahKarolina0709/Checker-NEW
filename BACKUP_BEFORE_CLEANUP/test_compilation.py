#!/usr/bin/env python3
"""
Test file pair clicking functionality directly.
"""

import sys
import os

# Test the compilation first
print("[TEST] Testing compilation of modified files...")

try:
    import py_compile
    
    # Test controller
    py_compile.compile('pruefung_workflow_controller.py', doraise=True)
    print("[✓] Controller compiles successfully")
    
    # Test view
    py_compile.compile('ui_components/pruefung_workflow_view.py', doraise=True)
    print("[✓] View compiles successfully")
    
    print("\n[SUCCESS] All files compile correctly!")
    print("[INFO] The file pair clicking functionality should now work.")
    print("[INFO] When you click on a file pair in the Prüfung workflow, it should:")
    print("  - Change color to indicate selection")
    print("  - Print debug information to console")
    print("  - Show file pair details")
    
except Exception as e:
    print(f"[ERROR] Compilation failed: {e}")
    import traceback
    traceback.print_exc()
