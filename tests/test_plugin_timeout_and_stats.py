#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests für Plugin-Timeout & Statistik-Erfassung.

Ziele:
- Simulieren einer langsamen Regel und Sicherstellen dass Timeout greift.
- Prüfen dass events/Stats Struktur aus _analyze_with_plugins korrekt ist.

Hinweis: Nutzt direkte Instanziierung der App-Klasse in isolierter Umgebung.
"""
from __future__ import annotations

import time

from plugins.base_rule import BaseRule, RuleResult
from quality_gui_main_app import QualityGuiMainApp


class SlowRule(BaseRule):
    """Regel die länger schläft als der eingestellte Timeout."""
    def analyze(self, context: dict) -> RuleResult:  # pragma: no cover - simple behavior
        time.sleep(0.25)  # 250ms
        return RuleResult(rule="slow_rule", passed=True, details={"slept": True})


def test_plugin_timeout_stats(monkeypatch):
    app = QualityGuiMainApp()
    # Reduziere Timeout auf 100ms sodass SlowRule sicher timeouted
    class DummySettings:
        def get(self, key, default=None):
            if key == 'plugins.timeout_ms':
                return 100
            return default
    app.settings_service = DummySettings()
    app.loaded_rules = [SlowRule]
    ctx = {"analysis_id": "test", "source_files": [], "translation_files": []}
    results = app._analyze_with_plugins(ctx)
    # Erwartet: Pseudo-Result (timeout -> passed False)
    assert len(results) == 1
    r = results[0]
    # Bei Timeout wird aktuell der Klassenname genutzt (SlowRule) statt Instanz-Result rule
    assert getattr(r, 'rule', '') in ('slow_rule', 'SlowRule')
    assert getattr(r, 'passed', True) is False, 'Timeout sollte passed False markieren'
    assert getattr(r, 'details', {}).get('timeout') is True
    # Stats wurden geschrieben
    stats = getattr(app, '_last_plugin_stats', {})
    assert stats.get('timeouts') == 1
    assert stats.get('executed') == 1
    assert stats.get('errors') == 0
    assert isinstance(stats.get('per_rule'), list) and stats['per_rule'][0]['rule'] == 'SlowRule'
