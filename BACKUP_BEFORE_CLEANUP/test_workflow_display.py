#!/usr/bin/env python3
"""
Test script to verify that all workflows are being created and displayed correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import checker_app
import customtkinter as ctk
from welcome_screen_components.workflow_section import WorkflowSection

def test_workflows():
    """Test workflow creation and display."""
    print("Testing workflow system...")
    
    # Create app
    app = checker_app.CheckerApp()
    
    # Check workflow routes
    print(f"Number of workflow routes: {len(app.workflow_routes)}")
    print("Workflow routes:")
    for i, (workflow_id, data) in enumerate(app.workflow_routes.items()):
        print(f"  {i+1}. {workflow_id}")
        print(f"     Name: {data.get('name', 'Unknown')}")
        print(f"     Description: {data.get('description', 'No description')}")
        print(f"     Icon: {data.get('icon', 'No icon')}")
        print()
    
    # Create GUI components
    root = ctk.CTk()
    root.withdraw()  # Hide window for testing
    
    # Mock welcome screen
    class MockWelcomeScreen:
        def create_icon_button(self, parent, text, icon_name, callback, style, width):
            button = ctk.CTkButton(parent, text=text, width=width)
            return button
        
        def start_workflow_callback(self, workflow_id):
            print(f"Would start workflow: {workflow_id}")
    
    mock_welcome = MockWelcomeScreen()
    
    # Create workflow section
    print("Creating workflow section...")
    workflow_section = WorkflowSection(root, app, mock_welcome)
    
    # Check if workflow section was created successfully
    print("Workflow section created successfully")
    
    # Clean up
    root.destroy()
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_workflows()
