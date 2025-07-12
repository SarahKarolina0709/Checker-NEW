#!/usr/bin/env python3
"""
Testskript zur Überprüfung der UI-Optimierungen
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from checker_app import CheckerApp
    print("Starte Checker App mit optimierter UI...")
    print("Beachten Sie die folgenden Verbesserungen:")
    print("• Ausbalancierte Spaltenbreiten")
    print("• Vereinheitlichte Containerhöhen (630px)")
    print("• Optimierte Workflow-Karten")
    print("• Verbesserte Schriftgrößen und Abstände")
    print("• Verbesserter Hintergrund und Farbkontrast")
    
    app = CheckerApp()
    app.run()
    
except Exception as e:
    print(f"Fehler beim Start der App: {e}")
    import traceback
    traceback.print_exc()
