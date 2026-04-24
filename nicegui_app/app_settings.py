# -*- coding: utf-8 -*-
"""App-Konfiguration – einmal laden, ueberall importieren.

`settings` ist ein mutabler Dict. Aenderungen (z.B. in _open_settings)
sind in allen Modulen sichtbar, da alle dieselbe Dict-Referenz halten.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_settings() -> Dict[str, Any]:
    """Laedt Benutzer-Einstellungen aus checker_config.json."""
    defaults: Dict[str, Any] = {
        'project_path': '',
        'projects_base_path': str(Path(__file__).parent.parent / 'Checker_Projekte'),
        'src_lang': 'Auto-Erkennung',
        'tgt_lang': 'Auto-Erkennung',
        'depth': 'Mittel',
        'chars_per_norm_line': 36,
    }
    try:
        cfg_path = Path(__file__).parent.parent / 'checker_config.json'
        if cfg_path.exists():
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            for src_key, dst_key in [
                ('projects_base_path', 'projects_base_path'),
                ('default_src_lang', 'src_lang'),
                ('default_tgt_lang', 'tgt_lang'),
                ('depth', 'depth'),
            ]:
                if cfg.get(src_key):
                    defaults[dst_key] = cfg[src_key]
            if cfg.get('chars_per_norm_line'):
                defaults['chars_per_norm_line'] = int(cfg['chars_per_norm_line'])
    except Exception:
        pass
    return defaults


settings: Dict[str, Any] = load_settings()
