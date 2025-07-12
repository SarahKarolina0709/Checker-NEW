#!/usr/bin/env python3
"""
Direct test of the PruefungWorkflow instantiation
"""

import sys
import os
import traceback

# Redirect debug output
class DevNull:
    def write(self, x): pass
    def flush(self): pass

# Temporarily suppress debug output
original_stdout = sys.stdout
original_stderr = sys.stderr

try:
    print("Testing PruefungWorkflow instantiation...")
    
    # Suppress debug output during imports
    sys.stdout = DevNull()
    sys.stderr = DevNull()
    
    # Import required modules
    import customtkinter as ctk
    from pruefung_workflow import PruefungWorkflow
    
    # Restore output
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    print("✓ Imports successful")
    
    # Create a simple tkinter root for testing
    root = ctk.CTk()
    root.withdraw()  # Hide window
    
    print("✓ Root window created")
    
    # Create a content frame  
    content_frame = ctk.CTkFrame(root)
    content_frame.pack(fill="both", expand=True)
    
    print("✓ Content frame created")
    
    # Try to create the workflow
    workflow = PruefungWorkflow(content_frame, app=None, project_data={})
    
    print("✅ SUCCESS: PruefungWorkflow created without errors!")
    print("   - Controller exists:", hasattr(workflow, 'controller'))
    print("   - View exists:", hasattr(workflow, 'view'))
    
    if hasattr(workflow, 'controller'):
        controller = workflow.controller
        methods_to_check = ['select_all_checks', 'clear_all_file_pairs', 'start_checking_process']
        for method in methods_to_check:
            exists = hasattr(controller, method)
            print(f"   - {method}: {'✓' if exists else '✗'}")
    
    # Clean up
    root.destroy()
    
except Exception as e:
    # Restore output if there was an error
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
    
print("\nTest completed.")
