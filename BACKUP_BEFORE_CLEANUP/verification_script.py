#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script that writes results to a file
"""

import os
import sys
import traceback
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def write_log(message):
    """Write message to log file"""
    with open("verification_results.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def test_fixes():
    """Test the fixes we implemented"""
    write_log("=== Checker App Fix Verification ===")
    
    # Test 1: AccessibilityUserProfileManager import
    try:
        from accessibility_extensions import AccessibilityUserProfileManager
        write_log("✓ SUCCESS: AccessibilityUserProfileManager imported successfully")
        
        # Test instantiation
        profile_manager = AccessibilityUserProfileManager()
        write_log("✓ SUCCESS: AccessibilityUserProfileManager instantiated successfully")
        
        # Test basic functionality
        profiles = profile_manager.list_profiles()
        write_log(f"✓ SUCCESS: Profile manager lists {len(profiles)} profiles")
        
    except Exception as e:
        write_log(f"✗ FAILED: AccessibilityUserProfileManager test failed: {e}")
        write_log(f"Error details: {traceback.format_exc()}")
    
    # Test 2: CheckerApp import and basic initialization
    try:
        from checker_app import CheckerApp
        write_log("✓ SUCCESS: CheckerApp imported successfully")
        
        # Test that we can create an instance without GUI
        class TestCheckerApp(CheckerApp):
            def run(self):
                # Override run to skip GUI initialization
                self.setup_root()
                return True
        
        app = TestCheckerApp()
        write_log("✓ SUCCESS: CheckerApp instance created successfully")
        
    except Exception as e:
        write_log(f"✗ FAILED: CheckerApp test failed: {e}")
        write_log(f"Error details: {traceback.format_exc()}")
    
    # Test 3: WelcomeScreen import
    try:
        from welcome_screen import WelcomeScreen
        write_log("✓ SUCCESS: WelcomeScreen imported successfully")
        
        # Check if enhance_button_interactions method exists
        if hasattr(WelcomeScreen, 'enhance_button_interactions'):
            write_log("✓ SUCCESS: enhance_button_interactions method found in WelcomeScreen")
        else:
            write_log("✗ FAILED: enhance_button_interactions method missing from WelcomeScreen")
            
    except Exception as e:
        write_log(f"✗ FAILED: WelcomeScreen test failed: {e}")
        write_log(f"Error details: {traceback.format_exc()}")
    
    # Test 4: File operations
    try:
        from file_operations import lese_datei
        write_log("✓ SUCCESS: file_operations.lese_datei imported successfully")
    except Exception as e:
        write_log(f"✗ FAILED: file_operations.lese_datei import failed: {e}")
    
    write_log("=== Verification Complete ===")

if __name__ == "__main__":
    # Clear previous log
    if os.path.exists("verification_results.txt"):
        os.remove("verification_results.txt")
    
    test_fixes()
    
    print("Verification complete. Check verification_results.txt for results.")
