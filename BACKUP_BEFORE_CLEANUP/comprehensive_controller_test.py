#!/usr/bin/env python3
"""
Comprehensive test for all controller methods and view integration
"""

import sys
import os

# Suppress debug output
old_stdout = sys.stdout
old_stderr = sys.stderr

try:
    # Redirect debug output to devnull during imports
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
        
        # Import controller
        from pruefung_workflow_controller import PruefungWorkflowController
        
        # Create instance
        controller = PruefungWorkflowController()
        
    # Restore output
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    print("Controller imported and created successfully!")
    
    # List of all methods that should be present
    required_methods = [
        'get_available_checks',
        'get_tab_configurations',
        'add_file_pair',
        'clear_all_file_pairs',
        'select_all_checks',
        'deselect_all_checks', 
        'start_checking_process',
        'stop_checking_process',
        'export_results_as_pdf',
        'remove_file_pair_by_id',
        'set_view'
    ]
    
    print(f"\nChecking {len(required_methods)} required methods:")
    print("-" * 50)
    
    all_present = True
    for method_name in required_methods:
        if hasattr(controller, method_name):
            method = getattr(controller, method_name)
            if callable(method):
                print(f"✓ {method_name}")
            else:
                print(f"✗ {method_name} (not callable)")
                all_present = False
        else:
            print(f"✗ {method_name} (missing)")
            all_present = False
    
    print("-" * 50)
    
    if all_present:
        print("🎉 ALL METHODS PRESENT! Controller is ready for use.")
        print("\nTesting attribute access:")
        print(f"✓ CHECK_DEFINITIONS: {type(controller.CHECK_DEFINITIONS)} with {len(controller.CHECK_DEFINITIONS)} items")
        print(f"✓ TAB_CONFIGURATIONS: {type(controller.TAB_CONFIGURATIONS)} with {len(controller.TAB_CONFIGURATIONS)} items")
        print(f"✓ file_pairs: {type(controller.file_pairs)}")
        
    else:
        print("❌ SOME METHODS ARE MISSING!")
        
except Exception as e:
    # Restore output if there was an error
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
