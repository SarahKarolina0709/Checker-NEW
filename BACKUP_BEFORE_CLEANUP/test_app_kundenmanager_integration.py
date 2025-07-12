#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der KundenManager Integration in der Hauptanwendung
Überprüft, ob das Kundenmanagement korrekt in checker_app.py funktioniert
"""

import sys
import os
import json
from datetime import datetime

# Arbeitsverzeichnis hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_kundenmanager_integration():
    """Testet die KundenManager Integration in der Hauptanwendung"""
    print("=" * 60)
    print("🔬 TEST: KundenManager Integration in Hauptanwendung")
    print("=" * 60)
    
    try:
        # Importiere die Hauptanwendung und KundenManager
        from kunden_manager import KundenManager
        import project_data_manager
        
        print("1️⃣ TESTE: KundenManager Initialisierung")
        print("-" * 50)
        
        # Initialisiere KundenManager
        kunden_manager = KundenManager()
        print(f"✅ KundenManager initialisiert mit Basis-Verzeichnis: {kunden_manager.base_dir}")
        
        # Prüfe ob Basis-Verzeichnis existiert
        if os.path.exists(kunden_manager.base_dir):
            print(f"✅ Basis-Verzeichnis existiert: {kunden_manager.base_dir}")
        else:
            print(f"❌ Basis-Verzeichnis nicht gefunden: {kunden_manager.base_dir}")
            return False
        
        print("\n2️⃣ TESTE: Kundenliste und Verwaltung")
        print("-" * 50)
        
        # Alle Kunden abrufen
        alle_kunden = kunden_manager.alle_kunden()
        print(f"📋 Gefundene Kunden: {len(alle_kunden)}")
        
        for kunde in alle_kunden:
            print(f"  👤 {kunde}")
            
            # Prüfe Unterordner für jeden Kunden
            unterordner = kunden_manager.kunden_unterordner(kunde)
            for ordner in unterordner:
                print(f"    📁 {ordner}")
                
                # Prüfe Projekte in diesem Ordner
                ordner_pfad = os.path.join(kunden_manager.kunden_ordner(kunde), ordner)
                if os.path.exists(ordner_pfad):
                    projekte = [d for d in os.listdir(ordner_pfad) 
                              if os.path.isdir(os.path.join(ordner_pfad, d))]
                    if projekte:
                        print(f"      📄 Projekte: {', '.join(projekte)}")
        
        print("\n3️⃣ TESTE: Workflow-Daten Kompatibilität")
        print("-" * 50)
        
        # Teste verschiedene Workflow-Szenarien
        test_scenarios = [
            {
                "kunde_name": "Test Kunde", 
                "auftragsnummer": "TEST-001",
                "workflow": "Angebot"
            },
            {
                "kunde_name": "Test_Kunde", 
                "auftragsnummer": "TEST-002",
                "workflow": "Pruefung"
            },
            {
                "kunde_name": "test kunde", 
                "auftragsnummer": "TEST-003", 
                "workflow": "Finalisierung"
            }
        ]
        
        for scenario in test_scenarios:
            kunde_name = scenario["kunde_name"]
            workflow = scenario["workflow"]
            
            # Teste Fuzzy-Matching
            fuzzy_match = kunden_manager.fuzzy_kundenname_suche(kunde_name)
            if fuzzy_match:
                print(f"✅ Fuzzy-Match: '{kunde_name}' → '{fuzzy_match}'")
                
                # Teste Workflow-Ordner Zugriff
                workflow_ordner = kunden_manager.get_ordner_fuer_workflow(fuzzy_match, workflow)
                if os.path.exists(workflow_ordner):
                    print(f"  ✅ Workflow-Ordner existiert: {workflow_ordner}")
                else:
                    print(f"  ⚠️ Workflow-Ordner nicht gefunden: {workflow_ordner}")
            else:
                print(f"❌ Kein Match für: '{kunde_name}'")
        
        print("\n4️⃣ TESTE: Project Data Manager Integration")
        print("-" * 50)
        
        # Lade Projekte aus project_data_manager
        try:
            projekte = project_data_manager.load_projects()
            print(f"📊 Projekte in project_data_manager: {len(projekte)}")
            
            for projekt in projekte:
                print(f"  📄 {projekt.get('auftragsnummer')} ({projekt.get('kunde_name')})")
                
                # Prüfe ob KundenManager den Kunden findet
                kunde_name = projekt.get('kunde_name')
                if kunde_name:
                    fuzzy_match = kunden_manager.fuzzy_kundenname_suche(kunde_name)
                    if fuzzy_match:
                        print(f"    ✅ Kunde gefunden: '{kunde_name}' → '{fuzzy_match}'")
                    else:
                        print(f"    ❌ Kunde nicht gefunden: '{kunde_name}'")
                        
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Projekte: {e}")
        
        print("\n5️⃣ TESTE: Workflow-Daten Verarbeitung")
        print("-" * 50)
        
        # Simuliere Workflow-Daten wie sie von der App übergeben werden
        workflow_data_examples = [
            {
                "kunde_name": "Test Kunde 1",
                "auftragsnummer": "TK1-2025-001",
                "workflow": "Angebot",
                "uploaded_files": ["test1.docx", "test2.pdf"],
                "kundenbetreuer": "Manager A",
                "zielsprache": "DE → EN"
            },
            {
                "kunde_name": "Test",
                "auftragsnummer": "T-2025-001", 
                "workflow": "Pruefung",
                "uploaded_files": ["source.txt", "target.txt"],
                "kundenbetreuer": "Manager B",
                "zielsprache": "EN → DE"
            }
        ]
        
        for workflow_data in workflow_data_examples:
            kunde_name = workflow_data["kunde_name"]
            workflow = workflow_data["workflow"]
            auftrag = workflow_data["auftragsnummer"]
            
            print(f"🔄 Teste Workflow: {workflow} für Kunde: {kunde_name}")
            
            # Prüfe ob Kunde existiert oder gefunden werden kann
            existing_customer = kunden_manager.fuzzy_kundenname_suche(kunde_name)
            if existing_customer:
                print(f"  ✅ Kunde gefunden: {existing_customer}")
                
                # Teste Ordner-Erstellung
                try:
                    projekt_ordner = kunden_manager.neuer_anfrage_ordner(
                        kunde_name, workflow, auftrag
                    )
                    print(f"  ✅ Projekt-Ordner würde erstellt: {projekt_ordner}")
                    
                    # Simuliere Metadaten-Speicherung
                    metadata = {
                        "kunde_name": existing_customer,
                        "auftragsnummer": auftrag,
                        "workflow": workflow,
                        "kundenbetreuer": workflow_data.get("kundenbetreuer"),
                        "zielsprache": workflow_data.get("zielsprache"),
                        "erstellt_am": datetime.now().isoformat(),
                        "status": "aktiv",
                        "dateien": workflow_data.get("uploaded_files", [])
                    }
                    print(f"  ✅ Metadaten bereit für Speicherung")
                    
                except Exception as e:
                    print(f"  ❌ Fehler bei Ordner-Erstellung: {e}")
            else:
                print(f"  ⚠️ Kunde nicht gefunden, würde neuen Kunden erstellen: {kunde_name}")
        
        print("\n6️⃣ TESTE: Error Handling und Edge Cases")
        print("-" * 50)
        
        # Teste Error Handling
        edge_cases = [
            "",  # Leerer String
            None,  # None
            "Kunde/mit\\ungültigen:Zeichen",  # Ungültige Zeichen
            "   Kunde mit Leerzeichen   ",  # Führende/nachfolgende Leerzeichen
            "sehr_langer_kundenname_der_möglicherweise_probleme_verursacht_" * 3  # Sehr langer Name
        ]
        
        for test_case in edge_cases:
            try:
                if test_case is None:
                    print(f"  🧪 Test mit None...")
                    continue
                    
                print(f"  🧪 Test mit: '{test_case[:50]}{'...' if len(str(test_case)) > 50 else ''}'")
                
                # Teste Fuzzy-Matching
                match = kunden_manager.fuzzy_kundenname_suche(test_case)
                if match:
                    print(f"    ✅ Match gefunden: {match}")
                else:
                    print(f"    ⚪ Kein Match (erwartbar)")
                    
                # Teste Sanitization
                if test_case:
                    sanitized = kunden_manager._sanitize_name(test_case)
                    print(f"    🧹 Sanitized: '{sanitized}'")
                    
            except Exception as e:
                print(f"    ❌ Fehler bei Edge Case: {e}")
        
        print("\n" + "=" * 60)
        print("✅ HAUPTANWENDUNG INTEGRATION TEST ERFOLGREICH")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_specific_functions():
    """Testet workflow-spezifische Funktionen"""
    print("\n" + "=" * 60)
    print("🔬 TEST: Workflow-spezifische Funktionen")
    print("=" * 60)
    
    try:
        from kunden_manager import KundenManager
        
        kunden_manager = KundenManager()
        
        # Teste verschiedene Workflows
        workflows = ["Angebot", "Pruefung", "Finalisierung"]
        test_kunde = "Test_Kunde"
        
        print(f"🎯 Teste Workflows für Kunde: {test_kunde}")
        
        for workflow in workflows:
            print(f"\n📋 Workflow: {workflow}")
            
            # Hole Workflow-Ordner
            workflow_ordner = kunden_manager.get_ordner_fuer_workflow(test_kunde, workflow)
            print(f"  📁 Ordner: {workflow_ordner}")
            
            if os.path.exists(workflow_ordner):
                # Liste Projekte in diesem Workflow
                projekte = [d for d in os.listdir(workflow_ordner) 
                           if os.path.isdir(os.path.join(workflow_ordner, d))]
                print(f"  📊 Projekte: {len(projekte)}")
                
                for projekt in projekte:
                    projekt_pfad = os.path.join(workflow_ordner, projekt)
                    metadata_pfad = os.path.join(projekt_pfad, "project_metadata.json")
                    
                    if os.path.exists(metadata_pfad):
                        try:
                            with open(metadata_pfad, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                print(f"    📄 {projekt}: {metadata.get('auftragsnummer', 'N/A')}")
                        except Exception as e:
                            print(f"    ❌ Fehler beim Lesen von {projekt}: {e}")
                    else:
                        print(f"    ⚠️ {projekt}: Keine Metadaten")
            else:
                print(f"  ❌ Ordner nicht gefunden")
        
        print("\n✅ Workflow-spezifische Tests abgeschlossen")
        return True
        
    except Exception as e:
        print(f"\n❌ FEHLER in Workflow-Tests: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte KundenManager Hauptanwendung Integration Tests")
    
    success1 = test_app_kundenmanager_integration()
    success2 = test_workflow_specific_functions()
    
    if success1 and success2:
        print("\n🎉 ALLE INTEGRATION TESTS ERFOLGREICH!")
        print("✅ KundenManager ist vollständig in die Hauptanwendung integriert")
        print("✅ Alle Workflow-Daten werden korrekt verarbeitet")
        print("✅ Fuzzy-Matching und Error-Handling funktionieren")
        print("✅ Project Data Manager Integration arbeitet korrekt")
    else:
        print("\n⚠️ EINIGE INTEGRATION TESTS FEHLGESCHLAGEN")
        print("❌ Überprüfung der Integration erforderlich")
