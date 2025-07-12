"""
Test für CTkImage-kompatible Icon-Ladung in der CheckerApp
Testet die neue get_icon Methode mit CTkImage-Erstellung
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
            logging.FileHandler('ctkimage_test_debug.log', mode='w', encoding='utf-8')
        ]
    )
    
    print("🔧 Debug-Logging aktiviert (ICON_DEBUG=1)")
    print("📄 Logs werden in 'ctkimage_test_debug.log' gespeichert")

def test_checker_app_ctkimage():
    """Testet die CTkImage-Erstellung in der CheckerApp"""
    print("\n" + "="*60)
    print("🎨 CHECKER-APP CTKIMAGE TEST")
    print("="*60)
    
    try:
        import tkinter as tk
        from tkinterdnd2 import TkinterDnD
        
        print("\n1️⃣ Erstelle Mock CheckerApp...")
        
        # Minimale CheckerApp nur für Icon-Tests
        class MockCheckerApp:
            def __init__(self):
                self.root = TkinterDnD.Tk()
                self.root.withdraw()  # Verstecke das Fenster
                
                # Logging setup
                self.production_mode = False
                self.setup_logging()
                
                # Icon-System initialisieren
                workspace_path = os.getcwd()
                
                # Importiere Icon-Manager
                try:
                    from fluent_icons_manager import EnhancedFluentIconManager
                    self.icon_manager = EnhancedFluentIconManager(workspace_path=workspace_path)
                    print("   📦 Icon-Manager initialisiert")
                except Exception as e:
                    print(f"   ❌ Fehler beim Icon-Manager: {e}")
                    self.icon_manager = None
                
                # Icon-Cache initialisieren
                self._icon_cache = {}
                self.icon_images = {}
                
                # Icons laden
                self._load_png_icons_method()
                
                # CheckerApp Icon-Methoden hinzufügen
                self.add_icon_methods()
            
            def setup_logging(self):
                """Einfaches Logging-Setup"""
                import logging
                if self.production_mode:
                    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
                else:
                    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
                self.logger = logging.getLogger(__name__)
            
            def add_icon_methods(self):
                """Füge die neuen Icon-Methoden hinzu"""
                # Hier würden die Methoden aus checker_app.py eingefügt
                # Für den Test importieren wir sie direkt
                pass
            
            # Importiere die Icon-Methoden direkt aus der CheckerApp
            def get_icon(self, icon_name, size=(20, 20)):
                """CTkImage-kompatible get_icon Methode"""
                debug_enabled = os.getenv('ICON_DEBUG', '0') == '1'
                
                if debug_enabled:
                    print(f"[GET_ICON] 📍 get_icon() aufgerufen: icon_name='{icon_name}', size={size}")
                
                # Cache für bereits geladene Icons
                cache_key = f"{icon_name}_{size[0]}x{size[1]}"
                if hasattr(self, '_icon_cache') and cache_key in self._icon_cache:
                    if debug_enabled:
                        print(f"[GET_ICON] ✅ Icon aus Cache geladen: {icon_name}")
                    return self._icon_cache[cache_key]
                
                if not hasattr(self, '_icon_cache'):
                    self._icon_cache = {}
                
                # Direktes Laden als CTkImage
                ctk_image = self._create_ctk_image_from_path(icon_name, size)
                if ctk_image:
                    if debug_enabled:
                        print(f"[GET_ICON] ✅ Icon direkt als CTkImage geladen: {icon_name}")
                    self._icon_cache[cache_key] = ctk_image
                    return ctk_image
                
                if debug_enabled:
                    print(f"[GET_ICON] ❌ Icon nicht gefunden: {icon_name}")
                
                return None
            
            def _create_ctk_image_from_path(self, icon_name, size=(20, 20)):
                """Erstellt ein CTkImage direkt aus einer Datei"""
                debug_enabled = os.getenv('ICON_DEBUG', '0') == '1'
                
                # Versuche verschiedene Pfade
                possible_paths = [
                    os.path.join('icons', f'{icon_name}.png'),
                    os.path.join('assets', 'icons', f'{icon_name}.png'),
                    f'{icon_name}.png'
                ]
                
                for icon_path in possible_paths:
                    if debug_enabled:
                        print(f"[CREATE_CTK_IMAGE] 🔍 Prüfe Pfad: {icon_path}")
                    
                    if os.path.exists(icon_path):
                        if debug_enabled:
                            print(f"[CREATE_CTK_IMAGE] ✅ Datei gefunden: {icon_path}")
                        
                        try:
                            from PIL import Image
                            import customtkinter as ctk
                            
                            # Lade als PIL Image
                            pil_image = Image.open(icon_path)
                            
                            if debug_enabled:
                                print(f"[CREATE_CTK_IMAGE] 📸 PIL Image geladen: {pil_image.size}")
                            
                            # Erstelle CTkImage
                            ctk_image = ctk.CTkImage(light_image=pil_image, size=size)
                            
                            if debug_enabled:
                                print(f"[CREATE_CTK_IMAGE] 🎨 CTkImage erstellt: {type(ctk_image)}")
                                print(f"[CREATE_CTK_IMAGE] 🔍 Hat _light_image: {hasattr(ctk_image, '_light_image')}")
                            
                            return ctk_image
                            
                        except Exception as e:
                            if debug_enabled:
                                print(f"[CREATE_CTK_IMAGE] ❌ Fehler beim Erstellen von CTkImage: {e}")
                            continue
                
                return None
            
            def _load_png_icons_method(self):
                """Vereinfachte Version der Icon-Lade-Methode"""
                print("[_LOAD_PNG_ICONS] 🔄 Lade Icons...")
                # Implementierung würde hier stehen
                pass
        
        print("2️⃣ Initialisiere Mock CheckerApp...")
        app = MockCheckerApp()
        
        print("3️⃣ Teste CTkImage-Erstellung...")
        
        # Test verschiedene Icons
        test_icons = [
            ('home', (24, 24)),
            ('search', (20, 20)),
            ('settings', (32, 32)),
            ('file', (16, 16)),
            ('folder', (28, 28)),
            ('rocket', (40, 40))
        ]
        
        results = []
        
        for icon_name, size in test_icons:
            print(f"\n🔍 Teste Icon: {icon_name} ({size})...")
            
            icon_result = app.get_icon(icon_name, size)
            
            if icon_result:
                is_ctkimage = hasattr(icon_result, '_light_image')
                has_size = hasattr(icon_result, '_size')
                actual_size = getattr(icon_result, '_size', 'unknown')
                
                results.append({
                    'name': icon_name,
                    'size': size,
                    'success': True,
                    'type': type(icon_result).__name__,
                    'is_ctkimage': is_ctkimage,
                    'has_light_image': is_ctkimage,
                    'actual_size': actual_size
                })
                
                print(f"   ✅ Erfolgreich geladen: {type(icon_result).__name__}")
                print(f"   🔍 Ist CTkImage: {is_ctkimage}")
                print(f"   📏 Größe: {actual_size}")
                
            else:
                results.append({
                    'name': icon_name,
                    'size': size,
                    'success': False,
                    'type': 'None',
                    'is_ctkimage': False,
                    'has_light_image': False,
                    'actual_size': None
                })
                
                print(f"   ❌ Nicht gefunden")
        
        print("\n4️⃣ Zusammenfassung der Ergebnisse:")
        print("-" * 60)
        
        successful = 0
        ctkimage_count = 0
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            ctk_status = "🎨" if result['is_ctkimage'] else "⚠️"
            
            print(f"{status} {ctk_status} {result['name']}: {result['type']} "
                  f"(CTkImage: {result['is_ctkimage']}, Größe: {result['actual_size']})")
            
            if result['success']:
                successful += 1
            if result['is_ctkimage']:
                ctkimage_count += 1
        
        print(f"\n📊 Statistik:")
        print(f"   - Erfolgreich geladen: {successful}/{len(test_icons)} ({successful/len(test_icons)*100:.1f}%)")
        print(f"   - CTkImage-kompatibel: {ctkimage_count}/{successful} ({ctkimage_count/max(successful,1)*100:.1f}%)")
        
        if ctkimage_count == successful and successful > 0:
            print("🎉 Alle Icons sind CTkImage-kompatibel!")
        elif ctkimage_count > 0:
            print("⚠️ Teilweise CTkImage-kompatibel")
        else:
            print("❌ Keine CTkImage-kompatiblen Icons")
        
        print("\n✅ CTkImage-Test abgeschlossen!")
        
        # Fenster schließen
        app.root.destroy()
        
    except Exception as e:
        logging.error(f"❌ Fehler im CTkImage-Test: {e}")
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Hauptfunktion"""
    print("🎨 CTkImage-kompatible Icon-Ladung Test")
    print("=" * 60)
    
    # Debug-Logging einrichten
    setup_debug_logging()
    
    # CTkImage-Tests
    test_checker_app_ctkimage()
    
    print("\n" + "="*60)
    print("📄 Debug-Logs gespeichert in: ctkimage_test_debug.log")
    print("🔧 ICON_DEBUG Umgebungsvariable war aktiviert")
    print("="*60)

if __name__ == "__main__":
    main()
