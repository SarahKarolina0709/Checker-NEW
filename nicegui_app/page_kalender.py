# -*- coding: utf-8 -*-
"""Kalender-Seite – zeigt Projekte in Monatsansicht.

Registriert Route /kalender via @ui.page-Dekorator beim Import.
"""
from __future__ import annotations

import calendar as _calendar_mod
import os
from datetime import date as _date_type
from typing import List

from nicegui import ui

from nicegui_app.app_settings import settings
from nicegui_app.customers import MONTH_NAMES_DE
from nicegui_app import customers as _customers_mod
from nicegui_app.styles import APP_CSS
from nicegui_app.utils import safe_open_folder, make_keyboard_activatable


def _scan_project_dates():
    return _customers_mod.scan_project_dates(settings.get('projects_base_path', ''))


@ui.page('/kalender')
def kalender_page():
    today = _date_type.today()
    view = {'year': today.year, 'month': today.month}
    cal_container = None
    detail_container = None
    # Projekt-Datums-Scan nur einmal pro Seitenaufruf (statt bei jedem
    # Monatswechsel den ganzen Projektbaum erneut zu durchlaufen).
    _dates_cache: dict = {}

    def _project_dates():
        if 'v' not in _dates_cache:
            _dates_cache['v'] = _scan_project_dates()
        return _dates_cache['v']

    def _nav_month(delta: int):
        m = view['month'] + delta
        y = view['year']
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        view['month'], view['year'] = m, y
        _render_calendar()
        _reset_detail()

    def _reset_detail():
        """Setzt das Detail-Panel auf den Platzhalter zurueck (z.B. nach Monatswechsel)."""
        if not detail_container:
            return
        detail_container.clear()
        with detail_container:
            with ui.column().classes('w-full items-center justify-center').style(
                'min-height:60vh;gap:12px;padding:32px 12px;'):
                ui.icon('event', size='2.75rem').style('color:var(--text-light);')
                ui.label('Tag auswählen').style(
                    'font-size:var(--fs-lg);font-weight:600;color:var(--text-muted);')
                ui.label('Klicken Sie im Kalender auf einen Tag, um dessen Projekte zu sehen.').style(
                    'font-size:var(--fs-sm);color:var(--text-light);text-align:center;max-width:240px;')

    def _show_day(day_str: str, customers: List[str]):
        if not detail_container:
            return
        detail_container.clear()
        with detail_container:
            ui.label(f'Projekte am {day_str}').classes('t-title').style('margin-bottom:12px;')
            if not customers:
                ui.label('Keine Projekte an diesem Tag').style('font-size:var(--fs-sm);color:var(--text-light);padding:24px 0;')
                return
            base = settings.get('projects_base_path', '')
            for cust in customers:
                proj_path = ''
                for name, path in _customers_mod.list_projects_full(base, cust):
                    if name.startswith(day_str):
                        proj_path = path
                        break
                if not proj_path:
                    cand = os.path.join(base, cust, day_str)
                    if os.path.isdir(cand):
                        proj_path = cand
                n_src = _customers_mod.count_files_in_folder(_customers_mod.find_source_folder(proj_path)) if proj_path else 0
                n_tgt = _customers_mod.count_files_in_folder(_customers_mod.find_translation_folder(proj_path)) if proj_path else 0
                with ui.card().classes('w-full').props('flat bordered').style('margin-bottom:8px;padding:12px;'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('business', size='sm').style('color:var(--primary)')
                        ui.label(_customers_mod.display_name(cust)).style('font-size:var(--fs-md);font-weight:600;')
                    with ui.row().classes('gap-4').style('margin-left:28px;'):
                        ui.label(f'{n_src} Ausgangstexte').style(
                            f'font-size:var(--fs-sm);color:{"var(--text)" if n_src else "var(--text-light)"};')
                        ui.label(f'{n_tgt} Übersetzungen').style(
                            f'font-size:var(--fs-sm);color:{"var(--success)" if n_tgt else "var(--text-light)"};')
                    with ui.row().classes('gap-2').style('margin-left:28px;margin-top:4px;'):
                        ui.button('Analyse starten', icon='play_arrow',
                            on_click=lambda _, c=cust, d=day_str: ui.navigate.to(f'/?kunde={c}&auftrag={d}')
                        ).props('flat dense no-caps size=sm').style('color:var(--primary);font-size:var(--fs-sm);')
                        if os.path.isdir(proj_path):
                            ui.button('Ordner öffnen', icon='folder_open',
                                on_click=lambda _, p=proj_path: safe_open_folder(p)
                            ).props('flat dense no-caps size=sm').style('color:var(--text-muted);font-size:var(--fs-sm);')

    def _render_calendar():
        nonlocal cal_container
        if not cal_container:
            return
        cal_container.clear()
        base = settings.get('projects_base_path', '')
        if not base or not os.path.isdir(base):
            with cal_container:
                with ui.column().classes('w-full items-center').style('padding:64px 0;gap:12px;'):
                    ui.icon('folder_off', size='2.5rem').style('color:var(--text-light)')
                    ui.label('Kein Projektordner konfiguriert').style(
                        'font-size:var(--fs-lg);font-weight:600;color:var(--text-muted);')
                    ui.label('Bitte in den Einstellungen einen Projektbasispfad festlegen.').style(
                        'font-size:var(--fs-sm);color:var(--text-light);text-align:center;')
            return
        y, m = view['year'], view['month']
        project_dates = _project_dates()
        month_name = MONTH_NAMES_DE.get(m, str(m))
        with cal_container:
            with ui.row().classes('w-full items-center justify-center gap-4').style('margin-bottom:16px;'):
                ui.button(icon='chevron_left', on_click=lambda: _nav_month(-1)).props('flat round')
                ui.label(f'{month_name} {y}').style(
                    'font-size:var(--fs-xl);font-weight:700;color:var(--text);min-width:200px;text-align:center;')
                ui.button(icon='chevron_right', on_click=lambda: _nav_month(1)).props('flat round')
            with ui.row().classes('w-full gap-0'):
                for wd in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']:
                    ui.label(wd).style(
                        'width:14.28%;text-align:center;font-size:var(--fs-sm);font-weight:700;color:var(--text-muted);padding:4px 0;')
            cal = _calendar_mod.Calendar(firstweekday=0)
            for week in cal.monthdayscalendar(y, m):
                with ui.row().classes('w-full gap-0'):
                    for day_num in week:
                        if day_num == 0:
                            ui.element('div').style('width:14.28%;height:80px;')
                        else:
                            day_str = f'{y}-{m:02d}-{day_num:02d}'
                            customers = project_dates.get(day_str, [])
                            count = len(customers)
                            is_today = (day_num == today.day and m == today.month and y == today.year)
                            if count > 0:
                                bg = 'background:var(--bg-info-soft);border-color:var(--info);'
                            elif is_today:
                                bg = ('background:var(--bg-info-soft);border-color:var(--info);'
                                      'box-shadow:0 0 0 1px var(--info) inset;')
                            else:
                                bg = 'background:var(--surface);border-color:var(--surface-border);'
                            with make_keyboard_activatable(
                                ui.card().style(
                                    f'width:14.28%;min-height:80px;padding:6px;cursor:pointer;'
                                    f'border-radius:var(--radius-sm);border:1px solid;{bg}'
                                ).props('flat').on('click', lambda _, ds=day_str, cs=customers: _show_day(ds, cs)),
                                lambda ds=day_str, cs=customers: _show_day(ds, cs),
                            ):
                                with ui.row().classes('items-center gap-1'):
                                    ui.label(str(day_num)).style(
                                        f'font-size:var(--fs-md);font-weight:700;'
                                        f'color:{"var(--info)" if is_today else "var(--text)" if count == 0 else "var(--info)"};')
                                    if count > 0:
                                        ui.badge(str(count), color=None).style(
                                            'background:var(--info);color:var(--text-inverse);font-size:var(--fs-sm);border-radius:var(--radius-pill);')
                                if count > 0:
                                    for cust in customers[:2]:
                                        ui.label(_customers_mod.display_name(cust)).style(
                                            'font-size:var(--fs-sm);color:var(--info);overflow:hidden;'
                                            'text-overflow:ellipsis;white-space:nowrap;line-height:1.2;')
                                    if count > 2:
                                        ui.label(f'+{count-2} weitere').style('font-size:var(--fs-sm);color:var(--text-light);')

    ui.add_head_html(APP_CSS)
    with ui.header().classes('items-center px-6 py-0').style(
        'background:var(--brand-grad);min-height:56px;'
        'box-shadow:0 2px 12px rgba(0,0,0,.15);'
    ):
        with ui.row().classes('w-full items-center gap-4'):
            from nicegui_app.utils import render_logo
            render_logo(clickable=True, subtitle=True)
            ui.element('div').style(
                'width:1px;height:24px;background:rgba(255,255,255,.15);margin:0 4px;')
            ui.icon('calendar_month', size='xs').style('color:var(--accent);opacity:.8;')
            ui.label('Kalender').style(
                'font-size:var(--fs-md);font-weight:600;color:rgba(255,255,255,.7);')
            ui.element('div').classes('flex-grow')
            ui.button('Zurück', icon='arrow_back',
                on_click=lambda: ui.navigate.to('/')).props('flat no-caps text-color=white dense').style(
                'font-size:var(--fs-sm);opacity:.7;')

    with ui.row().classes('w-full flex-nowrap items-start gap-4 p-6 qf-stack').style(
        'min-height:calc(100vh - 56px);background:var(--surface-alt);'
    ):
        with ui.column().classes('flex-grow gap-0'):
            cal_container = ui.column().classes('w-full')
        with ui.column().classes('w-[350px] min-w-[300px]'):
            detail_container = ui.column().classes('w-full')
            _reset_detail()
    _render_calendar()
