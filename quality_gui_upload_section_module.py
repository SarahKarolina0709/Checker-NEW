"""Upload Section (umbenannt) – Ehemals upload_section_module.py

Konsistenter Prefix: quality_gui_
Keine funktionale Änderung – rein Dateiname / Import-Pfad.
"""
from typing import Any
import customtkinter as ctk

def build_upload_section(app: Any, parent):  # app = ProfessionelleUebersetzungsqualitaetsApp Instanz
    """Erstellt die Upload-Sektion im angegebenen Parent.

    Erwartet, dass app folgende Methoden/Attribute besitzt:
      - get_spacing, get_color, get_typography, _create_card_frame, _add_header_accent
      - _create_button, _upload_source_files, _upload_translation_files, _upload_batch_files
      - _setup_modern_file_management, _responsive_upload_layout, _smart_file_pairing,
        _check_and_show_manual_pairing_option, _show_enhanced_upload_results, _update_file_counter,
        _refresh_file_list_display, update_status, show_toast
    """
    try:
        # Spacing/Radius/Border aus Design-System abrufen (mit Fallbacks)
        spacing_md = app.get_spacing('md') if hasattr(app, 'get_spacing') else 16
        spacing_sm = app.get_spacing('sm') if hasattr(app, 'get_spacing') else 8

        def _comp(path: str, fallback):
            try:
                if hasattr(app, 'get_component_value'):
                    v = app.get_component_value(path)
                    return v if v is not None else fallback
            except Exception:
                pass
            return fallback

        # Sichere Farb-/Font-Helfer (kompatibel mit unterschiedlichen Signaturen)
        def _gc(token: str, fallback: str):
            try:
                fn = getattr(app, 'get_color', None)
                if fn:
                    try:
                        return fn(token, fallback)
                    except TypeError:
                        return fn(token)
            except Exception:
                pass
            return fallback

        def _font(token: str, fallback=("Segoe UI", 12, "normal")):
            try:
                f = app.get_typography(token)
                if isinstance(f, ctk.CTkFont):
                    return f
                if isinstance(f, (list, tuple)):
                    return ctk.CTkFont(*f)
            except Exception:
                pass
            return ctk.CTkFont(*fallback)

        radius = _comp('borders.radius_md', 8)
        border_w = _comp('borders.width_medium', 2)

        upload_card = app._create_card_frame(parent, corner_radius=radius)
        upload_card.pack(fill="x", pady=(0, spacing_sm), padx=spacing_sm)

        header_frame = ctk.CTkFrame(
            upload_card,
            fg_color=_gc('gray_50', '#F8FAFC'),
            corner_radius=radius,
        )
        header_frame.pack(fill="x", padx=spacing_sm, pady=spacing_sm)

        header_content = ctk.CTkFrame(header_frame, fg_color=_gc('transparent', 'transparent'))
        header_content.pack(fill="x", padx=spacing_md, pady=spacing_sm)
        app._add_header_accent(header_content, 'primary')
        header_label = ctk.CTkLabel(
            header_content,
            text=app._t("Datei-Upload und Verwaltung"),
            font=_font('subtitle_unified'),
            text_color=_gc('primary', '#1F4E79')
        )
        header_label.pack(side="left", padx=(spacing_sm, 0))

        # Legacy Zähler entfernt – konsolidierter kombinierter Badge in moderner Upload-Variante

        content_frame = ctk.CTkFrame(upload_card, fg_color=_gc('transparent', 'transparent'))
        content_frame.pack(fill="x", padx=spacing_sm, pady=spacing_sm)

        button_frame = ctk.CTkFrame(content_frame, fg_color=_gc('transparent', 'transparent'))
        button_frame.pack(fill="x", pady=(0, spacing_sm), padx=spacing_sm)
        # Min-Breite aus Design-System ableiten (Fallback 120)
        def _button_min_width(default=120):
            try:
                if hasattr(app, 'get_component_value'):
                    w = app.get_component_value('widths.button_min')
                    if isinstance(w, (int, float)) and w > 0:
                        return int(w)
            except Exception:
                pass
            return default

        min_w = _button_min_width(120)
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, minsize=min_w)

        # Zentrale Button-Fabrik: Versuche Enhanced/ProfessionalButton, fallback auf app._create_button
        def _make_button(parent, text: str, kind: str, command, height=40):
            try:
                # Lazy Import um Zyklen zu vermeiden
                from quality_gui_ui_components import ProfessionalButton, EnhancedButton  # type: ignore
                # ProfessionalButton bevorzugen (Outline/Styling konsistenter)
                if ProfessionalButton:
                    return ProfessionalButton(parent, text=text, style=('primary' if kind=='primary' else 'secondary'), command=command, height=height)
            except Exception:
                try:
                    from quality_gui_ui_components import EnhancedButton  # type: ignore
                    if EnhancedButton:
                        return EnhancedButton.create(parent, text=text, style=('primary' if kind=='primary' else 'secondary'), command=command, height=height)
                except Exception:
                    pass
            # Fallback: bestehende App-Factory nutzen
            return app._create_button(parent, text=text, command=command, kind=kind, height=height)

        def _show_preview_from_upload():
            try:
                rows = getattr(app, '_last_pair_details', None)
                if not isinstance(rows, list) or not rows:
                    if hasattr(app, 'show_toast'):
                        app.show_toast(app._t('Noch keine eingelesenen Segmente verfügbar.'), 'info')
                    return
                metrics_snapshot = None
                try:
                    results = getattr(app, 'analysis_results', None)
                    if isinstance(results, dict):
                        metrics_snapshot = results.get('metrics')
                except Exception:
                    metrics_snapshot = None
                launch_fn = getattr(app, '_launch_pair_details_preview', None)
                if callable(launch_fn):
                    launch_fn(rows, metrics_snapshot)
                    return
                if hasattr(app, 'show_toast'):
                    app.show_toast(app._t('Vorschau aktuell nicht verfügbar.'), 'warning')
            except Exception:
                try:
                    if hasattr(app, 'show_toast'):
                        app.show_toast(app._t('Vorschau konnte nicht geöffnet werden.'), 'error')
                except Exception:
                    pass

        source_btn = _make_button(
            button_frame,
            text=app._t("Ausgangstexte hochladen"),
            command=app._upload_source_files,
            kind="secondary",
            height=40
        )
        source_btn.grid(row=0, column=0, sticky="ew", padx=(0, spacing_sm), pady=1)
        source_hint = ctk.CTkLabel(
            button_frame,
            text=app._t("PDF, DOCX, TXT"),
            font=_font('caption', ("Segoe UI", 11, "normal")),
            text_color=_gc('text_secondary', '#6B7280'),
            anchor="w"
        )
        source_hint.grid(row=1, column=0, sticky="w", padx=(0, spacing_sm), pady=(1, 0))

        translation_btn = _make_button(
            button_frame,
            text=app._t("Übersetzungen hochladen"),
            command=app._upload_translation_files,
            kind="secondary",
            height=40
        )
        translation_btn.grid(row=0, column=1, sticky="ew", padx=spacing_sm, pady=1)
        translation_hint = ctk.CTkLabel(
            button_frame,
            text=app._t("PDF, DOCX, TXT"),
            font=_font('caption', ("Segoe UI", 11, "normal")),
            text_color=_gc('text_secondary', '#6B7280'),
            anchor="w"
        )
        translation_hint.grid(row=1, column=1, sticky="w", padx=spacing_sm, pady=(1, 0))

        batch_btn = _make_button(
            button_frame,
            text=app._t("Stapel-Upload"),
            command=app._upload_batch_files,
            kind="primary",
            height=40
        )
        batch_btn.grid(row=0, column=2, sticky="ew", padx=(spacing_sm, 0), pady=1)
        batch_hint = ctk.CTkLabel(
            button_frame,
            text=app._t("ZIP, Ordner"),
            font=_font('caption', ("Segoe UI", 11, "normal")),
            text_color=_gc('text_secondary', '#6B7280'),
            anchor="w"
        )
        batch_hint.grid(row=1, column=2, sticky="w", padx=(spacing_sm, 0), pady=(1, 0))

        preview_btn = _make_button(
            button_frame,
            text=app._t('Eingelesenen Text anzeigen'),
            command=_show_preview_from_upload,
            kind='secondary',
            height=36
        )
        preview_btn.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(spacing_md, 0))

        # OPTIONAL: Settings-getriebene Dateierweiterungs-Hinweise (für Source/Translation)
        try:
            ss = getattr(app, 'settings_service', None)
            val = ss.get('upload_settings.allowed_extensions', ['.pdf', '.docx', '.txt']) if ss else ['.pdf', '.docx', '.txt']
            if not isinstance(val, (list, tuple)):
                val = [v.strip() for v in str(val).split(',') if v.strip()]
            exts = [e if str(e).startswith('.') else f'.{e}' for e in val]
            label_text = ', '.join([e.strip('.').upper() for e in exts]) or "PDF, DOCX, TXT"
            txt = app._t(label_text)
            source_hint.configure(text=txt)
            translation_hint.configure(text=txt)
        except Exception:
            pass

        app._upload_buttons = {
            'frame': button_frame,
            'source_btn': source_btn,
            'source_hint': source_hint,
            'translation_btn': translation_btn,
            'translation_hint': translation_hint,
            'batch_btn': batch_btn,
            'batch_hint': batch_hint,
            'preview_btn': preview_btn,
        }
        setattr(app, '_preview_ingest_button', preview_btn)

        # Debounce für Resize-Events
        _resize_job = {"id": None}

        def _on_resize(event):
            try:
                if _resize_job["id"]:
                    try:
                        button_frame.after_cancel(_resize_job["id"])
                    except Exception:
                        pass
                _resize_job["id"] = button_frame.after(
                    60, lambda: getattr(app, '_responsive_upload_layout', lambda *_: None)(event.width)
                )
            except Exception:
                pass
        if not hasattr(button_frame, "_resize_bound"):
            button_frame.bind("<Configure>", _on_resize)
            button_frame._resize_bound = True

        app._setup_modern_file_management(content_frame)

        info_frame = ctk.CTkFrame(
            content_frame,
            fg_color=_gc('gray_50', '#F8FAFC'),
            corner_radius=radius,
            border_width=border_w,
            border_color=_gc('surface_border', '#E5E7EB')
        )
        info_frame.pack(fill="x", pady=(spacing_sm, 0))
        # Optionaler Info-Inhalt: Hinweise & Limits
        try:
            info_inner = ctk.CTkFrame(info_frame, fg_color=_gc('transparent', 'transparent'))
            info_inner.pack(fill="x", padx=spacing_md, pady=spacing_sm)
            hint1 = ctk.CTkLabel(
                info_inner,
                text=app._t("Unterstützte Formate: PDF, DOCX, TXT. Mehrfachauswahl möglich."),
                font=_font('caption', ("Segoe UI", 11, "normal")),
                text_color=_gc('text_secondary', '#6B7280'),
                anchor='w'
            )
            hint1.pack(fill='x')
            hint2 = ctk.CTkLabel(
                info_inner,
                text=app._t("Tipp: Für viele Dateien den Stapel-Upload (ZIP/Ordner) verwenden."),
                font=_font('caption', ("Segoe UI", 11, "normal")),
                text_color=_gc('text_secondary', '#6B7280'),
                anchor='w'
            )
            hint2.pack(fill='x', pady=(4, 0))
        except Exception:
            pass

        # Tastatur- und Tooltip-Affordances (A11y/UX)
        for b, tip in (
            (source_btn, app._t("Ausgangstexte hinzufügen")),
            (translation_btn, app._t("Übersetzungen hinzufügen")),
            (batch_btn, app._t("ZIP hochladen oder Ordner wählen")),
            (preview_btn, app._t('Eingelesenen Text ansehen')),
        ):
            try:
                b.configure(takefocus=True)
                b.bind("<Return>", lambda _e, btn=b: btn.invoke())
                b.bind("<space>",  lambda _e, btn=b: btn.invoke())
                if hasattr(app, '_attach_tooltip'):
                    app._attach_tooltip(b, tip, delay=500)
            except Exception:
                pass
        return upload_card
    except Exception as e:
        try:
            logger = getattr(app, 'logger', None)
            if logger:
                logger.exception("Fehler beim Aufbau der Upload-Sektion")
        except Exception:
            pass
        if hasattr(app, '_handle_error'):
            app._handle_error(e, context="ui.upload.section")
        return None

__all__ = ["build_upload_section"]
