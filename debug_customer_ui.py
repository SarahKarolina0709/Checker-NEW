#!/usr/bin/env python3
"""
Debug-Script für Customer UI Problem
Analysiert was bei show_customer_menu() passiert
"""

import os
import sys
import traceback

def debug_customer_ui():
    """Debugge Customer UI Problem"""
    
    print("🔍 DEBUG: Customer UI Problem Analyse")
    print("=" * 50)
    
    # 1. Prüfe welche Customer UI Dateien verfügbar sind
    print("\n📁 Verfügbare Customer UI Dateien:")
    customer_files = [
        "simplified_modern_customer_ui.py",
        "welcome_screen_components/customer_section_complete.py",
        "ui_modernization_update.py",
        "checker_app.py"
    ]
    
    for file_path in customer_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (FEHLT)")
    
    # 2. Prüfe show_customer_menu Implementierung
    print("\n🔍 show_customer_menu() Analyse:")
    
    try:
        with open("checker_app.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Finde show_customer_menu
        if "def show_customer_menu(self):" in content:
            print("   ✅ show_customer_menu() gefunden")
            
            # Prüfe CustomerSectionComplete Integration
            if "CustomerSectionComplete" in content:
                print("   ✅ CustomerSectionComplete Import vorhanden")
            else:
                print("   ❌ CustomerSectionComplete Import FEHLT")
                
            # Prüfe ViewStack Integration  
            if "customer_management" in content and "views.show" in content:
                print("   ✅ ViewStack Integration vorhanden")
            else:
                print("   ⚠️ ViewStack Integration möglicherweise unvollständig")
                
        else:
            print("   ❌ show_customer_menu() NICHT GEFUNDEN")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Analysieren: {e}")
    
    # 3. Prüfe ImportError Probleme
    print("\n📦 Import-Test:")
    
    import_tests = [
        ("simplified_modern_customer_ui", "SimplifiedModernCustomerUI"),
        ("welcome_screen_components.customer_section_complete", "CustomerSectionComplete"),
        ("ui_modernization_update", "ModernUIUpdater"),
        ("view_stack", "EnhancedViewStack")
    ]
    
    for module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}.{class_name} - ImportError: {e}")
        except AttributeError as e:
            print(f"   ⚠️ {module_name}.{class_name} - AttributeError: {e}")
        except Exception as e:
            print(f"   ❌ {module_name}.{class_name} - Error: {e}")
    
    # 4. Empfohlene Fixes
    print("\n🔧 Empfohlene Lösungen:")
    
    print("\n1. ✅ CustomerSectionComplete Integration prüfen:")
    print("   - Prüfe ob CustomerSectionComplete in show_customer_menu() verwendet wird")
    print("   - ViewStack Integration für 'customer_management' prüfen")
    
    print("\n2. ⚠️ Prioritätssystem implementieren:")
    print("   try:")
    print("       # Priorität 1: CustomerSectionComplete")
    print("       self.show_customer_section_complete()")
    print("   except:")
    print("       # Priorität 2: SimplifiedModernCustomerUI")
    print("       self.show_simplified_customer_ui()")
    
    print("\n3. 🔄 ViewStack korrekt verwenden:")
    print("   if hasattr(self, 'views') and self.views:")
    print("       self.views.show('customer_management')")
    
    print("\n4. 📋 Debugging aktivieren:")
    print("   - Mehr Debug-Ausgaben in show_customer_menu()")
    print("   - Exception Handling verbessern")
    print("   - Import-Errors abfangen")

if __name__ == "__main__":
    debug_customer_ui()

import sys
import tkinter as tk
from pathlib import Path

