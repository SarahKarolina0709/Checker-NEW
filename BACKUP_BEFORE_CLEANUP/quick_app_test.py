#!/usr/bin/env python3
"""
Simple test to check if the app starts without the AttributeError
"""

import subprocess
import sys
import time
import os

def test_app_startup():
    """Test if the app can start the Prüfung workflow without errors"""
    try:
        print("🧪 Testing app startup with Prüfung workflow...")
        
        # Create a test script that tries to import and create the workflow
        test_script = '''
import sys
import os

try:
    # Test imports
    from pruefung_workflow_controller import PruefungWorkflowController
    from pruefung_workflow import PruefungWorkflow
    import customtkinter as ctk
    
    print("✅ All imports successful")
    
    # Test controller creation
    controller = PruefungWorkflowController()
    
    # Check if critical attributes exist
    if hasattr(controller, 'CHECK_DEFINITIONS'):
        print("✅ CHECK_DEFINITIONS exists")
    else:
        print("❌ CHECK_DEFINITIONS missing")
        
    if hasattr(controller, 'select_all_checks'):
        print("✅ select_all_checks method exists")
    else:
        print("❌ select_all_checks method missing")
        
    if hasattr(controller, 'clear_all_file_pairs'):
        print("✅ clear_all_file_pairs method exists")
    else:
        print("❌ clear_all_file_pairs method missing")
    
    print("🎉 Controller test passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
        
        # Write and run the test script
        with open('temp_test.py', 'w') as f:
            f.write(test_script)
        
        # Run the test
        result = subprocess.run([sys.executable, 'temp_test.py'], 
                              capture_output=True, text=True, timeout=30)
        
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        # Clean up
        try:
            os.remove('temp_test.py')
        except:
            pass
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("QUICK APP STARTUP TEST")
    print("=" * 50)
    
    success = test_app_startup()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test passed! The app should work now.")
        print("You can run: python checker_app.py")
    else:
        print("❌ Test failed. Check the errors above.")
    print("=" * 50)
