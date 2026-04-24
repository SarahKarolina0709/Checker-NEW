# -*- coding: utf-8 -*-
"""Session-Persistierung (laden/speichern session.json).

Reine Funktionen, kein NiceGUI- oder app.storage-Zugriff.
Aufrufer (main.py) liefert das session-data-Dict; das Modul kuemmert sich
nur um Pfad-Resolution + atomares Schreiben + Recovery.
"""
from __future__ import annotations

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

_logger = logging.getLogger(__name__)


def get_session_path(active_project_path: str, fallback_dir: str) -> str:
    """Liefert den Pfad zur session.json.

    Bevorzugt das aktive Projekt; fallback ist das `fallback_dir` (i.d.R. tmp).
    """
    if active_project_path and os.path.isdir(active_project_path):
        return os.path.join(active_project_path, 'session.json')
    return os.path.join(fallback_dir, 'session.json')


def build_session_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Baut das serialisierbare Session-Dict aus dem App-State.

    Erwartet ein Dict mit den Schluesseln: source_files, translation_files,
    paired_results, findings, active_customer, active_project_path,
    current_score. Fehlende Schluessel werden defensiv ersetzt.
    """
    return {
        'source_files': list(state.get('source_files', [])),
        'translation_files': list(state.get('translation_files', [])),
        'paired_results': list(state.get('paired_results', [])),
        'findings': list(state.get('findings', [])),
        'checked_findings': dict(state.get('checked_findings', {}) or {}),
        'manual_glossary_terms': dict(state.get('manual_glossary_terms', {}) or {}),
        'glossary_path': state.get('glossary_path') or '',
        'customer': state.get('active_customer', ''),
        'project_path': state.get('active_project_path', ''),
        'score': state.get('current_score', -1),
        'score_history': list(state.get('score_history', []) or []),
        'timestamp': datetime.now().isoformat(),
    }


def save_session(path: str, data: Dict[str, Any]) -> bool:
    """Speichert die Session atomar (tmp + os.replace).

    Verhindert Korruption der existierenden Datei bei Crash mid-write.
    Returns True bei Erfolg.
    """
    tmp_path = path + '.tmp'
    try:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        return True
    except Exception as exc:
        _logger.warning('Session speichern fehlgeschlagen: %s', exc)
        return False
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def load_session_from_path(path: str) -> Optional[Dict[str, Any]]:
    """Laedt eine session.json. None bei Fehler/Nicht-Existent."""
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as exc:
        _logger.warning('Session laden fehlgeschlagen (%s): %s', path, exc)
        return None


def find_latest_session(base_path: str) -> str:
    """Sucht die juengste session.json unterhalb von base_path. Leerer String wenn keine."""
    if not base_path or not os.path.isdir(base_path):
        return ''
    latest_path = ''
    latest_mtime = 0.0
    try:
        for root, _dirs, files in os.walk(base_path):
            if 'session.json' in files:
                sp = os.path.join(root, 'session.json')
                try:
                    mt = os.path.getmtime(sp)
                except OSError:
                    continue
                if mt > latest_mtime:
                    latest_mtime = mt
                    latest_path = sp
    except OSError:
        pass
    return latest_path


def load_session(active_project_path: str, fallback_dir: str,
                 base_path: str) -> Optional[Dict[str, Any]]:
    """Versucht der Reihe nach: aktives Projekt -> tmp-fallback -> juengste in base_path."""
    candidates = []
    if active_project_path:
        candidates.append(os.path.join(active_project_path, 'session.json'))
    candidates.append(os.path.join(fallback_dir, 'session.json'))
    for c in candidates:
        data = load_session_from_path(c)
        if data is not None:
            return data
    latest = find_latest_session(base_path)
    if latest:
        return load_session_from_path(latest)
    return None
