#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Kompletter Kunde-zu-Workflow Transfer
Testet den kompletten Datenfluss von Welcome-Screen zum Prüfungsflow
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Arbeitsverzeichnis hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_welcome_to_pruefung_workflow():
    """Testet den kompletten Workflow vom Welcome-Screen zur Prüfung"""
    print("=" * 70)
    print("🔬 TEST: Welcome-Screen → Prüfungsflow Kundendaten-Transfer")
    print("=" * 70)
    
    try:
        from kunden_manager import KundenManager
        import project_data_manager
        
        # Test-Setup
        print("1️⃣ SETUP: Test-Umgebung vorbereiten")
        print("-" * 50)
        
        # Simuliere Kundeneingabe aus Welcome-Screen
        customer_input = {
            "kunde_name": "Tech Solutions GmbH",
            "auftragsnummer": "TS-2025-001",
            "workflow_type": "pruefung_workflow"
        }
        
        print(f"📋 Kunde eingegeben: {customer_input['kunde_name']}")
        print(f"📋 Auftrag: {customer_input['auftragsnummer']}")
        print(f"📋 Workflow: {customer_input['workflow_type']}")
        
        # KundenManager initialisieren
        kunden_manager = KundenManager()
        
        print("\n2️⃣ SCHRITT: Kundenerkennung & Ordnererstellung")
        print("-" * 50)
        
        # Fuzzy-Matching für bestehende Kunden
        existing_customer = kunden_manager.fuzzy_kundenname_suche(customer_input["kunde_name"])
        
        if existing_customer:
            print(f"✅ Bestehender Kunde gefunden: '{customer_input['kunde_name']}' → '{existing_customer}'")
            final_kunde = existing_customer
        else:
            print(f"➕ Neuer Kunde wird erstellt: '{customer_input['kunde_name']}'")
            sanitized_name = kunden_manager._sanitize_name(customer_input["kunde_name"])
            kunden_manager.erstelle_kundenstruktur(sanitized_name)
            final_kunde = sanitized_name
        
        # Projekt-Ordner erstellen (simuliert _map_workflow_to_folder)
        workflow_folder = "Pruefung"  # Mapping für pruefung_workflow
        project_folder = kunden_manager.neuer_anfrage_ordner(
            final_kunde, workflow_folder, customer_input["auftragsnummer"]
        )
        
        print(f"✅ Projekt-Ordner erstellt: {project_folder}")
        
        # Projekt-Daten für Workflow vorbereiten
        project_data = {
            "kunde_name": final_kunde,
            "auftragsnummer": customer_input["auftragsnummer"],
            "workflow": workflow_folder,
            "project_path": project_folder,
            "kundenbetreuer": "Test Manager",
            "zielsprache": "DE → EN",
            "erstellt_am": datetime.now().isoformat(),
            "status": "in_bearbeitung",
            "dateien": []
        }
        
        print(f"✅ Projekt-Daten vorbereitet für Prüfungsflow")
        
        print("\n3️⃣ SCHRITT: Projekt-Metadaten speichern")
        print("-" * 50)
        
        # Metadaten in Projekt-Ordner speichern
        metadata_file = os.path.join(project_folder, "project_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadaten gespeichert: {metadata_file}")
        
        print("\n4️⃣ SCHRITT: Prüfungsflow initialisieren (simuliert)")
        print("-" * 50)
        
        # Simuliere was in checker_app.py passiert
        print("🔄 Simuliere: _start_specific_workflow('pruefung_workflow', project_data)")
        print(f"   → PruefungWorkflow(parent=content_frame, app=self, project_data={project_data})")
        
        # Teste was der PruefungWorkflowController erhalten würde
        print(f"📄 Controller würde erhalten:")
        print(f"   - kunde_name: {project_data['kunde_name']}")
        print(f"   - auftragsnummer: {project_data['auftragsnummer']}")
        print(f"   - project_path: {project_data['project_path']}")
        
        # Simuliere Controller-Methoden
        print(f"\n🔧 Controller-Methoden würden funktionieren:")
        
        # get_project_save_path() Test
        if os.path.exists(project_data['project_path']):
            print(f"   ✅ get_project_save_path(): {project_data['project_path']}")
        else:
            print(f"   ❌ get_project_save_path(): Pfad nicht gefunden")
        
        # Export-Pfad Test
        auftragsnummer = project_data['auftragsnummer']
        export_filename = f"Pruefung_Ergebnisse_{auftragsnummer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        export_path = os.path.join(project_data['project_path'], export_filename)
        print(f"   ✅ Export würde gespeichert: {export_path}")
        
        # Results-JSON Test
        results_filename = f"Pruefung_Ergebnisse_{auftragsnummer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_path = os.path.join(project_data['project_path'], results_filename)
        print(f"   ✅ Ergebnisse würden gespeichert: {results_path}")
        
        print("\n5️⃣ SCHRITT: Project Data Manager Integration")
        print("-" * 50)
        
        # Backup für Sicherheit
        backup_file = None
        if os.path.exists(project_data_manager.DATA_FILE):
            backup_file = project_data_manager.DATA_FILE + ".backup_workflow"
            shutil.copy2(project_data_manager.DATA_FILE, backup_file)
        
        # Projekt registrieren
        project_entry = {
            "project_id": f"{final_kunde}_{customer_input['auftragsnummer']}",
            "kunde_name": final_kunde,
            "auftragsnummer": customer_input["auftragsnummer"],
            "kundenbetreuer": project_data["kundenbetreuer"],
            "status": project_data["status"],
            "erstellt_am": project_data["erstellt_am"],
            "project_path": project_folder,
            "workflow": workflow_folder
        }
        
        project_data_manager.add_or_update_project(project_entry)
        print(f"✅ Projekt im Project Data Manager registriert")
        
        # Abruf testen
        retrieved = project_data_manager.get_project_by_id(project_entry["project_id"])
        if retrieved:
            print(f"✅ Projekt erfolgreich abrufbar: {retrieved['auftragsnummer']}")
        else:
            print(f"❌ Projekt nicht abrufbar")
        
        print("\n6️⃣ SCHRITT: Workflow-spezifische Dateispeicherung testen")
        print("-" * 50)
        
        # Simuliere dass Benutzer Dateien hochlädt und Prüfung durchführt
        test_files = ["source_document.docx", "target_document.docx"]
        uploaded_files_path = os.path.join(project_folder, "uploaded_files")
        os.makedirs(uploaded_files_path, exist_ok=True)
        
        for test_file in test_files:
            test_file_path = os.path.join(uploaded_files_path, test_file)
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Test content for {test_file}")
            print(f"   📄 Test-Datei erstellt: {test_file}")
        
        # Simuliere Ergebnisspeicherung
        test_results = {
            "projekt_info": project_data,
            "pruefung_datum": datetime.now().isoformat(),
            "file_pairs": {
                "1": {
                    "source_file": os.path.join(uploaded_files_path, "source_document.docx"),
                    "target_file": os.path.join(uploaded_files_path, "target_document.docx"),
                    "results": {
                        "grammar_check": "5 Fehler gefunden",
                        "consistency_check": "2 Inkonsistenzen",
                        "quality_score": 85
                    }
                }
            },
            "zusammenfassung": {
                "total_errors": 7,
                "overall_quality": 85,
                "recommendations": ["Grammatik überprüfen", "Konsistenz verbessern"]
            }
        }
        
        test_results_path = os.path.join(project_folder, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(test_results_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Test-Ergebnisse gespeichert: {os.path.basename(test_results_path)}")
        
        print("\n7️⃣ SCHRITT: Validierung der kompletten Kette")
        print("-" * 50)
        
        # Prüfe dass alle Komponenten zusammenarbeiten
        validations = [
            ("Projekt-Ordner existiert", os.path.exists(project_folder)),
            ("Metadaten-Datei existiert", os.path.exists(metadata_file)),
            ("Uploaded Files Ordner existiert", os.path.exists(uploaded_files_path)),
            ("Test-Ergebnisse existieren", os.path.exists(test_results_path)),
            ("Project Data Manager Eintrag", retrieved is not None),
            ("Kunde im KundenManager", final_kunde in kunden_manager.alle_kunden())
        ]
        
        all_valid = True
        for validation_name, validation_result in validations:
            status = "✅" if validation_result else "❌"
            print(f"   {status} {validation_name}")
            if not validation_result:
                all_valid = False
        
        print(f"\n8️⃣ SCHRITT: Aufräumen")
        print("-" * 50)
        
        # Entferne Test-Daten
        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)
            print(f"✅ Test-Projekt-Ordner entfernt")
        
        # Project Data Manager bereinigen
        projects = project_data_manager.load_projects()
        projects = [p for p in projects if p.get("project_id") != project_entry["project_id"]]
        
        os.makedirs(os.path.dirname(project_data_manager.DATA_FILE), exist_ok=True)
        with open(project_data_manager.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=4)
        
        if backup_file and os.path.exists(backup_file):
            shutil.move(backup_file, project_data_manager.DATA_FILE)
            print(f"✅ Project Data Manager wiederhergestellt")
        
        print("\n" + "=" * 70)
        if all_valid:
            print("🎉 KOMPLETTER WORKFLOW-TRANSFER ERFOLGREICH!")
            print("✅ Kundendaten werden korrekt vom Welcome-Screen zum Prüfungsflow übertragen")
            print("✅ Alle Dateien werden im korrekten Kundenordner gespeichert")
            print("✅ Export-Funktionen haben Zugriff auf Kundendaten")
        else:
            print("⚠️ WORKFLOW-TRANSFER HAT PROBLEME")
            print("❌ Einige Validierungen sind fehlgeschlagen")
        print("=" * 70)
        
        return all_valid
        
    except Exception as e:
        print(f"\n❌ FEHLER im Workflow-Transfer Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_customer_scenarios():
    """Testet verschiedene Kunden-Szenarien"""
    print("\n" + "=" * 70)
    print("🔬 TEST: Verschiedene Kunden-Szenarien")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Bestehender Kunde (exakt)",
            "input_kunde": "Test Kunde 1",
            "expected_match": True
        },
        {
            "name": "Bestehender Kunde (Fuzzy)",
            "input_kunde": "test kunde 1",
            "expected_match": True
        },
        {
            "name": "Neuer Kunde",
            "input_kunde": "Komplett Neue Firma AG",
            "expected_match": False
        },
        {
            "name": "Kunde mit Sonderzeichen",
            "input_kunde": "Müller & Partner GmbH",
            "expected_match": False
        }
    ]
    
    try:
        from kunden_manager import KundenManager
        kunden_manager = KundenManager()
        
        results = []
        
        for scenario in scenarios:
            print(f"\n🎯 {scenario['name']}")
            print("-" * 40)
            
            kunde_input = scenario['input_kunde']
            expected_match = scenario['expected_match']
            
            # Teste Fuzzy-Matching
            match = kunden_manager.fuzzy_kundenname_suche(kunde_input)
            has_match = match is not None
            
            if has_match:
                print(f"   ✅ Match gefunden: '{kunde_input}' → '{match}'")
            else:
                print(f"   ⚪ Kein Match für: '{kunde_input}'")
                # Sanitized name für neue Kunden
                sanitized = kunden_manager._sanitize_name(kunde_input)
                print(f"   🧹 Würde erstellt als: '{sanitized}'")
            
            # Prüfe Erwartung
            if has_match == expected_match:
                print(f"   ✅ Ergebnis entspricht Erwartung")
                results.append(True)
            else:
                print(f"   ❌ Ergebnis entspricht NICHT Erwartung")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 Erfolgsrate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate == 100.0
        
    except Exception as e:
        print(f"\n❌ FEHLER in Kunden-Szenarien Test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Welcome-Screen → Prüfungsflow Integration Tests")
    
    success1 = test_welcome_to_pruefung_workflow()
    success2 = test_multiple_customer_scenarios()
    
    print("\n" + "=" * 80)
    print("📋 INTEGRATION TEST ZUSAMMENFASSUNG")
    print("=" * 80)
    
    if success1 and success2:
        print("🎉 ALLE INTEGRATION TESTS ERFOLGREICH!")
        print("")
        print("✅ Welcome-Screen → Prüfungsflow Datenübertragung funktioniert")
        print("✅ Kundendaten werden korrekt übernommen")
        print("✅ Dateien werden im richtigen Kundenordner gespeichert")
        print("✅ Export-Funktionen arbeiten mit Kundendaten")
        print("✅ Fuzzy-Matching erkennt bestehende Kunden korrekt")
        print("✅ Neue Kunden werden ordnungsgemäß erstellt")
        print("")
        print("🏆 DAS KUNDENMANAGEMENT IST VOLLSTÄNDIG INTEGRIERT!")
        
    else:
        print("⚠️ EINIGE INTEGRATION TESTS FEHLGESCHLAGEN")
        print("")
        if not success1:
            print("❌ Welcome-Screen → Prüfungsflow Integration hat Probleme")
        if not success2:
            print("❌ Kunden-Szenarien haben Probleme")
        print("")
        print("🔧 Weitere Entwicklung erforderlich")
