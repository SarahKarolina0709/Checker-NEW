# -*- coding: utf-8 -*-
"""UI-Render-Funktionen fuer Findings.

Closures aus index_page() werden via `ctx` (SimpleNamespace) uebergeben:
  ctx.s                    Per-Session-State (Dict)
  ctx.refs                 UI-Element-Refs (Dict)
  ctx.selected_idx         {'v': int} — aktuell selektierter Finding-Index
  ctx.toggle_checked       Callable(idx, val) — Geprueft-Status setzen
  ctx.refresh_results      Callable() — Ergebnisbereich neu rendern
"""
from __future__ import annotations

import os
from types import SimpleNamespace

from nicegui import ui

from nicegui_app.utils import copy_to_clipboard, html_esc


def render_finding_card(ctx: SimpleNamespace, idx: int, f) -> None:
    """Rendert eine Finding-Karte (normal- oder kompakt-Modus).

    Muss innerhalb eines NiceGUI-Containers aufgerufen werden.
    """
    # Lazy-Import um Zirkel-Importe mit main.py zu vermeiden
    from nicegui_app.severity import (
        severity_label, severity_color, phase_from_code,
    )
    s = ctx.s
    refs = ctx.refs
    selected_idx = ctx.selected_idx

    sev_lbl = severity_label(f.severity)
    sev_clr = severity_color(f.severity)
    phase_lbl = phase_from_code(f.code)
    is_selected = idx == selected_idx['v']
    compact = s.get('view_mode', 'normal') == 'compact'
    pad = '6px 10px' if compact else '12px'
    mb = '4px' if compact else '8px'
    card_style = (
        f'border-left:5px solid {sev_clr};border-radius:6px;'
        f'margin-bottom:{mb};padding:0;background:white;'
        f'border-top:1px solid #e5e7eb;border-right:1px solid #e5e7eb;'
        f'border-bottom:1px solid #e5e7eb;'
        f'{"box-shadow:0 0 0 2px #0f2744;" if is_selected else ""}'
    )
    with ui.card().classes('w-full').props('flat').style(card_style) as card_el:
        try:
            card_el.props(f'id=finding-card-{idx}')
        except Exception:
            pass
        with ui.column().classes('w-full gap-1').style(f'padding:{pad};'):
            src_f = getattr(f, 'source_file', '') or ''
            tgt_f = getattr(f, 'target_file', '') or ''
            if (src_f or tgt_f) and not compact:
                with ui.row().classes('w-full items-center gap-2 cursor-pointer').style(
                    'padding:2px 6px;background:#f1f5f9;border-radius:4px;'
                    'margin-bottom:4px;font-size:11px;'
                ).on('click', lambda _, sf=os.path.basename(src_f or tgt_f):
                     (s.update({'search_text': sf}),
                      refs.get('search_input') and refs['search_input'].set_value(sf),
                      ctx.refresh_results())):
                    ui.icon('description', size='xs').style('color:var(--text-muted);')
                    if src_f:
                        ui.label(os.path.basename(src_f)).style(
                            'color:var(--primary);font-weight:600;')
                    if src_f and tgt_f:
                        ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
                    if tgt_f:
                        ui.label(os.path.basename(tgt_f)).style(
                            'color:var(--success);font-weight:600;')
            with ui.row().classes('w-full items-center gap-2 flex-wrap'):
                ui.badge(sev_lbl).style(
                    f'background:transparent;color:{sev_clr};border:1px solid {sev_clr};border-radius:20px;')
                if phase_lbl and not compact:
                    ui.badge(phase_lbl).style(
                        'background:transparent;color:var(--text-muted);border:1px solid #d1d5db;border-radius:20px;')
                ui.badge(f.code).style(
                    'background:transparent;color:var(--text-muted);border:1px solid #d1d5db;border-radius:20px;')
                diff = s.get('analysis_diff', {}) or {}
                if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
                    ui.badge('NEU').style(
                        'background:#dc2626;color:white;border-radius:20px;'
                        'font-weight:700;font-size:11px;')
                ui.element('div').classes('flex-grow')
                cb = ui.checkbox('Geprueft',
                    value=s.get('checked_findings', {}).get(str(idx), False),
                    on_change=lambda e, i=idx: ctx.toggle_checked(
                        i, getattr(e, 'value', getattr(e, 'args', False))))
                cb.style('font-size:12px;')
            msg_fs = '12px' if compact else '13px'
            msg_text = (f.message[:120] + '…' if compact and len(f.message) > 120
                        else f.message)
            ui.label(msg_text).style(
                f'font-size:{msg_fs};color:var(--text);line-height:1.4;font-weight:500;')
            if compact:
                return
            meta = getattr(f, 'meta', {}) or {}
            suggestion = (meta.get('suggestion') or '').strip()
            if suggestion:
                with ui.row().classes('w-full items-start gap-2').style(
                    'background:#ecfdf5;border-left:3px solid #16a34a;'
                    'padding:8px 10px;border-radius:6px;margin-top:6px;'
                ):
                    ui.icon('lightbulb', size='sm').style('color:var(--success);flex-shrink:0;margin-top:1px;')
                    with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                        ui.label('Vorschlag').style(
                            'font-size:11px;font-weight:700;color:var(--success);'
                            'text-transform:uppercase;letter-spacing:0.5px;')
                        ui.label(suggestion[:500]).style(
                            'font-size:12px;color:#064e3b;'
                            'white-space:pre-wrap;word-break:break-word;')
                    ui.button(icon='content_copy',
                        on_click=lambda _, t=suggestion: copy_to_clipboard(t)
                    ).props('flat dense round size=xs').tooltip(
                        'Vorschlag kopieren'
                    ).style('color:var(--success);flex-shrink:0;')
            if f.source_text or f.target_text:
                error_span = (meta.get('error_text') or '').strip()
                with ui.column().classes('w-full gap-1').style('margin-top:6px;'):
                    if f.source_text:
                        with ui.row().classes('w-full items-start gap-1').style(
                            'background:#f8fafc;padding:6px 8px;border-radius:6px;'
                            'border-left:2px solid #0f2744;'
                        ):
                            ui.label('SRC').style(
                                'font-size:11px;font-weight:700;color:var(--primary);'
                                'min-width:30px;padding-top:1px;')
                            ui.label(f.source_text[:400]).style(
                                'font-size:12px;color:#334155;'
                                'white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                            ui.button(icon='content_copy',
                                on_click=lambda _, t=f.source_text: copy_to_clipboard(t)
                            ).props('flat dense round size=xs').tooltip(
                                'Quelltext kopieren'
                            ).style('color:#94a3b8;flex-shrink:0;')
                    if f.target_text:
                        with ui.row().classes('w-full items-start gap-1').style(
                            'background:#fef3c7;padding:6px 8px;border-radius:6px;'
                            'border-left:2px solid #d97706;'
                        ):
                            ui.label('ZIEL').style(
                                'font-size:11px;font-weight:700;color:var(--warning);'
                                'min-width:30px;padding-top:1px;')
                            if error_span and error_span in f.target_text:
                                pos = f.target_text.find(error_span)
                                before = f.target_text[:pos][:200]
                                after = f.target_text[pos + len(error_span):][:200]
                                ui.html(
                                    f'<span style="font-size:12px;color:#334155;'
                                    f'white-space:pre-wrap;word-break:break-word;">'
                                    f'{html_esc(before)}'
                                    f'<mark style="background:#fecaca;color:#7f1d1d;'
                                    f'padding:1px 3px;border-radius:3px;font-weight:700;">'
                                    f'{html_esc(error_span)}</mark>'
                                    f'{html_esc(after)}</span>'
                                ).classes('flex-grow')
                            else:
                                ui.label(f.target_text[:400]).style(
                                    'font-size:12px;color:#334155;'
                                    'white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                            ui.button(icon='content_copy',
                                on_click=lambda _, t=f.target_text: copy_to_clipboard(t)
                            ).props('flat dense round size=xs').tooltip(
                                'Zieltext kopieren'
                            ).style('color:#94a3b8;flex-shrink:0;')


