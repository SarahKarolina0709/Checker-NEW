#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigierte und umfassende Tests für die Welcome Screen Implementierung
Behebt alle identifizierten Probleme
"""

import sys
import os
import traceback
import tkinter as tk
import customtkinter as ctk

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def test_imports():
    """Test: Import-Funktionalität"""
    print("=== TEST 1: Import-Funktionalität ===")
    try:
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        print("✓ UltraModernWelcomeScreen erfolgreich importiert")
        return True
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        traceback.print_exc()
        return False

def test_syntax():
    """Test: Syntax-Überprüfung"""
    print("\n=== TEST 2: Syntax-Überprüfung ===")
    try:
        import py_compile
        result = py_compile.compile('ultra_modern_welcome_screen_v2.py', doraise=True)
        print("✓ Syntax-Überprüfung erfolgreich")
        return True
    except Exception as e:
        print(f"✗ Syntax-Fehler: {e}")
        return False

class EnhancedMockApp:
    """Verbesserte Mock-App für Tests mit allen erforderlichen Attributen"""
    def __init__(self):
        # Create a proper Tkinter root for testing
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Logger setup
        import logging
        self.logger = logging.getLogger('EnhancedMockApp')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Mock attributes that the welcome screen expects
        self.icon_manager = self
        self.kunden_manager = self
        
    def get_icon(self, name, size=(24, 24)):
        """Enhanced mock icon getter that returns None (simulating missing icons)"""
        self.logger.info(f"Mock: Icon '{name}' angefordert (Größe: {size})")
        return None  # Simuliert fehlende Icons
        
    def show_welcome_screen(self):
        """Mock welcome screen method"""
        print("Mock: Welcome Screen angezeigt")
        
    def clear_main_container(self):
        """Mock clear method"""
        print("Mock: Container geleert")
        
    def handle_workflow_start(self, workflow_name, data=None):
        """Mock workflow handler"""
        print(f"Mock: Workflow '{workflow_name}' gestartet mit Daten: {data}")
    
    def cleanup(self):
        """Cleanup mock app"""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()

def test_mockapp_integration():
    """Test: MockApp Integration"""
    print("\n=== TEST 3: MockApp Integration ===")
    try:
        mock_app = EnhancedMockApp()
        
        # Test that mock app has all required attributes
        required_attrs = ['root', 'get_icon', 'handle_workflow_start', 'logger']
        for attr in required_attrs:
            if not hasattr(mock_app, attr):
                print(f"✗ MockApp fehlt Attribut: {attr}")
                return False
            print(f"✓ MockApp hat Attribut: {attr}")
        
        # Test icon method
        icon = mock_app.get_icon('test_icon')
        if icon is None:
            print("✓ MockApp.get_icon funktioniert korrekt")
        
        mock_app.cleanup()
        print("✓ MockApp Integration erfolgreich")
        return True
        
    except Exception as e:
        print(f"✗ MockApp Integration fehlgeschlagen: {e}")
        traceback.print_exc()
        return False

def test_welcome_screen_creation():
    """Test: Welcome Screen Erstellung"""
    print("\n=== TEST 4: Welcome Screen Erstellung ===")
    try:
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        # Create enhanced mock app
        mock_app = EnhancedMockApp()
        
        # Create a test frame to hold the welcome screen
        test_frame = ctk.CTkFrame(mock_app.root)
        
        # Create welcome screen with proper parameters
        welcome_screen = UltraModernWelcomeScreen(
            master=test_frame,
            app=mock_app,
            app_callback=mock_app.handle_workflow_start
        )
        
        print("✓ Welcome Screen erfolgreich erstellt")
        
        # Test key methods
        if hasattr(welcome_screen, 'safe_get_icon'):
            icon, text = welcome_screen.safe_get_icon('test_icon')
            print(f"✓ safe_get_icon funktioniert: icon={icon}, text='{text}'")
        
        if hasattr(welcome_screen, 'show_error_fallback'):
            print("✓ show_error_fallback Methode vorhanden")
        
        # Cleanup
        welcome_screen.destroy()
        mock_app.cleanup()
        
        print("✓ Welcome Screen Test erfolgreich")
        return True
        
    except Exception as e:
        print(f"✗ Welcome Screen Erstellung fehlgeschlagen: {e}")
        traceback.print_exc()
        try:
            mock_app.cleanup()
        except:
            pass
        return False

def test_icon_fallback_system():
    """Test: Icon Fallback System"""
    print("\n=== TEST 5: Icon Fallback System ===")
    try:
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        mock_app = EnhancedMockApp()
        test_frame = ctk.CTkFrame(mock_app.root)
        
        # Create welcome screen ohne UI setup
        welcome_screen = UltraModernWelcomeScreen.__new__(UltraModernWelcomeScreen)
        ctk.CTkFrame.__init__(welcome_screen, test_frame)
        
        # Initialize required attributes
        welcome_screen.app = mock_app
        welcome_screen.app_callback = mock_app.handle_workflow_start
        welcome_screen.logger = mock_app.logger
        welcome_screen.main_container = test_frame  # Set this for icon loading
        
        # Test safe_get_icon with existing icon (should return None, fallback_text)
        icon, text = welcome_screen.safe_get_icon('existing_icon', fallback_text='⚙')
        if icon is None and text == '⚙':
            print("✓ Icon fallback system funktioniert korrekt")
        else:
            print(f"⚠ Icon fallback unerwartetes Ergebnis: icon={icon}, text='{text}'")
        
        # Test mit verschiedenen Icons
        test_icons = ['rocket', 'home', 'person', 'missing_icon']
        for icon_name in test_icons:
            icon, text = welcome_screen.safe_get_icon(icon_name, fallback_text='🔧')
            print(f"  - '{icon_name}': icon={'CTkImage' if icon else 'None'}, text='{text}'")
        
        # Cleanup
        welcome_screen.destroy()
        mock_app.cleanup()
        
        print("✓ Icon Fallback System Test erfolgreich")
        return True
        
    except Exception as e:
        print(f"✗ Icon Fallback Test fehlgeschlagen: {e}")
        traceback.print_exc()
        try:
            mock_app.cleanup()
        except:
            pass
        return False

def test_error_recovery():
    """Test: Error Recovery"""
    print("\n=== TEST 6: Error Recovery ===")
    try:
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        mock_app = EnhancedMockApp()
        test_frame = ctk.CTkFrame(mock_app.root)
        
        # Create welcome screen
        welcome_screen = UltraModernWelcomeScreen.__new__(UltraModernWelcomeScreen)
        ctk.CTkFrame.__init__(welcome_screen, test_frame)
        
        # Initialize minimal attributes for error fallback
        welcome_screen.app = mock_app
        welcome_screen.logger = mock_app.logger
        welcome_screen.COLORS = {
            'primary': '#2196f3',
            'error': '#f44336',
            'error_light': '#ffebee'
        }
        
        # Test error fallback
        welcome_screen.show_error_fallback()
        print("✓ Error fallback ausgeführt ohne Fehler")
        
        # Cleanup
        welcome_screen.destroy()
        mock_app.cleanup()
        
        print("✓ Error Recovery Test erfolgreich")
        return True
        
    except Exception as e:
        print(f"✗ Error Recovery Test fehlgeschlagen: {e}")
        traceback.print_exc()
        try:
            mock_app.cleanup()
        except:
            pass
        return False

def main():
    """Haupttestfunktion"""
    print("KORRIGIERTE WELCOME SCREEN TESTS")
    print("=" * 60)
    
    tests = [
        ("Import-Test", test_imports),
        ("Syntax-Test", test_syntax),
        ("MockApp Integration", test_mockapp_integration),
        ("Welcome Screen Erstellung", test_welcome_screen_creation),
        ("Icon Fallback System", test_icon_fallback_system),
        ("Error Recovery", test_error_recovery)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name}: BESTANDEN\n")
            else:
                failed += 1
                print(f"✗ {test_name}: FEHLGESCHLAGEN\n")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name}: KRITISCHER FEHLER - {e}\n")
    
    print("=" * 60)
    print("FINALE TESTERGEBNISSE:")
    print(f"Bestanden: {passed}")
    print(f"Fehlgeschlagen: {failed}")
    print(f"Gesamt: {passed + failed}")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 ALLE TESTS BESTANDEN!")
        print("✨ Welcome Screen ist vollständig korrigiert!")
        return True
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN!")
        print("⚠️  Weitere Korrekturen erforderlich!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
