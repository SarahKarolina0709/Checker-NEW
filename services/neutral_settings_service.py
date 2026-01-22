#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Neutral Settings Service (ehemals services/settings_service)

Thread-sicherer Zugriff auf verschachtelte Konfigurationswerte.
"""
from __future__ import annotations
from typing import Any, Dict
from threading import RLock

try:
    from config_manager import ConfigManager  # type: ignore
except Exception:  # pragma: no cover
    ConfigManager = None  # type: ignore

_DEFAULTS: Dict[str, Any] = {
    "infrastructure": {"worker_pool": {"size": 3, "enabled": True}},
    "plugins": {"enabled": True, "disabled_rules": [], "timeout_ms": 2000},
    "ui": {"contrast_mode": False, "font_scale": 1.0},
    "reporting": {
        "auto_generate": True,
        "output_dir": "reports",
        "filename_prefix": "analysis_report",
        "last_export_path": None,
    },
        "analysis": {
        "phases": {
            "phase1": {"enabled": True},
            "phase2": {"enabled": True},
            "phase3": {
                "enabled": True,
                "semantic": {
                    "enabled": True,
                    "threshold": 0.85,
                    "use_ollama": False,
                    "ollama_model": "nomic-embed-text"
                },
                "spellcheck": {
                    "enabled": True,
                    "target_language": "de",
                    "source_language": None,
                    "max_issues_per_segment": 3,
                    "use_language_tool": False,
                    "custom_dictionary": []
                }
            }
        },
        "phase2": {
            "coverage": {"enabled": True, "min_ratio": 0.60, "min_source_len": 40},
            "names": {"enabled": True, "whitelist": [], "do_not_translate": []},
            "terminology": {"critical_terms": []}
        },
        "phase3": {
            "semantic": {
                "threshold": 0.85,
                "use_ollama": False,
                "ollama_model": "nomic-embed-text"
            }
        },
        "embeddings": {"model": "all-MiniLM-L6-v2"},
        "max_findings_per_phase": 250,
        "validation": {
            "locale": {
                "target_language": "de",
                "source_language": None,
                "date_format": "DD.MM.YYYY",
                "allow_iso_dates": True,
                "decimal_separator": ",",
                "thousand_separator": ".",
                "time_separator": ":"
            },
            "blacklist": {
                "enabled": True,
                "terms": [],
                "severity": "critical",
                "match_target": True,
                "match_source": False
            },
            "lists": {
                "enabled": True,
                "require_matching_markers": True,
                "enforce_sequence": True,
                "ignore_single_items": True
            },
            "metadata": {
                "enabled": False,
                "allowed_attributes": [],
                "required_attributes": [],
                "protected_values": {}
            }
        },
        "lang": {
            "source": "auto",
            "target": "de"
        }
    },
    "quality": {
        "thresholds": {
            "accuracy": {"low": 0.85, "mid": 0.92},
            "terminology": {"min": 0.90},
            "readability": {"min": 60},
            "passive": {"max": 0.15},
            "length": {
                "variance": 0.05,
                "expected_ratio_default": 1.0,
                "language_pairs": {
                    "en->de": {"expected_ratio": 1.12, "tolerance": 0.08},
                    "de->en": {"expected_ratio": 0.88, "tolerance": 0.08},
                    "en->fr": {"expected_ratio": 1.05, "tolerance": 0.07},
                    "fr->en": {"expected_ratio": 0.95, "tolerance": 0.07},
                    "en->es": {"expected_ratio": 1.07, "tolerance": 0.08},
                    "es->en": {"expected_ratio": 0.93, "tolerance": 0.08},
                    "any->de": {"expected_ratio": 1.10, "tolerance": 0.08},
                    "de->any": {"expected_ratio": 0.90, "tolerance": 0.08},
                    "any->any": {"expected_ratio": 1.0, "tolerance": 0.10}
                }
            },
            "similarity": {
                "critical": 0.75,
                "major": 0.85,
                "use_percentiles": False,
                "percentiles": {"critical": 10.0, "major": 25.0}
            },
            "gate": {"min_score": 75.0}
        },
        "weights": {
            "accuracy": 0.40,
            "terminology": 0.15,
            "fluency": 0.15,
            "style": 0.10,
            "grammar": 0.10,
            "completeness": 0.10
        },
        "scoring": {"use_geometric": False},
        "findings": {"clustering": {"enabled": True}}
    },
}


class SettingsService:
    """Zentrale Settings-Verwaltung mit verschachtelten Key-Pfaden."""

    def __init__(self):
        self._lock = RLock()
        self._manager = ConfigManager() if ConfigManager else None
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self):
        with self._lock:
            data = {}
            try:
                if self._manager:
                    data = getattr(self._manager, "_overrides", {}) or {}
            except Exception:
                data = {}
            self._cache = self._deep_merge(_DEFAULTS, data)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        keys = set(base.keys()) | set(override.keys())
        for k in keys:
            bv = base.get(k)
            ov = override.get(k)
            if isinstance(bv, dict) and isinstance(ov, dict):
                result[k] = self._deep_merge(bv, ov)
            elif ov is not None:
                result[k] = ov
            else:
                result[k] = bv
        return result

    def _split(self, key_path: str):
        return [p for p in key_path.split('.') if p]

    def get(self, key_path: str, default: Any = None) -> Any:
        with self._lock:
            node: Any = self._cache
            for part in self._split(key_path):
                if isinstance(node, dict) and part in node:
                    node = node[part]
                else:
                    return default
            return node

    def set(self, key_path: str, value: Any) -> None:
        with self._lock:
            node = self._cache
            parts = self._split(key_path)
            for p in parts[:-1]:
                if p not in node or not isinstance(node[p], dict):
                    node[p] = {}
                node = node[p]  # type: ignore
            node[parts[-1]] = value
            self._persist()
        # Event publizieren (additiv, optional)
        try:
            from infra.event_bus import get_global_event_bus  # type: ignore
            bus = get_global_event_bus()
            if bus:
                bus.publish('settings.changed', {'key': key_path, 'value': value})
        except Exception:
            pass

    def _persist(self):
        if not self._manager:
            return
        overrides = self._compute_overrides(_DEFAULTS, self._cache)
        try:
            self._manager._overrides = overrides  # type: ignore
            self._manager.save()
        except Exception:
            pass

    def _compute_overrides(self, defaults: Dict[str, Any], merged: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in merged.items():
            dv = defaults.get(k, None)
            if isinstance(v, dict) and isinstance(dv, dict):
                sub = self._compute_overrides(dv, v)
                if sub:
                    out[k] = sub
            else:
                if v != dv:
                    out[k] = v
        return out

    def is_enabled(self, key_path: str, default: bool = True) -> bool:
        val = self.get(key_path, default)
        return bool(val)

    def reload(self):  # Hot-Reload Option
        self._load()

__all__ = ["SettingsService"]
