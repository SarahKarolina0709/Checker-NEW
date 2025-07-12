"""
Schneller Test für die neuen Icons in der Checker-App
"""

def test_icons_quick():
    """Schneller Test der Icon-Integration"""
    
    print("🎨 Schneller Icons-Test")
    print("=" * 40)
    
    try:
        from fluent_icons_manager import FluentIconManager
        
        # Icon-Manager testen
        icon_manager = FluentIconManager()
        print("✅ Icon-Manager geladen")
        
        # Alle für Welcome Screen benötigten Icons testen
        required_icons = [
            'file', 'projects', 'settings', 'help',
            'user', 'workflow', 'analytics', 'quality', 
            'complete', 'project', 'theme', 'warning'
        ]
        
        print("\n🔍 Icon-Verfügbarkeit:")
        missing_icons = []
        
        for icon_name in required_icons:
            icon = icon_manager.get_icon(icon_name, "❌")
            if icon == "❌":
                missing_icons.append(icon_name)
                print(f"   ❌ {icon_name} - FEHLT")
            else:
                print(f"   ✅ {icon_name} - {icon}")
        
        if missing_icons:
            print(f"\n⚠️ Fehlende Icons: {', '.join(missing_icons)}")
        else:
            print(f"\n🎉 Alle Icons verfügbar!")
        
        # Test Welcome Screen Icons direkt
        print(f"\n📱 UI-Elemente mit Icons:")
        ui_elements = [
            ('Header-Menü "Datei"', icon_manager.get_icon('file')),
            ('Header-Menü "Projekte"', icon_manager.get_icon('projects')),
            ('Header-Menü "Einstellungen"', icon_manager.get_icon('settings')),
            ('Header-Menü "Hilfe"', icon_manager.get_icon('help')),
            ('Kundenmanagement', icon_manager.get_icon('user')),
            ('Workflow-Bereich', icon_manager.get_icon('workflow')),
            ('Angebotsanalyse', icon_manager.get_icon('analytics')),
            ('Qualitätsprüfung', icon_manager.get_icon('quality')),
            ('Finalisierung', icon_manager.get_icon('complete')),
            ('Projektübersicht', icon_manager.get_icon('project'))
        ]
        
        for element, icon in ui_elements:
            print(f"   {icon} {element}")
        
        print(f"\n💡 So starten Sie die App mit den neuen Icons:")
        print(f"   python checker_app.py")
        
        return len(missing_icons) == 0
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = test_icons_quick()
    
    if success:
        print(f"\n✅ Alle Icons sind bereit!")
        print(f"\n🚀 Starten Sie jetzt: python checker_app.py")
    else:
        print(f"\n❌ Es gibt noch Icon-Probleme")
