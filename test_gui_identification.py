#!/usr/bin/env python3
"""
GUI Debug Script - Identifiziert welche Customer Management GUI geladen wird
"""

def test_which_gui_loads():
    """Teste welche GUI tatsächlich geladen wird"""
    
    print("🔍 GUI DEBUG: Welche Customer Management GUI wird geladen?")
    print("=" * 60)
    
    # Test 1: Teste CustomerSectionComplete direkt
    print("\n1. 📋 TEST: CustomerSectionComplete (Soll-GUI)")
    try:
        from welcome_screen_components.customer_section_complete import CustomerSectionComplete
        print("   ✅ CustomerSectionComplete erfolgreich importiert")
        print("   📝 Diese GUI sollte angezeigt werden:")
        print("      - Kundenauswahl mit Eingabefeld")
        print("      - Projekt-Dropdown")
        print("      - Recent Projects Sektion")
        print("      - Action Buttons (Projekt bestätigen, Kalender)")
        print("   🎯 FARBEN: Grüne Buttons, transparenter Hintergrund")
        
    except Exception as e:
        print(f"   ❌ CustomerSectionComplete Fehler: {e}")
    
    # Test 2: Teste SimplifiedModernCustomerUI
    print("\n2. 📋 TEST: SimplifiedModernCustomerUI (Fallback-GUI)")
    try:
        from simplified_modern_customer_ui import SimplifiedModernCustomerUI
        print("   ✅ SimplifiedModernCustomerUI erfolgreich importiert")
        print("   📝 Diese GUI könnte fälschlicherweise angezeigt werden:")
        print("      - Kundenmanagement-Titel")
        print("      - Suchleiste")
        print("      - Filter-Buttons (Alle, Aktiv, Inaktiv)")
        print("      - Kunden-Karten Grid")
        print("   🎯 FARBEN: Blaue Buttons, weißer Hintergrund")
        
    except Exception as e:
        print(f"   ❌ SimplifiedModernCustomerUI Fehler: {e}")
    
    # Test 3: Teste UI Modernizer
    print("\n3. 📋 TEST: UI Modernizer (Legacy Fallback)")
    try:
        from ui_modernization_update import ModernUIUpdater
        print("   ✅ ModernUIUpdater erfolgreich importiert")
        print("   📝 Diese GUI ist der letzte Fallback:")
        print("      - Alte Kundenmanagement-Oberfläche")
        print("      - Weniger moderne Styling")
        
    except Exception as e:
        print(f"   ❌ ModernUIUpdater Fehler: {e}")
    
    # Test 4: Simuliere das Prioritätssystem
    print("\n4. 🔄 PRIORITÄTSSYSTEM SIMULATION:")
    print("   App wird in dieser Reihenfolge versuchen:")
    print("   1️⃣ CustomerSectionComplete (GEWÜNSCHT)")
    print("   2️⃣ SimplifiedModernCustomerUI (Fallback)")
    print("   3️⃣ UI Modernizer (Legacy)")
    
    # Test 5: Identifiziere mögliche Probleme
    print("\n5. ⚠️ MÖGLICHE PROBLEME:")
    
    problems = []
    
    # Prüfe ob ViewStack fehlt
    try:
        from view_stack import EnhancedViewStack
        print("   ✅ ViewStack verfügbar")
    except Exception as e:
        problems.append("ViewStack nicht verfügbar - könnte zu Fallback führen")
        print(f"   ❌ ViewStack Problem: {e}")
    
    # Prüfe App-Initialisierung
    try:
        from checker_app import CheckerApp
        print("   ✅ CheckerApp importierbar")
        
        # Prüfe kritische Methoden
        app_class = CheckerApp
        if hasattr(app_class, 'show_customer_section_complete'):
            print("   ✅ show_customer_section_complete Methode vorhanden")
        else:
            problems.append("show_customer_section_complete Methode fehlt")
            print("   ❌ show_customer_section_complete FEHLT")
            
    except Exception as e:
        problems.append(f"CheckerApp Problem: {e}")
        print(f"   ❌ CheckerApp Problem: {e}")
    
    if problems:
        print("\n❌ IDENTIFIZIERTE PROBLEME:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")
    else:
        print("\n✅ Keine offensichtlichen Probleme gefunden")
    
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("   1. Starte checker_app.py")
    print("   2. Klicke auf Kundenmanagement")
    print("   3. Prüfe Console-Output auf [DEBUG] Nachrichten")
    print("   4. Vergleiche angezeigte GUI mit erwarteter CustomerSectionComplete")
    
    print("\n💡 ERKENNUNGSMERKMALE:")
    print("   RICHTIGE GUI (CustomerSectionComplete):")
    print("   - Eingabefeld 'Kundenname *'")
    print("   - Dropdown 'Projekt auswählen'")
    print("   - 'Kürzlich verwendet' Sektion unten")
    print("   - Grüne 'Projekt bestätigen' Button")
    
    print("\n   FALSCHE GUI (SimplifiedModernCustomerUI):")
    print("   - Titel 'Kundenmanagement' oben")
    print("   - Suchfeld 'Kunde suchen...'")
    print("   - Filter-Buttons 'Alle', 'Aktiv', 'Inaktiv'")
    print("   - Kunden-Karten in Grid-Layout")

if __name__ == "__main__":
    test_which_gui_loads()
