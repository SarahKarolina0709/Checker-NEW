# -*- coding: utf-8 -*-
"""Kunden-Manager Seite.

Registriert Route /kunden via @ui.page-Dekorator beim Import.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List

from nicegui import ui

from nicegui_app.app_settings import settings
from nicegui_app.customers import PROJECT_FOLDERS
from nicegui_app import customers as _customers_mod
from nicegui_app.styles import APP_CSS
from nicegui_app.utils import safe_open_folder, make_keyboard_activatable


@ui.page('/kunden')
def kunden_page():
    ui.add_head_html(APP_CSS)
    with ui.header().classes('items-center px-6 py-0').style(
        'background:var(--brand-grad);min-height:56px;'
    ):
        with ui.row().classes('w-full items-center gap-4'):
            ui.icon('business', size='md').style('color:var(--accent)')
            ui.label('Kunden-Manager').style('font-size:var(--fs-lg);font-weight:700;color:var(--text-inverse);')
            ui.element('div').classes('flex-grow')
            ui.button('Zurück zur Analyse', icon='arrow_back',
                on_click=lambda: ui.navigate.to('/')).props('flat no-caps text-color=white').style('font-size:var(--fs-sm);')
            ui.button('Kalender', icon='calendar_month',
                on_click=lambda: ui.navigate.to('/kalender')).props('flat no-caps text-color=white').style('font-size:var(--fs-sm);')

    base = settings.get('projects_base_path', '')
    customers = _customers_mod.load_customers(base)
    selected = {'name': ''}
    project_detail = None

    with ui.row().classes('w-full gap-0 qf-stack').style('min-height:calc(100vh - 56px);'):
        with ui.column().classes('w-[320px] p-4 gap-2').style(
            'background:var(--surface);border-right:1px solid var(--surface-border);overflow-y:auto;max-height:calc(100vh - 56px);'
        ):
            ui.label('KUNDEN').classes('section-label')
            search_inp = ui.input(placeholder='Kunde suchen...').classes('w-full').props('dense outlined clearable')
            ui.button('Neuer Kunde', icon='person_add',
                on_click=lambda: _new_customer()).props('no-caps outline dense').classes('w-full')
            ui.separator()
            customer_list = ui.column().classes('w-full gap-1')

            def _filter_list(query=''):
                customer_list.clear()
                filtered = _customers_mod.filter_customers(customers, query)
                with customer_list:
                    for cust in filtered:
                        info = _customers_mod.load_customer_info(base, cust)
                        initial = cust[0].upper() if cust else '?'
                        n_proj = len(_customers_mod.list_projects(base, cust))
                        is_sel = selected.get('name') == cust
                        with make_keyboard_activatable(
                            ui.card().classes('w-full cursor-pointer').props('flat bordered').style(
                                f'padding:8px 12px;{"background:var(--bg-info-soft);border-color:var(--border-info);" if is_sel else ""}'
                            ).on('click', lambda _, c=cust: _show_customer(c)),
                            lambda c=cust: _show_customer(c),
                        ):
                            with ui.row().classes('items-center gap-4 w-full'):
                                with ui.element('div').style(
                                    'width:36px;height:36px;border-radius:var(--radius-sm);'
                                    'background:var(--brand-grad-badge);'
                                    'display:flex;align-items:center;justify-content:center;'
                                ):
                                    ui.label(initial).style('color:var(--accent);font-size:var(--fs-lg);font-weight:700;')
                                with ui.column().classes('gap-0 flex-grow'):
                                    ui.label(_customers_mod.display_name(cust)).style('font-size:var(--fs-md);font-weight:600;')
                                    parts = []
                                    if n_proj:
                                        parts.append(f'{n_proj} {"Projekt" if n_proj == 1 else "Projekte"}')
                                    if info.get('branche'):
                                        parts.append(info['branche'])
                                    ui.label(' · '.join(parts) if parts else 'Kein Projekt').style(
                                        'font-size:var(--fs-sm);color:var(--text-muted);')
                    if not filtered:
                        ui.label('Keine Kunden gefunden').style(
                            'font-size:var(--fs-sm);color:var(--text-light);padding:16px 0;text-align:center;')

            # Suche entprellen: filtert erst 250 ms nach dem letzten Tastendruck,
            # statt pro Anschlag N JSON-Reads + Verzeichnis-Scans auszuloesen.
            _search_timer = {'t': None}

            def _on_search(e):
                val = getattr(e, 'value', getattr(e, 'args', '')) or ''
                if _search_timer['t'] is not None:
                    try:
                        _search_timer['t'].cancel()
                    except Exception:
                        pass
                _search_timer['t'] = ui.timer(0.25, lambda: _filter_list(val), once=True)

            search_inp.on('update:model-value', _on_search)
            _filter_list()

        with ui.column().classes('flex-grow p-6 gap-4').style(
            'overflow-y:auto;max-height:calc(100vh - 56px);background:var(--surface-alt);'
        ):
            project_detail = ui.column().classes('w-full gap-4')
            with project_detail:
                with ui.column().classes('w-full items-center justify-center').style(
                    'min-height:65vh;gap:14px;'):
                    ui.icon('business', size='3rem').style('color:var(--text-light)')
                    ui.label('Kunde auswählen').style('font-size:var(--fs-lg);font-weight:600;color:var(--text-muted);')
                    ui.label('Wählen Sie links einen Kunden, um Projekte und Dateien zu sehen.').style(
                        'font-size:var(--fs-sm);color:var(--text-light);text-align:center;max-width:280px;')

    def _show_customer(customer_name: str):
        selected['name'] = customer_name
        # Linke Liste neu rendern, damit die aktive Karte markiert wird
        _filter_list(search_inp.value or '')
        if not project_detail:
            return
        project_detail.clear()
        projects = _customers_mod.list_projects(base, customer_name)
        with project_detail:
            with ui.row().classes('w-full items-center gap-4'):
                with ui.element('div').style(
                    'width:48px;height:48px;border-radius:var(--radius-sm);'
                    'background:var(--brand-grad-badge);'
                    'display:flex;align-items:center;justify-content:center;'
                ):
                    initial = customer_name[0].upper() if customer_name else '?'
                    ui.label(initial).style('color:var(--accent);font-size:var(--fs-xl);font-weight:800;')
                with ui.column().classes('gap-0'):
                    ui.label(customer_name).classes('t-title')
                    ui.label(f'{len(projects)} {"Projekt" if len(projects) == 1 else "Projekte"}').style(
                        'font-size:var(--fs-sm);color:var(--text-muted);')
                ui.element('div').classes('flex-grow')
                ui.button('Neues Projekt', icon='add',
                    on_click=lambda: _new_project(customer_name)).props(
                    'no-caps unelevated').style('background:var(--bg-primary);color:var(--text-inverse);')
                cpath = _customers_mod.get_customer_path(base, customer_name)
                ui.button('Ordner öffnen', icon='folder_open',
                    on_click=lambda: safe_open_folder(cpath)).props('flat no-caps')
            ui.separator()
            if not projects:
                ui.label('Noch keine Projekte').style('font-size:var(--fs-sm);color:var(--text-light);padding:32px 0;text-align:center;')
            else:
                for proj in projects:
                    proj_path = _customers_mod.get_project_path(base, customer_name, proj)
                    if not proj_path:
                        proj_path = os.path.join(base, customer_name, proj)
                    folders = {f: os.path.join(proj_path, f) for f in PROJECT_FOLDERS}
                    total_files = sum(_customers_mod.count_files_in_folder(f) for f in folders.values())
                    src_folder = _customers_mod.find_source_folder(proj_path)
                    tgt_folder = _customers_mod.find_translation_folder(proj_path)
                    n_src = _customers_mod.count_files_in_folder(src_folder) if src_folder else 0
                    n_tgt = _customers_mod.count_files_in_folder(tgt_folder) if tgt_folder else 0
                    with ui.card().classes('w-full').props('flat bordered'):
                        with ui.row().classes('w-full items-center gap-4').style('padding:12px;'):
                            ui.icon('folder', size='sm').style('color:var(--accent)')
                            with ui.column().classes('gap-0 flex-grow'):
                                ui.label(proj).style('font-size:var(--fs-lg);font-weight:600;')
                                parts = []
                                if n_src:
                                    parts.append(f'{n_src} Quell')
                                if n_tgt:
                                    parts.append(f'{n_tgt} Übers.')
                                parts.append(f'{total_files} Dateien')
                                ui.label(' · '.join(parts)).style('font-size:var(--fs-sm);color:var(--text-muted);')
                            if n_src and n_tgt:
                                ui.button('Analyse', icon='play_arrow',
                                    on_click=lambda _, c=customer_name, p=proj: ui.navigate.to(
                                        f'/?kunde={c}&auftrag={p}')).props(
                                    'dense no-caps unelevated size=sm').style('background:var(--bg-primary);color:var(--text-inverse);')
                            ui.button(icon='folder_open',
                                on_click=lambda _, p=proj_path: safe_open_folder(p)).props(
                                'flat dense round size=sm').style('color:var(--text-light)')
                        with ui.expansion('Dateien anzeigen', icon='account_tree').props(
                            'dense header-class="text-xs text-gray-500 font-semibold"'
                        ).classes('w-full'):
                            with ui.column().classes('w-full gap-0 px-1 pb-2'):
                                for folder_name in PROJECT_FOLDERS:
                                    folder_path = os.path.join(proj_path, folder_name)
                                    files = _customers_mod.list_files_in_folder(folder_path)
                                    count = len(files)
                                    with ui.row().classes('w-full items-center gap-2').style('padding:4px 0;'):
                                        ui.icon('folder', size='xs').style(
                                            f'color:{"var(--accent)" if count else "var(--surface-border-strong)"};')
                                        ui.label(folder_name).style(
                                            f'font-size:var(--fs-sm);font-weight:600;'
                                            f'color:{"var(--text)" if count else "var(--text-muted)"};')
                                        if count:
                                            ui.badge(str(count)).style(
                                                'background:var(--bg-primary);color:var(--text-inverse);font-size:var(--fs-sm);border-radius:var(--radius-pill);')
                                        ui.element('div').classes('flex-grow')
                                        if os.path.isdir(folder_path):
                                            ui.button(icon='folder_open',
                                                on_click=lambda _, p=folder_path: safe_open_folder(p)).props(
                                                'flat dense round size=xs').style('color:var(--text-light)')
                                    if files:
                                        icon_map = {'.pdf': 'picture_as_pdf', '.docx': 'description',
                                            '.doc': 'description', '.txt': 'text_snippet',
                                            '.xlsx': 'table_chart', '.csv': 'table_chart',
                                            '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.tiff': 'image'}
                                        for fp in files:
                                            fname = os.path.basename(fp)
                                            fsize = os.path.getsize(fp)
                                            sz = f'{fsize/1024:.0f} KB' if fsize < 1024*1024 else f'{fsize/1024/1024:.1f} MB'
                                            ext = os.path.splitext(fname)[1].lower()
                                            with ui.row().classes('w-full items-center gap-1').style('padding:2px 0 2px 24px;'):
                                                ui.icon(icon_map.get(ext, 'insert_drive_file'), size='xs').style('color:var(--text-light)')
                                                ui.label(fname).style('font-size:var(--fs-sm);color:var(--text);flex-grow:1;')
                                                ui.label(sz).style('font-size:var(--fs-sm);color:var(--text-light);')

    def _new_customer():
        from types import SimpleNamespace
        from nicegui_app import ui_dialogs as _ui_dialogs

        def _finalize(name: str, info: dict):
            folder = _customers_mod.sanitize_folder_name(name)
            info['display_name'] = name
            info['folder_name'] = folder
            path = _customers_mod.ensure_project(base, folder)
            if path:
                try:
                    with open(os.path.join(path, 'kundeninfo.json'), 'w', encoding='utf-8') as fh:
                        json.dump(info, fh, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            # Closure-Liste in place aktualisieren, damit _filter_list den neuen Kunden sieht
            customers[:] = _customers_mod.load_customers(base)
            selected['name'] = folder
            _filter_list(search_inp.value or '')
            _show_customer(folder)
            ui.notify(f'Kunde "{name}" angelegt', type='positive')

        _ui_dialogs.show_new_customer_dialog(SimpleNamespace(finalize_new_customer=_finalize))

    def _new_project(customer_name: str):
        with ui.dialog() as dlg, ui.card().style('width:380px;'):
            ui.label('Neues Projekt').classes('t-heading')
            name_input = ui.input(label='Projektname',
                value=datetime.now().strftime('%Y-%m-%d')).classes('w-full')
            with ui.row().classes('w-full justify-end gap-2').style('margin-top:16px;'):
                ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
                def _do():
                    pname = name_input.value.strip()
                    if pname:
                        _customers_mod.ensure_project(base, customer_name, pname)
                        ui.notify(f'Projekt "{pname}" angelegt', type='positive')
                        dlg.close()
                        _show_customer(customer_name)
                ui.button('Anlegen', on_click=_do).props('no-caps unelevated').style(
                    'background:var(--bg-primary);color:var(--text-inverse);')
        dlg.open()
