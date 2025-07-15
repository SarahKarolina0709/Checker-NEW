# -*- coding: utf-8 -*-
import customtkinter as ctk
from typing import Dict, Optional, Any

# Internal imports
from pruefung_workflow_controller import PruefungWorkflowController
from ui_components.pruefung_workflow_view import PruefungWorkflowView
from ui_theme import UITheme

class PruefungWorkflow(ctk.CTkFrame):
    """
    Container frame for the 'Prüfung' (Checking) workflow.

    This class integrates the controller (logic) and the view (UI) for the
    checking process. It serves as the main entry point for this workflow
    when called from the main application.
    """
    def __init__(self, parent: ctk.CTkFrame, app: Any, project_data: Dict[str, Any]) -> None:
        """
        Initializes the PruefungWorkflow.

        Args:
            parent: The parent widget.
            app: The main application instance.
            project_data (Dict): Data related to the current project.
        """
        super().__init__(parent, fg_color=UITheme.TUPLE_BG)
        self.app = app
        self.project_data = project_data

        # Configure grid layout for this workflow frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # The controller manages the logic, and the view manages the UI.
        self.controller = PruefungWorkflowController(app=self.app, project_data=self.project_data)
        self.view = PruefungWorkflowView(
            root=self,
            app=self.app,
            controller=self.controller,
            project_data=self.project_data
        )

        self.controller.set_view(self.view)
        
        # The view is placed using grid to fill the entire container
        self.view.grid(row=0, column=0, sticky="nsew")
        
        self.update_idletasks()

    def update_theme(self) -> None:
        """Updates the theme for the workflow and its view."""
        # The container itself has a theme-aware background color.
        # We just need to propagate the theme update to the main view.
        if hasattr(self, 'view') and self.view and hasattr(self.view, 'update_theme'):
            self.view.update_theme()

    def show_workflow(self, project_data: Optional[Dict[str, Any]] = None) -> None:
        """Shows the workflow frame and updates with new data."""
        self.project_data = project_data or {}
        # Pass the new data down to the controller/view if needed
        self.controller.update_project_data(self.project_data)
        self.view.update_project_data(self.project_data)
        self.pack(fill="both", expand=True)

    def cleanup(self) -> None:
        """Prepares the workflow for being hidden or destroyed."""
        self.pack_forget()

    def destroy(self) -> None:
        """Overrides the default destroy method to ensure proper cleanup."""
        if hasattr(self, 'view') and self.view and self.view.winfo_exists():
            self.view.destroy()
        super().destroy()

if __name__ == "__main__":
    # This block allows the workflow to be run standalone for testing
    import os
    
    # Create a mock app object that the workflow expects
    # In a real scenario, the IconManager would be part of the app
    from icon_manager import IconManager
    class MockApp:
        def __init__(self, root_window):
            self.root = root_window
            self.icon_manager = IconManager(os.path.join(os.path.dirname(__file__), 'assets'))
            self.persistent_buttons = []

        def register_persistent_button(self, button):
            # Mock implementation
            if hasattr(button, "cget") and button.cget("image"):
                button.image = button.cget("image") # Keep a reference
                self.persistent_buttons.append(button)

    # --- Main Execution ---
    root = ctk.CTk()
    root.geometry("1400x900")
    root.title("Pruefung Workflow - Standalone Test")
    
    # Set a consistent theme for testing
    ctk.set_appearance_mode(UITheme.APPEARANCE_MODE)
    ctk.set_default_color_theme(UITheme.COLOR_THEME)
    root.configure(fg_color=UITheme.COLOR_BACKGROUND)

    # Create the mock app and dummy project data
    mock_app_instance = MockApp(root)
    dummy_project_data = {
        "kunde_name": "Testkunde",
        "projekt_id": "2025-07-06_Test_Projekt_123",
        "dateipfade": []
    }

    # Create and display the workflow
    workflow_frame = PruefungWorkflow(
        parent=root, 
        app=mock_app_instance, 
        project_data=dummy_project_data
    )
    workflow_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()