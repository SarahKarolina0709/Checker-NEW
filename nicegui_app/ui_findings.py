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


def _text_excerpt(text: str, error_span: str = '', window: int = 180) -> tuple[str, str]:
    """Gibt einen fokussierten Textausschnitt + Positionsinfo zurück.

    Returns:
        (excerpt, pos_label)  — pos_label ist z.B. '∼ Pos. 340 / 1250' oder ''
    """
    if not text:
        return '', ''
    total = len(text)
    pos_label = ''
    if total <= window:
        return text, ''
    # Mittelpunkt: error_span-Position, sonst Anfang
    if error_span and error_span in text:
        center = text.find(error_span) + len(error_span) // 2
        pos_label = f'∼ Pos.\u202f{center}\u202f/\u202f{total}'
    else:
        center = 0
    start = max(0, center - window // 2)
    end = min(total, start + window)
    # Wortgrenzen einhalten
    if start > 0:
        sp = text.rfind(' ', start, start + 20)
        if sp > 0:
            start = sp + 1
    if end < total:
        sp = text.find(' ', end - 20, end)
        if sp > 0:
            end = sp
    excerpt = (('… ' if start > 0 else '') +
               text[start:end] +
               (' …' if end < total else ''))
    return excerpt, pos_label


def render_finding_card(ctx: SimpleNamespace, idx: int, f) -> None:
    """Rendert eine Finding-Karte (normal- oder kompakt-Modus).

    Muss innerhalb eines NiceGUI-Containers aufgerufen werden.
    """
    # Lazy-Import um Zirkel-Importe mit main.py zu vermeiden
    from nicegui_app.severity import (
        severity_label, severity_color, severity_icon, severity_css_color, phase_from_code,
    )
    s = ctx.s
    refs = ctx.refs
    selected_idx = ctx.selected_idx

    sev_lbl = severity_label(f.severity)
    sev_clr = severity_css_color(f.severity)
    sev_ico = severity_icon(f.severity)
    phase_lbl = phase_from_code(f.code)
    is_selected = idx == selected_idx['v']
    compact = s.get('view_mode', 'normal') == 'compact'
    meta = getattr(f, 'meta', {}) or {}
    hint_only = bool(meta.get('hint_only'))
    pad = '6px 10px' if compact else '12px'
    mb = '4px' if compact else '8px'
    _sel = getattr(ctx, 'select_finding', None)
    card_style = (
        f'border-left:5px solid {sev_clr};border-radius:var(--radius-sm);'
        f'margin-bottom:{mb};padding:0;'
        f'background:{"var(--bg-muted)" if hint_only else "var(--surface)"};'
        f'{"opacity:.85;" if hint_only else ""}'
        f'{"cursor:pointer;" if _sel else ""}'
        f'border-top:1px solid var(--surface-border);border-right:1px solid var(--surface-border);'
        f'border-bottom:1px solid var(--surface-border);'
        # Auswahl via outline (box-shadow wird von der globalen .q-card-Regel
        # mit !important ueberschrieben und waere unsichtbar)
        f'{"outline:2px solid var(--info);outline-offset:-2px;" if is_selected else ""}'
    )
    with ui.card().classes('w-full finding-card').props('flat').style(card_style) as card_el:
        try:
            card_el.props(f'id=finding-card-{idx}')
        except Exception:
            pass
        # Mausklick auf die Karte selektiert sie (analog Tastatur j/k). Klicks auf
        # interaktive Kinder (Datei-Zeile, Checkbox) stoppen via .stop die Weiterleitung.
        if _sel:
            card_el.on('click', lambda _, i=idx: _sel(i))
            # Tastatur-Zugang: Karte in die Tab-Reihenfolge + Enter selektiert
            # (aktiviert den :focus-visible-Ring). NUR Enter — Leertaste ist global
            # mit "Geprueft umschalten" belegt. Schnellnavigation bleibt j/k.
            # Roving-Tabindex: nur die selektierte Karte ist tab-fokussierbar,
            # damit 50+ Karten nicht 50+ Tab-Stopps erzeugen. Eintrittspunkt: die
            # Liste selektiert beim Rendern die erste sichtbare Karte vor; j/k
            # verschiebt die Selektion (und den Fokus, siehe _scroll_to_selected).
            card_el.props(f'tabindex={"0" if is_selected else "-1"} role=button')
            # Praegnanter Screenreader-Name statt Vorlesen des ganzen Karteninhalts
            _aria = f'Befund {sev_lbl}: {getattr(f, "code", "") or ""}'.replace('"', "'")
            card_el.props(f'aria-label="{_aria}"')
            card_el.on('keydown.enter', lambda _, i=idx: _sel(i))
        with ui.column().classes('w-full gap-1').style(f'padding:{pad};'):
            src_f = getattr(f, 'source_file', '') or ''
            tgt_f = getattr(f, 'target_file', '') or ''
            if (src_f or tgt_f) and not compact:
                with ui.row().classes('w-full items-center gap-2 cursor-pointer').style(
                    'padding:4px 8px;background:var(--bg-muted);border-radius:var(--radius-xs);'
                    'margin-bottom:4px;font-size:var(--fs-xs);'
                ).on('click.stop', lambda _, sf=os.path.basename(src_f or tgt_f):
                     (s.update({'search_text': sf}),
                      refs.get('search_input') and refs['search_input'].set_value(sf),
                      ctx.refresh_results())):
                    ui.icon('description', size='xs').style('color:var(--text-muted);')
                    if src_f:
                        ui.label(os.path.basename(src_f)).style(
                            'color:var(--role-source);font-weight:600;')
                    if src_f and tgt_f:
                        ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
                    if tgt_f:
                        ui.label(os.path.basename(tgt_f)).style(
                            'color:var(--success);font-weight:600;')
            with ui.row().classes('w-full items-center gap-2 flex-wrap'):
                ui.icon(sev_ico, size='xs').style(f'color:{sev_clr};flex-shrink:0;') \
                    .tooltip(sev_lbl)
                ui.badge(sev_lbl, color=None).style(
                    f'background:transparent;color:{sev_clr};border:1px solid {sev_clr};border-radius:var(--radius-pill);')
                if hint_only and not compact:
                    ui.badge('Kein Score-Abzug', color=None).style(
                        'background:transparent;color:var(--text-light);'
                        'border:1px dashed var(--surface-border-strong);border-radius:var(--radius-pill);'
                        'font-size:var(--fs-xs);')
                if phase_lbl and not compact:
                    ui.badge(phase_lbl, color=None).style(
                        'background:transparent;color:var(--text-muted);border:1px solid var(--surface-border-strong);border-radius:var(--radius-pill);')
                ui.badge(f.code, color=None).style(
                    'background:transparent;color:var(--text-muted);border:1px solid var(--surface-border-strong);border-radius:var(--radius-pill);')
                diff = s.get('analysis_diff', {}) or {}
                if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
                    ui.badge('NEU', color=None).style(
                        'background:var(--error-solid);color:var(--text-inverse);border-radius:var(--radius-pill);'
                        'font-weight:700;font-size:var(--fs-xs);')
                ui.element('div').classes('flex-grow')
                cb = ui.checkbox('Geprüft',
                    value=s.get('checked_findings', {}).get(str(idx), False),
                    on_change=lambda e, i=idx: ctx.toggle_checked(
                        i, getattr(e, 'value', getattr(e, 'args', False))))
                cb.style('font-size:var(--fs-sm);')
                # Checkbox-Klick darf die Karte nicht zusaetzlich selektieren
                cb.on('click.stop', lambda: None)
            msg_fs = '12px' if compact else '13px'
            msg_text = (f.message[:120] + '…' if compact and len(f.message) > 120
                        else f.message)
            ui.label(msg_text).style(
                f'font-size:{msg_fs};color:var(--text);line-height:1.4;font-weight:500;')
            if compact:
                return
            suggestion = (meta.get('suggestion') or '').strip()
            if suggestion:
                with ui.row().classes('w-full items-start gap-2').style(
                    'background:var(--bg-success-soft);border-left:3px solid var(--success);'
                    'padding:8px 12px;border-radius:var(--radius-sm);margin-top:8px;'
                ):
                    ui.icon('lightbulb', size='sm').style('color:var(--success);flex-shrink:0;margin-top:1px;')
                    with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                        ui.label('Vorschlag').style(
                            'font-size:var(--fs-xs);font-weight:700;color:var(--success);'
                            'text-transform:uppercase;letter-spacing:0.5px;')
                        ui.label(suggestion[:500]).style(
                            'font-size:var(--fs-sm);color:var(--success-text);'
                            'white-space:pre-wrap;word-break:break-word;')
                    ui.button(icon='content_copy',
                        on_click=lambda _, t=suggestion: copy_to_clipboard(t)
                    ).props('flat dense round size=xs').tooltip(
                        'Vorschlag kopieren'
                    ).style('color:var(--success);flex-shrink:0;')
            if f.source_text or f.target_text:
                error_span = (meta.get('error_text') or '').strip()
                with ui.column().classes('w-full gap-2').style('margin-top:8px;'):
                    if f.source_text:
                        src_excerpt, src_pos = _text_excerpt(f.source_text, error_span)
                        with ui.column().classes('w-full gap-0'):
                            with ui.row().classes('w-full items-center gap-1').style('margin-bottom:2px;'):
                                ui.label('QUELLTEXT').style(
                                    'font-size:var(--fs-xs);font-weight:700;color:var(--role-source);'
                                    'text-transform:uppercase;letter-spacing:0.5px;')
                                if src_pos:
                                    ui.label(src_pos).style('font-size:var(--fs-xs);color:var(--text-light);')
                            with ui.row().classes('w-full items-start gap-2').style(
                                'background:var(--surface-alt);padding:8px 12px;border-radius:var(--radius-sm);'
                                'border-left:2px solid var(--role-source);'
                            ):
                                ui.label(src_excerpt).style(
                                    'font-size:var(--fs-read);color:var(--text);line-height:1.55;'
                                    'white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                                ui.button(icon='content_copy',
                                    on_click=lambda _, t=f.source_text: copy_to_clipboard(t)
                                ).props('flat dense round size=xs').tooltip(
                                    'Volltext kopieren'
                                ).style('color:var(--text-light);flex-shrink:0;')
                    if f.target_text:
                        tgt_excerpt, tgt_pos = _text_excerpt(f.target_text, error_span)
                        with ui.column().classes('w-full gap-0'):
                            with ui.row().classes('w-full items-center gap-1').style('margin-bottom:2px;'):
                                ui.label('ZIELTEXT').style(
                                    'font-size:var(--fs-xs);font-weight:700;color:var(--warning);'
                                    'text-transform:uppercase;letter-spacing:0.5px;')
                                if tgt_pos:
                                    ui.label(tgt_pos).style('font-size:var(--fs-xs);color:var(--text-light);')
                            with ui.row().classes('w-full items-start gap-2').style(
                                'background:var(--bg-warning-soft);padding:8px 12px;border-radius:var(--radius-sm);'
                                'border-left:2px solid var(--warning);'
                            ):
                                if error_span and error_span in f.target_text:
                                    pos = f.target_text.find(error_span)
                                    win = 200
                                    start = max(0, pos - win)
                                    before = ('… ' if start > 0 else '') + f.target_text[start:pos]
                                    after = f.target_text[pos + len(error_span):pos + len(error_span) + win]
                                    if len(f.target_text) > pos + len(error_span) + win:
                                        after += ' …'
                                    ui.html(
                                        f'<span style="font-size:var(--fs-read);color:var(--text);line-height:1.55;'
                                        f'white-space:pre-wrap;word-break:break-word;">'
                                        f'{html_esc(before)}'
                                        f'<mark style="background:var(--bg-error-soft);color:var(--error-text);'
                                        f'padding:1px 3px;border-radius:var(--radius-xs);font-weight:700;text-decoration:underline wavy;">'
                                        f'{html_esc(error_span)}</mark>'
                                        f'{html_esc(after)}</span>'
                                    ).classes('flex-grow')
                                else:
                                    ui.label(tgt_excerpt).style(
                                        'font-size:var(--fs-read);color:var(--text);line-height:1.55;'
                                        'white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                                ui.button(icon='content_copy',
                                    on_click=lambda _, t=f.target_text: copy_to_clipboard(t)
                                ).props('flat dense round size=xs').tooltip(
                                    'Volltext kopieren'
                                ).style('color:var(--text-light);flex-shrink:0;')


def render_split_list(ctx: SimpleNamespace, filtered) -> None:
    """Linke Spalte im Split-Modus: kompakte Karten ohne Texte.

    ctx braucht: s, selected_idx, select_finding(idx).
    """
    from nicegui_app.severity import severity_label, severity_color, severity_icon, severity_css_color
    s = ctx.s
    selected_idx = ctx.selected_idx
    _SEV_ORDER = [('Kritisch', 'var(--error)'), ('Wichtig', 'var(--warning)'), ('Hinweis', 'var(--text-muted)')]
    _sev_counts = {lbl: sum(1 for _, f in filtered if severity_label(f.severity) == lbl)
                   for lbl, _ in _SEV_ORDER}
    _last_sev = None
    _show_headers = s.get('sort_mode', 'default') in ('default', 'severity')
    for real_idx, f in filtered:
        sev_lbl = severity_label(f.severity)
        sev_clr = severity_css_color(f.severity)
        is_sel = real_idx == selected_idx['v']
        hint_only = bool((getattr(f, 'meta', {}) or {}).get('hint_only'))
        if _show_headers and sev_lbl != _last_sev and _sev_counts.get(sev_lbl, 0) > 0:
            _last_sev = sev_lbl
            clr = next((c for l, c in _SEV_ORDER if l == sev_lbl), 'var(--text-muted)')
            with ui.row().classes('w-full items-center gap-2').style('padding:4px 2px 2px;'):
                ui.icon(severity_icon(f.severity), size='xs').style(
                    f'color:{clr};flex-shrink:0;')
                ui.label(f'{sev_lbl}  ({_sev_counts[sev_lbl]})').style(
                    f'font-size:var(--fs-xs);font-weight:700;color:{clr};'
                    f'text-transform:uppercase;letter-spacing:0.6px;')
                ui.element('div').style(
                    f'flex-grow:1;height:1px;background:{clr};opacity:.2;')
        row_bg = 'var(--bg-info-soft)' if is_sel else ('var(--bg-muted)' if hint_only else 'var(--surface)')
        checked = s.get('checked_findings', {}).get(str(real_idx), False)
        with ui.row().classes('w-full items-center cursor-pointer gap-1').style(
            f'padding:6px 8px;border-left:4px solid {sev_clr};'
            f'background:{row_bg};border-radius:var(--radius-xs);margin-bottom:3px;'
            f'{"opacity:.7;" if hint_only else ""}'
            f'{"box-shadow:0 0 0 1px var(--primary);" if is_sel else ""}'
        ).on('click', lambda _, i=real_idx: ctx.select_finding(i)):
            with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                ui.label(f.message[:80] + ('…' if len(f.message) > 80 else '')).style(
                    'font-size:var(--fs-xs);color:var(--text);line-height:1.35;font-weight:500;')
                ui.badge(f.code, color=None).style(
                    'background:transparent;color:var(--text-light);border:none;'
                    'font-size:var(--fs-xs);padding:0;')
            if checked:
                ui.icon('check_circle', size='xs').style('color:var(--success);flex-shrink:0;')


def render_detail_panel(ctx: SimpleNamespace) -> None:
    """Rechtes Detail-Panel im Split-Modus.

    ctx braucht: s, refs, selected_idx, toggle_checked, dict_to_finding.
    """
    from nicegui_app.severity import severity_label, severity_color, severity_icon, severity_css_color, phase_from_code
    s = ctx.s
    selected_idx = ctx.selected_idx
    idx = selected_idx['v']
    if idx < 0:
        with ui.column().classes('w-full items-center justify-center').style('padding:32px;'):
            ui.icon('touch_app', size='3rem').style('color:var(--text-light);')
            ui.label('Befund auswählen').style('font-size:var(--fs-lg);color:var(--text-light);margin-top:8px;')
            ui.label('Klicken Sie links auf einen Befund für Details').style(
                'font-size:var(--fs-sm);color:var(--text-light);')
        return
    findings = s.get('findings', [])
    if idx >= len(findings):
        return
    f = ctx.dict_to_finding(findings[idx])
    sev_lbl = severity_label(f.severity)
    sev_clr = severity_css_color(f.severity)
    phase_lbl = phase_from_code(f.code)
    meta = getattr(f, 'meta', {}) or {}
    suggestion = (meta.get('suggestion') or '').strip()
    error_span = (meta.get('error_text') or '').strip()
    with ui.row().classes('w-full items-center gap-2 flex-wrap').style('margin-bottom:8px;'):
        ui.icon(severity_icon(f.severity), size='sm').style(f'color:{sev_clr};flex-shrink:0;')
        ui.badge(sev_lbl, color=None).style(
            f'background:{sev_clr};color:var(--text-inverse);border-radius:var(--radius-pill);font-size:var(--fs-sm);')
        if phase_lbl:
            ui.badge(phase_lbl, color=None).style(
                'background:transparent;color:var(--text-muted);border:1px solid var(--surface-border-strong);border-radius:var(--radius-pill);')
        ui.badge(f.code, color=None).style(
            'background:transparent;color:var(--text-muted);border:1px solid var(--surface-border-strong);border-radius:var(--radius-pill);')
        diff = s.get('analysis_diff', {}) or {}
        if diff.get('has_prev') and idx in set(diff.get('new_idx', []) or []):
            ui.badge('NEU', color=None).style(
                'background:var(--error-solid);color:var(--text-inverse);border-radius:var(--radius-pill);font-weight:700;font-size:var(--fs-xs);')
        ui.element('div').classes('flex-grow')
        cb = ui.checkbox('Geprüft',
            value=bool(s.get('checked_findings', {}).get(str(idx), False)),
            on_change=lambda e, i=idx: ctx.toggle_checked(i, getattr(e, 'value', getattr(e, 'args', False))))
        cb.style('font-size:var(--fs-md);')
    src_f = getattr(f, 'source_file', '') or ''
    tgt_f = getattr(f, 'target_file', '') or ''
    seg_idx = getattr(f, 'segment_index', -1)
    n_pairs = len(s.get('paired_results', []) or [])
    if src_f or tgt_f:
        with ui.row().classes('items-center gap-1 flex-wrap').style(
            'padding:4px 8px;background:var(--bg-muted);border-radius:var(--radius-xs);margin-bottom:8px;'
        ):
            ui.icon('description', size='xs').style('color:var(--text-muted);')
            if src_f:
                ui.label(os.path.basename(src_f)).style(
                    'font-size:var(--fs-xs);color:var(--primary);font-weight:600;')
            if src_f and tgt_f:
                ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
            if tgt_f:
                ui.label(os.path.basename(tgt_f)).style(
                    'font-size:var(--fs-xs);color:var(--success);font-weight:600;')
            if seg_idx >= 0 and n_pairs > 1:
                ui.element('div').style('flex-grow:1;')
                ui.label(f'Dateipaar {seg_idx + 1} / {n_pairs}').style(
                    'font-size:var(--fs-xs);color:var(--text-light);font-weight:500;')
    ui.label(f.message).style(
        'font-size:var(--fs-lg);color:var(--text);line-height:1.5;font-weight:500;margin-bottom:8px;')
    if suggestion:
        with ui.row().classes('w-full items-start gap-2').style(
            'background:var(--bg-success-soft);border-left:3px solid var(--success);'
            'padding:8px 10px;border-radius:var(--radius-sm);margin-bottom:8px;'
        ):
            ui.icon('lightbulb', size='sm').style('color:var(--success);flex-shrink:0;')
            with ui.column().classes('gap-0 flex-grow').style('min-width:0;'):
                ui.label('Vorschlag').style(
                    'font-size:var(--fs-xs);font-weight:700;color:var(--success);'
                    'text-transform:uppercase;letter-spacing:0.5px;')
                ui.label(suggestion).style(
                    'font-size:var(--fs-md);color:var(--success-text);white-space:pre-wrap;word-break:break-word;')
            ui.button(icon='content_copy',
                on_click=lambda _, t=suggestion: copy_to_clipboard(t)
            ).props('flat dense round size=xs').tooltip('Vorschlag kopieren').style('color:var(--success);')
    if f.source_text:
        src_excerpt, src_pos = _text_excerpt(f.source_text, error_span, window=350)
        with ui.column().classes('w-full gap-0').style('margin-bottom:6px;'):
            with ui.row().classes('w-full items-center gap-2').style('margin-bottom:2px;'):
                ui.label('Quelltext').style('font-size:var(--fs-xs);font-weight:700;color:var(--role-source);'
                    'text-transform:uppercase;letter-spacing:0.5px;')
                if src_pos:
                    ui.label(src_pos).style('font-size:var(--fs-xs);color:var(--text-light);')
            with ui.row().classes('w-full items-start gap-1').style(
                'background:var(--surface-alt);padding:8px;border-radius:var(--radius-sm);border-left:3px solid var(--role-source);'
            ):
                ui.label(src_excerpt).style(
                    'font-size:var(--fs-read);color:var(--text);line-height:1.55;white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                ui.button(icon='content_copy',
                    on_click=lambda _, t=f.source_text: copy_to_clipboard(t)
                ).props('flat dense round size=xs').tooltip('Volltext kopieren').style(
                    'color:var(--text-light);flex-shrink:0;')
    if f.target_text:
        tgt_excerpt, tgt_pos = _text_excerpt(f.target_text, error_span, window=350)
        with ui.column().classes('w-full gap-0'):
            with ui.row().classes('w-full items-center gap-2').style('margin-bottom:2px;'):
                ui.label('Zieltext').style('font-size:var(--fs-xs);font-weight:700;color:var(--warning);'
                    'text-transform:uppercase;letter-spacing:0.5px;')
                if tgt_pos:
                    ui.label(tgt_pos).style('font-size:var(--fs-xs);color:var(--text-light);')
            with ui.row().classes('w-full items-start gap-1').style(
                'background:var(--bg-warning-soft);padding:8px;border-radius:var(--radius-sm);border-left:3px solid var(--warning);'
            ):
                if error_span and error_span in f.target_text:
                    err_pos = f.target_text.find(error_span)
                    win = 350
                    start = max(0, err_pos - win // 2)
                    before = ('… ' if start > 0 else '') + f.target_text[start:err_pos]
                    after = f.target_text[err_pos + len(error_span):err_pos + len(error_span) + win // 2]
                    if len(f.target_text) > err_pos + len(error_span) + win // 2:
                        after += ' …'
                    ui.html(
                        f'<span style="font-size:var(--fs-read);color:var(--text);line-height:1.55;'
                        f'white-space:pre-wrap;word-break:break-word;">'
                        f'{html_esc(before)}'
                        f'<mark style="background:var(--bg-error-soft);color:var(--error-text);'
                        f'padding:1px 3px;border-radius:var(--radius-xs);font-weight:700;text-decoration:underline wavy;">'
                        f'{html_esc(error_span)}</mark>'
                        f'{html_esc(after)}</span>'
                    ).classes('flex-grow')
                else:
                    ui.label(tgt_excerpt).style(
                        'font-size:var(--fs-read);color:var(--text);line-height:1.55;white-space:pre-wrap;word-break:break-word;flex-grow:1;')
                ui.button(icon='content_copy',
                    on_click=lambda _, t=f.target_text: copy_to_clipboard(t)
                ).props('flat dense round size=xs').tooltip('Volltext kopieren').style(
                    'color:var(--text-light);flex-shrink:0;')


def render_findings_list(ctx: SimpleNamespace) -> None:
    """Orchestriert den Findings-Bereich (Welcome / Empty / Split / Normal-Modus).

    ctx braucht: s, refs, filtered_findings(), render_welcome(),
    render_split_list(filtered), render_detail_panel(), render_finding_card(idx, f).
    """
    from nicegui_app.severity import severity_label, severity_icon
    s = ctx.s
    refs = ctx.refs
    container = refs['findings_container']
    welcome = refs.get('welcome_area')
    # Welcome/Onboarding rendert in welcome_area (Sibling von results_area).
    # findings_container liegt INNERHALB results_area, die bei current_score<0
    # versteckt wird -> Welcome dorthin zu rendern ergaebe ein leeres Dashboard.
    if welcome is not None:
        welcome.clear()
    if not container:
        return
    container.clear()
    current_score = s.get('current_score', -1)
    filtered = ctx.filtered_findings()
    split_mode = s.get('view_mode', 'normal') == 'split'
    refs['detail_panel'] = None  # reset for this render
    if current_score < 0:
        if welcome is not None:
            with welcome:
                ctx.render_welcome()
        return
    with container:
        if not filtered:
            total_findings = len(s.get('findings', []))
            if total_findings == 0:
                # Perfekte Analyse — keinerlei Findings
                with ui.column().classes('w-full items-center').style('gap:10px;padding:32px 0;'):
                    with ui.element('div').style(
                        'width:64px;height:64px;border-radius:50%;'
                        'background:var(--bg-success-soft);'
                        'display:flex;align-items:center;justify-content:center;'):
                        ui.icon('check_circle', size='2rem').style('color:var(--success);')
                    ui.label('Keine Probleme gefunden').style(
                        'font-size:var(--fs-xl);font-weight:700;color:var(--text);')
                    ui.label('Die Übersetzung hat alle Prüfungen bestanden.').style(
                        'font-size:var(--fs-sm);color:var(--text-muted);text-align:center;')
            else:
                # Findings vorhanden, aber Filter/Suche blendet alle aus
                with ui.column().classes('w-full items-center').style('gap:8px;padding:28px 0;'):
                    ui.icon('filter_alt_off', size='1.75rem').style('color:var(--text-light);opacity:.5;')
                    ui.label('Keine Treffer in dieser Ansicht').style(
                        'font-size:var(--fs-md);font-weight:600;color:var(--text-muted);')
                    _hint = ('Suchbegriff anpassen oder Filter zurücksetzen'
                             if (s.get('search_text') or '').strip()
                             else 'Anderen Schweregrad-Filter wählen')
                    ui.label(f'{total_findings} Befund(e) vorhanden · {_hint}').style(
                        'font-size:var(--fs-sm);color:var(--text-light);text-align:center;')
            return
        if split_mode:
            with ui.row().classes('w-full gap-0 items-start qf-stack').style('min-height:300px;'):
                list_col = ui.column().classes('gap-0').style(
                    'width:340px;min-width:300px;flex-shrink:0;'
                    'overflow-y:auto;max-height:calc(100vh - 420px);'
                    'border-right:1px solid var(--surface-border);padding-right:8px;'
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
            _SEV_ORDER = [('Kritisch', 'var(--error)'), ('Wichtig', 'var(--warning)'), ('Hinweis', 'var(--text-muted)')]
            _sev_counts = {lbl: sum(1 for _, f in filtered if severity_label(f.severity) == lbl)
                           for lbl, _ in _SEV_ORDER}
            _last_sev_group = None
            _show_sev_headers = s.get('sort_mode', 'default') in ('default', 'severity')
            for real_idx, f in filtered:
                sev_lbl = severity_label(f.severity)
                if _show_sev_headers and sev_lbl != _last_sev_group and _sev_counts.get(sev_lbl, 0) > 0:
                    _last_sev_group = sev_lbl
                    clr = next((c for l, c in _SEV_ORDER if l == sev_lbl), 'var(--text-muted)')
                    cnt = _sev_counts[sev_lbl]
                    with ui.row().classes('w-full items-center gap-2').style(
                        'padding:6px 4px 4px;margin-top:4px;'
                    ):
                        ui.icon(severity_icon(f.severity), size='xs').style(
                            f'color:{clr};flex-shrink:0;')
                        ui.label(f'{sev_lbl}  ({cnt})').style(
                            f'font-size:var(--fs-xs);font-weight:700;color:{clr};'
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
    from nicegui import run
    from nicegui_app.text_extraction import extract_text
    s = ctx.s
    customer = s.get('active_customer', '')
    src_files = s.get('source_files', [])
    tgt_files = s.get('translation_files', [])
    has_files = bool(src_files or tgt_files)

    if has_files:
        # --- Zustand 3: Dateien geladen -> Textvorschau ---
        def _safe_extract(path):
            return extract_text(path)[:500] if os.path.exists(path) else ''

        def _preview_label(fp):
            """Zeigt sofort einen Platzhalter und laedt die Textvorschau dann
            nicht-blockierend nach (run.io_bound im Threadpool), damit der
            Render-Pfad nicht auf die Datei-Extraktion wartet."""
            lbl = ui.label('Vorschau wird geladen …').style(
                'font-size:var(--fs-sm);color:var(--text-light);white-space:pre-wrap;'
                'max-height:150px;overflow:hidden;line-height:1.5;')

            async def _fill(label=lbl, path=fp):
                try:
                    txt = await run.io_bound(_safe_extract, path)
                except Exception:
                    txt = None
                label.set_text(txt or 'Vorschau nicht verfügbar')
                if txt:
                    label.style('color:var(--text-muted)')

            ui.timer(0.05, _fill, once=True)

        with ui.column().classes('w-full gap-4'):
            ui.label('Textvorschau').style('font-size:var(--fs-xl);font-weight:700;color:var(--text);')
            with ui.row().classes('w-full gap-4').style('min-height:200px;'):
                with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                    ui.label('Ausgangstext').style(
                        'font-size:var(--fs-sm);font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:1px;')
                    if src_files:
                        for fp in src_files[:3]:
                            ui.label(os.path.basename(fp)).style('font-size:var(--fs-sm);font-weight:600;color:var(--text);')
                            _preview_label(fp)
                            ui.separator().style('margin:4px 0;')
                    else:
                        ui.label('Keine Ausgangstexte').style('font-size:var(--fs-sm);color:var(--text-light);')

                with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                    ui.label('Übersetzung').style(
                        'font-size:var(--fs-sm);font-weight:700;color:var(--success);text-transform:uppercase;letter-spacing:1px;')
                    if tgt_files:
                        for fp in tgt_files[:3]:
                            ui.label(os.path.basename(fp)).style('font-size:var(--fs-sm);font-weight:600;color:var(--text);')
                            _preview_label(fp)
                            ui.separator().style('margin:4px 0;')
                    else:
                        ui.label('Keine Übersetzungen').style('font-size:var(--fs-sm);color:var(--text-light);')

            pairs = s.get('paired_results', [])
            if pairs:
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;'):
                    ui.label(f'{len(pairs)} {"Paar" if len(pairs) == 1 else "Paare"} erkannt').style(
                        'font-size:var(--fs-md);font-weight:600;color:var(--primary);')
                    for p in pairs[:5]:
                        src_name = os.path.basename(p.get('source', ''))
                        tgt_name = os.path.basename(p.get('translation', ''))
                        with ui.row().classes('w-full items-center gap-2').style('padding:4px 0;'):
                            ui.icon('description', size='xs').style('color:var(--text-muted);')
                            ui.label(src_name).style('font-size:var(--fs-sm);color:var(--text);')
                            ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
                            ui.label(tgt_name).style('font-size:var(--fs-sm);color:var(--text);')

    elif customer:
        # --- Zustand 2: Kunde gewaehlt, keine Dateien ---
        info = ctx.load_customer_info(customer)
        projects = ctx.list_projects(customer)
        with ui.column().classes('w-full items-center').style('padding:32px 0;gap:16px;'):
            ui.icon('business' if info.get('typ') == 'firma' else 'person', size='3rem').style('color:var(--accent);')
            ui.label(ctx.display_name(customer)).style('font-size:var(--fs-2xl);font-weight:700;color:var(--text);')
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
                    'background:var(--bg-info-soft);padding:6px 16px;border-radius:var(--radius-pill);margin-top:4px;'):
                    ui.icon('folder_open', size='xs').style('color:var(--primary);')
                    ui.label(f'Projekt: {display}').style('font-size:var(--fs-md);font-weight:600;color:var(--primary);')
            if info.get('email') or info.get('telefon'):
                with ui.row().classes('gap-4').style('margin-top:4px;'):
                    if info.get('email'):
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('email', size='xs').style('color:var(--text-light);')
                            ui.label(info['email']).style('font-size:var(--fs-sm);color:var(--text-muted);')
                    if info.get('telefon'):
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('phone', size='xs').style('color:var(--text-light);')
                            ui.label(info['telefon']).style('font-size:var(--fs-sm);color:var(--text-muted);')
            with ui.row().classes('gap-6').style('margin-top:8px;'):
                with ui.column().classes('items-center'):
                    ui.label(str(len(projects))).style('font-size:var(--fs-3xl);font-weight:800;color:var(--primary);')
                    ui.label('Projekte').style('font-size:var(--fs-sm);color:var(--text-light);')
                n_src = len(s.get('source_files', []))
                n_tgt = len(s.get('translation_files', []))
                with ui.column().classes('items-center'):
                    ui.label(str(n_src)).style('font-size:var(--fs-3xl);font-weight:800;color:var(--primary);')
                    ui.label('Ausgangstexte').style('font-size:var(--fs-sm);color:var(--text-light);')
                with ui.column().classes('items-center'):
                    ui.label(str(n_tgt)).style('font-size:var(--fs-3xl);font-weight:800;color:var(--success);')
                    ui.label('Übersetzungen').style('font-size:var(--fs-sm);color:var(--text-light);')
            if not proj_path:
                ui.label('Wählen Sie ein Projekt und laden Sie Dateien hoch').style(
                    'font-size:var(--fs-sm);color:var(--text-light);margin-top:12px;')
            elif proj_path and os.path.isdir(proj_path):
                src_dir = ctx.find_source_folder(proj_path)
                tgt_dir = ctx.find_translation_folder(proj_path)
                src_files_list = ctx.list_files_in_folder(src_dir) if src_dir else []
                tgt_files_list = ctx.list_files_in_folder(tgt_dir) if tgt_dir else []

                if src_files_list or tgt_files_list:
                    with ui.row().classes('w-full gap-4').style('margin-top:16px;'):
                        with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                            with ui.row().classes('items-center gap-2').style('margin-bottom:8px;'):
                                ui.element('div').style('width:4px;height:16px;border-radius:2px;background:var(--role-source);')
                                ui.label(f'Ausgangstexte ({len(src_files_list)})').style(
                                    'font-size:var(--fs-md);font-weight:700;color:var(--role-source);')
                            if src_files_list:
                                for fp in src_files_list:
                                    fname = os.path.basename(fp)
                                    fsize = os.path.getsize(fp) if os.path.exists(fp) else 0
                                    with ui.row().classes('w-full items-center gap-2').style(
                                        'padding:4px 0;border-bottom:1px solid var(--surface-border-light);'):
                                        ui.icon('description', size='xs').style('color:var(--text-muted);')
                                        ui.label(fname).style(
                                            'font-size:var(--fs-sm);color:var(--text);flex-grow:1;'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                        ui.label(f'{fsize/1024:.0f} KB').style('font-size:var(--fs-sm);color:var(--text-light);')
                            else:
                                ui.label('Keine Dateien').style('font-size:var(--fs-sm);color:var(--text-light);')

                        with ui.card().classes('flex-1').props('flat bordered').style('padding:12px;'):
                            with ui.row().classes('items-center gap-2').style('margin-bottom:8px;'):
                                ui.element('div').style('width:4px;height:16px;border-radius:2px;background:var(--success);')
                                ui.label(f'Übersetzungen ({len(tgt_files_list)})').style(
                                    'font-size:var(--fs-md);font-weight:700;color:var(--success);')
                            if tgt_files_list:
                                for fp in tgt_files_list:
                                    fname = os.path.basename(fp)
                                    fsize = os.path.getsize(fp) if os.path.exists(fp) else 0
                                    with ui.row().classes('w-full items-center gap-2').style(
                                        'padding:4px 0;border-bottom:1px solid var(--surface-border-light);'):
                                        ui.icon('translate', size='xs').style('color:var(--text-muted);')
                                        ui.label(fname).style(
                                            'font-size:var(--fs-sm);color:var(--text);flex-grow:1;'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                        ui.label(f'{fsize/1024:.0f} KB').style('font-size:var(--fs-sm);color:var(--text-light);')
                            else:
                                ui.label('Keine Dateien').style('font-size:var(--fs-sm);color:var(--text-light);')
                else:
                    ui.label('Projekt ist leer — laden Sie Dateien über die Ordner links hoch').style(
                        'font-size:var(--fs-sm);color:var(--text-light);margin-top:12px;')

            if len(projects) > 1:
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;margin-top:12px;'):
                    ui.label(f'Alle Projekte von {ctx.display_name(customer)}').style(
                        'font-size:var(--fs-md);font-weight:700;color:var(--text);margin-bottom:8px;')
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
                            f'padding:6px 8px;border-radius:var(--radius-sm);'
                            f'{"background:var(--bg-info-soft);border:1px solid var(--border-info);" if is_active else "border:1px solid transparent;"}'
                        ).on('click', lambda _, p=proj, pp2=pp, ns=n_s, nt=n_t:
                             ctx.select_auftrag(p, pp2, ns, nt)):
                            ui.icon('folder', size='xs').style(
                                f'color:{"var(--primary)" if is_active else "var(--accent)"};')
                            ui.label(display).style(
                                f'font-size:var(--fs-sm);{"font-weight:700;color:var(--primary);" if is_active else "color:var(--text);"}flex-grow:1;')
                            if n_s or n_t:
                                ui.label(f'{n_s}Q · {n_t}Ü').style('font-size:var(--fs-sm);color:var(--text-muted);')

    else:
        # --- Zustand 1: Kein Kunde -> 2-Spalten Dashboard ---
        all_dates = ctx.scan_project_dates()

        _DE_WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

        with ui.row().classes('w-full gap-4 items-start animate-in').style('padding:4px 0;'):

            # ── Linke Spalte: Unified Card ───────────────────────────────────
            with ui.element('div').style(
                'flex:1 1 0;min-width:0;border-radius:var(--radius-lg);overflow:hidden;'
                'border:1px solid var(--surface-border);'
                'box-shadow:0 2px 8px rgba(15,39,68,.06);'):

                # --- dunkler Header (verbessertes Banner) ---
                with ui.element('div').style(
                    'background:linear-gradient(135deg,#0a1628 0%,#0f2744 45%,#1a3a5c 100%);'
                    'padding:24px 28px;position:relative;overflow:hidden;'):
                    # Hintergrund-Schrift (Wasserzeichen-Style)
                    ui.element('div').style(
                        'position:absolute;right:-10px;top:50%;transform:translateY(-50%);'
                        'font-size:96px;font-weight:900;color:rgba(255,255,255,.03);'
                        'letter-spacing:-4px;pointer-events:none;user-select:none;'
                        'font-family:"DM Sans",sans-serif;line-height:1;')
                    # Akzent-Linie links
                    ui.element('div').style(
                        'position:absolute;left:0;top:0;bottom:0;width:4px;'
                        'background:linear-gradient(180deg,var(--accent) 0%,rgba(212,175,55,.3) 100%);')
                    # Leuchtpunkt oben rechts
                    ui.element('div').style(
                        'position:absolute;top:-40px;right:-40px;width:160px;height:160px;'
                        'border-radius:50%;'
                        'background:radial-gradient(circle,rgba(212,175,55,.12) 0%,transparent 70%);'
                        'pointer-events:none;')
                    # zweiter Leuchtpunkt
                    ui.element('div').style(
                        'position:absolute;bottom:-30px;left:30%;width:100px;height:100px;'
                        'border-radius:50%;'
                        'background:radial-gradient(circle,rgba(59,130,246,.08) 0%,transparent 70%);'
                        'pointer-events:none;')
                    with ui.row().classes('items-center gap-4').style('position:relative;z-index:1;'):
                        # Logo-Badge: identisch mit Header-Logo
                        with ui.element('div').style(
                            'width:52px;height:52px;flex-shrink:0;border-radius:var(--radius-lg);'
                            'background:linear-gradient(145deg,#d4af37,#c49b28);'
                            'display:flex;align-items:center;justify-content:center;'
                            'box-shadow:0 4px 16px rgba(0,0,0,.40),inset 0 1px 0 rgba(255,255,255,.25);'
                            'position:relative;overflow:hidden;'):
                            ui.element('div').style(
                                'position:absolute;top:0;left:0;right:0;height:50%;'
                                'background:rgba(255,255,255,.20);border-radius:var(--radius-lg) 14px 0 0;'
                                'pointer-events:none;')
                            ui.icon('translate').style(
                                'font-size:28px;color:#0a1628;position:relative;z-index:1;')
                        with ui.column().style('gap:4px;'):
                            with ui.row().classes('items-center gap-2'):
                                ui.label('Qualitäts-Framework').style(
                                    'font-size:21px;font-weight:800;color:var(--text-inverse);'
                                    'letter-spacing:-.4px;line-height:1.15;')
                                with ui.element('div').style(
                                    'padding:2px 8px;border-radius:var(--radius-pill);'
                                    'background:rgba(212,175,55,.18);'
                                    'border:1px solid rgba(212,175,55,.35);'):
                                    ui.label('PROFESSIONAL').style(
                                        'font-size:var(--fs-xs);color:var(--accent);'
                                        'font-weight:700;letter-spacing:1.5px;')
                            # Feature-Tags
                            with ui.row().classes('items-center gap-2').style('flex-wrap:wrap;'):
                                ui.label('Professionelle Qualitätssicherung').style(
                                    'font-size:var(--fs-sm);color:rgba(255,255,255,.55);')
                                for tag in ['Phase 1–4', 'KI-gestützt', 'PDF · DOCX · TXT']:
                                    with ui.element('div').style(
                                        'padding:2px 8px;border-radius:var(--radius-pill);'
                                        'background:rgba(255,255,255,.07);'
                                        'border:1px solid rgba(255,255,255,.12);'):
                                        ui.label(tag).style(
                                            'font-size:var(--fs-xs);color:rgba(255,255,255,.60);'
                                            'font-weight:500;white-space:nowrap;')

                # --- heller Body: Schritte + Tipp ---
                with ui.element('div').style(
                    'background:var(--surface);padding:20px 24px 18px;'):

                    # Schritt-Label
                    ui.label('SO GEHT\'S').style(
                        'font-size:var(--fs-xs);font-weight:700;color:var(--text-light);'
                        'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;display:block;')

                    # 3-Schritte-Karten
                    # num_clr/num_bg dark-aware ueber Tokens (zuvor hartkodierte
                    # Hex -> im Dark-Mode unangepasst): weisse/dunkle Surface-
                    # Scheibe + farbiger Ring + farbige Zahl, in beiden Modi lesbar.
                    _steps = [
                        ('login',       '1', 'Kunde wählen',
                         'Links in der Seitenleiste auswählen oder neu anlegen',
                         'var(--bg-info-soft)',    'var(--border-info)',    'var(--info)',          'var(--surface)'),
                        ('upload_file', '2', 'Dateien hochladen',
                         'Ausgangstext + Übersetzung per Klick oder Drag & Drop',
                         'var(--bg-success-soft)', 'var(--border-success)', 'var(--success-text)',  'var(--surface)'),
                        ('play_circle', '3', 'Analyse starten',
                         'Score, Befunde & Korrekturvorschläge erhalten',
                         'var(--bg-warning-soft)', 'var(--border-warning)', 'var(--warning-text)',  'var(--surface)'),
                    ]
                    with ui.row().classes('w-full gap-3').style('flex-wrap:nowrap;margin-bottom:16px;'):
                        for icon, num, title, desc, bg, bdr, num_clr, num_bg in _steps:
                            with ui.element('div').style(
                                f'flex:1 1 0;min-width:0;border-radius:var(--radius-md);'
                                f'background:{bg};border:1px solid {bdr};padding:14px 14px 12px;'):
                                with ui.row().classes('items-center gap-2').style('margin-bottom:7px;'):
                                    with ui.element('div').style(
                                        f'width:24px;height:24px;border-radius:50%;flex-shrink:0;'
                                        f'background:{num_bg};border:1.5px solid {bdr};'
                                        f'display:flex;align-items:center;justify-content:center;'):
                                        ui.label(num).style(
                                            f'font-size:var(--fs-xs);font-weight:800;color:{num_clr};')
                                    ui.icon(icon, size='xs').style(
                                        f'color:{num_clr};opacity:.7;')
                                ui.label(title).style(
                                    'font-size:var(--fs-md);font-weight:700;color:var(--text);'
                                    'margin-bottom:3px;line-height:1.2;')
                                ui.label(desc).style(
                                    'font-size:var(--fs-xs);color:var(--text-muted);line-height:1.5;')

                    # Tipp-Box — nahtlos in Body integriert
                    with ui.element('div').style(
                        'border-radius:var(--radius-sm);background:var(--bg-warning-tint);'
                        'border:1px solid var(--border-warning);padding:9px 12px;'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('lightbulb', size='xs').style(
                                'color:var(--warning);flex-shrink:0;')
                            ui.label('Tipp: Unterstützte Formate sind PDF, DOCX und TXT. '
                                     'Bilder werden per OCR erkannt.').style(
                                'font-size:var(--fs-xs);color:var(--text-muted);line-height:1.45;')

            # ── Rechte Spalte: Letzte Aktivitäten ────────────────────────────
            with ui.card().props('flat bordered').style(
                'width:260px;flex-shrink:0;padding:0;border-radius:var(--radius-lg);'
                'background:var(--surface);overflow:hidden;align-self:start;'):

                # Card-Header
                with ui.element('div').style(
                    'padding:12px 16px 10px;'
                    'border-bottom:1px solid var(--surface-border-light);'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('history', size='xs').style('color:var(--accent);')
                        ui.label('Letzte Aktivität').style(
                            'font-size:var(--fs-md);font-weight:700;color:var(--text);')

                if all_dates:
                    sorted_dates = sorted(all_dates.keys(), reverse=True)[:7]
                    with ui.column().style('gap:0;padding:6px 0 4px;'):
                        for day_str in sorted_dates:
                            customers_on_day = all_dates[day_str]
                            try:
                                dt = datetime.strptime(day_str, '%Y-%m-%d')
                                display_date = dt.strftime('%d.%m.')
                                weekday = _DE_WEEKDAYS[dt.weekday()]
                            except Exception:
                                display_date = day_str
                                weekday = ''
                            with ui.row().classes('w-full items-start gap-2').style(
                                'padding:5px 14px;'):
                                # Datum-Badge
                                with ui.element('div').style(
                                    'min-width:40px;background:var(--bg-info-soft);'
                                    'border-radius:var(--radius-sm);padding:3px 5px;text-align:center;'
                                    'border:1px solid var(--border-info);flex-shrink:0;'):
                                    ui.label(display_date).style(
                                        'font-size:var(--fs-xs);font-weight:700;color:var(--primary);'
                                        'display:block;line-height:1.3;')
                                    if weekday:
                                        ui.label(weekday).style(
                                            'font-size:var(--fs-xs);color:var(--text-light);'
                                            'display:block;line-height:1.3;')
                                with ui.column().classes('gap-1 flex-grow').style('min-width:0;'):
                                    for cust in customers_on_day[:2]:
                                        _cust_name = ctx.display_name(cust)
                                        _initial = (_cust_name.strip()[:1] or '?').upper()
                                        with ui.row().classes('items-center gap-2 cursor-pointer act-row').style(
                                            'padding:2px 5px;border-radius:var(--radius-sm);'
                                            'transition:background .15s;'
                                        ).on('click', lambda _, c=cust: ctx.on_customer_selected(c)):
                                            with ui.element('div').style(
                                                'width:20px;height:20px;border-radius:var(--radius-xs);flex-shrink:0;'
                                                'background:var(--brand-grad-badge);'
                                                'display:flex;align-items:center;justify-content:center;'
                                                'font-size:var(--fs-xs);font-weight:700;color:var(--accent);'):
                                                ui.label(_initial)
                                            ui.label(_cust_name).style(
                                                'font-size:var(--fs-sm);color:var(--text);'
                                                'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                    if len(customers_on_day) > 2:
                                        ui.label(f'+{len(customers_on_day)-2} weitere').style(
                                            'font-size:var(--fs-xs);color:var(--text-light);'
                                            'padding-left:24px;')
                else:
                    with ui.column().classes('items-center').style('padding:28px 16px;gap:8px;'):
                        ui.icon('inbox', size='2rem').style('color:var(--text-light);')
                        ui.label('Noch keine Projekte').style(
                            'font-size:var(--fs-sm);color:var(--text-muted);text-align:center;')
                        ui.label('Legen Sie einen Kunden an und starten Sie Ihr erstes Projekt.').style(
                            'font-size:var(--fs-xs);color:var(--text-light);text-align:center;'
                            'line-height:1.45;')

        # ── Mini-Kalender (volle Breite) ──────────────────────────────────────
        import calendar as _cal_mod
        from datetime import date as _date_t
        from nicegui_app.customers import MONTH_NAMES_DE

        _today = _date_t.today()
        _cal_view = {'year': _today.year, 'month': _today.month, 'selected': None}

        with ui.card().props('flat bordered').classes('w-full').style(
            'border-radius:var(--radius-lg);padding:0;overflow:hidden;margin-top:4px;'):

            # Header
            with ui.element('div').style(
                'padding:10px 20px;border-bottom:1px solid var(--surface-border-light);'
                'background:var(--surface);'):
                with ui.row().classes('w-full items-center gap-2'):
                    ui.icon('calendar_month', size='xs').style('color:var(--accent);')
                    ui.label('Projektkalender').style(
                        'font-size:var(--fs-md);font-weight:700;color:var(--text);flex-grow:1;')
                    ui.button('Vollansicht', icon='open_in_new',
                        on_click=lambda: ui.navigate.to('/kalender')
                    ).props('flat no-caps dense').style(
                        'font-size:var(--fs-xs);color:var(--text-muted);')

            # 2-Spalten: Kalender links, Tages-Preview rechts
            with ui.row().classes('w-full items-start').style(
                'gap:0;background:var(--surface);'):

                # Kalender-Grid (flexibel)
                _cal_body = ui.column().classes('flex-grow').style(
                    'padding:12px 16px 14px;min-width:0;')

                # Tages-Preview (feste Breite)
                _preview_panel = ui.column().style(
                    'width:240px;flex-shrink:0;padding:14px 16px;'
                    'border-left:1px solid var(--surface-border-light);min-height:200px;')
                with _preview_panel:
                    ui.label('Tag auswählen').style(
                        'font-size:var(--fs-sm);color:var(--text-light);')

            def _show_day_preview(day_str: str, customers_day: list):
                _preview_panel.clear()
                _cal_view['selected'] = day_str
                with _preview_panel:
                    try:
                        dt = _date_t.fromisoformat(day_str)
                        pretty = dt.strftime('%d.%m.%Y')
                        wd_de = _DE_WEEKDAYS[dt.weekday()]
                    except Exception:
                        pretty, wd_de = day_str, ''
                    with ui.row().classes('items-center gap-2').style('margin-bottom:10px;'):
                        with ui.element('div').style(
                            'width:36px;height:36px;border-radius:var(--radius-sm);flex-shrink:0;'
                            'background:var(--bg-info-soft);border:1px solid var(--border-info);'
                            'display:flex;flex-direction:column;align-items:center;justify-content:center;'):
                            ui.label(dt.strftime('%d') if hasattr(dt, 'strftime') else '').style(
                                'font-size:var(--fs-md);font-weight:800;color:var(--primary);line-height:1;')
                            if wd_de:
                                ui.label(wd_de).style(
                                    'font-size:var(--fs-xs);color:var(--text-light);line-height:1;')
                        with ui.column().style('gap:1px;'):
                            ui.label(pretty).style(
                                'font-size:var(--fs-md);font-weight:700;color:var(--text);')
                            ui.label(f'{len(customers_day)} Projekt{"e" if len(customers_day)!=1 else ""}').style(
                                'font-size:var(--fs-xs);color:var(--text-muted);') if customers_day else \
                            ui.label('Kein Projekt').style(
                                'font-size:var(--fs-xs);color:var(--text-light);')
                    if customers_day:
                        with ui.column().classes('w-full gap-2'):
                            for cust in customers_day:
                                _cust_name = ctx.display_name(cust)
                                _initial = (_cust_name.strip()[:1] or '?').upper()
                                with ui.element('div').style(
                                    'border-radius:var(--radius-md);border:1px solid var(--surface-border);'
                                    'padding:8px 10px;background:var(--surface-alt);cursor:pointer;'
                                    'transition:border-color .15s,background .15s;'
                                ).on('click', lambda _, c=cust: ctx.on_customer_selected(c)):
                                    with ui.row().classes('items-center gap-2').style('margin-bottom:4px;'):
                                        with ui.element('div').style(
                                            'width:22px;height:22px;border-radius:var(--radius-sm);flex-shrink:0;'
                                            'background:var(--brand-grad-badge);'
                                            'display:flex;align-items:center;justify-content:center;'
                                            'font-size:var(--fs-xs);font-weight:700;color:var(--accent);'):
                                            ui.label(_initial)
                                        ui.label(_cust_name).style(
                                            'font-size:var(--fs-sm);font-weight:600;color:var(--text);'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                    ui.label('Klicken zum Öffnen →').style(
                                        'font-size:var(--fs-xs);color:var(--primary);')
                    else:
                        ui.label('Kein Projekt an diesem Tag.').style(
                            'font-size:var(--fs-xs);color:var(--text-light);margin-top:4px;')

            def _render_mini_cal():
                _cal_body.clear()
                y, m = _cal_view['year'], _cal_view['month']
                proj_dates = all_dates
                month_name = MONTH_NAMES_DE.get(m, str(m))
                sel = _cal_view.get('selected')
                with _cal_body:
                    # Navigation
                    with ui.row().classes('w-full items-center justify-between').style('margin-bottom:8px;'):
                        ui.button(icon='chevron_left', on_click=lambda: _nav_cal(-1)).props(
                            'flat round dense').style('color:var(--text-muted);')
                        ui.label(f'{month_name} {y}').style(
                            'font-size:var(--fs-md);font-weight:700;color:var(--text);')
                        ui.button(icon='chevron_right', on_click=lambda: _nav_cal(1)).props(
                            'flat round dense').style('color:var(--text-muted);')
                    # Wochentag-Header
                    with ui.row().classes('w-full').style('gap:0;margin-bottom:2px;'):
                        for wd in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']:
                            ui.label(wd).style(
                                'width:14.28%;text-align:center;'
                                'font-size:var(--fs-xs);font-weight:700;color:var(--text-light);padding:2px 0;')
                    # Wochen
                    cal_obj = _cal_mod.Calendar(firstweekday=0)
                    for week in cal_obj.monthdayscalendar(y, m):
                        with ui.row().classes('w-full').style('gap:2px;margin-bottom:2px;'):
                            for day_num in week:
                                if day_num == 0:
                                    ui.element('div').style('flex:1;')
                                else:
                                    day_str = f'{y}-{m:02d}-{day_num:02d}'
                                    customers_day = proj_dates.get(day_str, [])
                                    cnt = len(customers_day)
                                    is_today = (day_num == _today.day and m == _today.month and y == _today.year)
                                    is_sel = (day_str == sel)
                                    if is_sel:
                                        cell_bg = 'background:var(--bg-primary);border-color:var(--bg-primary);'
                                        num_clr = '#fff'
                                    elif cnt > 0:
                                        cell_bg = 'background:var(--bg-info-soft);border-color:var(--info);'
                                        num_clr = 'var(--info)'
                                    elif is_today:
                                        cell_bg = 'background:var(--bg-info-soft);border-color:var(--info);'
                                        num_clr = 'var(--info)'
                                    else:
                                        cell_bg = 'background:var(--surface-alt);border-color:transparent;'
                                        num_clr = 'var(--text-muted)'
                                    with ui.element('div').style(
                                        f'flex:1;padding:4px 2px;cursor:pointer;text-align:center;'
                                        f'border-radius:var(--radius-sm);border:1px solid;{cell_bg}'
                                        f'transition:background .12s,border-color .12s;'
                                    ).on('click', lambda _, ds=day_str, cd=customers_day:
                                         (_show_day_preview(ds, cd), _render_mini_cal())):
                                        ui.label(str(day_num)).style(
                                            f'font-size:var(--fs-sm);font-weight:{"700" if cnt>0 or is_today else "500"};'
                                            f'color:{num_clr};line-height:1.6;display:block;')
                                        if cnt > 0 and not is_sel:
                                            ui.element('div').style(
                                                'width:4px;height:4px;border-radius:50%;'
                                                'background:var(--info);margin:0 auto;margin-top:-2px;')

            def _nav_cal(delta: int):
                mo = _cal_view['month'] + delta
                yr = _cal_view['year']
                if mo < 1:
                    mo, yr = 12, yr - 1
                elif mo > 12:
                    mo, yr = 1, yr + 1
                _cal_view['month'], _cal_view['year'] = mo, yr
                _render_mini_cal()

            _render_mini_cal()
