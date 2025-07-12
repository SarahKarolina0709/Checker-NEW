#!/usr/bin/env python3
"""
Debug script to isolate the problem with PruefungWorkflowController.
"""

import sys
import traceback

def test_import():
    """Test importing the controller."""
    try:
        print("[TEST] Attempting to import PruefungWorkflowController...")
        from pruefung_workflow_controller import PruefungWorkflowController
        print("✅ Import successful")
        return PruefungWorkflowController
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return None

def test_instantiation(cls):
    """Test creating an instance of the controller."""
    try:
        print("[TEST] Attempting to create controller instance...")
        controller = cls({'test': 'data'})
        print("✅ Instance creation successful")
        return controller
    except Exception as e:
        print(f"❌ Instance creation failed: {e}")
        traceback.print_exc()
        return None

def test_attributes(controller):
    """Test accessing the required attributes."""
    print("[TEST] Testing attributes...")
    
    attrs_to_test = ['CHECK_DEFINITIONS', 'clear_all_file_pairs', 'select_all_checks']
    
    for attr in attrs_to_test:
        try:
            if hasattr(controller, attr):
                print(f"✅ {attr} exists")
            else:
                print(f"❌ {attr} missing")
        except Exception as e:
            print(f"❌ Error checking {attr}: {e}")

def main():
    print("=== Debug PruefungWorkflowController ===")
    
    # Test 1: Import
    cls = test_import()
    if not cls:
        return
    
    # Test 2: Instantiation
    controller = test_instantiation(cls)
    if not controller:
        return
    
    # Test 3: Attributes
    test_attributes(controller)
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main()
