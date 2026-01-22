"""Quality GUI File Components

Ausgelagerte UI-Bausteine aus `quality_gui_main_app.ProfessionelleUebersetzungsqualitaetsApp`.

NAMING-POLICY:
- Prefix: quality_gui_components_*
- Dieses Modul: Datei-/Explorer-bezogene Komponenten
- Original-Methoden behalten ihre Signaturen und rufen nur diese Funktionen auf.

TRACEABILITY:
- Ursprünglich: _create_file_category_section, _create_file_card
- Zentraler Backup-Filter nutzt: quality_gui_utilities.is_backup_filename

Verwendung:
    from quality_gui_components_file import (
        build_file_category_section,
        build_file_card,
    )

Alle Funktionen erwarten das ursprüngliche App-Objekt (self) als ersten Parameter
um Design-System und State zu nutzen.
"""
from __future__ import annotations
from typing import List, Callable
import os, time, logging
import customtkinter as ctk
try:
    import tkinter as tk  # Für Kontextmenü / Variablen
except Exception:  # pragma: no cover
    tk = None  # type: ignore

try:
    from quality_gui_utilities import is_backup_filename
except Exception:  # Fallback falls Import sehr früh fehlschlägt
    def is_backup_filename(name: str) -> bool:  # type: ignore
        return False

# ---------------------------------------------------------------------------
# DESIGN-SYSTEM / UI THREAD HELFER
# ---------------------------------------------------------------------------
def _ds_radius(app, token: str, fallback: int = 8) -> int:
    try:
        ds = getattr(app, 'design_system', None)
        if isinstance(ds, dict):
            return int(ds.get('components', {}).get('borders', {}).get(token, fallback))
    except Exception:
        pass
    return fallback

def _space(app, key: str, fallback: int) -> int:
    try:
        fn = getattr(app, 'get_spacing', None)
        if callable(fn):
            return int(fn(key))
    except Exception:
        pass
    return fallback

def _ui(app, fn):
    root = getattr(app, 'root', None)
    if root and hasattr(root, 'after'):
        return root.after(0, fn)
    return fn()

def _color(app, token: str, fallback_token: str = 'surface'):
    try:
        return app.get_color(token)
    except Exception:
        try:
            return app.get_color(fallback_token)
        except Exception:
            return '#CCCCCC'

# ---------------------------------------------------------------------------
# PUBLIC BUILDERS
# ---------------------------------------------------------------------------

