#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der KundenManager-Integration in der Hauptanwendung
Überprüft, ob das KundenManager-System ordnungsgemäß in die 
Checker App integriert ist und mit den Workflows funktioniert.
"""

import os
import sys
import json
from datetime import datetime
import traceback

def test_main_app_integration():
    """Testet die Integration des KundenManagers in die Hauptanwendung"""
    print("🔍 TESTE HAUPTANWENDUNG-INTEGRATION")
    print("="*60)
    
    try:
        # Import der Hauptanwendung
        from checker_app import CheckerApp
        from kunden_manager import KundenManager
        print("✅ Module erfolgreich importiert")
        
        # Prüfe, ob die Hauptanwendung einen KundenManager hat
        app = CheckerApp()
        print("✅ CheckerApp erfolgreich initialisiert")
        
        # Prüfe KundenManager-Integration
        if hasattr(app, 'kunden_manager'):
            print("✅ KundenManager ist in der Hauptanwendung integriert")
            
            # Teste KundenManager-Methoden
            manager = app.kunden_manager
            
            # Test: Alle Kunden anzeigen
            kunden = manager.alle_kunden()
            print(f"✅ Gefundene Kunden: {len(kunden)}")
            for kunde in kunden[:3]:  # Zeige nur die ersten 3
                print(f"   • {kunde}")
            
            # Test: Neuen Testkunden erstellen
            test_kunde = "Integration_Test_Kunde"
            kunde_pfad = manager.erstelle_kundenstruktur(test_kunde)
            print(f"✅ Test-Kunde erstellt: {kunde_pfad}")
            
            # Test: Projektordner erstellen
            projekt_pfad = manager.neuer_anfrage_ordner(
                test_kunde, 
                "Angebot", 
                "Integration_Test_Projekt"
            )
            print(f"✅ Test-Projekt erstellt: {projekt_pfad}")
            
        else:
            print("❌ KundenManager ist nicht in der Hauptanwendung integriert")
            return False
            
        # Cleanup
        if hasattr(app, 'root') and app.root:
            app.root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Hauptanwendung-Integration: {e}")
        traceback.print_exc()
        return False

def test_workflow_data_handling():
    """Testet die Handhabung von Workflow-Daten"""
    print("\n🔍 TESTE WORKFLOW-DATEN-HANDHABUNG")
    print("="*60)
    
    try:
        from kunden_manager import KundenManager
        
        manager = KundenManager()
        
        # Simuliere typische Workflow-Daten
        workflow_scenarios = [
            {
                "kunde_name": "Workflow Test GmbH",
                "auftragsnummer": "WT-2025-001",
                "workflow": "Angebot",
                "kundenbetreuer": "Test Betreuer",
                "zielsprache": "DE → EN"
            },
            {
                "kunde_name": "workflow test gmbh",  # Lowercase für Fuzzy-Test
                "auftragsnummer": "WT-2025-002", 
                "workflow": "Pruefung",
                "kundenbetreuer": "Test Betreuer 2",
                "zielsprache": "EN → DE"
            }
        ]
        
        for i, scenario in enumerate(workflow_scenarios, 1):
            print(f"\n📋 Workflow-Szenario {i}:")
            
            # Erstelle Projektordner
            projekt_pfad = manager.neuer_anfrage_ordner(
                scenario["kunde_name"],
                scenario["workflow"],
                scenario["auftragsnummer"]
            )
            print(f"   ✅ Projektordner: {projekt_pfad}")
            
            # Erstelle Metadaten
            metadata = {
                **scenario,
                "erstellt_am": datetime.now().isoformat(),
                "status": "aktiv",
                "dateien": []
            }
            
            metadata_file = os.path.join(projekt_pfad, "project_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Metadaten gespeichert")
            
            # Erstelle typische Projektstruktur
            os.makedirs(os.path.join(projekt_pfad, "quellen"), exist_ok=True)
            os.makedirs(os.path.join(projekt_pfad, "uebersetzungen"), exist_ok=True)
            os.makedirs(os.path.join(projekt_pfad, "final"), exist_ok=True)
            
            print(f"   ✅ Projektstruktur erstellt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Workflow-Daten-Handhabung: {e}")
        traceback.print_exc()
        return False

def test_project_data_compatibility():
    """Testet die Kompatibilität mit project_data_manager"""
    print("\n🔍 TESTE PROJECT-DATA-KOMPATIBILITÄT")
    print("="*60)
    
    try:
        # Prüfe ob project_data_manager existiert
        if os.path.exists("project_data_manager.py"):
            from project_data_manager import load_projects, add_or_update_project
            print("✅ project_data_manager gefunden")
            
            # Lade existierende Projekte
            projects = load_projects()
            print(f"✅ Existierende Projekte geladen: {len(projects)}")
            
            # Teste Integration
            test_project = {
                "project_id": "integration_test_001",
                "kunde_name": "Integration Test Firma",
                "auftragsnummer": "IT-001",
                "kundenbetreuer": "Test Manager",
                "status": "in_bearbeitung",
                "erstellt_am": datetime.now().isoformat()
            }
            
            add_or_update_project(test_project)
            print("✅ Test-Projekt zu project_data_manager hinzugefügt")
            
        else:
            print("ℹ️  project_data_manager.py nicht gefunden (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Project-Data-Kompatibilität: {e}")
        traceback.print_exc()
        return False

def test_customer_menu_functions():
    """Testet die Kunden-Menü-Funktionen"""
    print("\n🔍 TESTE KUNDEN-MENÜ-FUNKTIONEN")
    print("="*60)
    
    try:
        from kunden_manager import KundenManager
        
        manager = KundenManager()
        
        # Test: Kundenliste
        kunden = manager.alle_kunden()
        print(f"✅ Kundenliste abrufbar: {len(kunden)} Kunden")
        
        # Test: Fuzzy-Suche
        if kunden:
            test_kunde = kunden[0]
            # Teste verschiedene Suchvarianten
            search_variants = [
                test_kunde.lower(),
                test_kunde.replace('_', ' '),
                test_kunde[:5] + "..."  # Teilstring
            ]
            
            for variant in search_variants:
                match = manager.fuzzy_kundenname_suche(variant)
                if match:
                    print(f"✅ Fuzzy-Match: '{variant}' → '{match}'")
                else:
                    print(f"ℹ️  Kein Match: '{variant}'")
        
        # Test: Kundenstatistiken
        stats = {}
        for kunde in kunden:
            unterordner = manager.kunden_unterordner(kunde)
            stats[kunde] = len(unterordner)
        
        print(f"✅ Kundenstatistiken berechnet für {len(stats)} Kunden")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Kunden-Menü-Funktionen: {e}")
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Bereinigt Test-Daten"""
    print("\n🧹 BEREINIGE TEST-DATEN")
    print("="*40)
    
    test_entities = [
        "Integration_Test_Kunde",
        "Workflow Test GmbH", 
        "Integration Test Firma"
    ]
    
    from kunden_manager import KundenManager
    manager = KundenManager()
    
    for entity in test_entities:
        entity_path = manager.kunden_ordner(entity)
        if os.path.exists(entity_path):
            import shutil
            try:
                shutil.rmtree(entity_path)
                print(f"✅ Bereinigt: {entity}")
            except Exception as e:
                print(f"⚠️  Konnte nicht bereinigen: {entity} ({e})")

def main():
    """Hauptfunktion für Integrationstests"""
    print("🚀 KUNDENMANAGER INTEGRATIONS-TEST")
    print("=" * 60)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Hauptanwendung-Integration", test_main_app_integration),
        ("Workflow-Daten-Handhabung", test_workflow_data_handling),
        ("Project-Data-Kompatibilität", test_project_data_compatibility),
        ("Kunden-Menü-Funktionen", test_customer_menu_functions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name.upper()}")
        print(f"{'='*60}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Kritischer Fehler in {test_name}: {e}")
            results[test_name] = False
    
    # Zusammenfassung
    print(f"\n{'='*60}")
    print("📊 TEST-ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nERGEBNIS: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 ALLE INTEGRATIONSTESTS ERFOLGREICH!")
        print("Der KundenManager ist vollständig integriert und funktionsfähig.")
    else:
        print("⚠️  EINIGE TESTS FEHLGESCHLAGEN")
        print("Bitte überprüfen Sie die Fehlerausgaben oben.")
    
    # Optional: Test-Daten bereinigen
    try:
        cleanup_test_data()
    except:
        pass  # Fehler beim Cleanup ignorieren
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
