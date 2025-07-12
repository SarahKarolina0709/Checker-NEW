#!/usr/bin/env python3
"""
Test-Skript für die Checker-App um Probleme zu identifizieren
"""
import os
import sys
import traceback

def test_imports():
    """Teste alle kritischen Imports"""
    print("=== Testing Imports ===")
    
    try:
        import customtkinter as ctk
        print("✅ CustomTkinter import successful")
    except Exception as e:
        print(f"❌ CustomTkinter import failed: {e}")
        return False
    
    try:
        from ui_theme import UITheme
        print("✅ UITheme import successful")
    except Exception as e:
        print(f"❌ UITheme import failed: {e}")
        return False
    
    try:
        from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
        print("✅ UltraModernWelcomeScreen import successful")
    except Exception as e:
        print(f"❌ UltraModernWelcomeScreen import failed: {e}")
        return False
    
    try:
        from fluent_icons_manager import FluentIconManager
        print("✅ FluentIconManager import successful")
    except Exception as e:
        print(f"❌ FluentIconManager import failed: {e}")
        return False
    
    return True

def test_minimal_app():
    """Teste eine minimale App-Erstellung"""
    print("\n=== Testing Minimal App ===")
    
    try:
        import customtkinter as ctk
        from ui_theme import UITheme
        
        # Disable DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        
        # Create minimal root
        root = ctk.CTk()
        root.title("Test App")
        root.geometry("800x600")
        
        # Apply theme
        ctk.set_appearance_mode(UITheme.APPEARANCE_MODE)
        ctk.set_default_color_theme(UITheme.COLOR_THEME)
        
        # Create simple frame
        frame = ctk.CTkFrame(root)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create simple label
        label = ctk.CTkLabel(frame, text="Test App läuft erfolgreich!", font=ctk.CTkFont(size=18))
        label.pack(pady=50)
        
        # Create simple button
        button = ctk.CTkButton(frame, text="Schließen", command=root.destroy)
        button.pack(pady=20)
        
        print("✅ Minimal app created successfully")
        
        # Show and run for 3 seconds
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✅ Minimal app ran successfully")
        return True
        
    except Exception as e:
        print(f"❌ Minimal app failed: {e}")
        traceback.print_exc()
        return False

def test_welcome_screen():
    """Teste die Welcome Screen-Erstellung"""
    print("\n=== Testing Welcome Screen ===")
    
    try:
        import customtkinter as ctk
        from ui_theme import UITheme
        from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
        
        # Create mock app class
        class MockApp:
            def __init__(self):
                self.icon_manager = None
            
            def get_icon(self, name, size=(20, 20)):
                return None
            
            def handle_workflow_start(self, workflow_type, customer_data):
                print(f"Mock workflow start: {workflow_type}")
        
        # Create root
        root = ctk.CTk()
        root.title("Welcome Screen Test")
        root.geometry("1200x800")
        
        # Create mock app
        mock_app = MockApp()
        
        # Create welcome screen
        welcome_screen = UltraModernWelcomeScreen(
            master=root,
            app=mock_app,
            app_callback=mock_app.handle_workflow_start
        )
        welcome_screen.pack(fill="both", expand=True)
        
        print("✅ Welcome screen created successfully")
        
        # Show for 3 seconds
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✅ Welcome screen ran successfully")
        return True
        
    except Exception as e:
        print(f"❌ Welcome screen failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Checker-App diagnostics...")
    
    success = True
    success &= test_imports()
    success &= test_minimal_app()
    success &= test_welcome_screen()
    
    if success:
        print("\n🎉 All tests passed! The app should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    input("\nPress Enter to continue...")