def render_split_list(ctx: SimpleNamespace, filtered) -> None:
    """Linke Spalte im Split-Modus: kompakte Karten ohne Texte.

    ctx braucht: s, selected_idx, select_finding(idx).
    """
    from nicegui_app.severity import severity_label, severity_color
    s = ctx.s
    selected_idx = ctx.selected_idx
    _SEV_ORDER = [('Kritisch', '#dc2626'), ('Wichtig', '#ea580c'), ('Hinweis', '#6b7280')]
    _sev_counts = {lbl: sum(1 for _, f in filtered if severity_label(f.severity) == lbl)
                   for lbl, _ in _SEV_ORDER}
    _last_sev = None
    _show_headers = s.get('sort_mode', 'default') in ('default', 'severity')
    for real_idx, f in filtered:
        sev_lbl = severity_label(f.severity)
        sev_clr = severity_color(f.severity)
        is_sel = real_idx == selected_idx['v']
        if _show_headers and sev_lbl != _last_sev and _sev_counts.get(sev_lbl, 0) > 0:
            _last_sev = sev_lbl
            clr = next((c for l, c in _SEV_ORDER if l == sev_lbl), '#9ca3af')
            with ui.row().classes('w-full items-center gap-2').style('padding:4px 2px 2px;'):
                ui.element('div').style(
                    f'height:2px;width:10px;border-radius:2px;background:{clr};')
                ui.label(f'{sev_lbl}  ({_sev_counts[sev_lbl]})').style(
                    f'font-size:11px;font-weight:700;color:{clr};'
                    f'text-transform:uppercase;letter-spacing:0.6px;')
                ui.element('div').style(
                    f'flex-grow:1;height:1px;background:{clr};opacity:.2;')
        row_bg = '#eff6ff' if is_sel else 'white'
        with ui.row().classes('w-full items-start cursor-pointer').style(
            f'padding:6px 8px;border-left:4px solid {sev_clr};'
            f'background:{row_bg};border-radius:4px;margin-bottom:3px;'
            f'{"box-shadow:0 0 0 1px #0f2744;" if is_sel else ""}'
        ).on('click', lambda _, i=real_idx: ctx.select_finding(i)):
            with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                ui.label(f.message[:80] + ('…' if len(f.message) > 80 else '')).style(
                    'font-size:11px;color:var(--text);line-height:1.35;font-weight:500;')
                ui.badge(f.code).style(
                    'background:transparent;color:var(--text-light);border:none;'
                    'font-size:11px;padding:0;')
        checked = s.get('checked_findings', {}).get(str(real_idx), False)
        if checked:
            ui.icon('check_circle', size='xs').style(
                'color:var(--success);position:absolute;right:6px;top:6px;')


