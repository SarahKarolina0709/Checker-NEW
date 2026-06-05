# -*- coding: utf-8 -*-
"""Kleine UI-Helfer ohne eigene Logik."""
from __future__ import annotations

import logging
import os
import platform
import subprocess

from nicegui import ui

_logger = logging.getLogger(__name__)


def safe_open_folder(path: str) -> None:
    """Oeffnet einen Ordner im Datei-Explorer (cross-platform)."""
    if not os.path.isdir(path):
        ui.notify(f'Ordner nicht gefunden: {path}', type='warning')
        return
    try:
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)  # type: ignore[attr-defined]
        elif system == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except Exception as exc:
        ui.notify(f'Ordner konnte nicht geöffnet werden: {exc}', type='warning')


def fmt_size(size: int) -> str:
    """Formatiert Dateigroesse als lesbaren String."""
    if size < 1024:
        return f'{size} B'
    if size < 1024 * 1024:
        return f'{size / 1024:.1f} KB'
    return f'{size / (1024 * 1024):.1f} MB'


def html_esc(text: str) -> str:
    """Minimaler HTML-Escape fuer Inline-Anzeige."""
    if not text:
        return ''
    return (text.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))


def render_logo(clickable: bool = True, subtitle: bool = True) -> None:
    """Einheitliches Brand-Logo für Header aller Seiten.

    Rendert: [QF-Badge mit translate-Icon] [Qualitäts-Framework / PROFESSIONAL EDITION]
    """
    def _build():
        with ui.row().classes('items-center gap-3 flex-nowrap'):
            # QF-Badge: gold-border Karte mit translate-Icon
            badge = ui.element('div').style(
                'width:38px;height:38px;flex-shrink:0;border-radius:10px;'
                'background:linear-gradient(145deg,#d4af37,#c49b28);'
                'display:flex;align-items:center;justify-content:center;'
                'box-shadow:0 2px 8px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.25);'
                'cursor:pointer;position:relative;overflow:hidden;')
            with badge:
                # innerer Glanz-Highlight
                ui.element('div').style(
                    'position:absolute;top:0;left:0;right:0;height:50%;'
                    'background:rgba(255,255,255,.18);border-radius:10px 10px 0 0;pointer-events:none;')
                ui.icon('translate').style(
                    'font-size:20px;color:#0a1628;position:relative;z-index:1;')
            if clickable:
                badge.on('click', lambda: ui.navigate.to('/'))
            # Text-Block
            with ui.column().classes('gap-0'):
                ui.label('Qualitäts-Framework').style(
                    'font-size:var(--fs-lg);font-weight:800;color:#fff;'
                    'letter-spacing:-.3px;line-height:1.15;white-space:nowrap;')
                if subtitle:
                    ui.label('PROFESSIONAL EDITION').style(
                        'font-size:9px;font-weight:700;color:var(--accent);'
                        'text-transform:uppercase;letter-spacing:2px;line-height:1.1;')
    _build()


def copy_to_clipboard(text: str) -> None:
    """Kopiert Text in die Zwischenablage (clientseitig via JS)."""
    if not text:
        return
    try:
        safe = text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        ui.run_javascript(f'navigator.clipboard.writeText(`{safe}`)')
        ui.notify('In Zwischenablage kopiert', type='positive')
    except Exception as exc:
        _logger.debug('Copy fehlgeschlagen: %s', exc)
        ui.notify('Kopieren fehlgeschlagen', type='warning')

