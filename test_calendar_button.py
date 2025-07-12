#!/usr/bin/env python3
"""
Test script to specifically test the upload calendar button functionality
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

def test_calendar_button():
    """Test the calendar button functionality"""
    try:
        print("Testing calendar button functionality...")
        
        # Import the main app
        from checker_app import CheckerApp
        
        # Create app
        app = CheckerApp()
        
        # Define a test function to run after the app is initialized
        def test_button_click():
            try:
                print("Testing calendar button click...")
                
                # Access the customer section
                if hasattr(app, 'welcome_screen') and app.welcome_screen:
                    if hasattr(app.welcome_screen, 'customer_section'):
                        customer_section = app.welcome_screen.customer_section
                        
                        print(f"Initial calendar state: {customer_section.calendar_visible}")
                        
                        # Check if calendar button exists
                        if hasattr(customer_section, 'calendar_btn'):
                            print("Calendar button found, simulating click...")
                            
                            # Get button text before click
                            button_text_before = customer_section.calendar_btn.cget("text")
                            print(f"Button text before click: {button_text_before}")
                            
                            # Simulate button click
                            customer_section.calendar_btn.invoke()
                            
                            # Check state after click
                            print(f"Calendar state after click: {customer_section.calendar_visible}")
                            
                            # Get button text after click
                            button_text_after = customer_section.calendar_btn.cget("text")
                            print(f"Button text after click: {button_text_after}")
                            
                            # Check if calendar content is visible
                            if hasattr(customer_section, 'calendar_content'):
                                calendar_content = customer_section.calendar_content
                                grid_info = calendar_content.grid_info()
                                print(f"Calendar grid info after click: {grid_info}")
                                
                                # Check dimensions
                                try:
                                    app.root.update_idletasks()
                                    height = calendar_content.winfo_height()
                                    width = calendar_content.winfo_width()
                                    print(f"Calendar dimensions after click: {width}x{height}")
                                    
                                    # Check if calendar frame exists
                                    if hasattr(customer_section, 'calendar_frame'):
                                        cal_frame = customer_section.calendar_frame
                                        cal_height = cal_frame.winfo_height()
                                        cal_width = cal_frame.winfo_width()
                                        print(f"Calendar frame dimensions: {cal_width}x{cal_height}")
                                        
                                        # Check if calendar frame is visible
                                        cal_visible = cal_frame.winfo_viewable()
                                        print(f"Calendar frame visible: {cal_visible}")
                                        
                                        # Check if calendar frame has children
                                        children = cal_frame.winfo_children()
                                        print(f"Calendar frame children: {len(children)}")
                                        
                                    else:
                                        print("Calendar frame not found!")
                                        
                                except Exception as e:
                                    print(f"Error checking calendar dimensions: {e}")
                            
                            # Test clicking again to hide
                            print("Clicking button again to hide calendar...")
                            customer_section.calendar_btn.invoke()
                            print(f"Calendar state after second click: {customer_section.calendar_visible}")
                            
                        else:
                            print("ERROR: Calendar button not found!")
                    else:
                        print("ERROR: Customer section not found!")
                else:
                    print("ERROR: Welcome screen not found!")
                    
            except Exception as e:
                print(f"ERROR during button test: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule the test to run after a short delay
        app.root.after(3000, test_button_click)
        
        # Run the app
        app.run()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_button()
