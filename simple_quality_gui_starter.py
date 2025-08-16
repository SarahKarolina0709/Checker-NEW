#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Simple Quality GUI Starter
Direct startup test for Quality GUI
"""


import os

def main():
    try:
        print("🚀 Starting Quality GUI...")

        # Ensure correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"Working directory: {os.getcwd()}")

        # Check if main GUI file exists
        gui_file = "modern_translation_quality_gui.py"
        if not os.path.exists(gui_file):
            print(f"❌ GUI file not found: {gui_file}")
            return

        print(f"✅ Found GUI file: {gui_file}")

        # Try to import and run
        print("📦 Importing Quality GUI...")
        import modern_translation_quality_gui

        print("🎯 Creating application instance...")
        app = modern_translation_quality_gui.ProfessionalTranslationQualityApp()

        print("▶️ Starting application...")
        app.run()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Trying alternative import...")

        try:
            # Alternative import method

            spec = importlib.util.spec_from_file_location("quality_gui", gui_file)
            quality_gui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(quality_gui)

            app = quality_gui.ProfessionalTranslationQualityApp()
            app.run()

        except Exception as alt_error:
            print(f"❌ Alternative import failed: {alt_error}")

    except Exception as e:
        print(f"❌ Startup Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()