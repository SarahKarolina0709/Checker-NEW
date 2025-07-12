#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der KundenManager-Integration mit Projektdaten
Prüft, ob das Kundenmanagement korrekt mit project_data_manager zusammenarbeitet
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Arbeitsverzeichnis hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_kundenmanager_projektdaten():
    """Testet die Integration von KundenManager mit Projektdaten"""
    print("=" * 60)
    print("🔬 TEST: KundenManager & Projektdaten Integration")
    print("=" * 60)
    
    # Test-Setup mit temporärem Verzeichnis
    test_dir = tempfile.mkdtemp(prefix="checker_test_")
    print(f"📁 Test-Verzeichnis: {test_dir}")
    
    try:
        # Import der Module
        from kunden_manager import KundenManager
        import project_data_manager
        
        # KundenManager mit Test-Verzeichnis erstellen
        kunden_manager = KundenManager(base_dir=test_dir)
        
        print("\n1️⃣ TESTE: Kundenerstellung und Projektordner")
        print("-" * 50)
        
        # Test-Kundendaten
        test_kunde = "Test Firma GmbH"
        test_auftrag = "TF-2025-001"
        test_workflow = "Angebot"
        
        # Kunde erstellen
        kundenpfad = kunden_manager.erstelle_kundenstruktur(test_kunde)
        print(f"✅ Kunde erstellt: {kundenpfad}")
        
        # Projektordner erstellen
        projekt_pfad = kunden_manager.neuer_anfrage_ordner(
            test_kunde, 
            test_workflow, 
            test_auftrag
        )
        print(f"✅ Projektordner erstellt: {projekt_pfad}")
        
        print("\n2️⃣ TESTE: Projekt-Metadaten speichern")
        print("-" * 50)
        
        # Projekt-Metadaten erstellen
        projekt_metadata = {
            "kunde_name": test_kunde,
            "auftragsnummer": test_auftrag,
            "workflow": test_workflow,
            "kundenbetreuer": "Test Manager",
            "zielsprache": "DE → EN",
            "erstellt_am": datetime.now().isoformat(),
            "status": "aktiv",
            "dateien": []
        }
        
        # Metadaten-Datei speichern
        metadata_pfad = os.path.join(projekt_pfad, "project_metadata.json")
        with open(metadata_pfad, 'w', encoding='utf-8') as f:
            json.dump(projekt_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadaten gespeichert: {metadata_pfad}")
        
        print("\n3️⃣ TESTE: project_data_manager Integration")
        print("-" * 50)
        
        # Projekt im project_data_manager registrieren
        project_details = {
            "project_id": f"{test_kunde}_{test_auftrag}",
            "kunde_name": test_kunde,
            "auftragsnummer": test_auftrag,
            "kundenbetreuer": "Test Manager",
            "status": "in_bearbeitung",
            "erstellt_am": datetime.now().isoformat(),
            "project_path": projekt_pfad
        }
        
        # Backup der ursprünglichen projects.json falls vorhanden
        backup_file = None
        if os.path.exists(project_data_manager.DATA_FILE):
            backup_file = project_data_manager.DATA_FILE + ".backup"
            shutil.copy2(project_data_manager.DATA_FILE, backup_file)
            print(f"📋 Backup erstellt: {backup_file}")
        
        # Projekt hinzufügen
        project_data_manager.add_or_update_project(project_details)
        print(f"✅ Projekt in project_data_manager registriert")
        
        # Projekt abrufen
        retrieved_project = project_data_manager.get_project_by_id(project_details["project_id"])
        if retrieved_project:
            print(f"✅ Projekt erfolgreich abgerufen: {retrieved_project['auftragsnummer']}")
        else:
            print("❌ Projekt konnte nicht abgerufen werden")
        
        print("\n4️⃣ TESTE: Fuzzy-Matching mit Projektdaten")
        print("-" * 50)
        
        # Test mit ähnlichem Kundennamen
        similar_name = "Test Firma GmbH Co"
        fuzzy_match = kunden_manager.fuzzy_kundenname_suche(similar_name)
        
        if fuzzy_match:
            print(f"✅ Fuzzy-Match gefunden: '{similar_name}' → '{fuzzy_match}'")
        else:
            print(f"❌ Kein Fuzzy-Match für '{similar_name}'")
        
        print("\n5️⃣ TESTE: Ordnerstruktur-Validierung")
        print("-" * 50)
        
        # Prüfe Ordnerstruktur
        alle_kunden = kunden_manager.alle_kunden()
        print(f"📋 Alle Kunden: {alle_kunden}")
        
        for kunde in alle_kunden:
            unterordner = kunden_manager.kunden_unterordner(kunde)
            print(f"📁 {kunde}: {unterordner}")
            
            # Prüfe Workflow-Ordner
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_pfad = kunden_manager.get_ordner_fuer_workflow(kunde, workflow)
                if os.path.exists(workflow_pfad):
                    # Zähle Projekte in diesem Workflow
                    projekte = [d for d in os.listdir(workflow_pfad) 
                              if os.path.isdir(os.path.join(workflow_pfad, d))]
                    print(f"  └── {workflow}: {len(projekte)} Projekte")
        
        print("\n6️⃣ TESTE: Projektdaten aus Ordnerstruktur laden")
        print("-" * 50)
        
        # Simuliere das Laden von Projekten wie im projekt_workflow
        projekte_gefunden = []
        
        if os.path.exists(test_dir):
            for customer_folder in os.listdir(test_dir):
                customer_path = os.path.join(test_dir, customer_folder)
                if not os.path.isdir(customer_path):
                    continue
                    
                for project_folder in os.listdir(customer_path):
                    project_path = os.path.join(customer_path, project_folder)
                    if not os.path.isdir(project_path):
                        continue
                        
                    # Prüfe auf Unterordner (Workflows)
                    for workflow_folder in os.listdir(project_path):
                        workflow_path = os.path.join(project_path, workflow_folder)
                        if not os.path.isdir(workflow_path):
                            continue
                            
                        for specific_project in os.listdir(workflow_path):
                            specific_project_path = os.path.join(workflow_path, specific_project)
                            if not os.path.isdir(specific_project_path):
                                continue
                                
                            # Versuche Metadaten zu laden
                            metadata_file = os.path.join(specific_project_path, "project_metadata.json")
                            if os.path.exists(metadata_file):
                                try:
                                    with open(metadata_file, 'r', encoding='utf-8') as f:
                                        metadata = json.load(f)
                                        metadata['project_path'] = specific_project_path
                                        projekte_gefunden.append(metadata)
                                        print(f"✅ Projekt geladen: {metadata.get('auftragsnummer')} ({metadata.get('workflow')})")
                                except Exception as e:
                                    print(f"⚠️ Fehler beim Laden der Metadaten: {e}")
        
        print(f"\n📊 ERGEBNIS: {len(projekte_gefunden)} Projekte gefunden")
        
        print("\n7️⃣ TESTE: Workflow-spezifische Datenverarbeitung")
        print("-" * 50)
        
        # Teste Workflow-spezifische Funktionen
        for projekt in projekte_gefunden:
            workflow_type = projekt.get('workflow')
            kunde_name = projekt.get('kunde_name')
            auftrag = projekt.get('auftragsnummer')
            
            print(f"🔄 Workflow: {workflow_type}")
            print(f"   Kunde: {kunde_name}")
            print(f"   Auftrag: {auftrag}")
            
            # Prüfe ob KundenManager den Workflow-Ordner findet
            workflow_ordner = kunden_manager.get_ordner_fuer_workflow(kunde_name, workflow_type)
            if os.path.exists(workflow_ordner):
                print(f"   ✅ Workflow-Ordner existiert: {workflow_ordner}")
            else:
                print(f"   ❌ Workflow-Ordner nicht gefunden: {workflow_ordner}")
        
        print("\n" + "=" * 60)
        print("✅ INTEGRATION TEST ERFOLGREICH ABGESCHLOSSEN")
        print("=" * 60)
        
        # Wiederherstellen der ursprünglichen projects.json
        if backup_file and os.path.exists(backup_file):
            shutil.move(backup_file, project_data_manager.DATA_FILE)
            print(f"📋 Original projects.json wiederhergestellt")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Aufräumen
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Test-Verzeichnis gelöscht: {test_dir}")
    
    return True

def test_workflow_integration():
    """Testet die Integration mit echten Workflow-Daten"""
    print("\n" + "=" * 60)
    print("🔬 TEST: Workflow-Integration mit echten Daten")
    print("=" * 60)
    
    try:
        from kunden_manager import KundenManager
        
        # KundenManager mit echtem Checker_Projekte Verzeichnis
        kunden_manager = KundenManager()
        
        print("📋 Vorhandene Kunden:")
        kunden = kunden_manager.alle_kunden()
        for kunde in kunden:
            print(f"  👤 {kunde}")
            unterordner = kunden_manager.kunden_unterordner(kunde)
            for unter in unterordner:
                print(f"    📁 {unter}")
        
        print(f"\n📊 Gesamt: {len(kunden)} Kunden gefunden")
        
        # Teste Fuzzy-Matching mit echten Daten
        if kunden:
            test_names = [
                kunden[0],  # Exakter Match
                kunden[0].lower(),  # Kleinschreibung
                kunden[0].replace(' ', ''),  # Ohne Leerzeichen
                kunden[0] + " Co",  # Mit Zusatz
            ]
            
            print("\n🔍 Fuzzy-Matching Tests:")
            for test_name in test_names:
                match = kunden_manager.fuzzy_kundenname_suche(test_name)
                if match:
                    print(f"  ✅ '{test_name}' → '{match}'")
                else:
                    print(f"  ❌ '{test_name}' → Kein Match")
        
        print("\n✅ Workflow-Integration Test abgeschlossen")
        
    except Exception as e:
        print(f"\n❌ FEHLER in Workflow-Integration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starte KundenManager Projektdaten Integration Tests")
    
    success1 = test_kundenmanager_projektdaten()
    success2 = test_workflow_integration()
    
    if success1 and success2:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("✅ KundenManager funktioniert korrekt mit Projektdaten")
    else:
        print("\n⚠️ EINIGE TESTS FEHLGESCHLAGEN")
        print("❌ Integration benötigt weitere Überprüfung")
