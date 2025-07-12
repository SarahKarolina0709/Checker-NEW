#!/usr/bin/env python3
"""
Minimal test to debug the button functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== MINIMAL BUTTON TEST ===")

try:
    import customtkinter as ctk
    print("✓ CustomTkinter imported successfully")
except Exception as e:
    print(f"✗ CustomTkinter import failed: {e}")
    sys.exit(1)

try:
    from pruefung_workflow import PruefungWorkflow
    print("✓ PruefungWorkflow imported successfully")
except Exception as e:
    print(f"✗ PruefungWorkflow import failed: {e}")
    sys.exit(1)

# Create minimal test environment
root = ctk.CTk()
root.withdraw()  # Hide window

def dummy_callback():
    print("✓ Dummy callback called")

# Create workflow instance
try:
    workflow = PruefungWorkflow(root, dummy_callback)
    print("✓ PruefungWorkflow instance created")
except Exception as e:
    print(f"✗ PruefungWorkflow creation failed: {e}")
    sys.exit(1)

# Check StringVar initialization
try:
    print(f"✓ text_a_path_var exists: {hasattr(workflow, 'text_a_path_var')}")
    print(f"✓ text_b_path_var exists: {hasattr(workflow, 'text_b_path_var')}")
    
    if hasattr(workflow, 'text_a_path_var'):
        print(f"✓ text_a_path_var initial value: '{workflow.text_a_path_var.get()}'")
    if hasattr(workflow, 'text_b_path_var'):
        print(f"✓ text_b_path_var initial value: '{workflow.text_b_path_var.get()}'")
        
except Exception as e:
    print(f"✗ StringVar check failed: {e}")

# Create test files
test_file_a = os.path.join(os.path.dirname(__file__), "test_file_a.txt")
test_file_b = os.path.join(os.path.dirname(__file__), "test_file_b.txt")

try:
    # Set StringVar values
    workflow.text_a_path_var.set(test_file_a)
    workflow.text_b_path_var.set(test_file_b)
    print(f"✓ StringVars set successfully")
    print(f"  text_a_path_var: '{workflow.text_a_path_var.get()}'")
    print(f"  text_b_path_var: '{workflow.text_b_path_var.get()}'")
except Exception as e:
    print(f"✗ StringVar setting failed: {e}")

# Check if show_workflow creates UI elements
try:
    workflow.show_workflow()
    print("✓ show_workflow called successfully")
    
    # Check for UI elements
    print(f"✓ start_button exists: {hasattr(workflow, 'start_button') and workflow.start_button}")
    print(f"✓ status_label exists: {hasattr(workflow, 'status_label') and workflow.status_label}")
    print(f"✓ on_start_check method exists: {hasattr(workflow, 'on_start_check')}")
    
except Exception as e:
    print(f"✗ show_workflow failed: {e}")
    import traceback
    traceback.print_exc()

# Test on_start_check method if it exists
if hasattr(workflow, 'on_start_check'):
    try:
        print("\n=== Testing on_start_check method ===")
        
        # Ensure UI is ready
        root.update()
        
        # Patch run_check to avoid hanging
        original_run_check = None
        if hasattr(workflow, 'run_check'):
            original_run_check = workflow.run_check
            
            def simple_run_check():
                print("✓ Simple run_check called - mock processing")
                if hasattr(workflow, 'status_label') and workflow.status_label:
                    workflow.status_label.configure(text="Test completed")
                if hasattr(workflow, 'start_button') and workflow.start_button:
                    workflow.start_button.configure(state="normal")
                print("✓ Simple run_check completed")
            
            workflow.run_check = simple_run_check
        
        # Call on_start_check
        workflow.on_start_check()
        print("✓ on_start_check completed successfully")
        
        # Restore original method
        if original_run_check:
            workflow.run_check = original_run_check
            
    except Exception as e:
        print(f"✗ on_start_check failed: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Test completed ===")
root.destroy()
