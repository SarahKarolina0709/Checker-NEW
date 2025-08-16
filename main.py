#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Checker Application Launcher
===========================

Startet die Checker-Anwendung
"""

import sys
import os

# Fügt das Hauptverzeichnis zum Python-Pfad hinzu, um die `core`-Module zu finden
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from core.app import CheckerApp
except ImportError:
    print("❌ Fehler: core.app Module nicht gefunden")
    print("Verwende alternative Startmethode...")

    # Fallback zu modularisierter GUI
    try:
        from modern_translation_quality_gui_modular import main as gui_main
        gui_main()
        sys.exit(0)
    except ImportError:
        print("❌ Keine GUI-Module verfügbar")
        sys.exit(1)

if __name__ == "__main__":
    try:
        app = CheckerApp()
        app.run()
    except Exception as e:
        print(f"❌ Fehler beim Starten der Checker App: {e}")
        print("Versuche GUI-Fallback...")

        try:
            from modern_translation_quality_gui_modular import main as gui_main
            gui_main()
        except Exception as fallback_error:
            print(f"❌ GUI-Fallback fehlgeschlagen: {fallback_error}")
            print("Alle Startoptionen erschöpft.")
            sys.exit(1)
    app = CheckerApp()
    app.mainloop()

