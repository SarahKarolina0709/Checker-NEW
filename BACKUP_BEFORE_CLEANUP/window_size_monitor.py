"""
Window Size Monitor - Überwacht und protokolliert Fenstergrößenänderungen
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
import sys
import traceback

class WindowSizeMonitor:
    """
    Überwacht ein Fenster auf Größenänderungen und protokolliert diese.
    Hilft bei der Diagnose, wann und warum ein Fenster seine Größe ändert.
    """
    
    def __init__(self, window, target_width=1400, target_height=900, interval_ms=100):
        """
        Initialisiert den Monitor.
        
        Args:
            window: Das zu überwachende Fenster (tk.Tk oder tk.Toplevel)
            target_width: Die Soll-Breite des Fensters
            target_height: Die Soll-Höhe des Fensters
            interval_ms: Das Überwachungsintervall in Millisekunden
        """
        self.window = window
        self.target_width = target_width
        self.target_height = target_height
        self.interval_ms = interval_ms
        self.monitoring = False
        self.last_size = (0, 0)
        self.size_history = []
        self.size_changes = []
        self.after_id = None
    
    def start(self):
        """Startet die Überwachung im Hintergrund."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self._check_size()
        print(f"[WINDOW MONITOR] Überwachung gestartet für {self.window}")
    
    def stop(self):
        """Stoppt die Überwachung."""
        self.monitoring = False
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
                self.after_id = None
            except:
                pass
        print(f"[WINDOW MONITOR] Überwachung gestoppt für {self.window}")
    
    def _check_size(self):
        """Überprüft die aktuelle Fenstergröße und protokolliert Änderungen."""
        if not self.monitoring or not self.window.winfo_exists():
            return
        
        try:
            # Aktuelle Größe ermitteln
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            current_size = (current_width, current_height)
            
            # Der Historie hinzufügen
            self.size_history.append(current_size)
            if len(self.size_history) > 100:  # Begrenze Historie
                self.size_history.pop(0)
            
            # Auf Änderung prüfen
            if current_size != self.last_size and self.last_size != (0, 0):
                self.size_changes.append({
                    'from': self.last_size,
                    'to': current_size,
                    'time': time.time()
                })
                
                # Protokolliere die Änderung
                print(f"[WINDOW MONITOR] Größenänderung erkannt: {self.last_size} -> {current_size}")
                
                # Soll-Größe überprüfen
                if current_width != self.target_width or current_height != self.target_height:
                    print(f"[WINDOW MONITOR] WARNUNG: Aktuelle Größe weicht von Soll-Größe ab!")
                    print(f"[WINDOW MONITOR] Aktuell: {current_width}x{current_height}, Soll: {self.target_width}x{self.target_height}")
                    
                    # Stack Trace ausgeben um Ursache zu finden
                    print("[WINDOW MONITOR] Stack Trace zum Zeitpunkt der Größenänderung:")
                    traceback.print_stack()
            
            self.last_size = current_size
            
            # Nächste Überprüfung planen
            self.after_id = self.window.after(self.interval_ms, self._check_size)
        
        except Exception as e:
            print(f"[WINDOW MONITOR] Fehler bei der Größenüberprüfung: {e}")
            if self.monitoring and self.window.winfo_exists():
                self.after_id = self.window.after(self.interval_ms * 2, self._check_size)
    
    def get_report(self):
        """Gibt einen Bericht über die aufgezeichneten Größenänderungen aus."""
        if not self.size_changes:
            return "Keine Größenänderungen aufgezeichnet."
        
        report = "Aufgezeichnete Größenänderungen:\n"
        for i, change in enumerate(self.size_changes):
            report += f"{i+1}. {change['from']} -> {change['to']}\n"
        
        return report
    
    def enforce_size(self):
        """Erzwingt die Zielgröße, falls das Fenster davon abweicht."""
        if not self.window.winfo_exists():
            return
        
        try:
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            
            if current_width != self.target_width or current_height != self.target_height:
                print(f"[WINDOW MONITOR] Erzwinge Zielgröße: {current_width}x{current_height} -> {self.target_width}x{self.target_height}")
                
                # Größe direkt setzen
                self.window.geometry(f"{self.target_width}x{self.target_height}")
                
                # Größenbegrenzungen setzen
                self.window.minsize(self.target_width, self.target_height)
                self.window.maxsize(self.target_width, self.target_height)
                
                # Update erzwingen
                self.window.update_idletasks()
        except Exception as e:
            print(f"[WINDOW MONITOR] Fehler beim Erzwingen der Größe: {e}")