def build_file_category_section(app, parent, title: str, files: List[str], row: int, col: int, color_theme: str):
    """Erstellt einen Datei-Kategorie-Abschnitt (i18n + Pagination + Toggle + Events)."""
    logger = getattr(app, 'logger', logging.getLogger(__name__))
    try:
        show_backups = bool(getattr(app, '_show_backups_files', False))
        original_total = len(files)
        hidden_count = 0
        if not show_backups:
            filtered_files = [f for f in files if not is_backup_filename(os.path.basename(f))]
            hidden_count = original_total - len(filtered_files)
            files = filtered_files
            if hidden_count > 0:
                try:
                    logger.debug(f"Backup-Dateien ausgeblendet: {hidden_count} in '{title}'")
                except Exception:
                    pass

        page_size = getattr(app, '_file_page_size', 50)
        if not isinstance(page_size, int) or page_size <= 0:
            page_size = 50
        current_page = getattr(app, '_current_file_page', 1)
        max_page = max(1, (len(files) + page_size - 1) // page_size)
        if current_page > max_page:
            current_page = max_page
            setattr(app, '_current_file_page', current_page)
        start = (current_page - 1) * page_size
        end = start + page_size
        page_slice = files[start:end]

        category_frame = ctk.CTkFrame(
            parent,
            fg_color=_color(app, f'{color_theme}_light', 'surface'),
            corner_radius=_ds_radius(app, 'radius_md', 8),
            border_width=0,
        )
        category_frame.grid(row=row, column=col, sticky="nsew", padx=_space(app, 'md', 10))

        header_text = app._t("{title} ({count})").format(title=title, count=len(files))
        if hidden_count > 0:
            header_text += " – " + app._t("{n} hidden").format(n=hidden_count)
        header_label = ctk.CTkLabel(
            category_frame,
            text=header_text,
            font=ctk.CTkFont(*app.get_typography('subheading')),
            text_color=_color(app, color_theme, color_theme)
        )
        header_label.pack(pady=(15, 6), anchor='w', padx=12)

        try:
            if tk is not None:
                var = tk.IntVar(value=1 if show_backups else 0)
                toggle = ctk.CTkCheckBox(
                    category_frame,
                    text=app._t("Show backups"),
                    variable=var,
                    command=lambda v=var: _toggle_backups(app, v.get())
                )
                toggle.pack(anchor='e', padx=12, pady=(0, 4))
        except Exception:
            pass

        if files:
            files_scroll = ctk.CTkScrollableFrame(
                category_frame,
                fg_color="transparent",
                height=getattr(app, 'file_list_height', _space(app, '2xl', 224))
            )
            files_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 8))
            for i, file_path in enumerate(page_slice, start=start):
                build_file_card(app, files_scroll, file_path, i, color_theme)

            if max_page > 1:
                pager = ctk.CTkFrame(category_frame, fg_color="transparent")
                pager.pack(fill='x', padx=12, pady=(4, 8))
                def _set_page(delta: int):
                    try:
                        new_page = getattr(app, '_current_file_page', 1) + delta
                        new_page = max(1, min(max_page, new_page))
                        setattr(app, '_current_file_page', new_page)
                        _trigger_files_refresh(app)
                    except Exception:
                        pass
                prev_btn = ctk.CTkButton(
                    pager, text=app._t("Prev"),
                    width=_space(app, 'lg', 80),
                    command=lambda: _set_page(-1),
                    fg_color=_color(app, 'secondary', 'primary'),
                    hover_color=_color(app, 'secondary_hover', 'primary_hover'),
                    text_color=_color(app, 'text_inverse'),
                    font=ctk.CTkFont(*app.get_typography('button'))
                )
                prev_btn.pack(side='left', padx=(0, 6))
                info_lbl = ctk.CTkLabel(
                    pager,
                    text=app._t("Page {p}/{m}").format(p=current_page, m=max_page),
                    font=ctk.CTkFont(*app.get_typography('caption')),
                    text_color=app.get_color('text_secondary')
                )
                info_lbl.pack(side='left')
                next_btn = ctk.CTkButton(
                    pager, text=app._t("Next"),
                    width=_space(app, 'lg', 80),
                    command=lambda: _set_page(1),
                    fg_color=_color(app, 'secondary', 'primary'),
                    hover_color=_color(app, 'secondary_hover', 'primary_hover'),
                    text_color=_color(app, 'text_inverse'),
                    font=ctk.CTkFont(*app.get_typography('button'))
                )
                next_btn.pack(side='left', padx=(6, 0))

            remaining = len(files) - (start + len(page_slice))
            if remaining > 0:
                more_label = ctk.CTkLabel(
                    category_frame,
                    text=app._t("… and {n} more files").format(n=remaining),
                    font=ctk.CTkFont(*app.get_typography('caption')),
                    text_color=app.get_color('text_secondary')
                )
                more_label.pack(pady=4, anchor='w', padx=15)
        else:
            empty_label = ctk.CTkLabel(
                category_frame,
                text=app._t("No files uploaded yet\nDrag & drop files here"),
                font=ctk.CTkFont(*app.get_typography('body')),
                text_color=app.get_color('text_secondary'),
                justify="center"
            )
            empty_label.pack(expand=True, pady=30)

        if getattr(app, 'event_bus', None) and not getattr(app, '_files_section_bound', False):
            try:
                app.event_bus.subscribe('files.changed', lambda _=None: _trigger_files_refresh(app))
                app._files_section_bound = True
            except Exception:
                pass
        try:
            if not hasattr(app, '_files_rebuilders'):
                app._files_rebuilders = []  # type: ignore
            if not hasattr(app, '_files_rebuilders_keys'):
                app._files_rebuilders_keys = set()  # type: ignore
            key = f"{id(parent)}:{title}:{row}:{col}"
            def _rebuilder():
                try:
                    build_file_category_section(app, parent, title, files, row, col, color_theme)
                except Exception:
                    pass
            if key not in app._files_rebuilders_keys:  # type: ignore
                app._files_rebuilders.append(_rebuilder)  # type: ignore
                app._files_rebuilders_keys.add(key)       # type: ignore
        except Exception:
            pass
    except Exception as e:
        logger.exception("File category section error: %s", e)
        try: app._show_toast(app._t("Could not render file section"), 'warning')
        except Exception: pass


