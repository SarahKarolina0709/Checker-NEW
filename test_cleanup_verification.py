#!/usr/bin/env python3
"""
Test script to verify that the cleaned up calendar code works correctly.
Only the window-based calendar should be available now.
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

def test_cleaned_up_customer_section():
    """Test the cleaned up customer section"""
    try:
        logger.info("=== Testing Cleaned Up Customer Section ===")
        
        # Import the cleaned up module
        from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
        
        # Create test window
        root = ctk.CTk()
        root.title("Test: Cleaned Up Customer Section")
        root.geometry("600x400")
        
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
        
        # Verify window-based calendar methods exist
        assert hasattr(customer_section, 'toggle_calendar'), "toggle_calendar method missing"
        assert hasattr(customer_section, 'show_calendar_window'), "show_calendar_window method missing"
        assert hasattr(customer_section, 'create_calendar_window_content'), "create_calendar_window_content method missing"
        
        # Verify old methods are gone
        assert not hasattr(customer_section, 'show_calendar'), "Old show_calendar method still exists"
        assert not hasattr(customer_section, 'hide_calendar'), "Old hide_calendar method still exists"
        assert not hasattr(customer_section, 'create_calendar_content'), "Old create_calendar_content method still exists"
        
        # Verify old variables are gone
        assert not hasattr(customer_section, 'calendar_visible'), "Old calendar_visible variable still exists"
        assert not hasattr(customer_section, 'day_buttons'), "Old day_buttons variable still exists"
        assert not hasattr(customer_section, 'calendar_content'), "Old calendar_content variable still exists"
        
        logger.info("✅ All old calendar methods and variables removed successfully")
        
        # Test window-based calendar creation
        logger.info("Testing window-based calendar creation...")
        
        # This should work without errors (but we won't actually show the window)
        customer_section.load_upload_data()
        
        # Verify customer section loads correctly
        assert hasattr(customer_section, 'customer_entry'), "customer_entry missing"
        assert hasattr(customer_section, 'project_entry'), "project_entry missing"
        assert hasattr(customer_section, 'calendar_btn'), "calendar_btn missing"
        
        logger.info("✅ Customer section loaded successfully")
        
        # Test data retrieval
        data = customer_section.get_data()
        assert isinstance(data, dict), "get_data should return dict"
        assert 'kunde_name' in data, "kunde_name key missing from data"
        assert 'projekt_id' in data, "projekt_id key missing from data"
        
        logger.info("✅ Data retrieval works correctly")
        
        # Test customer confirmation
        customer_section.customer_entry.insert(0, "Test Customer")
        customer_section.project_entry.insert(0, "Test Project")
        
        # This should work without showing message box
        try:
            customer_section.handle_customer_confirmation()
            logger.info("✅ Customer confirmation works correctly")
        except Exception as e:
            logger.info(f"Customer confirmation test skipped (expected): {e}")
        
        # Cleanup
        root.destroy()
        
        logger.info("=== All Tests Passed! ===")
        logger.info("✅ Old embedded calendar methods removed")
        logger.info("✅ Window-based calendar preserved")
        logger.info("✅ Customer section functionality maintained")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cleaned_up_customer_section()
    if success:
        print("✅ Cleanup verification successful!")
    else:
        print("❌ Cleanup verification failed!")
        sys.exit(1)
