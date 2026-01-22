"""Separater Findings Viewer (Scrollable Dialog) – modular, design-system konform."""
from __future__ import annotations
import customtkinter as ctk
from typing import List, Dict, Any
try:
    import tkinter as tk  # für clipboard fallback
except Exception:  # pragma: no cover
    tk = None  # type: ignore


def open_findings_viewer(app, findings: List[Dict[str, Any]]):
    try:
        if not findings:
            if hasattr(app, '_show_toast'):
                app._show_toast(app._t('No findings available'), 'info')
            return
        top = ctk.CTkToplevel(app.root if hasattr(app, 'root') else None)
        top.title(app._t('Show all results'))
        try:
            top.geometry('900x600')
        except Exception:
            pass
        spacing_lg = app.get_spacing('lg') if hasattr(app, 'get_spacing') else 24
        radius_md = 8
        fg_surface = app.get_color('surface') if hasattr(app, 'get_color') else '#FFFFFF'
        fg_border = app.get_color('surface_border') if hasattr(app, 'get_color') else '#E5E7EB'
        top.configure(fg_color=fg_surface)

        container = ctk.CTkFrame(top, fg_color=fg_surface, border_width=1, border_color=fg_border, corner_radius=radius_md)
        container.pack(fill='both', expand=True, padx=spacing_lg, pady=spacing_lg)

        header = ctk.CTkLabel(
            container,
            text=app._t('Show all results'),
            font=ctk.CTkFont(*app.get_typography('heading')),
            text_color=app.get_color('text_primary')
        )
        header.pack(anchor='w', padx=spacing_lg, pady=(spacing_lg, spacing_lg//3))

        # Filter / Actions Bar
        actions_bar = ctk.CTkFrame(container, fg_color='transparent')
        actions_bar.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg//2))

        current_filter = {'severity': 'all'}

        def _render_filtered():
            try:
                # Lösche bestehende Finding Widgets im inner Frame
                for child in inner.winfo_children():
                    child.destroy()
                _render_findings()
            except Exception:
                pass

        def _set_filter(sev: str):
            current_filter['severity'] = sev
            _style_filter_buttons()
            _render_filtered()

        def _copy_findings():
            try:
                active = []
                for f in findings:
                    sev = (f.get('severity') or 'info').lower()
                    if current_filter['severity'] != 'all' and sev != current_filter['severity']:
                        continue
                    rid = f.get('rule_id') or f.get('rule') or 'rule'
                    msg = (f.get('message') or '').replace('\n', ' ')
                    active.append(f"[{sev}] {rid}: {msg}")
                data = '\n'.join(active)
                if not data:
                    if hasattr(app, '_show_toast'):
                        app._show_toast(app._t('No findings available'), 'info')
                    return
                try:
                    if app.root:
                        app.root.clipboard_clear()
                        app.root.clipboard_append(data)
                except Exception:
                    if tk and hasattr(tk, 'Tk'):
                        try:
                            _tmp = tk.Tk(); _tmp.withdraw(); _tmp.clipboard_clear(); _tmp.clipboard_append(data); _tmp.update(); _tmp.destroy()
                        except Exception:
                            pass
                if hasattr(app, '_show_toast'):
                    app._show_toast(app._t('Findings copied'), 'success')
            except Exception:
                if hasattr(app, '_show_toast'):
                    app._show_toast(app._t('Copy failed'), 'warning')

        # Filter Buttons
        filter_values = [
            ('all', app._t('All')),
            ('critical', app._t('Critical')),
            ('major', app._t('Major')),
            ('minor', app._t('Minor')),
        ]
        filter_buttons = {}
        for sev, label in filter_values:
            btn = ctk.CTkButton(
                actions_bar,
                text=label,
                width=130,
                command=lambda s=sev: _set_filter(s),
                fg_color=app.get_color('secondary'),
                hover_color=app.get_color('secondary_hover'),
                text_color=app.get_color('text_inverse'),
                font=ctk.CTkFont(*app.get_typography('button'))
            )
            btn.pack(side='left', padx=(0, 6))
            filter_buttons[sev] = btn

        copy_btn = ctk.CTkButton(
            actions_bar,
            text=app._t('Copy findings'),
            command=_copy_findings,
            fg_color=app.get_color('primary'),
            hover_color=app.get_color('primary_hover'),
            text_color=app.get_color('text_inverse'),
            font=ctk.CTkFont(*app.get_typography('button'))
        )
        copy_btn.pack(side='right')

        def _style_filter_buttons():
            try:
                active = current_filter['severity']
                for sev, btn in filter_buttons.items():
                    if sev == active:
                        btn.configure(fg_color=app.get_color('primary'), hover_color=app.get_color('primary_hover'))
                    else:
                        btn.configure(fg_color=app.get_color('secondary'), hover_color=app.get_color('secondary_hover'))
            except Exception:
                pass

        # initial styling
        _style_filter_buttons()

        # Scrollable area
        scroll_frame = ctk.CTkFrame(container, fg_color='transparent')
        scroll_frame.pack(fill='both', expand=True, padx=spacing_lg, pady=(0, spacing_lg))
        canvas = ctk.CTkCanvas(scroll_frame, highlightthickness=0, bg=fg_surface)
        vsb = ctk.CTkScrollbar(scroll_frame, orientation='vertical', command=canvas.yview)
        inner = ctk.CTkFrame(canvas, fg_color='transparent')
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        canvas_window = canvas.create_window((0,0), window=inner, anchor='nw')

        def _on_config(event):
            try:
                canvas.configure(scrollregion=canvas.bbox('all'))
                # dynamische Breite
                canvas.itemconfigure(canvas_window, width=canvas.winfo_width())
            except Exception:
                pass
        inner.bind('<Configure>', _on_config)
        canvas.bind('<Configure>', lambda e: _on_config(e))

        # Findings rendern (mit Filter)
        def _render_findings():
            color_map = {'critical':'error','major':'warning','minor':'info'}
            sev_filter = current_filter['severity']
            for f in findings:
                try:
                    sev_val = (f.get('severity') or 'info').lower()
                    if sev_filter != 'all' and sev_val != sev_filter:
                        continue
                    msg = (f.get('message') or '')
                    rid = f.get('rule_id') or f.get('rule') or 'rule'
                    token = color_map.get(sev_val, 'text_primary')
                    lbl = ctk.CTkLabel(
                        inner,
                        text=f"• [{sev_val}] {rid}: {msg}"[:800],
                        anchor='w',
                        justify='left',
                        font=ctk.CTkFont(*app.get_typography('body')),
                        text_color=app.get_color(token)
                    )
                    lbl.pack(fill='x', pady=2)
                    def _wrap(event=None, _lbl=lbl):
                        try:
                            w = _lbl.winfo_width()
                            if w > 0:
                                _lbl.configure(wraplength=int(w * 0.97))
                        except Exception:
                            pass
                    lbl.bind('<Configure>', _wrap)
                except Exception:
                    continue

        _render_findings()

        # Close button
        def _close():
            try:
                top.destroy()
            except Exception:
                pass
        btn_close = ctk.CTkButton(
            container,
            text=app._t('Close'),
            command=_close,
            fg_color=app.get_color('primary'),
            hover_color=app.get_color('primary_hover'),
            text_color=app.get_color('text_inverse')
        )
        btn_close.pack(pady=(0, spacing_lg), anchor='e', padx=spacing_lg)
    except Exception:
        pass
