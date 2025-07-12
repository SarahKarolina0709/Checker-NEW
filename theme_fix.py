"""
Ultimate Background Color Fix for CheckerApp

This script ensures all UI components use the correct background color.
"""

import customtkinter as ctk

def force_light_background():
    """Force all CTk components to use light gray background."""
    
    # Light gray background color
    light_gray = "#F5F5F5"
    
    # Override CTk default colors
    ctk.ThemeManager.theme["CTk"]["fg_color"] = [light_gray, light_gray]
    ctk.ThemeManager.theme["CTkToplevel"]["fg_color"] = [light_gray, light_gray]
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [light_gray, light_gray]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["fg_color"] = [light_gray, light_gray]
    
    # Set appearance mode to light
    ctk.set_appearance_mode("Light")
    
    print(f"[THEME_FIX] Applied light gray background color override: {light_gray}")

if __name__ == "__main__":
    force_light_background()
