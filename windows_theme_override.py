#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 WINDOWS SYSTEM THEME OVERRIDE
================================

Übersteuert Windows System Theme Einstellungen für Light Mode.
"""

import os
import sys

def force_windows_light_theme():
    """Forciert Windows Light Theme auf Anwendungsebene"""
    if sys.platform != "win32":
        print("⚠️ Windows Theme Override nur auf Windows verfügbar")
        return

    try:
        # Windows-spezifische Theme-Environment Variablen
        os.environ['WINDOWS_THEME_MODE'] = 'light'
        os.environ['SYSTEM_THEME'] = 'light'
        os.environ['PREFERRED_THEME'] = 'light'

        # Versuche Windows Registry Override (falls verfügbar)
        try:
            import winreg

            # Registry-Schlüssel für Personalisierung
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"

            # Versuche aktuellen App-Theme zu übersteuern
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    # Apps use light theme (1 = light, 0 = dark)
                    winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
                    print("✅ Windows App Light Theme erzwungen")
            except Exception as reg_error:
                print(f"⚠️ Registry App Theme Override nicht möglich: {reg_error}")

        except ImportError:
            print("⚠️ Windows Registry Module nicht verfügbar")

        print("✅ Windows Light Theme Environment gesetzt")

    except Exception as e:
        print(f"❌ Windows Theme Override Error: {e}")

# Führe Override automatisch beim Import aus
force_windows_light_theme()