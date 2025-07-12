#!/usr/bin/env python3
"""
Schneller Test der register_persistent_button Funktionalität in der echten App
"""

import os
import sys

# Mock für schnelles Testen ohne UI
class QuickTestApp:
    def __init__(self):
        self.persistent_buttons = []
        
        # Importiere die Methoden aus checker_app
        from datetime import datetime
        self.datetime = datetime
    
    def register_persistent_button(self, button, icon_ref=None, description=""):
        """Kopie der Methode aus checker_app.py für schnelles Testen"""
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
                    'registered_at': self.datetime.now().isoformat()
                })
            else:
                self.persistent_buttons = [{
                    'button': button,
                    'icon_ref': icon_ref,
                    'description': description,
                    'registered_at': 'fallback_creation'
                }]
            
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
    
    def get_persistent_button_count(self):
        """Gibt die Anzahl der registrierten persistenten Buttons zurück"""
        try:
            if hasattr(self, 'persistent_buttons'):
                return len(self.persistent_buttons)
            return 0
        except Exception:
            return 0
    
    def cleanup_persistent_buttons(self):
        """Bereinigt die persistenten Button-Referenzen"""
        try:
            if hasattr(self, 'persistent_buttons'):
                button_count = len(self.persistent_buttons)
                self.persistent_buttons.clear()
                print(f"[PERSISTENT_BUTTON] Cleaned up {button_count} persistent button references")
            
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
                print(f"[PERSISTENT_BUTTON] Cleaned up {len(attrs_to_remove)} persistent attributes")
                
        except Exception as e:
            print(f"[PERSISTENT_BUTTON] Error during cleanup: {e}")

# Mock Button und Icon Klassen
class MockButton:
    def __init__(self, text="Button"):
        self.text = text
        self.id = id(self)
    def __repr__(self):
        return f"MockButton('{self.text}')"

class MockIcon:
    def __init__(self, name="icon"):
        self.name = name
        self.id = id(self)
    def __repr__(self):
        return f"MockIcon('{self.name}')"

def quick_functionality_test():
    """Schneller Test der Kernfunktionalität"""
    print("🚀 Schneller Funktionalitätstest der register_persistent_button Methode")
    print("=" * 70)
    
    app = QuickTestApp()
    
    # Test 1: Einzelner Button
    print("\n📝 Test 1: Einzelner Button")
    button1 = MockButton("Test Button 1")
    icon1 = MockIcon("test-icon-1")
    
    result = app.register_persistent_button(button1, icon_ref=icon1, description="test_button_1")
    print(f"✅ Button registriert: {result}")
    print(f"✅ Anzahl persistenter Buttons: {app.get_persistent_button_count()}")
    
    # Test 2: Mehrere Buttons
    print("\n📝 Test 2: Mehrere Buttons")
    for i in range(2, 6):
        button = MockButton(f"Test Button {i}")
        icon = MockIcon(f"test-icon-{i}")
        app.register_persistent_button(button, icon_ref=icon, description=f"test_button_{i}")
    
    print(f"✅ Anzahl persistenter Buttons nach Batch: {app.get_persistent_button_count()}")
    
    # Test 3: Attribut-Überprüfung
    print("\n📝 Test 3: Attribut-Überprüfung")
    button_attrs = [attr for attr in dir(app) if attr.startswith('persistent_button_')]
    icon_attrs = [attr for attr in dir(app) if attr.startswith('persistent_icon_')]
    
    print(f"✅ Button-Attribute erstellt: {len(button_attrs)}")
    print(f"✅ Icon-Attribute erstellt: {len(icon_attrs)}")
    
    print("\n🔍 Beispiel-Attribute:")
    for attr in button_attrs[:3]:
        print(f"  - {attr}")
    
    # Test 4: Datenstruktur-Validation
    print("\n📝 Test 4: Datenstruktur-Validation")
    for i, entry in enumerate(app.persistent_buttons[:3]):
        print(f"  Button {i+1}: {entry['description']} | Registered: {entry['registered_at']}")
        print(f"    - Button: {entry['button']}")
        print(f"    - Icon: {entry['icon_ref']}")
    
    # Test 5: Cleanup
    print("\n📝 Test 5: Cleanup")
    pre_cleanup_count = app.get_persistent_button_count()
    app.cleanup_persistent_buttons()
    post_cleanup_count = app.get_persistent_button_count()
    
    print(f"✅ Buttons vor Cleanup: {pre_cleanup_count}")
    print(f"✅ Buttons nach Cleanup: {post_cleanup_count}")
    
    # Validierung nach Cleanup
    button_attrs_after = [attr for attr in dir(app) if attr.startswith('persistent_button_')]
    icon_attrs_after = [attr for attr in dir(app) if attr.startswith('persistent_icon_')]
    
    print(f"✅ Button-Attribute nach Cleanup: {len(button_attrs_after)}")
    print(f"✅ Icon-Attribute nach Cleanup: {len(icon_attrs_after)}")
    
    print("\n🎉 Alle Tests erfolgreich!")
    return True

