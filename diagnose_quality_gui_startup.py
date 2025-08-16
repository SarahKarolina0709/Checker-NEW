#!/usr/bin/env python3
"""
🔍 QUALITY GUI STARTUP PROBLEM DIAGNOSTICS
Identifiziert warum sich die Quality GUI nicht öffnen lässt
"""

import os
import sys
import traceback

def diagnose_quality_gui_startup():
    """Systematische Diagnose der Quality GUI Startup-Probleme"""

    print("🔍 QUALITY GUI STARTUP DIAGNOSTICS")
    print("=" * 50)

    problems_found = []

    # Test 1: Python Basis-Check
    print("\n📋 SCHRITT 1: Python Environment Check...")
    try:
        print(f"✅ Python Version: {sys.version}")
        print(f"✅ Python Executable: {sys.executable}")
        print(f"✅ Current Directory: {os.getcwd()}")
    except Exception as e:
        problems_found.append(f"Python Environment Error: {e}")
        print(f"❌ Python Environment Error: {e}")

    # Test 2: CustomTkinter Check
    print("\n📋 SCHRITT 2: CustomTkinter Check...")
    try:
        import customtkinter as ctk
        print(f"✅ CustomTkinter gefunden - Version: {ctk.__version__}")
    except ImportError as e:
        problems_found.append(f"CustomTkinter fehlt: {e}")
        print(f"❌ CustomTkinter FEHLT: {e}")
        print("💡 Lösung: pip install customtkinter")
    except Exception as e:
        problems_found.append(f"CustomTkinter Error: {e}")
        print(f"❌ CustomTkinter Error: {e}")

    # Test 3: Tkinter Check
    print("\n📋 SCHRITT 3: Tkinter Check...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Verstecke Fenster
        print("✅ Tkinter funktioniert")
        root.destroy()
    except ImportError as e:
        problems_found.append(f"Tkinter fehlt: {e}")
        print(f"❌ Tkinter FEHLT: {e}")
        print("💡 Lösung: Tkinter ist normalerweise in Python enthalten")
    except Exception as e:
        problems_found.append(f"Tkinter Error: {e}")
        print(f"❌ Tkinter Error: {e}")

    # Test 4: Quality GUI Import Check
    print("\n📋 SCHRITT 4: Quality GUI Import Check...")
    try:
        import modern_translation_quality_gui
        print("✅ Quality GUI Modul importiert")
    except ImportError as e:
        problems_found.append(f"Quality GUI Import Error: {e}")
        print(f"❌ Quality GUI Import Error: {e}")
        print("💡 Mögliche Ursachen:")
        print("   - Datei beschädigt oder nicht vollständig")
        print("   - Fehlende Abhängigkeiten")
        print("   - Syntax-Fehler in der Datei")
    except Exception as e:
        problems_found.append(f"Quality GUI Import Exception: {e}")
        print(f"❌ Quality GUI Import Exception: {e}")
        traceback.print_exc()

    # Test 5: Quality GUI Klassen-Check
    print("\n📋 SCHRITT 5: Quality GUI Klassen-Check...")
    try:
        import modern_translation_quality_gui
        app_class = modern_translation_quality_gui.ProfessionalTranslationQualityApp
        print(f"✅ Haupt-Klasse gefunden: {app_class.__name__}")
    except AttributeError as e:
        problems_found.append(f"Quality GUI Klassen Error: {e}")
        print(f"❌ Haupt-Klasse NICHT gefunden: {e}")
    except Exception as e:
        problems_found.append(f"Quality GUI Klassen Exception: {e}")
        print(f"❌ Quality GUI Klassen Exception: {e}")

    # Test 6: Abhängigkeiten Check
    print("\n📋 SCHRITT 6: Abhängigkeiten Check...")
    dependencies = [
        ('ui_theme', 'UI Theme System'),
        ('welcome_screen', 'Welcome Screen'),
        ('aggressive_anti_dark_mode', 'Anti-Dark Mode System'),
        ('PIL', 'Python Imaging Library'),
        ('pathlib', 'Path Library'),
        ('json', 'JSON Library'),
        ('logging', 'Logging Library'),
        ('threading', 'Threading Library')
    ]

    missing_deps = []
    for dep_name, dep_description in dependencies:
        try:
            __import__(dep_name)
            print(f"✅ {dep_description}")
        except ImportError:
            missing_deps.append(dep_name)
            print(f"❌ {dep_description} - FEHLT")
            problems_found.append(f"Missing dependency: {dep_name}")

    # Test 7: Datei-Existenz Check
    print("\n📋 SCHRITT 7: Datei-Existenz Check...")
    critical_files = [
        'modern_translation_quality_gui.py',
        'ui_theme.py',
        'welcome_screen.py',
        'config.json'
    ]

    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} - {size} bytes")
        else:
            print(f"❌ {file} - FEHLT")
            problems_found.append(f"Missing file: {file}")

    # Diagnose-Ergebnis
    print("\n🎯 DIAGNOSE-ERGEBNIS:")
    print("=" * 30)

    if not problems_found:
        print("✅ KEINE PROBLEME GEFUNDEN!")
        print("🚀 Quality GUI sollte startbar sein!")
        print("\n💡 Versuche direkten Start:")
        print("python modern_translation_quality_gui.py")
        return True
    else:
        print("❌ PROBLEME IDENTIFIZIERT:")
        for i, problem in enumerate(problems_found, 1):
            print(f"   {i}. {problem}")

        print("\n💡 EMPFOHLENE LÖSUNGEN:")

        # Spezifische Lösungsvorschläge
        if any('CustomTkinter' in problem for problem in problems_found):
            print("   🔧 CustomTkinter installieren: pip install customtkinter")

        if any('PIL' in problem for problem in problems_found):
            print("   🔧 Pillow installieren: pip install Pillow")

        if any('Import Error' in problem for problem in problems_found):
            print("   🔧 Syntax-Check ausführen: python -m py_compile modern_translation_quality_gui.py")

        if any('Missing file' in problem for problem in problems_found):
            print("   🔧 Fehlende Dateien aus Backup wiederherstellen")

        return False

