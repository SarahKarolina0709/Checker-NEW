#!/usr/bin/env python3
"""
Dependency check for Quality GUI
"""

import sys

import importlib

print("🔍 DEPENDENCY CHECK")
print("="*40)

# List of required modules
required_modules = [
    'customtkinter',
    'tkinter',
    'os',
    'sys',
    'threading',
    'time',
    'typing',
    'logging',
    'pathlib',
    'json',
    'datetime',
    're',
    'traceback',
    'webbrowser',
    'subprocess',
    'shutil',
    'glob',
    'random',
    'math',
    'copy'
]

missing_modules = []
working_modules = []

for module in required_modules:
    try:
        importlib.import_module(module)
        working_modules.append(module)
        print(f"✅ {module}")
    except ImportError:
        missing_modules.append(module)
        print(f"❌ {module} - MISSING")

print("\n" + "="*40)
print("📋 SUMMARY:")
print(f"   Working modules: {len(working_modules)}")
print(f"   Missing modules: {len(missing_modules)}")

if missing_modules:
    print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
    print("Install with: pip install " + " ".join(missing_modules))
else:
    print("\n✅ All dependencies available!")

# Test Quality GUI import
print("\n🔍 Testing Quality GUI import...")
try:
    if 'modern_translation_quality_gui' in sys.modules:
        del sys.modules['modern_translation_quality_gui']

    import modern_translation_quality_gui
    print("✅ Quality GUI import: SUCCESS")

    # Check main components
    if hasattr(modern_translation_quality_gui, 'ProfessionalTranslationQualityApp'):
        print("✅ Main class: FOUND")
    else:
        print("❌ Main class: MISSING")

    if hasattr(modern_translation_quality_gui, 'main'):
        print("✅ Main function: FOUND")
    else:
        print("❌ Main function: MISSING")

except Exception as e:
    print(f"❌ Quality GUI import: FAILED - {e}")
    import traceback
    traceback.print_exc()

print("="*40)