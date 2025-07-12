"""
Test script to directly run the fixed PruefungWorkflow
This test verifies that the bottom bar with Start and Export buttons remains visible.
"""
import customtkinter as ctk
import tkinter as tk
from pruefung_workflow import PruefungWorkflow  # Using the working version
import time
import threading

class TestWindow:
    def __init__(self):
        # Set up the root window
        self.root = ctk.CTk()
        self.root.title("PruefungWorkflow Test")
        self.root.geometry("1200x800")
        
        # Set up a frame to contain the workflow
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize the workflow with test data
        self.test_project_data = {
            "auftrag": "Test Project",
            "kunde": "Test Customer",
            "files": [None, None],
            "selected_checks": []
        }
        
        # Create the workflow instance
        self.workflow = PruefungWorkflow(
            root=self.content_frame,
            back_callback=self.back_callback,
            project_data=self.test_project_data
        )
        
        # Add a test button to simulate different UI scenarios
        self.test_btn = ctk.CTkButton(
            self.root, 
            text="Test UI Layers", 
            command=self.test_ui_layers
        )
        self.test_btn.pack(pady=5)
        
        # Show the workflow
        self.workflow.show_workflow()
        
        # Start a verification thread to periodically check if buttons are visible
        self.verification_thread = threading.Thread(target=self.verify_buttons, daemon=True)
        self.verification_thread.start()
    
    def back_callback(self):
        print("Back button clicked")
    
    def test_ui_layers(self):
        """Creates various UI elements to test if they interfere with the bottom bar visibility"""
        print("Testing UI layers and z-order")
        
        # Create a test panel that might interfere with the bottom bar
        test_panel = ctk.CTkFrame(self.content_frame, fg_color="#ffdddd")
        test_panel.place(relx=0.5, rely=0.9, relwidth=0.9, relheight=0.2, anchor="center")
        
        # Add a label to the test panel
        ctk.CTkLabel(test_panel, text="This is a test panel that could interfere with the bottom bar").pack(pady=20)
        
        # Schedule removal of the test panel after 3 seconds
        self.root.after(3000, test_panel.destroy)
        
        # Call ensure_bottom_bar_visible to make sure our fix works
        self.workflow.ensure_bottom_bar_visible()
    
    def verify_buttons(self):
        """Verification function running in a separate thread to check button visibility"""
        while True:
            time.sleep(2)  # Check every 2 seconds
            
            # Use after() to safely access UI from the main thread
            self.root.after(0, self.check_button_visibility)
    
    def check_button_visibility(self):
        """Checks if the Start and Export buttons are visible and accessible"""
        if not hasattr(self.workflow, 'start_button') or not self.workflow.start_button:
            print("WARNING: Start button not found!")
            return
            
        if not hasattr(self.workflow, 'export_button') or not self.workflow.export_button:
            print("WARNING: Export button not found!")
            return
            
        # Check if buttons are packed and visible
        try:
            start_info = self.workflow.start_button.pack_info()
            export_info = self.workflow.export_button.pack_info()
            print(f"Button visibility check: Start button is packed with {start_info.get('side')} side")
            print(f"Button visibility check: Export button is packed with {export_info.get('side')} side")
        except Exception as e:
            print(f"WARNING: Buttons may not be properly packed: {e}")
            # Try to fix the issue by calling ensure_bottom_bar_visible
            if hasattr(self.workflow, 'ensure_bottom_bar_visible'):
                print("Attempting to restore button visibility...")
                self.workflow.ensure_bottom_bar_visible()

def main():
    app = TestWindow()
    app.root.mainloop()

if __name__ == "__main__":
    main()
