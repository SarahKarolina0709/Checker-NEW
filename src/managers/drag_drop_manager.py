"""
Enhanced Drag & Drop Manager für die Checker App
Implementiert moderne Drag & Drop Funktionalität mit visuellen Effekten und Animationen
"""

from typing import List, Callable, Optional
import logging
import os

from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinterdnd_integration

class EnhancedDragDropManager:
    """
    Enhanced Manager für Drag & Drop Funktionalität mit modernen visuellen Effekten
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drop_targets = {}
        self.tkinterdnd_available = tkinterdnd_integration.is_tkinterdnd_available()

    def make_enhanced_drop_target(self, widget, callback: Callable[[List[str]], None],
                                file_types: Optional[List[str]] = None,
                                progress_callback: Optional[Callable[[int, int, str], None]] = None):
        """
        Macht ein Widget zu einem erweiterten Drag & Drop Ziel mit visuellen Effekten

        Args:
            widget: Das tkinter/customtkinter Widget
            callback: Funktion, die aufgerufen wird wenn Dateien dropped werden
            file_types: Liste erlaubter Dateierweiterungen (z.B. ['.pdf', '.docx'])
            progress_callback: Optional callback für Fortschrittsanzeige
        """
        try:
            if not self.tkinterdnd_available:
                self.logger.warning("TkinterDnD2 ist nicht verfügbar, verwende Fallback")
                return self._setup_fallback_drag_drop(widget, callback, file_types)

            # Speichere original styling
            original_fg_color = getattr(widget, 'cget', lambda x: "#F0F0F0")("fg_color") if hasattr(widget, 'cget') else "#F0F0F0"
            original_border_color = getattr(widget, 'cget', lambda x: "#CCCCCC")("border_color") if hasattr(widget, 'cget') else "#CCCCCC"
            original_border_width = getattr(widget, 'cget', lambda x: 2)("border_width") if hasattr(widget, 'cget') else 2

            # Speichere erweiterte Informationen
            self.drop_targets[widget] = {
                'callback': callback,
                'progress_callback': progress_callback,
                'file_types': file_types or [],
                'original_style': {
                    'fg_color': original_fg_color,
                    'border_color': original_border_color,
                    'border_width': original_border_width
                },
                'is_dragging': False
            }

            # Verwende die neue Integration für das Setup
            result = tkinterdnd_integration.make_drop_target(
                widget,
                lambda files: self._handle_dropped_files(widget, files),
                file_types
            )

            if result:
                self.logger.info(f"Enhanced Drop-Target registriert: {widget}")
                return True
            else:
                self.logger.warning(f"Konnte kein Enhanced Drop-Target für {widget} registrieren, verwende Fallback")
                return self._setup_fallback_drag_drop(widget, callback, file_types)

        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Enhanced Drop-Targets: {e}")
            # Fallback
            return self._setup_fallback_drag_drop(widget, callback, file_types)

    def _handle_dropped_files(self, widget, file_paths):
        """Verarbeitet gedropte Dateien mit allen erweiterten Funktionen"""
        try:
            target_info = self.drop_targets.get(widget, {})

            # Success-Feedback visuell anzeigen
            self._show_drop_success_feedback(widget)

            # Nach kurzer Verzögerung zum ursprünglichen Stil zurückkehren
            if hasattr(widget, 'after'):
                widget.after(500, lambda: self._restore_original_style(widget))

            if not file_paths:
                self.logger.warning("Keine gültigen Dateipfade gefunden")
                return

            # Filter anwenden falls vorhanden
            file_types = target_info.get('file_types', [])
            if file_types:
                filtered_paths = []
                for path in file_paths:
                    _, ext = os.path.splitext(path.lower())
                    if ext in [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]:
                        filtered_paths.append(path)
                    else:
                        self.logger.info(f"Datei übersprungen (falscher Typ): {path}")
                file_paths = filtered_paths

            if not file_paths:
                self.logger.warning("Keine Dateien nach Filterung übrig")
                self._show_no_valid_files_feedback(widget)
                return

            # Progress Callback für mehrere Dateien
            progress_callback = target_info.get('progress_callback')
            if progress_callback and len(file_paths) > 1:
                self._process_files_with_progress(file_paths, target_info, progress_callback)
            else:
                # Normale Verarbeitung für einzelne Datei
                callback = target_info.get('callback')
                if callback:
                    callback(file_paths)
                    self.logger.info(f"Enhanced Drop erfolgreich: {len(file_paths)} Dateien")

        except Exception as e:
            self.logger.error(f"Fehler beim Enhanced Drop-Event: {e}")
            self._show_drop_error_feedback(widget)

    def _add_drop_glow_animation(self, widget):
        """Fügt einen Glow-Effekt für die Drop-Zone hinzu"""
        try:
            # Simpler Glow-Effekt durch Border-Manipulation
            colors = ["#2196F3", "#64B5F6", "#90CAF9", "#64B5F6"]
            self._cycle_border_colors(widget, colors, 0)
        except Exception as e:
            self.logger.error(f"Fehler beim Glow-Effekt: {e}")

    def _cycle_border_colors(self, widget, colors, index):
        """Zykliert durch Border-Farben für Glow-Effekt"""
        try:
            target_info = self.drop_targets.get(widget, {})
            if not target_info.get('is_dragging', False):
                return

            if hasattr(widget, 'configure'):
                widget.configure(border_color=colors[index % len(colors)])

            # Nächste Farbe nach 150ms
            widget.after(150, lambda: self._cycle_border_colors(widget, colors, index + 1))
        except Exception as e:
            self.logger.error(f"Fehler beim Farb-Zyklus: {e}")

    def _add_enhanced_drop_glow_animation(self, widget):
        """Fügt einen erweiterten Glow-Effekt mit sanfteren Animationen hinzu"""
        try:
            # Erweiterte Glow-Farbpalette mit sanfteren Übergängen
            colors = [
                "#1E88E5",  # Material Blue 600
                "#42A5F5",  # Material Blue 400
                "#64B5F6",  # Material Blue 300
                "#90CAF9",  # Material Blue 200
                "#64B5F6",  # Material Blue 300
                "#42A5F5"   # Material Blue 400
            ]
            self._cycle_enhanced_border_colors(widget, colors, 0)
        except Exception as e:
            self.logger.error(f"Fehler beim erweiterten Glow-Effekt: {e}")

    def _cycle_enhanced_border_colors(self, widget, colors, index):
        """Zykliert durch Border-Farben mit sanfteren Übergängen"""
        try:
            target_info = self.drop_targets.get(widget, {})
            if not target_info.get('is_dragging', False):
                return

            if hasattr(widget, 'configure'):
                widget.configure(border_color=colors[index % len(colors)])

            # Langsamerer Zyklus für sanftere Animation (200ms statt 150ms)
            widget.after(200, lambda: self._cycle_enhanced_border_colors(widget, colors, index + 1))
        except Exception as e:
            self.logger.error(f"Fehler beim erweiterten Farb-Zyklus: {e}")

    def _add_drop_scale_animation(self, widget, scale_up=True):
        """Fügt eine subtile Scale-Animation hinzu für besseres visuelles Feedback"""
        try:
            # Nur für CTk Widgets mit place geometry manager
            if hasattr(widget, 'place_configure'):
                current_info = widget.place_info()
                if current_info:
                    # Sanfte Scale-Animation
                    if scale_up:
                        # Leichte Vergrößerung (2%)
                        widget.place_configure(
                            relwidth=float(current_info.get('relwidth', 1.0)) * 1.02,
                            relheight=float(current_info.get('relheight', 1.0)) * 1.02
                        )
                    else:
                        # Zurück zur ursprünglichen Größe
                        widget.place_configure(
                            relwidth=float(current_info.get('relwidth', 1.0)) / 1.02,
                            relheight=float(current_info.get('relheight', 1.0)) / 1.02
                        )
        except Exception as e:
            self.logger.error(f"Fehler bei Scale-Animation: {e}")

    def _add_drag_pulse_effect(self, widget):
        """Fügt einen Pulse-Effekt während des Draggings hinzu"""
        try:
            target_info = self.drop_targets.get(widget, {})
            if target_info.get('is_dragging', False):
                # Subtle pulse durch Border-Width-Änderung
                current_width = getattr(widget, 'cget', lambda x: 3)("border_width") if hasattr(widget, 'cget') else 3
                new_width = 4 if current_width == 3 else 3

                if hasattr(widget, 'configure'):
                    widget.configure(border_width=new_width)

                # Wiederhole nach 300ms
                widget.after(300, lambda: self._add_drag_pulse_effect(widget))
        except Exception as e:
            self.logger.error(f"Fehler beim Pulse-Effekt: {e}")

    def _add_enhanced_drag_pulse_effect(self, widget):
        """Erweiterte Pulse-Animation mit besserer Synchronisation"""
        try:
            target_info = self.drop_targets.get(widget, {})
            if target_info.get('is_dragging', False):
                # Erweiterte Pulse-Animation mit Farb- und Border-Änderungen
                current_width = getattr(widget, 'cget', lambda x: 3)("border_width") if hasattr(widget, 'cget') else 3

                # Alterniere zwischen 3 und 4 Pixel Border-Width für subtilen Pulse
                new_width = 4 if current_width == 3 else 3

                # Zusätzlich leichte Farbänderung für mehr Dynamik
                pulse_colors = ["#E8F4FD", "#F0F8FF"]
                current_color = widget.cget('fg_color') if hasattr(widget, 'cget') else "#E8F4FD"
                new_color = pulse_colors[1] if current_color == pulse_colors[0] else pulse_colors[0]

                if hasattr(widget, 'configure'):
                    widget.configure(border_width=new_width, fg_color=new_color)

                # Synchronisierte Wiederholung alle 400ms für sanfteren Effekt
                widget.after(400, lambda: self._add_enhanced_drag_pulse_effect(widget))
        except Exception as e:
            self.logger.error(f"Fehler beim erweiterten Pulse-Effekt: {e}")

    def _show_drop_success_feedback(self, widget):
        """Zeigt visuelles Success-Feedback"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(
                    fg_color="#E8F5E8",  # Helles Grün
                    border_color="#4CAF50",  # Grün
                    border_width=3
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Success-Feedback: {e}")

    def _show_drop_error_feedback(self, widget):
        """Zeigt visuelles Error-Feedback"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(
                    fg_color="#FFEBEE",  # Helles Rot
                    border_color="#F44336",  # Rot
                    border_width=3
                )

            # Nach 2 Sekunden zurück zum ursprünglichen Stil
            widget.after(2000, lambda: self._restore_original_style(widget))
        except Exception as e:
            self.logger.error(f"Fehler beim Error-Feedback: {e}")

    def _show_no_valid_files_feedback(self, widget):
        """Zeigt Feedback für keine gültigen Dateien"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(
                    fg_color="#FFF3E0",  # Helles Orange
                    border_color="#FF9800",  # Orange
                    border_width=3
                )

            # Nach 2 Sekunden zurück zum ursprünglichen Stil
            widget.after(2000, lambda: self._restore_original_style(widget))
        except Exception as e:
            self.logger.error(f"Fehler beim No-Valid-Files-Feedback: {e}")

    def _restore_original_style(self, widget):
        """Stellt den ursprünglichen Stil wieder her"""
        try:
            target_info = self.drop_targets.get(widget, {})
            original_style = target_info.get('original_style', {})

            if hasattr(widget, 'configure'):
                widget.configure(
                    fg_color=original_style.get('fg_color', "#F0F0F0"),
                    border_color=original_style.get('border_color', "#CCCCCC"),
                    border_width=original_style.get('border_width', 2)
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Wiederherstellen des ursprünglichen Stils: {e}")

    def _process_files_with_progress(self, file_paths, target_info, progress_callback):
        """Verarbeitet Dateien mit Fortschrittsanzeige"""
        total_files = len(file_paths)

        def process_next_file(index):
            if index >= total_files:
                # Alle Dateien verarbeitet - Callback aufrufen
                callback = target_info.get('callback')
                if callback:
                    callback(file_paths)
                return

            current_file = file_paths[index]
            filename = os.path.basename(current_file)

            # Progress-Update
            progress_callback(index + 1, total_files, filename)

            # Nächste Datei nach kurzer Verzögerung
            widget = next(iter([w for w, info in self.drop_targets.items() if info == target_info]))
            widget.after(100, lambda: process_next_file(index + 1))

        # Starte Verarbeitung
        process_next_file(0)

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
                self.logger.info(f"Enhanced Drop-Target entfernt: {widget}")
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Enhanced Drop-Targets: {e}")

    def get_supported_file_types(self) -> List[str]:
        """
        Gibt eine Liste der unterstützten Dateierweiterungen zurück
        """
        return [
            '.pdf', '.doc', '.docx', '.txt', '.rtf',
            '.xlsx', '.xls', '.pptx', '.ppt',
            '.odt', '.ods', '.odp', '.png', '.jpg', '.jpeg',
            '.gif', '.bmp', '.tiff'
        ]

    # Legacy Compatibility - Old DragDropManager methods
    def make_drop_target(self, widget, callback: Callable[[List[str]], None],
                        file_types: Optional[List[str]] = None):
        """Legacy compatibility method - delegates to enhanced version"""
        return self.make_enhanced_drop_target(widget, callback, file_types)

    def _setup_fallback_drag_drop(self, widget, callback: Callable[[List[str]], None],
                                 file_types: Optional[List[str]] = None):
        """
        Fallback Drag & Drop Setup für Widgets, die tkinterdnd2 nicht direkt unterstützen
        """
        try:
            # Einfaches Drag & Drop mit tkinter Events
            def on_drop_fallback(event):
                # Simuliere ein Drop-Event
                if hasattr(event, 'data'):
                    file_paths = self._parse_drop_data(event.data)
                else:
                    # Fallback für Clipboard oder andere Quellen
                    try:
                        pass

                        clipboard_data = widget.clipboard_get()
                        if os.path.exists(clipboard_data):
                            file_paths = [clipboard_data]
                        else:
                            file_paths = []
                    except:
                        file_paths = []

                if file_paths:
                    callback(file_paths)

            # Binde Standard-Events
            widget.bind('<Button-1>', lambda e: None)  # Placeholder für Click
            widget.bind('<B1-Motion>', lambda e: None)  # Placeholder für Drag

            # Speichere Fallback-Info
            self.drop_targets[widget] = {
                'callback': callback,
                'file_types': file_types or [],
                'is_fallback': True
            }

            self.logger.info(f"Fallback Drop-Target Setup für: {widget}")

        except Exception as e:
            self.logger.error(f"Fehler beim Fallback Drop-Target Setup: {e}")

# Globale Instanz für einfache Verwendung
drag_drop_manager = EnhancedDragDropManager()