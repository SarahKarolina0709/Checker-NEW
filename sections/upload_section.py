# -*- coding: utf-8 -*-
"""
UploadSection

Leichtgewichtiger Wrapper um die bestehende Upload-Karte aufzubauen.
Er nutzt den Host (WelcomeScreen) und dessen bestehende Methoden/Design-System.
Hinweis: UI-Texte bleiben icon- und emoji-frei (No-Icons-Policy).
"""
from __future__ import annotations
from typing import Any

try:
    import customtkinter as ctk  # noqa: F401  # UI-Klassen ggf. für spätere Erweiterungen
except Exception:
    ctk = None  # Fallback, wird aktuell nicht direkt benötigt


class UploadSection:
    """Kapselt die Erstellung der Upload-Section.

    Contract:
    - host: WelcomeScreen-Instanz mit get_color/get_typography/etc.
    - parent: Container-Widget
    - column: Grid-Spalte im parent

    Migrationsschritt: Container/Grundgerüst erstellt diese Klasse; die
    inhaltlichen Abschnitte (Header/Drop/Progress/Filelist/Buttons) werden
    weiterhin über die granularen Host-Methoden aufgebaut.
    """

    def __init__(self, host: Any, parent: Any, column: int) -> None:
        self.host = host
        self.parent = parent
        self.column = column
        self.container = None
        self.content = None
        self.file_list_frame = None  # Scrollbare Liste für Einzeldateien
        self.build()

    def build(self) -> None:
        try:
            # 1) Container/Card in dieser Section aufbauen
            self.container, self.content = self._setup_container(self.parent, self.column)

            # 2) Inhaltliche Abschnitte direkt hier aufbauen (Host-Attribute beibehalten!)
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
            fg_color=self.host.get_color('surface'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=self.host.get_spacing('sm'), pady=0)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True,
                     padx=self.host.get_spacing('card_padding'),
                     pady=self.host.get_spacing('card_padding'))

        return card, content

    # === Inhaltliche Abschnitte (setzen Host-Attribute wie bisher) ===

    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Upload",
            font=ctk.CTkFont(*self.host.get_typography("subheading")),
            text_color=self.host.get_color('primary'),
        )
        title.pack(pady=(0, 12), fill="x")
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.host.get_color('border'),
            corner_radius=self.host.get_component_value('borders.radius_hairline'),
        )
        separator.pack(fill="x", pady=(0, 20))

    def _build_drag_drop_area(self, content: Any) -> None:
        if ctk is None:
            return
        upload_area = ctk.CTkFrame(
            content,
            fg_color=self.host.get_color('upload_bg'),
            border_width=2,
            border_color=self.host.get_color('upload_border'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            height=140,
        )
        upload_area.pack(fill="x", pady=(0, self.host.get_spacing('component_margin')))
        upload_area.pack_propagate(False)

        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(expand=True, fill="both")

        upload_icon = ctk.CTkLabel(
            upload_content,
            text="Upload",
            font=ctk.CTkFont(*self.host.get_typography("subheading")),
            text_color=self.host.get_color('upload_icon'),
        )
        upload_icon.pack(pady=(self.host.get_spacing('lg'), self.host.get_spacing('sm')))

        upload_text = ctk.CTkLabel(
            upload_content,
            text="Dateien hierher ziehen oder klicken zum Durchsuchen",
            font=ctk.CTkFont(*self.host.get_typography("body")),
            text_color=self.host.get_color('upload_text'),
        )
        upload_text.pack(pady=(0, self.host.get_spacing('xs')))

        format_text = ctk.CTkLabel(
            upload_content,
            text="PDF • DOCX • TXT • XLSX",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('upload_hint'),
        )
        format_text.pack(pady=(0, self.host.get_spacing('md')))

        def on_upload_enter(event):
            upload_area.configure(border_color=self.host.get_color('primary'), fg_color=self.host.get_color('primary_light'))
            upload_icon.configure(text_color=self.host.get_color('primary'))
            upload_text.configure(text_color=self.host.get_color('primary'))

        def on_upload_leave(event):
            upload_area.configure(border_color=self.host.get_color('border'), fg_color=self.host.get_color('surface'))
            upload_icon.configure(text_color=self.host.get_color('text_secondary'))
            upload_text.configure(text_color=self.host.get_color('text_primary'))

        def on_upload_click(event):
            self.host._browse_files()

        def on_drag_enter(event):
            upload_area.configure(border_color=self.host.get_color('success'), fg_color=self.host.get_color('success_light'))
            upload_text.configure(text="Dateien hier ablegen zum Upload")

        def on_drag_leave(event):
            upload_area.configure(border_color=self.host.get_color('border'), fg_color=self.host.get_color('surface'))
            upload_text.configure(text="Dateien hierher ziehen oder klicken zum Durchsuchen")

        def on_drag_over(event):
            return 'copy'

        def on_file_drop(event):
            try:
                import os
                if hasattr(event, 'data'):
                    files = event.data.split()
                    dropped_files = [f.strip('{}') for f in files if os.path.isfile(f.strip('{}'))]
                    if dropped_files:
                        validation_result = self.host._validate_selected_files(dropped_files)
                        if validation_result['valid_files']:
                            self.host.uploaded_files.extend(validation_result['valid_files'])
                            self.host.selected_files = list(self.host.uploaded_files)
                            self.host._update_file_list_display(validation_result)
                            # Neu: Scrollbare Dateiliste aktualisieren
                            try:
                                self._refresh_file_list_ui()
                            except Exception:
                                pass
                            self.host._show_enhanced_toast(f"{len(validation_result['valid_files'])} Datei(en) per Drag & Drop hinzugefügt", "success")
                        else:
                            self.host._show_enhanced_toast("Keine gültigen Dateien in Drag & Drop gefunden", "warning")
                on_upload_leave(None)
            except Exception as e:
                print(f"Drag & Drop error: {e}")
                self.host._show_enhanced_toast("Fehler beim Drag & Drop", "error")

        # Host-Referenz setzen, damit andere Logik darauf zugreifen kann
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

    def _build_progress_section(self, content: Any) -> None:
        if ctk is None:
            return
        progress_frame = ctk.CTkFrame(
            content,
            fg_color=self.host.get_color('background'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
            border_width=1,
            border_color=self.host.get_color('border'),
        )
        progress_frame.pack(fill="x", pady=(0, 20))

        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill="x", padx=15, pady=12)

        progress_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_header.pack(fill="x", pady=(0, 10))

        left_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        status_row = ctk.CTkFrame(left_header, fg_color="transparent")
        status_row.pack(fill="x")

        self.host.progress_icon = ctk.CTkLabel(
            status_row,
            text="Status:",
            font=ctk.CTkFont(*self.host.get_typography("label")),
            text_color=self.host.get_color('success'),
        )
        self.host.progress_icon.pack(side="left", padx=(0, 8))

        self.host.progress_label = ctk.CTkLabel(
            status_row,
            text="Bereit für Upload",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('success'),
        )
        self.host.progress_label.pack(side="left")

        right_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        right_header.pack(side="right")

        self.host.upload_speed_label = ctk.CTkLabel(
            right_header,
            text="",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.upload_speed_label.pack(side="right", padx=(8, 0))

        self.host.upload_eta_label = ctk.CTkLabel(
            right_header,
            text="",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.upload_eta_label.pack(side="right")

        progress_bar_container = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_bar_container.pack(fill="x", pady=(0, 8))

        self.host.progress_bar = ctk.CTkProgressBar(
            progress_bar_container,
            height=8,
            corner_radius=self.host.get_component_value('borders.radius_xs'),
            progress_color=self.host.get_color('primary'),
            fg_color=self.host.get_color('border'),
            border_width=0,
        )
        self.host.progress_bar.pack(fill="x")
        self.host.progress_bar.set(0)

        details_row = ctk.CTkFrame(progress_content, fg_color="transparent")
        details_row.pack(fill="x")

        self.host.progress_percentage = ctk.CTkLabel(
            details_row,
            text="0%",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.progress_percentage.pack(side="left")

        self.host.file_progress_label = ctk.CTkLabel(
            details_row,
            text="",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.file_progress_label.pack()

        self.host.transfer_info_label = ctk.CTkLabel(
            details_row,
            text="",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.transfer_info_label.pack(side="right")

        self.host.upload_start_time = None
        self.host.upload_total_bytes = 0
        self.host.upload_transferred_bytes = 0

    def _build_file_list_section(self, content: Any) -> None:
        if ctk is None:
            return
        list_label = ctk.CTkLabel(
            content,
            text="Ausgewählte Dateien:",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_secondary'),
        )
        list_label.pack(anchor="w", pady=(0, 8))

        # Zusammenfassungs-Label (bestehende Host-Integration beibehalten)
        self.host.file_list_label = ctk.CTkLabel(
            content,
            text="Keine Dateien ausgewählt",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_secondary'),
        )
        self.host.file_list_label.pack(anchor="w", pady=(0, 8))

        # Scrollbare Liste einzelner Dateien mit Entfernen-Buttons
        self.file_list_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=self.host.get_color('surface'),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            height=140,
        )
        self.file_list_frame.pack(fill="x", pady=(0, 12))

        # Initial füllen
        self._refresh_file_list_ui()

    def _build_buttons_section(self, content: Any) -> None:
        if ctk is None:
            return
        # Container für Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(self.host.get_spacing('xs'), 0))
        # Drei Spalten: Auswählen | Upload | Zurücksetzen
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=0)

        # Dateien auswählen
        def _browse_action():
            try:
                self.host._browse_files()
            finally:
                # Nach Dateiauswahl UI aktualisieren
                self._refresh_file_list_ui()

        browse_btn = ctk.CTkButton(
            button_frame,
            text="Dateien durchsuchen",
            height=self.host.get_component_value('heights.button_md'),
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('button_secondary'),
            hover_color=self.host.get_color('button_secondary_hover'),
            text_color=self.host.get_color('button_secondary_text'),
            corner_radius=self.host.get_component_value('borders.radius_sm'),
            border_width=0,
            command=_browse_action,
        )
        browse_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.host.get_spacing('button_gap')))
        self.host.browse_btn = browse_btn

        # Upload starten
        self.host.upload_btn = ctk.CTkButton(
            button_frame,
            text="Upload starten",
            height=self.host.get_component_value('heights.button_md'),
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('button_primary'),
            hover_color=self.host.get_color('button_primary_hover'),
            text_color=self.host.get_color('button_primary_text'),
            corner_radius=self.host.get_component_value('borders.radius_sm'),
            border_width=0,
            command=self.host._start_upload,
        )
        self.host.upload_btn.grid(row=0, column=1, sticky="ew", padx=(self.host.get_spacing('button_gap'), self.host.get_spacing('button_gap')))
        try:
            self.host.upload_btn.configure(state="disabled")
        except Exception:
            pass

        # Zurücksetzen der Auswahl
        def _clear_action():
            used = False
            try:
                if hasattr(self.host, "_clear_files"):
                    self.host._clear_files()
                    used = True
            except Exception:
                pass
            # Fallback auf bestehendes Reset der Form
            if not used:
                try:
                    if hasattr(self.host, "_reset_upload_form"):
                        self.host._reset_upload_form()
                except Exception:
                    pass
            # Liste der Einzeldaten aktualisieren
            try:
                self._refresh_file_list_ui()
            except Exception:
                pass

        clear_btn = ctk.CTkButton(
            button_frame,
            text="Zurücksetzen",
            height=self.host.get_component_value('heights.button_md'),
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('warning'),
            hover_color=self.host.get_color('warning_hover'),
            text_color=self.host.get_color('white'),
            corner_radius=self.host.get_component_value('borders.radius_sm'),
            border_width=0,
            command=_clear_action,
        )
        clear_btn.grid(row=0, column=2, sticky="ew")

    # === Interne UI-Helper ===
    def _refresh_file_list_ui(self) -> None:
        """Aktualisiert die scrollbare Dateiliste mit Entfernen-Buttons."""
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
                # Falls ein UploadManager existiert, verwende dessen Liste als Quelle
                if hasattr(self.host, 'upload_manager') and getattr(self.host.upload_manager, 'uploaded_files', None) is not None:
                    files = list(self.host.upload_manager.uploaded_files)
                elif hasattr(self.host, 'uploaded_files') and isinstance(self.host.uploaded_files, list):
                    files = list(self.host.uploaded_files)
            except Exception:
                files = list(getattr(self.host, 'uploaded_files', []) or [])

            import os as _os
            for idx, path in enumerate(files):
                row = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
                row.pack(fill="x", pady=(0, 6))

                name = _os.path.basename(path) if isinstance(path, str) else str(path)

                lbl = ctk.CTkLabel(
                    row,
                    text=name,
                    font=ctk.CTkFont(*self.host.get_typography("caption")),
                    text_color=self.host.get_color('text_primary'),
                )
                lbl.pack(side="left", padx=(6, 6))

                def _remove_specific(p=path):
                    try:
                        # Aus Host-Listen entfernen
                        if hasattr(self.host, 'uploaded_files') and isinstance(self.host.uploaded_files, list):
                            try:
                                self.host.uploaded_files = [f for f in self.host.uploaded_files if f != p]
                            except Exception:
                                pass
                        if hasattr(self.host, 'selected_files') and isinstance(self.host.selected_files, list):
                            try:
                                self.host.selected_files = [f for f in self.host.selected_files if f != p]
                            except Exception:
                                pass
                        # UploadManager in Sync halten
                        if hasattr(self.host, 'upload_manager') and getattr(self.host.upload_manager, 'uploaded_files', None) is not None:
                            try:
                                self.host.upload_manager.uploaded_files = [f for f in self.host.upload_manager.uploaded_files if f != p]
                            except Exception:
                                pass
                        # Header/Buttons aktualisieren
                        try:
                            self.host._refresh_upload_ui_from_manager()
                        except Exception:
                            pass
                        # Eigene Liste neu aufbauen
                        self._refresh_file_list_ui()
                    except Exception:
                        pass

                rm_btn = ctk.CTkButton(
                    row,
                    text="Entfernen",
                    height=self.host.get_component_value('heights.button_sm'),
                    font=ctk.CTkFont(*self.host.get_typography("small")),
                    fg_color=self.host.get_color('secondary'),
                    hover_color=self.host.get_color('secondary_hover'),
                    text_color=self.host.get_color('white'),
                    corner_radius=self.host.get_component_value('borders.radius_sm'),
                    command=_remove_specific,
                    width=100,
                )
                rm_btn.pack(side="right", padx=(6, 6))

            # Falls keine Dateien, Hinweiszeile
            if not files:
                hint = ctk.CTkLabel(
                    self.file_list_frame,
                    text="Keine Dateien in der Liste",
                    font=ctk.CTkFont(*self.host.get_typography("caption")),
                    text_color=self.host.get_color('text_secondary'),
                )
                hint.pack(anchor="w", padx=6)
        except Exception:
            pass
