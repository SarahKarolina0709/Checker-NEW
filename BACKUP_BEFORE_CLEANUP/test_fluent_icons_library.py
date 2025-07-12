"""
Test der fluent-icons Python-Bibliothek
"""

def test_fluent_icons_library():
    """Testet die fluent-icons Python-Bibliothek"""
    
    print("🔍 Test der fluent-icons Python-Bibliothek")
    print("=" * 50)
    
    try:
        # Test 1: Import der Bibliothek
        print("1. Versuche fluent-icons zu importieren...")
        
        try:
            from fluenticons import FluentIcon
            print("✅ Import von fluenticons.FluentIcon erfolgreich")
            
            # Test 2: Icon erstellen
            icon = FluentIcon('settings')
            print(f"✅ FluentIcon('settings') erstellt: {icon}")
            
        except ImportError as e:
            print(f"❌ Import von fluenticons.FluentIcon fehlgeschlagen: {e}")
            
            # Alternative Imports testen
            try:
                import fluenticons
                print(f"✅ Alternative: import fluenticons erfolgreich")
                print(f"   Verfügbare Attribute: {dir(fluenticons)}")
            except ImportError:
                print("❌ Auch 'import fluenticons' fehlgeschlagen")
        
        # Test 3: Andere mögliche Import-Varianten
        print("\n2. Teste alternative Import-Möglichkeiten...")
        
        alternative_imports = [
            "fluent_icons",
            "fluent.icons", 
            "fluentui.icons",
            "microsoft.fluentui"
        ]
        
        for import_name in alternative_imports:
            try:
                __import__(import_name)
                print(f"✅ {import_name} verfügbar")
            except ImportError:
                print(f"❌ {import_name} nicht verfügbar")
        
        return True
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

def test_alternative_libraries():
    """Testet alternative Icon-Bibliotheken"""
    
    print(f"\n" + "=" * 50)
    print("🔍 Test alternativer Icon-Bibliotheken")
    print("=" * 50)
    
    # Mögliche alternative Bibliotheken
    alternatives = [
        "fluenticons",
        "microsoft-fluent-icons", 
        "fluent-ui-icons",
        "mdi-icons",
        "material-design-icons",
        "fontawesome"
    ]
    
    for lib in alternatives:
        try:
            __import__(lib.replace('-', '_'))
            print(f"✅ {lib} ist installiert")
        except ImportError:
            print(f"❌ {lib} nicht installiert")

if __name__ == "__main__":
    print("🚀 Teste Fluent Icons Python-Bibliotheken")
    print()
    
    test_fluent_icons_library()
    test_alternative_libraries()
    
    print(f"\n💡 Fazit:")
    print(f"Falls keine echte Fluent Icons Bibliothek verfügbar ist,")
    print(f"verwenden wir unseren eigenen FluentIconManager mit Unicode/Emoji.")
