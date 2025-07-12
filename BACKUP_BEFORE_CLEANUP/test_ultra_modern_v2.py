"""
Test-Script für das neue Ultra-Modern Welcome Screen v2.0 Design
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_ultra_robust_scaling_tracker_patch():
    """Wendet den robusten ScalingTracker Patch an"""
    import tkinter as tk
    
    def dummy_block_update_dimensions_event(self):
        pass
    
    def dummy_unblock_update_dimensions_event(self):
        pass
    
    if not hasattr(tk.Tk, 'block_update_dimensions_event'):
        tk.Tk.block_update_dimensions_event = dummy_block_update_dimensions_event
    if not hasattr(tk.Tk, 'unblock_update_dimensions_event'):
        tk.Tk.unblock_update_dimensions_event = dummy_unblock_update_dimensions_event
    
    if not hasattr(tk.Toplevel, 'block_update_dimensions_event'):
        tk.Toplevel.block_update_dimensions_event = dummy_block_update_dimensions_event
    if not hasattr(tk.Toplevel, 'unblock_update_dimensions_event'):
        tk.Toplevel.unblock_update_dimensions_event = dummy_unblock_update_dimensions_event
    
    print("[PATCH] Tkinter classes patched successfully")

# Apply patch before imports
apply_ultra_robust_scaling_tracker_patch()

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

class MockCheckerApp:
    """Mock der Checker-App für Testing"""
    
    def __init__(self):
        # Setup basic properties
        self.root = ctk.CTk()
        self.root.title("Checker-App - Ultra-Modern Welcome Screen v2.0 Test")
        self.root.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Mock icon system
        self.icon_cache = {}
        self.persistent_buttons = []
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        # Initialize welcome screen
        self.welcome_screen = None
        
        print("[MOCK] MockCheckerApp initialized")

    def get_icon(self, icon_name, size=(24, 24), fallback_text="📄"):
        """
        Mock icon loading method
        Simuliert das Icon-System der echten App
        """
        try:
            # Simulate icon loading with a simple colored rectangle
            from PIL import Image, ImageDraw
            
            # Create a simple colored icon
            img = Image.new('RGBA', size, (59, 130, 246, 255))  # Blue color
            draw = ImageDraw.Draw(img)
            
            # Draw a simple shape based on icon name
            if 'rocket' in icon_name.lower():
                # Draw triangle for rocket
                draw.polygon([(size[0]//4, size[1]*3//4), (size[0]//2, size[1]//4), (size[0]*3//4, size[1]*3//4)], fill=(255, 255, 255, 255))
            elif 'person' in icon_name.lower() or 'customer' in icon_name.lower():
                # Draw circle for person
                draw.ellipse([size[0]//4, size[1]//4, size[0]*3//4, size[1]*3//4], fill=(255, 255, 255, 255))
            elif 'settings' in icon_name.lower():
                # Draw gear-like shape
                center = (size[0]//2, size[1]//2)
                radius = min(size) // 4
                draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], fill=(255, 255, 255, 255))
            elif 'folder' in icon_name.lower():
                # Draw folder shape
                draw.rectangle([size[0]//6, size[1]//3, size[0]*5//6, size[1]*5//6], fill=(255, 255, 255, 255))
            elif 'file' in icon_name.lower():
                # Draw document shape
                draw.rectangle([size[0]//3, size[1]//6, size[0]*2//3, size[1]*5//6], fill=(255, 255, 255, 255))
            elif 'add' in icon_name.lower() or 'plus' in icon_name.lower():
                # Draw plus sign
                center = (size[0]//2, size[1]//2)
                thickness = 3
                draw.rectangle([center[0]-thickness//2, size[1]//4, center[0]+thickness//2, size[1]*3//4], fill=(255, 255, 255, 255))
                draw.rectangle([size[0]//4, center[1]-thickness//2, size[0]*3//4, center[1]+thickness//2], fill=(255, 255, 255, 255))
            else:
                # Default: simple square
                draw.rectangle([size[0]//4, size[1]//4, size[0]*3//4, size[1]*3//4], fill=(255, 255, 255, 255))
            
            # Convert to CTkImage
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            
            # Cache the icon
            cache_key = f"{icon_name}_{size[0]}x{size[1]}"
            self.icon_cache[cache_key] = ctk_image
            
            print(f"[MOCK] Generated icon: {icon_name} ({size[0]}x{size[1]})")
            return ctk_image
            
        except Exception as e:
            print(f"[MOCK] Error generating icon {icon_name}: {e}")
            return None

    def register_persistent_button(self, button):
        """Registriert einen Button für persistente Referenzen"""
        self.persistent_buttons.append(button)
        print(f"[MOCK] Registered persistent button: {button}")

    def start_workflow(self, workflow_type):
        """Mock workflow starter"""
        print(f"[MOCK] Starting workflow: {workflow_type}")
        
        # Show a simple confirmation
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "Workflow gestartet", 
                f"Workflow '{workflow_type}' würde jetzt gestartet werden.\n\nDies ist nur ein Test des Welcome Screens."
            )
        except Exception as e:
            print(f"[MOCK] Error showing workflow confirmation: {e}")

    def run(self):
        """Startet die Test-App"""
        try:
            # Create welcome screen
            self.welcome_screen = UltraModernWelcomeScreen(
                root_for_ui=self.content_frame,
                app=self,
                app_callback=self.start_workflow
            )
            
            # Show welcome screen
            self.welcome_screen.show()
            
            print("[MOCK] Welcome screen displayed")
            
            # Start the main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"[MOCK] Error running test app: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Hauptfunktion für den Test"""
    print("=" * 60)
    print("Ultra-Modern Welcome Screen v2.0 Test")
    print("=" * 60)
    
    try:
        # Create and run test app
        app = MockCheckerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n[TEST] Test abgebrochen durch Benutzer")
    except Exception as e:
        print(f"[TEST] Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
