#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
paths.py
========
Zentrale Konstanten/Keys und Path-Helfer für die Checker-App.
Nutzen: Verhindert Streuung von String-Literalen (Dateinamen/Key-Pfade).
"""
from __future__ import annotations
from pathlib import Path
from typing import Final

# Dateien
CONFIG_FILE: Final[str] = "checker_config.json"  # Lightweight overrides (nicht systemkritisch)
ANALYTICS_FILE: Final[str] = "analytics.json"
CUSTOMERS_FILE: Final[str] = "customers.json"
RECENT_PROJECTS_FILE: Final[str] = "recent_projects.json"
LOG_DIR: Final[str] = "logs"
LOG_FILE: Final[str] = "checker_app.log"

# JSON Key Paths (dot-paths)
K_APP_NAME: Final[str] = "app.name"
K_PROJECTS_BASE: Final[str] = "paths.projects.default_directory"
K_UPLOAD_ALLOWED_EXT: Final[str] = "paths.projects.allowed_extensions"
K_UI_ANIMATIONS: Final[str] = "features.animations_enabled"
K_LOG_LEVEL: Final[str] = "logging.level"
K_CALENDAR_BUNDESLAND: Final[str] = "calendar_settings.bundesland"

# Pfad-Helfer
ROOT: Final[Path] = Path(__file__).resolve().parent


def ensure_dir(path: Path | str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
