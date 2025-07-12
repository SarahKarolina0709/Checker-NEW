#!/usr/bin/env python3
"""
Quick test script to verify that the pyimage garbage collection fix works
by testing workflow navigation and button creation.
"""

if __name__ == "__main__":
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from checker_app import CheckerApp
        
        print("Creating CheckerApp instance...")
        app = CheckerApp()
        
        print("Starting application...")
        
        # Test workflow creation after a short delay
        def test_workflow():
            try:
                print("Testing Pruefung workflow creation...")
                app.start_workflow("pruefung_workflow", {"kunde_name": "Test", "auftragsnummer": "TEST-001"})
                print("Workflow created successfully!")
            except Exception as e:
                print(f"Error creating workflow: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule test after 3 seconds
        app.root.after(3000, test_workflow)
        
        # Schedule app close after 10 seconds (for automated testing)
        app.root.after(10000, app.root.destroy)
        
        app.root.mainloop()
        
        print("Application closed. Testing completed.")
        
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
