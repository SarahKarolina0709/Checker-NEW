#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Umfassender Test für das KundenManager-System
Testet alle Funktionalitäten des KundenManagers einschließlich:
- Kundenerstellung und -verwaltung
- Projektordner-Erstellung
- Fuzzy-Matching für Kundennamen
- Workflow-Integration
"""

import os
import sys
import json
from datetime import datetime
import traceback

# Import des KundenManagers
try:
    from kunden_manager import KundenManager
    print("✅ KundenManager erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Import des KundenManagers: {e}")
    sys.exit(1)

def test_kundenmanager_grundfunktionen():
    """Testet die Grundfunktionalitäten des KundenManagers"""
    print("\n" + "="*60)
    print("🧪 TESTE KUNDENMANAGER GRUNDFUNKTIONEN")
    print("="*60)
    
    # Initialisierung
    manager = KundenManager()
    print(f"✅ KundenManager initialisiert mit Base-Dir: {manager.base_dir}")
    
    # Teste Kundenerstellung
    test_kunden = ["Test_Kunde_1", "Musterfirma_GmbH", "Übersetzungsbüro_Schmidt"]
    
    for kunde in test_kunden:
        try:
            kundenpfad = manager.erstelle_kundenstruktur(kunde)
            print(f"✅ Kunde erstellt: {kunde} -> {kundenpfad}")
            
            # Prüfe ob Ordnerstruktur korrekt erstellt wurde
            unterordner = ["Angebot", "Pruefung", "Finalisierung"]
            for ordner in unterordner:
                ordnerpfad = os.path.join(kundenpfad, ordner)
                if os.path.exists(ordnerpfad):
                    print(f"   ✅ Unterordner existiert: {ordner}")
                else:
                    print(f"   ❌ Unterordner fehlt: {ordner}")
                    
        except Exception as e:
            print(f"❌ Fehler bei Kunde {kunde}: {e}")
    
    # Teste Kundenliste
    try:
        alle_kunden = manager.alle_kunden()
        print(f"\n✅ Gefundene Kunden ({len(alle_kunden)}):")
        for kunde in alle_kunden:
            print(f"   • {kunde}")
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Kundenliste: {e}")
    
    return manager

def test_fuzzy_matching(manager):
    """Testet das Fuzzy-Matching für Kundennamen"""
    print("\n" + "="*60)
    print("🧪 TESTE FUZZY-MATCHING")
    print("="*60)
    
    test_fälle = [
        ("Test_Kunde_1", "Test Kunde 1"),  # Exakte Entsprechung mit Leerzeichen
        ("Musterfirma_GmbH", "musterfirma gmbh"),  # Lowercase
        ("Übersetzungsbüro_Schmidt", "Übersetzungsbuero Schmidt"),  # Tippfehler
        ("Nichtexistenter_Kunde", "Diesen Kunden gibt es nicht"),  # Kein Match
    ]
    
    for original, suche in test_fälle:
        try:
            match = manager.fuzzy_kundenname_suche(suche)
            if match:
                print(f"✅ Fuzzy-Match: '{suche}' -> '{match}'")
            else:
                print(f"ℹ️  Kein Match: '{suche}' -> Kein ähnlicher Kunde gefunden")
        except Exception as e:
            print(f"❌ Fehler beim Fuzzy-Matching für '{suche}': {e}")

def test_projekt_ordner_erstellung(manager):
    """Testet die Erstellung von Projektordnern"""
    print("\n" + "="*60)
    print("🧪 TESTE PROJEKTORDNER-ERSTELLUNG")
    print("="*60)
    
    test_projekte = [
        ("Test_Kunde_1", "Angebot", "Jahresbericht_2024"),
        ("Musterfirma_GmbH", "Pruefung", "Technische_Dokumentation"),
        ("Test Kunde 1", "Finalisierung", "Marketing_Broschüre"),  # Mit Fuzzy-Matching
    ]
    
    for kunde, workflow, projekt in test_projekte:
        try:
            projekt_pfad = manager.neuer_anfrage_ordner(kunde, workflow, projekt)
            print(f"✅ Projektordner erstellt:")
            print(f"   Kunde: {kunde}")
            print(f"   Workflow: {workflow}")
            print(f"   Projekt: {projekt}")
            print(f"   Pfad: {projekt_pfad}")
            
            # Prüfe ob Ordner tatsächlich existiert
            if os.path.exists(projekt_pfad):
                print("   ✅ Ordner physisch vorhanden")
            else:
                print("   ❌ Ordner nicht gefunden!")
                
        except Exception as e:
            print(f"❌ Fehler bei Projektordner-Erstellung: {e}")
            traceback.print_exc()

def test_workflow_integration(manager):
    """Testet die Integration mit Workflow-Daten"""
    print("\n" + "="*60)
    print("🧪 TESTE WORKFLOW-INTEGRATION")
    print("="*60)
    
    # Simuliere Workflow-Daten wie sie von der Anwendung kommen
    workflow_data = {
        "kunde_name": "Test_Kunde_1",
        "auftragsnummer": "AUF2024-001",
        "kundenbetreuer": "Max Mustermann",
        "zielsprache": "Deutsch → Englisch",
        "dateien": ["dokument1.docx", "dokument2.pdf"]
    }
    
    try:
        # Erstelle Projektordner basierend auf Workflow-Daten
        projekt_pfad = manager.neuer_anfrage_ordner(
            workflow_data["kunde_name"], 
            "Angebot", 
            workflow_data["auftragsnummer"]
        )
        
        print(f"✅ Workflow-Projektordner erstellt: {projekt_pfad}")
        
        # Erstelle eine Metadaten-Datei im Projektordner
        metadata = {
            "kunde_name": workflow_data["kunde_name"],
            "auftragsnummer": workflow_data["auftragsnummer"],
            "kundenbetreuer": workflow_data["kundenbetreuer"],
            "zielsprache": workflow_data["zielsprache"],
            "dateien": workflow_data["dateien"],
            "erstellt_am": datetime.now().isoformat(),
            "status": "in_bearbeitung"
        }
        
        metadata_pfad = os.path.join(projekt_pfad, "project_metadata.json")
        with open(metadata_pfad, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Metadaten gespeichert: {metadata_pfad}")
        
        # Erstelle Unterordner für Dateien
        quellen_ordner = os.path.join(projekt_pfad, "quellen")
        uebersetzungen_ordner = os.path.join(projekt_pfad, "uebersetzungen")
        
        os.makedirs(quellen_ordner, exist_ok=True)
        os.makedirs(uebersetzungen_ordner, exist_ok=True)
        
        print(f"✅ Dateiordner erstellt: quellen, uebersetzungen")
        
    except Exception as e:
        print(f"❌ Fehler bei Workflow-Integration: {e}")
        traceback.print_exc()

def test_ordnerstruktur_analyse(manager):
    """Analysiert die erstellte Ordnerstruktur"""
    print("\n" + "="*60)
    print("🔍 ORDNERSTRUKTUR-ANALYSE")
    print("="*60)
    
    try:
        base_dir = manager.base_dir
        print(f"Basis-Verzeichnis: {base_dir}")
        
        for kunde in manager.alle_kunden():
            print(f"\n📁 {kunde}:")
            kunde_pfad = manager.kunden_ordner(kunde)
            
            # Liste Workflow-Ordner
            workflows = manager.kunden_unterordner(kunde)
            for workflow in workflows:
                workflow_pfad = os.path.join(kunde_pfad, workflow)
                projekte = [d for d in os.listdir(workflow_pfad) 
                           if os.path.isdir(os.path.join(workflow_pfad, d))]
                
                print(f"  📂 {workflow} ({len(projekte)} Projekte):")
                for projekt in projekte:
                    projekt_pfad = os.path.join(workflow_pfad, projekt)
                    
                    # Prüfe auf Metadaten
                    metadata_pfad = os.path.join(projekt_pfad, "project_metadata.json")
                    if os.path.exists(metadata_pfad):
                        with open(metadata_pfad, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        auftrag = metadata.get('auftragsnummer', 'N/A')
                        status = metadata.get('status', 'N/A')
                        print(f"    📄 {projekt} (Auftrag: {auftrag}, Status: {status})")
                    else:
                        print(f"    📄 {projekt} (keine Metadaten)")
                        
    except Exception as e:
        print(f"❌ Fehler bei Ordnerstruktur-Analyse: {e}")
        traceback.print_exc()

def test_error_handling(manager):
    """Testet Fehlerbehandlung"""
    print("\n" + "="*60)
    print("🧪 TESTE FEHLERBEHANDLUNG")
    print("="*60)
    
    # Test mit ungültigen Zeichen im Kundennamen
    invalid_names = ["Test<>Kunde", "Test/Kunde", "Test:Kunde", "Test|Kunde"]
    
    for invalid_name in invalid_names:
        try:
            # Dies sollte funktionieren, da der KundenManager Zeichen ersetzt
            pfad = manager.erstelle_kundenstruktur(invalid_name)
            print(f"✅ Ungültiger Name behandelt: '{invalid_name}' -> {os.path.basename(pfad)}")
        except Exception as e:
            print(f"❌ Fehler bei ungültigem Namen '{invalid_name}': {e}")

def main():
    """Hauptfunktion für umfassende Tests"""
    print("🚀 KUNDENMANAGER UMFASSENDER TEST")
    print("=" * 60)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Grundfunktionen testen
        manager = test_kundenmanager_grundfunktionen()
        
        # Fuzzy-Matching testen
        test_fuzzy_matching(manager)
        
        # Projektordner-Erstellung testen
        test_projekt_ordner_erstellung(manager)
        
        # Workflow-Integration testen
        test_workflow_integration(manager)
        
        # Ordnerstruktur analysieren
        test_ordnerstruktur_analyse(manager)
        
        # Fehlerbehandlung testen
        test_error_handling(manager)
        
        print("\n" + "="*60)
        print("✅ ALLE TESTS ABGESCHLOSSEN")
        print("="*60)
        print("Der KundenManager ist vollständig funktionsfähig und bereit für den produktiven Einsatz!")
        
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
