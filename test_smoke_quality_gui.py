#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke-Test: Stellt sicher, dass die Haupt-GUI ohne Mainloop initialisiert.

Ausführung: python -m pytest -q test_smoke_quality_gui.py
"""
import importlib

def test_quality_gui_starts():
    mod = importlib.import_module('quality_gui_main_app')
    app = mod.ProfessionelleUebersetzungsqualitaetsApp()
    assert app.root is not None, 'Root Fenster nicht erstellt'
    assert getattr(app, '_app_initialized', False) is True
    # Keine Mainloop starten; nur grundlegende Attribute prüfen
    assert hasattr(app, 'design_system')
