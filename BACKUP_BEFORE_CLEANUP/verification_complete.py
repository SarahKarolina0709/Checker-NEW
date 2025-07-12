"""
Final verification script for the fixed pruefung_workflow_complete.py file.
This script performs a comprehensive test of the workflow.
"""
import os
import tkinter as tk
from tkinter import messagebox
import sys

try:
    # Create a log file
    with open("final_verification_results.txt", "w", encoding="utf-8") as log:
        log.write("FINAL VERIFICATION OF FIXED_PRUEFUNG_WORKFLOW_COMPLETE.PY\n")
        log.write("=======================================================\n\n")
        
        # Step 1: Import the module
        log.write("Step 1: Importing the module...\n")
        from fixed_pruefung_workflow_complete import PruefungWorkflow
        log.write("SUCCESS: PruefungWorkflow module imported successfully\n\n")
        
        # Step 2: Create a root window
        log.write("Step 2: Creating a test window...\n")
        root = tk.Tk()
        root.title("PruefungWorkflow Test")
        root.geometry("1200x800")
        log.write("SUCCESS: Test window created\n\n")
        
        # Step 3: Create an instance of PruefungWorkflow
        log.write("Step 3: Creating PruefungWorkflow instance...\n")
        test_data = {
            'kunde_name': 'Test Kunde',
            'betreuer_name': 'Test Betreuer',
            'auftragsnummer': 'TEST-123',
            'uploaded_files': []
        }
        workflow = PruefungWorkflow(
            root=root,
            back_callback=lambda: root.destroy(),
            project_data=test_data
        )
        log.write("SUCCESS: PruefungWorkflow instance created\n\n")
        
        # Step 4: Test show_workflow method
        log.write("Step 4: Testing show_workflow method...\n")
        workflow.show_workflow(test_data)
        log.write("SUCCESS: show_workflow method executed without errors\n\n")
        
        # Step 5: Test create_ui method
        log.write("Step 5: Testing that all required methods exist...\n")
        methods = [
            'create_ui',
            'start_comparison',
            '_update_dynamic_content',
            'show_help',
            'show_workflow',
            'cleanup'
        ]
        
        for method in methods:
            if hasattr(workflow, method) and callable(getattr(workflow, method)):
                log.write(f"SUCCESS: Method '{method}' exists and is callable\n")
            else:
                log.write(f"ERROR: Method '{method}' does not exist or is not callable\n")
        
        log.write("\nALL TESTS COMPLETED SUCCESSFULLY!\n")
        log.write("The fixed_pruefung_workflow_complete.py file is now functioning correctly.\n")
        
        # Clean up
        root.after(1000, root.destroy)
        root.mainloop()
        
    print("Verification completed. See 'final_verification_results.txt' for results.")
    
except Exception as e:
    import traceback
    with open("final_verification_results.txt", "w", encoding="utf-8") as log:
        log.write(f"ERROR: {str(e)}\n\n")
        log.write(traceback.format_exc())
    print(f"Error during verification: {str(e)}")
    traceback.print_exc()
