#!/usr/bin/env python3
"""
Test the Pruefung workflow startup to ensure it works without errors.
"""

import sys
import os
import tkinter as tk
import customtkinter as ctk

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_pruefung_workflow():
    print("Testing Prüfung workflow startup...")
    
    try:
        # Create a root window to provide tkinter context
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test controller creation
        from pruefung_workflow_controller import PruefungWorkflowController
        controller = PruefungWorkflowController()
        print("✓ Controller created successfully")
        
        # Test that all required methods exist
        required_methods = [
            'get_tab_configurations',
            'on_language_change', 
            'set_view',
            'add_file_pair',
            'remove_file_pair_by_id',
            'clear_all_file_pairs',
            'select_file_pair',
            'select_all_checks',
            'deselect_all_checks',
            'start_checking_process',
            'stop_checking_process',
            'export_results_as_pdf'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(controller, method) or not callable(getattr(controller, method)):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ Missing methods: {missing_methods}")
            return False
        else:
            print("✓ All required methods found")
        
        # Test get_tab_configurations
        tabs = controller.get_tab_configurations()
        print(f"✓ Tab configurations: {len(tabs)} tabs found")
        
        # Test that CHECK_DEFINITIONS exists
        if hasattr(controller, 'CHECK_DEFINITIONS') and controller.CHECK_DEFINITIONS:
            print(f"✓ CHECK_DEFINITIONS found with {len(controller.CHECK_DEFINITIONS)} checks")
        else:
            print("✗ CHECK_DEFINITIONS missing or empty")
            return False
        
        # Test workflow import
        try:
            from pruefung_workflow import PruefungWorkflow
            print("✓ PruefungWorkflow can be imported")
        except Exception as e:
            print(f"✗ PruefungWorkflow import failed: {e}")
            return False
        
        # Clean up
        root.destroy()
        
        print("✓ All tests passed! Prüfung workflow should work correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pruefung_workflow()
    exit(0 if success else 1)
