"""
Test-Skript für die Logging-Optimierungen des Welcome Screens
"""

import logging
import inspect
from modern_welcome_screen import ModernWelcomeScreen, catch_errors

def test_decorator_presence():
    """Testet ob der catch_errors Decorator bei wichtigen Methoden vorhanden ist"""
    print("=== Test: Decorator-Präsenz ===")
    
    # Liste der Methoden, die den Decorator haben sollten
    expected_decorated_methods = [
        'show',
        'update_gradient_background',
        'update_responsive_layout',
        'cleanup',
        'create_new_customer',
        'execute_workflow',
        'toggle_dark_mode',
        'update_ui_colors',
        'validate_customer_data',
        'show_loading_spinner',
        'hide_loading_spinner',
        'start_workflow_with_confirmation',
        'menu_file_clicked',
        'menu_projects_clicked',
        'menu_settings_clicked',
        'menu_help_clicked'
    ]
    
    decorated_count = 0
    
    for method_name in expected_decorated_methods:
        try:
            method = getattr(ModernWelcomeScreen, method_name)
            # Prüfen ob Decorator vorhanden ist
            if hasattr(method, '__wrapped__'):
                print(f"✅ {method_name}: Decorator vorhanden")
                decorated_count += 1
            else:
                print(f"❌ {method_name}: Decorator fehlt")
        except AttributeError:
            print(f"❌ {method_name}: Methode nicht gefunden")
    
    print(f"\nDekorierte Methoden: {decorated_count}/{len(expected_decorated_methods)}")
    return decorated_count == len(expected_decorated_methods)

def test_logging_levels():
    """Testet ob verschiedene Logging-Level verwendet werden"""
    print("\n=== Test: Logging-Level-Verwendung ===")
    
    # Lese die Quelldatei und suche nach verschiedenen Logging-Aufrufen
    try:
        with open('modern_welcome_screen.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        logging_levels = {
            'debug': content.count('logging.debug('),
            'info': content.count('logging.info('),
            'warning': content.count('logging.warning('),
            'error': content.count('logging.error('),
            'exception': content.count('logging.exception(')
        }
        
        for level, count in logging_levels.items():
            print(f"logging.{level}: {count} Verwendungen")
        
        # Prüfe ob verschiedene Level verwendet werden
        used_levels = sum(1 for count in logging_levels.values() if count > 0)
        print(f"\nVerwendete Logging-Level: {used_levels}/5")
        
        return used_levels >= 4  # Mindestens 4 verschiedene Level sollten verwendet werden
        
    except FileNotFoundError:
        print("❌ modern_welcome_screen.py nicht gefunden")
        return False

def test_print_removal():
    """Testet ob alle print()-Anweisungen durch Logging ersetzt wurden"""
    print("\n=== Test: Print-Statement-Entfernung ===")
    
    try:
        with open('modern_welcome_screen.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Suche nach print()-Anweisungen (außer in Kommentaren)
        lines = content.split('\n')
        print_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Ignoriere Kommentare und Docstrings
            if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                if 'print(' in line and not line.strip().startswith('#'):
                    print_lines.append((i, line.strip()))
        
        if print_lines:
            print(f"❌ Gefundene print()-Anweisungen:")
            for line_num, line in print_lines:
                print(f"   Zeile {line_num}: {line}")
            return False
        else:
            print("✅ Keine print()-Anweisungen gefunden")
            return True
            
    except FileNotFoundError:
        print("❌ modern_welcome_screen.py nicht gefunden")
        return False

def test_decorator_functionality():
    """Testet die Funktionalität des catch_errors Decorators"""
    print("\n=== Test: Decorator-Funktionalität ===")
    
    @catch_errors
    def test_function_success():
        return "success"
    
    @catch_errors
    def test_function_error():
        raise ValueError("Test-Fehler")
    
    # Test erfolgreicher Aufruf
    try:
        result = test_function_success()
        if result == "success":
            print("✅ Decorator funktioniert bei erfolgreichen Aufrufen")
            success_test = True
        else:
            print("❌ Decorator verändert Rückgabewerte")
            success_test = False
    except Exception as e:
        print(f"❌ Decorator wirft Fehler bei erfolgreichen Aufrufen: {e}")
        success_test = False
    
    # Test Fehlerbehandlung
    try:
        result = test_function_error()
        if result is None:  # Decorator sollte None zurückgeben bei Fehlern
            print("✅ Decorator behandelt Fehler korrekt")
            error_test = True
        else:
            print("❌ Decorator gibt unerwarteten Wert bei Fehlern zurück")
            error_test = False
    except Exception as e:
        print(f"❌ Decorator lässt Fehler durch: {e}")
        error_test = False
    
    return success_test and error_test

def run_all_tests():
    """Führt alle Tests aus"""
    print("🔍 Starte Logging-Optimierungen Tests...\n")
    
    tests = [
        ("Decorator-Präsenz", test_decorator_presence),
        ("Logging-Level-Verwendung", test_logging_levels),
        ("Print-Statement-Entfernung", test_print_removal),
        ("Decorator-Funktionalität", test_decorator_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Fehler in Test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "="*50)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nErgebnis: {passed}/{len(results)} Tests bestanden")
    
    if passed == len(results):
        print("🎉 Alle Logging-Optimierungen erfolgreich implementiert!")
    else:
        print("⚠️ Einige Tests sind fehlgeschlagen. Bitte überprüfen Sie die Implementierung.")

if __name__ == '__main__':
    run_all_tests()
