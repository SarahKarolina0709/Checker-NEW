#!/usr/bin/env python3
"""
Test the specific error scenario: simulate starting the Prüfung workflow
and check for the 'get_tab_configurations' AttributeError
"""

import sys
import os
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_specific_error():
    print("Testing the specific error scenario...")
    
    try:
        # Create minimal tkinter context
        root = tk.Tk()
        root.withdraw()
        
        # Import and create the exact components that were failing
        from pruefung_workflow_controller import PruefungWorkflowController
        
        # Create controller like the workflow does
        controller = PruefungWorkflowController()
        
        # This was the exact error: AttributeError: 'PruefungWorkflowController' object has no attribute 'get_tab_configurations'
        print("Testing get_tab_configurations method...")
        tabs = controller.get_tab_configurations()
        
        if tabs and isinstance(tabs, dict):
            print(f"✓ SUCCESS: get_tab_configurations returned {len(tabs)} tab configurations")
            for tab_key, config in tabs.items():
                if 'title' in config and 'color' in config:
                    print(f"  ✓ {tab_key}: {config['title']} ({config['color']})")
                else:
                    print(f"  ✗ {tab_key}: Missing title or color")
                    return False
        else:
            print("✗ get_tab_configurations returned invalid data")
            return False
        
        # Test other methods that might be called
        print("\nTesting other critical methods...")
        
        # Test on_language_change
        try:
            controller.on_language_change()
            print("✓ on_language_change method works")
        except Exception as e:
            print(f"✗ on_language_change failed: {e}")
            return False
        
        # Test CHECK_DEFINITIONS access
        if hasattr(controller, 'CHECK_DEFINITIONS'):
            print(f"✓ CHECK_DEFINITIONS available with {len(controller.CHECK_DEFINITIONS)} checks")
        else:
            print("✗ CHECK_DEFINITIONS missing")
            return False
        
        # Test set_view method (this initializes the tkinter variables)
        class MockView:
            def __init__(self):
                import customtkinter as ctk
                self.language_var = ctk.StringVar(value="Deutsch")
            
            def update_file_pair_display(self, pairs):
                pass
        
        mock_view = MockView()
        controller.set_view(mock_view)
        print("✓ set_view method works and initialized check variables")
        
        # Test that check variables are now initialized
        if controller.selected_checks:
            print(f"✓ Check selection variables initialized: {len(controller.selected_checks)} checks")
        else:
            print("✗ Check selection variables not initialized")
            return False
        
        root.destroy()
        
        print("\n🎉 ALL TESTS PASSED! The error should be fixed!")
        print("The 'PruefungWorkflowController' object has no attribute 'get_tab_configurations' error should no longer occur.")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_error()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)
