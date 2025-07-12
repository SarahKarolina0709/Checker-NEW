#!/usr/bin/env python3
"""Test script to verify ultra modern welcome screen functionality"""

import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Test importing welcome screen components
    from welcome_screen_components.performance_monitor import WelcomeScreenPerformanceMonitor
    print("✓ WelcomeScreenPerformanceMonitor import successful")
    
    # Test structured logging
    from structured_logging import LoggerFactory
    print("✓ LoggerFactory import successful")
    
    # Test the specific method
    logger = LoggerFactory.get_performance_logger("test")
    print("✓ get_performance_logger method works")
    
    # Check what methods are available
    print(f"Available methods: {[m for m in dir(LoggerFactory) if not m.startswith('_')]}")
    
    # Test creating performance monitor with minimal setup
    class MockWelcomeScreen:
        def __init__(self):
            import logging
            self.logger = logging.getLogger("test")
    
    ws = MockWelcomeScreen()
    monitor = WelcomeScreenPerformanceMonitor(ws)
    print("✓ WelcomeScreenPerformanceMonitor creation successful")
    
    print("\nAll tests passed! The performance monitor should work correctly.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
