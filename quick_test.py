"""
Einfacher Test für KundenManagerV2 Ordnerstruktur
"""

import os
import sys
from datetime import datetime

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from kunden_manager_v2 import KundenManagerV2
    
    print("🔍 Teste KundenManagerV2...")
    
    # Erstelle eine Test-Instanz
    km = KundenManagerV2("Test_Projekte")
    
    # Test: Erstelle ein Projekt
    kunde_name = "TestKunde_AG"
    projekt_name = "Website_Update"
    datum = "2025-01-20"
    
    print(f"📋 Erstelle Projekt für {kunde_name}...")
    result = km.erstelle_projekt_ordner(
        kundenname=kunde_name,
        projektname=projekt_name,
        datum=datum
    )
    
    if result:
        projekt_pfad, projekt_id = result
        print(f"✅ Projekt erstellt!")
        print(f"   🆔 Projekt-ID: {projekt_id}")
        print(f"   📁 Pfad: {projekt_pfad}")
        
        # Prüfe Workflow-Ordner
        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        print(f"📂 Prüfe Workflow-Ordner:")
        
        for workflow in workflows:
            workflow_pfad = os.path.join(projekt_pfad, workflow)
            exists = os.path.exists(workflow_pfad)
            status = "✅" if exists else "❌"
            print(f"   {status} {workflow}: {workflow_pfad}")
            
        print(f"\n📊 Ordnerstruktur unter {projekt_pfad}:")
        try:
            for item in os.listdir(projekt_pfad):
                item_path = os.path.join(projekt_pfad, item)
                is_dir = os.path.isdir(item_path)
                icon = "📁" if is_dir else "📄"
                print(f"   {icon} {item}")
        except Exception as e:
            print(f"   ❌ Fehler beim Auflisten: {e}")
            
    else:
        print("❌ Projekt konnte nicht erstellt werden")
        
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
except Exception as e:
    print(f"❌ Allgemeiner Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Test abgeschlossen")
