#!/usr/bin/env python3
"""
🔥 LIGHT MODE STARTUP IMPORT
===========================
Universeller Import für AUTOMATISCHE Light Mode Enforcement

USAGE:
Einfach am Anfang JEDER Python-Datei importieren:

    from light_mode_startup import *

Das wars! Dark Mode wird automatisch verhindert.
"""

# 🔥 SOFORTIGE LIGHT MODE ENFORCEMENT BEI IMPORT
try:
    from global_light_mode_enforcer import apply_light_mode_startup
    apply_light_mode_startup()
except ImportError:
    # Fallback wenn global_light_mode_enforcer nicht verfügbar
    try:
        import customtkinter as ctk
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        print("✅ Fallback Light Mode enforcement active")
    except ImportError:
        pass

print("🔥 Light Mode Startup Import executed - Dark Mode blocked!")