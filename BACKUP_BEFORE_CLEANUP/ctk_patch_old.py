"""
Complete CustomTkinter Dark Mode and Scaling Patch
This module disables dark mode and patches scaling to prevent crashes.
"""

import customtkinter as ctk
import sys
from tkinter import Tk

# --- Patch 1: Force Light Mode --- #
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")
print("[PATCH] Appearance mode set to Light.")

# --- Patch 2: AGGRESSIVE SCALING OVERRIDE --- #
# The previous attempts were not enough. We will now completely
# disable the problematic parts of CustomTkinter's scaling.

print("[PATCH] Applying aggressive scaling override.")

try:
    # Forcibly prevent CustomTkinter from detecting DPI changes.
    # This is the suspected source of the AttributeError crashes.
    def _update_scaling_factor_wrapper(self):
        # Print a message to confirm the patch is active.
        # print("[PATCHED] _update_scaling_factor_wrapper called and blocked.")
        return 1.0 # Always return a fixed scaling factor

    def _get_window_scaling(self):
        # print("[PATCHED] _get_window_scaling called and blocked.")
        return 1.0

    # Replace the methods on the CTk class
    ctk.CTk._update_scaling_factor_wrapper = _update_scaling_factor_wrapper
    ctk.CTk._get_window_scaling = _get_window_scaling
    
    # Check if Nuclear Patch is already active
    nuclear_patch_active = hasattr(ctk.ScalingTracker, 'set_widget_scaling') and hasattr(ctk.ScalingTracker, 'set_window_scaling')
    
    # Also apply a fixed scaling to all widgets and windows (if not nuclear patched)
    if nuclear_patch_active:
        print("[PATCH] Nuclear Patch detected - skipping scaling override.")
    else:
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

    print("[PATCH] Aggressive scaling override applied successfully. Scaling is now fixed at 1.0x.")

except Exception as e:
    print(f"[PATCH-ERROR] Failed to apply aggressive scaling patch: {e}. Critical error.")
    # If this fails, the app is likely to be unstable.
    # We still try the fallback.
    try:
        # Check if Nuclear Patch is active before fallback
        nuclear_patch_active = hasattr(ctk.ScalingTracker, 'set_widget_scaling') and hasattr(ctk.ScalingTracker, 'set_window_scaling')
        if not nuclear_patch_active:
            ctk.set_widget_scaling(1.0)
            ctk.set_window_scaling(1.0)
        else:
            print("[PATCH] Nuclear Patch fallback detected - skipping standard scaling.")
    except Exception as fallback_error:
        print(f"[PATCH-ERROR] Fallback scaling also failed: {fallback_error}")

# --- Patch 3: ANTI-TRANSPARENCY PROTECTION --- #
print("[PATCH] Applying anti-transparency protection...")

try:
    # Überschreibe problematische fg_color Setters um Transparenz zu verhindern
    def safe_configure_wrapper(original_configure):
        def wrapper(*args, **kwargs):
            # Erstes Argument ist self, extrahiere es
            if len(args) > 0:
                self = args[0]
                remaining_args = args[1:]
            else:
                # Fehlerfall - sollte nicht passieren
                return original_configure(*args, **kwargs)
                
            # Verhindere transparente fg_color Werte
            if 'fg_color' in kwargs:
                fg_color = kwargs['fg_color']
                if fg_color == "transparent" or (isinstance(fg_color, tuple) and "transparent" in str(fg_color)):
                    print(f"[PATCH] Blocked transparent fg_color on {self.__class__.__name__}")
                    kwargs['fg_color'] = "#F0F0F0"  # Fallback auf helles Grau
            return original_configure(self, *remaining_args, **kwargs)
        return wrapper

    # Wende Anti-Transparenz-Schutz auf alle wichtigen CTK Widgets an
    widget_classes = [
        ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkEntry,
        ctk.CTkTextbox, ctk.CTkOptionMenu, ctk.CTkCheckBox, 
        ctk.CTkRadioButton, ctk.CTkScrollableFrame
    ]

    for widget_class in widget_classes:
        if hasattr(widget_class, 'configure'):
            try:
                original_configure = widget_class.configure
                widget_class.configure = safe_configure_wrapper(original_configure)
                print(f"[PATCH] Anti-transparency applied to {widget_class.__name__}")
            except Exception as e:
                print(f"[PATCH] Warning: Could not patch {widget_class.__name__}: {e}")

    # Überschreibe auch direkte _set_appearance_mode Aufrufe
    if hasattr(ctk, '_set_appearance_mode'):
        original_set_appearance = ctk._set_appearance_mode
        def anti_transparency_appearance(mode_string):
            print(f"[PATCH] Appearance mode change blocked: {mode_string} -> Light")
            return original_set_appearance("Light")
        ctk._set_appearance_mode = anti_transparency_appearance

    print("[PATCH] Anti-transparency protection applied successfully.")

except Exception as e:
    print(f"[PATCH-ERROR] Failed to apply anti-transparency patch: {e}")

# --- Patch 4: TIMER-BASED MONITORING --- #
print("[PATCH] Setting up transparency monitoring...")

import threading
import time

def transparency_monitor():
    """Monitor für Transparenz-Probleme alle 2 Sekunden"""
    while True:
        try:
            time.sleep(2)
            # Force Light Mode falls es sich geändert hat
            current_mode = ctk.get_appearance_mode() if hasattr(ctk, 'get_appearance_mode') else "Light"
            if current_mode.lower() != "light":
                print(f"[PATCH] Monitor: Korrigiere {current_mode} -> Light")
                ctk.set_appearance_mode("Light")
        except Exception as e:
            print(f"[PATCH] Monitor error: {e}")
            break

# Starte Monitor-Thread
monitor_thread = threading.Thread(target=transparency_monitor, daemon=True, name="TransparencyMonitor")
monitor_thread.start()
print("[PATCH] Transparency monitor started.")

print("[PATCH] CustomTkinter patched successfully.")
