# -*- coding: utf-8 -*-
"""Kleine UI-Helfer ohne eigene Logik."""
from __future__ import annotations

import os
import platform
import subprocess

from nicegui import ui


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
