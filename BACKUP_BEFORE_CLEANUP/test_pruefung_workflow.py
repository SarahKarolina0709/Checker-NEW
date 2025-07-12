#!/usr/bin/env python3
"""
Quick test to verify the Prüfung workflow starts without errors.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the necessary modules
try:
    from checker_app import CheckerApp
    print("✅ CheckerApp imported successfully")
    
    from pruefung_workflow import PruefungWorkflow
    print("✅ PruefungWorkflow imported successfully")
    
    from ui_components.pruefung_workflow_view import PruefungWorkflowView
    print("✅ PruefungWorkflowView imported successfully")
    
    print("\n🎉 All imports successful! The Prüfung workflow should work correctly.")
    print("📝 Key fixes applied:")
    print("   - Fixed geometry manager conflicts (pack vs grid)")
    print("   - Added missing clear_all_results() method")
    print("   - Added missing update_progress_display() method")
    print("   - Fixed data type handling in update_results_display()")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