def identify_running_gui():
    """Identifiziert welche Customer Management GUI aktuell läuft"""
    
    # Erstelle Debug-Fenster
    debug_window = tk.Tk()
    debug_window.title("🔍 GUI Debug - Welche Customer Management GUI läuft?")
    debug_window.geometry("800x600")
    debug_window.configure(bg="#f0f0f0")
    
    # Header
    header_label = tk.Label(
        debug_window,
        text="🔍 GUI Debug Analyse",
        font=("Arial", 16, "bold"),
        bg="#f0f0f0",
        fg="#333"
    )
    header_label.pack(pady=10)
    
    # Info Text
    info_text = """
Das Screenshot zeigt eine Customer Management GUI mit:
- Kundenmanagement Header 
- Suchfeld "Kunde suchen..."
- Filter Buttons: Alle, Aktiv, Inaktiv
- Kundenkarten: TechCorp GmbH, Global Solutions, StartUp Innovation
- Datei-Upload Sektion

Diese GUI entspricht NICHT der CustomerSectionComplete, die wir integriert haben!
    """
    
    info_label = tk.Label(
        debug_window,
        text=info_text,
        font=("Arial", 11),
        bg="#f0f0f0",
        fg="#666",
        justify="left",
        wraplength=750
    )
    info_label.pack(pady=20, padx=20)
    
    # Mögliche Ursachen
    ursachen_frame = tk.Frame(debug_window, bg="#fff", relief="ridge", bd=2)
    ursachen_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    ursachen_title = tk.Label(
        ursachen_frame,
        text="🚨 Mögliche Ursachen:",
        font=("Arial", 14, "bold"),
        bg="#fff",
        fg="#d63384"
    )
    ursachen_title.pack(pady=10)
    
    ursachen_liste = [
        "1. checker_app.py ist beschädigt (Syntax-Fehler) → Fallback GUI läuft",
        "2. SimplifiedModernCustomerUI wird geladen statt CustomerSectionComplete",
        "3. Eine andere Customer Management App läuft parallel",
        "4. ui_modernizer.show_modern_customer_management() wird aufgerufen",
        "5. ViewStack Integration funktioniert nicht → Fallback aktiviert"
    ]
    
    for ursache in ursachen_liste:
        ursache_label = tk.Label(
            ursachen_frame,
            text=ursache,
            font=("Arial", 10),
            bg="#fff",
            fg="#333",
            anchor="w",
            justify="left"
        )
        ursache_label.pack(anchor="w", padx=20, pady=2)
    
    # Lösungsvorschläge
    loesungen_frame = tk.Frame(debug_window, bg="#e8f5e8", relief="ridge", bd=2)
    loesungen_frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    loesungen_title = tk.Label(
        loesungen_frame,
        text="✅ Lösungsvorschläge:",
        font=("Arial", 14, "bold"),
        bg="#e8f5e8",
        fg="#198754"
    )
    loesungen_title.pack(pady=10)
    
    loesungen_liste = [
        "1. checker_app.py syntax reparieren",
        "2. Prüfen ob ViewStack Integration aktiv ist",
        "3. Debug welche show_customer_menu() Priorität greift",
        "4. Alle Python-Prozesse beenden und neu starten",
        "5. CustomerSectionComplete direkt testen"
    ]
    
    for loesung in loesungen_liste:
        loesung_label = tk.Label(
            loesungen_frame,
            text=loesung,
            font=("Arial", 10),
            bg="#e8f5e8",
            fg="#333",
            anchor="w",
            justify="left"
        )
        loesung_label.pack(anchor="w", padx=20, pady=2)
    
    # Action Buttons
    button_frame = tk.Frame(debug_window, bg="#f0f0f0")
    button_frame.pack(pady=20)
    
    def close_debug():
        debug_window.destroy()
    
    def check_processes():
        import subprocess
        try:
            result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                                  capture_output=True, text=True)
            
            process_window = tk.Toplevel(debug_window)
            process_window.title("🔍 Python Prozesse")
            process_window.geometry("600x400")
            
            text_widget = tk.Text(process_window, wrap="word")
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            text_widget.insert("1.0", result.stdout)
            
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Konnte Prozesse nicht prüfen: {e}")
    
    tk.Button(
        button_frame,
        text="🔍 Python Prozesse prüfen",
        command=check_processes,
        bg="#0d6efd",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=5
    ).pack(side="left", padx=10)
    
    tk.Button(
        button_frame,
        text="❌ Schließen",
        command=close_debug,
        bg="#dc3545",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=5
    ).pack(side="left", padx=10)
    
    # Zeige aktueller Pfad
    pfad_label = tk.Label(
        debug_window,
        text=f"Aktueller Pfad: {Path.cwd()}",
        font=("Arial", 9),
        bg="#f0f0f0",
        fg="#999"
    )
    pfad_label.pack(side="bottom", pady=5)
    
    debug_window.mainloop()

if __name__ == "__main__":
    identify_running_gui()
