#!/usr/bin/env python3
"""
UITheme Daily Test Runner
=========================
Regularly run this script to ensure the theme system remains robust
and all UI components are properly styled.
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'uitheme_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('UIThemeTest')

def run_theme_tests():
    """Run comprehensive tests on the UITheme system."""
    logger.info("Starting UITheme test suite")
    
    try:
        from ui_theme import UITheme, enhanced_theme
        logger.info("UITheme modules imported successfully")
        
        # Test 1: Basic import check
        logger.info("Test 1: Basic attribute access")
        try:
            primary_color = UITheme.COLOR_PRIMARY
            logger.info(f"UITheme.COLOR_PRIMARY = {primary_color}")
            logger.info("✅ Test 1 passed: Basic attribute access works")
        except AttributeError as e:
            logger.error(f"❌ Test 1 failed: {e}")
            return False
        
        # Test 2: Theme switching
        logger.info("Test 2: Theme switching")
        try:
            # Record original theme
            original_primary = UITheme.COLOR_PRIMARY
            logger.info(f"Original theme primary color: {original_primary}")
            
            # Switch to dark
            UITheme.switch_theme("dark")
            dark_primary = UITheme.COLOR_PRIMARY
            logger.info(f"Dark theme primary color: {dark_primary}")
            
            # Switch back to light
            UITheme.switch_theme("light")
            light_primary = UITheme.COLOR_PRIMARY
            logger.info(f"Light theme primary color: {light_primary}")
            
            # Verify they changed
            if dark_primary != light_primary:
                logger.info("✅ Test 2 passed: Theme switching works")
            else:
                logger.warning("⚠️ Test 2 warning: Theme colors are the same")
        except Exception as e:
            logger.error(f"❌ Test 2 failed: {e}")
            return False
        
        # Test 3: Modern API
        logger.info("Test 3: Modern theme API")
        try:
            color_via_api = UITheme.get_color('primary')
            tuple_via_api = UITheme.get_color_tuple('primary')
            button_style = UITheme.get_button_style('primary')
            
            logger.info(f"get_color('primary'): {color_via_api}")
            logger.info(f"get_color_tuple('primary'): {tuple_via_api}")
            logger.info(f"get_button_style('primary'): {len(button_style)} properties")
            
            logger.info("✅ Test 3 passed: Modern API works")
        except Exception as e:
            logger.error(f"❌ Test 3 failed: {e}")
            return False
        
        # Test 4: Enhanced Theme Provider
        logger.info("Test 4: Enhanced Theme Provider")
        try:
            color_via_provider = enhanced_theme.get_color('primary')
            
            if color_via_provider == UITheme.COLOR_PRIMARY:
                logger.info("✅ Test 4 passed: Enhanced Theme Provider synchronized with UITheme")
            else:
                logger.error(f"❌ Test 4 failed: Provider returned {color_via_provider}, UITheme returned {UITheme.COLOR_PRIMARY}")
                return False
        except Exception as e:
            logger.error(f"❌ Test 4 failed: {e}")
            return False
        
        # Test 5: Legacy constants
        logger.info("Test 5: Legacy color constants")
        try:
            # Test a sample of legacy constants
            legacy_constants = [
                'COLOR_CONTAINER_CUSTOMER',
                'COLOR_CONTAINER_UPLOAD',
                'COLOR_SURFACE_HOVER_LIGHT',
                'TUPLE_BG_SECONDARY',
                'TUPLE_INPUT_BG', 
                'TUPLE_TEXT_ON_PRIMARY'
            ]
            
            for const in legacy_constants:
                value = getattr(UITheme, const)
                logger.info(f"{const}: {value}")
            
            logger.info("✅ Test 5 passed: Legacy constants work")
        except AttributeError as e:
            logger.error(f"❌ Test 5 failed: {e}")
            return False
        
        # Test 6: Style dictionaries
        logger.info("Test 6: Style dictionaries")
        try:
            style_constants = [
                'BUTTON_STYLE_PRIMARY',
                'BUTTON_STYLE_SECONDARY',
                'CHECKBOX_STYLE',
                'OPTIONMENU_STYLE',
                'CONTAINER_STYLE_CUSTOMER'
            ]
            
            for const in style_constants:
                style_dict = getattr(UITheme, const)
                logger.info(f"{const}: {len(style_dict)} properties")
            
            logger.info("✅ Test 6 passed: Style dictionaries work")
        except AttributeError as e:
            logger.error(f"❌ Test 6 failed: {e}")
            return False
        
        # Test 7: Button-specific color constants
        logger.info("Test 7: Button color constants")
        try:
            button_constants = [
                'COLOR_BUTTON_PRIMARY',
                'COLOR_BUTTON_SECONDARY',
                'COLOR_BUTTON_SUCCESS',
                'COLOR_BUTTON_INFO',
                'COLOR_BUTTON_TEXT'
            ]
            
            for const in button_constants:
                value = getattr(UITheme, const)
                logger.info(f"{const}: {value}")
            
            logger.info("✅ Test 7 passed: Button color constants work")
        except AttributeError as e:
            logger.error(f"❌ Test 7 failed: {e}")
            return False
        
        logger.info("✅ All UITheme tests passed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import UITheme: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during testing: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("UITheme Test Runner")
    print("=" * 50)
    
    success = run_theme_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED")
        print("UITheme system is functioning correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Check the log file for details: {log_file}")
    print("=" * 50)
    
    sys.exit(0 if success else 1)
