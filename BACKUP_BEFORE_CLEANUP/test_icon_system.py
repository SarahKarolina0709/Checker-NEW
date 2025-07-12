"""
Icon-Customization Test
Demonstriert die Funktionalität des Icon-Systems
"""

from fluent_icons_manager import FluentIconManager
import json
import os

def test_icon_customization():
    """Testet die Icon-Anpassungsfunktionen"""
    
    print("=== Fluent Icons Customization Test ===\n")
    
    # 1. Icon-Manager initialisieren
    print("1. Icon-Manager initialisieren...")
    icon_manager = FluentIconManager("test_icons_config.json")
    print(f"   Theme: {icon_manager.icon_theme}")
    print(f"   Unicode Fallback: {icon_manager.use_unicode_fallback}")
    print(f"   Custom Icons: {len(icon_manager.custom_icons)}")
    
    # 2. Standard-Icons anzeigen
    print("\n2. Standard-Icons (Auswahl):")
    standard_icons = [
        'home', 'search', 'settings', 'workflow', 'user', 'file', 
        'folder', 'success', 'error', 'theme', 'light_mode', 'dark_mode'
    ]
    
    for icon_name in standard_icons:
        icon = icon_manager.get_icon(icon_name)
        print(f"   {icon} {icon_name}")
    
    # 3. Custom Icons hinzufügen
    print("\n3. Custom Icons hinzufügen...")
    custom_icons = {
        'rocket': '🚀',
        'star': '⭐',
        'heart': '❤️',
        'fire': '🔥',
        'lightning': '⚡',
        'magic': '✨'
    }
    
    for name, icon in custom_icons.items():
        icon_manager.set_custom_icon(name, icon)
        print(f"   Custom Icon hinzugefügt: {icon} {name}")
    
    # 4. Theme wechseln
    print("\n4. Theme-Wechsel testen...")
    themes = ['fluent', 'minimal', 'classic', 'custom']
    
    for theme in themes:
        icon_manager.set_theme(theme)
        workflow_icon = icon_manager.get_icon('workflow')
        print(f"   Theme '{theme}': Workflow = {workflow_icon}")
    
    # 5. Icon-Suche testen
    print("\n5. Icon-Suche testen...")
    search_terms = ['file', 'user', 'work', 'star']
    
    for term in search_terms:
        results = icon_manager.search_icons(term)
        print(f"   Suche '{term}': {len(results)} Ergebnisse")
        for name, icon in list(results.items())[:3]:  # Nur erste 3 anzeigen
            print(f"     {icon} {name}")
    
    # 6. Alle verfügbaren Icons
    print("\n6. Statistiken:")
    all_icons = icon_manager.get_all_available_icons()
    print(f"   Gesamt verfügbare Icons: {len(all_icons)}")
    print(f"   Standard Fluent Icons: {len(icon_manager.FLUENT_ICONS)}")
    print(f"   Unicode Alternativen: {len(icon_manager.UNICODE_ALTERNATIVES)}")
    print(f"   Custom Icons: {len(icon_manager.custom_icons)}")
    
    # 7. Konfiguration anzeigen
    print("\n7. Aktuelle Konfiguration:")
    if os.path.exists(icon_manager.config_file):
        with open(icon_manager.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"   Config-Datei: {icon_manager.config_file}")
        print(f"   Theme: {config.get('theme')}")
        print(f"   Version: {config.get('version')}")
        print(f"   Custom Icons: {len(config.get('custom_icons', {}))}")
    
    # 8. Icon-Export testen
    print("\n8. Icon-Export testen...")
    export_success = icon_manager.export_icon_list("test_icon_export.json")
    if export_success:
        print("   ✅ Icon-Liste erfolgreich exportiert")
        if os.path.exists("test_icon_export.json"):
            with open("test_icon_export.json", 'r', encoding='utf-8') as f:
                exported = json.load(f)
            print(f"   Exportierte Icons: {len(exported)}")
    else:
        print("   ❌ Icon-Export fehlgeschlagen")
    
    # 9. Fallback-System testen
    print("\n9. Fallback-System testen...")
    fallback_tests = [
        ('existing_icon', 'home'),
        ('non_existing_icon', 'does_not_exist'),
        ('empty_name', ''),
        ('special_chars', 'icon@#$%')
    ]
    
    for test_name, icon_name in fallback_tests:
        icon = icon_manager.get_icon(icon_name, "❓")
        print(f"   {test_name}: '{icon_name}' → {icon}")
    
    # 10. Performance-Test
    print("\n10. Performance-Test...")
    import time
    
    start_time = time.time()
    for _ in range(1000):
        icon_manager.get_icon('workflow')
    end_time = time.time()
    
    print(f"   1000 Icon-Abrufe: {(end_time - start_time)*1000:.2f}ms")
    
    print("\n=== Test abgeschlossen ===")
    
    # Cleanup
    cleanup_files = [
        "test_icons_config.json",
        "test_icon_export.json"
    ]
    
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleanup: {file} entfernt")

def demonstrate_ui_integration():
    """Zeigt die Integration in UI-Komponenten"""
    
    print("\n=== UI-Integration Beispiele ===\n")
    
    icon_manager = FluentIconManager()
    
    # Beispiel 1: Button-Texte
    print("1. Button-Texte mit Icons:")
    buttons = [
        ('new_workflow', 'Neuer Workflow'),
        ('save', 'Speichern'),
        ('export', 'Exportieren'),
        ('settings', 'Einstellungen'),
        ('help', 'Hilfe')
    ]
    
    for icon_name, text in buttons:
        icon = icon_manager.get_icon(icon_name, '❓')
        button_text = f"{icon} {text}"
        print(f"   Button: '{button_text}'")
    
    # Beispiel 2: Status-Nachrichten
    print("\n2. Status-Nachrichten mit Icons:")
    statuses = [
        ('success', 'Workflow erfolgreich gestartet'),
        ('error', 'Fehler beim Laden der Datei'),
        ('warning', 'Achtung: Datei bereits vorhanden'),
        ('info', 'Neue Version verfügbar'),
        ('loading', 'Daten werden geladen...')
    ]
    
    for icon_name, message in statuses:
        icon = icon_manager.get_icon(icon_name, '❓')
        status_text = f"{icon} {message}"
        print(f"   Status: '{status_text}'")
    
    # Beispiel 3: Menü-Einträge
    print("\n3. Menü-Einträge mit Icons:")
    menu_items = [
        ('home', 'Startseite'),
        ('customer', 'Kunden verwalten'),
        ('workflow', 'Workflows'),
        ('analytics', 'Berichte'),
        ('settings', 'Einstellungen'),
        ('help', 'Hilfe & Support')
    ]
    
    for icon_name, text in menu_items:
        icon = icon_manager.get_icon(icon_name, '❓')
        menu_text = f"{icon} {text}"
        print(f"   Menü: '{menu_text}'")
    
    print("\n=== UI-Integration Demo abgeschlossen ===")

if __name__ == "__main__":
    test_icon_customization()
    demonstrate_ui_integration()