def build_file_card(app, parent, file_path: str, index: int, color_theme: str):
    """Erstellt eine einzelne Datei-Karte (i18n + Kontextmenü + Tooltips + Doppelklick)."""
    logger = getattr(app, 'logger', logging.getLogger(__name__))
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    try:
        file_size = os.path.getsize(file_path)
        size_str = app._format_file_size(file_size)
        modified_time = os.path.getmtime(file_path)
        modified_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(modified_time))
    except Exception:
        size_str = app._t("Unknown")
        modified_str = app._t("Unknown")

    file_card = app._create_card_frame(
        parent,
        corner_radius=_ds_radius(app, 'radius_md', 8),
        border_width=1
    )
    file_card.pack(fill="x", pady=3)
    # Klick / Kontext / Middle / Doppelklick Bindings (Fallback sicher)
    def _safe_bind(widget, sequence, handler):
        try:
            widget.bind(sequence, handler)
        except Exception:
            pass
    def _open_path_inline(path: str):
        try:
            if hasattr(app, '_open_file'):
                return app._open_file(path)
            import subprocess, sys
            if os.name == 'nt':
                os.startfile(path)  # type: ignore
            else:
                subprocess.Popen(['xdg-open' if sys.platform.startswith('linux') else 'open', path])
        except Exception:
            pass
    _safe_bind(file_card, "<Double-Button-1>", lambda e, p=file_path: _open_path_inline(p))
    _safe_bind(file_card, "<Button-3>", lambda e, p=file_path: _file_context_menu(app, e, p, parent))
    _safe_bind(file_card, "<Button-2>", lambda e, p=file_path: _open_path_inline(p))  # Middle Click gleich öffnen

    info_frame = ctk.CTkFrame(file_card, fg_color="transparent")
    info_frame.pack(fill="x", padx=12, pady=8)
    name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
    name_frame.pack(fill="x")

    file_label = ctk.CTkLabel(
        name_frame,
        text=f"{index + 1}. {file_name}",
        font=ctk.CTkFont(*app.get_typography('body_bold')),
        text_color=app.get_color('text_primary'),
        anchor="w"
    )
    file_label.pack(side="left")
    # Tooltip
    try:
        file_label.bind("<Enter>", lambda e, t=file_name: getattr(app, '_show_tooltip', lambda *a, **k: None)(file_label, t))
        file_label.bind("<Leave>", lambda e: getattr(app, '_hide_tooltip', lambda *a, **k: None)())
    except Exception:
        pass

    badge_text = (file_ext.upper()[1:] if file_ext.startswith('.') else file_ext.upper()) or "FILE"
    ext_badge = ctk.CTkLabel(
        name_frame,
        text=badge_text,
        font=ctk.CTkFont(*app.get_typography('caption')),
        text_color=_color(app, 'text_inverse'),
        fg_color=_color(app, color_theme, 'primary'),
        corner_radius=_ds_radius(app, 'radius_sm', 6),
        width=_space(app, 'xl', 40),
        height=_space(app, 'md', 20)
    )
    ext_badge.pack(side="right")

    meta_label = ctk.CTkLabel(
        info_frame,
        text=app._t("Size: {size} • Modified: {date}").format(size=size_str, date=modified_str),
        font=ctk.CTkFont(*app.get_typography('caption')),
        text_color=app.get_color('text_secondary'),
        anchor="w"
    )
    meta_label.pack(fill="x", pady=(3, 0))
    # Ende build_file_card (Fehler in Subblöcken bereits abgefangen)


