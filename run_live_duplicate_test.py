#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 WELCOME SCREEN LIVE TEST
===========================

Startet den Welcome Screen direkt für manuellen Duplikat-Test.
"""

import sys
import os
import logging
from pathlib import Path

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def run_welcome_screen():
    """Startet Welcome Screen für Live-Test"""
    try:
        print("🚀 WELCOME SCREEN LIVE TEST")
        print("=" * 40)
        print("✅ Test customers already created")
        print("📋 Available test customers:")
        print("   1. TestFirma GmbH")
        print("   2. Beispiel AG")
        print()
        print("🎯 DUPLIKAT-TEST ANWEISUNGEN:")
        print("1. Versuche 'TestFirma GmbH' hinzuzufügen")
        print("   → Erwartung: Warnung 'Kunde bereits vorhanden'")
        print("2. Versuche 'testfirma gmbh' (klein) hinzuzufügen")
        print("   → Erwartung: Warnung + Auto-Selektion")
        print("3. Versuche 'beispiel ag' (klein) hinzuzufügen")
        print("   → Erwartung: Warnung + Auto-Selektion")
        print("4. Versuche 'Neue Test Firma' hinzuzufügen")
        print("   → Erwartung: Erfolgreich hinzugefügt")
        print()
        print("🚀 Starte Welcome Screen...")
        print("-" * 40)
        
        # Import und starte Welcome Screen
        from welcome_screen import WelcomeScreen
        import customtkinter as ctk
        
        # Mock App Objekt für WelcomeScreen
        class MockApp:
            def __init__(self):
                self.config = {"theme": "light"}
                
        # Erstelle Root und App
        root = ctk.CTk()
        root.title("🧪 Duplikat-Test - Welcome Screen")
        root.geometry("1200x800")
        
        # Setze Light Mode
        ctk.set_appearance_mode("light")
        
        # Mock App erstellen
        app = MockApp()
        
        # Welcome Screen erstellen
        welcome = WelcomeScreen(root, app)
        welcome.pack(fill="both", expand=True)
        
        print("✅ Welcome Screen gestartet!")
        print("🧪 Führe jetzt die Duplikat-Tests durch...")
        
        # Starte GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler beim Starten: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_welcome_screen()
    if success:
        print("✅ Test abgeschlossen")
    else:
        print("❌ Test fehlgeschlagen")
        sys.exit(1)