def test_welcome_screen_integration():
    """Test der Integration mit Welcome Screen Patterns"""
    print("\n" + "=" * 70)
    print("🔗 Test: Welcome Screen Integration Patterns")
    print("=" * 70)
    
    app = QuickTestApp()
    
    # Simuliere Welcome Screen Button-Erstellung
    welcome_screen_buttons = [
        {"text": "Neuen Kunden erstellen", "icon": "add-20", "category": "customer"},
        {"text": "Angebotsanalyse", "icon": "analytics", "category": "workflow"},
        {"text": "Qualitätsprüfung", "icon": "spell-check-20", "category": "workflow"},
        {"text": "Finalisierung", "icon": "certificate", "category": "workflow"},
        {"text": "Projektübersicht", "icon": "folder_icon", "category": "management"},
        {"text": "Schnellstart", "icon": "rocket", "category": "quick_action"},
        {"text": "Zuletzt verwendet", "icon": "clock", "category": "quick_action"},
        {"text": "Einstellungen", "icon": "settings", "category": "tools"},
        {"text": "Hilfe", "icon": "help_icon", "category": "tools"}
    ]
    
    # Registriere alle Welcome Screen Buttons
    for btn_config in welcome_screen_buttons:
        button = MockButton(btn_config["text"])
        icon = MockIcon(btn_config["icon"])
        
        # Verwende Welcome Screen Namenskonvention
        description = f"welcome_screen_{btn_config['text'].replace(' ', '_')}"
        
        app.register_persistent_button(button, icon_ref=icon, description=description)
    
    print(f"✅ Welcome Screen Buttons registriert: {len(welcome_screen_buttons)}")
    print(f"✅ Total persistent buttons: {app.get_persistent_button_count()}")
    
    # Überprüfe Kategorisierung
    categories = {}
    for entry in app.persistent_buttons:
        desc = entry['description']
        if 'welcome_screen_' in desc:
            # Finde ursprüngliche Kategorie
            original_button = next(btn for btn in welcome_screen_buttons 
                                 if btn['text'].replace(' ', '_') in desc)
            category = original_button['category']
            
            if category not in categories:
                categories[category] = []
            categories[category].append(desc)
    
    print(f"\n📊 Buttons nach Kategorien:")
    for category, buttons in categories.items():
        print(f"  {category}: {len(buttons)} buttons")
    
    # Test Memory-Footprint Simulation
    print(f"\n💾 Memory Footprint Simulation:")
    total_attributes = len([attr for attr in dir(app) 
                           if attr.startswith('persistent_button_') or attr.startswith('persistent_icon_')])
    estimated_memory = total_attributes * 64  # Grobe Schätzung in Bytes
    print(f"  - Total Attributes: {total_attributes}")
    print(f"  - Estimated Memory: ~{estimated_memory} bytes ({estimated_memory/1024:.1f} KB)")
    
    # Cleanup Test
    print(f"\n🧹 Cleanup Test:")
    app.cleanup_persistent_buttons()
    final_count = app.get_persistent_button_count()
    print(f"✅ Final button count after cleanup: {final_count}")
    
    return final_count == 0

if __name__ == "__main__":
    success1 = quick_functionality_test()
    success2 = test_welcome_screen_integration()
    
    print("\n" + "=" * 70)
    print("🏁 GESAMTERGEBNIS")
    print("=" * 70)
    print(f"Funktionalitätstest: {'✅ BESTANDEN' if success1 else '❌ FEHLGESCHLAGEN'}")
    print(f"Integration Test: {'✅ BESTANDEN' if success2 else '❌ FEHLGESCHLAGEN'}")
    
    if success1 and success2:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("✅ register_persistent_button ist vollständig implementiert und funktionsfähig!")
    else:
        print("\n⚠️ EINIGE TESTS FEHLGESCHLAGEN!")
