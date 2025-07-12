"""
ABSOLUTE WINDOW SIZE TEST

Dieser Test überprüft die ABSOLUTE Fenstergröße von 1400x900
und versucht aktiv, diese zu brechen.
"""

import tkinter as tk
import customtkinter as ctk
import time
import sys
import threading

# CRITICAL: Import the comprehensive patch FIRST
import lite_nuclear_ctk_patch
import nuclear_geometry_manager

# Explizit die Funktionen importieren
from lite_nuclear_ctk_patch import (
    activate_lock_for_window,
    activate_absolute_lock_for_main_window,
    activate_click_interceptor_for_main_window
)

class WindowSizeTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ABSOLUTE WINDOW SIZE TEST - 1400x900")
        
        # Größe initial setzen
        self.root.geometry("1400x900")
        self.root.minsize(1400, 900)
        self.root.maxsize(1400, 900)
        
        # Informationen anzeigen
        label = ctk.CTkLabel(
            self.root, 
            text="ABSOLUTE WINDOW SIZE TEST\n"
                 "Dieses Fenster MUSS 1400x900 bleiben.",
            font=("Arial", 20, "bold")
        )
        label.pack(pady=20)
        
        # Statusanzeige
        self.status_label = ctk.CTkLabel(
            self.root,
            text="Status: Initialisiert",
            font=("Arial", 16)
        )
        self.status_label.pack(pady=10)
        
        # Größenanzeige
        self.size_label = ctk.CTkLabel(
            self.root,
            text="Aktuelle Größe: 0x0",
            font=("Arial", 16)
        )
        self.size_label.pack(pady=10)
        
        # Test-Buttons
        test_frame = ctk.CTkFrame(self.root)
        test_frame.pack(pady=20)
        
        # Standard Lock aktivieren
        std_lock_button = ctk.CTkButton(
            test_frame,
            text="1. Standard Lock aktivieren",
            command=self.activate_standard_lock
        )
        std_lock_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Absoluten Lock aktivieren
        abs_lock_button = ctk.CTkButton(
            test_frame,
            text="2. Absoluten Lock aktivieren",
            command=self.activate_absolute_lock
        )
        abs_lock_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Click-Interceptor aktivieren
        click_lock_button = ctk.CTkButton(
            test_frame,
            text="3. Click-Interceptor aktivieren",
            command=self.activate_click_interceptor
        )
        click_lock_button.grid(row=1, column=0, padx=10, pady=10)
        
        # Nuklearen Geometry Manager aktivieren
        nuclear_button = ctk.CTkButton(
            test_frame,
            text="4. Nuklearen Geometry Manager",
            command=self.activate_nuclear_manager
        )
        nuclear_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Versuche zu brechen
        break_frame = ctk.CTkFrame(self.root)
        break_frame.pack(pady=20)
        
        # Versuche kleiner zu machen
        small_button = ctk.CTkButton(
            break_frame,
            text="Versuche 800x600",
            command=lambda: self.try_resize(800, 600)
        )
        small_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Versuche größer zu machen
        large_button = ctk.CTkButton(
            break_frame,
            text="Versuche 1600x1200",
            command=lambda: self.try_resize(1600, 1200)
        )
        large_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Aggressiver Stress-Test
        stress_button = ctk.CTkButton(
            break_frame,
            text="STRESS TEST (100 Größenänderungen)",
            command=self.stress_test
        )
        stress_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Größenüberwachung starten
        self.start_size_monitor()
    
    def activate_standard_lock(self):
        self.update_status("Aktiviere Standard Lock...")
        activate_lock_for_window(self.root)
        self.update_status("Standard Lock aktiviert!")
    
    def activate_absolute_lock(self):
        self.update_status("Aktiviere Absoluten Lock...")
        activate_absolute_lock_for_main_window(self.root)
        self.update_status("Absoluter Lock aktiviert!")
    
    def activate_click_interceptor(self):
        self.update_status("Aktiviere Click-Interceptor...")
        activate_click_interceptor_for_main_window(self.root)
        self.update_status("Click-Interceptor aktiviert!")
    
    def activate_nuclear_manager(self):
        self.update_status("Aktiviere Nuklearen Geometry Manager...")
        nuclear_geometry_manager.apply_nuclear_geometry_control(self.root)
        self.update_status("Nuklearer Geometry Manager aktiviert!")
    
    def try_resize(self, width, height):
        self.update_status(f"Versuche Größe zu ändern auf {width}x{height}...")
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()
        self.update_status(f"Resize-Versuch abgeschlossen!")
    
    def stress_test(self):
        self.update_status("Starte Stress-Test mit 100 Größenänderungen...")
        
        # Erstelle Thread für Stress-Test
        def stress_thread():
            for i in range(100):
                # Abwechselnd klein und groß
                if i % 2 == 0:
                    width, height = 800, 600
                else:
                    width, height = 1600, 1200
                
                # Versuche zu ändern
                try:
                    self.root.geometry(f"{width}x{height}")
                    self.root.update_idletasks()
                    time.sleep(0.01)  # Kurze Pause
                except:
                    pass
            
            # Update im Hauptthread
            self.root.after(0, lambda: self.update_status("Stress-Test abgeschlossen!"))
        
        # Starte Thread
        thread = threading.Thread(target=stress_thread)
        thread.daemon = True
        thread.start()
    
    def update_status(self, text):
        self.status_label.configure(text=f"Status: {text}")
        print(f"[TEST] {text}")
    
    def start_size_monitor(self):
        def update_size():
            if self.root.winfo_exists():
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                self.size_label.configure(text=f"Aktuelle Größe: {width}x{height}")
                
                # Prüfe ob die Größe korrekt ist
                if width == 1400 and height == 900:
                    self.size_label.configure(text_color="green")
                else:
                    self.size_label.configure(text_color="red")
                
                # Nächste Prüfung planen
                self.root.after(100, update_size)
        
        # Erste Prüfung starten
        self.root.after(100, update_size)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WindowSizeTest()
    app.run()
