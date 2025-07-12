#!/usr/bin/env python3
"""
Quick test to verify the controller attributes
"""

try:
    # Suppress debug output
    import sys
    import os
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    from pruefung_workflow_controller import PruefungWorkflowController
    controller = PruefungWorkflowController()
    
    # Restore output
    sys.stdout.close()
    sys.stderr.close()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    print("✅ Controller created successfully!")
    
    # Check critical attributes
    attrs = ['CHECK_DEFINITIONS', 'TAB_CONFIGURATIONS']
    for attr in attrs:
        if hasattr(controller, attr):
            value = getattr(controller, attr)
            print(f"✅ {attr}: {type(value)} with {len(value)} items")
        else:
            print(f"❌ {attr}: MISSING")
    
    # Check critical methods
    methods = ['select_all_checks', 'clear_all_file_pairs', 'start_checking_process']
    for method in methods:
        if hasattr(controller, method):
            print(f"✅ {method}: exists")
        else:
            print(f"❌ {method}: MISSING")
    
    print("\n🎉 Controller verification complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
