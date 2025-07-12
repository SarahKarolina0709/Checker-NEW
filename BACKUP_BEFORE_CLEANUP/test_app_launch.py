#!/usr/bin/env python3
"""Test the Prüfung workflow by trying to start the app and click Prüfung"""

import sys
import os
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Starting Checker App to test Prüfung workflow...")
    
    # Import the app
    from checker_app import CheckerApp
    
    # Create app instance
    app = CheckerApp()
    
    def test_pruefung_workflow():
        """Test function to be run after app starts"""
        try:
            time.sleep(2)  # Wait for app to load
            print("Attempting to start Prüfung workflow...")
            
            # Try to start the Prüfung workflow
            app.start_workflow("pruefung_workflow", {})
            print("✅ Prüfung workflow started successfully!")
            
            # Wait a bit then close
            time.sleep(2)
            app.root.quit()
            
        except Exception as e:
            print(f"❌ Error starting Prüfung workflow: {e}")
            import traceback
            traceback.print_exc()
            app.root.quit()
    
    # Schedule the test after the app starts
    app.root.after(1000, test_pruefung_workflow)
    
    # Start the app
    print("App starting...")
    app.root.mainloop()
    print("App closed.")
    
except Exception as e:
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
