#!/usr/bin/env python3
"""
Test-Script für die erweiterten Icon-Features der Checker-App
"""

import sys
import os

# Add the current directory to the path so we can import checker_app
sys.path.insert(0, os.path.dirname(__file__))

def test_icon_features():
    """Testet die neuen Icon-Features"""
    print("🧪 Testing Enhanced Icon Features...")
    print("="*60)
    
    # Import and create app instance (but don't show UI)
    from checker_app import CheckerApp
    
    # Create app instance without showing UI
    app = CheckerApp()
    
    # Test 1: Icon suggestions
    print("\n🔍 Testing Icon Suggestions:")
    suggestions = app.get_icon_suggestions("file")
    print(f"Suggestions for 'file': {suggestions}")
    
    suggestions = app.get_icon_suggestions("user")
    print(f"Suggestions for 'user': {suggestions}")
    
    # Test 2: Category-based icon lookup
    print("\n📂 Testing Category-based Icon Lookup:")
    categories_to_test = ['file', 'user', 'settings', 'action', 'export']
    for category in categories_to_test:
        icon = app.get_icon_by_category(category)
        status = "✅ Found" if icon else "❌ Not found"
        print(f"Category '{category}': {status}")
    
    # Test 3: Icon fallback system
    print("\n🔄 Testing Icon Fallback System:")
    test_icons = ['quality', 'complete', 'project', 'document', 'person', 'help']
    for icon_name in test_icons:
        icon = app.get_icon(icon_name)
        status = "✅ Found" if icon else "❌ Not found"
        print(f"Icon '{icon_name}': {status}")
    
    # Test 4: Print comprehensive icon summary
    print("\n📊 Icon Summary:")
    app.print_icon_summary()
    
    print("🏁 Icon testing completed!")
    
    # Don't show the actual UI, just exit
    app.root.quit()
    app.root.destroy()

if __name__ == "__main__":
    test_icon_features()
