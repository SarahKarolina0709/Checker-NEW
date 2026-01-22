#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test für Frühabbruch-Ereignis (plugins.analysis.aborted) und Auto-Reset des Cancel-Flags.

Ziele:
- Erzeugen mehrerer künstlicher Timeout-Regeln um Abbruchschwelle (>40% Timeouts) zu triggern.
- Prüfen, dass Event published wurde und Cancel-Flag nach Lauf wieder False ist.
"""
from __future__ import annotations
import time

from plugins.base_rule import BaseRule, RuleResult
from quality_gui_main_app import QualityGuiMainApp


class VerySlowRule(BaseRule):
    def analyze(self, context: dict) -> RuleResult:  # pragma: no cover
        time.sleep(0.3)  # bewusst langsamer als Timeout
        return RuleResult(rule="veryslow", passed=True)

class FastRule(BaseRule):
    def analyze(self, context: dict) -> RuleResult:  # pragma: no cover
        return RuleResult(rule="fast", passed=True)


def test_plugin_abort_event_and_cancel_reset(monkeypatch):
    app = QualityGuiMainApp()

    # Dummy Settings: Timeout sehr klein, damit VerySlowRule timeouts erzeugt
    class DummySettings:
        def get(self, key, default=None):
            if key == 'plugins.timeout_ms':
                return 50  # 50ms -> garantiert Timeout bei 300ms Sleep
            return default
    app.settings_service = DummySettings()

    # Event collector
    published = []
    class DummyBus:
        def publish(self, name, payload):  # pragma: no cover - simple capture
            published.append((name, payload))
    app.event_bus = DummyBus()

    # Lade mehrere Regeln (Mischung), so dass >40% Timeout Quote möglich
    # z.B. 3 VerySlow + 2 Fast => 60% Timeouts
    app.loaded_rules = [VerySlowRule, VerySlowRule, VerySlowRule, FastRule, FastRule]

    ctx = {"analysis_id": "abort-test"}
    results = app._analyze_with_plugins(ctx)

    # Es können einige Resultate vorhanden sein (nur rechtzeitig fertig werdende FastRule ggf.)
    assert isinstance(results, list)

    # Abort-Event sollte vorhanden sein
    abort_events = [e for e in published if e[0] == 'plugins.analysis.aborted']
    assert abort_events, "Erwartet abort Event"
    abort_payload = abort_events[0][1]
    ratio = abort_payload.get('timeout_ratio')
    assert ratio and ratio > 0.4
    # Threshold (falls gesetzt) validieren
    if 'threshold' in abort_payload:
        thr = abort_payload['threshold']
        assert 0 < thr < 1, "Ungültiger Threshold"

    # Completed Event ebenfalls erwartbar
    completed = [e for e in published if e[0] == 'plugins.analysis.completed']
    assert completed, "Completed Event fehlt"
    # Aborted Flag in Stats prüfen
    stats = completed[-1][1].get('stats', {})
    assert stats.get('aborted') is True, "Stats enthalten aborted Flag nicht"

    # Cancel Flag muss zurückgesetzt sein
    assert getattr(app, '_plugin_cancel_requested', False) is False, "Cancel Flag nicht zurückgesetzt"
