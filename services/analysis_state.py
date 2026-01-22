#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AnalysisState

Zentrale, leichtgewichtige State-Verwaltung für die Analyse-UI.

Ziele:
- Einheitliche Persistenz aller UI-Zustände (Tabs, Filter, Sortierung, Suche, Gruppierung)
- Schwellenwerte (Risk, Vollständigkeit, Ähnlichkeit) konsistent speichern/lesen
- Optionale Events bei Änderungen (über bereitgestellten EventBus)

Implementierungsdetails:
- Backing-Store: services.SettingsService (verschachtelte key-paths)
- Defensive Fallbacks: Wenn kein SettingsService vorhanden, In-Memory Cache
- Keine Abhängigkeit zu Tk/CTk; reine Logik
"""
from __future__ import annotations
from typing import Any, Dict, Optional


class AnalysisState:
    """Zentraler State-Container mit Settings-Persistenz."""

    def __init__(self, settings_service: Optional[Any] = None, event_bus: Optional[Any] = None):
        self._settings = settings_service
        self._event_bus = event_bus
        # In-Memory Fallback Cache falls kein SettingsService verfügbar ist
        self._cache: Dict[str, Any] = {}

    # ----------------------------- Tabs -----------------------------
    def get_last_tab(self, default: str = "overview") -> str:
        val = None
        try:
            if self._settings:
                val = self._settings.get("analysis.ui.last_tab", default)
        except Exception:
            val = None
        if not isinstance(val, str):
            val = self._cache.get("analysis.ui.last_tab", default)
        return val if val in ("overview", "phases", "findings") else default

    def set_last_tab(self, tab: str) -> None:
        if tab not in ("overview", "phases", "findings"):
            return
        try:
            if self._settings:
                self._settings.set("analysis.ui.last_tab", tab)
            else:
                self._cache["analysis.ui.last_tab"] = tab
        except Exception:
            self._cache["analysis.ui.last_tab"] = tab
        self._emit("analysis.state.changed", {"scope": "ui", "key": "last_tab", "value": tab})

    # --------------------------- Findings UI ---------------------------
    _FINDINGS_KEYS = ("severity", "checker", "sort", "sort_dir", "query", "grouped")

    def get_findings_state(self) -> Dict[str, Any]:
        """Liest den Findings-UI-State. Liefert Defaults bei fehlenden Werten."""
        defaults: Dict[str, Any] = {
            "severity": "ALL",
            "checker": "ALL",
            "sort": "severity",
            "sort_dir": "asc",
            "query": "",
            "grouped": False,
        }
        out = dict(defaults)
        for k in self._FINDINGS_KEYS:
            val = None
            try:
                if self._settings:
                    val = self._settings.get(f"analysis.ui.findings.{k}", defaults[k])
            except Exception:
                val = None
            if val is None:
                val = self._cache.get(f"analysis.ui.findings.{k}", defaults[k])
            out[k] = val
        # Sanitize types
        out["severity"] = out.get("severity") if out.get("severity") in ("ALL", "critical", "major", "minor") else "ALL"
        out["checker"] = out.get("checker") if isinstance(out.get("checker"), str) else "ALL"
        out["sort"] = out.get("sort") if out.get("sort") in ("severity", "rule", "message", "count", "confidence") else "severity"
        out["sort_dir"] = out.get("sort_dir") if out.get("sort_dir") in ("asc", "desc") else "asc"
        out["query"] = out.get("query") if isinstance(out.get("query"), str) else ""
        out["grouped"] = bool(out.get("grouped", False))
        return out

    def update_findings_state(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Schreibt Teilzustände; gibt den konsolidierten neuen Zustand zurück."""
        if not isinstance(patch, dict):
            return self.get_findings_state()
        current = self.get_findings_state()
        # Merge
        current.update({k: v for k, v in patch.items() if k in self._FINDINGS_KEYS})
        # Persist
        for k in self._FINDINGS_KEYS:
            try:
                if self._settings:
                    self._settings.set(f"analysis.ui.findings.{k}", current[k])
                else:
                    self._cache[f"analysis.ui.findings.{k}"] = current[k]
            except Exception:
                self._cache[f"analysis.ui.findings.{k}"] = current[k]
        self._emit("analysis.state.changed", {"scope": "findings", "patch": patch, "state": current})
        return current

    # --------------------------- Thresholds ---------------------------
    def get_thresholds(self) -> Dict[str, Any]:
        defaults = {"risk_high": 70, "completeness_low": 0.98, "similarity_low": 0.85}
        out = dict(defaults)
        for k in ("risk_high", "completeness_low", "similarity_low"):
            val = None
            try:
                if self._settings:
                    val = self._settings.get(f"analysis.thresholds.{k}", defaults[k])
            except Exception:
                val = None
            if val is None:
                val = self._cache.get(f"analysis.thresholds.{k}", defaults[k])
            out[k] = val
        # sanitize
        try:
            out["risk_high"] = int(out.get("risk_high", 70))
        except Exception:
            out["risk_high"] = 70
        try:
            out["completeness_low"] = float(out.get("completeness_low", 0.98))
        except Exception:
            out["completeness_low"] = 0.98
        try:
            out["similarity_low"] = float(out.get("similarity_low", 0.85))
        except Exception:
            out["similarity_low"] = 0.85
        # bounds
        out["risk_high"] = max(0, min(100, out["risk_high"]))
        out["completeness_low"] = max(0.0, min(1.0, out["completeness_low"]))
        out["similarity_low"] = max(0.0, min(1.0, out["similarity_low"]))
        return out

    def set_thresholds(self, risk_high: Optional[int] = None, completeness_low: Optional[float] = None, similarity_low: Optional[float] = None) -> Dict[str, Any]:
        cur = self.get_thresholds()
        if isinstance(risk_high, (int, float)):
            cur["risk_high"] = max(0, min(100, int(risk_high)))
        if isinstance(completeness_low, (int, float)):
            cur["completeness_low"] = max(0.0, min(1.0, float(completeness_low)))
        if isinstance(similarity_low, (int, float)):
            cur["similarity_low"] = max(0.0, min(1.0, float(similarity_low)))
        # Persist
        for k, v in cur.items():
            key = f"analysis.thresholds.{k}"
            try:
                if self._settings:
                    self._settings.set(key, v)
                else:
                    self._cache[key] = v
            except Exception:
                self._cache[key] = v
        self._emit("analysis.state.changed", {"scope": "thresholds", "state": cur})
        return cur

    # --------------------------- intern ---------------------------
    def _emit(self, evt: str, payload: Dict[str, Any]) -> None:
        try:
            if self._event_bus and hasattr(self._event_bus, 'publish'):
                self._event_bus.publish(evt, payload)
        except Exception:
            pass

__all__ = ["AnalysisState"]
