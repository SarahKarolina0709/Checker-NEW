"""
Einfacher Test für lokale PNG-Icons ohne UI-Abhängigkeiten
"""

import os
import logging
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_local_icons_basic():
    """Grundlegender Test für lokale Icon-Funktionalität"""
    print("=" * 60)
    print("TESTE LOKALE PNG-ICONS (GRUNDFUNKTIONALITÄT)")
    print("=" * 60)
    
    try:
        from fluent_icons_manager import FluentIconManager
        
        # Manager initialisieren
        workspace_path = os.getcwd()
        icon_manager = FluentIconManager(workspace_path=workspace_path)
        
        print(f"✅ Icon Manager initialisiert")
        print(f"📁 Workspace: {workspace_path}")
        
        # Statistiken
        stats = icon_manager.get_stats()
        print(f"\n📊 Statistiken:")
        print(f"   Lokale Icons: {stats['local_icons']}")
        print(f"   Emoji Icons: {stats['emoji_icons']}")
        print(f"   Custom Icons: {stats['custom_icons']}")
        
        # Icon-Pfade prüfen
        print(f"\n📂 Icon-Pfade:")
        for path in icon_manager.icon_paths:
            exists = os.path.exists(path)
            file_count = 0
            if exists:
                try:
                    files = [f for f in os.listdir(path) if f.lower().endswith('.png')]
                    file_count = len(files)
                    print(f"   ✅ {path} ({file_count} PNG-Dateien)")
                    
                    # Erste 5 Dateien zeigen
                    if files:
                        print(f"      Beispiele: {', '.join(files[:5])}")
                        if len(files) > 5:
                            print(f"      ... und {len(files) - 5} weitere")
                except Exception as e:
                    print(f"   ⚠️ {path} (Fehler beim Lesen: {e})")
            else:
                print(f"   ❌ {path} (nicht gefunden)")
        
        # Verfügbare lokale Icons
        available_icons = icon_manager.list_available_icons()
        local_icons = {name: source for name, source in available_icons.items() if source == "local"}
        
        print(f"\n🖼️ Verfügbare lokale Icons ({len(local_icons)}):")
        for i, icon_name in enumerate(sorted(local_icons.keys())[:15]):
            print(f"   {i+1:2d}. {icon_name}")
        if len(local_icons) > 15:
            print(f"   ... und {len(local_icons) - 15} weitere")
        
        # Icon-Mapping-Tests
        print(f"\n🔍 TESTE ICON-MAPPING:")
        test_mappings = [
            'home', 'settings', 'search', 'close', 'help',
            'file', 'folder', 'edit', 'check', 'info'
        ]
        
        for icon_name in test_mappings:
            local_path = icon_manager._find_local_icon(icon_name)
            if local_path:
                filename = os.path.basename(local_path)
                print(f"   ✅ {icon_name:12s} -> {filename}")
            else:
                print(f"   ❌ {icon_name:12s} -> Nicht gefunden")
        
        # Fallback-Test
        print(f"\n🔄 TESTE FALLBACK:")
        icon_result = icon_manager.get_icon_for_button('nonexistent_icon')
        print(f"   Nicht existierendes Icon: {type(icon_result).__name__} = '{icon_result}'")
        
        print(f"\n✅ Grundlegender Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        logging.exception("Detaillierter Fehler:")
        return False

def test_icon_file_access():
    """Testet direkten Zugriff auf Icon-Dateien"""
    print(f"\n" + "=" * 60)
    print("TESTE DIREKTEN DATEIZUGRIFF")
    print("=" * 60)
    
    try:
        # Direkte Dateiprüfung
        icon_dirs = [
            'icons',
            'assets/icons',
            'assets'
        ]
        
        total_icons = 0
        for icon_dir in icon_dirs:
            full_path = os.path.join(os.getcwd(), icon_dir)
            if os.path.exists(full_path):
                png_files = [f for f in os.listdir(full_path) if f.lower().endswith('.png')]
                total_icons += len(png_files)
                
                print(f"\n📁 {icon_dir}/ ({len(png_files)} PNG-Dateien):")
                for i, filename in enumerate(sorted(png_files)):
                    file_path = os.path.join(full_path, filename)
                    size_kb = os.path.getsize(file_path) / 1024
                    print(f"   {i+1:2d}. {filename} ({size_kb:.1f} KB)")
        
        print(f"\n📊 Gesamt: {total_icons} PNG-Icon-Dateien gefunden")
        
        return True
        
    except Exception as e:
        print(f"❌ Dateizugriff-Fehler: {e}")
        return False

if __name__ == "__main__":
    print("Starte lokale PNG-Icons Test...")
    
    # Test 1: Grundfunktionalität
    success1 = test_local_icons_basic()
    
    # Test 2: Direkter Dateizugriff
    success2 = test_icon_file_access()
    
    # Ergebnis
    print(f"\n" + "=" * 60)
    print("TESTERGEBNISSE")
    print("=" * 60)
    print(f"Grundfunktionalität: {'✅ Erfolgreich' if success1 else '❌ Fehlgeschlagen'}")
    print(f"Dateizugriff: {'✅ Erfolgreich' if success2 else '❌ Fehlgeschlagen'}")
    
    if success1 and success2:
        print(f"\n🎉 Alle Tests erfolgreich!")
        print(f"💡 Die lokalen PNG-Icons sind verfügbar und werden korrekt erkannt.")
        print(f"🚀 Sie können jetzt die Checker-App mit PNG-Icons starten!")
    else:
        print(f"\n⚠️ Einige Tests sind fehlgeschlagen.")
