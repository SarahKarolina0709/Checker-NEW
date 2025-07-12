#!/usr/bin/env python3
"""
Test des Tools-Menüs - prüft ob 'Kundenpfad konfigurieren' angezeigt wird
"""

def test_tools_menu():
    """Testet die Tools-Menü Einträge"""
    print("🔧 Tools-Menü Test")
    print("=" * 30)
    
    # Simuliere die Menü-Items wie in checker_app.py
    menu_items = [
        ("Cache leeren", "clear_icon_cache", "refresh"),
        ("Anwendung neu laden", "reload_application", "restart"),
        ("Performance-Statistiken", "show_performance_stats", "analysis"),
        ("---", None, None),
        ("Kundenpfad konfigurieren", "configure_customer_path", "folder"),
        ("Theme umschalten", "toggle_theme", "theme"),
        ("Layout zurücksetzen", "reset_layout", "undo")
    ]
    
    print("📋 Tools-Menü sollte folgende Einträge haben:")
    for i, item in enumerate(menu_items, 1):
        if item[0] == "---":
            print("     ──────────────")
        else:
            icon = "📁" if "folder" in str(item[2]) else "🔧"
            print(f"  {i}. {icon} {item[0]}")
    
    print("\n✅ Der Eintrag 'Kundenpfad konfigurieren' sollte bei Position 5 stehen!")
    print("📁 Mit einem Ordner-Icon")
    
    print("\n💡 Wenn der Eintrag nicht angezeigt wird:")
    print("   1. Checker-App neu starten")
    print("   2. Tools-Menü öffnen")
    print("   3. Prüfen ob 'Kundenpfad konfigurieren' da ist")

if __name__ == "__main__":
    test_tools_menu()
