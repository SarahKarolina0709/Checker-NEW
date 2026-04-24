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
                    ui.icon('description', size='xs').style('color:#6b7280;')
                    if src_f:
                        ui.label(os.path.basename(src_f)).style(
                            'color:#0f2744;font-weight:600;')
                    if src_f and tgt_f:
                        ui.icon('arrow_forward', size='xs').style('color:#d4af37;')
                    if tgt_f:
                        ui.label(os.path.basename(tgt_f)).style(
                            'color:#16a34a;font-weight:600;')
            with ui.row().classes('w-full items-center gap-2 flex-wrap'):
                ui.badge(sev_lbl).style(
                    f'background:transparent;color:{sev_clr};border:1px solid {sev_clr};border-radius:20px;')
                if phase_lbl and not compact:
                    ui.badge(phase_lbl).style(
                        'background:transparent;color:#6b7280;border:1px solid #d1d5db;border-radius:20px;')
                ui.badge(f.code).style(
                    'background:transparent;color:#6b7280;border:1px solid #d1d5db;border-radius:20px;')
                diff = s.get('analysis_diff', {}) or {}
                if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
                    ui.badge('NEU').style(
                        'background:#dc2626;color:white;border-radius:20px;'
                        'font-weight:700;font-size:10px;')
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
                f'font-size:{msg_fs};color:#1f2937;line-height:1.4;font-weight:500;')
            if compact:
                return
            meta = getattr(f, 'meta', {}) or {}
            suggestion = (meta.get('suggestion') or '').strip()
            if suggestion:
                with ui.row().classes('w-full items-start gap-2').style(
                    'background:#ecfdf5;border-left:3px solid #16a34a;'
                    'padding:8px 10px;border-radius:6px;margin-top:6px;'
                ):
                    ui.icon('lightbulb', size='sm').style('color:#16a34a;flex-shrink:0;margin-top:1px;')
                    with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                        ui.label('Vorschlag').style(
                            'font-size:10px;font-weight:700;color:#16a34a;'
                            'text-transform:uppercase;letter-spacing:0.5px;')
                        ui.label(suggestion[:500]).style(
                            'font-size:12px;color:#064e3b;'
                            'white-space:pre-wrap;word-break:break-word;')
                    ui.button(icon='content_copy',
                        on_click=lambda _, t=suggestion: copy_to_clipboard(t)
                    ).props('flat dense round size=xs').tooltip(
                        'Vorschlag kopieren'
                    ).style('color:#16a34a;flex-shrink:0;')
            if f.source_text or f.target_text:
                error_span = (meta.get('error_text') or '').strip()
                with ui.column().classes('w-full gap-1').style('margin-top:6px;'):
                    if f.source_text:
                        with ui.row().classes('w-full items-start gap-1').style(
                            'background:#f8fafc;padding:6px 8px;border-radius:6px;'
                            'border-left:2px solid #0f2744;'
                        ):
                            ui.label('SRC').style(
                                'font-size:9px;font-weight:700;color:#0f2744;'
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
                                'font-size:9px;font-weight:700;color:#d97706;'
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
                    f'font-size:10px;font-weight:700;color:{clr};'
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
                    'font-size:11px;color:#1f2937;line-height:1.35;font-weight:500;')
                ui.badge(f.code).style(
                    'background:transparent;color:#9ca3af;border:none;'
                    'font-size:9px;padding:0;')
        checked = s.get('checked_findings', {}).get(str(real_idx), False)
        if checked:
            ui.icon('check_circle', size='xs').style(
                'color:#16a34a;position:absolute;right:6px;top:6px;')


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
            ui.icon('touch_app', size='3rem').style('color:#d1d5db;')
            ui.label('Finding auswählen').style('font-size:14px;color:#9ca3af;margin-top:8px;')
            ui.label('Klicke links auf ein Finding für Details').style(
                'font-size:12px;color:#d1d5db;')
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
                'background:transparent;color:#6b7280;border:1px solid #d1d5db;border-radius:20px;')
        ui.badge(f.code).style(
            'background:transparent;color:#6b7280;border:1px solid #d1d5db;border-radius:20px;')
        diff = s.get('analysis_diff', {}) or {}
        if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
            ui.badge('NEU').style(
                'background:#dc2626;color:white;border-radius:20px;font-weight:700;font-size:10px;')
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
            ui.icon('description', size='xs').style('color:#6b7280;')
            if src_f:
                ui.label(os.path.basename(src_f)).style(
                    'font-size:11px;color:#0f2744;font-weight:600;')
            if src_f and tgt_f:
                ui.icon('arrow_forward', size='xs').style('color:#d4af37;')
            if tgt_f:
                ui.label(os.path.basename(tgt_f)).style(
                    'font-size:11px;color:#16a34a;font-weight:600;')
    ui.label(f.message).style(
        'font-size:14px;color:#1f2937;line-height:1.5;font-weight:500;margin-bottom:8px;')
    if suggestion:
        with ui.row().classes('w-full items-start gap-2').style(
            'background:#ecfdf5;border-left:3px solid #16a34a;'
            'padding:8px 10px;border-radius:6px;margin-bottom:8px;'
        ):
            ui.icon('lightbulb', size='sm').style('color:#16a34a;flex-shrink:0;')
            with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                ui.label('Vorschlag').style(
                    'font-size:10px;font-weight:700;color:#16a34a;'
                    'text-transform:uppercase;letter-spacing:0.5px;')
                ui.label(suggestion).style(
                    'font-size:13px;color:#064e3b;white-space:pre-wrap;word-break:break-word;')
            ui.button(icon='content_copy',
                on_click=lambda _, t=suggestion: copy_to_clipboard(t)
            ).props('flat dense round size=xs').tooltip('Vorschlag kopieren').style('color:#16a34a;')
    if f.source_text:
        with ui.column().classes('w-full gap-0').style('margin-bottom:6px;'):
            ui.label('Quelltext').style('font-size:10px;font-weight:700;color:#0f2744;'
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
            ui.label('Zieltext').style('font-size:10px;font-weight:700;color:#d97706;'
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
