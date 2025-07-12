#!/usr/bin/env python3
"""
Test script to check the actual customer section calendar window.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockApp:
    """Mock app for testing"""
    def __init__(self):
        self.logger = logger
        self.kunden_manager = None

class MockWelcomeScreen:
    """Mock welcome screen for testing"""
    def __init__(self):
        pass

def test_calendar_window():
    """Test the actual calendar window"""
    try:
        logger.info("=== Testing Calendar Window ===")
        
        # Import the actual module
        from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
        
        # Create test window
        root = ctk.CTk()
        root.title("Test: Calendar Window Debug")
        root.geometry("800x600")
        
        # Create mock dependencies
        app = MockApp()
        welcome_screen = MockWelcomeScreen()
        
        # Create the customer section
        customer_section = CustomerSectionWithCalendar(
            master=root,
            app=app,
            welcome_screen=welcome_screen
        )
        customer_section.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Function to open calendar window and debug
        def debug_calendar():
            logger.info("Opening calendar window for debug...")
            
            # Open calendar window
            customer_section.toggle_calendar()
            
            # Check if window was created
            if hasattr(customer_section, 'calendar_window'):
                logger.info("✅ Calendar window created successfully")
                
                # Check if calendar frame exists
                if hasattr(customer_section, 'window_calendar_frame'):
                    logger.info("✅ Window calendar frame exists")
                    
                    # Check children of calendar frame
                    children = customer_section.window_calendar_frame.winfo_children()
                    logger.info(f"Calendar frame has {len(children)} children")
                    
                    for i, child in enumerate(children):
                        logger.info(f"Child {i}: {type(child).__name__} - Text: {getattr(child, 'cget', lambda x: 'N/A')('text') if hasattr(child, 'cget') else 'N/A'}")
                
                # Check if day buttons were created
                if hasattr(customer_section, 'window_day_buttons'):
                    day_buttons = customer_section.window_day_buttons
                    logger.info(f"✅ Found {len(day_buttons)} day buttons")
                    
                    for day, button in day_buttons.items():
                        button_text = button.cget('text') if hasattr(button, 'cget') else 'N/A'
                        logger.info(f"Day {day}: Button text = '{button_text}'")
                else:
                    logger.error("❌ No window_day_buttons found")
            else:
                logger.error("❌ Calendar window not created")
        
        # Add debug button
        debug_btn = ctk.CTkButton(
            root,
            text="🔍 Debug Calendar Window",
            command=debug_calendar,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        debug_btn.pack(pady=10)
        
        # Automatically trigger debug after a short delay
        root.after(1000, debug_calendar)
        
        # Run the app
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_window()
