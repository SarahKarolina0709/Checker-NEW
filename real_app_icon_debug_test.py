"""
Finaler Icon-Debug-Test mit echter Checker-App
Testet das erweiterte Debugging-System mit der realen Anwendungsumgebung
"""

import customtkinter as ctk
import logging
import sys
import os

# Logging für Debug-Ausgaben konfigurieren (ohne Emojis für Windows-Kompatibilität)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('real_app_icon_debug.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def test_real_app_icons():
    """Testet das Icon-Debugging mit der echten Checker-App"""
    try:
        logger.info("=== Starting Real App Icon Debug Test ===")
        
        # CTkinter Setup
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Versuche die echte Checker-App zu importieren
        try:
            from checker_app import CheckerApp
            logger.info("CheckerApp erfolgreich importiert")
        except ImportError as e:
            logger.error(f"Import-Fehler für CheckerApp: {e}")
            logger.info("Versuche alternative Imports...")
            
            # Alternative Import-Versuche
            alternatives = [
                'checker_app_refactored',
                'main',
                'app'
            ]
            
            CheckerApp = None
            for alt in alternatives:
                try:
                    module = __import__(alt)
                    if hasattr(module, 'CheckerApp'):
                        CheckerApp = getattr(module, 'CheckerApp')
                        logger.info(f"CheckerApp aus {alt} erfolgreich importiert")
                        break
                    elif hasattr(module, 'App'):
                        CheckerApp = getattr(module, 'App')
                        logger.info(f"App aus {alt} erfolgreich importiert")
                        break
                except ImportError:
                    continue
            
            if CheckerApp is None:
                logger.error("Keine Checker-App gefunden - verwende Mock")
                return test_with_mock()
        
        # Main Window für die App
        root = ctk.CTk()
        root.title("Real App Icon Debug Test")
        root.geometry("1000x700")
        
        # Checker-App erstellen
        logger.info("Erstelle echte Checker-App...")
        app = CheckerApp()  # CheckerApp erstellt ihr eigenes root
        
        # Das root der App verwenden
        if hasattr(app, 'root'):
            app_root = app.root
            logger.info("Verwende App-eigenes root")
        else:
            app_root = root
            logger.info("Verwende externes root")
        
        # Icon-Manager prüfen
        if hasattr(app, 'icon_manager'):
            logger.info(f"Icon-Manager gefunden: {type(app.icon_manager)}")
            
            if hasattr(app.icon_manager, 'available_icons'):
                available = app.icon_manager.available_icons
                logger.info(f"Verfügbare Icons: {len(available) if available else 0}")
                if available and len(available) > 0:
                    logger.info(f"Erste 10 Icons: {list(available)[:10]}")
            
            # Test einige Icons direkt
            test_icons = ['home', 'settings', 'rocket', 'file_icon', 'person', 'moon', 'sun']
            logger.info("=== Testing Real App Icons ===")
            
            for icon_name in test_icons:
                try:
                    result = app.get_icon(icon_name, size=(24, 24))
                    if result:
                        logger.info(f"SUCCESS: Icon '{icon_name}' loaded - Type: {type(result)}")
                        if hasattr(result, '_light_image'):
                            logger.info(f"  - Has _light_image: {type(result._light_image)}")
                        if hasattr(result, '_size'):
                            logger.info(f"  - CTkImage size: {result._size}")
                    else:
                        logger.warning(f"FAILED: Icon '{icon_name}' returned None")
                except Exception as e:
                    logger.error(f"ERROR: Icon '{icon_name}' - {e}")
        else:
            logger.warning("Kein Icon-Manager in der App gefunden")
        
        # Welcome Screen Test
        try:
            from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
            logger.info("Welcome Screen erfolgreich importiert")
            
            # Welcome Screen erstellen
            logger.info("Erstelle Welcome Screen mit echter App...")
            welcome_screen = UltraModernWelcomeScreen(
                master=app_root,
                app=app,
                app_callback=lambda: logger.info("Welcome Screen Callback aufgerufen")
            )
            welcome_screen.pack(fill="both", expand=True)
            
            logger.info("Welcome Screen erfolgreich mit echter App erstellt")
            
            # Test einige Icon-Aufrufe direkt
            logger.info("=== Testing Welcome Screen safe_get_icon ===")
            test_welcome_icons = ['home', 'rocket', 'settings', 'moon', 'missing_icon']
            
            for icon_name in test_welcome_icons:
                icon, text = welcome_screen.safe_get_icon(icon_name, size=(24, 24), fallback_text="?")
                logger.info(f"safe_get_icon('{icon_name}'): icon={type(icon) if icon else None}, text='{text}'")
            
        except ImportError as e:
            logger.error(f"Welcome Screen Import-Fehler: {e}")
        
        # App kurz anzeigen
        logger.info("Zeige App für 5 Sekunden...")
        app_root.after(5000, app_root.quit)
        app_root.mainloop()
        
        logger.info("=== Real App Icon Debug Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"Test-Fehler: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def test_with_mock():
    """Fallback-Test mit Mock wenn echte App nicht verfügbar"""
    logger.info("Führe Fallback-Test mit Mock-App durch...")
    
    # Hier würde der Mock-Test aus icon_debug_test.py laufen
    try:
        from icon_debug_test import test_welcome_screen_icons
        return test_welcome_screen_icons()
    except ImportError:
        logger.error("Auch Mock-Test nicht verfügbar")
        return False

if __name__ == "__main__":
    logger.info("Realer App Icon Debug Test gestartet")
    success = test_real_app_icons()
    
    if success:
        logger.info("Real App Icon Debug Test erfolgreich abgeschlossen")
        print("\n=== Check real_app_icon_debug.log for detailed analysis ===")
    else:
        logger.error("Real App Icon Debug Test fehlgeschlagen")
    
    # Log-Datei anzeigen
    try:
        with open('real_app_icon_debug.log', 'r', encoding='utf-8') as f:
            log_content = f.read()
            print("\n=== REAL APP DEBUG LOG (Last 1500 chars) ===")
            print(log_content[-1500:])
    except Exception as e:
        print(f"Konnte Log-Datei nicht lesen: {e}")
