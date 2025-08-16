#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 GLOBALE LIGHT MODE ERZWINGUNG
====================================

Diese Datei MUSS als ERSTES importiert werden, um Dark Mode vollständig zu verhindern.
Setzt alle notwendigen Environment-Variablen und Monkey-Patches.
"""

import os

os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'
os.environ['TKINTER_APPEARANCE'] = 'light'
os.environ['CTK_THEME'] = 'light'

# Importiere CustomTkinter erst NACH Environment Setup
import customtkinter as ctk

# 🚨 SOFORTIGE LIGHT MODE ERZWINGUNG
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# 🔥 MONKEY PATCH - VERHINDERE JEDEN DARK MODE ZUGRIFF
_original_set_appearance = ctk.set_appearance_mode

def _force_light_only(mode):
    """
    Globaler Monkey Patch - verhindert jeden Dark Mode Zugriff
    """
    if isinstance(mode, str) and mode.lower() == "dark":
        print("🚨 DARK MODE BLOCKIERT! Erzwinge Light Mode!")
        return _original_set_appearance("light")
    return _original_set_appearance("light")

# Ersetze die originale Funktion
ctk.set_appearance_mode = _force_light_only

# 🔥 FINALE LIGHT MODE ERZWINGUNG
ctk.set_appearance_mode("light")

print("✅ Light Mode global erzwungen - Dark Mode vollständig blockiert!")