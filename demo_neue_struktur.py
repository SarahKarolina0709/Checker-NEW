#!/usr/bin/env python3
"""
Demo: Neue Kundenstruktur in Aktion
Zeigt die Vorteile der projekt-zentrierten Organisation
"""

import os
import tempfile
import shutil
from datetime import datetime, timedelta
from kunden_manager_v2 import KundenManagerV2

def demo_neue_struktur():
    """Demonstriert die neue Kundenstruktur mit realistischen Szenarien"""
    
    print("🎯 DEMO: Neue Kundenstruktur in Aktion")
    print("=" * 60)
    
    # Temporärer Ordner für Demo
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = KundenManagerV2(temp_dir)
        
        print("\n📋 Szenario: Kunde 'Müller GmbH' sendet verschiedene Anfragen")
        print("-" * 60)
        
        kunde = "Müller GmbH"
        
        # Szenario 1: Erste Anfrage am Montag
        print("\n🗓️ Montag: Website-Übersetzung Anfrage")
        projekt1 = manager.erstelle_projekt_ordner(kunde, "Website_Übersetzung", "2025-07-07")
        print(f"   ✅ Erstellt: {os.path.basename(projekt1)}")
        
        # Simuliere Ausgangstexte Upload
        ausgangstexte1 = manager.get_projekt_workflow_ordner(kunde, os.path.basename(projekt1), "Ausgangstexte")
        demo_file1 = os.path.join(ausgangstexte1, "website_de.html")
        with open(demo_file1, "w", encoding="utf-8") as f:
            f.write("<html><body>Willkommen auf unserer Website!</body></html>")
        print(f"   📄 Ausgangstexte: website_de.html")
        
        # Szenario 2: Zweite Anfrage am Mittwoch
        print("\n🗓️ Mittwoch: Broschüre-Übersetzung Anfrage")
        projekt2 = manager.erstelle_projekt_ordner(kunde, "Broschüre_Englisch", "2025-07-09")
        print(f"   ✅ Erstellt: {os.path.basename(projekt2)}")
        
        # Simuliere Ausgangstexte Upload
        ausgangstexte2 = manager.get_projekt_workflow_ordner(kunde, os.path.basename(projekt2), "Ausgangstexte")
        demo_file2 = os.path.join(ausgangstexte2, "broschüre_de.pdf")
        with open(demo_file2, "w", encoding="utf-8") as f:
            f.write("PDF-Inhalt: Unsere Produkte und Dienstleistungen...")
        print(f"   📄 Ausgangstexte: broschüre_de.pdf")
        
        # Szenario 3: Notfall-Anfrage am Freitag
        print("\n🗓️ Freitag: Notfall-Übersetzung (Pressemitteilung)")
        projekt3 = manager.erstelle_projekt_ordner(kunde, "Pressemitteilung_Notfall", "2025-07-11")
        print(f"   ✅ Erstellt: {os.path.basename(projekt3)}")
        
        # Simuliere Ausgangstexte Upload
        ausgangstexte3 = manager.get_projekt_workflow_ordner(kunde, os.path.basename(projekt3), "Ausgangstexte")
        demo_file3 = os.path.join(ausgangstexte3, "pressemitteilung_de.docx")
        with open(demo_file3, "w", encoding="utf-8") as f:
            f.write("PRESSEMITTEILUNG: Wichtige Unternehmensnews...")
        print(f"   📄 Ausgangstexte: pressemitteilung_de.docx")
        
        # Zeige Ergebnis-Struktur
        print("\n📁 Resultierende Ordnerstruktur:")
        print("-" * 40)
        kunde_pfad = manager.kunden_ordner(kunde)
        print_directory_tree(kunde_pfad, "")
        
        # Zeige Projekt-Liste
        print("\n📋 Projekt-Übersicht:")
        print("-" * 40)
        projekte = manager.liste_kundenprojekte(kunde)
        for i, projekt in enumerate(projekte, 1):
            print(f"{i}. {projekt}")
            
            # Zeige Dateien in Ausgangstexte
            ausgangstexte_pfad = manager.get_projekt_workflow_ordner(kunde, projekt, "Ausgangstexte")
            if os.path.exists(ausgangstexte_pfad):
                dateien = os.listdir(ausgangstexte_pfad)
                if dateien:
                    print(f"   📄 Ausgangstexte: {', '.join(dateien)}")
        
        print("\n🎯 Vorteile der neuen Struktur:")
        print("-" * 40)
        print("✅ Klare Trennung verschiedener Projekte")
        print("✅ Zeitliche Nachverfolgung durch Datum")
        print("✅ Keine Vermischung von Ausgangstexten")
        print("✅ Einfache Navigation für Mitarbeiter")
        print("✅ Bessere Archivierung und Verwaltung")
        
        return True

def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """Zeigt die Ordnerstruktur als Baum"""
    if current_depth > max_depth or not os.path.exists(path):
        return
    
    items = sorted(os.listdir(path))
    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        if os.path.isdir(item_path) and current_depth < max_depth:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_tree(item_path, next_prefix, max_depth, current_depth + 1)

