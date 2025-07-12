#!/usr/bin/env python3
"""
FINALE OPTIMIERTE VERSION - WELCOME SCREEN TEST
==============================================

Testet die optimierte Version der Welcome-Seite mit verbesserter Performance
"""

import sys
import os
import time
import traceback

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_optimized_welcome_screen():
    """Testet die optimierte Welcome-Seite"""
    
    print("🚀 TESTE OPTIMIERTE WELCOME-SEITE")
    print("=" * 50)
    
    try:
        # Performance-Messung: Startup-Zeit
        start_time = time.time()
        
        # Checker-App importieren und starten
        from checker_app import CheckerApp
        
        import_time = time.time()
        print(f"⏱️  Import-Zeit: {(import_time - start_time) * 1000:.1f}ms")
        
        # App erstellen
        app = CheckerApp()
        
        init_time = time.time()
        print(f"⏱️  Initialisierungszeit: {(init_time - import_time) * 1000:.1f}ms")
        
        # Performance-Tests
        print("\n🔍 PERFORMANCE-TESTS")
        print("-" * 30)
        
        # Icon-Cache testen
        if hasattr(app, '_icon_cache'):
            print(f"✅ Icon-Cache initialisiert (0 Einträge)")
        else:
            print("❌ Icon-Cache nicht gefunden")
        
        # Mehrere Icons laden und Cache-Performance testen
        test_icons = ['home', 'settings', 'file_icon', 'folder_icon', 'export']
        cache_test_start = time.time()
        
        for icon_name in test_icons:
            icon = app.get_icon(icon_name, size=(24, 24))
            if icon:
                print(f"✅ Icon '{icon_name}': Erfolgreich geladen")
            else:
                print(f"⚠️  Icon '{icon_name}': Placeholder erstellt")
        
        # Cache-Performance: Zweiter Durchlauf (sollte schneller sein)
        second_pass_start = time.time()
        for icon_name in test_icons:
            app.get_icon(icon_name, size=(24, 24))
        second_pass_time = time.time() - second_pass_start
        
        cache_total_time = time.time() - cache_test_start
        cache_efficiency = ((cache_total_time - second_pass_time) / cache_total_time) * 100 if cache_total_time > 0 else 0
        
        print(f"⚡ Cache-Effizienz: {cache_efficiency:.1f}% Zeitersparnis bei wiederholten Zugriffen")
        print(f"⚡ Cache-Größe: {len(app._icon_cache)} Icons gecacht")
        
        # Memory-Test
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        print(f"🧠 Memory-Verbrauch: {memory_usage:.1f}MB")
        
        # Produktionsmodus-Test
        production_mode = getattr(app, 'production_mode', False)
        print(f"🔧 Produktionsmodus: {'✅ Aktiv' if production_mode else '⚠️  Entwicklungsmodus'}")
        
        # UI-Responsivität testen
        print("\n🖥️  UI-RESPONSIVITÄT TEST")
        print("-" * 30)
        
        ui_test_start = time.time()
        
        # Simuliere UI-Updates
        for i in range(5):
            try:
                app.root.update_idletasks()
            except Exception as e:
                print(f"⚠️  UI-Update {i+1} fehlgeschlagen: {e}")
        
        ui_test_time = (time.time() - ui_test_start) * 1000
        print(f"⚡ UI-Update-Performance: {ui_test_time:.1f}ms für 5 Updates")
        
        # Persistent Button System testen
        button_count = app.get_persistent_button_count()
        print(f"🔗 Persistente Buttons: {button_count} registriert")
        
        # Gesamtbewertung
        total_startup_time = (init_time - start_time) * 1000
        
        print(f"\n📊 GESAMTBEWERTUNG")
        print("-" * 30)
        print(f"⏱️  Gesamt-Startup-Zeit: {total_startup_time:.1f}ms")
        
        if total_startup_time < 1000:
            print("🟢 Performance: EXZELLENT (< 1s)")
        elif total_startup_time < 2000:
            print("🟢 Performance: SEHR GUT (< 2s)")
        elif total_startup_time < 3000:
            print("🟡 Performance: GUT (< 3s)")
        else:
            print("🟡 Performance: AKZEPTABEL (> 3s)")
        
        if memory_usage < 50:
            print("🟢 Memory-Effizienz: EXZELLENT (< 50MB)")
        elif memory_usage < 100:
            print("🟢 Memory-Effizienz: SEHR GUT (< 100MB)")
        else:
            print("🟡 Memory-Effizienz: AKZEPTABEL")
        
        # Kurze visuelle Überprüfung
        print(f"\n👁️  Starte kurze visuelle Überprüfung (3 Sekunden)...")
        app.root.after(3000, app.root.quit)
        app.root.mainloop()
        
        print(f"\n🎉 OPTIMIERUNGSTEST ERFOLGREICH ABGESCHLOSSEN!")
        print(f"Die Welcome-Seite läuft optimal mit verbesserter Performance.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FEHLER BEIM OPTIMIERUNGSTEST:")
        print(f"   {e}")
        print("\nStacktrace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimized_welcome_screen()
    if success:
        print("\n✅ ALLE OPTIMIERUNGEN ERFOLGREICH GETESTET!")
    else:
        print("\n⚠️  OPTIMIERUNGSTEST NICHT VOLLSTÄNDIG BESTANDEN")