def _file_context_menu(app, event, path: str, master):  # pragma: no cover
    try:
        # CTk hat kein natives Menu → Tk Menu fallback
        menu = None
        factory = getattr(app, '_context_menu_factory', None)
        if callable(factory):
            try:
                menu = factory(master)
            except Exception:
                menu = None
        if menu is None:
            if tk is None:
                return
            menu = tk.Menu(master, tearoff=0)
        # Standard-Optionen
        menu.add_command(label=app._t("Open in Explorer"), command=lambda: _open_in_explorer(app, path))
        menu.add_separator()
        menu.add_command(label=app._t("Mark as Source"), command=lambda: _mark_file(app, path, 'source'))
        menu.add_command(label=app._t("Mark as Translation"), command=lambda: _mark_file(app, path, 'translation'))

        # Analyse nur diese Datei
        def _analyze_single():
            try:
                if hasattr(app, "start_analysis_for_file"):
                    app.start_analysis_for_file(path)
                elif getattr(app, "event_bus", None):
                    app.event_bus.publish("analysis.requested.single", {"path": path})
                else:
                    if hasattr(app, '_show_toast'):
                        app._show_toast(app._t("No analysis function available"), "warning")
            except Exception as e:
                (getattr(app, "logger", None) or print)(f"Single analysis failed: {e}")

        # Analyse alle Dateien
        def _analyze_all():
            try:
                if hasattr(app, "start_analysis"):
                    app.start_analysis()
                elif getattr(app, "event_bus", None):
                    app.event_bus.publish("analysis.requested.all", {"files": getattr(app, 'uploaded_files', {})})
                else:
                    if hasattr(app, '_show_toast'):
                        app._show_toast(app._t("No analysis function available"), "warning")
            except Exception as e:
                (getattr(app, "logger", None) or print)(f"All analysis failed: {e}")

        menu.add_separator()
        menu.add_command(label=app._t("Start analysis (this file)"), command=_analyze_single)
        menu.add_command(label=app._t("Start analysis (all files)"), command=_analyze_all)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            if hasattr(menu, 'grab_release'):
                try: menu.grab_release()
                except Exception: pass
    except Exception:
        pass


def _open_in_explorer(app, path: str):  # pragma: no cover
    try:
        if hasattr(app, '_open_in_explorer'):
            return app._open_in_explorer(path)
        import subprocess, sys
        if os.name == 'nt':
            subprocess.Popen(['explorer', '/select,', path])
        else:
            subprocess.Popen(['xdg-open' if sys.platform.startswith('linux') else 'open', os.path.dirname(path)])
    except Exception:
        pass


def _mark_file(app, path: str, role: str):  # pragma: no cover
    try:
        if hasattr(app, '_mark_file'):
            app._mark_file(path, role)
        # Fallback: Attribute setzen
        else:
            if role == 'source':
                app._last_marked_source = path  # type: ignore
            elif role == 'translation':
                app._last_marked_translation = path  # type: ignore
        if getattr(app, 'event_bus', None):
            try: app.event_bus.publish('files.changed', {'action': 'mark', 'role': role, 'path': path})
            except Exception: pass
    except Exception:
        pass


def _toggle_backups(app, value: int):  # pragma: no cover
    try:
        app._show_backups_files = bool(value)
        _trigger_files_refresh(app)
    except Exception:
        pass


def _trigger_files_refresh(app):  # pragma: no cover
    try:
        def _do():
            if hasattr(app, 'refresh_files_view'):
                app.refresh_files_view(show_backups=getattr(app, '_show_backups_files', False))
                return
            rebuilders = getattr(app, '_files_rebuilders', [])
            for rb in list(rebuilders):
                try: rb()
                except Exception: continue
        _ui(app, _do)
    except Exception:
        pass
