#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modularisierte Upload Section (aus quality_gui_main_app extrahiert).

Nur UI-Aufbau + Events (nutzt bestehende Methoden des Haupt-Apps).
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
        spacing_md = app.get_spacing('md') if hasattr(app, 'get_spacing') else 16
        spacing_sm = app.get_spacing('sm') if hasattr(app, 'get_spacing') else 8

        upload_card = app._create_card_frame(parent, corner_radius=8)
        upload_card.pack(fill="x", pady=(0, 6), padx=4)

        header_frame = ctk.CTkFrame(
            upload_card,
            fg_color=app.get_color('gray_50'),
            corner_radius=8,
            height=50
        )
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)

        header_content = ctk.CTkFrame(header_frame, fg_color=app.get_color('transparent'))
        header_content.pack(fill="x", padx=14, pady=6)
        app._add_header_accent(header_content, 'primary')
        header_label = ctk.CTkLabel(
            header_content,
            text=app._t("File Upload & Management"),
            font=ctk.CTkFont(*app.get_typography('subtitle_unified')),
            text_color=app.get_color('primary')
        )
        header_label.pack(side="left", padx=(8, 0))

        app.header_file_counter_label = ctk.CTkLabel(
            header_content,
            text=app._t("Files: 0 source, 0 translations"),
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary')
        )
        app.header_file_counter_label.pack(side="right")

        content_frame = ctk.CTkFrame(upload_card, fg_color=app.get_color('transparent'))
        content_frame.pack(fill="x", padx=8, pady=6)

        button_frame = ctk.CTkFrame(content_frame, fg_color=app.get_color('transparent'))
        button_frame.pack(fill="x", pady=(0, 4), padx=5)
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, minsize=120)

        source_btn = app._create_button(
            button_frame,
            text=app._t("Upload Source Files"),
            command=app._upload_source_files,
            kind="secondary",
            height=40
        )
        source_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=1)
        source_hint = ctk.CTkLabel(
            button_frame,
            text="PDF, DOCX, TXT",
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary'),
            anchor="w"
        )
        source_hint.grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(1, 0))

        translation_btn = app._create_button(
            button_frame,
            text=app._t("Upload Translations"),
            command=app._upload_translation_files,
            kind="secondary",
            height=40
        )
        translation_btn.grid(row=0, column=1, sticky="ew", padx=4, pady=1)
        translation_hint = ctk.CTkLabel(
            button_frame,
            text="PDF, DOCX, TXT",
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary'),
            anchor="w"
        )
        translation_hint.grid(row=1, column=1, sticky="w", padx=4, pady=(1, 0))

        batch_btn = app._create_button(
            button_frame,
            text=app._t("Batch Upload"),
            command=app._upload_batch_files,
            kind="primary",
            height=40
        )
        batch_btn.grid(row=0, column=2, sticky="ew", padx=(4, 0), pady=1)
        batch_hint = ctk.CTkLabel(
            button_frame,
            text="ZIP, Ordner",
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary'),
            anchor="w"
        )
        batch_hint.grid(row=1, column=2, sticky="w", padx=(4, 0), pady=(1, 0))

        app._upload_buttons = {
            'frame': button_frame,
            'source_btn': source_btn,
            'source_hint': source_hint,
            'translation_btn': translation_btn,
            'translation_hint': translation_hint,
            'batch_btn': batch_btn,
            'batch_hint': batch_hint,
        }

        def _on_resize(event):
            try:
                app._responsive_upload_layout(event.width)
            except Exception:
                pass
        if not hasattr(button_frame, "_resize_bound"):
            button_frame.bind("<Configure>", _on_resize)
            button_frame._resize_bound = True

        app._setup_modern_file_management(content_frame)

        info_frame = ctk.CTkFrame(
            content_frame,
            fg_color=app.get_color('gray_50'),
            corner_radius=12,
            border_width=2,
            border_color=app.get_color('primary_light', '#F0F7FF') if hasattr(app, 'get_color') else '#F0F7FF'
        )
        info_frame.pack(fill="x", pady=(spacing_sm, 0))
        return upload_card
    except Exception as e:
        if hasattr(app, '_handle_error'):
            app._handle_error(e, context="ui.upload.section")
        return None
