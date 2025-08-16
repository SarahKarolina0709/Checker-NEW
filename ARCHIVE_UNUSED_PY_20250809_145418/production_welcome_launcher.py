#!/usr/bin/env python3
"""
Production Welcome Screen Launcher (aligned to consolidated WelcomeScreen)
"""

import sys
import traceback
import customtkinter as ctk

# Enforce light mode (No Dark Mode policy)
ctk.set_appearance_mode("light")

def main():
    print("CHECKER PRO - Production Welcome Screen")
    print("=" * 60)

    try:
        # Import the consolidated welcome screen
        from welcome_screen import WelcomeScreen
    except Exception as e:
        print(f"Import error: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Create root window
    root = ctk.CTk()
    root.title("CHECKER PRO - Welcome")
    root.geometry("1400x900")
    root.minsize(1200, 700)
    root.configure(fg_color="#F1F5F9")  # Light background only

    # Responsive grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Minimal app adapter for WelcomeScreen callbacks/state
    class ProductionApp:
        def __init__(self):
            self.root = root
            self.current_state = {}

        def show_main_interface(self, workflow_type="default"):
            try:
                import os, py_compile, subprocess
                script_path = os.path.join(os.path.dirname(__file__), "modern_translation_quality_gui.py")
                modular_path = os.path.join(os.path.dirname(__file__), "modern_translation_quality_gui_modular.py")

                root.withdraw()

                try:
                    if os.path.exists(script_path):
                        py_compile.compile(script_path, doraise=True)
                        subprocess.Popen(["python", script_path], cwd=os.path.dirname(__file__))
                    elif os.path.exists(modular_path):
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                    else:
                        raise FileNotFoundError("No main GUI file found")
                except Exception:
                    if os.path.exists(modular_path):
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                    else:
                        raise
            except Exception as e:
                print(f"Navigation error: {e}")
                traceback.print_exc()
                root.deiconify()

        def set_current_customer(self, customer):
            self.current_state['customer'] = customer

        def add_files(self, files):
            self.current_state.setdefault('files', []).extend(files)

    app = ProductionApp()

    # Create and show welcome screen
    welcome_screen = WelcomeScreen(root, app)
    welcome_screen.grid(row=0, column=0, sticky="nsew")

    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (1400 // 2)
    y = (screen_height // 2) - (900 // 2)
    root.geometry(f"1400x900+{x}+{y}")

    print("Production Welcome Screen ready")
    root.mainloop()

if __name__ == "__main__":
    main()
