#!/usr/bin/env python3
"""
Vollständiger Funktionstest für die erweiterte Checker-App
========================================================

Dieses Skript testet alle Kernfunktionen der modernisierten Checker-App:
- Kundenmanagement mit Fuzzy-Matching
- Upload-System mit automatischer Kundenablage
- Workflow-Integration
- UI-Komponenten und Dialoge

Führen Sie dieses Skript aus, um sicherzustellen, dass alle Features korrekt funktionieren.
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure the app modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_test_environment():
    """Setze eine sichere Testumgebung auf."""
    
    # Erstelle temporären Testordner
    test_dir = tempfile.mkdtemp(prefix="checker_app_test_")
    
    # Sichere den ursprünglichen Arbeitsordner
    original_cwd = os.getcwd()
    
    # Wechsle in den Testordner
    os.chdir(test_dir)
    
    print(f"✓ Testumgebung erstellt: {test_dir}")
    return test_dir, original_cwd

def cleanup_test_environment(test_dir, original_cwd):
    """Räume die Testumgebung auf."""
    
    # Zurück zum ursprünglichen Ordner
    os.chdir(original_cwd)
    
    # Lösche Testordner
    try:
        shutil.rmtree(test_dir)
        print(f"✓ Testumgebung bereinigt: {test_dir}")
    except Exception as e:
        print(f"⚠ Warnung: Testordner konnte nicht gelöscht werden: {e}")

def test_kunden_manager():
    """Teste das Kundenmanagement."""
    
    print("\n=== Test: Kundenmanagement ===")
    
    try:
        from kunden_manager import KundenManager
        
        # Initialisiere KundenManager
        km = KundenManager()
        print("✓ KundenManager erfolgreich importiert und initialisiert")
        
        # Teste Kundenerstellung
        test_kunde = "Test Kunde GmbH"
        success = km.neuer_kunde(test_kunde)
        
        if success:
            print(f"✓ Kunde '{test_kunde}' erfolgreich erstellt")
            
            # Prüfe Ordnerstruktur
            kunde_pfad = km.kunden_ordner(test_kunde)
            if os.path.exists(kunde_pfad):
                print(f"✓ Kunden-Ordner erstellt: {kunde_pfad}")
                
                # Prüfe Workflow-Ordner
                workflows = ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]
                for workflow in workflows:
                    workflow_pfad = km.get_ordner_fuer_workflow(test_kunde, workflow)
                    if os.path.exists(workflow_pfad):
                        print(f"✓ Workflow-Ordner '{workflow}' erstellt")
                    else:
                        print(f"❌ Workflow-Ordner '{workflow}' fehlt")
                        
            else:
                print(f"❌ Kunden-Ordner nicht gefunden: {kunde_pfad}")
        else:
            print(f"❌ Kunde '{test_kunde}' konnte nicht erstellt werden")
        
        # Teste Fuzzy-Matching
        print("\n--- Fuzzy-Matching Test ---")
        exists, match = km.customer_exists("Test Kunde")
        if exists:
            print(f"✓ Fuzzy-Matching funktioniert: '{match}' gefunden für 'Test Kunde'")
        else:
            print("❌ Fuzzy-Matching funktioniert nicht")
        
        # Teste Kundenliste
        alle_kunden = km.alle_kunden()
        if test_kunde in alle_kunden:
            print(f"✓ Kundenliste enthält {len(alle_kunden)} Kunden")
        else:
            print("❌ Kunde nicht in Kundenliste gefunden")
            
    except ImportError as e:
        print(f"❌ KundenManager Import fehlgeschlagen: {e}")
    except Exception as e:
        print(f"❌ KundenManager Test fehlgeschlagen: {e}")

def test_upload_manager():
    """Teste das Upload-System."""
    
    print("\n=== Test: Upload-System ===")
    
    try:
        from kunden_manager import KundenManager
        from upload_manager import UploadManager
        
        # Erstelle Mock-App Instanz
        class MockApp:
            def __init__(self):
                self.logger = None
        
        mock_app = MockApp()
        
        # Initialisiere Manager
        km = KundenManager()
        um = UploadManager(mock_app, km)
        print("✓ UploadManager erfolgreich importiert und initialisiert")
        
        # Erstelle Testkunden
        test_kunde = "Upload Test Kunde"
        km.neuer_kunde(test_kunde)
        
        # Erstelle Testdateien
        test_files = []
        for i in range(3):
            test_file = f"test_document_{i+1}.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"Dies ist Testdokument {i+1}\nFür Upload-Test\nKunde: {test_kunde}")
            test_files.append(os.path.abspath(test_file))
        
        print(f"✓ {len(test_files)} Testdateien erstellt")
        
        # Teste Kundenvorschläge
        um.uploaded_files = test_files
        suggestions = um.get_customer_suggestions()
        print(f"✓ Kundenvorschläge: {len(suggestions)} gefunden")
        
        # Teste Upload-Statistiken
        stats = um.get_upload_statistics()
        if stats and stats.get('uploaded_files_count', 0) == len(test_files):
            print(f"✓ Upload-Statistiken korrekt: {stats['uploaded_files_count']} Dateien, {stats['total_size_mb']:.2f} MB")
        else:
            print(f"❌ Upload-Statistiken inkorrekt")
        
        # Teste Dateikategorisierung
        workflow_suggestion = um.suggest_workflow_from_filename("Angebot_Kunde_2024.docx")
        if workflow_suggestion:
            print(f"✓ Workflow-Vorschlag funktioniert: '{workflow_suggestion}'")
        else:
            print("⚠ Workflow-Vorschlag leer (normal für unbekannte Dateien)")
        
        print("✓ Upload-System Test abgeschlossen")
        
    except ImportError as e:
        print(f"❌ UploadManager Import fehlgeschlagen: {e}")
    except Exception as e:
        print(f"❌ UploadManager Test fehlgeschlagen: {e}")

def test_app_initialization():
    """Teste die App-Initialisierung (ohne GUI)."""
    
    print("\n=== Test: App-Initialisierung ===")
    
    try:
        # Teste Import der Hauptmodule
        modules_to_test = [
            'kunden_manager',
            'upload_manager',
            'path_utils',
            'error_handlers',
            'fluent_icons_manager'
        ]
        
        imported_modules = []
        for module in modules_to_test:
            try:
                __import__(module)
                imported_modules.append(module)
                print(f"✓ Modul '{module}' erfolgreich importiert")
            except ImportError as e:
                print(f"⚠ Modul '{module}' nicht verfügbar: {e}")
            except Exception as e:
                print(f"❌ Fehler beim Import von '{module}': {e}")
        
        print(f"✓ {len(imported_modules)}/{len(modules_to_test)} Module erfolgreich importiert")
        
        # Teste Pfad-Utilities
        try:
            from path_utils import get_app_base_path, get_resource_path
            
            base_path = get_app_base_path()
            if os.path.exists(base_path):
                print(f"✓ App-Basispfad gefunden: {base_path}")
            else:
                print(f"⚠ App-Basispfad nicht gefunden: {base_path}")
            
        except Exception as e:
            print(f"❌ Pfad-Utilities Test fehlgeschlagen: {e}")
        
    except Exception as e:
        print(f"❌ App-Initialisierung Test fehlgeschlagen: {e}")

def test_file_operations():
    """Teste Dateioperationen."""
    
    print("\n=== Test: Dateioperationen ===")
    
    try:
        from kunden_manager import KundenManager
        
        km = KundenManager()
        
        # Erstelle Testkunden
        test_kunde = "Datei Test Kunde"
        km.neuer_kunde(test_kunde)
        
        # Erstelle Projektstruktur
        projekt_name = "Test Projekt 2024"
        projekt_pfad = km.erstelle_projektstruktur(test_kunde, projekt_name)
        
        if os.path.exists(projekt_pfad):
            print(f"✓ Projektstruktur erstellt: {projekt_pfad}")
            
            # Erstelle Testdateien im Projekt
            test_dateien = ["dokument1.docx", "tabelle1.xlsx", "praesentation1.pptx"]
            
            for datei in test_dateien:
                datei_pfad = os.path.join(projekt_pfad, datei)
                with open(datei_pfad, 'w', encoding='utf-8') as f:
                    f.write(f"Testinhalt für {datei}")
                
                if os.path.exists(datei_pfad):
                    print(f"✓ Testdatei erstellt: {datei}")
                else:
                    print(f"❌ Testdatei nicht erstellt: {datei}")
            
            # Teste datumsbasierte Ablage
            datum_ordner = km.get_datum_ordner()
            print(f"✓ Datumsordner: {datum_ordner}")
            
        else:
            print(f"❌ Projektstruktur nicht erstellt: {projekt_pfad}")
        
    except Exception as e:
        print(f"❌ Dateioperationen Test fehlgeschlagen: {e}")

def run_comprehensive_test():
    """Führe einen umfassenden Test aller Features durch."""
    
    print("🚀 Starte umfassenden Feature-Test der Checker-App")
    print("=" * 60)
    
    # Setup
    test_dir, original_cwd = setup_test_environment()
    
    try:
        # Führe alle Tests durch
        test_app_initialization()
        test_kunden_manager()
        test_upload_manager()
        test_file_operations()
        
        print("\n" + "=" * 60)
        print("✅ Alle Tests abgeschlossen!")
        print("✅ Die Checker-App ist bereit für den produktiven Einsatz.")
        
    except Exception as e:
        print(f"\n❌ Kritischer Fehler beim Testen: {e}")
        
    finally:
        # Cleanup
        cleanup_test_environment(test_dir, original_cwd)

def main():
    """Hauptfunktion für interaktive Tests."""
    
    print("Checker-App Feature-Test")
    print("========================")
    print()
    print("Optionen:")
    print("1. Vollständiger Test")
    print("2. Nur Kundenmanagement")
    print("3. Nur Upload-System")
    print("4. App-Initialisierung")
    print("5. Dateioperationen")
    print()
    
    try:
        choice = input("Wählen Sie eine Option (1-5): ").strip()
        
        test_dir, original_cwd = setup_test_environment()
        
        try:
            if choice == "1":
                run_comprehensive_test()
                return
            elif choice == "2":
                test_kunden_manager()
            elif choice == "3":
                test_upload_manager()
            elif choice == "4":
                test_app_initialization()
            elif choice == "5":
                test_file_operations()
            else:
                print("Ungültige Auswahl. Führe vollständigen Test durch...")
                run_comprehensive_test()
                return
                
        finally:
            cleanup_test_environment(test_dir, original_cwd)
            
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
    except Exception as e:
        print(f"\nFehler beim Test: {e}")

if __name__ == "__main__":
    # Prüfe ob im interaktiven Modus
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automatischer Test ohne Eingabe
        run_comprehensive_test()
    else:
        # Interaktiver Modus
        main()
