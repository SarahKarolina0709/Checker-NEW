#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reporting Exporter (minimaler JSON Export) - additiv, keine bestehende Logik ersetzt.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from core.model import AnalysisReport

class ReportExporter:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "reports"
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback: aktuelles Verzeichnis
            self.base_dir = Path.cwd()

    def export_json(self, report: AnalysisReport, filename_prefix: str = "analysis_report") -> Optional[Path]:
        try:
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            path = self.base_dir / f"{filename_prefix}_{ts}.json"
            with path.open("w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            return path
        except Exception:
            return None

__all__ = ["ReportExporter"]
