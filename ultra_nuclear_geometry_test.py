"""
ULTRA-NUCLEAR GEOMETRY TEST

Dieser Test kombiniert ALLE verfügbaren Schutzmaßnahmen gegen Größenänderungen
und versucht, diese auf verschiedene Arten zu umgehen.

Er ist als ultimativer Stresstest konzipiert, um sicherzustellen, dass die
Fenstergröße unter allen Umständen exakt 1400x900 bleibt.
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
import time
import threading
import traceback

# Alle Schutzmodule importieren
import lite_nuclear_ctk_patch
import nuclear_geometry_manager
import window_size_monitor
import enforce_frame_sizes

class UltraNuclearTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ULTRA-NUCLEAR GEOMETRY TEST")
        
        # Fenstergröße initial setzen
        self.root.geometry("1400x900")
        self.root.minsize(1400, 900)
        self.root.maxsize(1400, 900)
        self.root.update_idletasks()
        
        # Haupt-Container erstellen
        self.main_frame = ctk.CTkFrame(
            self.root,
            width=1400,
            height=900,
            fg_color="#2B2B2B"
        )
        # CustomTkinter erlaubt keine width/height bei place, also benutzen wir relwidth/relheight
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_frame.pack_propagate(False)
        self.main_frame.grid_propagate(False)
        
        # Titel
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="ULTRA-NUCLEAR GEOMETRY TEST",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Dieser Test kombiniert ALLE Schutzmaßnahmen gegen Größenänderungen",
            font=("Arial", 16)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Status
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(pady=10, fill="x", padx=50)
        
        # Größenanzeige
        self.size_label = ctk.CTkLabel(
            self.status_frame,
            text="Aktuelle Größe: 0x0",
            font=("Arial", 16)
        )
        self.size_label.pack(pady=10)
        
        # Aktivierungs-Buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20, fill="x", padx=50)
        
        # Grid für Buttons
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        
        # Buttons für jede Schutzebene
        protection_buttons = [
            ("1. Basis Geometry Lock", self.activate_base_lock),
            ("2. Absoluter Size Lock", self.activate_absolute_lock),
            ("3. Click Interceptor", self.activate_click_interceptor),
            ("4. Nuclear Geometry Manager", self.activate_nuclear_manager),
            ("5. Window Size Monitor", self.activate_window_monitor),
            ("6. Frame Size Enforcer", self.activate_frame_enforcer),
            ("7. AKTIVIERE ALLE SCHUTZEBENEN", self.activate_all_protections),
        ]
        
        for i, (text, command) in enumerate(protection_buttons):
            row, col = divmod(i, 2)
            button = ctk.CTkButton(self.button_frame, text=text, command=command)
            button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Bereich für Stress-Tests
        self.test_frame = ctk.CTkFrame(self.main_frame)
        self.test_frame.pack(pady=20, fill="x", padx=50)
        
        # Grid für Test-Buttons
        self.test_frame.columnconfigure(0, weight=1)
        self.test_frame.columnconfigure(1, weight=1)
        
        # Test-Buttons
        test_buttons = [
            ("Resize auf 800x600", lambda: self.try_resize(800, 600)),
            ("Resize auf 1600x1200", lambda: self.try_resize(1600, 1200)),
            ("100 Große Widgets packen", self.pack_large_widgets),
            ("Verzerrende Grid-Struktur", self.create_distorting_grid),
            ("ULTRA STRESS TEST", self.run_ultra_stress_test),
            ("Zeige Schutzebenen-Bericht", self.show_protection_report),
        ]
        
        for i, (text, command) in enumerate(test_buttons):
            row, col = divmod(i, 2)
            button = ctk.CTkButton(self.test_frame, text=text, command=command)
            button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Ergebnis-Anzeige
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(pady=20, fill="both", expand=True, padx=50)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="Testergebnisse werden hier angezeigt",
            font=("Arial", 14),
            wraplength=1200
        )
        self.result_label.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Starte Größenüberwachung
        self.start_size_monitor()
    
    def update_status(self, message):
        """Aktualisiert die Statusanzeige"""
        self.result_label.configure(text=message)
        print(f"[TEST] {message}")
    
    def start_size_monitor(self):
        """Startet die Überwachung der Fenstergröße"""
        def update_size():
            if self.root.winfo_exists():
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                self.size_label.configure(text=f"Aktuelle Größe: {width}x{height}")
                
                # Farbe je nach Zustand
                if width == 1400 and height == 900:
                    self.size_label.configure(text_color="green")
                else:
                    self.size_label.configure(text_color="red")
                
                # Weiter überwachen
                self.root.after(100, update_size)
        
        # Starte die Überwachung
        self.root.after(100, update_size)
    
    def activate_base_lock(self):
        """Aktiviert den Basis Geometry Lock"""
        self.update_status("Aktiviere Basis Geometry Lock...")
        lite_nuclear_ctk_patch.activate_lock_for_window(self.root)
        self.update_status("Basis Geometry Lock aktiviert. Das Fenster sollte jetzt nicht unter seine Mindestgröße schrumpfen können.")
    
    def activate_absolute_lock(self):
        """Aktiviert den absoluten Size Lock"""
        self.update_status("Aktiviere absoluten Size Lock...")
        lite_nuclear_ctk_patch.activate_absolute_lock_for_main_window(self.root)
        self.update_status("Absoluter Size Lock aktiviert. Das Fenster sollte jetzt exakt 1400x900 bleiben.")
    
    def activate_click_interceptor(self):
        """Aktiviert den Click Interceptor"""
        self.update_status("Aktiviere Click Interceptor...")
        lite_nuclear_ctk_patch.activate_click_interceptor_for_main_window(self.root)
        self.update_status("Click Interceptor aktiviert. Nach jedem Klick sollte das Fenster auf 1400x900 zurückgesetzt werden.")
    
    def activate_nuclear_manager(self):
        """Aktiviert den Nuclear Geometry Manager"""
        self.update_status("Aktiviere Nuclear Geometry Manager...")
        nuclear_geometry_manager.apply_nuclear_geometry_control(self.root)
        self.update_status("Nuclear Geometry Manager aktiviert. Layout-Manager sollten jetzt die Fenstergröße nicht mehr ändern können.")
    
    def activate_window_monitor(self):
        """Aktiviert den Window Size Monitor"""
        self.update_status("Aktiviere Window Size Monitor...")
        window_size_monitor.enable_nuclear_protection(self.root, 1400, 900)
        self.update_status("Window Size Monitor aktiviert. Jede Größenänderung wird jetzt protokolliert und korrigiert.")
    
    def activate_frame_enforcer(self):
        """Aktiviert den Frame Size Enforcer"""
        self.update_status("Aktiviere Frame Size Enforcer...")
        self.main_enforcer = enforce_frame_sizes.enforce_frame_size(self.main_frame, 1400, 900, continuous=True)
        self.update_status("Frame Size Enforcer aktiviert. Die Größe des Hauptframes wird jetzt kontinuierlich überwacht und erzwungen.")
    
    def activate_all_protections(self):
        """Aktiviert ALLE Schutzebenen"""
        self.update_status("Aktiviere ALLE Schutzebenen...")
        
        # Reihenfolge ist wichtig
        lite_nuclear_ctk_patch.activate_lock_for_window(self.root)
        lite_nuclear_ctk_patch.activate_absolute_lock_for_main_window(self.root)
        lite_nuclear_ctk_patch.activate_click_interceptor_for_main_window(self.root)
        nuclear_geometry_manager.apply_nuclear_geometry_control(self.root)
        window_size_monitor.enable_nuclear_protection(self.root, 1400, 900)
        self.main_enforcer = enforce_frame_sizes.enforce_frame_size(self.main_frame, 1400, 900, continuous=True)
        
        # Setze die Größe nochmal explizit
        self.root.geometry("1400x900")
        self.root.minsize(1400, 900)
        self.root.maxsize(1400, 900)
        self.root.update_idletasks()
        
        self.update_status("ALLE Schutzebenen aktiviert! Das Fenster sollte jetzt unter allen Umständen exakt 1400x900 bleiben.")
    
    def try_resize(self, width, height):
        """Versucht, das Fenster auf eine bestimmte Größe zu setzen"""
        self.update_status(f"Versuche Resize auf {width}x{height}...")
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()
        
        # Prüfe, ob der Resize erfolgreich war
        actual_width = self.root.winfo_width()
        actual_height = self.root.winfo_height()
        
        if actual_width == 1400 and actual_height == 900:
            self.update_status(f"Resize auf {width}x{height} FEHLGESCHLAGEN - Schutz funktioniert! Fenster bleibt bei 1400x900.")
        else:
            self.update_status(f"Resize auf {width}x{height} ERFOLGREICH - Schutz hat VERSAGT! Aktuelle Größe: {actual_width}x{actual_height}")
    
    def pack_large_widgets(self):
        """Fügt 100 große Widgets hinzu, die versuchen, das Fenster zu vergrößern"""
        self.update_status("Füge 100 große Widgets hinzu...")
        
        # Frame für die Widgets
        container = ctk.CTkScrollableFrame(self.result_frame, width=1200, height=400)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Füge 100 große Widgets hinzu
        for i in range(100):
            frame = ctk.CTkFrame(container, width=2000, height=50)
            frame.pack(fill="x", pady=5)
            
            label = ctk.CTkLabel(frame, text=f"Großes Widget #{i+1} - Sollte das Fenster nicht vergrößern")
            label.pack(pady=10)
        
        self.update_status("100 große Widgets hinzugefügt. Das Fenster sollte weiterhin 1400x900 bleiben.")
    
    def create_distorting_grid(self):
        """Erstellt eine Grid-Struktur, die versucht, das Fenster zu verzerren"""
        self.update_status("Erstelle verzerrende Grid-Struktur...")
        
        # Lösche vorherige Inhalte
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Grid-Konfiguration
        for i in range(10):
            self.result_frame.columnconfigure(i, weight=1)
            self.result_frame.rowconfigure(i, weight=1)
        
        # Füge Widgets mit Stretch-Einstellungen hinzu
        for i in range(10):
            for j in range(10):
                frame = ctk.CTkFrame(self.result_frame, width=200, height=200)
                frame.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
                
                label = ctk.CTkLabel(frame, text=f"Grid {i},{j}")
                label.pack(expand=True, fill="both")
        
        self.update_status("Verzerrende Grid-Struktur erstellt. Das Fenster sollte weiterhin 1400x900 bleiben.")
    
    def run_ultra_stress_test(self):
        """Führt einen extremen Stress-Test durch"""
        self.update_status("Starte ULTRA STRESS TEST...")
        
        # Aktiviere zunächst alle Schutzebenen
        self.activate_all_protections()
        
        # Erstelle einen Thread für den Stress-Test
        def stress_thread():
            try:
                # 1. Mehrere Größenänderungen hintereinander
                for _ in range(20):
                    self.root.geometry("800x600")
                    time.sleep(0.01)
                    self.root.geometry("1600x1200")
                    time.sleep(0.01)
                
                # 2. Viele Widgets dynamisch hinzufügen und entfernen
                container = ctk.CTkFrame(self.result_frame)
                container.pack(fill="both", expand=True)
                
                for i in range(50):
                    # Hinzufügen
                    frames = []
                    for j in range(10):
                        frame = ctk.CTkFrame(container, width=2000, height=50)
                        frame.pack(fill="x", pady=2)
                        frames.append(frame)
                    
                    # Update erzwingen
                    self.root.update_idletasks()
                    time.sleep(0.01)
                    
                    # Entfernen
                    for frame in frames:
                        frame.destroy()
                    
                    # Update erzwingen
                    self.root.update_idletasks()
                    time.sleep(0.01)
                
                # 3. Layout-Wechsel zwischen pack, grid und place
                test_frame = ctk.CTkFrame(self.result_frame, width=1200, height=400)
                
                # Pack -> Grid -> Place -> Pack
                for _ in range(10):
                    # Pack
                    test_frame.pack(fill="both", expand=True)
                    self.root.update_idletasks()
                    time.sleep(0.01)
                    test_frame.pack_forget()
                    
                    # Grid
                    test_frame.grid(row=0, column=0, sticky="nsew")
                    self.root.update_idletasks()
                    time.sleep(0.01)
                    test_frame.grid_forget()
                    
                    # Place
                    test_frame.place(x=0, y=0, relwidth=1, relheight=1)
                    self.root.update_idletasks()
                    time.sleep(0.01)
                    test_frame.place_forget()
                
                # Im Hauptthread das Ergebnis anzeigen
                self.root.after(0, lambda: self.update_status("ULTRA STRESS TEST ABGESCHLOSSEN! Das Fenster sollte weiterhin exakt 1400x900 groß sein."))
            
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Fehler im Stress-Test: {e}"))
                traceback.print_exc()
        
        # Starte den Thread
        thread = threading.Thread(target=stress_thread)
        thread.daemon = True
        thread.start()
    
    def show_protection_report(self):
        """Zeigt einen Bericht über die aktivierten Schutzebenen"""
        report = "AKTIVE SCHUTZEBENEN:\n\n"
        
        # Prüfe jede Schutzebene
        try:
            # 1. Basis Geometry Lock
            if hasattr(self.root, '_locked_min_width'):
                report += "✅ Basis Geometry Lock ist aktiv\n"
                report += f"   Gesperrte Mindestgröße: {self.root._locked_min_width}x{self.root._locked_min_height}\n\n"
            else:
                report += "❌ Basis Geometry Lock ist NICHT aktiv\n\n"
            
            # 2. Min/Max Size
            min_w, min_h = self.root.minsize()
            max_w, max_h = self.root.maxsize()
            report += f"✅ Aktueller Min/Max Size: {min_w}x{min_h} / {max_w}x{max_h}\n\n"
            
            # 3. Window Size Monitor
            if hasattr(window_size_monitor, 'main_window_monitor') and window_size_monitor.main_window_monitor is not None:
                report += "✅ Window Size Monitor ist aktiv\n"
                report += f"   Zielgröße: {window_size_monitor.main_window_monitor.target_width}x{window_size_monitor.main_window_monitor.target_height}\n\n"
            else:
                report += "❌ Window Size Monitor ist NICHT aktiv\n\n"
            
            # 4. Frame Size Enforcer
            if hasattr(self, 'main_enforcer'):
                report += "✅ Frame Size Enforcer ist aktiv\n"
                report += f"   Überwachter Frame: {self.main_enforcer.frame}\n"
                report += f"   Zielgröße: {self.main_enforcer.target_width}x{self.main_enforcer.target_height}\n\n"
            else:
                report += "❌ Frame Size Enforcer ist NICHT aktiv\n\n"
            
            # 5. Aktuelle Fenstergröße
            current_w = self.root.winfo_width()
            current_h = self.root.winfo_height()
            
            if current_w == 1400 and current_h == 900:
                report += f"✅ AKTUELLE FENSTERGRÖßE: {current_w}x{current_h} - KORREKT!\n\n"
            else:
                report += f"❌ AKTUELLE FENSTERGRÖßE: {current_w}x{current_h} - FALSCH!\n"
                report += "   Sollte 1400x900 sein.\n\n"
            
            # 6. Gesamtbewertung
            if current_w == 1400 and current_h == 900 and min_w == 1400 and min_h == 900 and max_w == 1400 and max_h == 900:
                report += "✅ GESAMTBEWERTUNG: ALLE TESTS BESTANDEN!\n"
                report += "   Das Fenster hat die korrekte Größe und alle Sperren sind aktiv."
            else:
                report += "⚠️ GESAMTBEWERTUNG: EINIGE TESTS FEHLGESCHLAGEN!\n"
                report += "   Aktivieren Sie alle Schutzebenen und prüfen Sie erneut."
            
            self.update_status(report)
            
        except Exception as e:
            self.update_status(f"Fehler beim Erstellen des Berichts: {e}")
            traceback.print_exc()
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()

if __name__ == "__main__":
    app = UltraNuclearTest()
    app.run()
