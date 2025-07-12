"""
Umfassender Icon-Test für die Checker-App.
Testet alle verfügbaren Icons und deren Mappings.
"""

import os
import sys

# Stelle sicher, dass wir die App-Module importieren können
sys.path.append(os.path.dirname(__file__))

def test_all_icons():
    """Testet alle verfügbaren Icons und deren Mappings"""
    
    # Importiere nur die notwendigen Module für den Test
    try:
        from checker_app import CheckerApp
        import customtkinter as ctk
        
        # Erstelle eine minimale App-Instanz für Tests
        root = ctk.CTk()
        root.withdraw()  # Verstecke das Fenster
        
        # Erstelle App-Instanz
        app = CheckerApp()
        app.root = root  # Setze root manuell
        
        # Initialisiere Icon-System
        if hasattr(app, '_load_png_icons'):
            app._load_png_icons()
        
        print("🔍 ICON TESTING GESTARTET")
        print("="*60)
        
        # 1. Teste alle verfügbaren Icons
        print("\n1. VERFÜGBARE ICON-DATEIEN:")
        print("-" * 40)
        
        icons_dir = "icons"
        available_files = []
        if os.path.exists(icons_dir):
            for file in os.listdir(icons_dir):
                if file.endswith('.png'):
                    available_files.append(file)
        
        available_files.sort()
        for i, file in enumerate(available_files, 1):
            print(f"   {i:2d}. {file}")
        
        print(f"\n   📊 Gesamt: {len(available_files)} Icon-Dateien gefunden")
        
        # 2. Teste Icon-Mappings
        print("\n2. ICON-MAPPING TESTS:")
        print("-" * 40)
        
        test_mappings = [
            # Basis-Icons
            ('rocket', 'Raketen-Icon für Launch'),
            ('quality', 'Qualitäts-Icon'),
            ('delete', 'Lösch-Icon'),
            ('upload', 'Upload-Icon'),
            ('download', 'Download-Icon'),
            ('pdf', 'PDF-Icon'),
            ('doc', 'DOC-Icon'),
            ('txt', 'TXT-Icon'),
            ('link', 'Link-Icon'),
            ('connect', 'Verbindungs-Icon'),
            
            # Alias-Tests
            ('launch', 'Launch-Alias für rocket'),
            ('validate', 'Validate-Alias für quality'),
            ('import', 'Import-Alias für upload'),
            ('export', 'Export-Alias für download'),
            ('chain', 'Chain-Alias für link'),
            
            # Häufig verwendete Icons
            ('user', 'Benutzer-Icon'),
            ('settings', 'Einstellungs-Icon'),
            ('search', 'Such-Icon'),
            ('folder', 'Ordner-Icon'),
            ('file', 'Datei-Icon'),
            ('check', 'Häkchen-Icon'),
            ('close', 'Schließen-Icon'),
            ('menu', 'Menü-Icon'),
            
            # Workflow-spezifische Icons
            ('workflow', 'Workflow-Icon'),
            ('analytics', 'Analytics-Icon'),
            ('report', 'Report-Icon'),
            ('home', 'Home-Icon'),
        ]
        
        successful_mappings = 0
        failed_mappings = []
        
        for icon_name, description in test_mappings:
            try:
                icon = app.get_icon(icon_name, size=(16, 16))
                if icon is not None:
                    status = "✅"
                    successful_mappings += 1
                else:
                    status = "❌"
                    failed_mappings.append((icon_name, description))
                
                print(f"   {status} {icon_name:<15} | {description}")
                
            except Exception as e:
                print(f"   ❌ {icon_name:<15} | ERROR: {e}")
                failed_mappings.append((icon_name, description))
        
        # 3. Teste Kategorien
        print("\n3. KATEGORIEN-TEST:")
        print("-" * 40)
        
        if hasattr(app, 'get_available_icons'):
            try:
                categorized = app.get_available_icons(categorized=True)
                for category, icons in categorized.items():
                    print(f"   📁 {category}: {len(icons)} Icons")
                    # Zeige erste 5 Icons als Beispiel
                    examples = icons[:5]
                    if examples:
                        print(f"      Beispiele: {', '.join(examples)}")
                        if len(icons) > 5:
                            print(f"      ... und {len(icons) - 5} weitere")
                    print()
            except Exception as e:
                print(f"   ❌ Kategorie-Test fehlgeschlagen: {e}")
        
        # 4. Zusammenfassung
        print("\n4. TEST-ZUSAMMENFASSUNG:")
        print("="*60)
        print(f"   📁 Verfügbare Icon-Dateien: {len(available_files)}")
        print(f"   ✅ Erfolgreiche Mappings: {successful_mappings}")
        print(f"   ❌ Fehlgeschlagene Mappings: {len(failed_mappings)}")
        print(f"   📊 Erfolgsrate: {(successful_mappings / len(test_mappings) * 100):.1f}%")
        
        if failed_mappings:
            print(f"\n   ⚠️  FEHLGESCHLAGENE MAPPINGS:")
            for icon_name, description in failed_mappings:
                print(f"      - {icon_name}: {description}")
        
        # 5. Empfehlungen
        print(f"\n5. EMPFEHLUNGEN:")
        print("-" * 40)
        
        if len(failed_mappings) == 0:
            print("   🎉 Alle Icons sind korrekt gemappt!")
        else:
            print("   💡 Folgende Icons könnten noch erstellt werden:")
            missing_icons = [name for name, desc in failed_mappings]
            for icon in missing_icons:
                print(f"      - {icon}.png")
        
        # Cleanup
        root.destroy()
        
        print("\n" + "="*60)
        print("🔍 ICON TESTING ABGESCHLOSSEN")
        
        return successful_mappings, len(failed_mappings)
        
    except Exception as e:
        print(f"❌ Fehler beim Icon-Testing: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

if __name__ == "__main__":
    test_all_icons()
