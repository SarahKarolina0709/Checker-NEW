#!/usr/bin/env python3
"""
Direkter GUI-Test mit Diagnose
"""

import os
import sys
import traceback

def test_gui_directly():
    """Test GUI directly with comprehensive diagnostics"""
    print("🔍 STARTING COMPREHENSIVE GUI DIAGNOSIS...")

    try:
        # Import the GUI class
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        print("📦 Importing GUI module...")
        from modern_translation_quality_gui import ProfessionalTranslationQualityApp
        print("✅ GUI module imported successfully")

        # Create instance
        print("🏗️ Creating app instance...")
        app = ProfessionalTranslationQualityApp()
        print("✅ App instance created successfully")

        # Check all methods
        print("\n🔍 CHECKING METHOD AVAILABILITY:")
        required_methods = [
            'show_home_view', 'show_files_view', 'show_settings_view',
            'show_demo_results', 'clear_files', 'start_analysis', 'export_results'
        ]

        all_methods_found = True
        for method in required_methods:
            if hasattr(app, method):
                print(f"  ✅ {method}: FOUND")
                # Try to get method info
                try:
                    method_obj = getattr(app, method)
                    print(f"     📋 Type: {type(method_obj)}")
                    print(f"     📋 Callable: {callable(method_obj)}")
                except Exception as e:
                    print(f"     ⚠️ Method check error: {e}")
            else:
                print(f"  ❌ {method}: MISSING")
                all_methods_found = False

        if not all_methods_found:
            print("\n🚨 MISSING METHODS DETECTED!")
            print("📋 Available methods starting with 'show':")
            for attr in dir(app):
                if attr.startswith('show'):
                    print(f"  📌 {attr}")
            return False

        print("\n✅ ALL REQUIRED METHODS FOUND!")

        # Test calling show_home_view
        print("\n🧪 TESTING show_home_view...")
        try:
            app.show_home_view()
            print("✅ show_home_view() executed successfully!")
        except Exception as e:
            print(f"❌ show_home_view() failed: {e}")
            traceback.print_exc()
            return False

        print("\n🚀 STARTING GUI APPLICATION...")
        app.run()
        return True

    except Exception as main_error:
        print(f"❌ CRITICAL ERROR: {main_error}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_directly()
    if not success:
        input("\n⏸️ Press Enter to exit...")