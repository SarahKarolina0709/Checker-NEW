"""
Simple test to verify our PruefungWorkflow implementation works correctly.
This script will create a simple window with a button that opens the workflow.
"""
import tkinter as tk
import customtkinter as ctk
from pruefung_workflow import PruefungWorkflow

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PruefungWorkflow Test")
        self.root.geometry("400x300")
        
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.button = ctk.CTkButton(
            self.content_frame, 
            text="Open PruefungWorkflow", 
            command=self.open_workflow
        )
        self.button.pack(pady=50)
        
        self.workflow = None
        
    def open_workflow(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show the workflow
        if self.workflow is None:
            self.workflow = PruefungWorkflow(
                root=self.content_frame,
                back_callback=self.back_to_main,
                project_data={"files": [None, None], "selected_checks": ["Grammatikprüfung"]}
            )
        
        self.workflow.show_workflow()
        
    def back_to_main(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show main button again
        self.button = ctk.CTkButton(
            self.content_frame, 
            text="Open PruefungWorkflow Again", 
            command=self.open_workflow
        )
        self.button.pack(pady=50)

def main():
    # Create the root window
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
