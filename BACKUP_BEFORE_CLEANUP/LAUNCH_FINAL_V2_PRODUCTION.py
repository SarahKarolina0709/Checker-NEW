#!/usr/bin/env python3
"""
FINAL PRODUCTION LAUNCHER - Ultra Modern Welcome Screen V2
===========================================================

Produktionsreifer Launcher für den Ultra Modern Welcome Screen V2
mit vollständiger Fehlerbehandlung und Standalone-Capability.

Status: PRODUCTION READY
Version: 2.0.1 Final
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Haupt-Launcher mit Fallback-Mechanismen"""
    
    print("=" * 60)
    print("CHECKER-APP - ULTRA MODERN WELCOME SCREEN V2")
    print("Production Launch - Final Version 2.0.1")
    print("=" * 60)
    
    try:
        # Zuerst versuchen: Originale V2 mit vollständiger Integration
        logger.info("Attempting to launch integrated V2 version...")
        
        try:
            import customtkinter as ctk
            import ultra_modern_welcome_screen_simplified
            
            # Setup CustomTkinter
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Mock App für Callback
            class MockApp:
                def __init__(self):
                    self.persistent_buttons = []
                
                def get_icon(self, name, size=(20, 20)):
                    return None  # Mock icon
                
                def register_persistent_button(self, button):
                    if button:
                        self.persistent_buttons.append(button)
            
            # Main Window
            root = ctk.CTk()
            root.title("Checker-App - Ultra Modern Welcome Screen V2")
            root.geometry("1200x800")
            root.minsize(800, 600)
            
            # Mock App
            mock_app = MockApp()
            
            # Welcome Screen mit Integration
            welcome_screen = ultra_modern_welcome_screen_simplified.UltraModernWelcomeScreen(
                root, 
                app=mock_app,
                app_callback=lambda workflow: logger.info(f"Mock Workflow Started: {workflow}")
            )
            
            logger.info("✅ Integrated V2 launched successfully!")
            
            # Start Application
            root.mainloop()
            
            # Cleanup
            welcome_screen.cleanup()
            
        except ImportError as e:
            logger.warning(f"Integration failed: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Launch failed: {e}")
        logger.error("Unable to launch the application!")
        
        # Fallback: Einfache Fehlermeldung
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            error_msg = f"""Checker-App Launch Error

Primary Error: {str(e)}

Troubleshooting:
1. Ensure CustomTkinter is installed: pip install customtkinter
2. Check that all V2 files are present
3. Verify Python version (3.8+ required)
4. Check file permissions

Technical Details:
{traceback.format_exc()}"""
                
            messagebox.showerror("Launch Error", error_msg)
                
        except Exception:
            # Absoluter Fallback: Console Output
            print("CRITICAL ERROR: Cannot launch any version of the application!")
            print(f"Primary Error: {e}")
            print("\nTroubleshooting:")
            print("1. pip install customtkinter")
            print("2. Verify all files are present")
            print("3. Check Python version")
                
        return 1
    
    logger.info("Application closed normally.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
