"""
Simplified test script to run the fixed PruefungWorkflow
"""
import traceback
import sys
import customtkinter as ctk

def main():
    try:
        # Set up the root window
        root = ctk.CTk()
        root.title("PruefungWorkflow Test (Simple)")
        root.geometry("1200x800")
        
        # Set up a frame to contain the workflow
        content_frame = ctk.CTkFrame(root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Import workflow module inside try block to capture import errors
        try:
            from pruefung_workflow import PruefungWorkflow
            print("Successfully imported PruefungWorkflow")
        except Exception as e:
            print(f"Error importing PruefungWorkflow: {e}")
            traceback.print_exc()
            return
        
        # Create a function to simulate going back to the welcome screen
        def back_callback():
            print("Back button clicked")
        
        # Initialize the workflow with test data
        test_project_data = {
            "auftrag": "Test Project",
            "kunde": "Test Customer",
            "files": [None, None],
            "selected_checks": []
        }
        
        try:
            # Create the workflow instance
            workflow = PruefungWorkflow(
                root=content_frame,
                back_callback=back_callback,
                project_data=test_project_data
            )
            print("Successfully created PruefungWorkflow instance")
        except Exception as e:
            print(f"Error creating PruefungWorkflow instance: {e}")
            traceback.print_exc()
            return
        
        try:
            # Show the workflow
            workflow.show_workflow()
            print("Successfully showed workflow")
        except Exception as e:
            print(f"Error showing workflow: {e}")
            traceback.print_exc()
            return
        
        # Add debug buttons
        def test_buttons():
            print("Testing buttons...")
            try:
                if hasattr(workflow, 'ensure_bottom_bar_visible'):
                    workflow.ensure_bottom_bar_visible()
                    print("ensure_bottom_bar_visible executed successfully")
                else:
                    print("ERROR: ensure_bottom_bar_visible method not found")
            except Exception as e:
                print(f"Error in ensure_bottom_bar_visible: {e}")
                traceback.print_exc()
        
        debug_btn = ctk.CTkButton(root, text="Debug Buttons", command=test_buttons)
        debug_btn.pack(pady=5)
        
        # Start the main loop
        root.mainloop()
    except Exception as e:
        print(f"Critical error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
