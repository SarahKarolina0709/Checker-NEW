#!/usr/bin/env python3
"""
Comprehensive test script to verify the full functionality of the Prüfungs-Workflow
"""

import sys
import os
import traceback
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from pruefung_workflow import PruefungWorkflow

def test_comprehensive_functionality():
    """Test the full functionality of the Prüfungs-Workflow"""
    
    print("[TEST] Creating test window...")
    root = ctk.CTk()
    root.title("Comprehensive Test")
    root.geometry("1000x800")
    
    print("[TEST] Creating PruefungWorkflow instance...")
    def dummy_back_callback():
        print("[TEST] Back callback called")
    
    project_data = {
        'kunde': 'Test Kunde GmbH',
        'auftrag': 'TEST-123',
        'betreuer': 'Test Betreuer'
    }
    
    workflow = PruefungWorkflow(root, back_callback=dummy_back_callback, project_data=project_data)
    
    # Create and set test files
    print("[TEST] Preparing test files...")
    test_file_a = os.path.join(os.path.dirname(__file__), "test_file_a.txt")
    test_file_b = os.path.join(os.path.dirname(__file__), "test_file_b.txt")
    
    # Create test files if they don't exist
    if not os.path.exists(test_file_a):
        with open(test_file_a, "w", encoding="utf-8") as f:
            f.write("Dies ist ein Test-Text A.\nEr enthält mehrere Zeilen.\nUnd ist auf Deutsch geschrieben.")
    
    if not os.path.exists(test_file_b):
        with open(test_file_b, "w", encoding="utf-8") as f:
            f.write("This is a test text B.\nIt contains multiple lines.\nAnd is written in English.")
    
    # Set test files in workflow
    workflow.text_a_file = test_file_a
    workflow.text_b_file = test_file_b
    print(f"[TEST] Test files set: {test_file_a}, {test_file_b}")
    
    # Test step 1: Verify button existence
    print("[TEST] STEP 1: Testing button existence...")
    if hasattr(workflow, 'start_button'):
        print(f"[TEST] ✓ start_button exists: {workflow.start_button}")
        try:
            button_cmd = workflow.start_button.cget('command')
            print(f"[TEST] ✓ Button command: {button_cmd}")
        except Exception as e:
            print(f"[TEST] ✗ Could not get button command: {e}")
            return False
    else:
        print("[TEST] ✗ start_button not found!")
        return False
    
    # Test step 2: Verify enhanced systems
    print("[TEST] STEP 2: Testing enhanced systems...")
    if hasattr(workflow, 'progress_tracker') and workflow.progress_tracker is not None:
        print("[TEST] ✓ progress_tracker initialized")
    else:
        print("[TEST] ✗ progress_tracker not initialized")
        return False
    
    if hasattr(workflow, 'error_handler') and workflow.error_handler is not None:
        print("[TEST] ✓ error_handler initialized")
    else:
        print("[TEST] ✗ error_handler not initialized")
        return False
    
    # Test step 3: Test the on_start_check method
    print("[TEST] STEP 3: Testing on_start_check method...")
    if hasattr(workflow, 'on_start_check'):
        print("[TEST] ✓ on_start_check method exists")
        # Test calling the method directly
        try:
            print("[TEST] Calling on_start_check directly...")
            workflow.on_start_check()
            print("[TEST] ✓ on_start_check executed successfully")
        except Exception as e:
            print(f"[TEST] ✗ Error calling on_start_check: {e}")
            traceback.print_exc()
            return False
    else:
        print("[TEST] ✗ on_start_check method not found!")
        return False
    
    # Test step 4: Test update_project_info method
    print("[TEST] STEP 4: Testing update_project_info method...")
    if hasattr(workflow, 'update_project_info'):
        print("[TEST] ✓ update_project_info method exists")
        try:
            workflow.project_data = {
                'customer_name': 'Updated Customer',
                'order_number': 'UPDATED-456',
                'supervisor_name': 'Updated Supervisor'
            }
            workflow.update_project_info()
            print("[TEST] ✓ update_project_info executed successfully")
        except Exception as e:
            print(f"[TEST] ✗ Error calling update_project_info: {e}")
            traceback.print_exc()
            return False
    else:
        print("[TEST] ✗ update_project_info method not found!")
        return False
    
    print("[TEST] All tests completed successfully!")
    
    # Give some time to view the UI before closing
    time.sleep(2)
    root.destroy()
    return True

if __name__ == "__main__":
    try:
        success = test_comprehensive_functionality()
        if success:
            print("\n[RESULT] ✓ Comprehensive functionality test PASSED")
        else:
            print("\n[RESULT] ✗ Comprehensive functionality test FAILED")
    except Exception as e:
        print(f"\n[RESULT] ✗ Test failed with exception: {e}")
        traceback.print_exc()
