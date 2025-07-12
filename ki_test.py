#!/usr/bin/env python3
"""
Test des KI-Moduls
"""
import sys
import traceback

try:
    print("Teste Import des KI-Moduls...")
    import ki_module
    print("KI-Modul erfolgreich importiert!")
    
    print("Verfügbare Funktionen im KI-Modul:")
    functions = [name for name in dir(ki_module) if callable(getattr(ki_module, name)) and not name.startswith("_")]
    for func in functions:
        print(f"- {func}")
    
    print("Test abgeschlossen!")
except Exception as e:
    print(f"Test fehlgeschlagen: {e}")
    traceback.print_exc()
