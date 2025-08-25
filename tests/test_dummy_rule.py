#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Basis-Test für Plugin Discovery & DummyTerminologyRule.

Ziele:
- Sicherstellen, dass discover_rules() die Dummy-Regel findet
- Ausführen der analyze() Methode mit Minimal-Kontext
- Validieren der Result-Struktur

DE-Strings weil Projektvorgabe (Deutsch UI / Doku).
"""
from __future__ import annotations

import os
import sys
import types

# Pfad hinzufügen, falls Tests direkt ausgeführt werden (kein Paketinstall)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from plugins.loader import discover_rules  # noqa: E402
from plugins.base_rule import BaseRule, RuleResult  # noqa: E402


def test_discover_rules_finds_dummy_rule():
    rules = discover_rules()
    names = {r.__name__ for r in rules}
    assert 'DummyTerminologyRule' in names, "DummyTerminologyRule sollte gefunden werden"


def test_dummy_rule_analyze_structure():
    # Finde konkrete Dummy-Regelklasse
    rule_cls = None
    for r in discover_rules():
        if r.__name__ == 'DummyTerminologyRule':
            rule_cls = r
            break
    assert rule_cls is not None, "DummyTerminologyRule nicht gefunden"
    rule: BaseRule = rule_cls()
    ctx = {"translation_files": ["a.txt", "b.txt"]}
    res = rule.analyze(ctx)
    assert isinstance(res, RuleResult)
    assert res.rule == 'dummy_terminology'
    assert res.passed is True
    assert isinstance(res.details, dict)
    assert res.details.get('translation_files') == 2


def test_dummy_rule_zero_files():
    # Leerer Kontext → count 0
    rule_cls = None
    for r in discover_rules():
        if r.__name__ == 'DummyTerminologyRule':
            rule_cls = r
            break
    assert rule_cls, "DummyTerminologyRule nicht gefunden"
    res = rule_cls().analyze({})
    assert res.details.get('translation_files') == 0
