#!/usr/bin/env python3
"""
Test für das Kundenmanagement-System
"""

import os
import sys

# Workspace-Pfad hinzufügen
workspace_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, workspace_path)

try:
    from kunden_manager import KundenManager
    
    print("=== Kundenmanagement Test ===")
    
    # KundenManager initialisieren
    manager = KundenManager(base_dir="Checker_Projekte")
    print(f"Base Directory: {manager.base_dir}")
    print(f"Base Directory exists: {os.path.exists(manager.base_dir)}")
    
    print("\n1. Teste Kundenstruktur-Erstellung:")
    kunde_test = "Test_Kunde_GmbH"
    kundenpfad = manager.erstelle_kundenstruktur(kunde_test)
    print(f"   Kunde '{kunde_test}' erstellt: {kundenpfad}")
    print(f"   Pfad existiert: {os.path.exists(kundenpfad)}")
    
    print("\n2. Teste Unterordner:")
    unterordner = manager.kunden_unterordner(kunde_test)
    print(f"   Unterordner: {unterordner}")
    
    print("\n3. Teste Workflow-Ordner:")
    angebot_pfad = manager.get_ordner_fuer_workflow(kunde_test, "Angebot")
    print(f"   Angebot-Ordner: {angebot_pfad}")
    print(f"   Existiert: {os.path.exists(angebot_pfad)}")
    
    print("\n4. Teste Projekt-Ordner-Erstellung:")
    projekt_pfad = manager.neuer_anfrage_ordner(kunde_test, "Angebot", "Website_Übersetzung")
    print(f"   Projekt-Ordner: {projekt_pfad}")
    print(f"   Existiert: {os.path.exists(projekt_pfad)}")
    
    print("\n5. Teste Kundenliste:")
    alle_kunden = manager.alle_kunden()
    print(f"   Alle Kunden: {alle_kunden}")
    
    print("\n6. Teste Fuzzy-Matching:")
    fuzzy_result = manager.fuzzy_kundenname_suche("test kunde")
    print(f"   Fuzzy-Match für 'test kunde': {fuzzy_result}")
    
    print("\n7. Directory-Struktur:")
    if os.path.exists(kundenpfad):
        for root, dirs, files in os.walk(kundenpfad):
            level = root.replace(kundenpfad, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"   {indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"   {subindent}{file}")
    
except Exception as e:
    print(f"Fehler beim Test: {e}")
    import traceback
    traceback.print_exc()
