#!/usr/bin/env python3
"""
Test script to verify the PruefungWorkflowController is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_controller():
    print("Testing PruefungWorkflowController...")
    
    try:
        from pruefung_workflow_controller import PruefungWorkflowController
        print("✓ Controller imported successfully")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    try:
        # Create instance
        controller = PruefungWorkflowController()
        print("✓ Controller instance created")
    except Exception as e:
        print(f"✗ Controller instantiation failed: {e}")
        return False
    
    # Check for required attributes/methods
    required_attrs = ['get_tab_configurations', 'on_language_change', 'CHECK_DEFINITIONS', 'language_var']
    missing = []
    for attr in required_attrs:
        if not hasattr(controller, attr):
            missing.append(attr)
    
    if missing:
        print(f"✗ Missing attributes: {missing}")
        return False
    else:
        print("✓ All required attributes found")
    
    # Test get_tab_configurations method
    try:
        tabs = controller.get_tab_configurations()
        print(f"✓ Tab configurations: {len(tabs)} tabs found")
        for tab_key, config in tabs.items():
            print(f"  - {tab_key}: {config['title']}")
        print("✓ get_tab_configurations works correctly")
    except Exception as e:
        print(f"✗ Error in get_tab_configurations: {e}")
        return False
    
    print("✓ Controller verification complete - ALL TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = test_controller()
    exit(0 if success else 1)
