"""
Test-Skript für das erweiterte Upload-System
============================================

Dieses Skript demonstriert die neuen Features der Checker-App:
1. Automatische Dateiablage mit Datumsorganisation
2. Fuzzy-Matching für Kunden
3. Intelligente Kundenvorschläge
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Importiere die Module
from kunden_manager import KundenManager

def test_upload_system():
    """Testet das erweiterte Upload-System"""
    print("=" * 50)
    print("TEST: Erweiterte Upload-System")
    print("=" * 50)
    
    # Initialisiere den KundenManager
    manager = KundenManager("Test_Projekte")
    
    # Test 1: Bestehende Kunden anzeigen
    print("\n1. Bestehende Kunden:")
    kunden = manager.alle_kunden()
    for i, kunde in enumerate(kunden, 1):
        print(f"   {i}. {kunde}")
    
    # Test 2: Neuen Kunden anlegen
    print("\n2. Neuen Testkunden anlegen:")
    test_kunde = "Test_Firma_GmbH"
    pfad = manager.erstelle_kundenstruktur(test_kunde)
    print(f"   Kunde erstellt: {test_kunde}")
    print(f"   Pfad: {pfad}")
    
    # Test 3: Fuzzy-Matching testen
    print("\n3. Fuzzy-Matching testen:")
    
    # Exakte Übereinstimmung
    exact_match = manager.find_customer_fuzzy("Test_Firma_GmbH")
    print(f"   Exact 'Test_Firma_GmbH' → {exact_match}")
    
    # Ähnliche Namen
    fuzzy_tests = [
        "Test Firma",
        "TestFirma",
        "Test_Firma",
        "Test-Firma-GmbH",
        "test firma gmbh"
    ]
    
    for test_name in fuzzy_tests:
        match = manager.find_customer_fuzzy(test_name)
        print(f"   Fuzzy '{test_name}' → {match}")
    
    # Test 4: Dateiablage mit Datumsorganisation
    print("\n4. Dateiablage mit Datumsorganisation:")
    
    # Erstelle temporäre Testdateien
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test-Dateien erstellen
        test_files = [
            "Test_Firma_Angebot.pdf",
            "Dokument_001.docx",
            "Ausgangstexte_2025.txt"
        ]
        
        for filename in test_files:
            temp_file = os.path.join(temp_dir, filename)
            with open(temp_file, 'w') as f:
                f.write(f"Test-Inhalt für {filename}")
            
            # Datei mit Datumsorganisation speichern
            result = manager.speichere_datei_mit_datum(
                kundenname="Test_Firma_GmbH",
                workflow="Ausgangstexte", 
                datei_pfad=temp_file,
                projekt_name="Test_Projekt"
            )
            
            if result:
                print(f"   ✓ {filename} → {result['relative_path']}")
            else:
                print(f"   ✗ Fehler bei {filename}")
    
    # Test 5: Ordnerstruktur anzeigen
    print("\n5. Erstellte Ordnerstruktur:")
    kunde_pfad = manager.kunden_ordner(test_kunde)
    zeige_ordnerstruktur(kunde_pfad, "   ")
    
    # Test 6: Workflow-Ordner testen
    print("\n6. Workflow-Ordner:")
    workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
    for workflow in workflows:
        workflow_pfad = manager.get_ordner_fuer_workflow(test_kunde, workflow)
        exists = os.path.exists(workflow_pfad)
        print(f"   {workflow}: {workflow_pfad} {'✓' if exists else '✗'}")
    
    print("\n" + "=" * 50)
    print("TEST ABGESCHLOSSEN")
    print("=" * 50)

def zeige_ordnerstruktur(pfad, einrueckung=""):
    """Zeigt die Ordnerstruktur rekursiv an"""
    if not os.path.exists(pfad):
        return
    
    try:
        for item in sorted(os.listdir(pfad)):
            item_pfad = os.path.join(pfad, item)
            if os.path.isdir(item_pfad):
                print(f"{einrueckung}📁 {item}/")
                zeige_ordnerstruktur(item_pfad, einrueckung + "  ")
            else:
                print(f"{einrueckung}📄 {item}")
    except PermissionError:
        print(f"{einrueckung}❌ Zugriff verweigert")

def test_filename_patterns():
    """Testet die Dateinamen-Muster-Erkennung"""
    print("\n" + "=" * 50)
    print("TEST: Dateinamen-Muster-Erkennung")
    print("=" * 50)
    
    # Simuliere die Funktion aus der App
    import re
    
    def extract_customer_from_filename(filename):
        """Extrahiert potenzielle Kundennamen aus Dateinamen"""
        name_without_ext = os.path.splitext(filename)[0]
        
        patterns = [
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Aa]ngebot',
            r'[Aa]ngebot_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Pp]ruefung',
            r'[Pp]ruefung_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'^([A-Za-z][A-Za-z0-9_\-\s]+)_20\d{2}',
            r'^([A-Za-z][A-Za-z0-9_\-\s]{2,})_\d',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_without_ext)
            if match:
                return match.group(1).strip()
        return None
    
    # Test-Dateinamen
    test_files = [
        "Mueller_Angebot.pdf",
        "Angebot_Schmidt_AG.docx",
        "Firma_XYZ_Pruefung.txt",
        "Pruefung_Testfirma.pdf",
        "Kunde_2024.docx",
        "Muster_GmbH_2025.pdf",
        "Dokument_001.txt",
        "Test_123.pdf",
        "Normalfile.docx"
    ]
    
    for filename in test_files:
        customer = extract_customer_from_filename(filename)
        if customer:
            print(f"   ✓ {filename} → {customer}")
        else:
            print(f"   ✗ {filename} → Kein Muster erkannt")

def cleanup_test_data():
    """Räumt Test-Daten auf"""
    test_dir = "Test_Projekte"
    if os.path.exists(test_dir):
        try:
            shutil.rmtree(test_dir)
            print(f"\n🗑️  Test-Ordner '{test_dir}' gelöscht")
        except Exception as e:
            print(f"\n❌ Fehler beim Löschen: {e}")

if __name__ == "__main__":
    print("Starte Tests für erweiterte Upload-System...")
    
    try:
        test_upload_system()
        test_filename_patterns()
        
        # Frage ob Test-Daten gelöscht werden sollen
        antwort = input("\nSollen die Test-Daten gelöscht werden? (j/n): ")
        if antwort.lower() in ['j', 'ja', 'y', 'yes']:
            cleanup_test_data()
        else:
            print("\nTest-Daten bleiben erhalten.")
            
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fehler beim Testen: {e}")
        sys.exit(1)
    
    print("\n✅ Alle Tests abgeschlossen!")
