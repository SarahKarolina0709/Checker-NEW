"""
Einfacher Test für Python Icon-Bibliotheken
"""

def simple_icon_test():
    print("🔍 Teste installierte Icon-Bibliotheken")
    
    # Test 1: fluent-icons
    try:
        import fluent_icons
        print("✅ fluent_icons importiert")
        print(f"   Inhalt: {dir(fluent_icons)}")
    except ImportError:
        print("❌ fluent_icons nicht verfügbar")
    
    # Test 2: fluenticons  
    try:
        import fluenticons
        print("✅ fluenticons importiert")
        print(f"   Inhalt: {dir(fluenticons)}")
    except ImportError:
        print("❌ fluenticons nicht verfügbar")
    
    # Test 3: Prüfe, was tatsächlich installiert wurde
    try:
        import pip
        import subprocess
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        print(f"\n📦 Installierte Pakete (Auszug):")
        for line in result.stdout.split('\n'):
            if 'fluent' in line.lower() or 'icon' in line.lower():
                print(f"   {line}")
    except:
        print("❌ Konnte installierte Pakete nicht auflisten")

if __name__ == "__main__":
    simple_icon_test()
