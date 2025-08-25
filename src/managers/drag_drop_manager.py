"""
Enhanced Drag & Drop Manager für die Checker App
Implementiert moderne Drag & Drop Funktionalität mit visuellen Effekten und Animationen
"""

from typing import List, Callable, Optional
import logging
import os

# Optionaler Import: tkinterdnd2 kann fehlen
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # optional
    _TKDND2_OK = True
except Exception:
    TkinterDnD = None  # type: ignore
    DND_FILES = None   # type: ignore
    _TKDND2_OK = False
try:
    import tkinterdnd_integration  # type: ignore
except Exception:  # Fallback-Stubs, falls Integration nicht verfügbar ist
    class _TkDnDIntegrationStub:
        @staticmethod
        def is_tkinterdnd_available() -> bool:
            return False

        @staticmethod
        def make_drop_target(widget, callback, file_types=None):
            return False

        @staticmethod
        def remove_drop_target(widget):
            return None

    tkinterdnd_integration = _TkDnDIntegrationStub()  # type: ignore

class EnhancedDragDropManager:
    """
    Enhanced Manager für Drag & Drop Funktionalität mit modernen visuellen Effekten
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drop_targets = {}
        # Kombiniere optionales Paket + Integrationstest
        self.tkinterdnd_available = _TKDND2_OK and bool(
            getattr(tkinterdnd_integration, "is_tkinterdnd_available", lambda: False)()
        )

    def make_enhanced_drop_target(self, widget, callback: Callable[[List[str]], None],
                                file_types: Optional[List[str]] = None,
                                progress_callback: Optional[Callable[[int, int, str], None]] = None,
                                allow_directories: bool = True):
        """
        Macht ein Widget zu einem erweiterten Drag & Drop Ziel mit visuellen Effekten

        Args:
            widget: Das tkinter/customtkinter Widget
            callback: Funktion, die aufgerufen wird wenn Dateien dropped werden
            file_types: Liste erlaubter Dateierweiterungen (z.B. ['.pdf', '.docx'])
            progress_callback: Optional callback für Fortschrittsanzeige
            allow_directories: Ob Ordner-Drops erlaubt sind (True) oder verworfen werden (False)
        """
        try:
            if not self.tkinterdnd_available:
                self.logger.warning("TkinterDnD2 ist nicht verfügbar, verwende Fallback")
                return self._setup_fallback_drag_drop(widget, callback, file_types)

            # Helper für sicheres cget (erlaubt Tuple etc.)
            def _safe_cget(name: str, default):
                try:
                    if not hasattr(widget, 'cget'):
                        return default
                    val = widget.cget(name)
                    # CTk kann Tupel für Farben liefern (light, dark)
                    if isinstance(val, (tuple, list)) and val:
                        return val[0]
                    return val if val is not None else default
                except Exception:
                    return default

            # Speichere original styling (sanfte Defaults)
            original_fg_color = _safe_cget('fg_color', "#F0F0F0")
            original_border_color = _safe_cget('border_color', "#E5E7EB")
            original_border_width = _safe_cget('border_width', 1)

            # Dateitypen einmal normalisieren (lower + führender Punkt)
            norm_types = set()
            for ft in (file_types or []):
                if not ft:
                    continue
                s = str(ft).strip().lower()
                if not s:
                    continue
                if not s.startswith('.'):
                    s = '.' + s
                norm_types.add(s)

            # Speichere erweiterte Informationen
            self.drop_targets[widget] = {
                'callback': callback,
                'progress_callback': progress_callback,
                'file_types': file_types or [],
                'file_types_normalized': norm_types,
                'original_style': {
                    'fg_color': original_fg_color,
                    'border_color': original_border_color,
                    'border_width': original_border_width
                },
                'is_dragging': False,
                'allow_directories': bool(allow_directories),
                '_after_ids': []  # IDs geplanter after-Callbacks für sauberes Aufräumen
            }

            # Verwende die neue Integration für das Setup
            norm_list = sorted(self.drop_targets[widget]['file_types_normalized'])
            result = tkinterdnd_integration.make_drop_target(
                widget,
                lambda files: self._handle_dropped_files(widget, files),
                norm_list
            )

            if result:
                self.logger.info(f"Enhanced Drop-Target registriert: {widget}")
                # Drag-Lifecycle Events (falls verfügbar) binden
                try:
                    if getattr(widget, 'dnd_bind', None):
                        widget.dnd_bind('<<DropEnter>>', lambda e: self._on_drop_enter(widget))
                        widget.dnd_bind('<<DropLeave>>', lambda e: self._on_drop_leave(widget))
                        # Optional: Direkter Drop-Event-Handler (String-Daten parsen)
                        widget.dnd_bind('<<Drop>>', lambda e: self._handle_drop_event(widget, getattr(e, 'data', '')))
                except Exception as _e:
                    self.logger.debug(f"Drop-Lifecycle-Bindings nicht verfügbar: {_e}")
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

            # Tolerant: Strings (tkdnd) → Liste parsen
            allow_dirs = target_info.get('allow_directories', True)
            if isinstance(file_paths, str):
                file_paths = self._parse_drop_data(file_paths, allow_directories=allow_dirs)
            elif isinstance(file_paths, (tuple, list)):
                # Liste kann einen zusammengefassten String enthalten
                if len(file_paths) == 1 and isinstance(file_paths[0], str) and ('{' in file_paths[0] or ' ' in file_paths[0] or '\n' in file_paths[0]):
                    file_paths = self._parse_drop_data(file_paths[0], allow_directories=allow_dirs)
                else:
                    # Normiere alle Einträge
                    file_paths = [str(p) for p in file_paths]

            if not file_paths:
                self.logger.warning("Keine gültigen Dateipfade gefunden")
                self._show_no_valid_files_feedback(widget)
                return

            # Filter anwenden falls vorhanden
            norm_types = target_info.get('file_types_normalized', set())
            if norm_types:
                filtered_paths = []
                for path in file_paths:
                    try:
                        if os.path.isdir(path):
                            # Ordner: nach allow_directories filtern, Typen gelten nur für Dateien
                            if allow_dirs:
                                filtered_paths.append(path)
                            else:
                                self.logger.info(f"Ordner nicht erlaubt: {path}")
                            continue
                        # Datei: nach Erweiterung prüfen
                        _, ext = os.path.splitext(path)
                        if ext.lower() in norm_types:
                            filtered_paths.append(path)
                        else:
                            self.logger.info(f"Datei übersprungen (falscher Typ): {path}")
                    except Exception:
                        pass
                file_paths = filtered_paths

            if not file_paths:
                self.logger.warning("Keine Dateien nach Filterung übrig")
                self._show_no_valid_files_feedback(widget)
                return

            # Jetzt erst visuelles Success-Feedback, da valide Dateien vorliegen
            self._show_drop_success_feedback(widget)
            if hasattr(widget, 'after'):
                widget.after(500, lambda: self._restore_original_style(widget))

            # Progress Callback für mehrere Dateien
            progress_callback = target_info.get('progress_callback')
            if progress_callback and len(file_paths) > 1:
                self._process_files_with_progress(widget, file_paths, target_info, progress_callback)
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
            if hasattr(widget, 'after'):
                aid = widget.after(150, lambda: self._cycle_border_colors(widget, colors, index + 1))
                try:
                    target_info.setdefault('_after_ids', []).append(aid)
                except Exception:
                    pass
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
            if hasattr(widget, 'after'):
                aid = widget.after(200, lambda: self._cycle_enhanced_border_colors(widget, colors, index + 1))
                try:
                    target_info.setdefault('_after_ids', []).append(aid)
                except Exception:
                    pass
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
                if hasattr(widget, 'after'):
                    aid = widget.after(300, lambda: self._add_drag_pulse_effect(widget))
                    try:
                        target_info.setdefault('_after_ids', []).append(aid)
                    except Exception:
                        pass
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
                if hasattr(widget, 'after'):
                    aid = widget.after(400, lambda: self._add_enhanced_drag_pulse_effect(widget))
                    try:
                        target_info.setdefault('_after_ids', []).append(aid)
                    except Exception:
                        pass
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

    def _process_files_with_progress(self, widget, file_paths, target_info, progress_callback):
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
            if hasattr(widget, 'after'):
                widget.after(100, lambda: process_next_file(index + 1))
            else:
                # Fallback: direkte Rekursion (ohne UI-Tick)
                process_next_file(index + 1)

        # Starte Verarbeitung
        process_next_file(0)

    def _parse_drop_data(self, data: str, allow_directories: bool = True) -> List[str]:
        """
        Parst die Drop-Daten und extrahiert Dateipfade

        Args:
            data: Rohe Drop-Daten vom Event

        Returns:
            Liste von Dateipfaden
        """
        try:
            # tkinterdnd2 gibt Dateipfade in geschweiften Klammern zurück
            # Format: "{Pfad1} {Pfad2}" oder einzelne Pfade ohne Klammern, teils mit Zeilenumbrüchen

            file_paths = []

            # Entferne äußere Klammern falls vorhanden
            data = (data or '').replace('\r', ' ').replace('\n', ' ').strip()
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

            # Filtere existierende Pfade (Dateien + optional Ordner)
            valid_paths = []
            for path in file_paths:
                try:
                    if os.path.isfile(path):
                        valid_paths.append(path)
                    elif os.path.isdir(path):
                        if allow_directories:
                            valid_paths.append(path)
                        else:
                            self.logger.info(f"Ordner ignoriert: {path}")
                    else:
                        self.logger.warning(f"Pfad existiert nicht: {path}")
                except Exception:
                    pass

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
                # Drag-Lifecycle stoppen
                info = self.drop_targets.get(widget, {})
                info['is_dragging'] = False
                # Geplante after-Callbacks sauber abbrechen
                try:
                    for aid in info.get('_after_ids', []) or []:
                        try:
                            if hasattr(widget, 'after_cancel'):
                                widget.after_cancel(aid)
                        except Exception:
                            pass
                    info['_after_ids'] = []
                except Exception:
                    pass
                # Versuche zuerst die native Methode
                try:
                    if hasattr(widget, 'drop_target_unregister'):
                        widget.drop_target_unregister()
                    elif hasattr(tkinterdnd_integration, 'remove_drop_target'):
                        tkinterdnd_integration.remove_drop_target(widget)
                except Exception:
                    # Ignorieren, wir räumen unten trotzdem auf
                    pass
                # Unbind DnD-Events falls verfügbar
                try:
                    if getattr(widget, 'dnd_unbind', None):
                        widget.dnd_unbind('<<DropEnter>>')
                        widget.dnd_unbind('<<DropLeave>>')
                        widget.dnd_unbind('<<Drop>>')
                except Exception:
                    pass
                del self.drop_targets[widget]
                self.logger.info(f"Enhanced Drop-Target entfernt: {widget}")
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Enhanced Drop-Targets: {e}")

    # ---- Drag Lifecycle Helpers ----
    def _on_drop_enter(self, widget):
        try:
            info = self.drop_targets.get(widget, {})
            info['is_dragging'] = True
            # Sanfter Glow + Pulse starten
            self._add_enhanced_drop_glow_animation(widget)
            self._add_enhanced_drag_pulse_effect(widget)
        except Exception as e:
            self.logger.debug(f"DropEnter-Handler Fehler: {e}")

    def _on_drop_leave(self, widget):
        try:
            info = self.drop_targets.get(widget, {})
            info['is_dragging'] = False
            # Stil nach kurzer Zeit zurücksetzen
            if hasattr(widget, 'after'):
                widget.after(200, lambda: self._restore_original_style(widget))
        except Exception as e:
            self.logger.debug(f"DropLeave-Handler Fehler: {e}")

    def _handle_drop_event(self, widget, data: str):
        """Direkter Handler für <<Drop>> mit Rohdaten-String."""
        try:
            paths = self._parse_drop_data(data, allow_directories=self.drop_targets.get(widget, {}).get('allow_directories', True))
            self._handle_dropped_files(widget, paths)
        except Exception as e:
            self.logger.error(f"Fehler im <<Drop>> Handler: {e}")

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
                file_paths: List[str] = []
                if hasattr(event, 'data'):
                    file_paths = self._parse_drop_data(getattr(event, 'data', ''))
                else:
                    # Fallback für Clipboard oder andere Quellen
                    try:
                        clipboard_data = widget.clipboard_get()
                        if os.path.exists(clipboard_data):
                            file_paths = [clipboard_data]
                    except Exception:
                        pass

                if file_paths:
                    callback(file_paths)

            # Binde Standard-Events
            widget.bind('<Button-1>', lambda e: None)  # Placeholder für Click
            widget.bind('<B1-Motion>', lambda e: None)  # Placeholder für Drag
            # Optional: Tastenkürzel für Clipboard-Test
            try:
                widget.bind('<Control-v>', lambda e: callback([widget.clipboard_get()]) if os.path.exists(widget.clipboard_get()) else None)
            except Exception:
                pass

            # Speichere Fallback-Info
            self.drop_targets[widget] = {
                'callback': callback,
                'file_types': file_types or [],
                'is_fallback': True,
                '_after_ids': [],
                'is_dragging': False
            }

            self.logger.info(f"Fallback Drop-Target Setup für: {widget}")
            self.logger.info("Fallback aktiv: echtes OS-Drag&Drop nicht verfügbar; nutze Platzhalter/Clipboard.")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Fallback Drop-Target Setup: {e}")
            return False

# Globale Instanz für einfache Verwendung
drag_drop_manager = EnhancedDragDropManager()