"""
Verbesserte Drag & Drop Integration mit TkinterDnD
"""

import os
import logging
from typing import List, Callable, Optional
import customtkinter as ctk
import tkinterdnd_integration

class ImprovedDragDropManager:
    """
    Verbesserte Drag & Drop Manager für CustomTkinter Widgets mit TkinterDnD
    """
    
    def __init__(self, root_window):
        self.root = root_window
        self.logger = logging.getLogger(__name__)
        self.drop_zones = {}
        
        # Prüfe TkinterDnD-Unterstützung mit der verbesserten Integration
        self.tkinterdnd_available = tkinterdnd_integration.is_tkinterdnd_available()
        
        # Überprüfe, ob das Root-Fenster korrekt initialisiert ist
        if self.tkinterdnd_available:
            self.tkinterdnd_properly_initialized = tkinterdnd_integration.setup_tkinterdnd_integration(self.root)
            if not self.tkinterdnd_properly_initialized:
                self.logger.warning("Root-Fenster unterstützt TkinterDnD nicht!")
                self.logger.warning("Init-Fehler: Das Root-Fenster wurde nicht als TkinterDnD.Tk() initialisiert.")
                self.logger.warning("Drag-&-Drop-Unterstützung wird auf Fallback-Modus umgestellt.")
                self.logger.warning("→ Root-Fenster als TkinterDnD.Tk() erzeugen.")
                
                # Erstelle Fallback-Manager statt Exception zu werfen
                self._init_fallback_mode()
        else:
            self.logger.warning("TkinterDnD ist nicht verfügbar!")
            self.logger.warning("Installiere TkinterDnD2: pip install tkinterdnd2")
            self._init_fallback_mode()
    
    def add_drop_zone(self, widget, callback: Callable[[List[str]], None], 
                     file_types: Optional[List[str]] = None):
        """
        Fügt eine Drop-Zone für ein CustomTkinter Widget hinzu
        
        Args:
            widget: CustomTkinter Widget
            callback: Callback-Funktion für dropped files
            file_types: Erlaubte Dateierweiterungen (z.B. ['.pdf', '.docx'])
        """
        try:
            # Registriere die Drop-Zone
            zone_id = id(widget)
            self.drop_zones[zone_id] = {
                'widget': widget,
                'callback': callback,
                'file_types': file_types or [],
                'original_style': self._get_widget_style(widget)
            }
            
            # Binde Mouse-Events für visuelles Feedback
            widget.bind('<Enter>', lambda e: self._on_mouse_enter(zone_id))
            widget.bind('<Leave>', lambda e: self._on_mouse_leave(zone_id))
            
            # Verwende die verbesserte TkinterDnD Integration, wenn verfügbar
            if self.tkinterdnd_available and self.tkinterdnd_properly_initialized:
                result = tkinterdnd_integration.make_drop_target(widget, callback, file_types)
                if result:
                    self.logger.info(f"Drop-Zone erfolgreich registriert: {widget}")
                    return True
            else:
                # Fallback mit Klick-zum-Auswählen
                self._setup_fallback_dnd(widget, zone_id)
                
            self.logger.info(f"Drop-Zone registriert für Widget {zone_id} (Native: {self.tkinterdnd_available})")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Drop-Zone: {e}")
            # Versuche Fallback-Methode im Fehlerfall
            try:
                self._setup_fallback_dnd(widget, zone_id)
                return True
            except:
                return False
            
    def _setup_native_dnd(self, widget, zone_id):
        """Setup echtes Drag&Drop mit TkinterDnD über die zentrale Integration."""
        try:
            zone_info = self.drop_zones.get(zone_id, {})
            callback = zone_info.get('callback')
            file_types = zone_info.get('file_types', [])
            
            # Verwende zentrale TkinterDnD Integration
            result = tkinterdnd_integration.make_drop_target(
                widget,
                lambda files: self._on_files_dropped(zone_id, files),
                file_types
            )
            
            if result:
                self.logger.info(f"Native Drag&Drop erfolgreich registriert für Widget {zone_id}")
                return True
            else:
                self.logger.warning(f"Native Drag&Drop konnte nicht registriert werden für Widget {zone_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des nativen Drag&Drop: {e}")
            return False
    
    def _setup_fallback_dnd(self, widget, zone_id):
        """Setup Fallback Drag&Drop mit Klick-zum-Auswählen."""
        try:
            # Füge Klick-Handler hinzu, der Dateiauswahl-Dialog öffnet
            def on_click(event):
                self._open_file_dialog(zone_id)
            
            widget.bind('<Button-1>', on_click)
            
            # Füge Tastatur-Support hinzu für Barrierefreiheit
            def on_key(event):
                if event.keysym in ['Return', 'space']:
                    self._open_file_dialog(zone_id)
            
            widget.bind('<KeyPress>', on_key)
            widget.focus_set()  # Widget kann Fokus erhalten
            
            self.logger.info(f"Fallback Drag&Drop (Klick-zum-Auswählen) registriert für Widget {zone_id}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Fallback Drag&Drop: {e}")
    
    def _open_file_dialog(self, zone_id):
        """Öffnet Dateiauswahl-Dialog als Fallback für Drag&Drop."""
        try:
            from tkinter import filedialog
            
            zone_info = self.drop_zones.get(zone_id)
            if not zone_info:
                return
            
            # Bestimme erlaubte Dateitypen
            file_types = zone_info.get('file_types', [])
            if file_types:
                filetypes = []
                for ext in file_types:
                    filetypes.append((f"{ext.upper()} Dateien", f"*{ext}"))
                filetypes.append(("Alle Dateien", "*.*"))
            else:
                filetypes = [("Alle Dateien", "*.*")]
            
            # Öffne Dateiauswahl-Dialog
            files = filedialog.askopenfilenames(
                title="Dateien auswählen",
                filetypes=filetypes
            )
            
            if files:
                # Rufe Callback mit ausgewählten Dateien auf
                callback = zone_info.get('callback')
                if callback:
                    callback(list(files))
                    self.logger.info(f"Dateien über Dialog ausgewählt: {len(files)} Dateien")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Öffnen des Dateiauswahl-Dialogs: {e}")
    
    def _get_widget_style(self, widget):
        """Extrahiert den aktuellen Stil eines Widgets"""
        try:
            style = {}
            if hasattr(widget, 'cget'):
                try:
                    style['fg_color'] = widget.cget('fg_color')
                except:
                    style['fg_color'] = "#F0F0F0"
                try:
                    style['border_color'] = widget.cget('border_color')
                except:
                    style['border_color'] = "#CCCCCC"
                try:
                    style['border_width'] = widget.cget('border_width')
                except:
                    style['border_width'] = 2
            return style
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren des Widget-Stils: {e}")
            return {'fg_color': "#F0F0F0", 'border_color': "#CCCCCC", 'border_width': 2}
    
    def _on_mouse_enter(self, zone_id):
        """Handler für Mouse Enter Events - Visuelles Feedback"""
        try:
            # Verwende die _highlight_drop_zone Methode mit success=False für normales Hover
            self._highlight_drop_zone(zone_id, success=False)
        except Exception as e:
            self.logger.error(f"Fehler in mouse_enter: {e}")
    
    def _on_mouse_leave(self, zone_id):
        """Handler für Mouse Leave Events - Stellt Original-Stil wieder her"""
        try:
            # Verwende die _restore_style Methode um Original-Stil wiederherzustellen
            self._restore_style(zone_id)
        except Exception as e:
            self.logger.error(f"Fehler in mouse_leave: {e}")
    
    def _on_root_drop(self, event):
        """Handler für Drop-Events auf dem Root-Fenster"""
        try:
            # Parse Dateipfade
            file_paths = self._parse_drop_data(event.data)
            if not file_paths:
                return
            
            # Finde das Widget unter der Maus
            x, y = self.root.winfo_pointerxy()
            target_widget = self.root.winfo_containing(x, y)
            
            if not target_widget:
                return
            
            # Finde die entsprechende Drop-Zone
            target_zone = None
            for zone_id, zone in self.drop_zones.items():
                if self._is_widget_or_child(target_widget, zone['widget']):
                    target_zone = zone
                    break
            
            if target_zone:
                # Filtere Dateien nach erlaubten Typen
                filtered_paths = self._filter_files(file_paths, target_zone['file_types'])
                
                if filtered_paths:
                    # Visuelles Feedback
                    self._show_drop_feedback(target_zone['widget'])
                    
                    # Rufe Callback auf
                    target_zone['callback'](filtered_paths)
                    
                    self.logger.info(f"Dateien erfolgreich dropped: {len(filtered_paths)} Dateien")
                else:
                    self.logger.warning("Keine gültigen Dateien zum Droppen gefunden")
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Root-Drop: {e}")
    
    def _is_widget_or_child(self, widget, target_widget):
        """Prüft, ob widget das target_widget ist oder ein Kind davon"""
        try:
            current = widget
            while current:
                if current == target_widget:
                    return True
                current = current.master if hasattr(current, 'master') else None
            return False
        except:
            return False
    
    def _filter_files(self, file_paths: List[str], allowed_types: List[str]) -> List[str]:
        """Filtert Dateien nach erlaubten Typen"""
        if not allowed_types:
            return file_paths
        
        filtered = []
        for path in file_paths:
            _, ext = os.path.splitext(path.lower())
            if ext in [t.lower() for t in allowed_types]:
                filtered.append(path)
        
        return filtered
    
    def _parse_drop_data(self, data: str) -> List[str]:
        """Parsed Drop-Daten zu Dateipfaden"""
        try:
            if not data:
                return []
            
            # TkinterDnD gibt Pfade in geschweiften Klammern zurück
            paths = []
            current_path = ""
            in_braces = False
            
            i = 0
            while i < len(data):
                char = data[i]
                
                if char == '{':
                    in_braces = True
                    current_path = ""
                elif char == '}':
                    in_braces = False
                    if current_path.strip() and os.path.exists(current_path.strip()):
                        paths.append(current_path.strip())
                    current_path = ""
                elif in_braces:
                    current_path += char
                elif char == ' ' and not in_braces:
                    if current_path.strip() and os.path.exists(current_path.strip()):
                        paths.append(current_path.strip())
                    current_path = ""
                else:
                    current_path += char
                
                i += 1
            
            # Letzten Pfad hinzufügen falls vorhanden
            if current_path.strip() and os.path.exists(current_path.strip()):
                paths.append(current_path.strip())
            
            return paths
            
        except Exception as e:
            self.logger.error(f"Fehler beim Parsen der Drop-Daten: {e}")
            return []
    
    def _show_drop_feedback(self, widget):
        """Zeigt visuelles Feedback für erfolgreichen Drop"""
        try:
            if hasattr(widget, 'configure'):
                # Kurzes grünes Feedback
                widget.configure(
                    fg_color="#C8E6C9",
                    border_color="#4CAF50",
                    border_width=3
                )
                
                # Nach 500ms zurück zum normalen Stil
                widget.after(500, lambda: self._restore_widget_style(widget))
                
        except Exception as e:
            self.logger.error(f"Fehler beim Drop-Feedback: {e}")
    
    def _restore_widget_style(self, widget):
        """Stellt den ursprünglichen Widget-Stil wieder her"""
        try:
            zone_id = id(widget)
            zone = self.drop_zones.get(zone_id)
            if zone:
                original = zone['original_style']
                if hasattr(widget, 'configure'):
                    widget.configure(
                        fg_color=original.get('fg_color', "#F0F0F0"),
                        border_color=original.get('border_color', "#CCCCCC"),
                        border_width=original.get('border_width', 2)
                    )
        except Exception as e:
            self.logger.error(f"Fehler beim Wiederherstellen des Widget-Stils: {e}")
    
    def _init_fallback_mode(self):
        """Initialisiert den Fallback-Modus ohne TkinterDnD."""
        self.logger.info("Initialisiere Fallback-Drag&Drop-Modus")
        # Im Fallback-Modus können Drop-Zones registriert werden,
        # aber sie werden nur visuelles Feedback bieten und 
        # Dateiauswahl-Dialoge öffnen statt echtes Drag&Drop zu unterstützen
    
    def _on_files_dropped(self, zone_id, file_paths):
        """
        Verarbeitet gedropte Dateien für eine spezifische Drop-Zone
        
        Args:
            zone_id: ID der Drop-Zone
            file_paths: Liste mit Dateipfaden
        """
        try:
            zone_info = self.drop_zones.get(zone_id, {})
            if not zone_info:
                self.logger.warning(f"Drop-Zone {zone_id} nicht gefunden!")
                return
                
            widget = zone_info.get('widget')
            callback = zone_info.get('callback')
            file_types = zone_info.get('file_types', [])
            
            # Visuelles Feedback (kurzes Aufleuchten)
            self._highlight_drop_zone(zone_id, success=True)
            
            # Filter Dateien nach erlaubten Typen
            if file_types:
                filtered_paths = []
                for path in file_paths:
                    if os.path.isfile(path):  # Stelle sicher, dass es eine Datei ist
                        _, ext = os.path.splitext(path)
                        ext = ext.lower()
                        if not file_types or ext in [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]:
                            filtered_paths.append(path)
                file_paths = filtered_paths
            
            # Rufe Callback auf, wenn Dateien vorhanden sind
            if file_paths and callback:
                self.logger.info(f"Verarbeite {len(file_paths)} gedropte Dateien für Zone {zone_id}")
                callback(file_paths)
            elif not file_paths:
                self.logger.warning(f"Keine passenden Dateien für Zone {zone_id} gefunden!")
                
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung gedropter Dateien: {e}")
    
    def _highlight_drop_zone(self, zone_id, success=False):
        """Hebt eine Drop-Zone kurz hervor (visuelles Feedback)"""
        try:
            zone_info = self.drop_zones.get(zone_id, {})
            if not zone_info:
                return
                
            widget = zone_info.get('widget')
            original_style = zone_info.get('original_style', {})
            
            if not widget or not hasattr(widget, 'configure'):
                return
                
            # Farben für Erfolgs- oder normales Highlight
            highlight_color = "#E8F5E9" if success else "#E3F2FD"  # Grün für Erfolg, Blau für Hover
            highlight_border = "#4CAF50" if success else "#2196F3"
            
            # Setze Highlight-Stil
            try:
                widget.configure(
                    fg_color=highlight_color,
                    border_color=highlight_border,
                    border_width=2
                )
                
                # Stelle original Stil nach Verzögerung wieder her
                if hasattr(widget, 'after'):
                    widget.after(300, lambda: self._restore_style(zone_id))
            except Exception as e:
                self.logger.debug(f"Konnte Widget-Stil nicht ändern: {e}")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hervorheben der Drop-Zone: {e}")
            
    def _restore_style(self, zone_id):
        """Stellt den originalen Stil einer Drop-Zone wieder her"""
        try:
            zone_info = self.drop_zones.get(zone_id, {})
            if not zone_info:
                return
                
            widget = zone_info.get('widget')
            original_style = zone_info.get('original_style', {})
            
            if not widget or not hasattr(widget, 'configure'):
                return
                
            # Stelle originalen Stil wieder her
            try:
                widget.configure(
                    fg_color=original_style.get('fg_color', widget.cget('fg_color')),
                    border_color=original_style.get('border_color', widget.cget('border_color')),
                    border_width=original_style.get('border_width', widget.cget('border_width'))
                )
            except Exception as e:
                self.logger.debug(f"Konnte original Stil nicht wiederherstellen: {e}")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Wiederherstellen des Stils: {e}")
    

# Globale Instanz für einfache Verwendung
_improved_dnd_manager = None

def get_improved_dnd_manager(root_window=None):
    """Gibt die globale ImprovedDragDropManager Instanz zurück oder None bei Fehlern"""
    global _improved_dnd_manager
    if _improved_dnd_manager is None and root_window:
        try:
            _improved_dnd_manager = ImprovedDragDropManager(root_window)
        except Exception as e:
            # Log den Fehler aber werfe keine Exception
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Konnte Drag&Drop Manager nicht initialisieren: {e}")
            logger.error("Drag&Drop-Funktionalität nicht verfügbar")
            return None
    return _improved_dnd_manager
