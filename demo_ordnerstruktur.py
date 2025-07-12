"""
Demo-Test für vollständige Ordnerstruktur-Erstellung
"""

import os
import sys
import shutil
from datetime import datetime

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_ordnerstruktur_erstellung():
    """Demonstriert die vollständige Ordnerstruktur-Erstellung"""
    
    print("🎯 Demo: Vollständige Ordnerstruktur-Erstellung")
    print("=" * 50)
    
    # Importiere KundenManagerV2
    try:
        from kunden_manager_v2 import KundenManagerV2
    except ImportError as e:
        print(f"❌ Fehler beim Import: {e}")
        return False
    
    # Verwende ein Demo-Verzeichnis
    demo_dir = "Demo_Checker_Projekte"
    
    # Entferne altes Demo-Verzeichnis falls vorhanden
    if os.path.exists(demo_dir):
        print(f"🧹 Entferne altes Demo-Verzeichnis: {demo_dir}")
        shutil.rmtree(demo_dir)
    
    print(f"📁 Erstelle neues Demo-Verzeichnis: {demo_dir}")
    
    # Initialisiere KundenManagerV2
    km = KundenManagerV2(demo_dir)
    
    # Demo-Daten
    kunden_projekte = [
        ("Musterfirma_GmbH", "Website_Redesign", "2025-01-20"),
        ("TechCorp_AG", "App_Übersetzung", "2025-01-21"),
        ("StartupXYZ", "Marketing_Materialien", "2025-01-22"),
    ]
    
    print(f"\n📋 Erstelle {len(kunden_projekte)} Demo-Projekte...")
    
    erfolgreiche_projekte = []
    
    for kunde_name, projekt_name, datum in kunden_projekte:
        print(f"\n🏗️  Erstelle Projekt: {kunde_name} - {projekt_name}")
        
        try:
            result = km.erstelle_projekt_ordner(
                kundenname=kunde_name,
                projektname=projekt_name,
                datum=datum
            )
            
            if result:
                projekt_pfad, projekt_id = result
                print(f"   ✅ Erfolgreich erstellt: {projekt_id}")
                print(f"   📂 Pfad: {projekt_pfad}")
                
                # Prüfe Workflow-Ordner
                workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                alle_ordner_da = True
                
                for workflow in workflows:
                    workflow_pfad = os.path.join(projekt_pfad, workflow)
                    if os.path.exists(workflow_pfad):
                        print(f"   ✅ {workflow}")
                    else:
                        print(f"   ❌ {workflow} fehlt!")
                        alle_ordner_da = False
                
                if alle_ordner_da:
                    erfolgreiche_projekte.append((kunde_name, projekt_id))
                else:
                    print(f"   ⚠️  Unvollständige Ordnerstruktur!")
                    
            else:
                print(f"   ❌ Projekt konnte nicht erstellt werden")
                
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
    
    print(f"\n📊 Zusammenfassung:")
    print(f"   Erfolgreich erstellt: {len(erfolgreiche_projekte)}/{len(kunden_projekte)} Projekte")
    
    if erfolgreiche_projekte:
        print(f"\n🎉 Erfolgreich erstellte Projekte:")
        for kunde, projekt_id in erfolgreiche_projekte:
            print(f"   ✅ {kunde} - {projekt_id}")
    
    # Zeige komplette Ordnerstruktur
    print(f"\n🌳 Komplette Ordnerstruktur:")
    print_ordnerstruktur(demo_dir)
    
    # Optional: Aufräumen
    cleanup = input(f"\n❓ Demo-Verzeichnis '{demo_dir}' löschen? (y/n): ").lower().strip()
    if cleanup == 'y':
        shutil.rmtree(demo_dir)
        print("🧹 Demo-Verzeichnis gelöscht")
    else:
        print(f"📁 Demo-Verzeichnis bleibt erhalten: {demo_dir}")
    
    return len(erfolgreiche_projekte) == len(kunden_projekte)

def print_ordnerstruktur(directory, prefix="", max_depth=3, current_depth=0):
    """Zeigt die Ordnerstruktur hierarchisch an"""
    
    if current_depth > max_depth or not os.path.exists(directory):
        return
    
    try:
        items = sorted(os.listdir(directory))
        
        for i, item in enumerate(items):
            item_path = os.path.join(directory, item)
            is_last = i == len(items) - 1
            
            if os.path.isdir(item_path):
                print(f"{prefix}{'└── ' if is_last else '├── '}📁 {item}/")
                extension = "    " if is_last else "│   "
                print_ordnerstruktur(item_path, prefix + extension, max_depth, current_depth + 1)
            else:
                print(f"{prefix}{'└── ' if is_last else '├── '}📄 {item}")
                
    except PermissionError:
        print(f"{prefix}❌ Zugriff verweigert")

if __name__ == "__main__":
    erfolg = demo_ordnerstruktur_erstellung()
    
    if erfolg:
        print("\n🎉 Demo erfolgreich abgeschlossen!")
        print("✅ Ordnerstruktur-Erstellung funktioniert vollständig")
    else:
        print("\n⚠️  Demo mit Fehlern abgeschlossen")
        print("❌ Ordnerstruktur-Erstellung benötigt weitere Prüfung")
