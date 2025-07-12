#!/usr/bin/env python3
"""Test script to launch angebots workflow directly."""

import sys
import os
import tkinter as tk
import customtkinter as ctk

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_angebots_workflow():
    print("Testing angebots workflow directly...")
    
    # Initialize customtkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Test Angebotsanalyse Workflow")
    root.geometry("1200x800")
    
    def back_callback():
        print("Back callback called")
        root.quit()
    
    # Import and create workflow
    try:
        from angebots_workflow import AngebotsanalyseWorkflow
        print("Successfully imported AngebotsanalyseWorkflow")
        
        # Create workflow instance
        workflow = AngebotsanalyseWorkflow(
            root=root,
            back_to_welcome_callback=back_callback
        )
        print("Successfully created AngebotsanalyseWorkflow instance")
        
        # Show workflow with project data
        workflow_data = {
            "customer_name": "Test Kunde",
            "order_number": "2025-001",
            "files": ["c:\\Users\\sarah\\Desktop\\Checker\\angebots_test.txt"]
        }
        
        workflow.show_workflow(workflow_data)
        print("Called show_workflow()")
        
        # Add test button to start the analysis
        def start_test_analysis():
            print("Starting test analysis...")
            if hasattr(workflow, '_start_analysis'):
                workflow._start_analysis()
            else:
                print("ERROR: _start_analysis method not found")
                
        test_button = ctk.CTkButton(
            root, 
            text="Start Analyse", 
            command=start_test_analysis,
            fg_color="green",
            width=200,
            height=40
        )
        test_button.pack(pady=10, padx=10, side="bottom")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    root.mainloop()
    
if __name__ == "__main__":
    test_angebots_workflow()
