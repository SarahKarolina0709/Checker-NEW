#!/usr/bin/env python3
"""
Debug import of PruefungWorkflowController
"""

import sys
import traceback

try:
    print("Step 1: Importing module...")
    import pruefung_workflow_controller
    print("✓ Module imported successfully")
    
    print("Step 2: Checking module contents...")
    print(f"Module contents: {dir(pruefung_workflow_controller)}")
    
    if hasattr(pruefung_workflow_controller, 'PruefungWorkflowController'):
        print("✓ PruefungWorkflowController class found in module")
        
        print("Step 3: Importing class...")
        from pruefung_workflow_controller import PruefungWorkflowController
        print("✓ Class imported successfully")
        
        print("Step 4: Creating instance...")
        controller = PruefungWorkflowController()
        print("✓ Instance created successfully")
        
    else:
        print("✗ PruefungWorkflowController class not found in module")
        
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