def try_minimal_startup():
    """Versuche minimalen Quality GUI Start"""
    print("\n🚀 MINIMAL STARTUP TEST:")
    print("=" * 25)

    try:
        print("1. Import Quality GUI...")
        import modern_translation_quality_gui

        print("2. Import CustomTkinter...")
        import customtkinter as ctk

        print("3. Erstelle Root Window...")
        root = ctk.CTk()
        root.withdraw()  # Verstecke für Test

        print("4. Erstelle Quality GUI Instanz...")
        app = modern_translation_quality_gui.ProfessionalTranslationQualityApp()

        print("5. Teste GUI Methoden...")
        if hasattr(app, 'root'):
            print("✅ GUI Root verfügbar")

        print("✅ MINIMAL STARTUP ERFOLGREICH!")
        print("🎉 Quality GUI kann erstellt werden!")

        # Cleanup
        root.quit()
        root.destroy()

        return True

    except Exception as e:
        print(f"❌ MINIMAL STARTUP FEHLGESCHLAGEN: {e}")
        print("📋 Fehler-Details:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 QUALITY GUI STARTUP PROBLEM SOLVER")
    print("=" * 60)

    # Hauptdiagnose
    diagnosis_ok = diagnose_quality_gui_startup()

    # Wenn Basis-Diagnose OK, versuche minimalen Start
    if diagnosis_ok:
        startup_ok = try_minimal_startup()

        if startup_ok:
            print("\n🎉 ALLE TESTS ERFOLGREICH!")
            print("🚀 Quality GUI ist funktionsbereit!")
            print("\n▶️ Starte Quality GUI mit:")
            print("python modern_translation_quality_gui.py")
        else:
            print("\n⚠️ MINIMAL STARTUP FEHLGESCHLAGEN!")
            print("📋 Auch minimaler Start funktioniert nicht.")

    print("\n" + "=" * 60)
    print("Diagnostic Complete - Prüfe Ausgabe für Lösungsvorschläge")