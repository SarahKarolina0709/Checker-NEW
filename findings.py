from __future__ import annotations
from typing import Any, Dict, List, Tuple
import time
import customtkinter as ctk

from ds_utils import ds_get_color, get_font, get_spacing
from widgets import Tooltip
from exporters import export_findings, make_correction_package


def render_findings_block(app: Any, parent: Any, findings: List[Dict[str, Any]], findings_grouped: List[Dict[str, Any]] | None = None, config: Any = None, initial_state: Dict[str, Any] | None = None) -> None:
    """Render die Findings-Liste inkl. Filter, Suche, Export, Korrekturpaket.

    Diese Implementierung ist eine extrahierte, leicht vereinfachte Variante des bisherigen Blocks.
    """
    if not findings and not findings_grouped:
        ctk.CTkLabel(
            parent,
            text=app._t('Keine Befunde gefunden'),
            font=ctk.CTkFont(*get_font(app, 'body')),
            text_color=ds_get_color(app, 'text_secondary'),
        ).pack(anchor='w')
        return

    spacing_md = get_spacing(app, 'md')
    spacing_lg = get_spacing(app, 'lg')
    spacing_sm = get_spacing(app, 'sm')

    container = ctk.CTkFrame(parent, fg_color=ds_get_color(app, 'surface_hover'))
    container.pack(fill='both', expand=True)

    controls = ctk.CTkFrame(container, fg_color=ds_get_color(app, 'surface'), border_width=1, border_color=ds_get_color(app, 'surface_border'))
    controls.pack(fill='x')

    state: Dict[str, Any] = {
        'severity': 'ALL',
        'checker': 'ALL',
        'query': '',
        'sort': 'severity',
        'sort_dir': 'asc',
        'grouped': False,
    }

    # Load centralized AnalysisState first (if available)
    try:
        if hasattr(app, 'analysis_state') and app.analysis_state:
            st = app.analysis_state.get_findings_state()
            if isinstance(st, dict):
                for k, v in st.items():
                    if k in state:
                        state[k] = v
    except Exception:
        pass

    # Apply initial state if provided (from parent view)
    try:
        if isinstance(initial_state, dict):
            for k, v in initial_state.items():
                if k in state and isinstance(v, type(state[k])):
                    state[k] = v
    except Exception:
        pass

    # Persisted settings (optional, legacy fallback via config)
    _cfg = config
    try:
        if _cfg:
            for k in ('severity', 'checker', 'sort', 'sort_dir'):
                val = _cfg.get(f'analysis.ui.findings.{k}')
                if isinstance(val, str):
                    state[k] = val
    except Exception:
        pass

    def _persist() -> None:
        # Primary: use centralized AnalysisState
        try:
            if hasattr(app, 'analysis_state') and app.analysis_state:
                app.analysis_state.update_findings_state({
                    'severity': state['severity'],
                    'checker': state['checker'],
                    'sort': state['sort'],
                    'sort_dir': state['sort_dir'],
                    'query': state.get('query', ''),
                    'grouped': state.get('grouped', False),
                })
        except Exception:
            pass
        # Fallback legacy persistence
        try:
            if _cfg:
                _cfg.set('analysis.ui.findings.severity', state['severity'])
                _cfg.set('analysis.ui.findings.checker', state['checker'])
                _cfg.set('analysis.ui.findings.sort', state['sort'])
                _cfg.set('analysis.ui.findings.sort_dir', state['sort_dir'])
        except Exception:
            pass

    # Severity Filter
    sev_frame = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    sev_frame.pack(side='left')
    sev_defs = [(app._t('Alle'), 'ALL'), (app._t('Kritisch'), 'critical'), (app._t('Wesentlich'), 'major'), (app._t('Gering'), 'minor')]
    sev_buttons: List[Tuple[Any, str]] = []

    def _set_severity(val: str) -> None:
        state['severity'] = val
        _persist(); _render_list()
        for b, v in sev_buttons:
            try:
                b.configure(
                    fg_color=ds_get_color(app, 'primary') if v == val else ds_get_color(app, 'surface_hover'),
                    text_color=ds_get_color(app, 'text_inverse') if v == val else ds_get_color(app, 'text_primary')
                )
            except Exception:
                pass

    for lab, val in sev_defs:
        try:
            b = ctk.CTkButton(
                sev_frame, text=lab, width=92, height=26,
                fg_color=ds_get_color(app, 'surface_hover'),
                hover_color=ds_get_color(app, 'surface_hover'),
                text_color=ds_get_color(app, 'text_primary'),
                command=lambda _v=val: _set_severity(_v)
            )
            b.pack(side='left', padx=2)
            sev_buttons.append((b, val))
        except Exception:
            continue

    # Checker Filter
    chk_frame = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    chk_frame.pack(side='left', padx=spacing_lg)
    ctk.CTkLabel(
        chk_frame, text=app._t('Prüfer'), font=ctk.CTkFont(*get_font(app, 'caption')),
        text_color=ds_get_color(app, 'text_secondary')
    ).pack(anchor='w')
    checker_defs = [(app._t('Alle'), 'ALL'), ('heuristic', 'heuristic'), ('hunspell', 'hunspell'), ('languagetool', 'languagetool'), ('ollama', 'ollama')]
    chk_buttons: List[Tuple[Any, str]] = []

    def _set_checker(val: str) -> None:
        state['checker'] = val
        _persist(); _render_list()
        for b, v in chk_buttons:
            try:
                b.configure(
                    fg_color=ds_get_color(app, 'primary') if v == val else ds_get_color(app, 'surface_hover'),
                    text_color=ds_get_color(app, 'text_inverse') if v == val else ds_get_color(app, 'text_primary')
                )
            except Exception:
                pass

    for lab, val in checker_defs:
        try:
            b = ctk.CTkButton(
                chk_frame, text=lab, width=80, height=24,
                fg_color=ds_get_color(app, 'surface_hover'),
                hover_color=ds_get_color(app, 'surface_hover'),
                text_color=ds_get_color(app, 'text_primary'),
                command=lambda _v=val: _set_checker(_v)
            )
            b.pack(side='left', padx=2, pady=(2, 0))
            chk_buttons.append((b, val))
        except Exception:
            continue

    # Suche
    search_frame = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    search_frame.pack(side='left', padx=spacing_lg)
    ctk.CTkLabel(
        search_frame, text=app._t('Suche'), font=ctk.CTkFont(*get_font(app, 'caption')),
        text_color=ds_get_color(app, 'text_secondary')
    ).pack(anchor='w')
    query_var = ctk.StringVar(value=state.get('query', ''))

    def _on_query(*_):
        state['query'] = query_var.get().strip().lower(); _persist(); _render_list()

    try:
        ent = ctk.CTkEntry(search_frame, textvariable=query_var, width=180)
        ent.pack(anchor='w')
        query_var.trace_add('write', _on_query)
        # Expose search entry for Ctrl+F focus from parent containers
        try:
            setattr(parent, '_findings_search_entry', ent)
            pm = getattr(parent, 'master', None)
            if pm is not None:
                setattr(pm, '_findings_search_entry', ent)
        except Exception:
            pass
    except Exception:
        ent = None

    # Sortierung
    sort_frame = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    sort_frame.pack(side='left', padx=spacing_lg)
    ctk.CTkLabel(
        sort_frame, text=app._t('Sortierung'), font=ctk.CTkFont(*get_font(app, 'caption')),
        text_color=ds_get_color(app, 'text_secondary')
    ).pack(anchor='w')
    sort_buttons: List[Tuple[Any, str, str]] = []  # (button, value, base_label)

    def _refresh_sort_labels() -> None:
        try:
            for b, v, base in sort_buttons:
                is_active = (v == state['sort'])
                suffix = ''
                if is_active:
                    suffix = ' (Auf)' if state['sort_dir'] == 'asc' else ' (Ab)'
                b.configure(text=base + suffix)
        except Exception:
            pass

    def _set_sort(val: str) -> None:
        state['sort'] = val
        _persist(); _render_list()
        for b, v, _ in sort_buttons:
            try:
                b.configure(
                    fg_color=ds_get_color(app, 'primary') if v == val else ds_get_color(app, 'surface_hover'),
                    text_color=ds_get_color(app, 'text_inverse') if v == val else ds_get_color(app, 'text_primary')
                )
            except Exception:
                pass
        _refresh_sort_labels()

    def _rebuild_sort_buttons() -> None:
        nonlocal sort_buttons
        for b, _, _ in list(sort_buttons):
            try:
                b.destroy()
            except Exception:
                pass
        sort_buttons = []
        local_defs = [(app._t('Schweregrad'), 'severity'), (app._t('Regel'), 'rule'), (app._t('Nachricht'), 'message')]
        if state.get('grouped'):
            local_defs.append((app._t('Anzahl'), 'count'))
            local_defs.append((app._t('Sicherheitswert'), 'confidence'))
        for lab, val in local_defs:
            try:
                b = ctk.CTkButton(
                    sort_frame, text=lab, width=84, height=24,
                    fg_color=ds_get_color(app, 'surface_hover'),
                    hover_color=ds_get_color(app, 'surface_hover'),
                    text_color=ds_get_color(app, 'text_primary'),
                    command=lambda _v=val: _set_sort(_v)
                )
                b.pack(side='left', padx=2, pady=(2, 0))
                sort_buttons.append((b, val, lab))
            except Exception:
                continue
        _refresh_sort_labels()

    _rebuild_sort_buttons()

    def _toggle_sort_dir() -> None:
        state['sort_dir'] = 'desc' if state['sort_dir'] == 'asc' else 'asc'
        try:
            dir_btn.configure(text=app._t('Auf') if state['sort_dir'] == 'asc' else app._t('Ab'))
        except Exception:
            pass
        _persist(); _render_list(); _refresh_sort_labels()

    try:
        dir_btn = ctk.CTkButton(
            sort_frame,
            text=(app._t('Auf') if state['sort_dir'] == 'asc' else app._t('Ab')),
            width=60, height=24,
            fg_color=ds_get_color(app, 'primary'),
            hover_color=ds_get_color(app, 'primary_hover'),
            text_color=ds_get_color(app, 'text_inverse'),
            command=_toggle_sort_dir,
        )
        dir_btn.pack(side='left', padx=(6, 0), pady=(2, 0))
    except Exception:
        dir_btn = None

    # Gruppierung
    grp_frame = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    grp_frame.pack(side='left', padx=spacing_lg)
    ctk.CTkLabel(
        grp_frame, text=app._t('Ansicht'), font=ctk.CTkFont(*get_font(app, 'caption')),
        text_color=ds_get_color(app, 'text_secondary')
    ).pack(anchor='w')
    try:
        grp_var = ctk.BooleanVar(value=bool(state.get('grouped', False)))

        def _on_grouped_change() -> None:
            state['grouped'] = bool(grp_var.get())
            # Checker Buttons sperren in grouped mode
            for b, _ in chk_buttons:
                try:
                    b.configure(state=('disabled' if state['grouped'] else 'normal'))
                except Exception:
                    pass
            _persist(); _rebuild_sort_buttons(); _render_list()

        grp_switch = ctk.CTkSwitch(grp_frame, text=app._t('Gruppierte Befunde'), command=_on_grouped_change, variable=grp_var)
        grp_switch.pack(anchor='w')
        # Apply initial grouped state to disable/enable checker buttons accordingly
        _on_grouped_change()
    except Exception:
        pass

    # Actions
    actions = ctk.CTkFrame(controls, fg_color=ds_get_color(app, 'transparent'))
    actions.pack(side='right')

    def _subset() -> List[Dict[str, Any]]:
        base = (findings_grouped if state.get('grouped') else findings) or []
        # severity
        sub = [f for f in base if (state['severity'] == 'ALL' or f.get('severity') == state['severity'])]
        # checker only for ungrouped
        if (not state.get('grouped')) and state['checker'] != 'ALL':
            sub = [f for f in sub if (f.get('checker') or '').lower() == state['checker']]
        # query
        if state['query']:
            q = state['query']
            sub = [f for f in sub if q in (f.get('message') or '').lower() or q in (f.get('rule_id') or f.get('rule') or '').lower()]
        # sort
        reverse = (state['sort_dir'] == 'desc')
        try:
            if state['sort'] == 'severity':
                order = {'critical': 0, 'major': 1, 'minor': 2, 'info': 3}
                sub = sorted(sub, key=lambda f: (order.get(f.get('severity') or 'info', 9), (f.get('rule_id') or f.get('rule') or ''), (f.get('message') or '')), reverse=reverse)
            elif state['sort'] == 'rule':
                sub = sorted(sub, key=lambda f: ((f.get('rule_id') or f.get('rule') or ''), (f.get('severity') or ''), (f.get('message') or '')), reverse=reverse)
            elif state['sort'] == 'count':
                sub = sorted(sub, key=lambda f: (f.get('count') or 0, (f.get('rule_id') or f.get('rule') or ''), (f.get('message') or '')), reverse=reverse)
            elif state['sort'] == 'confidence':
                def _conf_val(ff: Dict[str, Any]):
                    c = ff.get('confidence')
                    if c is None:
                        c = ff.get('avg_confidence') if isinstance(ff.get('avg_confidence'), (int, float, str)) else ff.get('avg_conf')
                    try:
                        if isinstance(c, str):
                            c = float(c)
                    except Exception:
                        pass
                    return c if isinstance(c, (int, float)) else -1
                sub = sorted(sub, key=lambda f: (_conf_val(f), (f.get('rule_id') or f.get('rule') or ''), (f.get('message') or '')), reverse=reverse)
            else:
                sub = sorted(sub, key=lambda f: ((f.get('message') or ''), (f.get('severity') or ''), (f.get('rule_id') or f.get('rule') or '')), reverse=reverse)
        except Exception:
            pass
        return sub

    def _copy_all() -> None:
        try:
            sub = _subset()
            lines = []
            if state.get('grouped'):
                for f in sub:
                    cnt = f.get('count') or 1
                    conf = f.get('confidence') if f.get('confidence') is not None else (f.get('avg_confidence') if isinstance(f.get('avg_confidence'), (int, float, str)) else f.get('avg_conf'))
                    try:
                        if isinstance(conf, str):
                            conf = float(conf)
                    except Exception:
                        pass
                    conf_txt = f" {app._t('Ø')} {conf:.2f}" if isinstance(conf, (int, float)) else ''
                    lines.append(f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'Regel')}: {(f.get('message') or '')} ×{cnt}{conf_txt}")
            else:
                lines = [f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}" for f in sub]
            blob = '\n'.join(lines)
            if getattr(app, 'root', None):
                app.root.clipboard_clear(); app.root.clipboard_append(blob)
            if hasattr(app, 'show_toast'):
                app.show_toast(app._t('Liste in die Zwischenablage kopiert'), 'success')
        except Exception:
            pass

    def _copy_critical() -> None:
        try:
            crit = [f for f in _subset() if f.get('severity') == 'critical']
            if not crit:
                if hasattr(app, 'show_toast'):
                    app.show_toast(app._t('Keine kritischen Einträge'), 'info')
                return
            blob = '\n'.join([f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}" for f in crit])
            if getattr(app, 'root', None):
                app.root.clipboard_clear(); app.root.clipboard_append(blob)
            if hasattr(app, 'show_toast'):
                app.show_toast(app._t('Kritische kopiert'), 'success')
        except Exception:
            pass

    def _export() -> None:
        try:
            filters = {'severity': state.get('severity'), 'query': state.get('query'), 'grouped': state.get('grouped', False)}
            export_findings(app, (_subset() if not state.get('grouped') else findings or []), (findings_grouped or []) if state.get('grouped') else None, filters)
            if hasattr(app, 'show_toast'):
                app.show_toast(app._t('Export erstellt'), 'success')
        except Exception:
            pass

    def _make_pkg() -> None:
        try:
            make_correction_package(app, _subset() if not state.get('grouped') else findings or [], (findings_grouped or []) if state.get('grouped') else None)
            if hasattr(app, 'show_toast'):
                app.show_toast(app._t('Korrekturpaket erstellt'), 'success')
        except Exception:
            pass

    try:
        ctk.CTkButton(actions, text=app._t('Kopieren'), width=70, height=26,
                      fg_color=ds_get_color(app, 'primary'), hover_color=ds_get_color(app, 'primary_hover'),
                      text_color=ds_get_color(app, 'text_inverse'), command=_copy_all).pack(side='left', padx=4)
        ctk.CTkButton(actions, text=app._t('Exportieren'), width=90, height=26,
                      fg_color=ds_get_color(app, 'secondary'), hover_color=ds_get_color(app, 'secondary_hover'),
                      text_color=ds_get_color(app, 'text_inverse'), command=_export).pack(side='left', padx=4)
        ctk.CTkButton(actions, text=app._t('Korrekturpaket erstellen'), width=160, height=26,
                      fg_color=ds_get_color(app, 'surface'), hover_color=ds_get_color(app, 'surface_hover'),
                      text_color=ds_get_color(app, 'text_primary'), command=_make_pkg).pack(side='left', padx=4)
        ctk.CTkButton(actions, text=app._t('Kritisch'), width=80, height=26,
                      fg_color=ds_get_color(app, 'error'), hover_color=ds_get_color(app, 'error_hover'),
                      text_color=ds_get_color(app, 'text_inverse'), command=_copy_critical).pack(side='left', padx=4)
    except Exception:
        pass

    # Kopfzeile der Liste
    try:
        header_h = 28
        list_header = ctk.CTkFrame(container, fg_color=ds_get_color(app, 'surface'), border_width=1, border_color=ds_get_color(app, 'surface_border'))
        list_header.pack(fill='x', pady=(6, 0))
        header_inner = ctk.CTkFrame(list_header, fg_color=ds_get_color(app, 'transparent'))
        header_inner.pack(fill='x')
        # Streifen
        ctk.CTkFrame(header_inner, width=6, height=header_h, fg_color=ds_get_color(app, 'transparent')).pack(side='left', fill='y')
        # Meta
        meta_hdr = ctk.CTkFrame(header_inner, width=160, height=header_h, fg_color=ds_get_color(app, 'transparent'))
        meta_hdr.pack_propagate(False)
        meta_hdr.pack(side='left', fill='y')
        meta_hdr_label = ctk.CTkLabel(meta_hdr, text=app._t('Regel'), font=ctk.CTkFont(*get_font(app, 'caption_bold')),
                                      text_color=ds_get_color(app, 'text_secondary'), anchor='w')
        meta_hdr_label.pack(fill='both', padx=6)
        # Nachricht
        msg_hdr = ctk.CTkFrame(header_inner, fg_color=ds_get_color(app, 'transparent'))
        msg_hdr.pack(side='left', fill='both', expand=True)
        ctk.CTkLabel(msg_hdr, text=app._t('Nachricht'), font=ctk.CTkFont(*get_font(app, 'caption_bold')),
                     text_color=ds_get_color(app, 'text_secondary'), anchor='w').pack(fill='both', padx=6)
        # Confidence
        conf_hdr = ctk.CTkFrame(header_inner, width=110, height=header_h, fg_color=ds_get_color(app, 'transparent'))
        conf_hdr.pack_propagate(False)
        conf_hdr.pack(side='right', fill='y')
        conf_hdr_label = ctk.CTkLabel(conf_hdr, text=app._t('Sicherheitswert'), font=ctk.CTkFont(*get_font(app, 'caption_bold')),
                                      text_color=ds_get_color(app, 'text_secondary'), anchor='e')
        conf_hdr_label.pack(fill='both', padx=6)
        # Tooltips
        tt = Tooltip(app)

        def _bind_header_tip(widget, text):
            if not widget:
                return
            def _on_enter(e):
                tt.show(widget, text, e.x_root, e.y_root)
            def _on_leave(_e):
                tt.hide()
            widget.bind('<Enter>', _on_enter)
            widget.bind('<Leave>', _on_leave)

        _bind_header_tip(meta_hdr_label, app._t('Regel (intern über Prüfer-Module ermittelt)'))
        _bind_header_tip(conf_hdr_label, app._t('Sicherheitswert (0–1) – Verlässlichkeit des Befunds, 1 = sehr sicher'))
    except Exception:
        pass

    # Scrollbereich
    list_wrap = ctk.CTkScrollableFrame(container, fg_color=ds_get_color(app, 'surface'))
    list_wrap.pack(fill='both', expand=True, pady=(spacing_md, 0))
    inner_holder = list_wrap

    rendered: Dict[int, Tuple[Any, Any]] = {}
    current_subset: List[Dict[str, Any]] = []

    def _row_base_color(index: int) -> str:
        try:
            return ds_get_color(app, 'surface_hover') if (index % 2 == 1) else ds_get_color(app, 'transparent')
        except Exception:
            return ds_get_color(app, 'transparent')

    def _highlight() -> None:
        for idx, (frm, lbl) in list(rendered.items()):
            try:
                base = getattr(frm, '_base_fg', None)
                frm.configure(fg_color=base if isinstance(base, str) else _row_base_color(idx))
            except Exception:
                pass

    # No manual scrollregion needed with CTkScrollableFrame

    def _debounce_wrap(lbl):
        try:
            def _apply():
                try:
                    w = lbl.winfo_width()
                    if w > 0:
                        lbl.configure(wraplength=int(w * 0.97))
                except Exception:
                    pass
            if getattr(app, 'root', None):
                app.root.after(60, _apply)
            else:
                _apply()
        except Exception:
            pass

    def _create_row(parent_row, idx: int, f: Dict[str, Any]):
        sev = f.get('severity') or 'info'
        base_fg = _row_base_color(idx)
        row = ctk.CTkFrame(parent_row, fg_color=base_fg)
        try:
            row._base_fg = base_fg  # type: ignore[attr-defined]
        except Exception:
            pass
        row.pack(fill='x')
        # Streifen links
        ctk.CTkFrame(row, width=6, fg_color=ds_get_color(app, {'critical': 'error', 'major': 'warning', 'minor': 'info'}.get(sev, 'text_primary'))).pack(side='left', fill='y')
        # Meta-Spalte
        meta_fr = ctk.CTkFrame(row, width=160, fg_color=ds_get_color(app, 'transparent'))
        meta_fr.pack_propagate(False)
        meta_fr.pack(side='left', fill='y')
        rule_txt = (f.get('rule_id') or f.get('rule') or '')
        checker_txt = (f.get('checker') or '')
        ctk.CTkLabel(meta_fr, text=rule_txt, anchor='w', font=ctk.CTkFont(*get_font(app, 'caption_bold')),
                     text_color=ds_get_color(app, 'text_primary')).pack(fill='x', padx=6, pady=(4, 0))
        ctk.CTkLabel(meta_fr, text=checker_txt, anchor='w', font=ctk.CTkFont(*get_font(app, 'caption')),
                     text_color=ds_get_color(app, 'text_secondary')).pack(fill='x', padx=6)
        # Nachricht
        txt = (f.get('message') or '')
        lbl = ctk.CTkLabel(row, text=txt, anchor='w', justify='left', font=ctk.CTkFont(*get_font(app, 'body')),
                           text_color=ds_get_color(app, {'critical': 'error', 'major': 'warning', 'minor': 'info'}.get(sev, 'text_primary')))
        lbl.pack(side='left', fill='both', expand=True, padx=spacing_md, pady=2)
        lbl.bind('<Configure>', lambda e: _debounce_wrap(lbl))
        rendered[idx] = (row, lbl)
        return row

    def _render_list() -> None:
        for idx, (frm, lbl) in list(rendered.items()):
            try:
                frm.destroy()
            except Exception:
                pass
        rendered.clear()
        nonlocal current_subset
        current_subset = _subset()
        for w in inner_holder.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        if not current_subset:
            ctk.CTkLabel(inner_holder, text=app._t('Keine Ergebnisse'), font=ctk.CTkFont(*get_font(app, 'body')),
                         text_color=ds_get_color(app, 'text_secondary')).pack(fill='x')
            return
        for idx, f in enumerate(current_subset):
            _create_row(inner_holder, idx, f)
        _highlight()

    # Events
    # No-op bindings; CTkScrollableFrame manages scrolling
    pass

    # Aktionen am Ende initialisieren
    _render_list()
    # Apply initial filters to UI controls
    _set_severity(state['severity']); _set_checker(state['checker']); _set_sort(state['sort'])
    try:
        if state.get('query') and 'query_var' in locals():
            query_var.set(state['query'])
    except Exception:
        pass
