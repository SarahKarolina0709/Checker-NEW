#!/usr/bin/env python3
"""
Test für die neue KundenManagerV2 Struktur
"""

import os
import tempfile
import shutil
from kunden_manager_v2 import KundenManagerV2

def test_neue_struktur():
    """Test der neuen projekt-zentrierten Struktur"""
    
    print("🧪 Testing neue Kunden-Struktur (V2)")
    print("=" * 50)
    
    # Temporärer Ordner für Tests
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = KundenManagerV2(temp_dir)
        
        # Test 1: Kunde erstellen
        print("\n1. Kunde erstellen...")
        kunde = "Mustermann GmbH"
        manager.erstelle_kundenstruktur(kunde)
        print(f"✅ Kunde '{kunde}' erstellt")
        
        # Test 2: Erstes Projekt erstellen
        print("\n2. Erstes Projekt erstellen...")
        projekt1 = manager.erstelle_projekt_ordner(kunde, "Website_Übersetzung")
        print(f"✅ Projekt 1 erstellt: {os.path.basename(projekt1)}")
        
        # Test 3: Zweites Projekt am gleichen Tag
        print("\n3. Zweites Projekt erstellen...")
        projekt2 = manager.erstelle_projekt_ordner(kunde, "Broschüre_Englisch")
        print(f"✅ Projekt 2 erstellt: {os.path.basename(projekt2)}")
        
        # Test 4: Projekte auflisten
        print("\n4. Projekte auflisten...")
        projekte = manager.liste_kundenprojekte(kunde)
        print(f"✅ Gefundene Projekte: {projekte}")
        
        # Test 5: Workflow-Ordner testen
        print("\n5. Workflow-Ordner testen...")
        for projekt in projekte:
            for workflow in ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]:
                workflow_pfad = manager.get_projekt_workflow_ordner(kunde, projekt, workflow)
                exists = os.path.exists(workflow_pfad)
                print(f"  {workflow} in {projekt}: {'✅' if exists else '❌'}")
        
        # Test 6: Struktur anzeigen
        print("\n6. Ordnerstruktur:")
        kunde_pfad = manager.kunden_ordner(kunde)
        print_directory_structure(kunde_pfad, "  ")
        
        # Test 7: Neuestes Projekt
        print("\n7. Neuestes Projekt:")
        neuestes = manager.get_neuestes_projekt(kunde)
        print(f"✅ Neuestes Projekt: {neuestes}")
        
        print("\n✅ Alle Tests erfolgreich!")
        return True

def print_directory_structure(path, prefix=""):
    """Hilfsfunktion zum Anzeigen der Ordnerstruktur"""
    if not os.path.exists(path):
        return
    
    items = sorted(os.listdir(path))
    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        
        if os.path.isdir(item_path):
            print(f"{prefix}{'└── ' if is_last else '├── '}{item}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_structure(item_path, next_prefix)
        else:
            print(f"{prefix}{'└── ' if is_last else '├── '}{item}")

def test_migration():
    """Test der Migration von alter zu neuer Struktur"""
    
    print("\n🔄 Testing Migration von alter zu neuer Struktur")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Erstelle alte Struktur
        kunde = "Migration_Test"
        alte_struktur = os.path.join(temp_dir, kunde)
        os.makedirs(alte_struktur)
        
        # Erstelle alte Workflow-Ordner
        for workflow in ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]:
            workflow_pfad = os.path.join(alte_struktur, workflow)
            os.makedirs(workflow_pfad)
            # Erstelle Dummy-Datei
            with open(os.path.join(workflow_pfad, "test.txt"), "w") as f:
                f.write(f"Test-Datei für {workflow}")
        
        print("✅ Alte Struktur erstellt")
        
        # Initialisiere neuen Manager
        manager = KundenManagerV2(temp_dir)
        
        # Migration durchführen
        success = manager.migrate_from_old_structure(kunde)
        print(f"✅ Migration {'erfolgreich' if success else 'fehlgeschlagen'}")
        
        # Neue Struktur überprüfen
        projekte = manager.liste_kundenprojekte(kunde)
        print(f"✅ Projekte nach Migration: {projekte}")
        
        # Struktur anzeigen
        print("\n7. Neue Struktur nach Migration:")
        kunde_pfad = manager.kunden_ordner(kunde)
        print_directory_structure(kunde_pfad, "  ")
        
        return success

def test_rückwärtskompatibilität():
    """Test der Rückwärtskompatibilität"""
    
    print("\n🔄 Testing Rückwärtskompatibilität")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = KundenManagerV2(temp_dir)
        
        kunde = "Kompatibilitäts_Test"
        
        # Test alte API
        print("1. Test alte API (neuer_anfrage_ordner)...")
        angebot_ordner = manager.neuer_anfrage_ordner(kunde, "Angebot", "Test_Projekt")
        print(f"✅ Angebot-Ordner: {angebot_ordner}")
        
        # Test get_ordner_fuer_workflow
        print("2. Test get_ordner_fuer_workflow...")
        pruefung_ordner = manager.get_ordner_fuer_workflow(kunde, "Pruefung")
        print(f"✅ Prüfung-Ordner: {pruefung_ordner}")
        
        # Struktur anzeigen
        print("\n3. Struktur nach Rückwärtskompatibilitäts-Test:")
        kunde_pfad = manager.kunden_ordner(kunde)
        print_directory_structure(kunde_pfad, "  ")
        
        return True

if __name__ == "__main__":
    try:
        test_neue_struktur()
        test_migration()
        test_rückwärtskompatibilität()
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
    except Exception as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
