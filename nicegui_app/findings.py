# -*- coding: utf-8 -*-
"""Findings-Hilfsfunktionen (Fingerprint fuer Diff zwischen Analyselaeufen)."""
from __future__ import annotations

import os


def finding_fingerprint(fd_or_obj) -> str:
    """Stabiler Hash zum Wiedererkennen identischer Findings ueber Re-Analysen.

    Akzeptiert sowohl QAIssue-Objekte als auch dicts (aus s['findings']).
    """
    if isinstance(fd_or_obj, dict):
        d = fd_or_obj
        code = d.get('code', '')
        seg = d.get('segment_index', -1)
        sf = d.get('source_file', '') or ''
        tf = d.get('target_file', '') or ''
        msg = (d.get('message', '') or '')[:80]
    else:
        code = getattr(fd_or_obj, 'code', '')
        seg = getattr(fd_or_obj, 'segment_index', -1)
        sf = getattr(fd_or_obj, 'source_file', '') or ''
        tf = getattr(fd_or_obj, 'target_file', '') or ''
        msg = (getattr(fd_or_obj, 'message', '') or '')[:80]
    return f'{code}|{seg}|{os.path.basename(sf)}|{os.path.basename(tf)}|{msg}'
