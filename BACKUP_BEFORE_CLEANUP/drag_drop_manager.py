"""
Drag & Drop Manager für die Checker App
Implementiert echte Drag & Drop Funktionalität mit tkinterdnd2
"""

import os
import logging
from typing import List, Callable, Optional
from tkinterdnd2 import TkinterDnD, DND_FILES

class DragDropManager:
    """
    Manager für Drag & Drop Funktionalität
    Unterstützt das Ziehen von Dateien auf bestimmte Widgets
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drop_targets = {}
        
    def make_drop_target(self, widget, callback: Callable[[List[str]], None], 
                        file_types: Optional[List[str]] = None):
        """
        Macht ein Widget zu einem Drag & Drop Ziel
        
        Args:
            widget: Das tkinter/customtkinter Widget
            callback: Funktion, die aufgerufen wird wenn Dateien dropped werden
            file_types: Liste erlaubter Dateierweiterungen (z.B. ['.pdf', '.docx'])
        """
        try:
            # Registriere Widget als Drop-Target
            widget.drop_target_register(DND_FILES)
            
            # Speichere Callback und Filter
            self.drop_targets[widget] = {
                'callback': callback,
                'file_types': file_types or []
            }
            
            # Binde Events
            widget.dnd_bind('<<DropEnter>>', lambda e: self._on_drop_enter(e, widget))
            widget.dnd_bind('<<DropPosition>>', lambda e: self._on_drop_position(e, widget))
            widget.dnd_bind('<<DropLeave>>', lambda e: self._on_drop_leave(e, widget))
            widget.dnd_bind('<<Drop>>', lambda e: self._on_drop(e, widget))
            
            self.logger.info(f"Widget als Drop-Target registriert: {widget}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Drop-Targets: {e}")
    
    def _on_drop_enter(self, event, widget):
        """Wird aufgerufen wenn Dateien über das Widget gezogen werden"""
        try:
            # Visuelles Feedback - Border-Farbe ändern
            if hasattr(widget, 'configure'):
                widget.configure(border_color="#0078D4", border_width=3)
            self.logger.debug("Drop enter event")
        except Exception as e:
            self.logger.error(f"Fehler in drop_enter: {e}")
    
    def _on_drop_position(self, event, widget):
        """Wird aufgerufen während Dateien über das Widget bewegt werden"""
        # Optional: Hier könnte man zusätzliches visuelles Feedback implementieren
        pass
    
    def _on_drop_leave(self, event, widget):
        """Wird aufgerufen wenn Dateien das Widget verlassen"""
        try:
            # Visuelles Feedback zurücksetzen
            if hasattr(widget, 'configure'):
                widget.configure(border_color="#808080", border_width=2)
            self.logger.debug("Drop leave event")
        except Exception as e:
            self.logger.error(f"Fehler in drop_leave: {e}")
    
    def _on_drop(self, event, widget):
        """Wird aufgerufen wenn Dateien auf das Widget fallen gelassen werden"""
        try:
            # Visuelles Feedback zurücksetzen
            if hasattr(widget, 'configure'):
                widget.configure(border_color="#808080", border_width=2)
            
            # Dateipfade aus Event extrahieren
            file_paths = self._parse_drop_data(event.data)
            
            if not file_paths:
                self.logger.warning("Keine gültigen Dateipfade gefunden")
                return
            
            # Filter anwenden falls vorhanden
            target_info = self.drop_targets.get(widget, {})
            file_types = target_info.get('file_types', [])
            
            if file_types:
                filtered_paths = []
                for path in file_paths:
                    _, ext = os.path.splitext(path.lower())
                    if ext in [ft.lower() for ft in file_types]:
                        filtered_paths.append(path)
                    else:
                        self.logger.info(f"Datei übersprungen (falscher Typ): {path}")
                file_paths = filtered_paths
            
            if not file_paths:
                self.logger.warning("Keine Dateien nach Filterung übrig")
                return
            
            # Callback ausführen
            callback = target_info.get('callback')
            if callback:
                callback(file_paths)
                self.logger.info(f"Drop erfolgreich: {len(file_paths)} Dateien")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Drop-Event: {e}")
    
    def _parse_drop_data(self, data: str) -> List[str]:
        """
        Parst die Drop-Daten und extrahiert Dateipfade
        
        Args:
            data: Rohe Drop-Daten vom Event
            
        Returns:
            Liste von Dateipfaden
        """
        try:
            # tkinterdnd2 gibt Dateipfade in geschweiften Klammern zurück
            # Format: "{Pfad1} {Pfad2}" oder einzelne Pfade ohne Klammern
            
            file_paths = []
            
            # Entferne äußere Klammern falls vorhanden
            data = data.strip()
            if data.startswith('{') and data.endswith('}'):
                data = data[1:-1]
            
            # Teile bei Leerzeichen, aber respektiere Pfade in Anführungszeichen/Klammern
            current_path = ""
            in_braces = 0
            
            i = 0
            while i < len(data):
                char = data[i]
                
                if char == '{':
                    in_braces += 1
                    if in_braces == 1:
                        # Beginne neuen Pfad
                        current_path = ""
                        i += 1
                        continue
                elif char == '}':
                    in_braces -= 1
                    if in_braces == 0:
                        # Pfad abgeschlossen
                        if current_path.strip():
                            file_paths.append(current_path.strip())
                        current_path = ""
                        i += 1
                        continue
                elif char == ' ' and in_braces == 0:
                    # Leerzeichen außerhalb von Klammern
                    if current_path.strip():
                        file_paths.append(current_path.strip())
                    current_path = ""
                    i += 1
                    continue
                
                current_path += char
                i += 1
            
            # Letzten Pfad hinzufügen falls vorhanden
            if current_path.strip():
                file_paths.append(current_path.strip())
            
            # Filtere nur existierende Dateien
            valid_paths = []
            for path in file_paths:
                if os.path.isfile(path):
                    valid_paths.append(path)
                else:
                    self.logger.warning(f"Pfad ist keine Datei: {path}")
            
            return valid_paths
            
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen der Drop-Daten: {e}")
            return []
    
    def remove_drop_target(self, widget):
        """
        Entfernt ein Widget als Drop-Target
        
        Args:
            widget: Das Widget, das entfernt werden soll
        """
        try:
            if widget in self.drop_targets:
                widget.drop_target_unregister()
                del self.drop_targets[widget]
                self.logger.info(f"Drop-Target entfernt: {widget}")
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Drop-Targets: {e}")
    
    def get_supported_file_types(self) -> List[str]:
        """
        Gibt eine Liste der unterstützten Dateierweiterungen zurück
        """
        return [
            '.pdf', '.doc', '.docx', '.txt', '.rtf', 
            '.xlsx', '.xls', '.pptx', '.ppt',
            '.odt', '.ods', '.odp'
        ]

# Globale Instanz für einfache Verwendung
drag_drop_manager = DragDropManager()
