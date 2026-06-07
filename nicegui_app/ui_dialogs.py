# -*- coding: utf-8 -*-
"""UI-Dialoge fuer index_page().

Closures aus index_page() werden via `ctx` (SimpleNamespace) uebergeben.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

from nicegui import ui

from nicegui_app.app_settings import settings, save_settings as _save_settings_to_file



LANGUAGES = ['Auto-Erkennung', 'Deutsch', 'Englisch', 'Franz\u00f6sisch', 'Spanisch',
             'Italienisch', 'Niederl\u00e4ndisch', 'Polnisch', 'Tschechisch', 'Russisch',
             'Chinesisch', 'Japanisch', 'Koreanisch', 'Arabisch', 'T\u00fcrkisch']


def open_settings_dialog() -> None:
    """Öffnet den Einstellungen-Dialog (Projektpfad, Glossarpfad, Sprachen, Prüftiefe, Normzeile)."""
    with ui.dialog().props('persistent') as dlg, ui.card().style('width:520px;'):
        ui.label('Einstellungen').classes('t-title')
        with ui.column().classes('w-full gap-4'):

            def _make_path_row(label_text: str, current_val: str) -> 'ui.input':
                ui.label(label_text).style('font-size:13px;font-weight:600;color:var(--text);')
                with ui.row().classes('w-full items-end gap-2'):
                    inp = ui.input('Pfad', value=current_val).classes('flex-grow').props('outlined dense')

                    def _browse(target_inp=inp):
                        with ui.dialog() as bdlg, ui.card().style('width:500px;max-height:400px;'):
                            ui.label('Ordner wählen').style('font-size:14px;font-weight:700;')
                            current = {'path': target_inp.value or str(Path.home())}
                            path_label = ui.label(current['path']).style(
                                'font-size:12px;color:var(--text-muted);word-break:break-all;')
                            folder_list = ui.column().classes('w-full gap-0').style(
                                'max-height:250px;overflow-y:auto;')

                            def _render_folders():
                                folder_list.clear()
                                p = current['path']
                                with folder_list:
                                    parent = str(Path(p).parent)
                                    if parent != p:
                                        with ui.row().classes('w-full items-center cursor-pointer gap-2').style(
                                            'padding:6px 8px;border-radius:4px;'
                                        ).on('click', lambda: _nav(parent)):
                                            ui.icon('arrow_upward', size='xs').style('color:var(--text-muted);')
                                            ui.label('..').style('font-size:12px;color:var(--text-muted);')
                                    try:
                                        dirs = sorted([d for d in os.listdir(p)
                                            if os.path.isdir(os.path.join(p, d)) and not d.startswith('.')])
                                        for d in dirs[:30]:
                                            with ui.row().classes('w-full items-center cursor-pointer gap-2').style(
                                                'padding:6px 8px;border-radius:4px;'
                                            ).on('click', lambda _, dd=d: _nav(os.path.join(current['path'], dd))):
                                                ui.icon('folder', size='xs').style('color:var(--accent);')
                                                ui.label(d).style('font-size:12px;color:var(--text);')
                                    except PermissionError:
                                        ui.label('Zugriff verweigert').style('font-size:12px;color:var(--error);')

                            def _nav(new_path):
                                current['path'] = new_path
                                path_label.set_text(new_path)
                                _render_folders()

                            _render_folders()
                            with ui.row().classes('w-full justify-end gap-2').style('margin-top:8px;'):
                                ui.button('Abbrechen', on_click=bdlg.close).props('flat no-caps')
                                def _select(ti=target_inp):
                                    ti.value = current['path']
                                    bdlg.close()
                                ui.button('Auswählen', on_click=_select).props('no-caps unelevated').style(
                                    'background:var(--bg-primary);color:var(--text-inverse);')
                        bdlg.open()

                    ui.button(icon='folder_open', on_click=_browse).props('flat dense round color=primary')
                ui.label(f'Aktuell: {current_val or "nicht gesetzt"}').style(
                    'font-size:12px;color:var(--text-light);word-break:break-all;margin-top:-4px;')
                return inp

            base_input = _make_path_row('Projektordner', settings.get('projects_base_path', ''))
            ui.separator()
            glossary_input = _make_path_row('Glossar-Ordner', settings.get('glossaries_path', ''))
            ui.separator()
            lang_src = ui.select(LANGUAGES, value=settings.get('src_lang', 'Auto-Erkennung'),
                label='Standard-Quellsprache').classes('w-full')
            lang_tgt = ui.select(LANGUAGES, value=settings.get('tgt_lang', 'Auto-Erkennung'),
                label='Standard-Zielsprache').classes('w-full')
            depth_sel = ui.select(['Schnell', 'Mittel', 'Umfangreich'],
                value=settings.get('depth', 'Mittel'), label='Prüftiefe').classes('w-full')
            ui.separator()
            ui.label('Normzeilen-Berechnung').style('font-size:13px;font-weight:600;color:var(--text);')
            with ui.row().classes('w-full items-center gap-2'):
                norm_input = ui.number(label='Anschläge pro Normzeile',
                    value=settings.get('chars_per_norm_line', 36),
                    min=30, max=100, step=1).classes('w-40').props('dense outlined')
                ui.label('(Standard: 36)').style('font-size:12px;color:var(--text-light);')
            with ui.row().classes('w-full justify-end gap-2').style('margin-top:8px;'):
                ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')

                def _save():
                    settings['project_path'] = base_input.value
                    settings['projects_base_path'] = base_input.value
                    settings['glossaries_path'] = glossary_input.value
                    settings['src_lang'] = lang_src.value
                    settings['tgt_lang'] = lang_tgt.value
                    settings['depth'] = depth_sel.value
                    settings['chars_per_norm_line'] = int(norm_input.value or 36)
                    _save_settings_to_file(
                        Path(__file__).parent.parent / 'checker_config.json', settings)
                    ui.notify('Einstellungen gespeichert', type='positive')
                    dlg.close()
                ui.button('Speichern', on_click=_save).props('no-caps unelevated').style(
                    'background:var(--bg-primary);color:var(--text-inverse);')
    dlg.open()


def show_pairing_dialog(ctx: SimpleNamespace) -> None:
    """Dialog zum manuellen Paaren von Quell- und Ziel-Dateien.

    ctx braucht: s, refresh_pairing_display(), update_start_btn().
    """
    s = ctx.s
    pairs = list(s.get('paired_results', []))
    unmatched_src = list(s.get('unmatched_src', []))
    unmatched_tgt = list(s.get('unmatched_tgt', []))
    with ui.dialog() as dlg, ui.card().style('width:640px;max-width:90vw;padding:24px;'):
        with ui.row().classes('w-full items-center gap-3').style('margin-bottom:16px;'):
            ui.icon('link', size='md').style('color:var(--primary);')
            with ui.column().classes('gap-0'):
                ui.label('Dateipaarung').style('font-size:16px;font-weight:700;color:var(--primary);')
                ui.label('Zuordnung anpassen oder ungepaarte Dateien verbinden').style(
                    'font-size:12px;color:var(--text-muted);')

        pair_list = ui.column().classes('w-full gap-2')

        def _render():
            pair_list.clear()
            with pair_list:
                if pairs:
                    ui.label(f'{len(pairs)} Paar{"e" if len(pairs) != 1 else ""}').style(
                        'font-size:12px;font-weight:600;color:var(--success);margin-bottom:4px;')
                for i, p in enumerate(pairs):
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:var(--bg-success-tint);border:1px solid var(--border-success);'
                        'border-radius:8px;display:flex;align-items:center;gap:12px;'
                    ):
                        ui.icon('check_circle', size='sm').style('color:var(--success);flex-shrink:0;')
                        with ui.column().classes('flex-grow gap-0 min-w-0'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('description', size='xs').style('color:var(--primary);')
                                ui.label(os.path.basename(p.get('source', ''))).style(
                                    'font-size:13px;font-weight:600;color:var(--primary);')
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('translate', size='xs').style('color:var(--success);')
                                ui.label(os.path.basename(p.get('translation', ''))).style(
                                    'font-size:13px;font-weight:500;color:var(--success);')

                        def _unpair(idx=i):
                            pair = pairs.pop(idx)
                            unmatched_src.append(pair['source'])
                            unmatched_tgt.append(pair['translation'])
                            _render()
                        ui.button(icon='link_off', on_click=_unpair).props(
                            'flat dense round').style('color:var(--text-light);')

                if unmatched_src or unmatched_tgt:
                    ui.element('div').style('width:100%;height:1px;background:var(--surface-border);margin:8px 0;')

                if unmatched_src:
                    ui.label('Ohne Partner (Ausgangstexte)').style(
                        'font-size:12px;font-weight:600;color:var(--warning);')
                for j, fp in enumerate(unmatched_src):
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:var(--bg-warning-tint);border:1px solid var(--border-warning);'
                        'border-radius:8px;display:flex;align-items:center;gap:12px;'
                    ):
                        ui.icon('description', size='sm').style('color:var(--primary);flex-shrink:0;')
                        ui.label(os.path.basename(fp)).style(
                            'font-size:13px;font-weight:500;color:var(--text);flex-grow:1;')
                        if unmatched_tgt:
                            tgt_options = {os.path.basename(t): t for t in unmatched_tgt}
                            default_val = list(tgt_options.keys())[0] if len(tgt_options) == 1 else None
                            sel = ui.select(
                                options=list(tgt_options.keys()),
                                value=default_val,
                                label='\u00dcbersetzung w\u00e4hlen',
                                with_input=True,
                            ).style('min-width:180px;').props('dense outlined')

                            def _manual_pair(src_idx=j, select=sel):
                                tgt_name = getattr(select, 'value', None)
                                if not tgt_name:
                                    return
                                tgt_path = tgt_options.get(tgt_name, '')
                                if tgt_path:
                                    pairs.append({'source': unmatched_src[src_idx],
                                                  'translation': tgt_path, 'similarity': 1.0})
                                    unmatched_src.pop(src_idx)
                                    unmatched_tgt.remove(tgt_path)
                                    _render()
                            ui.button('Verbinden', icon='link',
                                      on_click=_manual_pair).props('dense no-caps color=primary size=sm')

                if unmatched_tgt:
                    ui.label('Ohne Partner (\u00dcbersetzungen)').style(
                        'font-size:12px;font-weight:600;color:var(--warning);margin-top:8px;')
                for fp in unmatched_tgt:
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:var(--bg-warning-tint);border:1px solid var(--border-warning);'
                        'border-radius:8px;display:flex;align-items:center;gap:8px;'
                    ):
                        ui.icon('translate', size='sm').style('color:var(--success);')
                        ui.label(os.path.basename(fp)).style('font-size:13px;color:var(--text);')

        _render()

        ui.element('div').style('width:100%;height:1px;background:var(--surface-border);margin:16px 0 12px 0;')
        with ui.row().classes('w-full justify-end gap-3'):
            ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps').style('font-size:13px;')

            def _save():
                s['paired_results'] = pairs
                s['unmatched_src'] = unmatched_src
                s['unmatched_tgt'] = unmatched_tgt
                ctx.refresh_pairing_display()
                ctx.update_start_btn()
                dlg.close()
                ui.notify(f'{len(pairs)} Paare gespeichert', type='positive')
            ui.button('\u00dcbernehmen', icon='check', on_click=_save).props(
                'no-caps unelevated').style('background:var(--bg-primary);color:var(--text-inverse);')
    dlg.open()


def show_keyboard_help() -> None:
    """Tastatur-Kuerzel-Dialog."""
    with ui.dialog() as dlg, ui.card().style('width:480px;'):
        ui.label('Tastatur-Kuerzel').style(
            'font-size:18px;font-weight:700;color:var(--primary);margin-bottom:8px;')
        shortcuts = [
            ('Strg + Eingabe', 'Analyse starten'),
            ('Esc', 'Analyse abbrechen / Hilfe schliessen'),
            ('Strg + Z', 'Letzte Erledigt-Aktion rueckgaengig'),
            ('j  /  Pfeil ab', 'Nächster Befund'),
            ('k  /  Pfeil auf', 'Vorheriger Befund'),
            ('x  /  Leertaste', 'Aktuellen Befund als erledigt markieren'),
            ('1 / 2 / 3 / 0', 'Filter Kritisch / Wichtig / Hinweis / Alle'),
            ('?', 'Diese Hilfe anzeigen'),
        ]
        for keys, desc in shortcuts:
            with ui.row().classes('w-full items-center gap-3').style(
                'padding:6px 0;border-bottom:1px solid var(--surface-border-light);'
            ):
                ui.label(keys).style(
                    'font-family:monospace;font-size:12px;font-weight:700;'
                    'color:var(--primary);background:var(--bg-muted);padding:3px 8px;'
                    'border-radius:4px;min-width:140px;')
                ui.label(desc).style('font-size:13px;color:var(--text-muted);')
        ui.button('Schliessen', on_click=dlg.close).props(
            'flat dense no-caps').style('margin-top:12px;')
    dlg.open()


def show_archive_confirm(ctx: SimpleNamespace, customer: str, parent_dlg) -> None:
    """Bestaetigungs-Dialog fuer Kunden-Archivierung.

    ctx braucht: s, archive_customer(customer), refresh_customer_info().
    """
    s = ctx.s
    with ui.dialog() as cdlg, ui.card().style('width:360px;'):
        ui.label(f'Kunde "{customer}" archivieren?').classes('t-heading')
        ui.label('Der Kundenordner wird nach _archiv/ verschoben.').style(
            'font-size:12px;color:var(--text-muted);')
        with ui.row().classes('w-full justify-end gap-2').style('margin-top:12px;'):
            ui.button('Abbrechen', on_click=cdlg.close).props('flat no-caps')

            def _do():
                if ctx.archive_customer(customer):
                    ui.notify(f'Kunde "{customer}" archiviert', type='positive')
                    s['active_customer'] = ''
                    s['active_project_path'] = ''
                    ctx.refresh_customer_info()
                else:
                    ui.notify('Archivierung fehlgeschlagen', type='negative')
                cdlg.close()
                parent_dlg.close()
            ui.button('Archivieren', icon='archive', on_click=_do).props('no-caps color=negative')
    cdlg.open()


def show_edit_customer_dialog(ctx: SimpleNamespace, customer: str) -> None:
    """Kunde bearbeiten Dialog.

    ctx braucht: s, load_customer_info, save_customer_info, archive_customer,
    refresh_customer_info.
    """
    info = ctx.load_customer_info(customer)
    with ui.dialog().props('persistent') as dlg, ui.card().style('width:480px;'):
        ui.label(f'Kunde bearbeiten: {customer}').classes('t-title')
        ui.separator()
        typ = info.get('typ', 'firma')
        inp_branche = ui.input('Branche', value=info.get('branche', '')).classes('w-full').props('dense outlined') if typ == 'firma' else None
        inp_ansprech = ui.input('Ansprechpartner', value=info.get('ansprechpartner', '')).classes('w-full').props('dense outlined') if typ == 'firma' else None
        inp_email = ui.input('E-Mail', value=info.get('email', '')).classes('w-full').props('dense outlined')
        inp_tel = ui.input('Telefon', value=info.get('telefon', '')).classes('w-full').props('dense outlined')
        inp_sprache = ui.select(['Deutsch', 'Englisch', 'Französisch', 'Spanisch', 'Italienisch'],
            value=info.get('sprache', 'Deutsch'), label='Arbeitssprache').classes('w-full').props('dense outlined')
        inp_notiz = ui.textarea('Notizen', value=info.get('notizen', '')).classes('w-full').props('dense outlined rows=3')
        fav_cb = ui.checkbox('Favoritenkunde', value=info.get('favorit', False)).props('dense')
        ui.separator()
        with ui.row().classes('w-full justify-between'):
            ui.button('Archivieren', icon='archive',
                      on_click=lambda: show_archive_confirm(ctx, customer, dlg)).props('flat no-caps color=negative')
            with ui.row().classes('gap-2'):
                ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')

                def _save():
                    info['email'] = inp_email.value.strip()
                    info['telefon'] = inp_tel.value.strip()
                    info['sprache'] = inp_sprache.value
                    info['notizen'] = inp_notiz.value.strip()
                    info['favorit'] = fav_cb.value
                    if inp_branche:
                        info['branche'] = inp_branche.value.strip()
                    if inp_ansprech:
                        info['ansprechpartner'] = inp_ansprech.value.strip()
                    ctx.save_customer_info(customer, info)
                    ui.notify('Kundendaten gespeichert', type='positive')
                    dlg.close()
                    ctx.refresh_customer_info()
                ui.button('Speichern', icon='save', on_click=_save).props('no-caps unelevated').style(
                    'background:var(--bg-primary);color:var(--text-inverse);')
    dlg.open()


def show_new_customer_dialog(ctx: SimpleNamespace) -> None:
    """Neuen Kunden anlegen (Firma / Privat).

    ctx braucht: finalize_new_customer(name, info).
    """
    with ui.dialog().props('persistent') as dlg, ui.card().style('width:520px;max-width:90vw;'):
        ui.label('Neuer Kunde').classes('t-title')
        ui.separator()
        with ui.tabs().classes('w-full') as tabs:
            tab_firma = ui.tab('Firmenkunde', icon='business')
            tab_privat = ui.tab('Privatkunde', icon='person')
        with ui.tab_panels(tabs, value=tab_firma).classes('w-full'):
            with ui.tab_panel(tab_firma):
                f_name = ui.input('Firmenname *', placeholder='z.B. Mueller GmbH').classes('w-full').props('dense outlined')
                with ui.row().classes('w-full gap-2'):
                    f_branche = ui.input('Branche').classes('flex-grow').props('dense outlined')
                    f_sprache = ui.select(['Deutsch', 'Englisch', 'Französisch', 'Spanisch', 'Italienisch'],
                        value='Deutsch', label='Arbeitssprache').classes('w-32').props('dense outlined')
                f_ansprech = ui.input('Ansprechpartner').classes('w-full').props('dense outlined')
                with ui.row().classes('w-full gap-2'):
                    f_email = ui.input('E-Mail').classes('flex-grow').props('dense outlined')
                    f_tel = ui.input('Telefon').classes('w-40').props('dense outlined')
                f_notiz = ui.textarea('Notizen').classes('w-full').props('dense outlined rows=2')

                def _save_firma():
                    name = f_name.value.strip()
                    if not name:
                        ui.notify('Firmenname ist Pflichtfeld', type='warning')
                        return
                    ctx.finalize_new_customer(name, {
                        'typ': 'firma', 'name': name, 'branche': f_branche.value.strip(),
                        'sprache': f_sprache.value, 'ansprechpartner': f_ansprech.value.strip(),
                        'email': f_email.value.strip(), 'telefon': f_tel.value.strip(),
                        'notizen': f_notiz.value.strip(),
                    })
                    dlg.close()
                with ui.row().classes('w-full justify-end gap-2').style('margin-top:12px;'):
                    ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
                    ui.button('Firmenkunde anlegen', icon='business',
                              on_click=_save_firma).props('no-caps unelevated').style(
                        'background:var(--bg-primary);color:var(--text-inverse);')
            with ui.tab_panel(tab_privat):
                with ui.row().classes('w-full gap-2'):
                    p_vorname = ui.input('Vorname').classes('flex-grow').props('dense outlined')
                    p_nachname = ui.input('Nachname *').classes('flex-grow').props('dense outlined')
                with ui.row().classes('w-full gap-2'):
                    p_sprache = ui.select(['Deutsch', 'Englisch', 'Französisch', 'Spanisch', 'Italienisch'],
                        value='Deutsch', label='Arbeitssprache').classes('w-32').props('dense outlined')
                    p_email = ui.input('E-Mail').classes('flex-grow').props('dense outlined')
                p_tel = ui.input('Telefon').classes('w-full').props('dense outlined')
                p_notiz = ui.textarea('Notizen').classes('w-full').props('dense outlined rows=2')

                def _save_privat():
                    nachname = p_nachname.value.strip()
                    if not nachname:
                        ui.notify('Nachname ist Pflichtfeld', type='warning')
                        return
                    vorname = p_vorname.value.strip()
                    name = f'{nachname}, {vorname}' if vorname else nachname
                    ctx.finalize_new_customer(name, {
                        'typ': 'privat', 'name': name, 'vorname': vorname, 'nachname': nachname,
                        'sprache': p_sprache.value, 'email': p_email.value.strip(),
                        'telefon': p_tel.value.strip(), 'notizen': p_notiz.value.strip(),
                    })
                    dlg.close()
                with ui.row().classes('w-full justify-end gap-2').style('margin-top:12px;'):
                    ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
                    ui.button('Privatkunde anlegen', icon='person',
                              on_click=_save_privat).props('no-caps unelevated').style(
                        'background:var(--bg-primary);color:var(--text-inverse);')
    dlg.open()


def open_glossary_editor(ctx: SimpleNamespace, tmp_dir: str) -> None:
    """Manuelles Glossar bearbeiten.

    ctx braucht: s, refs, save_and_notify().
    """
    s = ctx.s
    refs = ctx.refs
    search_state = {'q': ''}
    with ui.dialog().props('persistent') as dlg, ui.card().style('width:640px;max-width:90vw;'):
        ui.label('Glossar bearbeiten').style(
            'font-size:16px;font-weight:700;color:var(--text);')
        ui.label(
            'Manuelle Begriffe werden zusätzlich zum geladenen Glossar geprüft.'
        ).style('font-size:12px;color:var(--text-muted);margin-bottom:8px;')

        with ui.row().classes('w-full items-center gap-2').style('margin-bottom:6px;'):
            search_input = ui.input(placeholder='Begriffe suchen...').props(
                'dense outlined clearable').classes('flex-1')
            count_lbl = ui.label('').style('font-size:11px;color:var(--text-muted);')

        list_container = ui.column().classes('w-full gap-1').style(
            'max-height:50vh;overflow-y:auto;border:1px solid var(--surface-border);'
            'border-radius:var(--radius-sm);padding:8px;background:var(--surface-alt);'
        )

        def _commit(new_terms) -> bool:
            s['manual_glossary_terms'] = new_terms
            if refs.get('glossary_count_label'):
                refs['glossary_count_label'].set_text(f'{len(new_terms)} Begriffe')
            try:
                ok = ctx.save_and_notify() is not False
            except Exception:
                ok = False
            if not ok:
                ui.notify('Speichern fehlgeschlagen', type='negative')
            return ok

        def _redraw():
            list_container.clear()
            cur = dict(s.get('manual_glossary_terms', {}) or {})
            q = (search_state['q'] or '').strip().lower()
            if q:
                cur = {k: v for k, v in cur.items()
                       if q in k.lower() or q in str(v).lower()}
            total = len(s.get('manual_glossary_terms', {}) or {})
            if q:
                count_lbl.set_text(f'{len(cur)} / {total}')
            else:
                count_lbl.set_text(f'{total} Begriffe')
            with list_container:
                if not cur:
                    msg = 'Keine Treffer.' if q else 'Noch keine Begriffe.'
                    ui.label(msg).style(
                        'font-size:12px;color:var(--text-light);padding:12px;text-align:center;')
                    return
                for src_term in sorted(cur.keys(), key=str.lower):
                    tgt_term = cur[src_term]
                    with ui.row().classes('w-full items-center gap-2').style(
                        'background:var(--surface);border:1px solid var(--surface-border);'
                        'border-radius:4px;padding:4px 8px;'
                    ):
                        si = ui.input(value=src_term).props('dense outlined').classes('flex-1')
                        ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
                        ti = ui.input(value=tgt_term).props('dense outlined').classes('flex-1')

                        def _save_row(orig=src_term, si_in=si, ti_in=ti):
                            new = dict(s.get('manual_glossary_terms', {}) or {})
                            new.pop(orig, None)
                            ns, nt = si_in.value.strip(), ti_in.value.strip()
                            if ns and nt:
                                new[ns] = nt
                            if _commit(new):
                                ui.notify('Gespeichert', type='positive')

                        def _del_row(orig=src_term):
                            new = dict(s.get('manual_glossary_terms', {}) or {})
                            new.pop(orig, None)
                            _commit(new)
                            _redraw()

                        ui.button(icon='save', on_click=_save_row).props(
                            'flat dense round size=sm').style('color:var(--success);').tooltip('Speichern')
                        ui.button(icon='delete', on_click=_del_row).props(
                            'flat dense round size=sm').style('color:var(--error);').tooltip('Löschen')

        def _on_search(e):
            search_state['q'] = getattr(e, 'value', '') or ''
            _redraw()

        search_input.on('update:model-value', _on_search)

        _redraw()

        ui.separator().style('margin:8px 0;')
        ui.label('Neuen Begriff hinzufügen').style(
            'font-size:12px;font-weight:700;color:var(--text);')
        with ui.row().classes('w-full items-center gap-2'):
            new_src = ui.input(placeholder='Quelle').props('dense outlined').classes('flex-1')
            ui.icon('arrow_forward', size='xs').style('color:var(--accent);')
            new_tgt = ui.input(placeholder='Übersetzung').props('dense outlined').classes('flex-1')

            def _add_new():
                ns, nt = new_src.value.strip(), new_tgt.value.strip()
                if not ns or not nt:
                    ui.notify('Beide Felder ausfüllen', type='warning')
                    return
                new = dict(s.get('manual_glossary_terms', {}) or {})
                new[ns] = nt
                _commit(new)
                new_src.value = ''
                new_tgt.value = ''
                _redraw()

            ui.button(icon='add', on_click=_add_new).props(
                'unelevated dense round size=sm').style('background:var(--bg-primary);color:var(--text-inverse);')

        with ui.row().classes('w-full justify-end gap-2').style('margin-top:8px;'):
            def _export_json():
                try:
                    path = os.path.join(tmp_dir, 'glossar_export.json')
                    with open(path, 'w', encoding='utf-8') as fh:
                        json.dump(s.get('manual_glossary_terms', {}) or {},
                                  fh, ensure_ascii=False, indent=2)
                    ui.download(path)
                except Exception as exc:
                    ui.notify(f'Export fehlgeschlagen: {exc}', type='negative')

            ui.button('Als JSON exportieren', icon='download',
                on_click=_export_json).props('outline dense no-caps size=sm')
            ui.button('Schließen', on_click=dlg.close).props(
                'unelevated dense no-caps size=sm').style('background:var(--bg-primary);color:var(--text-inverse);')

    dlg.open()
