#!/usr/bin/env python3
"""
Comprehensive test script for the Prüfungs-Workflow
This script tests the full workflow UI and verifies the "Prüfung starten" button functionality
"""
# import lite_nuclear_ctk_patch # Apply nuclear anti-dark-mode patch

import os
import sys
import time
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from pruefung_workflow import PruefungWorkflow

def run_comprehensive_test():
    """Run a comprehensive test of the workflow UI and button functionality"""
    
    print("\n=== Starting Comprehensive Workflow Test ===\n")
    
    # Initialize the test window
    print("[TEST] Setting up test environment...")
    root = ctk.CTk()
    root.title("Prüfungs-Workflow Comprehensive Test")
    root.geometry("1000x800")
    
    # Create test files if they don't exist
    test_file_a = os.path.join(os.path.dirname(__file__), "test_file_a.txt")
    test_file_b = os.path.join(os.path.dirname(__file__), "test_file_b.txt")
    
    if not os.path.exists(test_file_a):
        with open(test_file_a, "w", encoding="utf-8") as f:
            f.write("Dies ist ein ausführlicher Test-Text für die Prüfung.\n" * 5)
    
    if not os.path.exists(test_file_b):
        with open(test_file_b, "w", encoding="utf-8") as f:
            f.write("This is a comprehensive test text for checking.\n" * 5)
    
    # Create project data
    project_data = {
        'kunde': 'Test Customer GmbH',
        'auftrag': 'A-2025-06-123',
        'betreuer': 'Test Manager'
    }
    
    # Create workflow instance with project data
    print("[TEST] Creating workflow instance with project data...")
    def dummy_back_callback():
        print("[TEST] Back callback called")
        workflow_test_completed.set()
    
    workflow = PruefungWorkflow(root, back_callback=dummy_back_callback, project_data=project_data)
    
    # Display the workflow UI
    print("[TEST] Displaying workflow UI...")
    workflow.show_workflow(project_data)
    
    # Wait for the UI to be fully rendered
    root.update_idletasks()
    
    # Event to signal when workflow test is completed
    workflow_test_completed = threading.Event()
    
    # Function to run workflow test steps
    def run_workflow_steps():
        try:
            print("[TEST] Waiting for UI to fully render...")
            time.sleep(1)
            root.update_idletasks()
            
            # Set test files
            print("[TEST] Setting test files...")
            workflow.text_a_file = test_file_a
            workflow.text_b_file = test_file_b
            
            # Update file status display
            if hasattr(workflow, 'text_a_status'):
                workflow.text_a_status.configure(text=f"Text A: {test_file_a}", text_color="#2196F3")
            if hasattr(workflow, 'text_b_status'):
                workflow.text_b_status.configure(text=f"Text B: {test_file_b}", text_color="#4CAF50")
            
            print("[TEST] Verifying button existence...")
            if hasattr(workflow, 'start_button'):
                print(f"[TEST] ✓ Start button exists: {workflow.start_button}")
                
                # Click the button programmatically
                print("[TEST] Clicking start button...")
                workflow.on_start_check()
                
                # Wait for processing to complete
                print("[TEST] Waiting for processing to complete...")
                time.sleep(5)
                
                print("[TEST] Workflow test completed successfully!")
            else:
                print("[TEST] ✗ Start button not found!")
            
            # Complete the test
            workflow_test_completed.set()
            
        except Exception as e:
            print(f"[TEST] ✗ Error during workflow test: {e}")
            import traceback
            traceback.print_exc()
            workflow_test_completed.set()
    
    # Start the workflow test in a separate thread
    threading.Thread(target=run_workflow_steps, daemon=True).start()
    
    # Define a function to close the window after the test
    def check_completion():
        if workflow_test_completed.is_set():
            root.after(1000, root.destroy)  # Destroy the window after 1 second
        else:
            root.after(500, check_completion)  # Check again after 500ms
    
    # Start the completion check
    root.after(500, check_completion)
    
    # Start the main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("[TEST] Test interrupted by user")
    
    print("\n=== Comprehensive Workflow Test Completed ===\n")
    return True

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        if success:
            print("\n[RESULT] ✓ Comprehensive workflow test PASSED")
            sys.exit(0)
        else:
            print("\n[RESULT] ✗ Comprehensive workflow test FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n[RESULT] ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
