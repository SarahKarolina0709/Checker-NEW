"""Sample rule implementation measuring total characters of source text.
Demonstrates minimal analyze interface usage.
"""
from __future__ import annotations
from .base_rule import BaseRule, RuleResult

class LengthRule(BaseRule):
    name = "length"
    version = "0.1"

    def analyze(self, context: dict, cancel_event=None) -> RuleResult:  # cooperative cancellation optional
        if cancel_event is not None and getattr(cancel_event, 'is_set', lambda: False)():
            return RuleResult(rule=self.name, passed=False, details={"cancelled": True})
        sources = context.get("source_texts") or []
        total_chars = 0
        for s in sources:
            if cancel_event is not None and cancel_event.is_set():
                return RuleResult(rule=self.name, passed=False, details={"partial_total_chars": total_chars, "cancelled": True})
            total_chars += len(s or "")
        passed = total_chars > 0
        return RuleResult(rule=self.name, passed=passed, details={"total_chars": total_chars})
