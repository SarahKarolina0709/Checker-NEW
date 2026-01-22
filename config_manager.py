#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Manager
==============
Kapselt Laden/Speichern/Defaults sowie Pfadauflösung.
- Liest primäre Defaults aus systemkritischem config.json (read-only hier)
- Nutzt checker_config.json für nutzerbezogene Overrides (schreibbar)
- Bietet get/set via dot-path
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
import os

from paths import CONFIG_FILE, ROOT


class ConfigManager:
    def __init__(self, defaults_path: Path | str | None = None, overrides_path: Path | str | None = None):
        self.defaults_path = Path(defaults_path or (ROOT / 'config.json'))
        self.overrides_path = Path(overrides_path or (ROOT / CONFIG_FILE))
        self._defaults: Dict[str, Any] = {}
        self._overrides: Dict[str, Any] = {}
        self._load()

    def _load(self):
        # Defaults (read-only)
        try:
            if self.defaults_path.exists():
                with open(self.defaults_path, 'r', encoding='utf-8') as f:
                    self._defaults = json.load(f)
        except Exception:
            self._defaults = {}
        # Overrides (user)
        try:
            if self.overrides_path.exists():
                with open(self.overrides_path, 'r', encoding='utf-8') as f:
                    self._overrides = json.load(f)
            else:
                self._overrides = {}
        except Exception:
            self._overrides = {}

    def save(self) -> bool:
        try:
            with open(self.overrides_path, 'w', encoding='utf-8') as f:
                json.dump(self._overrides, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    # Dot-path helpers
    @staticmethod
    def _get_from(d: Dict[str, Any], keys: list[str]):
        cur: Any = d
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return None
            cur = cur[k]
        return cur

    @staticmethod
    def _set_into(d: Dict[str, Any], keys: list[str], value: Any):
        cur = d
        for k in keys[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                cur[k] = {}
            cur = cur[k]
        cur[keys[-1]] = value

    def get(self, path: str, default: Any = None) -> Any:
        keys = path.split('.') if path else []
        # Overrides first
        v = self._get_from(self._overrides, keys) if keys else None
        if v is not None:
            return v
        # Fallback to defaults
        v = self._get_from(self._defaults, keys) if keys else None
        return default if v is None else v

    def set(self, path: str, value: Any) -> bool:
        keys = path.split('.') if path else []
        if not keys:
            return False
        self._set_into(self._overrides, keys, value)
        return self.save()

    # Convenience
    def get_projects_base_dir(self) -> Path:
        p = self.get('paths.projects.default_directory')
        return Path(p) if p else (ROOT / 'Checker_Projekte')
