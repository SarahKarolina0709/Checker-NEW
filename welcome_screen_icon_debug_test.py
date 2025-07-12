"""
Ultra-Modern Welcome Screen Test mit Icon-Manager Debug-Logging
Testet das erweiterte Debug-Logging im realen Welcome Screen Kontext
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
            logging.FileHandler('welcome_screen_icon_debug.log', mode='w', encoding='utf-8')
        ]
    )
    
    print("🔧 Debug-Logging aktiviert (ICON_DEBUG=1)")
    print("📄 Logs werden in 'welcome_screen_icon_debug.log' gespeichert")

def test_welcome_screen_icons():
    """Testet die Icon-Ladung im Welcome Screen"""
    print("\n" + "="*60)
    print("🎨 WELCOME SCREEN ICON DEBUG-TEST")
    print("="*60)
    
    try:
        import tkinter as tk
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        print("\n1️⃣ Erstelle Test-Fenster...")
        root = tk.Tk()
        root.title("Welcome Screen Icon Debug Test")
        root.geometry("900x600")
        root.withdraw()  # Verstecke das Fenster
        
        # Mock-App und Callback für den Test
        class MockApp:
            def __init__(self, root):
                self.root = root
                # Importiere Icon-Manager für vollständigen Test
                try:
                    from fluent_icons_manager import EnhancedFluentIconManager
                    self.icon_manager = EnhancedFluentIconManager()
                    print("   📦 Icon-Manager in MockApp initialisiert")
                except Exception as e:
                    print(f"   ❌ Fehler beim Initialisieren des Icon-Managers: {e}")
                    self.icon_manager = None
            
            def get_icon(self, icon_name, size=(20, 20)):
                """Mock get_icon Methode mit echtem Icon-Manager"""
                if self.icon_manager:
                    return self.icon_manager.get_icon(icon_name, size)
                return None
        
        mock_app = MockApp(root)
        mock_callback = lambda: print("Mock callback called")
        
        print("2️⃣ Initialisiere Welcome Screen...")
        welcome_screen = UltraModernWelcomeScreen(root, mock_app, mock_callback)
        
        print("3️⃣ Teste safe_get_icon Funktion...")
        
        # Test verschiedene Icon-Anfragen
        test_icons = [
            ('home', (24, 24), "Standard-Home-Icon"),
            ('search', (20, 20), "Such-Icon"),
            ('settings', (32, 32), "Einstellungen-Icon"),
            ('nonexistent', (24, 24), "Nicht-existierendes Icon"),
            ('file', (16, 16), "Datei-Icon"),
            ('folder', (28, 28), "Ordner-Icon")
        ]
        
        results = []
        
        for icon_name, size, description in test_icons:
            print(f"\n🔍 Teste {description} ('{icon_name}', {size})...")
            
            # Verwende safe_get_icon aus dem Welcome Screen
            icon_result = welcome_screen.safe_get_icon(icon_name, size)
            
            result_type = type(icon_result).__name__
            result_value = str(icon_result) if icon_result else "None"
            
            results.append({
                'name': icon_name,
                'size': size,
                'description': description,
                'type': result_type,
                'value': result_value,
                'success': icon_result is not None
            })
            
            print(f"   📊 Ergebnis: {result_type} - {result_value}")
        
        print("\n4️⃣ Debug Icon Availability...")
        welcome_screen.debug_icon_availability()
        
        print("\n5️⃣ Zusammenfassung der Ergebnisse:")
        print("-" * 60)
        successful = 0
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['description']}: {result['type']}")
            if result['success']:
                successful += 1
        
        print(f"\n📊 Erfolgsrate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        
        # Test Cache-Verhalten
        print("\n6️⃣ Test Cache-Verhalten...")
        print("Zweite Anfrage für 'home' Icon (sollte aus Cache kommen):")
        cached_icon = welcome_screen.safe_get_icon('home', (24, 24))
        print(f"   💾 Cache-Ergebnis: {type(cached_icon)} - {cached_icon}")
        
        print("\n✅ Welcome Screen Icon Debug-Test abgeschlossen!")
        
        # Fenster schließen
        root.destroy()
        
    except Exception as e:
        logging.error(f"❌ Fehler im Welcome Screen Debug-Test: {e}")
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Hauptfunktion"""
    print("🎨 Welcome Screen Icon Debug-Test mit erweitertem Logging")
    print("=" * 60)
    
    # Debug-Logging einrichten
    setup_debug_logging()
    
    # Welcome Screen Icon-Tests
    test_welcome_screen_icons()
    
    print("\n" + "="*60)
    print("📄 Debug-Logs gespeichert in: welcome_screen_icon_debug.log")
    print("🔧 ICON_DEBUG Umgebungsvariable war aktiviert")
    print("="*60)

if __name__ == "__main__":
    main()
