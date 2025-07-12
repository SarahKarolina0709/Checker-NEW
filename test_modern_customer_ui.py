#!/usr/bin/env python3
"""
Direct test for modern customer management UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import necessary modules
import customtkinter as ctk
from ui_modernization_update import ModernUIUpdater
from kunden_manager import KundenManager

class TestApp:
    def __init__(self):
        # Initialize basic app structure similar to CheckerApp
        self.root = ctk.CTk()
        self.root.title("Test - Modern Customer Management")
        self.root.geometry("1280x800")
        
        # Set light mode
        ctk.set_appearance_mode("Light")
        
        # Initialize managers
        self.kunden_manager = KundenManager()
        
        # Create ViewStack-like container
        self.views = ctk.CTkFrame(self.root, fg_color="transparent")
        self.views.pack(fill="both", expand=True)
        self.views.grid_columnconfigure(0, weight=1)
        self.views.grid_rowconfigure(0, weight=1)
        
        # Simple ViewStack implementation
        self.current_view = None
        self.view_widgets = {}
        
        # Initialize UI modernizer
        self.ui_modernizer = ModernUIUpdater(self)
        
        # Create main UI
        self.create_test_ui()
        
    def add_view(self, name, widget):
        """Simple add view implementation."""
        self.view_widgets[name] = widget
        
    def show_view(self, name):
        """Simple show view implementation."""
        if self.current_view:
            self.current_view.grid_forget()
        
        if name in self.view_widgets:
            self.current_view = self.view_widgets[name]
            self.current_view.grid(row=0, column=0, sticky="nsew")
            
    def create_test_ui(self):
        """Create test UI with button to trigger modern customer management."""
        # Main container
        main_frame = ctk.CTkFrame(self.views, fg_color="#F8F9FA")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Test: Moderne Kundenmanagement-Oberfläche",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1F2937"
        )
        header.grid(row=0, column=0, pady=20)
        
        # Test button
        test_btn = ctk.CTkButton(
            main_frame,
            text="🚀 Moderne Kundenmanagement-UI testen",
            command=self.test_modern_customer_management,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        test_btn.grid(row=1, column=0, pady=20)
        
        self.add_view('main', main_frame)
        self.show_view('main')
        
    def test_modern_customer_management(self):
        """Test the modern customer management interface."""
        try:
            print("Testing modern customer management UI...")
            
            # Create a container for the modern UI
            modern_frame = ctk.CTkFrame(self.views, fg_color="transparent")
            modern_frame.grid_columnconfigure(0, weight=1)
            modern_frame.grid_rowconfigure(1, weight=1)
            
            # Apply modern customer management UI
            self.ui_modernizer.apply_modern_customer_management(modern_frame)
            
            # Add and show the view
            self.add_view('modern_customer_management', modern_frame)
            self.show_view('modern_customer_management')
            
            print("✅ Modern customer management UI successfully loaded!")
            
        except Exception as e:
            print(f"❌ Error testing modern customer management: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the test application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()
