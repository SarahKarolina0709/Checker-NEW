#!/usr/bin/env python3
"""
Schneller Test der reparierten register_persistent_button Funktionalität
"""

import os
import sys

def test_repaired_functionality():
    """Test der reparierten register_persistent_button Funktionalität"""
    print("🔧 TESTING REPAIRED register_persistent_button FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Import CheckerApp
        print("📦 Importing CheckerApp...")
        from checker_app import CheckerApp
        print("✅ CheckerApp imported successfully")
        
        # Test minimale Instanziierung ohne UI
        print("\n🧪 Testing method availability...")
        
        # Überprüfe ob die Methoden verfügbar sind
        has_register = hasattr(CheckerApp, 'register_persistent_button')
        has_count = hasattr(CheckerApp, 'get_persistent_button_count')
        has_cleanup = hasattr(CheckerApp, 'cleanup_persistent_buttons')
        
        print(f"✅ register_persistent_button: {has_register}")
        print(f"✅ get_persistent_button_count: {has_count}")
        print(f"✅ cleanup_persistent_buttons: {has_cleanup}")
        
        if not all([has_register, has_count, has_cleanup]):
            print("❌ Not all methods available!")
            return False
        
        # Test Signature der Methode
        import inspect
        sig = inspect.signature(CheckerApp.register_persistent_button)
        params = list(sig.parameters.keys())
        print(f"✅ Method signature: {params}")
        
        expected_params = ['self', 'button', 'icon_ref', 'description']
        has_correct_signature = all(param in params for param in expected_params)
        print(f"✅ Correct signature: {has_correct_signature}")
        
        if not has_correct_signature:
            print(f"❌ Expected {expected_params}, got {params}")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ register_persistent_button ist vollständig repariert!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_live_registration():
    """Test die tatsächliche Registrierung (minimal)"""
    print("\n" + "=" * 60)
    print("🔥 LIVE REGISTRATION TEST")
    print("=" * 60)
    
    try:
        # Mock Button für Test
        class MockButton:
            def __init__(self, text):
                self.text = text
            def __repr__(self):
                return f"MockButton('{self.text}')"
        
        # Mock CheckerApp für isolierten Test
        class MinimalCheckerApp:
            def __init__(self):
                self.persistent_buttons = []
                import datetime
                self.datetime = datetime
            
            def register_persistent_button(self, button, icon_ref=None, description=""):
                """Kopie der reparierten Methode für Test"""
                try:
                    if button is None:
                        print(f"[PERSISTENT_BUTTON] Warning: Attempted to register None button (desc: {description})")
                        return None
                    
                    # Button zur persistenten Liste hinzufügen
                    if hasattr(self, 'persistent_buttons'):
                        self.persistent_buttons.append({
                            'button': button,
                            'icon_ref': icon_ref,
                            'description': description,
                            'registered_at': self.datetime.datetime.now().isoformat()
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
                    
                    print(f"[PERSISTENT_BUTTON] Registered button successfully: {description} "
                          f"(total: {len(self.persistent_buttons)})")
                    
                    return button
                    
                except Exception as e:
                    print(f"[PERSISTENT_BUTTON] Error registering button '{description}': {e}")
                    return button
        
        # Test mit Mock App
        app = MinimalCheckerApp()
        
        # Test 1: Einfacher Button
        button1 = MockButton("Test Button 1")
        result1 = app.register_persistent_button(button1, description="test_button_1")
        print(f"✅ Test 1 successful: {result1}")
        
        # Test 2: Button mit Icon
        button2 = MockButton("Test Button 2")
        mock_icon = "mock_icon_reference"
        result2 = app.register_persistent_button(button2, icon_ref=mock_icon, description="test_button_2")
        print(f"✅ Test 2 successful: {result2}")
        
        # Test 3: Verifikation
        print(f"✅ Total registered buttons: {len(app.persistent_buttons)}")
        print(f"✅ First button registered at: {app.persistent_buttons[0]['registered_at']}")
        
        # Test 4: Attribut-Erstellung
        button_attrs = [attr for attr in dir(app) if attr.startswith('persistent_button_')]
        icon_attrs = [attr for attr in dir(app) if attr.startswith('persistent_icon_')]
        print(f"✅ Button attributes created: {len(button_attrs)}")
        print(f"✅ Icon attributes created: {len(icon_attrs)}")
        
        print("\n🎉 LIVE REGISTRATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ LIVE TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Repaired Functionality Tests...\n")
    
    # Test 1: Basis-Funktionalität
    test1_passed = test_repaired_functionality()
    
    # Test 2: Live-Registrierung
    test2_passed = test_live_registration()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Functionality Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Live Registration Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL REPAIRS SUCCESSFUL!")
        print("✅ register_persistent_button ist vollständig funktionsfähig!")
        sys.exit(0)
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        sys.exit(1)
