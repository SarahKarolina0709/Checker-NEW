# -*- coding: utf-8 -*-
"""
UploadSection

Leichtgewichtiger Wrapper um die bestehende Upload-Karte aufzubauen.
Er nutzt den Host (WelcomeScreen) und dessen bestehende Methoden/Design-System.
Hinweis: UI-Texte bleiben icon- und emoji-frei (No-Icons-Policy).
"""
from __future__ import annotations
from typing import Any, Optional, Tuple, List, Callable

try:
    import customtkinter as ctk  # noqa: F401
except Exception:
    ctk = None

# Optional: zentrale Buttons via ModernUIComponents, falls Host kein _button_style liefert
try:
    from modern_ui_components import ModernUIComponents
except Exception:
    ModernUIComponents = None  # Fallback


class UploadSection:
    """Kapselt die Erstellung der Upload-Section."""

    def __init__(self, host: Any, parent: Any, column: int) -> None:
        self.host = host
        self.parent = parent
        self.column = column
        self.container = None
        self.content = None
        self.file_list_frame = None  # Scrollbare Liste für Einzeldateien
        self.build()

    # ---------- kleine Helper mit sicheren Fallbacks ----------
    def _ensure_doc_extension(self) -> None:
        """Sorgt dafür, dass '.doc' als erlaubte Extension vorhanden ist (Dialog/Validierung).
        Greift nur, falls der Host entsprechende Listen hat.
        """
        try:
            for attr in ("supported_extensions", "allowed_extensions", "extensions"):
                exts = getattr(self.host, attr, None)
                if isinstance(exts, (list, set, tuple)):
                    # Normalisiere und erweitere
                    normalized = set(str(e).lower() for e in exts)
                    if ".doc" not in normalized and "doc" not in normalized:
                        normalized.add(".doc")
                    # Schreibe zurück als Liste (Host erwartet meist Liste)
                    try:
                        setattr(self.host, attr, list(normalized))
                    except Exception:
                        pass
        except Exception:
            pass
    def _get_color(self, name: str, fallback: Optional[str] = None) -> str:
        if hasattr(self.host, "get_color"):
            try:
                return self.host.get_color(name)
            except Exception:
                pass
        return fallback or "#000000"

    def _get_spacing(self, name: str, default: int = 16) -> int:
        if hasattr(self.host, "get_spacing"):
            try:
                return int(self.host.get_spacing(name))
            except Exception:
                pass
        return default

    def _get_typography(self, key: str) -> Tuple[str, int, str]:
        # Mappe Legacy-Namen auf DS-Keys
        remap = {
            "subheading": "heading_md",
            "body": "body_md",
            "body_bold": "button_md",
            "label": "body_md",
            "small": "caption",
        }
        mapped = remap.get(key, key)
        if hasattr(self.host, "get_typography"):
            try:
                return self.host.get_typography(mapped)
            except Exception:
                pass
        return ("Segoe UI", 12, "normal")

    def _get_component_value(self, dotted: str, default: Optional[int] = None):
        if hasattr(self.host, "get_component_value"):
            try:
                return self.host.get_component_value(dotted)
            except Exception:
                pass
        return default

    def _toast(self, message: str, level: str = "info") -> None:
        """Zentralisierte Toast-Ausgabe mit sicheren Fallbacks."""
        try:
            tm = getattr(self.host, 'toast_manager', None)
            if tm:
                if level == "success" and hasattr(tm, 'show_success'):
                    tm.show_success(message); return
                if level == "warning" and hasattr(tm, 'show_warning'):
                    tm.show_warning(message); return
                if level == "error" and hasattr(tm, 'show_error'):
                    tm.show_error(message); return
                if hasattr(tm, 'show_info'):
                    tm.show_info(message); return
            if hasattr(self.host, '_show_enhanced_toast'):
                self.host._show_enhanced_toast(message, level); return
            if hasattr(self.host, 'show_toast'):
                self.host.show_toast(message, level)
        except Exception:
            pass

    def _parse_tkdnd_paths(self, data: str) -> List[str]:
        """Robustes Parsen von TKDND-Pfadlisten, unterstützt {…} mit Leerzeichen.
        Liefert eine Liste normalisierter Pfade als Strings (ohne geschweifte Klammern).
        """
        if not data:
            return []
        items: List[str] = []
        buf: List[str] = []
        in_brace = False
        for ch in data:
            if ch == '{':
                in_brace = True
                if buf:
                    # flush vorherigen Token
                    token = ''.join(buf).strip()
                    if token:
                        items.append(token)
                    buf = []
                continue
            if ch == '}':
                in_brace = False
                token = ''.join(buf).strip()
                if token:
                    items.append(token)
                buf = []
                continue
            if not in_brace and ch.isspace():
                token = ''.join(buf).strip()
                if token:
                    items.append(token)
                buf = []
            else:
                buf.append(ch)
        # letztes Token
        if buf:
            token = ''.join(buf).strip()
            if token:
                items.append(token)

        # Windows-sichere Normalisierung (Belasse Backslashes, entferne restliche Klammern)
        cleaned: List[str] = []
        for it in items:
            cleaned.append(it.strip('{}').strip())
        return cleaned

    def _ingest_valid_files(self, valid_files: List[str]) -> None:
        """Übernimmt valide Dateien in Host-Listen und aktualisiert die UI konsistent."""
        if not valid_files:
            return
        try:
            if not hasattr(self.host, 'uploaded_files') or not isinstance(self.host.uploaded_files, list):
                self.host.uploaded_files = []
            self.host.uploaded_files.extend(valid_files)
            self.host.selected_files = list(self.host.uploaded_files)
        except Exception:
            pass
        # Host Zusammenfassung aktualisieren (falls vorhanden)
        try:
            if hasattr(self.host, '_update_file_list_display'):
                self.host._update_file_list_display({'valid_files': valid_files, 'invalid_files': []})
        except Exception:
            pass
        # Eigene Liste neu aufbauen
        self._refresh_file_list_ui()

    def _set_upload_enabled(self, enabled: bool) -> None:
        """Aktualisiert den Upload-Button-State und setzt eine klare Optik gemäß Design-Tokens."""
        try:
            btn = getattr(self.host, 'upload_btn', None)
            if not btn:
                return
            btn.configure(state=("normal" if enabled else "disabled"))
            if enabled:
                # Primärer, gefüllter Stil
                btn.configure(
                    fg_color=self._get_color('primary', '#1F4E79'),
                    hover_color=self._get_color('primary_hover', '#1A3F65'),
                    text_color=self._get_color('white', '#FFFFFF'),
                    border_width=0,
                    border_color=self._get_color('primary', '#1F4E79'),
                )
            else:
                # Deutlich sichtbarer Disabled-Outline-Stil
                btn.configure(
                    fg_color=self._get_color('white', '#FFFFFF'),
                    text_color=self._get_color('primary', '#1F4E79'),
                    hover_color=self._get_color('surface_hover', '#F3F4F6'),
                    border_width=1,
                    border_color=self._get_color('surface_border', '#E5E7EB'),
                )
        except Exception:
            pass

    def _make_button(self, parent: Any, text: str, command,
                     style: str = "primary", size: str = "md",
                     state: str = "normal", min_width: Optional[int] = None):
        """Einheitliche Button-Erzeugung mit Host-/DS-Fallbacks."""
        if ctk is None:
            return None

        btn = None
        if hasattr(self.host, "_button_style"):
            try:
                cfg = self.host._button_style(style, size, "solid")
                btn = ctk.CTkButton(parent, text=text, command=command, **cfg)
            except Exception:
                btn = None

        if btn is None and ModernUIComponents is not None and hasattr(self.host, "design_system"):
            try:
                btn = ModernUIComponents.create_professional_button(
                    parent, text, command, self.host.design_system, style=style, size=size
                )
            except Exception:
                btn = None

        if btn is None:
            # Minimal-Fallback (farblos)
            btn = ctk.CTkButton(parent, text=text, command=command)

        # Standard-Höhe/Radius aus DS
        try:
            h = int(self._get_component_value('heights.button_md', 38))
            r = int(self._get_component_value('borders.radius_md', 8))
            btn.configure(height=h, corner_radius=r)
        except Exception:
            pass

        # State & Mindestbreite
        try:
            if state:
                btn.configure(state=state)
            if min_width:
                btn.configure(width=min_width)
        except Exception:
            pass
        return btn

    # ---------- Build ----------
    def build(self) -> None:
        try:
            # Kompatibilität: .doc erlauben, falls Host-Listen existieren
            self._ensure_doc_extension()
            self.container, self.content = self._setup_container(self.parent, self.column)
            self._build_header(self.content)
            self._build_drag_drop_area(self.content)
            self._build_progress_section(self.content)
            self._build_file_list_section(self.content)
            self._build_buttons_section(self.content)
        except Exception:
            # Fallback: bei Fehlern gesamtes Card-Building dem Host überlassen
            try:
                if hasattr(self.host, "_create_simple_upload_card"):
                    self.host._create_simple_upload_card(self.parent, self.column)
                else:
                    print("UploadSection: Konnte nicht gebaut werden und Host hat keine _create_simple_upload_card")
            except Exception:
                pass

    def _setup_container(self, parent: Any, column: int):
        """Erzeugt den Card-Container analog zum Host-Design (Design-System)."""
        if ctk is None:
            return None, None

        card = ctk.CTkFrame(
            parent,
            fg_color=self._get_color('surface', '#FFFFFF'),
            corner_radius=self._get_component_value('borders.radius_md', 8),
            border_width=1,
            border_color=self._get_color('surface_border', '#E5E7EB'),
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=self._get_spacing('sm', 8), pady=0)

        pad = self._get_spacing('md', 16)  # statt 'card_padding'
        # Scrollbarer Inhalt, damit die Button-Leiste nie abgeschnitten wird
        content = ctk.CTkScrollableFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=pad, pady=pad)
        return card, content

    # === Inhaltliche Abschnitte ===
    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Upload",
            font=ctk.CTkFont(*self._get_typography("subheading")),  # → heading_md
            text_color=self._get_color('primary', '#1F4E79'),
        )
        title.pack(pady=(0, 12), fill="x")
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self._get_color('border', '#E5E7EB'),
            corner_radius=self._get_component_value('borders.radius_hairline', 1),
        )
        separator.pack(fill="x", pady=(0, 20))

    def _build_drag_drop_area(self, content: Any) -> None:
        if ctk is None:
            return

        # Grundzustand aus Upload-Tokens
        upload_area = ctk.CTkFrame(
            content,
            fg_color=self._get_color('upload_bg', '#FAFBFC'),
            border_width=1,
            border_color=self._get_color('upload_border', '#CBD5E1'),
            corner_radius=self._get_component_value('borders.radius_md', 8),
            height=140,
        )
        upload_area.pack(fill="x", pady=(0, self._get_spacing('md', 16)))
        upload_area.pack_propagate(False)

        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(expand=True, fill="both")

        upload_icon = ctk.CTkLabel(
            upload_content,
            text="Upload",
            font=ctk.CTkFont(*self._get_typography("subheading")),  # → heading_md
            text_color=self._get_color('upload_icon', '#6B7280'),
        )
        upload_icon.pack(pady=(self._get_spacing('lg', 24), self._get_spacing('sm', 8)))

        upload_text = ctk.CTkLabel(
            upload_content,
            text="Dateien hierher ziehen oder klicken zum Durchsuchen",
            font=ctk.CTkFont(*self._get_typography("body")),  # → body_md
            text_color=self._get_color('upload_text', '#374151'),
        )
        upload_text.pack(pady=(0, self._get_spacing('xs', 4)))

        format_text = ctk.CTkLabel(
            upload_content,
            text="PDF • DOCX • TXT • XLSX",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('upload_hint', '#9CA3AF'),
        )
        format_text.pack(pady=(0, self._get_spacing('md', 16)))

        # Hover/Drag-States konsequent mit Upload-Tokens
        def _to_base():
            upload_area.configure(
                border_color=self._get_color('upload_border', '#CBD5E1'),
                fg_color=self._get_color('upload_bg', '#FAFBFC'),
            )
            upload_icon.configure(text_color=self._get_color('upload_icon', '#6B7280'))
            upload_text.configure(
                text="Dateien hierher ziehen oder klicken zum Durchsuchen",
                text_color=self._get_color('upload_text', '#374151'),
            )

        def _to_hover():
            upload_area.configure(
                border_color=self._get_color('upload_hover_border', '#1F4E79'),
                fg_color=self._get_color('upload_hover_bg', '#F0F7FF'),
            )
            upload_icon.configure(text_color=self._get_color('upload_icon_hover', '#1F4E79'))
            upload_text.configure(text_color=self._get_color('upload_text_hover', '#1F4E79'))

        def _to_drag():
            upload_area.configure(
                border_color=self._get_color('success', '#2E8B57'),
                fg_color=self._get_color('success_light', '#ECFDF5'),
            )
            upload_text.configure(text="Dateien hier ablegen zum Upload")

        def on_upload_enter(event): _to_hover()
        def on_upload_leave(event): _to_base()
        def on_upload_click(event): 
            self.host._browse_files()
            # Nach Dateiauswahl UI aktualisieren
            try: self._refresh_file_list_ui()
            except Exception: pass

        def on_drag_enter(event): _to_drag()
        def on_drag_leave(event): _to_base()
        def on_drag_over(event): return 'copy'

        def on_file_drop(event):
            try:
                import os
                if hasattr(event, 'data'):
                    raw_paths = self._parse_tkdnd_paths(event.data)
                    dropped_files = [p for p in raw_paths if os.path.isfile(p)]
                    if dropped_files:
                        validation_result = self.host._validate_selected_files(dropped_files)
                        valid = list(validation_result.get('valid_files') or [])
                        if valid:
                            self._ingest_valid_files(valid)
                            self._toast(f"{len(valid)} Datei(en) per Drag & Drop hinzugefügt", "success")
                        else:
                            self._toast("Keine gültigen Dateien in Drag & Drop gefunden", "warning")
                    else:
                        self._toast("Keine gültigen Dateien in Drag & Drop gefunden", "warning")
                _to_base()
            except Exception as e:
                print(f"Drag & Drop error: {e}")
                self._toast("Fehler beim Drag & Drop", "error")

        # Host-Referenz setzen
        self.host.upload_area_widget = upload_area

        for widget in [upload_area, upload_content, upload_icon, upload_text, format_text]:
            widget.bind("<Button-1>", on_upload_click)
            widget.bind("<Enter>", on_upload_enter)
            widget.bind("<Leave>", on_upload_leave)
            widget.configure(cursor="hand2")
            if getattr(self.host, 'drag_drop_enabled', False):
                widget.bind("<<DragEnter>>", on_drag_enter)
                widget.bind("<<DragLeave>>", on_drag_leave)
                widget.bind("<<DragOver>>", on_drag_over)
                widget.bind("<<Drop>>", on_file_drop)

        # Optional: EnhancedDragDropManager verwenden, falls verfügbar
        try:
            if getattr(self.host, 'drag_drop_enabled', False):
                try:
                    from src.managers.drag_drop_manager import drag_drop_manager  # type: ignore
                except Exception:
                    drag_drop_manager = None  # type: ignore
                if drag_drop_manager and hasattr(drag_drop_manager, 'make_enhanced_drop_target'):
                    # Ermittele erlaubte Extensions falls der Host welche definiert
                    file_types = None
                    for attr in ("supported_extensions", "allowed_extensions", "extensions"):
                        exts = getattr(self.host, attr, None)
                        if isinstance(exts, (list, tuple, set)) and exts:
                            file_types = list(exts)
                            break

                    def _on_drop_cb(paths: List[str]):
                        if not paths:
                            self._toast("Keine gültigen Dateien in Drag & Drop gefunden", "warning")
                            return
                        validation_result = self.host._validate_selected_files(paths)
                        valid = list(validation_result.get('valid_files') or [])
                        if valid:
                            self._ingest_valid_files(valid)
                            self._toast(f"{len(valid)} Datei(en) per Drag & Drop hinzugefügt", "success")
                        else:
                            self._toast("Keine gültigen Dateien in Drag & Drop gefunden", "warning")

                    drag_drop_manager.make_enhanced_drop_target(upload_area, _on_drop_cb, file_types)
        except Exception:
            pass

        # Shortcut: Ctrl+O innerhalb der Upload-Card öffnet Dateiauswahl
        try:
            upload_area.bind_all("<Control-o>", lambda e: on_upload_click(e))
        except Exception:
            pass

    def _build_progress_section(self, content: Any) -> None:
        if ctk is None:
            return
        progress_frame = ctk.CTkFrame(
            content,
            fg_color=self._get_color('background', '#F8FAFC'),
            corner_radius=self._get_component_value('borders.radius_lg', 10),
            border_width=1,
            border_color=self._get_color('border', '#E5E7EB'),
        )
        progress_frame.pack(fill="x", pady=(0, 20))

        pad_x = 15
        pad_y = 12
        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill="x", padx=pad_x, pady=pad_y)

        progress_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_header.pack(fill="x", pady=(0, 10))

        left_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        status_row = ctk.CTkFrame(left_header, fg_color="transparent")
        status_row.pack(fill="x")

        self.host.progress_icon = ctk.CTkLabel(
            status_row,
            text="Status:",
            font=ctk.CTkFont(*self._get_typography("label")),  # → body_md
            text_color=self._get_color('success', '#2E8B57'),
        )
        self.host.progress_icon.pack(side="left", padx=(0, 8))

        self.host.progress_label = ctk.CTkLabel(
            status_row,
            text="Bereit für Upload",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('success', '#2E8B57'),
        )
        self.host.progress_label.pack(side="left")

        right_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        right_header.pack(side="right")

        self.host.upload_speed_label = ctk.CTkLabel(
            right_header,
            text="",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.upload_speed_label.pack(side="right", padx=(8, 0))

        self.host.upload_eta_label = ctk.CTkLabel(
            right_header,
            text="",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.upload_eta_label.pack(side="right")

        progress_bar_container = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_bar_container.pack(fill="x", pady=(0, 8))

        self.host.progress_bar = ctk.CTkProgressBar(
            progress_bar_container,
            height=8,
            corner_radius=self._get_component_value('borders.radius_xs', 4),
            progress_color=self._get_color('primary', '#1F4E79'),
            fg_color=self._get_color('border', '#E5E7EB'),
            border_width=0,
        )
        self.host.progress_bar.pack(fill="x")
        self.host.progress_bar.set(0)

        details_row = ctk.CTkFrame(progress_content, fg_color="transparent")
        details_row.pack(fill="x")

        self.host.progress_percentage = ctk.CTkLabel(
            details_row,
            text="0%",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.progress_percentage.pack(side="left")

        self.host.file_progress_label = ctk.CTkLabel(
            details_row,
            text="",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.file_progress_label.pack()

        self.host.transfer_info_label = ctk.CTkLabel(
            details_row,
            text="",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.transfer_info_label.pack(side="right")

        self.host.upload_start_time = None
        self.host.upload_total_bytes = 0
        self.host.upload_transferred_bytes = 0
        # Hygiene/Stats: Robustere Stats-Basis
        try:
            if not hasattr(self.host, 'last_upload'):
                self.host.last_upload = None
        except Exception:
            pass

    def _build_file_list_section(self, content: Any) -> None:
        if ctk is None:
            return
        list_label = ctk.CTkLabel(
            content,
            text="Ausgewählte Dateien:",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        list_label.pack(anchor="w", pady=(0, 8))

        # Zusammenfassungs-Label (bestehende Host-Integration beibehalten)
        self.host.file_list_label = ctk.CTkLabel(
            content,
            text="Keine Dateien ausgewählt",
            font=ctk.CTkFont(*self._get_typography("caption")),
            text_color=self._get_color('text_secondary', '#6B7280'),
        )
        self.host.file_list_label.pack(anchor="w", pady=(0, 8))

        # Scrollbare Liste einzelner Dateien
        self.file_list_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=self._get_color('surface', '#FFFFFF'),
            border_width=1,
            border_color=self._get_color('surface_border', '#E5E7EB'),
            corner_radius=self._get_component_value('borders.radius_md', 8),
            height=140,
        )
        self.file_list_frame.pack(fill="x", pady=(0, 12))

        # Initial füllen
        self._refresh_file_list_ui()

    def _build_buttons_section(self, content: Any) -> None:
        if ctk is None:
            return
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(self._get_spacing('xs', 4), 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=0)

        try:
            min_w = int(self._get_component_value('buttons.min_width_md', 140) or 140)
        except Exception:
            min_w = 140

        # Dateien auswählen
        def _browse_action():
            try:
                self.host._browse_files()
            finally:
                self._refresh_file_list_ui()

        # Deutlich sichtbarer machen: primärer Stil für die Dateiauswahl
        browse_btn = self._make_button(
            button_frame, "Dateien durchsuchen", _browse_action,
            style="primary", size="md", min_width=min_w
        )
        browse_btn.grid(row=0, column=0, sticky="ew", padx=(0, self._get_spacing('xs', 4)))
        self.host.browse_btn = browse_btn
        # Optionaler Tooltip
        try:
            if hasattr(self.host, "_attach_tooltip"):
                self.host._attach_tooltip(browse_btn, "Tipp: Ctrl+O")
        except Exception:
            pass

        # Upload starten (initial disabled)
        self.host.upload_btn = self._make_button(
            button_frame, "Upload starten", self.host._start_upload,
            style="primary", size="md", min_width=min_w
        )
        try:
            self._set_upload_enabled(False)
        except Exception:
            pass
        self.host.upload_btn.grid(row=0, column=1, sticky="ew",
                                  padx=(self._get_spacing('xs', 4), self._get_spacing('xs', 4)))

        # Zurücksetzen
        def _clear_action():
            used = False
            try:
                if hasattr(self.host, "_clear_files"):
                    self.host._clear_files()
                    used = True
            except Exception:
                pass
            if not used:
                try:
                    if hasattr(self.host, "_reset_upload_form"):
                        self.host._reset_upload_form()
                except Exception:
                    pass
            self._refresh_file_list_ui()

        clear_btn = self._make_button(
            button_frame, "Zurücksetzen", _clear_action,
            style="warning", size="md", min_width=min_w
        )
        clear_btn.grid(row=0, column=2, sticky="ew")

        # Accessibility: Enter auf dem Browse-Button auslösen
        try:
            browse_btn.bind("<Return>", lambda e: _browse_action())
        except Exception:
            pass

    # === Interne UI-Helper ===
    def _refresh_file_list_ui(self) -> None:
        """Aktualisiert die scrollbare Dateiliste mit Entfernen-Buttons &
        aktiviert/deaktiviert den Upload-Button abhängig von Dateien."""
        if ctk is None or self.file_list_frame is None:
            return
        try:
            # Kinder löschen
            for child in list(self.file_list_frame.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass

            files = []
            try:
                # UploadManager bevorzugen
                if hasattr(self.host, 'upload_manager') and getattr(self.host.upload_manager, 'uploaded_files', None) is not None:
                    files = list(self.host.upload_manager.uploaded_files)
                elif hasattr(self.host, 'uploaded_files') and isinstance(self.host.uploaded_files, list):
                    files = list(self.host.uploaded_files)
            except Exception:
                files = list(getattr(self.host, 'uploaded_files', []) or [])

            from pathlib import Path as _Path
            for idx, path in enumerate(files):
                row = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
                row.pack(fill="x", pady=(0, 6))

                try:
                    name = _Path(str(path)).name
                except Exception:
                    name = str(path)

                lbl = ctk.CTkLabel(
                    row,
                    text=name,
                    font=ctk.CTkFont(*self._get_typography("caption")),
                    text_color=self._get_color('text_primary', '#374151'),
                )
                lbl.pack(side="left", padx=(6, 6))

                def _remove_specific(p=path):
                    try:
                        # Aus Host-Listen entfernen
                        if hasattr(self.host, 'uploaded_files') and isinstance(self.host.uploaded_files, list):
                            self.host.uploaded_files = [f for f in self.host.uploaded_files if f != p]
                        if hasattr(self.host, 'selected_files') and isinstance(self.host.selected_files, list):
                            self.host.selected_files = [f for f in self.host.selected_files if f != p]
                        # UploadManager syncen
                        if hasattr(self.host, 'upload_manager') and getattr(self.host.upload_manager, 'uploaded_files', None) is not None:
                            self.host.upload_manager.uploaded_files = [f for f in self.host.upload_manager.uploaded_files if f != p]
                        # Host-UI aktualisieren (falls vorhanden)
                        try:
                            self.host._refresh_upload_ui_from_manager()
                        except Exception:
                            pass
                        # Eigene Liste neu aufbauen
                        self._refresh_file_list_ui()
                    except Exception:
                        pass

                rm_btn = self._make_button(
                    row, "Entfernen", _remove_specific, style="secondary", size="sm"
                )
                try:
                    # Deutlicher destruktiver Hover-State gemäß Design-System
                    rm_btn.configure(
                        width=100,
                        height=self._get_component_value('heights.button_sm', 32),
                        fg_color=self._get_color('error', '#DC2626'),
                        hover_color=self._get_color('error_hover', '#EF4444'),
                        text_color=self._get_color('white', '#FFFFFF'),
                    )
                except Exception:
                    pass
                rm_btn.pack(side="right", padx=(6, 6))

            # Falls keine Dateien, Hinweiszeile
            if not files:
                hint = ctk.CTkLabel(
                    self.file_list_frame,
                    text="Keine Dateien in der Liste",
                    font=ctk.CTkFont(*self._get_typography("caption")),
                    text_color=self._get_color('text_secondary', '#6B7280'),
                )
                hint.pack(anchor="w", padx=6)

            # Zusammenfassung aktualisieren
            try:
                if hasattr(self.host, 'file_list_label') and self.host.file_list_label:
                    if files:
                        self.host.file_list_label.configure(text=f"{len(files)} Datei(en) ausgewählt")
                    else:
                        self.host.file_list_label.configure(text="Keine Dateien ausgewählt")
            except Exception:
                pass

            # Upload-Button zustand
            try:
                self._set_upload_enabled(bool(files))
            except Exception:
                pass

        except Exception:
            pass