def render_detail_panel(ctx: SimpleNamespace) -> None:
    """Rechtes Detail-Panel im Split-Modus.

    ctx braucht: s, refs, selected_idx, toggle_checked, dict_to_finding.
    """
    from nicegui_app.severity import severity_label, severity_color, phase_from_code
    s = ctx.s
    selected_idx = ctx.selected_idx
    idx = selected_idx['v']
    if idx < 0:
        with ui.column().classes('w-full items-center justify-center').style('padding:32px;'):
            ui.icon('touch_app', size='3rem').style('color:var(--text-light);')
            ui.label('Finding auswählen').style('font-size:14px;color:var(--text-light);margin-top:8px;')
            ui.label('Klicke links auf ein Finding für Details').style(
                'font-size:12px;color:var(--text-light);')
        return
    findings = s.get('findings', [])
    if idx >= len(findings):
        return
    f = ctx.dict_to_finding(findings[idx])
    sev_lbl = severity_label(f.severity)
    sev_clr = severity_color(f.severity)
    phase_lbl = phase_from_code(f.code)
    meta = getattr(f, 'meta', {}) or {}
    suggestion = (meta.get('suggestion') or '').strip()
    error_span = (meta.get('error_text') or '').strip()
    with ui.row().classes('w-full items-center gap-2 flex-wrap').style('margin-bottom:8px;'):
        ui.badge(sev_lbl).style(
            f'background:{sev_clr};color:white;border-radius:20px;font-size:12px;')
        if phase_lbl:
            ui.badge(phase_lbl).style(
                'background:transparent;color:var(--text-muted);border:1px solid #d1d5db;border-radius:20px;')
        ui.badge(f.code).style(
            'background:transparent;color:var(--text-muted);border:1px solid #d1d5db;border-radius:20px;')
        diff = s.get('analysis_diff', {}) or {}
        if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
            ui.badge('NEU').style(
                'background:#dc2626;color:white;border-radius:20px;font-weight:700;font-size:11px;')
        ui.element('div').classes('flex-grow')
        cb = ui.checkbox('Geprüft',
            value=bool(s.get('checked_findings', {}).get(str(idx), False)),
            on_change=lambda e, i=idx: ctx.toggle_checked(i, getattr(e, 'value', getattr(e, 'args', False))))
        cb.style('font-size:13px;')
    src_f = getattr(f, 'source_file', '') or ''
    tgt_f = getattr(f, 'target_file', '') or ''
    if src_f or tgt_f:
        with ui.row().classes('items-center gap-1').style(
            'padding:4px 8px;background:#f1f5f9;border-radius:4px;margin-bottom:8px;'
        ):
            ui.icon('description', size='xs').style('color:var(--text-muted);')
            if src_f:
                ui.label(os.path.basename(src_f)).style(
                    'font-size:11px;color:var(--primary);font-weight:600;')
            if src_f and tgt_f:
                ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
            if tgt_f:
                ui.label(os.path.basename(tgt_f)).style(
                    'font-size:11px;color:var(--success);font-weight:600;')
    ui.label(f.message).style(
        'font-size:14px;color:var(--text);line-height:1.5;font-weight:500;margin-bottom:8px;')
    if suggestion:
        with ui.row().classes('w-full items-start gap-2').style(
            'background:#ecfdf5;border-left:3px solid #16a34a;'
            'padding:8px 10px;border-radius:6px;margin-bottom:8px;'
        ):
            ui.icon('lightbulb', size='sm').style('color:var(--success);flex-shrink:0;')
            with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                ui.label('Vorschlag').style(
                    'font-size:11px;font-weight:700;color:var(--success);'
                    'text-transform:uppercase;letter-spacing:0.5px;')
                ui.label(suggestion).style(
                    'font-size:13px;color:#064e3b;white-space:pre-wrap;word-break:break-word;')
            ui.button(icon='content_copy',
                on_click=lambda _, t=suggestion: copy_to_clipboard(t)
            ).props('flat dense round size=xs').tooltip('Vorschlag kopieren').style('color:var(--success);')
    if f.source_text:
        with ui.column().classes('w-full gap-0').style('margin-bottom:6px;'):
            ui.label('Quelltext').style('font-size:11px;font-weight:700;color:var(--primary);'
                'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:2px;')
            with ui.row().classes('w-full items-start gap-1').style(
                'background:#f8fafc;padding:8px;border-radius:6px;border-left:3px solid #0f2744;'
            ):
                ui.label(f.source_text[:800]).style(
                    'font-size:12px;color:#334155;white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                ui.button(icon='content_copy',
                    on_click=lambda _, t=f.source_text: copy_to_clipboard(t)
                ).props('flat dense round size=xs').style('color:#94a3b8;flex-shrink:0;')
    if f.target_text:
        with ui.column().classes('w-full gap-0'):
            ui.label('Zieltext').style('font-size:11px;font-weight:700;color:var(--warning);'
                'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:2px;')
            with ui.row().classes('w-full items-start gap-1').style(
                'background:#fef3c7;padding:8px;border-radius:6px;border-left:3px solid #d97706;'
            ):
                if error_span and error_span in f.target_text:
                    pos = f.target_text.find(error_span)
                    before = f.target_text[:pos][:400]
                    after = f.target_text[pos + len(error_span):][:400]
                    ui.html(
                        f'<span style="font-size:12px;color:#334155;'
                        f'white-space:pre-wrap;word-break:break-word;">'
                        f'{html_esc(before)}'
                        f'<mark style="background:#fecaca;color:#7f1d1d;'
                        f'padding:1px 3px;border-radius:3px;font-weight:700;">'
                        f'{html_esc(error_span)}</mark>'
                        f'{html_esc(after)}</span>'
                    ).classes('flex-grow')
                else:
                    ui.label(f.target_text[:800]).style(
                        'font-size:12px;color:#334155;white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                ui.button(icon='content_copy',
                    on_click=lambda _, t=f.target_text: copy_to_clipboard(t)
                ).props('flat dense round size=xs').style('color:#94a3b8;flex-shrink:0;')


