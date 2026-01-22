#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Einfache Dummy-Regel zum Testen des Plugin-Systems."""
from __future__ import annotations
from plugins.base_rule import BaseRule, RuleResult

class DummyTerminologyRule(BaseRule):
    name = "dummy_terminology"
    version = "0.1"

    def analyze(self, context: dict, cancel_event=None) -> RuleResult:
        files = context.get("translation_files") or []
        count = 0
        for f in files:
            if cancel_event is not None and cancel_event.is_set():
                return RuleResult(rule=self.name, passed=True, details={"translation_files": count, "cancelled": True})
            count += 1
        return RuleResult(rule=self.name, passed=True, details={"translation_files": count})
