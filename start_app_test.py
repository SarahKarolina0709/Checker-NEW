#!/usr/bin/env python3
"""
Test Script: Starter die App und prüft welche GUI angezeigt wird
"""

import subprocess
import sys
import os
import time

def test_app_gui():
    """Teste die App und gib Anweisungen zur GUI-Identifizierung"""
    
    print("🚀 APP GUI TEST")
    print("=" * 50)
    
    print("\n1. 📱 Starte die CheckerApp...")
    print("   Führe aus: python checker_app.py")
    print("   (Dies wird in einem separaten Fenster geöffnet)")
    
    print("\n2. 🎯 Gehe zu Kundenmanagement:")
    print("   - Klicke in der Welcome Screen auf 'Kundenmanagement'")
    print("   - ODER verwende das Menü")
    
    print("\n3. 🔍 Identifiziere welche GUI angezeigt wird:")
    
    print("\n   ✅ RICHTIGE GUI (CustomerSectionComplete):")
    print("      📋 Erkennungsmerkmale:")
    print("      - Titel: 'Projektdaten & Auswahl'")  
    print("      - Untertitel: 'Kunde wählen • Projekt auswählen • Workflow starten'")
    print("      - Eingabefeld: 'Kundenname *'")
    print("      - Dropdown: 'Projekt auswählen'")
    print("      - Buttons: 'Projekt bestätigen' (grün), 'Kalender öffnen'")
    print("      - Sektion unten: 'Kürzlich verwendet'")
    print("      - Icon: 👤 (businesswoman)")
    
    print("\n   ❌ FALSCHE GUI (SimplifiedModernCustomerUI):")
    print("      📋 Erkennungsmerkmale:")
    print("      - Titel: 'Kundenmanagement' (oben)")
    print("      - Button: '+ Neuer Kunde' (oben rechts)")
    print("      - Suchfeld: 'Kunde suchen...' mit 🔍")
    print("      - Filter-Buttons: 'Alle', 'Aktiv', 'Inaktiv'")
    print("      - Kunden werden als Karten angezeigt")
    print("      - Blaue/graue Farben")
    
    print("\n4. 📊 Console Output prüfen:")
    print("   Achte auf [DEBUG] Nachrichten:")
    print("   - '[DEBUG] 🎯 FORCE: Verwende CustomerSectionComplete'")
    print("   - '[DEBUG] ✅ CustomerSectionComplete erfolgreich importiert'")
    print("   - '[DEBUG] ✅ CustomerSectionComplete über ViewStack angezeigt'")
    
    print("\n5. 🐛 Bei falscher GUI:")
    print("   - Prüfe Console auf Fehlermeldungen")
    print("   - Falls 'FALLBACK' in Console → Problem identifiziert")
    print("   - Screenshot machen und vergleichen")
    
    print("\n6. ✅ Bei richtiger GUI:")
    print("   - Teste Funktionen:")
    print("     • Kundenname eingeben")
    print("     • Projekt-Dropdown verwenden")
    print("     • Buttons klicken")
    print("     • Recent Projects prüfen")
    
    print("\n" + "="*50)
    print("🎯 STARTE DIE APP JETZT:")
    print("   python checker_app.py")
    print("="*50)

if __name__ == "__main__":
    test_app_gui()
