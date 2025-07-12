"""
Debug version to find Welcome Screen visibility issue
"""
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
import logging
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("DEBUG")

class DebugApp:
    def __init__(self):
        print("[DEBUG] Creating debug app...")
        
        # Create root window
        self.root = TkinterDnD.Tk()
        self.root.title("DEBUG - Welcome Screen Test")
        self.root.geometry("1000x700")
        
        # Apply CustomTkinter theming
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        print("[DEBUG] Root window created")
        
        # Create Welcome Screen
        try:
            print("[DEBUG] Creating Welcome Screen...")
            self.welcome_screen = UltraModernWelcomeScreen(
                master=self.root,
                app=self
            )
            print("[DEBUG] Welcome Screen created successfully")
            
            # Pack the welcome screen
            print("[DEBUG] Packing Welcome Screen...")
            self.welcome_screen.pack(fill="both", expand=True)
            print("[DEBUG] Welcome Screen packed")
            
            # Check if it's visible
            self.root.after(1000, self.check_visibility)
            
        except Exception as e:
            print(f"[DEBUG] Error creating Welcome Screen: {e}")
            import traceback
            traceback.print_exc()
    
    def check_visibility(self):
        """Check if welcome screen is actually visible"""
        try:
            if hasattr(self, 'welcome_screen'):
                print(f"[DEBUG] Welcome screen exists: {self.welcome_screen}")
                print(f"[DEBUG] Welcome screen winfo_ismapped: {self.welcome_screen.winfo_ismapped()}")
                print(f"[DEBUG] Welcome screen winfo_viewable: {self.welcome_screen.winfo_viewable()}")
                print(f"[DEBUG] Welcome screen winfo_width: {self.welcome_screen.winfo_width()}")
                print(f"[DEBUG] Welcome screen winfo_height: {self.welcome_screen.winfo_height()}")
                
                # Check children
                children = self.root.winfo_children()
                print(f"[DEBUG] Root has {len(children)} children:")
                for i, child in enumerate(children):
                    print(f"[DEBUG]   Child {i}: {child} - mapped: {child.winfo_ismapped()}")
            else:
                print("[DEBUG] Welcome screen does not exist!")
                
        except Exception as e:
            print(f"[DEBUG] Error checking visibility: {e}")
    
    def workflow_routes(self):
        """Dummy workflow routes for Welcome Screen"""
        return {}
    
    def get_icon(self, icon_name, size=(24, 24)):
        """Dummy icon method"""
        return None
    
    def on_closing(self):
        """Dummy on_closing method"""
        self.root.destroy()
    
    def run(self):
        print("[DEBUG] Starting main loop...")
        self.root.mainloop()

if __name__ == "__main__":
    app = DebugApp()
    app.run()