def demo_vergleich_alt_neu():
    """Vergleicht alte vs neue Struktur"""
    
    print("\n🔄 VERGLEICH: Alte vs Neue Struktur")
    print("=" * 60)
    
    print("\n❌ ALTE STRUKTUR - Probleme:")
    print("-" * 40)
    print("Kunde_Müller/")
    print("├── Angebot/")
    print("│   ├── diverse_angebote_vermischt.pdf")
    print("│   └── welches_projekt???.pdf")
    print("├── Pruefung/")
    print("│   ├── alte_pruefungen.pdf")
    print("│   └── neue_pruefungen.pdf")
    print("├── Finalisierung/")
    print("│   └── finale_versionen_vermischt.pdf")
    print("└── Ausgangstexte/")
    print("    ├── website_de.html      ← Wann war das?")
    print("    ├── broschüre_de.pdf     ← Welches Projekt?")
    print("    └── pressemitteilung.docx ← Zusammenhang?")
    
    print("\n❌ PROBLEME:")
    print("   • Keine zeitliche Zuordnung")
    print("   • Vermischung verschiedener Projekte")
    print("   • Schwierige Nachverfolgung")
    print("   • Verwirrung bei Mitarbeitern")
    
    print("\n✅ NEUE STRUKTUR - Lösung:")
    print("-" * 40)
    print("Kunde_Müller/")
    print("├── 2025-07-07_Website_Übersetzung/")
    print("│   ├── Ausgangstexte/")
    print("│   │   └── website_de.html")
    print("│   ├── Angebot/")
    print("│   ├── Pruefung/")
    print("│   └── Finalisierung/")
    print("├── 2025-07-09_Broschüre_Englisch/")
    print("│   ├── Ausgangstexte/")
    print("│   │   └── broschüre_de.pdf")
    print("│   ├── Angebot/")
    print("│   ├── Pruefung/")
    print("│   └── Finalisierung/")
    print("└── 2025-07-11_Pressemitteilung_Notfall/")
    print("    ├── Ausgangstexte/")
    print("    │   └── pressemitteilung_de.docx")
    print("    ├── Angebot/")
    print("    ├── Pruefung/")
    print("    └── Finalisierung/")
    
    print("\n✅ VORTEILE:")
    print("   • Klare zeitliche Trennung")
    print("   • Eindeutige Projekt-Zuordnung")
    print("   • Bessere Nachverfolgung")
    print("   • Intuitive Navigation")
    print("   • Einfache Archivierung")

def demo_migration():
    """Demonstriert die Migration von alter zu neuer Struktur"""
    
    print("\n🔄 DEMO: Migration von alter zu neuer Struktur")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Erstelle alte Struktur
        print("\n1. Erstelle alte Struktur...")
        kunde = "Migration_Test"
        alte_struktur = os.path.join(temp_dir, kunde)
        os.makedirs(alte_struktur)
        
        # Alte Workflow-Ordner
        for workflow in ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]:
            workflow_pfad = os.path.join(alte_struktur, workflow)
            os.makedirs(workflow_pfad)
            
            # Dummy-Dateien
            for i in range(2):
                dummy_file = os.path.join(workflow_pfad, f"alte_datei_{i+1}.txt")
                with open(dummy_file, "w") as f:
                    f.write(f"Alte Datei aus {workflow} - Inhalt {i+1}")
        
        print("   ✅ Alte Struktur erstellt mit Dummy-Dateien")
        
        # Zeige alte Struktur
        print("\n2. Alte Struktur:")
        print_directory_tree(alte_struktur, "   ")
        
        # Migration durchführen
        print("\n3. Migration durchführen...")
        manager = KundenManagerV2(temp_dir)
        success = manager.migrate_from_old_structure(kunde)
        
        if success:
            print("   ✅ Migration erfolgreich!")
            
            # Zeige neue Struktur
            print("\n4. Neue Struktur nach Migration:")
            print_directory_tree(manager.kunden_ordner(kunde), "   ")
            
            # Zeige Projekte
            projekte = manager.liste_kundenprojekte(kunde)
            print(f"\n5. Gefundene Projekte: {projekte}")
            
            # Prüfe ob Dateien erhalten blieben
            if projekte:
                migration_projekt = projekte[0]
                for workflow in ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]:
                    workflow_pfad = manager.get_projekt_workflow_ordner(kunde, migration_projekt, workflow)
                    if os.path.exists(workflow_pfad):
                        dateien = os.listdir(workflow_pfad)
                        print(f"   📁 {workflow}: {len(dateien)} Dateien erhalten")
        else:
            print("   ❌ Migration fehlgeschlagen")

if __name__ == "__main__":
    try:
        demo_neue_struktur()
        demo_vergleich_alt_neu()
        demo_migration()
        print("\n🎉 Demo erfolgreich abgeschlossen!")
        print("\n💡 Die neue Struktur ist bereit für die Implementierung!")
    except Exception as e:
        print(f"\n❌ Demo fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
