#!/usr/bin/env python3
"""
Test script to verify workflow card visibility in the welcome screen.
"""

import logging
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_workflow_visibility():
    """Test to verify all workflow cards are visible"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(name)s] %(message)s')
    logger = logging.getLogger('workflow_visibility_test')
    
    try:
        # Import the welcome screen
        from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
        
        # Create a test window
        root = tk.Tk()
        root.title("Workflow Visibility Test")
        root.geometry("1200x800")
        
        # Create a minimal mock app object
        class MockApp:
            def __init__(self):
                self.root = root
                self.current_customer_data = {}
                self.workflows = {
                    'angebots_workflow': {'name': 'Angebots-Workflow', 'icon': 'play.png'},
                    'pruefung_workflow': {'name': 'Prüfungs-Workflow', 'icon': 'check-mark.png'},
                    'finalisierung_workflow': {'name': 'Finalisierungs-Workflow', 'icon': 'check-mark.png'},
                    'projekt_workflow': {'name': 'Projekt-Workflow', 'icon': 'folder.png'}
                }
                
            def get_customer_data(self):
                return self.current_customer_data
                
            def launch_workflow(self, workflow_id):
                logger.info(f"Mock: launching workflow {workflow_id}")
                
            def get_icon(self, icon_name, size=(16, 16)):
                """Mock icon method that returns None"""
                return None
                
            def get_customers(self):
                return []
                
            def get_all_customers(self):
                return []
        
        mock_app = MockApp()
        
        # Create the welcome screen
        logger.info("Creating welcome screen...")
        welcome_screen = UltraModernWelcomeScreen(root, mock_app)
        welcome_screen.pack(fill="both", expand=True)
        
        # Allow the UI to render
        root.update()
        
        # Check if workflow section exists
        if hasattr(welcome_screen, 'workflow_section'):
            workflow_section = welcome_screen.workflow_section
            logger.info(f"Workflow section found: {workflow_section}")
            
            # Check the scrollable frame
            if hasattr(workflow_section, 'scrollable_frame'):
                scrollable_frame = workflow_section.scrollable_frame
                logger.info(f"Scrollable frame found: {scrollable_frame}")
                
                # Get all children of the scrollable frame
                children = scrollable_frame.winfo_children()
                logger.info(f"Found {len(children)} children in scrollable frame")
                
                # Check each child
                for i, child in enumerate(children):
                    logger.info(f"Child {i}: {child} - {child.winfo_class()}")
                    
                    # Check if it's visible
                    if child.winfo_viewable():
                        logger.info(f"  - Child {i} is visible")
                        
                        # Get geometry info
                        try:
                            width = child.winfo_width()
                            height = child.winfo_height()
                            x = child.winfo_x()
                            y = child.winfo_y()
                            logger.info(f"  - Geometry: {width}x{height} at ({x}, {y})")
                        except Exception as e:
                            logger.warning(f"  - Could not get geometry: {e}")
                    else:
                        logger.warning(f"  - Child {i} is NOT visible")
                
                # Check scrollable frame dimensions
                try:
                    sf_width = scrollable_frame.winfo_width()
                    sf_height = scrollable_frame.winfo_height()
                    logger.info(f"Scrollable frame dimensions: {sf_width}x{sf_height}")
                except Exception as e:
                    logger.warning(f"Could not get scrollable frame dimensions: {e}")
                    
            else:
                logger.error("No scrollable_frame found in workflow section")
        else:
            logger.error("No workflow_section found in welcome screen")
        
        # Show the window for visual inspection
        logger.info("Window created. Check visually for workflow cards.")
        logger.info("Close the window to continue...")
        
        # Run for a few seconds to allow visual inspection
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = test_workflow_visibility()
    if success:
        print("Test completed successfully")
    else:
        print("Test failed")
        sys.exit(1)
