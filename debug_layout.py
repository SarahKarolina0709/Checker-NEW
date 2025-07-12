#!/usr/bin/env python3
"""Debug script to analyze layout issues in the welcome screen"""

import sys
import os
sys.path.insert(0, os.getcwd())

# Create a simple test to verify the workflow display
try:
    from checker_app import CheckerApp
    
    # Create app instance
    app = CheckerApp()
    
    # Check if workflow_routes are available
    if hasattr(app, 'workflow_routes'):
        workflow_routes = app.workflow_routes
        print(f"✓ Found {len(workflow_routes)} workflow routes:")
        for workflow_id, data in workflow_routes.items():
            print(f"  - {workflow_id}: {data.get('name', 'Unknown')}")
    else:
        print("✗ No workflow_routes found")
    
    # Check window size
    if hasattr(app, 'root'):
        w = app.root.winfo_width()
        h = app.root.winfo_height()
        print(f"✓ Window size: {w}x{h}")
        print(f"✓ Recommended: {app.RECOMMENDED_WINDOW_SIZE[0]}x{app.RECOMMENDED_WINDOW_SIZE[1]}")
        
        if w < app.RECOMMENDED_WINDOW_SIZE[0] or h < app.RECOMMENDED_WINDOW_SIZE[1]:
            print("⚠️  Window is smaller than recommended size")
        else:
            print("✓ Window size is adequate")
    
    # Check welcome screen
    if hasattr(app, 'welcome_screen'):
        welcome_screen = app.welcome_screen
        print(f"✓ Welcome screen initialized")
        
        # Check if workflow section exists
        if hasattr(welcome_screen, 'workflow_section'):
            workflow_section = welcome_screen.workflow_section
            print(f"✓ Workflow section found")
            
            # Check workflow section children
            children = workflow_section.winfo_children()
            print(f"✓ Workflow section has {len(children)} children")
            
        else:
            print("✗ No workflow_section found")
    
    print("\n🔍 Layout Analysis Complete")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