def render_findings_list(ctx: SimpleNamespace) -> None:
    """Orchestriert den Findings-Bereich (Welcome / Empty / Split / Normal-Modus).

    ctx braucht: s, refs, filtered_findings(), render_welcome(),
    render_split_list(filtered), render_detail_panel(), render_finding_card(idx, f).
    """
    from nicegui_app.severity import severity_label
    s = ctx.s
    refs = ctx.refs
    container = refs['findings_container']
    if not container:
        return
    container.clear()
    current_score = s.get('current_score', -1)
    filtered = ctx.filtered_findings()
    split_mode = s.get('view_mode', 'normal') == 'split'
    refs['detail_panel'] = None  # reset for this render
    with container:
        if current_score < 0:
            ctx.render_welcome()
            return
        if not filtered:
            ui.label('Keine Findings in diesem Filter').style(
                'font-size:12px;color:var(--text-light);padding:16px 0;text-align:center;')
            return
        if split_mode:
            with ui.row().classes('w-full gap-0 items-start').style('min-height:300px;'):
                list_col = ui.column().classes('gap-0').style(
                    'width:340px;min-width:300px;flex-shrink:0;'
                    'overflow-y:auto;max-height:calc(100vh - 420px);'
                    'border-right:1px solid #e5e7eb;padding-right:8px;'
                )
                detail_col = ui.column().classes('flex-grow gap-2').style(
                    'padding-left:12px;overflow-y:auto;'
                    'max-height:calc(100vh - 420px);'
                )
                refs['detail_panel'] = detail_col
                with list_col:
                    ctx.render_split_list(filtered)
                with detail_col:
                    ctx.render_detail_panel()
        else:
            _SEV_ORDER = [('Kritisch', '#dc2626'), ('Wichtig', '#ea580c'), ('Hinweis', '#6b7280')]
            _sev_counts = {lbl: sum(1 for _, f in filtered if severity_label(f.severity) == lbl)
                           for lbl, _ in _SEV_ORDER}
            _last_sev_group = None
            _show_sev_headers = s.get('sort_mode', 'default') in ('default', 'severity')
            for real_idx, f in filtered:
                sev_lbl = severity_label(f.severity)
                if _show_sev_headers and sev_lbl != _last_sev_group and _sev_counts.get(sev_lbl, 0) > 0:
                    _last_sev_group = sev_lbl
                    clr = next((c for l, c in _SEV_ORDER if l == sev_lbl), '#9ca3af')
                    cnt = _sev_counts[sev_lbl]
                    with ui.row().classes('w-full items-center gap-2').style(
                        'padding:6px 4px 4px;margin-top:4px;'
                    ):
                        ui.element('div').style(
                            f'height:2px;width:12px;border-radius:2px;'
                            f'background:{clr};flex-shrink:0;'
                        )
                        ui.label(f'{sev_lbl}  ({cnt})').style(
                            f'font-size:11px;font-weight:700;color:{clr};'
                            f'text-transform:uppercase;letter-spacing:0.8px;'
                        )
                        ui.element('div').style(
                            f'flex-grow:1;height:1px;background:{clr};opacity:.2;'
                        )
                ctx.render_finding_card(real_idx, f)


