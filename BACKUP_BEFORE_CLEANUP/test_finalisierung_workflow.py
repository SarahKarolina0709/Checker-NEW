#!/usr/bin/env python3
"""
Test script to specifically check if the finalisierung_workflow is being processed correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import checker_app

def test_finalisierung_workflow():
    """Test specifically the finalisierung_workflow."""
    print("Testing finalisierung_workflow...")
    
    # Create app
    app = checker_app.CheckerApp()
    
    # Check if finalisierung_workflow exists
    if 'finalisierung_workflow' in app.workflow_routes:
        workflow_data = app.workflow_routes['finalisierung_workflow']
        print("✅ finalisierung_workflow found!")
        print(f"  Name: {workflow_data.get('name', 'Unknown')}")
        print(f"  Description: {workflow_data.get('description', 'No description')}")
        print(f"  Icon: {workflow_data.get('icon', 'No icon')}")
        print(f"  Module: {workflow_data.get('module', 'No module')}")
    else:
        print("❌ finalisierung_workflow NOT found!")
        print("Available workflows:")
        for workflow_id in app.workflow_routes.keys():
            print(f"  - {workflow_id}")
    
    # Check workflow order
    print(f"\nWorkflow order:")
    for i, (workflow_id, data) in enumerate(app.workflow_routes.items()):
        print(f"  {i+1}. {workflow_id} ({data.get('name', 'Unknown')})")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_finalisierung_workflow()
