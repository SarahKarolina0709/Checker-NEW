"""
Icon-Manager Debug-Test mit ausführlichem Logging
Testet das erweiterte Debug-Logging im FluentIconManager
"""

import os
import sys
import logging
from pathlib import Path

# Pfad zur Checker-App hinzufügen
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_debug_logging():
    """Richtet ausführliches Debug-Logging ein"""
    # Icon-Debug aktivieren
    os.environ['ICON_DEBUG'] = '1'
    
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('icon_manager_debug.log', mode='w', encoding='utf-8')
        ]
    )
    
    print("🔧 Debug-Logging aktiviert (ICON_DEBUG=1)")
    print("📄 Logs werden in 'icon_manager_debug.log' gespeichert")

def test_icon_manager_debug():
    """Testet das Icon-Manager Debug-Logging"""
    print("\n" + "="*60)
    print("🧪 ICON-MANAGER DEBUG-TEST")
    print("="*60)
    
    try:
        # Import nach Logging-Setup
        from fluent_icons_manager import EnhancedFluentIconManager
        
        print("\n1️⃣ Initialisiere Icon-Manager...")
        icon_manager = EnhancedFluentIconManager()
        
        print(f"📁 Konfigurierte Icon-Pfade: {icon_manager.icon_paths}")
        print(f"📊 Verfügbare lokale Icons: {len(icon_manager.available_local_icons)}")
        
        # Test 1: Existierendes Icon laden
        print("\n2️⃣ Test: Existierendes Icon laden (home)")
        home_icon = icon_manager.get_icon('home', size=(24, 24))
        print(f"✅ Ergebnis 'home': {type(home_icon)} - {home_icon}")
        
        # Test 2: Nicht-existierendes Icon
        print("\n3️⃣ Test: Nicht-existierendes Icon (nonexistent)")
        missing_icon = icon_manager.get_icon('nonexistent', size=(24, 24))
        print(f"❌ Ergebnis 'nonexistent': {type(missing_icon)} - {missing_icon}")
        
        # Test 3: PNG-Icon direkt laden
        print("\n4️⃣ Test: PNG-Icon direkt laden (home.png)")
        png_icon = icon_manager.load_png_icon('home.png', size=(32, 32))
        print(f"🖼️ Ergebnis PNG 'home.png': {type(png_icon)} - {png_icon}")
        
        # Test 4: Verschiedene Größen (Cache-Test)
        print("\n5️⃣ Test: Cache-Verhalten bei verschiedenen Größen")
        for size in [(16, 16), (24, 24), (32, 32), (16, 16)]:  # 16x16 zweimal für Cache-Test
            icon = icon_manager.get_icon('search', size=size)
            print(f"🔍 Search-Icon {size}: {type(icon)}")
        
        # Test 5: Icon-Manager Status
        print("\n6️⃣ Icon-Manager Status:")
        print(f"💾 Icon-Cache Einträge: {len(icon_manager.icon_cache)}")
        print(f"🖼️ Image-Cache Einträge: {len(icon_manager.image_cache)}")
        print(f"🎯 Custom Icons: {len(icon_manager.custom_icons)}")
        
        # Test 6: Verfügbare Icons anzeigen
        print("\n7️⃣ Verfügbare lokale Icons (erste 10):")
        available_icons = list(icon_manager.available_local_icons.keys())[:10]
        for icon_name in available_icons:
            print(f"  📎 {icon_name}")
        
        print("\n✅ Icon-Manager Debug-Test abgeschlossen!")
        
    except Exception as e:
        logging.error(f"❌ Fehler im Debug-Test: {e}")
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

def test_icons_directory():
    """Testet das Icons-Verzeichnis"""
    print("\n" + "="*60)
    print("📁 ICONS-VERZEICHNIS ANALYSE")
    print("="*60)
    
    icons_paths = [
        'icons',
        'assets/icons',
        os.path.join(os.getcwd(), 'icons'),
        os.path.join(os.getcwd(), 'assets', 'icons')
    ]
    
    for path in icons_paths:
        print(f"\n🔍 Prüfe Pfad: {path}")
        
        if os.path.exists(path):
            print(f"✅ Pfad existiert: {os.path.abspath(path)}")
            
            try:
                files = os.listdir(path)
                icon_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                
                print(f"📊 Gesamt Dateien: {len(files)}")
                print(f"🖼️ Icon-Dateien: {len(icon_files)}")
                
                if icon_files:
                    print("📋 Icon-Dateien (erste 10):")
                    for icon_file in icon_files[:10]:
                        file_path = os.path.join(path, icon_file)
                        file_size = os.path.getsize(file_path)
                        print(f"  📎 {icon_file} ({file_size} Bytes)")
                        
            except Exception as e:
                print(f"❌ Fehler beim Lesen: {e}")
        else:
            print(f"❌ Pfad existiert nicht: {os.path.abspath(path)}")

def main():
    """Hauptfunktion"""
    print("🔧 Icon-Manager Debug-Test mit erweitertem Logging")
    print("=" * 60)
    
    # Debug-Logging einrichten
    setup_debug_logging()
    
    # Icons-Verzeichnis analysieren
    test_icons_directory()
    
    # Icon-Manager testen
    test_icon_manager_debug()
    
    print("\n" + "="*60)
    print("📄 Debug-Logs gespeichert in: icon_manager_debug.log")
    print("🔧 ICON_DEBUG Umgebungsvariable war aktiviert")
    print("="*60)

if __name__ == "__main__":
    main()
