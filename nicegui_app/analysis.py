# -*- coding: utf-8 -*-
"""Analyse-Hilfsfunktionen ohne UI-Abhaengigkeiten.

Reine Backend-Logik fuer Findings-Verwaltung, Snapshots, etc.
Testbar ohne NiceGUI.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, MutableMapping

_logger = logging.getLogger(__name__)

MAX_HISTORY_SNAPSHOTS = 30


def snapshot_previous_findings(
    s: MutableMapping[str, Any],
    repo_root: str,
) -> str | None:
    """Sichert den letzten Findings-Stand vor einer Re-Analyse.

    Schreibt nach ``<repo_root>/reports/history/findings_<projekt>_<ts>.json``
    sodass Erledigt-Marker und Befunde nach versehentlichem Re-Run
    rekonstruierbar sind. Nur wenn Findings vorhanden sind.

    Rotation: max. ``MAX_HISTORY_SNAPSHOTS`` Snapshots werden behalten.

    Args:
        s: Session-State-Dict mit Keys 'findings', 'active_project_path',
           'current_score', 'checked_findings'.
        repo_root: Absoluter Pfad zum Repo-Root (Eltern von ``reports/``).

    Returns:
        Pfad zur geschriebenen Snapshot-Datei oder None wenn nichts geschrieben.
    """
    prev_findings = list(s.get('findings', []) or [])
    if not prev_findings:
        return None
    proj = s.get('active_project_path', '') or ''
    proj_label = os.path.basename(proj.rstrip(os.sep)) or 'session'
    safe_label = ''.join(
        c if c.isalnum() or c in '-_' else '_' for c in proj_label
    )[:60]
    history_dir = os.path.join(repo_root, 'reports', 'history')
    try:
        os.makedirs(history_dir, exist_ok=True)
    except OSError:
        return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(history_dir, f'findings_{safe_label}_{ts}.json')
    snapshot: Dict[str, Any] = {
        'timestamp': datetime.now().isoformat(),
        'project_path': proj,
        'score': s.get('current_score', -1),
        'findings': prev_findings,
        'checked_findings': dict(s.get('checked_findings', {}) or {}),
    }
    try:
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(snapshot, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        _logger.debug('Snapshot konnte nicht geschrieben werden: %s', exc)
        return None

    # Rotation: max. MAX_HISTORY_SNAPSHOTS Snapshots behalten
    try:
        snaps = sorted(
            (os.path.join(history_dir, n) for n in os.listdir(history_dir)
             if n.startswith('findings_') and n.endswith('.json')),
            key=os.path.getmtime,
        )
        for old in snaps[:-MAX_HISTORY_SNAPSHOTS]:
            try:
                os.remove(old)
            except OSError:
                pass
    except OSError:
        pass

    return out_path
