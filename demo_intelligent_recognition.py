#!/usr/bin/env python3
"""
Demo für das intelligente Kundensystem
Zeigt die automatische Erkennung und Vorschläge für ähnliche Kunden.
"""

import os
import sys
import tempfile
import shutil
from kunden_manager import KundenManager

def demo_intelligent_customer_recognition():
    """Demonstriert das intelligente Kundensystem mit Erkennung und Vorschlägen."""
    
    print("🤖 Intelligentes Kundensystem - Live Demo")
    print("=" * 60)
    
    # Temporäres Verzeichnis für Demo
    demo_dir = tempfile.mkdtemp(prefix="demo_kunden_")
    print(f"📁 Demo-Verzeichnis: {demo_dir}")
    
    try:
        # KundenManager mit Demo-Verzeichnis
        km = KundenManager(base_dir=demo_dir)
        
        # Demo-Kunden erstellen
        demo_kunden = [
            "Mustermann GmbH",
            "Beispiel AG", 
            "ACME Corporation",
            "Test Solutions",
            "Demo & Partner",
            "Muster Consulting"
        ]
        
        print("\n📋 Demo-Kunden werden erstellt...")
        for kunde in demo_kunden:
            km.erstelle_kundenstruktur(kunde)
            print(f"  ✅ {kunde}")
        
        print(f"\n👥 {len(demo_kunden)} Demo-Kunden erstellt")
        
        # Test-Szenarien
        test_cases = [
            # Exakte Übereinstimmung
            ("Mustermann GmbH", "EXAKT"),
            
            # Tippfehler
            ("Musterman GmbH", "TIPPFEHLER"),
            ("Musterman", "TIPPFEHLER"),
            
            # Groß-/Kleinschreibung
            ("mustermann gmbh", "CASE"),
            ("MUSTERMANN", "CASE"),
            
            # Teilnamen
            ("Beispiel", "TEILNAME"),
            ("ACME", "TEILNAME"),
            ("Demo", "TEILNAME"),
            
            # Ähnliche Namen
            ("Muster GmbH", "ÄHNLICH"),
            ("Beispiel Solutions", "ÄHNLICH"),
            ("Test Corp", "ÄHNLICH"),
            
            # Komplett neue Kunden
            ("Völlig Neuer Kunde", "NEU"),
            ("Andere Firma", "NEU"),
        ]
        
        print("\n🔍 Intelligente Erkennungs-Tests")
        print("=" * 60)
        
        for eingabe, erwartung in test_cases:
            print(f"\n📝 Eingabe: '{eingabe}'")
            
            # Prüfung mit dem intelligenten System
            exists, matched_name = km.customer_exists(eingabe)
            
            if exists:
                if matched_name == eingabe:
                    print(f"  ✅ EXAKT GEFUNDEN: '{matched_name}'")
                    print(f"  🎯 Aktion: Bestehenden Kunden '{matched_name}' verwenden")
                else:
                    print(f"  🔍 ÄHNLICH GEFUNDEN: '{matched_name}'")
                    print(f"  🤔 Vorschlag: 'Meinten Sie {matched_name}?'")
                    print(f"  ⚡ Optionen:")
                    print(f"     • Ja: Bestehenden Kunden '{matched_name}' verwenden")
                    print(f"     • Nein: Neuen Kunden '{eingabe}' erstellen")
            else:
                print(f"  ➕ NEUER KUNDE: '{eingabe}'")
                print(f"  🎯 Aktion: Neuen Kunden '{eingabe}' erstellen")
            
            # Zusätzliche Fuzzy-Suche für Demonstration
            fuzzy_result = km.find_customer_fuzzy(eingabe)
            if fuzzy_result and fuzzy_result != matched_name:
                print(f"  🔍 Weitere Ähnlichkeit: '{fuzzy_result}'")
        
        print("\n🎉 Demo-Szenarien für Benutzer-Interface")
        print("=" * 60)
        
        ui_scenarios = [
            ("Mustermann GmbH", "Exakte Übereinstimmung"),
            ("Musterman GmbH", "Tippfehler mit Vorschlag"),
            ("Neue Firma", "Neuer Kunde"),
        ]
        
        for eingabe, beschreibung in ui_scenarios:
            print(f"\n📱 Szenario: {beschreibung}")
            print(f"   Eingabe: '{eingabe}'")
            
            exists, matched_name = km.customer_exists(eingabe)
            
            if exists:
                if matched_name == eingabe:
                    print(f"   💬 Dialog: \"✅ Kunde '{eingabe}' gefunden!\"")
                    print(f"   📁 Zeigt: Ordnerstruktur und Workflows verfügbar")
                else:
                    print(f"   💬 Dialog: \"🤔 Meinten Sie '{matched_name}'?\"")
                    print(f"   🔘 Option 1: Bestehenden Kunden '{matched_name}' verwenden")
                    print(f"   🔘 Option 2: Neuen Kunden '{eingabe}' erstellen")
                    print(f"   🔘 Option 3: Eingabe korrigieren")
            else:
                print(f"   💬 Dialog: \"✅ Neuer Kunde '{eingabe}' wird erstellt!\"")
                print(f"   📁 Aktion: Ordnerstruktur wird angelegt")
        
        print("\n🎯 System-Vorteile")
        print("=" * 60)
        print("✅ Automatische Erkennung bestehender Kunden")
        print("✅ Intelligente Vorschläge bei ähnlichen Namen")
        print("✅ Vermeidung von Duplikaten durch Tippfehler")
        print("✅ Benutzerfreundliche Bestätigungsdialoge")
        print("✅ Ein Button für alle Szenarien")
        print("✅ Kein manuelles 'Neu oder Bestehend?' mehr")
        
        print("\n🔧 Technische Details")
        print("=" * 60)
        print(f"📊 Fuzzy-Matching Schwellenwert: 70%")
        print(f"🎯 Erkennungstypen:")
        print(f"   • Exakte Übereinstimmung")
        print(f"   • Tippfehler (1-2 Buchstaben)")
        print(f"   • Groß-/Kleinschreibung")
        print(f"   • Teilnamen")
        print(f"   • Ähnliche Wörter")
        
    finally:
        # Aufräumen
        try:
            shutil.rmtree(demo_dir)
            print(f"\n🧹 Demo-Verzeichnis bereinigt: {demo_dir}")
        except:
            pass

if __name__ == "__main__":
    demo_intelligent_customer_recognition()
