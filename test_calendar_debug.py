#!/usr/bin/env python3
"""
Debug script to test the upload calendar functionality
"""

import customtkinter as ctk
import sys
import os
import logging
from pathlib import Path

# Add the current directory to sys.path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the main app
from checker_app import CheckerApp

def test_calendar_functionality():
    """Test the calendar functionality"""
    try:
        print("Starting calendar debug test...")
        
        # Create app
        app = CheckerApp()
        
        # Wait a bit and then try to access the calendar
        def test_after_init():
            try:
                print("Testing calendar access...")
                
                # Check if welcome screen exists
                if hasattr(app, 'welcome_screen') and app.welcome_screen:
                    print("Welcome screen found")
                    
                    # Check if customer section exists
                    if hasattr(app.welcome_screen, 'customer_section'):
                        print("Customer section found")
                        customer_section = app.welcome_screen.customer_section
                        
                        # Check if calendar button exists
                        if hasattr(customer_section, 'calendar_btn'):
                            print("Calendar button found")
                            
                            # Check if calendar content exists
                            if hasattr(customer_section, 'calendar_content'):
                                print("Calendar content found")
                                print(f"Calendar visible: {customer_section.calendar_visible}")
                                
                                # Try to toggle calendar
                                print("Attempting to toggle calendar...")
                                customer_section.toggle_calendar()
                                print(f"Calendar visible after toggle: {customer_section.calendar_visible}")
                                
                            else:
                                print("ERROR: Calendar content not found!")
                        else:
                            print("ERROR: Calendar button not found!")
                    else:
                        print("ERROR: Customer section not found!")
                else:
                    print("ERROR: Welcome screen not found!")
                    
            except Exception as e:
                print(f"ERROR during test: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule the test
        app.root.after(1000, test_after_init)
        
        # Run the app
        app.run()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_functionality()
