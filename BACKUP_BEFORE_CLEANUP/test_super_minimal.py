#!/usr/bin/env python3
"""
Super minimal button test with comprehensive error handling
"""

import os
import sys
import traceback

# Force unbuffered output
import functools
print = functools.partial(print, flush=True)

print("=== STARTING MINIMAL BUTTON TEST ===")

try:
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import required modules
    import tkinter as tk
    import customtkinter as ctk
    from pruefung_workflow import PruefungWorkflow
    
    print("✓ Imports successful")
    
    # Create minimal window
    root = ctk.CTk()
    root.title("Minimal Button Test")
    root.withdraw()  # Hide window
    
    print("✓ Root window created")
    
    # Create workflow instance
    workflow = PruefungWorkflow(root, lambda: None)
    print("✓ PruefungWorkflow instance created")
    
    # Call show_workflow to initialize UI elements
    workflow.show_workflow()
    print("✓ show_workflow called")
    
    # Set up test files
    test_file_a = os.path.join(os.path.dirname(__file__), "test_file_a.txt")
    test_file_b = os.path.join(os.path.dirname(__file__), "test_file_b.txt")
    
    # Ensure test files exist
    if not os.path.exists(test_file_a):
        with open(test_file_a, "w", encoding="utf-8") as f:
            f.write("Dies ist ein Test-Text A.\n")
    
    if not os.path.exists(test_file_b):
        with open(test_file_b, "w", encoding="utf-8") as f:
            f.write("This is a test text B.\n")
    
    print("✓ Test files prepared")
    
    # Set StringVars properly
    workflow.text_a_path_var.set(test_file_a)
    workflow.text_b_path_var.set(test_file_b)
    
    print(f"✓ text_a_path_var = {workflow.text_a_path_var.get()}")
    print(f"✓ text_b_path_var = {workflow.text_b_path_var.get()}")
    
    # Override run_check to avoid threading issues
    original_run_check = workflow.run_check
    
    def simple_run_check():
        """Simplified run_check to avoid threading/hanging"""
        print("✓ Simple run_check called")
        print(f"  Project data files: {workflow.project_data.get('files', [])}")
        
        # Simulate completion and re-enable button
        if hasattr(workflow, 'status_label') and workflow.status_label:
            workflow.status_label.configure(text="Test completed")
        
        if hasattr(workflow, 'start_button') and workflow.start_button:
            workflow.start_button.configure(state="normal")
        
        print("✓ Simple run_check completed")
    
    # Replace with simplified version
    workflow.run_check = simple_run_check
    
    # Check button attributes
    print("\n--- BUTTON TESTS ---")
    if hasattr(workflow, 'start_button'):
        print(f"✓ start_button exists: {workflow.start_button}")
        if workflow.start_button:
            try:
                button_cmd = workflow.start_button.cget('command')
                print(f"✓ Button command: {button_cmd}")
            except Exception as e:
                print(f"✗ Error getting button command: {e}")
    else:
        print("✗ start_button attribute not found")
    
    # Check method
    if hasattr(workflow, 'on_start_check'):
        print(f"✓ on_start_check method exists: {workflow.on_start_check}")
    else:
        print("✗ on_start_check method not found")
    
    # Test direct method call
    print("\n--- ON_START_CHECK TEST ---")
    try:
        print("Calling on_start_check...")
        workflow.on_start_check()
        print("✓ on_start_check completed successfully")
    except Exception as e:
        print(f"✗ Error in on_start_check: {e}")
        traceback.print_exc()
    
    # Restore original method
    workflow.run_check = original_run_check
    
    # Clean up
    root.destroy()
    
    print("\n=== TEST COMPLETED SUCCESSFULLY ===")

except Exception as e:
    print(f"\n!!! FATAL ERROR: {e}")
    traceback.print_exc()
    print("\n=== TEST FAILED ===")
