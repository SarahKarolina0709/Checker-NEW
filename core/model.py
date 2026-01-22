#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core Reporting / Findings Modelle (additiv, minimal)

Definiert schlanke Dataklassen für Analyse-Reporting ohne bestehende Logik zu brechen.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class Finding:
    rule: str
    message: str
    severity: str = "info"  # info|warning|error
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisReport:
    created_ts: float
    overall_score: Optional[float]
    findings: List[Finding] = field(default_factory=list)
    plugins_run: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    # 🆕 Additive optionale Metriken (brechen bestehende Aufrufer nicht)
    duration_s: Optional[float] = None
    file_counts: Dict[str, int] = field(default_factory=dict)
    plugin_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # Erweiterte Struktur – Felder nur ausgeben wenn gesetzt
        data = {
            "created_ts": self.created_ts,
            "overall_score": self.overall_score,
            "plugins_run": self.plugins_run,
            "findings": [f.__dict__ for f in self.findings],
            "context": self.context,
        }
        if self.duration_s is not None:
            data["duration_s"] = self.duration_s
        if self.file_counts:
            data["file_counts"] = self.file_counts
        if self.plugin_stats:
            data["plugin_stats"] = self.plugin_stats
        return data

    @classmethod
    def create(cls, overall_score: Optional[float], plugins_run: int, findings: List[Finding], context: Dict[str, Any]):
        return cls(created_ts=time.time(), overall_score=overall_score, plugins_run=plugins_run, findings=findings, context=context)

__all__ = ["Finding", "AnalysisReport"]
