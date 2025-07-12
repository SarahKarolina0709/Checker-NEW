"""
Test für die Enhanced Fluent Icons Integration mit lokalen PNG-Dateien
"""

import os
import sys
import logging
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_enhanced_icon_manager():
    """Testet den Enhanced Icon Manager mit lokalen Icons"""
    print("=" * 60)
    print("TESTE ENHANCED FLUENT ICON MANAGER MIT LOKALEN PNG-DATEIEN")
    print("=" * 60)
    
    try:
        # Enhanced Icon Manager importieren
        from fluent_icons_manager import FluentIconManager
        
        # Manager mit aktuellem Workspace initialisieren
        workspace_path = os.getcwd()
        icon_manager = FluentIconManager(workspace_path=workspace_path)
        
        print(f"\n✅ Icon Manager erfolgreich initialisiert")
        print(f"📁 Workspace: {workspace_path}")
        
        # Statistiken anzeigen
        stats = icon_manager.get_stats()
        print(f"\n📊 Icon-Statistiken:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Verfügbare lokale Icons auflisten
        print(f"\n🖼️ Verfügbare lokale Icons:")
        local_icons = [name for name, source in icon_manager.list_available_icons().items() if source == "local"]
        for i, icon_name in enumerate(sorted(local_icons)[:20]):  # Erste 20 anzeigen
            print(f"   {i+1:2d}. {icon_name}")
        if len(local_icons) > 20:
            print(f"   ... und {len(local_icons) - 20} weitere")
        
        print(f"\n🧪 TESTE ICON-ABRUF:")
        
        # Test verschiedener Icons
        test_icons = [
            'home', 'settings', 'search', 'close', 'help',
            'file', 'folder', 'edit', 'check', 'info',
            'workflow', 'user', 'projects', 'toolbox'
        ]
        
        for icon_name in test_icons:
            icon = icon_manager.get_icon_for_button(icon_name, size=(16, 16))
            icon_type = type(icon).__name__
            
            if hasattr(icon, 'width'):  # PhotoImage
                source_info = f"📷 PNG ({icon.width()}x{icon.height()}px)"
            else:  # String/Emoji
                source_info = f"😀 Emoji/Text: '{icon}'"
            
            print(f"   {icon_name:12s} -> {source_info}")
        
        # Test lokaler Icon-Pfade
        print(f"\n📂 TESTE LOKALE ICON-PFADE:")
        for icon_path in icon_manager.icon_paths:
            exists = "✅" if os.path.exists(icon_path) else "❌"
            file_count = 0
            if os.path.exists(icon_path):
                try:
                    files = [f for f in os.listdir(icon_path) if f.lower().endswith('.png')]
                    file_count = len(files)
                except:
                    pass
            print(f"   {exists} {icon_path} ({file_count} PNG-Dateien)")
        
        # Test Fallback-Funktionalität
        print(f"\n🔄 TESTE FALLBACK-FUNKTIONALITÄT:")
        
        # Nicht existierendes Icon (sollte auf Emoji zurückfallen)
        non_existing_icon = icon_manager.get_icon_for_button('nonexistent_icon_xyz')
        print(f"   Nicht existierendes Icon: {type(non_existing_icon).__name__} = '{non_existing_icon}'")
        
        # Mapping-Test
        print(f"\n🗺️ TESTE ICON-MAPPING:")
        mapping_tests = [
            ('home', 'home.png'),
            ('settings', 'settings.png'),
            ('user', 'about.png'),
            ('check', 'check-mark.png')
        ]
        
        for icon_name, expected_file in mapping_tests:
            local_path = icon_manager._find_local_icon(icon_name)
            if local_path:
                filename = os.path.basename(local_path)
                status = "✅" if filename == expected_file else f"⚠️ ({filename})"
            else:
                status = "❌ Nicht gefunden"
            print(f"   {icon_name:12s} -> {status}")
        
        print(f"\n✅ Enhanced Icon Manager Test erfolgreich abgeschlossen!")
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        logging.exception("Detaillierter Fehler:")
        return False

def test_icon_ui_integration():
    """Testet die Integration in einer UI-Komponente"""
    print(f"\n" + "=" * 60)
    print("TESTE UI-INTEGRATION MIT PNG-ICONS")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from fluent_icons_manager import FluentIconManager
        
        # Test-Fenster erstellen
        root = tk.Tk()
        root.title("Icon Integration Test")
        root.geometry("400x300")
        
        # Icon Manager initialisieren
        icon_manager = FluentIconManager(workspace_path=os.getcwd())
        
        # Test-Frame
        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Enhanced Icon Manager - PNG Integration Test", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Test-Icons anzeigen
        test_icons = ['home', 'settings', 'search', 'file', 'check', 'user']
        
        for i, icon_name in enumerate(test_icons):
            icon_frame = tk.Frame(frame)
            icon_frame.pack(fill='x', pady=2)
            
            # Icon abrufen
            icon = icon_manager.get_icon_for_button(icon_name, size=(24, 24))
            
            if hasattr(icon, 'width'):  # PhotoImage
                # PNG-Icon als Button
                btn = tk.Button(icon_frame, image=icon, width=30, height=30)
                btn.pack(side='left', padx=5)
                
                # Icon-Info
                info_text = f"{icon_name}: PNG ({icon.width()}x{icon.height()}px)"
                tk.Label(icon_frame, text=info_text).pack(side='left', padx=10)
                
                # Referenz halten (wichtig für PhotoImage)
                btn.image = icon
                
            else:  # Emoji/Text
                # Text-Icon als Button
                btn = tk.Button(icon_frame, text=icon, width=3, height=1)
                btn.pack(side='left', padx=5)
                
                # Icon-Info
                info_text = f"{icon_name}: Emoji '{icon}'"
                tk.Label(icon_frame, text=info_text).pack(side='left', padx=10)
        
        # Info-Label
        stats = icon_manager.get_stats()
        info_text = f"Lokale Icons: {stats['local_icons']} | Cache: {stats['cached_images']}"
        tk.Label(frame, text=info_text, fg='gray').pack(pady=10)
        
        # Automatisch nach 3 Sekunden schließen
        root.after(3000, root.destroy)
        
        print(f"✅ UI-Test gestartet - Fenster wird 3 Sekunden angezeigt")
        root.mainloop()
        
        print(f"✅ UI-Integration Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ UI-Test Fehler: {e}")
        logging.exception("Detaillierter Fehler:")
        return False

if __name__ == "__main__":
    print("Starte Enhanced Fluent Icons Test...")
    
    # Test 1: Icon Manager Funktionalität
    success1 = test_enhanced_icon_manager()
    
    # Test 2: UI Integration
    success2 = test_icon_ui_integration()
    
    # Ergebnis
    print(f"\n" + "=" * 60)
    print("TESTERGEBNISSE")
    print("=" * 60)
    print(f"Icon Manager Test: {'✅ Erfolgreich' if success1 else '❌ Fehlgeschlagen'}")
    print(f"UI Integration Test: {'✅ Erfolgreich' if success2 else '❌ Fehlgeschlagen'}")
    
    if success1 and success2:
        print(f"\n🎉 Alle Tests erfolgreich! Die lokalen PNG-Icons funktionieren korrekt.")
    else:
        print(f"\n⚠️ Einige Tests sind fehlgeschlagen. Überprüfen Sie die Logs.")
