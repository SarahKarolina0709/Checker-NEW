"""
Test der FluentIcons 2.0.0 Bibliothek
"""

def test_fluent_icons_2():
    print("🔍 Teste FluentIcons 2.0.0 Bibliothek")
    print("=" * 50)
    
    # Test verschiedene Import-Möglichkeiten
    import_attempts = [
        "FluentIcons",
        "fluenticons", 
        "fluent_icons",
        "FluentIcons.icons",
        "FluentIcons.core"
    ]
    
    successful_imports = []
    
    for attempt in import_attempts:
        try:
            module = __import__(attempt)
            print(f"✅ {attempt} erfolgreich importiert")
            print(f"   Attribute: {[attr for attr in dir(module) if not attr.startswith('_')][:10]}...")
            successful_imports.append((attempt, module))
        except ImportError as e:
            print(f"❌ {attempt} fehlgeschlagen: {e}")
    
    # Teste die erfolgreichen Imports
    print(f"\n🔍 Detaillierte Tests:")
    
    for name, module in successful_imports:
        print(f"\n📦 {name}:")
        try:
            # Suche nach Icon-bezogenen Funktionen/Klassen
            attrs = [attr for attr in dir(module) if not attr.startswith('_')]
            icon_attrs = [attr for attr in attrs if 'icon' in attr.lower() or 'fluent' in attr.lower()]
            
            print(f"   Icon-bezogene Attribute: {icon_attrs}")
            
            # Versuche häufige Icon-Namen
            test_icons = ['Settings', 'Home', 'File', 'User', 'Search']
            for icon_name in test_icons:
                if hasattr(module, icon_name):
                    icon = getattr(module, icon_name)
                    print(f"   ✅ {icon_name}: {icon}")
                    
        except Exception as e:
            print(f"   ❌ Fehler beim Testen: {e}")

def test_icon_usage():
    print(f"\n" + "=" * 50)
    print("🔍 Teste praktische Icon-Verwendung")
    print("=" * 50)
    
    try:
        # Häufigste Import-Varianten für FluentIcons
        from FluentIcons import *
        print("✅ 'from FluentIcons import *' erfolgreich")
        
        # Teste, ob spezifische Icons verfügbar sind
        icon_tests = [
            'Settings', 'SettingsIcon', 'SETTINGS',
            'Home', 'HomeIcon', 'HOME', 
            'File', 'FileIcon', 'FILE',
            'User', 'UserIcon', 'USER'
        ]
        
        available_icons = []
        for icon_name in icon_tests:
            try:
                icon = globals().get(icon_name)
                if icon:
                    available_icons.append((icon_name, icon))
                    print(f"   ✅ {icon_name}: {icon}")
            except:
                pass
        
        if available_icons:
            print(f"\n🎉 Gefundene Icons: {len(available_icons)}")
            return True
        else:
            print(f"\n❌ Keine verwendbaren Icons gefunden")
            return False
            
    except Exception as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Teste echte FluentIcons Python-Bibliothek")
    print()
    
    test_fluent_icons_2()
    success = test_icon_usage()
    
    if success:
        print(f"\n✅ FluentIcons Bibliothek ist verwendbar!")
        print(f"💡 Wir können unseren FluentIconManager erweitern!")
    else:
        print(f"\n❌ FluentIcons Bibliothek nicht praktisch verwendbar")
        print(f"💡 Unser eigener FluentIconManager ist die beste Lösung")
