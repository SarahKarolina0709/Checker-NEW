#!/usr/bin/env python3
"""
Test script to verify calendar visibility and functionality
"""

import customtkinter as ctk
import sys
import os
import logging
from pathlib import Path

# Add the current directory to sys.path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the main app
from checker_app import CheckerApp

def test_calendar_visibility():
    """Test the calendar visibility"""
    try:
        print("Starting calendar visibility test...")
        
        # Create app
        app = CheckerApp()
        
        # Define a test function to run after the app is initialized
        def test_calendar_after_init():
            try:
                print("Testing calendar after initialization...")
                
                # Access the customer section
                if hasattr(app, 'welcome_screen') and app.welcome_screen:
                    if hasattr(app.welcome_screen, 'customer_section'):
                        customer_section = app.welcome_screen.customer_section
                        
                        print(f"Initial calendar state: {customer_section.calendar_visible}")
                        
                        # Check if calendar_content exists and its properties
                        if hasattr(customer_section, 'calendar_content'):
                            calendar_content = customer_section.calendar_content
                            print(f"Calendar content exists: {calendar_content}")
                            
                            # Check grid info
                            grid_info = calendar_content.grid_info()
                            print(f"Calendar grid info: {grid_info}")
                            
                            # Check if it's actually visible
                            try:
                                visible = calendar_content.winfo_viewable()
                                print(f"Calendar is viewable: {visible}")
                                height = calendar_content.winfo_height()
                                width = calendar_content.winfo_width()
                                print(f"Calendar dimensions: {width}x{height}")
                            except Exception as e:
                                print(f"Error checking calendar visibility: {e}")
                            
                            # Try to toggle the calendar
                            print("Toggling calendar...")
                            customer_section.toggle_calendar()
                            
                            # Check state after toggle
                            print(f"Calendar state after toggle: {customer_section.calendar_visible}")
                            
                            # Check grid info after toggle
                            grid_info_after = calendar_content.grid_info()
                            print(f"Calendar grid info after toggle: {grid_info_after}")
                            
                            # Check if it's visible after toggle
                            try:
                                visible_after = calendar_content.winfo_viewable()
                                print(f"Calendar is viewable after toggle: {visible_after}")
                                height_after = calendar_content.winfo_height()
                                width_after = calendar_content.winfo_width()
                                print(f"Calendar dimensions after toggle: {width_after}x{height_after}")
                            except Exception as e:
                                print(f"Error checking calendar visibility after toggle: {e}")
                            
                            # Test toggle again to hide
                            print("Toggling calendar again to hide...")
                            customer_section.toggle_calendar()
                            print(f"Calendar state after second toggle: {customer_section.calendar_visible}")
                            
                        else:
                            print("ERROR: Calendar content not found!")
                    else:
                        print("ERROR: Customer section not found!")
                else:
                    print("ERROR: Welcome screen not found!")
                    
            except Exception as e:
                print(f"ERROR during calendar test: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule the test to run after a short delay
        app.root.after(2000, test_calendar_after_init)
        
        # Run the app
        app.run()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_visibility()
