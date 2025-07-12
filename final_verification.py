#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final verification test for the fixed Prüfung workflow

This test verifies that:
1. All required modules can be imported
2. The PruefungWorkflow can be instantiated
3. All required controller methods exist
4. The UI can be displayed
"""

import sys
import os
import traceback

# Suppress debug output during imports
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, *args):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        with SuppressOutput():
            import customtkinter as ctk
            from pruefung_workflow import PruefungWorkflow
            from pruefung_workflow_controller import PruefungWorkflowController
            from ui_components.pruefung_workflow_view import PruefungWorkflowView
        
        print("All imports successful")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        traceback.print_exc() # Add this to see the full error
        return False

def test_controller_methods():
    """Test if controller has all required methods"""
    print("Testing controller methods...")
    
    root = None
    try:
        import customtkinter as ctk
        # Controller might instantiate Tkinter variables, so a root is needed
        root = ctk.CTk()
        root.withdraw()

        # The controller is initialized by the workflow with an app object.
        # We create a mock object to simulate this.
        class MockApp:
            def __init__(self, r):
                self.root = r
        mock_app = MockApp(root)

        with SuppressOutput():
            from pruefung_workflow_controller import PruefungWorkflowController
            controller = PruefungWorkflowController(app=mock_app)
        
        required_methods = [
            'select_all_checks', 'clear_all_file_pairs', 'deselect_all_checks',
            'start_checks', 'stop_checking_process', 'export_results_as_pdf',
            'add_file_pair', 'remove_file_pair_by_id'
        ]
        
        missing = []
        for method in required_methods:
            if not hasattr(controller, method):
                missing.append(method)
        
        if missing:
            print(f"Missing methods: {missing}")
            return False
        
        print("All controller methods present")
        return True
        
    except Exception as e:
        print(f"Controller test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        # Ensure root is destroyed on failure too
        if root and root.winfo_exists():
            root.destroy()

def test_workflow_instantiation():
    """Test if workflow can be instantiated without Tcl errors."""
    print("Testing workflow instantiation...")
    
    root = None
    try:
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw() # Keep it hidden

        class MockApp:
            def __init__(self, r):
                self.root = r
                self.main_container = ctk.CTkFrame(r) # The workflow expects a main_container
                self.header_frame = ctk.CTkFrame(r) # Add the missing attribute
            def show_frame(self, name):
                pass # Mock method
            def go_home(self):
                pass # Mock method

        mock_app = MockApp(root)
        
        # Create dummy project data as required by the PruefungWorkflow
        dummy_project_data = {
            "kunde_name": "Verification Customer",
            "auftragsnummer": "VERIFY-001",
            "dateipfade": ["path/to/dummy1.pdf", "path/to/dummy2.pdf"]
        }

        with SuppressOutput():
            from pruefung_workflow import PruefungWorkflow
            # Correctly instantiate the workflow with parent, app, and project_data
            workflow = PruefungWorkflow(parent=mock_app.main_container, app=mock_app, project_data=dummy_project_data)
        
        print("Workflow instantiated successfully")
        return True
    except Exception as e:
        print(f"Workflow instantiation failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if root and root.winfo_exists():
            root.destroy()

def test_ui_display():
    """Test if the UI can be created, displayed, and destroyed."""
    print("Testing UI display...")
    
    root = None
    try:
        import customtkinter as ctk
        from pruefung_workflow import PruefungWorkflow

        class MockApp:
            def __init__(self, r):
                self.root = r
                self.main_container = ctk.CTkFrame(r)
                self.main_container.pack(fill="both", expand=True)
                self.header_frame = ctk.CTkFrame(r) # Add the missing attribute
            def show_frame(self, name):
                pass
            def go_home(self):
                pass

        root = ctk.CTk()
        root.geometry("1400x900")
        app = MockApp(root)
        
        # Create dummy project data as required by the PruefungWorkflow
        dummy_project_data = {
            "kunde_name": "UI Test Customer",
            "auftragsnummer": "UI-TEST-002",
            "dateipfade": []
        }

        workflow = PruefungWorkflow(parent=app.main_container, app=app, project_data=dummy_project_data)
        workflow.grid(row=0, column=0, sticky="nsew")
        
        # Let the UI update for a moment
        root.update()
        
        # The PruefungWorkflow is a frame, it doesn't have a 'show' method.
        # It's displayed by the main app's show_frame method, but for this test,
        # we can just grid it to make sure it renders without error.
        workflow.grid(row=0, column=0, sticky="nsew")

        # Let the UI update for a moment
        root.update()
        
        print("UI displayed and destroyed successfully")
        return True
    except Exception as e:
        print(f"UI display test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if root and root.winfo_exists():
            root.destroy()


if __name__ == "__main__":
    print("\n=========================================================\n====\n==== PRÜFUNG WORKFLOW FINAL VERIFICATION ====\n=========================================================\n====")
    
    tests = [
        test_imports,
        test_controller_methods,
        test_workflow_instantiation,
        test_ui_display
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        if not result:
            break # Stop on first failure
        print("-" * 20)

    if all(results):
        print("\n=========================================================\n====\nALL TESTS PASSED!\n=========================================================\n====")
        sys.exit(0)
    else:
        print("\n=========================================================\n====\nSOME TESTS FAILED!\nCheck the error messages above\n=========================================================\n====")
        sys.exit(1)
