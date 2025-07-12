#!/usr/bin/env python3
"""
Debugging script to check register_persistent_button method signature
"""

import sys
import os
import inspect

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the CheckerApp class
    from checker_app import CheckerApp
    
    print("=== Method Signature Debug ===")
    
    # Check if the class has the method
    if hasattr(CheckerApp, 'register_persistent_button'):
        method = getattr(CheckerApp, 'register_persistent_button')
        print(f"Method found: {method}")
        
        # Get method signature
        sig = inspect.signature(method)
        print(f"Method signature: {sig}")
        
        # List parameters
        print("Parameters:")
        for name, param in sig.parameters.items():
            print(f"  {name}: {param}")
            
        # Check if parameters exist
        params = list(sig.parameters.keys())
        print(f"Parameter names: {params}")
        
        # Test parameter requirements
        required_params = [name for name, param in sig.parameters.items() 
                          if param.default == inspect.Parameter.empty and name != 'self']
        optional_params = [name for name, param in sig.parameters.items() 
                          if param.default != inspect.Parameter.empty]
        
        print(f"Required parameters: {required_params}")
        print(f"Optional parameters: {optional_params}")
        
        # Check if icon_ref and description are in the signature
        if 'icon_ref' in params:
            print("✓ icon_ref parameter found")
        else:
            print("✗ icon_ref parameter NOT found")
            
        if 'description' in params:
            print("✓ description parameter found")
        else:
            print("✗ description parameter NOT found")
            
    else:
        print("ERROR: register_persistent_button method not found in CheckerApp")
        
    # List all methods containing 'register'
    print("\n=== All methods containing 'register' ===")
    for attr_name in dir(CheckerApp):
        if 'register' in attr_name.lower():
            attr = getattr(CheckerApp, attr_name)
            if callable(attr):
                try:
                    sig = inspect.signature(attr)
                    print(f"{attr_name}: {sig}")
                except Exception as e:
                    print(f"{attr_name}: Error getting signature - {e}")
    
except Exception as e:
    print(f"Error importing or analyzing: {e}")
    import traceback
    traceback.print_exc()
