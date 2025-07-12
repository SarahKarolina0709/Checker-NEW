"""
Enforce Frame Sizes - Erzwingt die Größe von Frames unabhängig von deren Inhalt
"""

import customtkinter as ctk
import tkinter as tk
import time
import traceback

class FrameSizeEnforcer:
    """
    Erzwingt die Größe eines Frames oder CTkFrames unabhängig von seinem Inhalt.
    Verhindert, dass Kinder-Widgets die Größe des Frames ändern.
    """
    
    def __init__(self, frame, width, height, interval_ms=50):
        """
        Initialisiert den FrameSizeEnforcer.
        
        Args:
            frame: Der zu überwachende Frame (tk.Frame oder ctk.CTkFrame)
            width: Die zu erzwingende Breite
            height: Die zu erzwingende Höhe
            interval_ms: Das Überwachungsintervall in Millisekunden
        """
        self.frame = frame
        self.target_width = width
        self.target_height = height
        self.interval_ms = interval_ms
        self.enforcing = False
        self.after_id = None
        
        # Sofort anwenden
        self._apply_protections()
    
    def _apply_protections(self):
        """Wendet alle bekannten Schutzmaßnahmen auf den Frame an."""
        try:
            # 1. Propagation deaktivieren
            if hasattr(self.frame, 'pack_propagate'):
                self.frame.pack_propagate(False)
            if hasattr(self.frame, 'grid_propagate'):
                self.frame.grid_propagate(False)
            
            # 2. Größe explizit setzen
            self.frame.configure(width=self.target_width, height=self.target_height)
            
            # 3. Bei CTkFrame zusätzliche Methoden verwenden
            if isinstance(self.frame, ctk.CTkFrame) and hasattr(self.frame, '_set_dimensions'):
                self.frame._set_dimensions(self.target_width, self.target_height)
            
            # 4. Update erzwingen
            if hasattr(self.frame, 'update_idletasks'):
                self.frame.update_idletasks()
                
            print(f"[FRAME ENFORCER] Protections applied to {self.frame}: {self.target_width}x{self.target_height}")
        except Exception as e:
            print(f"[FRAME ENFORCER] Error applying protections: {e}")
    
    def start_enforcing(self):
        """Startet die kontinuierliche Überwachung und Erzwingung der Framegröße."""
        if self.enforcing:
            return
        
        self.enforcing = True
        self._enforce_size()
        print(f"[FRAME ENFORCER] Started enforcing for {self.frame}")
    
    def stop_enforcing(self):
        """Stoppt die Überwachung."""
        self.enforcing = False
        if self.after_id and self.frame.winfo_exists():
            try:
                self.frame.after_cancel(self.after_id)
                self.after_id = None
            except:
                pass
        print(f"[FRAME ENFORCER] Stopped enforcing for {self.frame}")
    
    def _enforce_size(self):
        """Überprüft und korrigiert die Framegröße periodisch."""
        if not self.enforcing or not self.frame.winfo_exists():
            return
        
        try:
            # Aktuelle Größe ermitteln
            current_width = self.frame.winfo_width()
            current_height = self.frame.winfo_height()
            
            # Korrigieren wenn nötig
            if current_width != self.target_width or current_height != self.target_height:
                print(f"[FRAME ENFORCER] Correcting size: {current_width}x{current_height} -> {self.target_width}x{self.target_height}")
                self._apply_protections()
            
            # Nächste Überprüfung planen
            self.after_id = self.frame.after(self.interval_ms, self._enforce_size)
            
        except Exception as e:
            print(f"[FRAME ENFORCER] Error during size enforcement: {e}")
            if self.enforcing and self.frame.winfo_exists():
                self.after_id = self.frame.after(self.interval_ms * 2, self._enforce_size)

def enforce_frame_size(frame, width, height, continuous=True):
    """
    Erzwingt die Größe eines Frames.
    
    Args:
        frame: Der Frame (tk.Frame oder ctk.CTkFrame)
        width: Die zu erzwingende Breite
        height: Die zu erzwingende Höhe
        continuous: Ob die Größe kontinuierlich überwacht werden soll
    
    Returns:
        Der erstellte FrameSizeEnforcer
    """
    enforcer = FrameSizeEnforcer(frame, width, height)
    
    if continuous:
        enforcer.start_enforcing()
    
    return enforcer

def enforce_all_frames(root, width_map=None, height_map=None):
    """
    Durchsucht rekursiv alle Frames und erzwingt ihre Größe.
    
    Args:
        root: Das Wurzel-Widget
        width_map: Dictionary mit IDs oder Tags und zugehörigen Breiten
        height_map: Dictionary mit IDs oder Tags und zugehörigen Höhen
    
    Returns:
        Liste der erstellten Enforcer
    """
    width_map = width_map or {}
    height_map = height_map or {}
    enforcers = []
    
    def _process_widget(widget):
        # Prüfen ob es ein Frame ist
        if isinstance(widget, (tk.Frame, ctk.CTkFrame)):
            # ID oder Tag ermitteln
            widget_id = None
            if hasattr(widget, '_name'):
                widget_id = widget._name
            
            # Größe aus den Maps ermitteln oder aktuelle Größe verwenden
            width = width_map.get(widget_id, widget.winfo_width())
            height = height_map.get(widget_id, widget.winfo_height())
            
            # Nur sinnvolle Größen verwenden
            if width > 10 and height > 10:
                enforcer = enforce_frame_size(widget, width, height)
                enforcers.append(enforcer)
        
        # Rekursiv für alle Kinder
        for child in widget.winfo_children():
            _process_widget(child)
    
    # Starte mit dem Root-Widget
    _process_widget(root)
    
    return enforcers

# Exportiere die Hauptfunktionen
__all__ = ['enforce_frame_size', 'enforce_all_frames', 'FrameSizeEnforcer']
