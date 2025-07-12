#!/usr/bin/env python3
"""
Test the full Prüfung workflow startup to verify all issues are fixed.
"""

import sys
import os
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_workflow_startup():
    print("Testing complete Prüfung workflow startup...")
    
    try:
        # Create minimal tkinter environment
        root = tk.Tk()
        root.withdraw()
        
        print("Step 1: Testing controller creation...")
        from pruefung_workflow_controller import PruefungWorkflowController
        controller = PruefungWorkflowController()
        print("✓ Controller created successfully")
        
        print("Step 2: Testing controller properties...")
        
        # Test selected_checks property access (this was causing KeyError)
        try:
            checks = controller.selected_checks
            print(f"✓ selected_checks property accessible: {len(checks)} checks")
            
            # Test specific check that was causing KeyError
            if 'language_tool_check' in checks:
                print("✓ language_tool_check found in selected_checks")
            else:
                print("✗ language_tool_check missing from selected_checks")
                return False
                
        except Exception as e:
            print(f"✗ Error accessing selected_checks: {e}")
            return False
        
        print("Step 3: Testing workflow import...")
        try:
            from pruefung_workflow import PruefungWorkflow
            print("✓ PruefungWorkflow imported successfully")
        except Exception as e:
            print(f"✗ PruefungWorkflow import failed: {e}")
            return False
            
        print("Step 4: Testing workflow view import...")
        try:
            from ui_components.pruefung_workflow_view import PruefungWorkflowView
            print("✓ PruefungWorkflowView imported successfully")
        except Exception as e:
            print(f"✗ PruefungWorkflowView import failed: {e}")
            return False
        
        print("Step 5: Testing get_tab_configurations...")
        try:
            tabs = controller.get_tab_configurations()
            if 'errors' in tabs and 'quality' in tabs:
                print("✓ get_tab_configurations working correctly")
            else:
                print("✗ get_tab_configurations missing expected tabs")
                return False
        except Exception as e:
            print(f"✗ get_tab_configurations failed: {e}")
            return False
        
        print("Step 6: Testing controller methods...")
        required_methods = [
            'clear_all_file_pairs', 'select_all_checks', 'deselect_all_checks',
            'add_file_pair', 'remove_file_pair_by_id', 'select_file_pair'
        ]
        
        for method_name in required_methods:
            if hasattr(controller, method_name):
                print(f"✓ {method_name} method found")
            else:
                print(f"✗ {method_name} method missing")
                return False
        
        root.destroy()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The Prüfung workflow should now start correctly without errors!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow_startup()
    exit(0 if success else 1)
