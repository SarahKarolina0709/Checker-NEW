#!/usr/bin/env python3
"""DEPRECATED: Benutze statt dessen 'start_checker.py --menu'.

Dieses Skript bleibt als dünne Weiterleitung bestehen und wird in Zukunft entfernt.
"""
import sys
from pathlib import Path

print("[quick_start] Dieses Skript ist veraltet. Verwende: python start_checker.py --menu")

# Versuche automatisches Weiterleiten
launcher = Path(__file__).parent / "start_checker.py"
if launcher.exists():
    from start_checker import QualityCheckerLauncher
    QualityCheckerLauncher().menu_mode()
else:
    print("start_checker.py nicht gefunden – bitte manuell ausführen.")
