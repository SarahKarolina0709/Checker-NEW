# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.analysis."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from nicegui_app.analysis import (
    MAX_HISTORY_SNAPSHOTS,
    snapshot_previous_findings,
)


def test_snapshot_returns_none_when_no_findings(tmp_path: Path) -> None:
    s = {'findings': []}
    assert snapshot_previous_findings(s, str(tmp_path)) is None
    # Kein Verzeichnis erstellt
    assert not (tmp_path / 'reports' / 'history').exists()


def test_snapshot_writes_file_with_correct_payload(tmp_path: Path) -> None:
    s = {
        'findings': [{'id': 1, 'msg': 'test'}],
        'active_project_path': str(tmp_path / 'Kunde_X' / '2025-01-01_Auftrag'),
        'current_score': 87,
        'checked_findings': {'fp_abc': True},
    }
    out = snapshot_previous_findings(s, str(tmp_path))
    assert out is not None
    assert os.path.isfile(out)
    data = json.loads(Path(out).read_text(encoding='utf-8'))
    assert data['score'] == 87
    assert data['findings'] == [{'id': 1, 'msg': 'test'}]
    assert data['checked_findings'] == {'fp_abc': True}
    assert 'timestamp' in data
    # Dateiname enthaelt projektlabel
    assert '2025-01-01_Auftrag' in os.path.basename(out)


def test_snapshot_sanitizes_project_label(tmp_path: Path) -> None:
    s = {
        'findings': [{'x': 1}],
        'active_project_path': '/foo/bar/Kunde mit Slash:und/Sonderzeichen!',
    }
    out = snapshot_previous_findings(s, str(tmp_path))
    assert out is not None
    name = os.path.basename(out)
    # Keine Sonderzeichen ausser - und _
    label = name.replace('findings_', '').rsplit('_', 2)[0]
    for ch in label:
        assert ch.isalnum() or ch in '-_'


def test_snapshot_uses_session_when_no_project(tmp_path: Path) -> None:
    s = {'findings': [{'a': 1}], 'active_project_path': ''}
    out = snapshot_previous_findings(s, str(tmp_path))
    assert out is not None
    assert 'session' in os.path.basename(out)


def test_snapshot_rotation_keeps_max_n(tmp_path: Path) -> None:
    history_dir = tmp_path / 'reports' / 'history'
    history_dir.mkdir(parents=True)
    # 35 alte Snapshots erzeugen mit aufsteigenden mtimes
    for i in range(35):
        f = history_dir / f'findings_old_{i:03d}.json'
        f.write_text('{}', encoding='utf-8')
        os.utime(f, (1000 + i, 1000 + i))

    s = {'findings': [{'x': 1}], 'active_project_path': '/p/Neu'}
    out = snapshot_previous_findings(s, str(tmp_path))
    assert out is not None

    files = sorted(history_dir.glob('findings_*.json'))
    assert len(files) == MAX_HISTORY_SNAPSHOTS
    # Die aeltesten wurden geloescht (000..004 weg, 005.. + neuer Snapshot bleiben)
    names = [f.name for f in files]
    assert 'findings_old_000.json' not in names
    assert os.path.basename(out) in names


def test_snapshot_handles_unwritable_dir(tmp_path: Path, monkeypatch) -> None:
    s = {'findings': [{'a': 1}]}

    def boom(*a, **kw):
        raise OSError('permission denied')

    monkeypatch.setattr('nicegui_app.analysis.os.makedirs', boom)
    assert snapshot_previous_findings(s, str(tmp_path)) is None
