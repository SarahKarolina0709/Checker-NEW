#!/usr/bin/env python3
"""Test script to verify performance monitor functionality"""

try:
    from structured_logging import PerformanceLogger
    print("✓ PerformanceLogger import successful")
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"✗ PerformanceLogger import failed: {e}")
    STRUCTURED_LOGGING_AVAILABLE = False

if STRUCTURED_LOGGING_AVAILABLE:
    try:
        from structured_logging import LoggerFactory
        print("✓ LoggerFactory import successful")
        
        # Test get_performance_logger method
        logger = LoggerFactory.get_performance_logger("test")
        print("✓ get_performance_logger method works")
        
        # Test creating performance monitor
        from welcome_screen_components.performance_monitor import WelcomeScreenPerformanceMonitor
        print("✓ WelcomeScreenPerformanceMonitor import successful")
        
        # Test with mock welcome screen
        class MockWelcomeScreen:
            pass
        
        ws = MockWelcomeScreen()
        monitor = WelcomeScreenPerformanceMonitor(ws)
        print("✓ WelcomeScreenPerformanceMonitor creation successful")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Structured logging not available, skipping tests")
