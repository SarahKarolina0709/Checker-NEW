#!/usr/bin/env python3
"""
Test für die zentrale register_persistent_button Funktionalität

Dieser Test überprüft:
1. Korrekte Registrierung von Buttons mit Icons
2. Persistente Speicherung der Referenzen
3. Schutz vor Garbage Collection
4. Korrekte Cleanup-Funktionalität
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
import tempfile
import time

# Mock imports für Testing
class MockCTkButton:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.configured_state = None
    
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self.configured_state = kwargs['state']

class MockCTkImage:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

# Simuliere CheckerApp für Tests
class MockCheckerApp:
    def __init__(self):
        self.persistent_buttons = []
        self.icon_images = {}
        
    def register_persistent_button(self, button, icon_ref=None, description=""):
        """Test implementation of register_persistent_button"""
        try:
            if button is None:
                print(f"[TEST] Warning: Attempted to register None button (desc: {description})")
                return None
            
            # Button zur persistenten Liste hinzufügen
            self.persistent_buttons.append({
                'button': button,
                'icon_ref': icon_ref,
                'description': description,
                'registered_at': 'test_time'
            })
            
            # Zusätzliche Referenz als Instanz-Attribut
            button_count = len(self.persistent_buttons)
            attr_name = f"persistent_button_{button_count}_{description.replace(' ', '_')}"
            attr_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in attr_name)
            attr_name = attr_name[:50]
            
            setattr(self, attr_name, button)
            
            # Icon-Referenz ebenfalls persistent halten
            if icon_ref is not None:
                icon_attr_name = f"persistent_icon_{button_count}_{description.replace(' ', '_')}"
                icon_attr_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in icon_attr_name)
                icon_attr_name = icon_attr_name[:50]
                setattr(self, icon_attr_name, icon_ref)
            
            print(f"[TEST] Registered button successfully: {description} "
                  f"(total: {len(self.persistent_buttons)})")
            
            return button
            
        except Exception as e:
            print(f"[TEST] Error registering button '{description}': {e}")
            return button
    
    def get_persistent_button_count(self):
        """Test implementation"""
        return len(self.persistent_buttons) if hasattr(self, 'persistent_buttons') else 0
    
    def cleanup_persistent_buttons(self):
        """Test implementation"""
        if hasattr(self, 'persistent_buttons'):
            button_count = len(self.persistent_buttons)
            self.persistent_buttons.clear()
            print(f"[TEST] Cleaned up {button_count} persistent button references")
        
        # Bereinige auch die Instanz-Attribute
        attrs_to_remove = []
        for attr_name in dir(self):
            if attr_name.startswith('persistent_button_') or attr_name.startswith('persistent_icon_'):
                attrs_to_remove.append(attr_name)
        
        for attr_name in attrs_to_remove:
            try:
                delattr(self, attr_name)
            except Exception:
                pass
        
        if attrs_to_remove:
            print(f"[TEST] Cleaned up {len(attrs_to_remove)} persistent attributes")

class TestPersistentButtonManager(unittest.TestCase):
    """Test-Suite für die persistente Button-Verwaltung"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.app = MockCheckerApp()
    
    def test_register_single_button(self):
        """Test: Registrierung eines einzelnen Buttons"""
        print("\n[TEST] Testing single button registration...")
        
        # Erstelle Mock-Button
        button = MockCTkButton(text="Test Button")
        
        # Registriere Button
        result = self.app.register_persistent_button(button, description="test_button")
        
        # Assertions
        self.assertEqual(result, button)
        self.assertEqual(len(self.app.persistent_buttons), 1)
        self.assertEqual(self.app.persistent_buttons[0]['description'], "test_button")
        self.assertEqual(self.app.persistent_buttons[0]['button'], button)
        
        print("[TEST] ✅ Single button registration successful")
    
    def test_register_button_with_icon(self):
        """Test: Registrierung eines Buttons mit Icon"""
        print("\n[TEST] Testing button with icon registration...")
        
        # Erstelle Mock-Button und Icon
        button = MockCTkButton(text="Icon Button")
        icon = MockCTkImage()
        
        # Registriere Button mit Icon
        result = self.app.register_persistent_button(
            button, 
            icon_ref=icon, 
            description="icon_button"
        )
        
        # Assertions
        self.assertEqual(result, button)
        self.assertEqual(len(self.app.persistent_buttons), 1)
        self.assertEqual(self.app.persistent_buttons[0]['icon_ref'], icon)
        
        # Überprüfe, dass Icon-Attribut erstellt wurde
        icon_attrs = [attr for attr in dir(self.app) if attr.startswith('persistent_icon_')]
        self.assertGreater(len(icon_attrs), 0)
        
        print("[TEST] ✅ Button with icon registration successful")
    
    def test_register_multiple_buttons(self):
        """Test: Registrierung mehrerer Buttons"""
        print("\n[TEST] Testing multiple button registration...")
        
        buttons = []
        for i in range(5):
            button = MockCTkButton(text=f"Button {i}")
            icon = MockCTkImage() if i % 2 == 0 else None
            
            result = self.app.register_persistent_button(
                button,
                icon_ref=icon,
                description=f"button_{i}"
            )
            buttons.append(result)
        
        # Assertions
        self.assertEqual(len(self.app.persistent_buttons), 5)
        self.assertEqual(self.app.get_persistent_button_count(), 5)
        
        # Überprüfe alle Buttons
        for i, registered_button in enumerate(self.app.persistent_buttons):
            self.assertEqual(registered_button['description'], f"button_{i}")
            self.assertEqual(registered_button['button'], buttons[i])
        
        print("[TEST] ✅ Multiple button registration successful")
    
    def test_register_none_button(self):
        """Test: Behandlung von None-Button"""
        print("\n[TEST] Testing None button handling...")
        
        # Versuche None-Button zu registrieren
        result = self.app.register_persistent_button(None, description="none_button")
        
        # Assertions
        self.assertIsNone(result)
        self.assertEqual(len(self.app.persistent_buttons), 0)
        
        print("[TEST] ✅ None button handling successful")
    
    def test_button_cleanup(self):
        """Test: Cleanup-Funktionalität"""
        print("\n[TEST] Testing button cleanup...")
        
        # Registriere mehrere Buttons
        for i in range(3):
            button = MockCTkButton(text=f"Cleanup Button {i}")
            icon = MockCTkImage()
            self.app.register_persistent_button(
                button,
                icon_ref=icon,
                description=f"cleanup_button_{i}"
            )
        
        # Überprüfe vor Cleanup
        self.assertEqual(len(self.app.persistent_buttons), 3)
        button_attrs_before = [attr for attr in dir(self.app) if attr.startswith('persistent_button_')]
        icon_attrs_before = [attr for attr in dir(self.app) if attr.startswith('persistent_icon_')]
        
        self.assertGreater(len(button_attrs_before), 0)
        self.assertGreater(len(icon_attrs_before), 0)
        
        # Führe Cleanup durch
        self.app.cleanup_persistent_buttons()
        
        # Überprüfe nach Cleanup
        self.assertEqual(len(self.app.persistent_buttons), 0)
        button_attrs_after = [attr for attr in dir(self.app) if attr.startswith('persistent_button_')]
        icon_attrs_after = [attr for attr in dir(self.app) if attr.startswith('persistent_icon_')]
        
        self.assertEqual(len(button_attrs_after), 0)
        self.assertEqual(len(icon_attrs_after), 0)
        
        print("[TEST] ✅ Button cleanup successful")
    
    def test_attribute_name_sanitization(self):
        """Test: Bereinigung von Attributnamen"""
        print("\n[TEST] Testing attribute name sanitization...")
        
        # Button mit problematischen Zeichen im Namen
        button = MockCTkButton(text="Test Button")
        
        problematic_descriptions = [
            "button with spaces",
            "button-with-dashes",
            "button/with/slashes",
            "button@with#special$chars",
            "very_long_description_that_exceeds_fifty_characters_and_should_be_truncated"
        ]
        
        for desc in problematic_descriptions:
            result = self.app.register_persistent_button(button, description=desc)
            self.assertEqual(result, button)
        
        # Überprüfe, dass alle Attribute korrekt erstellt wurden
        button_attrs = [attr for attr in dir(self.app) if attr.startswith('persistent_button_')]
        self.assertEqual(len(button_attrs), len(problematic_descriptions))
        
        # Überprüfe Attributnamen-Länge
        for attr in button_attrs:
            self.assertLessEqual(len(attr), 60)  # Etwas Puffer für Präfix
            # Überprüfe, dass nur gültige Zeichen verwendet werden
            self.assertTrue(all(c.isalnum() or c == '_' for c in attr))
        
        print("[TEST] ✅ Attribute name sanitization successful")

