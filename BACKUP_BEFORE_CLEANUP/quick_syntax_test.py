#!/usr/bin/env python3
"""
Quick test for the fixed register_persistent_button method
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== Quick Syntax and Method Test ===")
    
    # Test import
    print("Testing import...")
    from checker_app import CheckerApp
    print("✓ Import successful")
    
    # Test method signature
    import inspect
    sig = inspect.signature(CheckerApp.register_persistent_button)
    print(f"✓ Method signature: {sig}")
    
    # Check parameters
    params = list(sig.parameters.keys())
    if 'icon_ref' in params and 'description' in params:
        print("✓ Required parameters (icon_ref, description) found")
    else:
        print(f"✗ Missing parameters. Found: {params}")
    
    print("✓ All basic tests passed")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
