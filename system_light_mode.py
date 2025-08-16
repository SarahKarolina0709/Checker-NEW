#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 SYSTEMWEITE LIGHT MODE ERZWINGUNG
====================================

Übersteuert alle möglichen System- und CustomTkinter Dark Mode Einstellungen.
"""

import os
import sys

os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'
os.environ['TKINTER_APPEARANCE'] = 'light'
os.environ['CTK_THEME'] = 'light'
os.environ['QT_SCALE_FACTOR'] = '1'
os.environ['GDK_SCALE'] = '1'

# Windows-spezifische Theme-Übersteuerung
if sys.platform == "win32":
    os.environ['WINDOWS_THEME_MODE'] = 'light'
    os.environ['SYSTEM_THEME'] = 'light'

try:
    import customtkinter as ctk

    # 🚨 SOFORTIGE LIGHT MODE ERZWINGUNG
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 🔥 ERWEITERTE MONKEY PATCHES
    _original_set_appearance = ctk.set_appearance_mode
    _original_get_appearance = ctk.get_appearance_mode

    def _force_light_appearance(mode=None):
        """Erzwinge immer Light Mode, unabhängig vom Parameter"""
        print(f"🚨 Appearance Mode Override: {mode} → light")
        return _original_set_appearance("light")

    def _force_light_get():
        """Gebe immer 'Light' zurück"""
        return "Light"

    # Ersetze beide Funktionen
    ctk.set_appearance_mode = _force_light_appearance
    ctk.get_appearance_mode = _force_light_get

    # 🔥 WIDGET-LEVEL OVERRIDES
    # Übersteuere Widget-Standard-Farben für Light Mode
    try:
        # CTkFrame Override
        original_ctk_frame_init = ctk.CTkFrame.__init__
        def light_frame_init(self, *args, **kwargs):
            # Forciere Light Mode Farben wenn nicht explizit gesetzt
            if 'fg_color' not in kwargs:
                kwargs['fg_color'] = '#FFFFFF'
            return original_ctk_frame_init(self, *args, **kwargs)
        ctk.CTkFrame.__init__ = light_frame_init

        # CTkButton Override
        original_ctk_button_init = ctk.CTkButton.__init__
        def light_button_init(self, *args, **kwargs):
            # Forciere Light Mode Farben
            if 'fg_color' not in kwargs:
                kwargs['fg_color'] = '#1F4E79'  # Professionelles Blau
            if 'text_color' not in kwargs:
                kwargs['text_color'] = '#FFFFFF'
            return original_ctk_button_init(self, *args, **kwargs)
        ctk.CTkButton.__init__ = light_button_init

        print("✅ Widget-Level Light Mode Overrides aktiviert")

    except Exception as widget_error:
        print(f"⚠️ Widget Override Error: {widget_error}")

    # 🔥 FINALE ERZWINGUNG
    ctk.set_appearance_mode("light")

    print("✅ Systemweite Light Mode Erzwingung aktiv!")
    print(f"✅ CustomTkinter Appearance Mode: {ctk.get_appearance_mode()}")

except ImportError as e:
    print(f"❌ CustomTkinter Import Error: {e}")
except Exception as e:
    print(f"❌ System Light Mode Override Error: {e}")