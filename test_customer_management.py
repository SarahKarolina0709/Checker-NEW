#!/usr/bin/env python3
"""
Test Customer Management Functionality
=====================================
Demonstriert die Kundenmanagement-Funktionen und Ordnererstellung.
"""

import os
import shutil
from kunden_manager import KundenManager

def test_customer_management():
    """Test der grundlegenden Kundenmanagement-Funktionen."""
    
    print("=== Customer Management Test ===")
    
    # Erstelle einen temporären Test-Ordner
    test_base_dir = "Test_Checker_Projekte"
    
    # Bereinige vorherige Tests
    if os.path.exists(test_base_dir):
        shutil.rmtree(test_base_dir)
    
    # Initialisiere KundenManager
    manager = KundenManager(base_dir=test_base_dir)
    
    print(f"✓ KundenManager initialisiert mit Basis-Ordner: {test_base_dir}")
    print(f"✓ Basis-Ordner existiert: {os.path.exists(test_base_dir)}")
    
    # Test 1: Neuen Kunden erstellen
    print("\n--- Test 1: Neuen Kunden erstellen ---")
    kunde1 = "TechCorp GmbH"
    success = manager.neuer_kunde(kunde1)
    print(f"✓ Kunde '{kunde1}' erstellt: {success}")
    
    # Prüfe Ordnerstruktur
    kunde_pfad = manager.kunden_ordner(kunde1)
    print(f"✓ Kundenpfad: {kunde_pfad}")
    print(f"✓ Kunde-Ordner existiert: {os.path.exists(kunde_pfad)}")
    
    # Prüfe Unterordner
    unterordner = manager.kunden_unterordner(kunde1)
    print(f"✓ Unterordner: {unterordner}")
    
    erwartete_ordner = ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]
    for ordner in erwartete_ordner:
        ordner_pfad = os.path.join(kunde_pfad, ordner)
        exists = os.path.exists(ordner_pfad)
        print(f"  - {ordner}: {exists}")
    
    # Test 2: Weitere Kunden erstellen
    print("\n--- Test 2: Weitere Kunden erstellen ---")
    weitere_kunden = ["Global Solutions", "StartUp Innovation", "Müller & Co"]
    
    for kunde in weitere_kunden:
        success = manager.neuer_kunde(kunde)
        print(f"✓ Kunde '{kunde}' erstellt: {success}")
    
    # Test 3: Alle Kunden anzeigen
    print("\n--- Test 3: Alle Kunden anzeigen ---")
    alle_kunden = manager.alle_kunden()
    print(f"✓ Anzahl Kunden: {len(alle_kunden)}")
    for kunde in alle_kunden:
        print(f"  - {kunde}")
    
    # Test 4: Fuzzy-Suche testen
    print("\n--- Test 4: Fuzzy-Suche testen ---")
    suchbegriffe = ["TechCorp", "Global", "Startup", "Mueller"]
    
    for begriff in suchbegriffe:
        gefunden = manager.find_customer_fuzzy(begriff)
        print(f"✓ Suche '{begriff}' -> '{gefunden}'")
    
    # Test 5: Kunde existiert prüfen
    print("\n--- Test 5: Kunde existiert prüfen ---")
    test_namen = ["TechCorp GmbH", "Unbekannter Kunde", "Global Solutions"]
    
    for name in test_namen:
        exists, match = manager.customer_exists(name)
        print(f"✓ Kunde '{name}' existiert: {exists} (Match: {match})")
    
    # Test 6: Projektstruktur erstellen
    print("\n--- Test 6: Projektstruktur erstellen ---")
    projekt_name = "Website Redesign"
    
    projekt_pfad = manager.erstelle_projektstruktur(kunde1, projekt_name)
    print(f"✓ Projekt '{projekt_name}' für '{kunde1}' erstellt")
    print(f"✓ Projekt-Pfad: {projekt_pfad}")
    print(f"✓ Projekt-Ordner existiert: {os.path.exists(projekt_pfad)}")
    
    # Prüfe Projekt-Ordner in allen Workflows
    workflows = ["Angebot", "Pruefung", "Finalisierung"]
    for workflow in workflows:
        workflow_projekt_pfad = os.path.join(
            manager.get_ordner_fuer_workflow(kunde1, workflow),
            manager._sanitize_name(projekt_name)
        )
        exists = os.path.exists(workflow_projekt_pfad)
        print(f"  - {workflow}: {exists}")
    
    # Test 7: Anfrage-Ordner erstellen
    print("\n--- Test 7: Anfrage-Ordner erstellen ---")
    
    anfrage_pfad = manager.neuer_anfrage_ordner(kunde1, "Angebot", "Mobile App")
    print(f"✓ Anfrage-Ordner erstellt: {anfrage_pfad}")
    print(f"✓ Anfrage-Ordner existiert: {os.path.exists(anfrage_pfad)}")
    
    # Test 8: Ordnerstruktur anzeigen
    print("\n--- Test 8: Ordnerstruktur anzeigen ---")
    
    def zeige_ordnerstruktur(pfad, level=0):
        """Zeigt die Ordnerstruktur rekursiv an."""
        indent = "  " * level
        if os.path.exists(pfad):
            print(f"{indent}{os.path.basename(pfad)}/")
            if os.path.isdir(pfad):
                for item in sorted(os.listdir(pfad)):
                    item_pfad = os.path.join(pfad, item)
                    if os.path.isdir(item_pfad):
                        zeige_ordnerstruktur(item_pfad, level + 1)
                    else:
                        print(f"{indent}  {item}")
    
    print("Gesamte Ordnerstruktur:")
    zeige_ordnerstruktur(test_base_dir)
    
    print("\n=== Test abgeschlossen ===")
    print(f"Test-Ordner: {os.path.abspath(test_base_dir)}")
    print("Sie können die erstellten Ordner im Datei-Explorer überprüfen.")

if __name__ == "__main__":
    test_customer_management()
