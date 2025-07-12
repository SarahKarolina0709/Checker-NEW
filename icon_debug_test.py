"""
Icon Debug Test für Welcome Screen
Testet das erweiterte Debugging-System zur Icon-Problemanalyse
"""

import customtkinter as ctk
import logging
import sys
import os

# Logging für Debug-Ausgaben konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('icon_debug.log')
    ]
)

logger = logging.getLogger(__name__)

class MockApp:
    """Mock-App für Icon-Tests"""
    def __init__(self, root):
        self.root = root
        self.icon_manager = MockIconManager()
        logger.info("MockApp initialisiert")
    
    def get_icon(self, icon_name, size=(24, 24)):
        """Mock get_icon Methode"""
        logger.debug(f"MockApp.get_icon called for '{icon_name}' with size {size}")
        if self.icon_manager:
            return self.icon_manager.get_icon(icon_name, size)
        return None

class MockIconManager:
    """Mock Icon Manager"""
    def __init__(self):
        self.available_icons = ['home', 'settings', 'file_icon', 'rocket', 'moon', 'sun']
        logger.debug(f"MockIconManager initialisiert mit {len(self.available_icons)} Icons")
    
    def get_icon(self, icon_name, size=(24, 24)):
        """Mock get_icon für Icon Manager"""
        logger.debug(f"MockIconManager.get_icon called for '{icon_name}' with size {size}")
        
        # Simuliere verschiedene Rückgabewerte
        if icon_name in self.available_icons:
            # Erstelle ein einfaches Mock-CTkImage (wird trotzdem fehlschlagen, aber für Debugging gut)
            try:
                import customtkinter as ctk
                from PIL import Image
                
                # Erstelle ein einfaches 24x24 Bild
                img = Image.new('RGBA', size, color=(100, 150, 200, 255))
                mock_icon = ctk.CTkImage(light_image=img, size=size)
                logger.debug(f"MockIconManager: Erstellt Mock-CTkImage für '{icon_name}'")
                return mock_icon
            except Exception as e:
                logger.error(f"MockIconManager: Fehler beim Erstellen des Mock-Icons: {e}")
                return None
        else:
            logger.warning(f"MockIconManager: Icon '{icon_name}' nicht verfügbar")
            return None

def test_welcome_screen_icons():
    """Testet das Icon-Debugging im Welcome Screen"""
    try:
        logger.info("=== Starting Icon Debug Test ===")
        
        # CTkinter Setup
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Main Window
        root = ctk.CTk()
        root.title("Icon Debug Test")
        root.geometry("800x600")
        
        # Mock App
        mock_app = MockApp(root)
        
        # Import Welcome Screen
        try:
            from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
            logger.info("Welcome Screen erfolgreich importiert")
        except ImportError as e:
            logger.error(f"Import-Fehler: {e}")
            return False
        
        # Welcome Screen erstellen
        logger.info("Erstelle Welcome Screen...")
        welcome_screen = UltraModernWelcomeScreen(
            master=root,
            app=mock_app,
            app_callback=lambda: None
        )
        welcome_screen.pack(fill="both", expand=True)
        
        logger.info("Welcome Screen erfolgreich erstellt")
        
        # Test Icon-Methoden direkt
        logger.info("=== Direct Icon Method Testing ===")
        test_icons = ['home', 'rocket', 'settings', 'moon', 'sun']
        
        for icon_name in test_icons:
            logger.info(f"Testing icon: {icon_name}")
            icon, text = welcome_screen.safe_get_icon(icon_name, size=(24, 24), fallback_text="❓")
            logger.info(f"Result for {icon_name}: icon={type(icon) if icon else None}, text='{text}'")
        
        # Kurz anzeigen
        root.after(3000, root.quit)  # Nach 3 Sekunden beenden
        root.mainloop()
        
        logger.info("=== Icon Debug Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"Test-Fehler: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("Icon Debug Test gestartet")
    success = test_welcome_screen_icons()
    if success:
        logger.info("✅ Icon Debug Test erfolgreich abgeschlossen")
        print("\n=== Check icon_debug.log for detailed analysis ===")
    else:
        logger.error("❌ Icon Debug Test fehlgeschlagen")
    
    # Log-Datei anzeigen
    try:
        with open('icon_debug.log', 'r', encoding='utf-8') as f:
            log_content = f.read()
            print("\n=== DEBUG LOG CONTENT ===")
            print(log_content[-2000:])  # Letzte 2000 Zeichen
    except Exception as e:
        print(f"Konnte Log-Datei nicht lesen: {e}")