def render_welcome(ctx: SimpleNamespace) -> None:
    """Welcome-/Customer-/Files-Bildschirm.

    ctx braucht: s, load_customer_info, list_projects, display_name,
    find_source_folder, find_translation_folder, list_files_in_folder,
    get_project_path, get_customer_path, count_files_in_folder,
    scan_project_dates, on_customer_selected, select_auftrag.
    """
    from datetime import datetime
    from nicegui_app.text_extraction import extract_text
    s = ctx.s
    customer = s.get('active_customer', '')
    src_files = s.get('source_files', [])
    tgt_files = s.get('translation_files', [])
    has_files = bool(src_files or tgt_files)

    if has_files:
        # --- Zustand 3: Dateien geladen -> Textvorschau ---
        with ui.column().classes('w-full gap-4'):
            ui.label('Textvorschau').style('font-size:16px;font-weight:700;color:var(--text);')
            with ui.row().classes('w-full gap-4').style('min-height:200px;'):
                with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                    ui.label('Ausgangstext').style(
                        'font-size:12px;font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:1px;')
                    if src_files:
                        for fp in src_files[:3]:
                            ui.label(os.path.basename(fp)).style('font-size:12px;font-weight:600;color:var(--text);')
                            try:
                                text = extract_text(fp)[:500] if os.path.exists(fp) else ''
                                if text:
                                    ui.label(text).style(
                                        'font-size:12px;color:var(--text-muted);white-space:pre-wrap;'
                                        'max-height:150px;overflow:hidden;line-height:1.5;')
                            except Exception:
                                ui.label('Vorschau nicht verfügbar').style('font-size:12px;color:var(--text-light);')
                            ui.separator().style('margin:4px 0;')
                    else:
                        ui.label('Keine Ausgangstexte').style('font-size:12px;color:var(--text-light);')

                with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                    ui.label('Übersetzung').style(
                        'font-size:12px;font-weight:700;color:var(--success);text-transform:uppercase;letter-spacing:1px;')
                    if tgt_files:
                        for fp in tgt_files[:3]:
                            ui.label(os.path.basename(fp)).style('font-size:12px;font-weight:600;color:var(--text);')
                            try:
                                text = extract_text(fp)[:500] if os.path.exists(fp) else ''
                                if text:
                                    ui.label(text).style(
                                        'font-size:12px;color:var(--text-muted);white-space:pre-wrap;'
                                        'max-height:150px;overflow:hidden;line-height:1.5;')
                            except Exception:
                                ui.label('Vorschau nicht verfügbar').style('font-size:12px;color:var(--text-light);')
                            ui.separator().style('margin:4px 0;')
                    else:
                        ui.label('Keine Übersetzungen').style('font-size:12px;color:var(--text-light);')

            pairs = s.get('paired_results', [])
            if pairs:
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;'):
                    ui.label(f'{len(pairs)} {"Paar" if len(pairs) == 1 else "Paare"} erkannt').style(
                        'font-size:13px;font-weight:600;color:var(--primary);')
                    for p in pairs[:5]:
                        src_name = os.path.basename(p.get('source', ''))
                        tgt_name = os.path.basename(p.get('translation', ''))
                        with ui.row().classes('w-full items-center gap-2').style('padding:4px 0;'):
                            ui.icon('description', size='xs').style('color:var(--text-muted);')
                            ui.label(src_name).style('font-size:12px;color:var(--text);')
                            ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
                            ui.label(tgt_name).style('font-size:12px;color:var(--text);')

    elif customer:
        # --- Zustand 2: Kunde gewaehlt, keine Dateien ---
        info = ctx.load_customer_info(customer)
        projects = ctx.list_projects(customer)
        with ui.column().classes('w-full items-center').style('padding:32px 0;gap:16px;'):
            ui.icon('business' if info.get('typ') == 'firma' else 'person', size='3rem').style('color:var(--accent);')
            ui.label(ctx.display_name(customer)).style('font-size:18px;font-weight:700;color:var(--text);')
            proj_path = s.get('active_project_path', '')
            if proj_path:
                proj_name = os.path.basename(proj_path)
                display = proj_name
                try:
                    date_part = proj_name.split('_')[0]
                    d = datetime.strptime(date_part, '%Y-%m-%d')
                    display = d.strftime('%d.%m.%Y')
                    rest = proj_name[len(date_part)+1:]
                    if rest and rest != customer:
                        display += f' — {ctx.display_name(rest)}'
                except Exception:
                    pass
                with ui.row().classes('items-center gap-2').style(
                    'background:#eff6ff;padding:6px 16px;border-radius:20px;margin-top:4px;'):
                    ui.icon('folder_open', size='xs').style('color:var(--primary);')
                    ui.label(f'Projekt: {display}').style('font-size:13px;font-weight:600;color:var(--primary);')
            if info.get('email') or info.get('telefon'):
                with ui.row().classes('gap-4').style('margin-top:4px;'):
                    if info.get('email'):
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('email', size='xs').style('color:var(--text-light);')
                            ui.label(info['email']).style('font-size:12px;color:var(--text-muted);')
                    if info.get('telefon'):
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('phone', size='xs').style('color:var(--text-light);')
                            ui.label(info['telefon']).style('font-size:12px;color:var(--text-muted);')
            with ui.row().classes('gap-6').style('margin-top:8px;'):
                with ui.column().classes('items-center'):
                    ui.label(str(len(projects))).style('font-size:24px;font-weight:800;color:var(--primary);')
                    ui.label('Projekte').style('font-size:12px;color:var(--text-light);')
                n_src = len(s.get('source_files', []))
                n_tgt = len(s.get('translation_files', []))
                with ui.column().classes('items-center'):
                    ui.label(str(n_src)).style('font-size:24px;font-weight:800;color:var(--primary);')
                    ui.label('Ausgangstexte').style('font-size:12px;color:var(--text-light);')
                with ui.column().classes('items-center'):
                    ui.label(str(n_tgt)).style('font-size:24px;font-weight:800;color:var(--success);')
                    ui.label('Übersetzungen').style('font-size:12px;color:var(--text-light);')
            if not proj_path:
                ui.label('Wählen Sie ein Projekt und laden Sie Dateien hoch').style(
                    'font-size:12px;color:var(--text-light);margin-top:12px;')
            elif proj_path and os.path.isdir(proj_path):
                src_dir = ctx.find_source_folder(proj_path)
                tgt_dir = ctx.find_translation_folder(proj_path)
                src_files_list = ctx.list_files_in_folder(src_dir) if src_dir else []
                tgt_files_list = ctx.list_files_in_folder(tgt_dir) if tgt_dir else []

                if src_files_list or tgt_files_list:
                    with ui.row().classes('w-full gap-4').style('margin-top:16px;'):
                        with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                            with ui.row().classes('items-center gap-2').style('margin-bottom:8px;'):
                                ui.element('div').style('width:4px;height:16px;border-radius:2px;background:#0f2744;')
                                ui.label(f'Ausgangstexte ({len(src_files_list)})').style(
                                    'font-size:13px;font-weight:700;color:var(--primary);')
                            if src_files_list:
                                for fp in src_files_list:
                                    fname = os.path.basename(fp)
                                    fsize = os.path.getsize(fp) if os.path.exists(fp) else 0
                                    with ui.row().classes('w-full items-center gap-2').style(
                                        'padding:4px 0;border-bottom:1px solid #f1f5f9;'):
                                        ui.icon('description', size='xs').style('color:var(--text-muted);')
                                        ui.label(fname).style(
                                            'font-size:12px;color:var(--text);flex-grow:1;'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                        ui.label(f'{fsize/1024:.0f} KB').style('font-size:12px;color:var(--text-light);')
                            else:
                                ui.label('Keine Dateien').style('font-size:12px;color:var(--text-light);')

                        with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                            with ui.row().classes('items-center gap-2').style('margin-bottom:8px;'):
                                ui.element('div').style('width:4px;height:16px;border-radius:2px;background:#16a34a;')
                                ui.label(f'Übersetzungen ({len(tgt_files_list)})').style(
                                    'font-size:13px;font-weight:700;color:var(--success);')
                            if tgt_files_list:
                                for fp in tgt_files_list:
                                    fname = os.path.basename(fp)
                                    fsize = os.path.getsize(fp) if os.path.exists(fp) else 0
                                    with ui.row().classes('w-full items-center gap-2').style(
                                        'padding:4px 0;border-bottom:1px solid #f1f5f9;'):
                                        ui.icon('translate', size='xs').style('color:var(--text-muted);')
                                        ui.label(fname).style(
                                            'font-size:12px;color:var(--text);flex-grow:1;'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                        ui.label(f'{fsize/1024:.0f} KB').style('font-size:12px;color:var(--text-light);')
                            else:
                                ui.label('Keine Dateien').style('font-size:12px;color:var(--text-light);')
                else:
                    ui.label('Projekt ist leer — laden Sie Dateien über die Ordner links hoch').style(
                        'font-size:12px;color:var(--text-light);margin-top:12px;')

            if len(projects) > 1:
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;margin-top:12px;'):
                    ui.label(f'Alle Projekte von {ctx.display_name(customer)}').style(
                        'font-size:13px;font-weight:700;color:var(--text);margin-bottom:8px;')
                    for proj in projects[:8]:
                        pp = ctx.get_project_path(customer, proj) or os.path.join(ctx.get_customer_path(customer), proj)
                        n_s = ctx.count_files_in_folder(ctx.find_source_folder(pp) or '')
                        n_t = ctx.count_files_in_folder(ctx.find_translation_folder(pp) or '')
                        is_active = pp == proj_path
                        display = proj
                        try:
                            d = datetime.strptime(proj.split('_')[0], '%Y-%m-%d')
                            display = d.strftime('%d.%m.%Y')
                            rest = proj[11:] if len(proj) > 10 else ''
                            if rest and rest != customer:
                                display += f' — {ctx.display_name(rest)}'
                        except Exception:
                            pass
                        with ui.row().classes('w-full items-center gap-3 cursor-pointer').style(
                            f'padding:6px 8px;border-radius:6px;'
                            f'{"background:#eff6ff;border:1px solid #93c5fd;" if is_active else "border:1px solid transparent;"}'
                        ).on('click', lambda _, p=proj, pp2=pp, ns=n_s, nt=n_t:
                             ctx.select_auftrag(p, pp2, ns, nt)):
                            ui.icon('folder', size='xs').style(
                                f'color:{"#0f2744" if is_active else "#d4af37"};')
                            ui.label(display).style(
                                f'font-size:12px;{"font-weight:700;color:var(--primary);" if is_active else "color:var(--text);"}flex-grow:1;')
                            if n_s or n_t:
                                ui.label(f'{n_s}Q · {n_t}Ü').style('font-size:12px;color:var(--text-muted);')

    else:
        # --- Zustand 1: Kein Kunde -> Welcome + Mini-Kalender ---
        with ui.column().classes('w-full items-center').style('padding:32px 0;gap:20px;'):
            ui.icon('translate', size='3rem').style('color:var(--text-light)')
            ui.label('Übersetzungsqualität prüfen').classes('t-title').style('color:var(--text);')
            with ui.column().style('gap:8px;margin-top:4px;'):
                for num, text in [('1', 'Kunde wählen (links)'),
                                   ('2', 'Ausgangstext + Übersetzung hochladen'),
                                   ('3', 'Analyse starten')]:
                    with ui.row().classes('items-center gap-2'):
                        ui.badge(num).style('background:#0f2744;color:white;border-radius:20px;')
                        ui.label(text).style('font-size:13px;color:var(--text-muted);')

        all_dates = ctx.scan_project_dates()
        if all_dates:
            with ui.card().classes('w-full').props('flat bordered').style('padding:16px;margin-top:8px;'):
                ui.label('Letzte Projekte').style('font-size:14px;font-weight:700;color:var(--text);margin-bottom:12px;')
                sorted_dates = sorted(all_dates.keys(), reverse=True)[:10]
                for day_str in sorted_dates:
                    customers_on_day = all_dates[day_str]
                    try:
                        display_date = datetime.strptime(day_str, '%Y-%m-%d').strftime('%d.%m.%Y')
                    except Exception:
                        display_date = day_str
                    with ui.row().classes('w-full items-start gap-3').style(
                        'padding:6px 0;border-bottom:1px solid #f1f5f9;'):
                        with ui.element('div').style('min-width:70px;text-align:center;'):
                            ui.label(display_date).style('font-size:12px;font-weight:700;color:var(--primary);')
                        with ui.column().classes('gap-1 flex-grow'):
                            for cust in customers_on_day[:3]:
                                with ui.row().classes('items-center gap-2 cursor-pointer').on(
                                    'click', lambda _, c=cust: ctx.on_customer_selected(c)):
                                    ui.element('div').style(
                                        'width:24px;height:24px;border-radius:6px;'
                                        'background:linear-gradient(135deg,#0f2744,#1a365d);'
                                        'display:flex;align-items:center;justify-content:center;'
                                        'font-size:12px;font-weight:700;color:var(--accent);'
                                    )
                                    ui.label(ctx.display_name(cust)).style(
                                        'font-size:12px;color:var(--text);cursor:pointer;')
                            if len(customers_on_day) > 3:
                                ui.label(f'+{len(customers_on_day)-3} weitere').style(
                                    'font-size:12px;color:var(--text-light);')
