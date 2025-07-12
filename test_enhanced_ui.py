"""
Enhanced UI Test Application
===========================
Test application to showcase the improved typography and layout.
"""

import customtkinter as ctk
import tkinter as tk
from enhanced_welcome_screen import EnhancedWelcomeScreen
from enhanced_typography import ui_helper

class TestApp:
    """Test application for the enhanced UI components."""
    
    def __init__(self):
        """Initialize the test application."""
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Enhanced UI Test - Checker Pro Suite")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create enhanced welcome screen
        self.welcome_screen = EnhancedWelcomeScreen(self.root, self)
        self.welcome_screen.grid(row=0, column=0, sticky="nsew")
        
        # Mock app properties
        self.workflow_routes = {
            'angebots_workflow': {
                'name': 'Angebotsanalyse',
                'icon': '💰',
                'description': 'Erstelle professionelle Angebote',
                'callback': self._mock_workflow
            },
            'pruefung_workflow': {
                'name': 'Dateiprüfung',
                'icon': '✅',
                'description': 'Prüfe Übersetzungen auf Qualität',
                'callback': self._mock_workflow
            },
            'finalisierung_workflow': {
                'name': 'Finalisierung',
                'icon': '🏁',
                'description': 'Finalisiere Projekte',
                'callback': self._mock_workflow
            },
            'projekt_workflow': {
                'name': 'Projektübersicht',
                'icon': '📊',
                'description': 'Verwalte deine Projekte',
                'callback': self._mock_workflow
            }
        }
    
    def _mock_workflow(self):
        """Mock workflow callback."""
        print("Workflow started!")
    
    def run(self):
        """Run the test application."""
        print("🎨 Enhanced UI Test Application")
        print("=" * 40)
        print("Testing improved typography and layout...")
        print("Close the window to exit.")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()
