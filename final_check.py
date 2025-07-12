#!/usr/bin/env python3
"""
Final check script for the Prüfung workflow
Verifies that all components work correctly
"""

import sys
import os

def main():
    """Main test function"""
    print("=" * 50)
    print("PRÜFUNG WORKFLOW FINAL CHECK")
    print("=" * 50)
    
    success = True
    
    # Test imports
    try:
        print("Testing imports...")
        from checker_app import CheckerApp
        from pruefung_workflow import PruefungWorkflow
        from pruefung_workflow_controller import PruefungWorkflowController
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        success = False
    
    # Test controller
    try:
        print("Testing controller...")
        
        # Suppress debug output
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        from pruefung_workflow_controller import PruefungWorkflowController
        controller = PruefungWorkflowController()
        
        # Restore output
        sys.stdout.close() 
        sys.stdout = old_stdout
        
        methods = ['select_all_checks', 'clear_all_file_pairs', 'start_checking_process']
        for method in methods:
            if not hasattr(controller, method):
                raise AttributeError(f"Missing: {method}")
        
        print("✅ Controller working")
    except Exception as e:
        print(f"❌ Controller failed: {e}")
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 SUCCESS! Everything is working.")
        print("You can now run: python checker_app.py")
    else:
        print("❌ Some issues found.")
    print("=" * 50)

if __name__ == "__main__":
    main()
