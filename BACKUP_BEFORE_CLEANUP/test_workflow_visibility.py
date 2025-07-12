#!/usr/bin/env python3
"""
Test script to verify all workflows are visible in the UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
import checker_app
from welcome_screen_components.workflow_section import WorkflowSection

def test_workflow_visibility():
    """Test if all workflows are visible in the UI."""
    print("Testing workflow visibility...")
    
    # Create app
    app = checker_app.CheckerApp()
    
    # Create GUI
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Workflow Visibility Test")
    root.geometry("400x600")  # Tall window to see all workflows
    
    # Configure grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    # Create container
    container = ctk.CTkFrame(root, fg_color="transparent")
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)
    
    # Mock welcome screen
    class MockWelcomeScreen:
        def create_icon_button(self, parent, text, icon_name, callback, style, width):
            return ctk.CTkButton(parent, text=text, width=width)
        
        def start_workflow_callback(self, workflow_id):
            print(f"Would start workflow: {workflow_id}")
    
    mock_welcome = MockWelcomeScreen()
    
    # Create workflow section
    workflow_section = WorkflowSection(container, app, mock_welcome)
    workflow_section.grid(row=0, column=0, sticky="nsew")
    
    # Add info label
    info_label = ctk.CTkLabel(
        root,
        text=f"Test: {len(app.workflow_routes)} workflows should be visible",
        font=ctk.CTkFont(size=12, weight="bold")
    )
    info_label.grid(row=1, column=0, pady=10)
    
    print(f"Created test window with {len(app.workflow_routes)} workflows")
    print("Check if all workflows are visible and can be scrolled to")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_workflow_visibility()
