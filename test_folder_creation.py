"""
Test für die Ordnerstruktur-Erstellung mit KundenManagerV2
"""

import os
import shutil
from datetime import datetime
from kunden_manager_v2 import KundenManagerV2

def test_projekt_ordner_erstellung():
    """Test die Erstellung von Projektordnern"""
    print("🔍 Teste Projektordner-Erstellung...")
    
    # Erstelle Test-Verzeichnis
    test_dir = "Test_Checker_Projekte"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Initialisiere KundenManagerV2
    km = KundenManagerV2(test_dir)
    
    # Test 1: Erstelle Projekt für neuen Kunden
    print("\n📋 Test 1: Neuer Kunde + Projekt")
    kunde_name = "Test_Kunde_AG"
    projekt_name = "Website_Redesign"
    
    result = km.erstelle_projekt_ordner(
        kundenname=kunde_name,
        projektname=projekt_name,
        datum="2025-01-20"
    )
    
    if result:
        projekt_pfad, projekt_id = result
        print(f"✅ Projekt erstellt: {projekt_id}")
        print(f"📁 Pfad: {projekt_pfad}")
        
        # Prüfe ob alle Workflow-Ordner existieren
        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        for workflow in workflows:
            workflow_pfad = os.path.join(projekt_pfad, workflow)
            if os.path.exists(workflow_pfad):
                print(f"   ✅ {workflow} Ordner erstellt")
            else:
                print(f"   ❌ {workflow} Ordner fehlt!")
    else:
        print("❌ Projekt konnte nicht erstellt werden")
    
    # Test 2: Erstelle zweites Projekt für denselben Kunden
    print("\n📋 Test 2: Zweites Projekt für denselben Kunden")
    result2 = km.erstelle_projekt_ordner(
        kundenname=kunde_name,
        projektname="Logo_Design",
        datum="2025-01-21"
    )
    
    if result2:
        projekt_pfad2, projekt_id2 = result2
        print(f"✅ Zweites Projekt erstellt: {projekt_id2}")
        print(f"📁 Pfad: {projekt_pfad2}")
    else:
        print("❌ Zweites Projekt konnte nicht erstellt werden")
    
    # Test 3: Liste alle Projekte des Kunden
    print("\n📋 Test 3: Alle Projekte des Kunden")
    projekte = km.liste_kundenprojekte(kunde_name)
    print(f"📊 Gefundene Projekte: {len(projekte)}")
    for projekt in projekte:
        print(f"   📋 {projekt}")
    
    # Test 4: Prüfe Ordnerstruktur
    print(f"\n📋 Test 4: Prüfe Ordnerstruktur in {test_dir}")
    def print_tree(directory, prefix="", is_last=True):
        if not os.path.exists(directory):
            print(f"{prefix}❌ {directory} (nicht gefunden)")
            return
        
        items = sorted(os.listdir(directory))
        for i, item in enumerate(items):
            item_path = os.path.join(directory, item)
            is_last_item = i == len(items) - 1
            
            if os.path.isdir(item_path):
                print(f"{prefix}{'└── ' if is_last_item else '├── '}{item}/")
                extension = "    " if is_last_item else "│   "
                print_tree(item_path, prefix + extension, is_last_item)
            else:
                print(f"{prefix}{'└── ' if is_last_item else '├── '}{item}")
    
    print_tree(test_dir)
    
    print(f"\n🎉 Test abgeschlossen! Test-Verzeichnis: {test_dir}")
    
    # Cleanup
    cleanup = input("\n❓ Test-Verzeichnis löschen? (y/n): ").lower()
    if cleanup == 'y':
        shutil.rmtree(test_dir)
        print("🧹 Test-Verzeichnis gelöscht")

if __name__ == "__main__":
    test_projekt_ordner_erstellung()
