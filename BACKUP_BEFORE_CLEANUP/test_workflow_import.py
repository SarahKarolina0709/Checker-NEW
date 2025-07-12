#!/usr/bin/env python3
"""
Test script to verify the PruefungWorkflow can be imported and instantiated properly.
"""
# import lite_nuclear_ctk_patch as ctk_patch # Apply nuclear anti-dark-mode patch

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test importing the PruefungWorkflow class"""
    try:
        print("Testing import of pruefung_workflow...")
        sys.stdout.flush()
        from pruefung_workflow import PruefungWorkflow
        print("✓ Import successful!")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        sys.stdout.flush()
        traceback.print_exc()
        return False

def test_instantiation():
    """Test creating an instance of PruefungWorkflow"""
    try:
        print("Testing instantiation of PruefungWorkflow...")
        import tkinter as tk
        import customtkinter as ctk
        
        # Create a minimal root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the test window
        
        content_frame = ctk.CTkFrame(root)
        
        from pruefung_workflow import PruefungWorkflow
        
        class DummyApp:
            def __init__(self, root_window):
                self.root = root_window
            def get_current_project_data(self):
                return {"files": [None, None], "selected_checks": []}

        app = DummyApp(root)

        # Test instantiation
        workflow = PruefungWorkflow(
            parent=content_frame,
            app=app,
            project_data=app.get_current_project_data()
        )
        
        print("✓ Instantiation successful!")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Testing pruefung_workflow.py")
    print("=" * 50)
    
    # Test import
    import_ok = test_import()
    
    if import_ok:
        # Test instantiation
        instantiation_ok = test_instantiation()
        
        if instantiation_ok:
            print("\n✓ All tests passed! The PruefungWorkflow should work correctly.")
            return True
        else:
            print("\n✗ Instantiation test failed.")
            return False
    else:
        print("\n✗ Import test failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