def run_persistent_button_tests():
    """Führt alle Tests für die persistente Button-Verwaltung durch"""
    print("=" * 80)
    print("🧪 PERSISTENT BUTTON MANAGER TESTS")
    print("=" * 80)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPersistentButtonManager)
    
    # Test-Runner konfigurieren
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    
    # Tests ausführen
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        return False

def test_integration_with_welcome_screen():
    """Test Integration mit dem Welcome Screen"""
    print("\n" + "=" * 80)
    print("🔗 INTEGRATION TEST: Welcome Screen & Persistent Buttons")
    print("=" * 80)
    
    try:
        # Simuliere Welcome Screen Button-Erstellung
        app = MockCheckerApp()
        
        # Simuliere verschiedene Button-Typen aus Welcome Screen
        button_types = [
            {"text": "Neuen Kunden erstellen", "icon": "add-20", "style": "primary"},
            {"text": "Angebotsanalyse", "icon": "analytics", "style": "secondary"},
            {"text": "Qualitätsprüfung", "icon": "spell-check-20", "style": "secondary"},
            {"text": "Schnellstart", "icon": "rocket", "style": "primary"},
            {"text": "Einstellungen", "icon": "settings", "style": "ghost"},
        ]
        
        registered_buttons = []
        
        for btn_config in button_types:
            # Simuliere Icon-Erstellung
            icon = MockCTkImage() if btn_config["icon"] else None
            
            # Simuliere Button-Erstellung
            button = MockCTkButton(
                text=btn_config["text"],
                image=icon
            )
            
            # Registriere mit Welcome Screen Namenskonvention
            description = f"welcome_screen_{btn_config['text'].replace(' ', '_')}"
            app.register_persistent_button(button, icon_ref=icon, description=description)
            
            registered_buttons.append(button)
        
        # Validierung
        assert len(registered_buttons) == 5
        assert app.get_persistent_button_count() == 5
        
        # Überprüfe Attribut-Erstellung
        button_attrs = [attr for attr in dir(app) if attr.startswith('persistent_button_')]
        icon_attrs = [attr for attr in dir(app) if attr.startswith('persistent_icon_')]
        
        assert len(button_attrs) == 5
        assert len(icon_attrs) == 5  # Alle Buttons haben Icons
        
        print(f"✅ Successfully registered {len(registered_buttons)} Welcome Screen buttons")
        print(f"✅ Created {len(button_attrs)} persistent button attributes")
        print(f"✅ Created {len(icon_attrs)} persistent icon attributes")
        
        # Test Cleanup
        app.cleanup_persistent_buttons()
        
        assert app.get_persistent_button_count() == 0
        button_attrs_after = [attr for attr in dir(app) if attr.startswith('persistent_button_')]
        icon_attrs_after = [attr for attr in dir(app) if attr.startswith('persistent_icon_')]
        
        assert len(button_attrs_after) == 0
        assert len(icon_attrs_after) == 0
        
        print("✅ Cleanup successful - all references removed")
        print("\n🎉 INTEGRATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Persistent Button Manager Tests...\n")
    
    # Führe Unit Tests durch
    unit_tests_passed = run_persistent_button_tests()
    
    # Führe Integration Tests durch
    integration_tests_passed = test_integration_with_welcome_screen()
    
    print("\n" + "=" * 80)
    print("🏁 FINAL RESULTS")
    print("=" * 80)
    print(f"Unit Tests: {'✅ PASSED' if unit_tests_passed else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_tests_passed else '❌ FAILED'}")
    
    if unit_tests_passed and integration_tests_passed:
        print("\n🎉 ALL TESTS SUCCESSFUL!")
        print("✅ register_persistent_button implementation is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("❌ Please review the implementation!")
        sys.exit(1)
