"""
Schnelle Übersicht der verfügbaren PNG-Icons in der Checker-App
"""

import os

def show_png_icons_overview():
    """Zeigt eine Übersicht der verfügbaren PNG-Icons"""
    print("=" * 60)
    print("🖼️ PNG-ICONS ÜBERSICHT FÜR CHECKER-APP")
    print("=" * 60)
    
    try:
        from fluent_icons_manager import FluentIconManager
        
        # Icon Manager initialisieren
        icon_manager = FluentIconManager(workspace_path=os.getcwd())
        
        # Verfügbare Icons kategorisieren
        available_icons = icon_manager.list_available_icons()
        
        local_icons = []
        emoji_icons = []
        
        for name, source in available_icons.items():
            if source == "local":
                local_icons.append(name)
            elif source == "emoji":
                emoji_icons.append(name)
        
        print(f"📊 STATISTIK:")
        print(f"   🖼️ Lokale PNG-Icons: {len(local_icons)}")
        print(f"   😀 Emoji-Icons: {len(emoji_icons)}")
        print(f"   📁 Icon-Pfade geprüft: {len(icon_manager.icon_paths)}")
        
        # Wichtige Icons für die App
        app_icons = [
            'home', 'settings', 'help', 'search', 'close',
            'file', 'folder', 'edit', 'check', 'info',
            'workflow', 'user', 'projects', 'toolbox',
            'menu', 'play', 'restart', 'bookmark',
            'idea', 'connect', 'share', 'plus'
        ]
        
        print(f"\n🎯 WICHTIGE APP-ICONS:")
        png_count = 0
        for icon_name in app_icons:
            local_path = icon_manager._find_local_icon(icon_name)
            if local_path:
                filename = os.path.basename(local_path)
                print(f"   🖼️ {icon_name:12s} -> {filename}")
                png_count += 1
            else:
                emoji = icon_manager.get_icon_for_button(icon_name)
                print(f"   😀 {icon_name:12s} -> {emoji}")
        
        print(f"\n✅ Von {len(app_icons)} wichtigen Icons sind {png_count} als PNG verfügbar!")
        
        # PNG-Dateien nach Ordnern
        print(f"\n📂 PNG-DATEIEN NACH ORDNERN:")
        for icon_path in icon_manager.icon_paths:
            if os.path.exists(icon_path):
                png_files = [f for f in os.listdir(icon_path) if f.lower().endswith('.png')]
                if png_files:
                    rel_path = os.path.relpath(icon_path, os.getcwd())
                    print(f"   📁 {rel_path}/ ({len(png_files)} Dateien)")
                    # Top 10 zeigen
                    for filename in sorted(png_files)[:10]:
                        size_kb = os.path.getsize(os.path.join(icon_path, filename)) / 1024
                        print(f"      • {filename} ({size_kb:.1f} KB)")
                    if len(png_files) > 10:
                        print(f"      ... und {len(png_files) - 10} weitere")
        
        print(f"\n🎉 PNG-Icons Integration erfolgreich!")
        print(f"💡 Ihre Checker-App verwendet jetzt lokale PNG-Dateien anstatt Emojis.")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = show_png_icons_overview()
    
    if success:
        print(f"\n🚀 NÄCHSTE SCHRITTE:")
        print(f"   1. Starten Sie die Checker-App: python checker_app.py")
        print(f"   2. Achten Sie auf die PNG-Icons in der Welcome Screen")
        print(f"   3. Testen Sie die Workflow-Buttons mit den neuen Icons")
        print(f"   4. Bei Bedarf können Sie weitere Icons hinzufügen")
    else:
        print(f"\n⚠️ Bitte überprüfen Sie die Installation und versuchen Sie es erneut.")
