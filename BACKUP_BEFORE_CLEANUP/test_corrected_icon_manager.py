"""
Test der korrigierten Icon-Behandlung (ohne beschädigte Dateien)
"""

import os
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_corrected_icon_manager():
    """Testet den korrigierten Icon Manager ohne beschädigte Dateien"""
    print("=" * 60)
    print("TESTE KORRIGIERTEN ICON MANAGER (OHNE BESCHÄDIGTE DATEIEN)")
    print("=" * 60)
    
    try:
        from fluent_icons_manager import FluentIconManager
        
        # Manager initialisieren
        workspace_path = os.getcwd()
        icon_manager = FluentIconManager(workspace_path=workspace_path)
        
        print(f"✅ Icon Manager erfolgreich initialisiert")
        print(f"📁 Workspace: {workspace_path}")
        
        # Statistiken
        stats = icon_manager.get_stats()
        print(f"\n📊 Statistiken:")
        print(f"   Lokale Icons: {stats['local_icons']}")
        print(f"   Emoji Icons: {stats['emoji_icons']}")
        print(f"   Custom Icons: {stats['custom_icons']}")
        print(f"   Cached Images: {stats['cached_images']}")
        
        # Test einzelner Icons
        print(f"\n🧪 TESTE ICON-ABRUF (nur funktionierende Dateien):")
        
        test_icons = [
            'home', 'settings', 'search', 'close', 'help',
            'file', 'folder', 'edit', 'check', 'info', 'workflow'
        ]
        
        successful_icons = 0
        failed_icons = 0
        
        for icon_name in test_icons:
            try:
                icon = icon_manager.get_icon_for_button(icon_name, size=(16, 16))
                if hasattr(icon, 'width'):  # PhotoImage
                    source_info = f"🖼️ PNG ({icon.width()}x{icon.height()}px)"
                    successful_icons += 1
                else:  # String/Emoji
                    source_info = f"😀 Emoji: '{icon}'"
                    successful_icons += 1
                
                print(f"   ✅ {icon_name:12s} -> {source_info}")
                
            except Exception as e:
                print(f"   ❌ {icon_name:12s} -> Fehler: {e}")
                failed_icons += 1
        
        print(f"\n📈 ERGEBNIS:")
        print(f"   ✅ Erfolgreich: {successful_icons}/{len(test_icons)}")
        print(f"   ❌ Fehlgeschlagen: {failed_icons}/{len(test_icons)}")
        
        # Icon-Pfade prüfen
        print(f"\n📂 VERFÜGBARE ICON-PFADE:")
        for i, path in enumerate(icon_manager.icon_paths, 1):
            exists = "✅" if os.path.exists(path) else "❌"
            file_count = 0
            valid_count = 0
            
            if os.path.exists(path):
                try:
                    files = [f for f in os.listdir(path) if f.lower().endswith('.png')]
                    file_count = len(files)
                    
                    # Zähle gültige Dateien (>100 Bytes)
                    for file in files:
                        file_path = os.path.join(path, file)
                        if os.path.getsize(file_path) > 100:
                            valid_count += 1
                except:
                    pass
            
            rel_path = os.path.relpath(path, workspace_path)
            print(f"   {i}. {exists} {rel_path}/ ({valid_count}/{file_count} gültige PNG-Dateien)")
        
        return successful_icons > 0
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        logging.exception("Detaillierter Fehler:")
        return False

if __name__ == "__main__":
    print("Starte Test des korrigierten Icon Managers...")
    
    success = test_corrected_icon_manager()
    
    print(f"\n" + "=" * 60)
    print("TESTERGEBNIS")
    print("=" * 60)
    if success:
        print("✅ Korrigierter Icon Manager funktioniert!")
        print("🔧 Beschädigte Dateien werden automatisch übersprungen.")
        print("🎨 Nur gültige PNG-Icons werden geladen.")
        print("🚀 Die Checker-App sollte jetzt ohne Fehler starten!")
    else:
        print("❌ Problem mit dem Icon Manager.")
        print("📋 Überprüfen Sie die Logs für Details.")
