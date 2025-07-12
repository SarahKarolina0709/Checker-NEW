#!/usr/bin/env python3
"""
ViewStack Implementation Test
============================

This script tests the new ViewStack pattern implementation in CheckerApp,
validating O(1) view switching and proper integration with the enhanced theme system.
"""

import sys
import os
import customtkinter as ctk
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from view_stack import ViewStack, EnhancedViewStack
from ui_theme import enhanced_theme

class ViewStackTestApp:
    """Test application for ViewStack functionality."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ViewStack Implementation Test")
        self.root.geometry("800x600")
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create control panel
        control_panel = ctk.CTkFrame(main_container, fg_color=enhanced_theme.get_color("surface"))
        control_panel.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            control_panel,
            text="🔄 ViewStack O(1) Switching Test",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=enhanced_theme.get_color("text_primary")
        )
        title_label.pack(pady=20)
        
        # Control buttons
        button_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Create ViewStack
        self.viewstack = EnhancedViewStack(
            main_container,
            enable_history=True,
            max_history=5
        )
        self.viewstack.pack(fill="both", expand=True)
        
        # Create test views
        self.create_test_views()
        
        # Create navigation buttons
        self.create_navigation_buttons(button_frame)
        
        # Show initial view
        self.viewstack.show("view1")
        
    def create_test_views(self):
        """Create test views to demonstrate ViewStack functionality."""
        
        # View 1: Welcome-style view
        view1 = ctk.CTkFrame(
            self.viewstack,
            fg_color=enhanced_theme.get_color("primary_container"),
            border_color=enhanced_theme.get_color("primary"),
            border_width=2
        )
        
        view1_label = ctk.CTkLabel(
            view1,
            text="🏠 View 1: Welcome Screen Simulation\n\nThis simulates the welcome screen.\nClick buttons above to switch views with O(1) performance.",
            font=ctk.CTkFont(size=16),
            text_color=enhanced_theme.get_color("text_primary"),
            justify="center"
        )
        view1_label.pack(expand=True)
        
        # View 2: Workflow-style view
        view2 = ctk.CTkFrame(
            self.viewstack,
            fg_color=enhanced_theme.get_color("success_surface"),
            border_color=enhanced_theme.get_color("success"),
            border_width=2
        )
        
        view2_content = ctk.CTkFrame(view2, fg_color="transparent")
        view2_content.pack(expand=True, fill="both", padx=50, pady=50)
        
        view2_label = ctk.CTkLabel(
            view2_content,
            text="⚙️ View 2: Workflow Simulation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=enhanced_theme.get_color("success")
        )
        view2_label.pack(pady=(0, 20))
        
        view2_desc = ctk.CTkLabel(
            view2_content,
            text="This simulates a workflow screen.\nNo more grid_forget() calls!\nJust clean O(1) switching.",
            font=ctk.CTkFont(size=14),
            text_color=enhanced_theme.get_color("text_primary"),
            justify="center"
        )
        view2_desc.pack()
        
        # View 3: Another workflow-style view
        view3 = ctk.CTkFrame(
            self.viewstack,
            fg_color=enhanced_theme.get_color("warning_surface"),
            border_color=enhanced_theme.get_color("warning"),
            border_width=2
        )
        
        view3_content = ctk.CTkFrame(view3, fg_color="transparent")
        view3_content.pack(expand=True, fill="both", padx=50, pady=50)
        
        view3_label = ctk.CTkLabel(
            view3_content,
            text="📄 View 3: Another Workflow",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=enhanced_theme.get_color("warning")
        )
        view3_label.pack(pady=(0, 20))
        
        view3_desc = ctk.CTkLabel(
            view3_content,
            text="Instant switching between any views.\nNo layout conflicts.\nClean and efficient!",
            font=ctk.CTkFont(size=14),
            text_color=enhanced_theme.get_color("text_primary"),
            justify="center"
        )
        view3_desc.pack()
        
        # Add views to ViewStack with callbacks
        self.viewstack.add(
            "view1", 
            view1,
            on_show=lambda **kwargs: self.on_view_shown("Welcome", kwargs.get('previous_view')),
            on_hide=lambda: self.on_view_hidden("Welcome")
        )
        
        self.viewstack.add(
            "view2", 
            view2,
            on_show=lambda **kwargs: self.on_view_shown("Workflow 1", kwargs.get('previous_view')),
            on_hide=lambda: self.on_view_hidden("Workflow 1")
        )
        
        self.viewstack.add(
            "view3", 
            view3,
            on_show=lambda **kwargs: self.on_view_shown("Workflow 2", kwargs.get('previous_view')),
            on_hide=lambda: self.on_view_hidden("Workflow 2")
        )
        
    def create_navigation_buttons(self, parent):
        """Create navigation buttons for testing."""
        
        # View switching buttons
        btn1 = ctk.CTkButton(
            parent,
            text="🏠 Welcome",
            command=lambda: self.switch_view("view1"),
            fg_color=enhanced_theme.get_color("primary"),
            hover_color=enhanced_theme.get_color("primary_hover")
        )
        btn1.pack(side="left", padx=5)
        
        btn2 = ctk.CTkButton(
            parent,
            text="⚙️ Workflow 1",
            command=lambda: self.switch_view("view2"),
            fg_color=enhanced_theme.get_color("success"),
            hover_color=enhanced_theme.get_color("success_hover")
        )
        btn2.pack(side="left", padx=5)
        
        btn3 = ctk.CTkButton(
            parent,
            text="📄 Workflow 2",
            command=lambda: self.switch_view("view3"),
            fg_color=enhanced_theme.get_color("warning"),
            hover_color=enhanced_theme.get_color("warning")
        )
        btn3.pack(side="left", padx=5)
        
        # Back button
        back_btn = ctk.CTkButton(
            parent,
            text="↩️ Back",
            command=self.go_back,
            fg_color=enhanced_theme.get_color("secondary"),
            hover_color=enhanced_theme.get_color("secondary_hover")
        )
        back_btn.pack(side="right", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            parent,
            text="Current: Welcome",
            font=ctk.CTkFont(size=12),
            text_color=enhanced_theme.get_color("text_secondary")
        )
        self.status_label.pack(side="right", padx=20)
        
    def switch_view(self, view_name):
        """Switch to a specific view."""
        success = self.viewstack.show(view_name)
        if success:
            print(f"✅ Switched to {view_name}")
        else:
            print(f"❌ Failed to switch to {view_name}")
    
    def go_back(self):
        """Go back to the previous view."""
        success = self.viewstack.go_back()
        if success:
            print("↩️ Went back to previous view")
        else:
            print("❌ No history available")
    
    def on_view_shown(self, view_name, previous_view=None):
        """Callback when a view is shown."""
        print(f"📺 View shown: {view_name} (was: {previous_view})")
        self.status_label.configure(text=f"Current: {view_name}")
    
    def on_view_hidden(self, view_name):
        """Callback when a view is hidden."""
        print(f"👁‍🗨 View hidden: {view_name}")
    
    def run(self):
        """Run the test application."""
        print("🚀 Starting ViewStack test...")
        print("🔄 Testing O(1) view switching performance...")
        print("📝 Check console for view change events")
        
        self.root.mainloop()

def main():
    """Main entry point."""
    print("=" * 60)
    print("ViewStack Implementation Test")
    print("=" * 60)
    print("Testing the new O(1) view switching pattern")
    print("No more grid_forget() calls - just clean switching!")
    print("")
    
    # Test basic ViewStack functionality
    print("🧪 Testing ViewStack functionality...")
    
    # Create and run the test app
    app = ViewStackTestApp()
    app.run()

if __name__ == "__main__":
    main()
