#!/usr/bin/env python3
"""Final test to confirm Prüfung workflow works"""

import os
import sys
import tkinter as tk
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pruefung_workflow():
    """Test if the Prüfung workflow can be started without errors"""
    
    try:
        print("Testing Prüfung workflow startup...")
        
        # Import required modules
        from checker_app import CheckerApp
        import threading
        import time
        
        # Create a simple root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create app instance
        app = CheckerApp()
        
        # Create a function to test the workflow startup
        def run_workflow_test():
            try:
                print("Attempting to start Prüfung workflow...")
                app.start_workflow("pruefung_workflow", {})
                print("✅ SUCCESS: Prüfung workflow started without errors!")
                
                # Close after successful test
                app.root.after(1000, app.root.quit)
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                traceback.print_exc()
                app.root.quit()
        
        # Schedule the test
        app.root.after(2000, run_workflow_test)
        
        # Run the app briefly
        print("Starting app for testing...")
        app.root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PRÜFUNG WORKFLOW STARTUP TEST")
    print("=" * 60)
    
    success = test_pruefung_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETED - Check output above for results")
    else:
        print("💥 TEST FAILED - Check errors above")
    print("=" * 60)
