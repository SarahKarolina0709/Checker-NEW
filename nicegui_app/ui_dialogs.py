# -*- coding: utf-8 -*-
"""UI-Dialoge fuer index_page().

Closures aus index_page() werden via `ctx` (SimpleNamespace) uebergeben.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from types import SimpleNamespace

from nicegui import ui

from nicegui_app.app_settings import settings

_logger = logging.getLogger(__name__)

LANGUAGES = ['Auto-Erkennung', 'Deutsch', 'Englisch', 'Franz\u00f6sisch', 'Spanisch',
             'Italienisch', 'Niederl\u00e4ndisch', 'Polnisch', 'Tschechisch', 'Russisch',
             'Chinesisch', 'Japanisch', 'Koreanisch', 'Arabisch', 'T\u00fcrkisch']


def open_settings_dialog() -> None:
    """\u00d6ffnet den Einstellungen-Dialog (Projektpfad, Sprachen, Pr\u00fcftiefe, Normzeile)."""
    with ui.dialog() as dlg, ui.card().style('width:500px;'):
        ui.label('Einstellungen').classes('t-title')
        with ui.column().classes('w-full gap-4'):
            ui.label('Projektordner').style('font-size:13px;font-weight:600;color:#1f2937;')
            with ui.row().classes('w-full items-end gap-2'):
                base_input = ui.input('Pfad zum Projektordner',
                    value=settings.get('projects_base_path', '')).classes('flex-grow').props('outlined dense')

                def _browse_folder():
                    with ui.dialog() as bdlg, ui.card().style('width:500px;max-height:400px;'):
                        ui.label('Ordner w\u00e4hlen').style('font-size:14px;font-weight:700;')
                        current = {'path': base_input.value or str(Path.home())}
                        path_label = ui.label(current['path']).style(
                            'font-size:12px;color:#6b7280;word-break:break-all;')
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
                                        ui.icon('arrow_upward', size='xs').style('color:#6b7280;')
                                        ui.label('..').style('font-size:12px;color:#6b7280;')
                                try:
                                    dirs = sorted([d for d in os.listdir(p)
                                        if os.path.isdir(os.path.join(p, d)) and not d.startswith('.')])
                                    for d in dirs[:30]:
                                        with ui.row().classes('w-full items-center cursor-pointer gap-2').style(
                                            'padding:6px 8px;border-radius:4px;'
                                        ).on('click', lambda _, dd=d: _nav(os.path.join(current['path'], dd))):
                                            ui.icon('folder', size='xs').style('color:#d4af37;')
                                            ui.label(d).style('font-size:12px;color:#1f2937;')
                                except PermissionError:
                                    ui.label('Zugriff verweigert').style('font-size:12px;color:#ef4444;')

                        def _nav(new_path):
                            current['path'] = new_path
                            path_label.set_text(new_path)
                            _render_folders()

                        _render_folders()
                        with ui.row().classes('w-full justify-end gap-2').style('margin-top:8px;'):
                            ui.button('Abbrechen', on_click=bdlg.close).props('flat no-caps')

                            def _select():
                                base_input.value = current['path']
                                bdlg.close()
                            ui.button('Ausw\u00e4hlen', on_click=_select).props('no-caps unelevated').style(
                                'background:#0f2744;color:white;')
                    bdlg.open()
                ui.button(icon='folder_open', on_click=_browse_folder).props(
                    'flat dense round color=primary')
            ui.label(f'Aktuell: {settings.get("projects_base_path", "nicht gesetzt")}').style(
                'font-size:12px;color:#9ca3af;word-break:break-all;margin-top:-4px;')
            ui.separator()
            lang_src = ui.select(LANGUAGES, value=settings.get('src_lang', 'Auto-Erkennung'),
                label='Standard-Quellsprache').classes('w-full')
            lang_tgt = ui.select(LANGUAGES, value=settings.get('tgt_lang', 'Auto-Erkennung'),
                label='Standard-Zielsprache').classes('w-full')
            depth_sel = ui.select(['Schnell', 'Mittel', 'Umfangreich'],
                value=settings.get('depth', 'Mittel'), label='Pr\u00fcftiefe').classes('w-full')
            ui.separator()
            ui.label('Normzeilen-Berechnung').style('font-size:13px;font-weight:600;color:#1f2937;')
            with ui.row().classes('w-full items-center gap-2'):
                norm_input = ui.number(label='Anschl\u00e4ge pro Normzeile',
                    value=settings.get('chars_per_norm_line', 36),
                    min=30, max=100, step=1).classes('w-40').props('dense outlined')
                ui.label('(Standard: 36)').style('font-size:12px;color:#9ca3af;')
            with ui.row().classes('w-full justify-end gap-2').style('margin-top:8px;'):
                ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')

                def _save():
                    settings['project_path'] = base_input.value
                    settings['projects_base_path'] = base_input.value
                    settings['src_lang'] = lang_src.value
                    settings['tgt_lang'] = lang_tgt.value
                    settings['depth'] = depth_sel.value
                    settings['chars_per_norm_line'] = int(norm_input.value or 36)
                    try:
                        cfg_path = Path(__file__).parent.parent / 'checker_config.json'
                        cfg = {}
                        if cfg_path.exists():
                            with open(cfg_path, 'r', encoding='utf-8') as f:
                                cfg = json.load(f)
                        cfg['projects_base_path'] = settings['projects_base_path']
                        cfg['default_src_lang'] = settings['src_lang']
                        cfg['default_tgt_lang'] = settings['tgt_lang']
                        cfg['depth'] = settings['depth']
                        cfg['chars_per_norm_line'] = settings['chars_per_norm_line']
                        with open(cfg_path, 'w', encoding='utf-8') as f:
                            json.dump(cfg, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        _logger.warning('Settings Persist Fehler: %s', e)
                    ui.notify('Einstellungen gespeichert', type='positive')
                    dlg.close()
                ui.button('Speichern', on_click=_save).props('no-caps unelevated').style(
                    'background:#0f2744;color:white;')
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
            ui.icon('link', size='md').style('color:#0f2744;')
            with ui.column().classes('gap-0'):
                ui.label('Dateipaarung').style('font-size:16px;font-weight:700;color:#0f2744;')
                ui.label('Zuordnung anpassen oder ungepaarte Dateien verbinden').style(
                    'font-size:12px;color:#6b7280;')

        pair_list = ui.column().classes('w-full gap-2')

        def _render():
            pair_list.clear()
            with pair_list:
                if pairs:
                    ui.label(f'{len(pairs)} Paar{"e" if len(pairs) != 1 else ""}').style(
                        'font-size:12px;font-weight:600;color:#16a34a;margin-bottom:4px;')
                for i, p in enumerate(pairs):
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:#f0fdf4;border:1px solid #bbf7d0;'
                        'border-radius:8px;display:flex;align-items:center;gap:12px;'
                    ):
                        ui.icon('check_circle', size='sm').style('color:#16a34a;flex-shrink:0;')
                        with ui.column().classes('flex-grow gap-0 min-w-0'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('description', size='xs').style('color:#0f2744;')
                                ui.label(os.path.basename(p.get('source', ''))).style(
                                    'font-size:13px;font-weight:600;color:#0f2744;')
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('translate', size='xs').style('color:#16a34a;')
                                ui.label(os.path.basename(p.get('translation', ''))).style(
                                    'font-size:13px;font-weight:500;color:#16a34a;')

                        def _unpair(idx=i):
                            pair = pairs.pop(idx)
                            unmatched_src.append(pair['source'])
                            unmatched_tgt.append(pair['translation'])
                            _render()
                        ui.button(icon='link_off', on_click=_unpair).props(
                            'flat dense round').style('color:#9ca3af;')

                if unmatched_src or unmatched_tgt:
                    ui.element('div').style('width:100%;height:1px;background:#e2e8f0;margin:8px 0;')

                if unmatched_src:
                    ui.label('Ohne Partner (Ausgangstexte)').style(
                        'font-size:12px;font-weight:600;color:#ea580c;')
                for j, fp in enumerate(unmatched_src):
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:#fff7ed;border:1px solid #fed7aa;'
                        'border-radius:8px;display:flex;align-items:center;gap:12px;'
                    ):
                        ui.icon('description', size='sm').style('color:#0f2744;flex-shrink:0;')
                        ui.label(os.path.basename(fp)).style(
                            'font-size:13px;font-weight:500;color:#1f2937;flex-grow:1;')
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
                        'font-size:12px;font-weight:600;color:#ea580c;margin-top:8px;')
                for fp in unmatched_tgt:
                    with ui.element('div').style(
                        'width:100%;padding:10px 14px;background:#fff7ed;border:1px solid #fed7aa;'
                        'border-radius:8px;display:flex;align-items:center;gap:8px;'
                    ):
                        ui.icon('translate', size='sm').style('color:#16a34a;')
                        ui.label(os.path.basename(fp)).style('font-size:13px;color:#1f2937;')

        _render()

        ui.element('div').style('width:100%;height:1px;background:#e2e8f0;margin:16px 0 12px 0;')
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
                'no-caps unelevated').style('background:#0f2744;color:white;')
    dlg.open()


def show_keyboard_help() -> None:
    """Tastatur-Kuerzel-Dialog."""
    with ui.dialog() as dlg, ui.card().style('width:480px;'):
        ui.label('Tastatur-Kuerzel').style(
            'font-size:18px;font-weight:700;color:#0f2744;margin-bottom:8px;')
        shortcuts = [
            ('Strg + Eingabe', 'Analyse starten'),
            ('Esc', 'Analyse abbrechen / Hilfe schliessen'),
            ('Strg + Z', 'Letzte Erledigt-Aktion rueckgaengig'),
            ('j  /  Pfeil ab', 'Naechstes Finding'),
            ('k  /  Pfeil auf', 'Vorheriges Finding'),
            ('x  /  Leertaste', 'Aktuelles Finding als erledigt markieren'),
            ('1 / 2 / 3 / 0', 'Filter Kritisch / Wichtig / Hinweis / Alle'),
            ('?', 'Diese Hilfe anzeigen'),
        ]
        for keys, desc in shortcuts:
            with ui.row().classes('w-full items-center gap-3').style(
                'padding:6px 0;border-bottom:1px solid #f1f5f9;'
            ):
                ui.label(keys).style(
                    'font-family:monospace;font-size:12px;font-weight:700;'
                    'color:#0f2744;background:#f1f5f9;padding:3px 8px;'
                    'border-radius:4px;min-width:140px;')
                ui.label(desc).style('font-size:13px;color:#4b5563;')
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
            'font-size:12px;color:#6b7280;')
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
    with ui.dialog() as dlg, ui.card().style('width:480px;'):
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
                    'background:#0f2744;color:white;')
    dlg.open()


def show_new_customer_dialog(ctx: SimpleNamespace) -> None:
    """Neuen Kunden anlegen (Firma / Privat).

    ctx braucht: finalize_new_customer(name, info).
    """
    with ui.dialog() as dlg, ui.card().style('width:520px;max-width:90vw;'):
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
                        'background:#0f2744;color:white;')
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
                        'background:#0f2744;color:white;')
    dlg.open()


def open_glossary_editor(ctx: SimpleNamespace, tmp_dir: str) -> None:
    """Manuelles Glossar bearbeiten.

    ctx braucht: s, refs, save_and_notify().
    """
    s = ctx.s
    refs = ctx.refs
    search_state = {'q': ''}
    with ui.dialog() as dlg, ui.card().style('width:640px;max-width:90vw;'):
        ui.label('Glossar bearbeiten').style(
            'font-size:16px;font-weight:700;color:#1f2937;')
        ui.label(
            'Manuelle Begriffe werden zusätzlich zum geladenen Glossar geprüft.'
        ).style('font-size:12px;color:#6b7280;margin-bottom:8px;')

        with ui.row().classes('w-full items-center gap-2').style('margin-bottom:6px;'):
            search_input = ui.input(placeholder='Begriffe suchen...').props(
                'dense outlined clearable').classes('flex-1')
            count_lbl = ui.label('').style('font-size:11px;color:#6b7280;')

        list_container = ui.column().classes('w-full gap-1').style(
            'max-height:50vh;overflow-y:auto;border:1px solid #e2e8f0;'
            'border-radius:6px;padding:8px;background:#f8fafc;'
        )

        def _commit(new_terms):
            s['manual_glossary_terms'] = new_terms
            if refs.get('glossary_count_label'):
                refs['glossary_count_label'].set_text(f'{len(new_terms)} Begriffe')
            try:
                ctx.save_and_notify()
            except Exception:
                pass

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
                        'font-size:12px;color:#9ca3af;padding:12px;text-align:center;')
                    return
                for src_term in sorted(cur.keys(), key=str.lower):
                    tgt_term = cur[src_term]
                    with ui.row().classes('w-full items-center gap-2').style(
                        'background:white;border:1px solid #e2e8f0;'
                        'border-radius:4px;padding:4px 8px;'
                    ):
                        si = ui.input(value=src_term).props('dense outlined').classes('flex-1')
                        ui.icon('arrow_forward', size='xs').style('color:#d4af37;')
                        ti = ui.input(value=tgt_term).props('dense outlined').classes('flex-1')

                        def _save_row(orig=src_term, si_in=si, ti_in=ti):
                            new = dict(s.get('manual_glossary_terms', {}) or {})
                            new.pop(orig, None)
                            ns, nt = si_in.value.strip(), ti_in.value.strip()
                            if ns and nt:
                                new[ns] = nt
                            _commit(new)
                            ui.notify('Gespeichert', type='positive')

                        def _del_row(orig=src_term):
                            new = dict(s.get('manual_glossary_terms', {}) or {})
                            new.pop(orig, None)
                            _commit(new)
                            _redraw()

                        ui.button(icon='save', on_click=_save_row).props(
                            'flat dense round size=sm').style('color:#16a34a;').tooltip('Speichern')
                        ui.button(icon='delete', on_click=_del_row).props(
                            'flat dense round size=sm').style('color:#dc2626;').tooltip('Löschen')

        def _on_search(e):
            search_state['q'] = getattr(e, 'value', '') or ''
            _redraw()

        search_input.on('update:model-value', _on_search)

        _redraw()

        ui.separator().style('margin:8px 0;')
        ui.label('Neuen Begriff hinzufügen').style(
            'font-size:12px;font-weight:700;color:#1f2937;')
        with ui.row().classes('w-full items-center gap-2'):
            new_src = ui.input(placeholder='Quelle').props('dense outlined').classes('flex-1')
            ui.icon('arrow_forward', size='xs').style('color:#d4af37;')
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
                'unelevated dense round size=sm').style('background:#0f2744;color:white;')

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
                'unelevated dense no-caps size=sm').style('background:#0f2744;color:white;')

    dlg.open()