# Globaler Monitor für das Hauptfenster
main_window_monitor = None

def start_monitoring(window, target_width=1400, target_height=900, interval_ms=100):
    """
    Startet die Überwachung für ein Fenster.
    
    Args:
        window: Das zu überwachende Fenster
        target_width: Die Soll-Breite
        target_height: Die Soll-Höhe
        interval_ms: Das Überwachungsintervall
    
    Returns:
        Der erstellte Monitor
    """
    global main_window_monitor
    
    # Wenn es sich um das Hauptfenster handelt, verwende den globalen Monitor
    if isinstance(window, tk.Tk):
        if main_window_monitor is None:
            main_window_monitor = WindowSizeMonitor(window, target_width, target_height, interval_ms)
            main_window_monitor.start()
        return main_window_monitor
    
    # Für andere Fenster erstelle einen neuen Monitor
    monitor = WindowSizeMonitor(window, target_width, target_height, interval_ms)
    monitor.start()
    return monitor

# def enable_nuclear_protection(window, target_width=1400, target_height=900):
#     """
#     Aktiviert den nuklearen Größenschutz für ein Fenster.
    
#     Diese Funktion kombiniert alle bekannten Methoden, um die Fenstergröße
#     absolut zu fixieren und jede Änderung zu verhindern.
    
#     Args:
#         window: Das zu schützende Fenster
#         target_width: Die zu fixierende Breite
#         target_height: Die zu fixierende Höhe
#     """
#     try:
#         print(f"[WINDOW MONITOR] Aktiviere nuklearen Größenschutz für {window}")
        
#         # 1. Fenstergröße explizit setzen
#         window.geometry(f"{target_width}x{target_height}")
        
#         # 2. Min- und Maxsize auf identische Werte setzen
#         window.minsize(target_width, target_height)
#         window.maxsize(target_width, target_height)
        
#         # 3. Update erzwingen
#         window.update_idletasks()
        
#         # 4. Importiere und verwende alle verfügbaren Locks
#         # import lite_nuclear_ctk_patch
#         # lite_nuclear_ctk_patch.activate_lock_for_window(window)
        
#         # if hasattr(lite_nuclear_ctk_patch, 'activate_absolute_lock_for_main_window'):
#         #     if isinstance(window, tk.Tk):
#         #         lite_nuclear_ctk_patch.activate_absolute_lock_for_main_window(window)
#         #     else:
#         #         # Für Toplevel-Fenster die spezifische Größe verwenden
#         #         lite_nuclear_ctk_patch.activate_absolute_window_lock(window, target_width, target_height)
        
#         # 5. Click-Interceptor wenn verfügbar
#         if hasattr(lite_nuclear_ctk_patch, 'activate_click_interceptor_for_main_window') and isinstance(window, tk.Tk):
#             lite_nuclear_ctk_patch.activate_click_interceptor_for_main_window(window)
        
#         # 6. Nuklearen Geometry Manager verwenden
#         import nuclear_geometry_manager
#         nuclear_geometry_manager.apply_nuclear_geometry_control(window)
        
#         # 7. Überwachung starten
#         monitor = start_monitoring(window, target_width, target_height, 50)
        
#         # 8. Periodische Korrektur einrichten
#         def _enforce_periodically():
#             if window.winfo_exists():
#                 monitor.enforce_size()
#                 window.after(25, _enforce_periodically)
        
#         window.after(25, _enforce_periodically)
        
#         print(f"[WINDOW MONITOR] Nuklearer Größenschutz aktiviert für {window}")
        
#     except Exception as e:
#         print(f"[WINDOW MONITOR] Fehler beim Aktivieren des nuklearen Größenschutzes: {e}")
#         traceback.print_exc()

# Exportiere die Hauptfunktionen
__all__ = ['start_monitoring', 'enable_nuclear_protection', 'WindowSizeMonitor']
