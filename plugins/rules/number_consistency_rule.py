"""Prüft Zahlenkonsistenz zwischen Quell- und Zieltext über alle Paare.

Erwartet im Kontext:
  - pairs: Liste mit Dict-Einträgen inkl. 'numbers_missing' / 'numbers_extra'
"""
from __future__ import annotations
from plugins.base_rule import BaseRule, RuleResult


class NumberConsistencyRule(BaseRule):
    name = "number_consistency"
    version = "0.1"

    def analyze(self, context: dict) -> RuleResult:
        pairs = context.get("pairs") or []
        total_missing = 0
        total_extra = 0
        affected = 0
        details_list = []
        for p in pairs:
            missing = p.get("numbers_missing") or []
            extra = p.get("numbers_extra") or []
            if missing or extra:
                affected += 1
                total_missing += len(missing)
                total_extra += len(extra)
                details_list.append({
                    "pair_id": p.get("id"),
                    "missing": missing,
                    "extra": extra
                })
        passed = (total_missing + total_extra) == 0
        return RuleResult(
            rule=self.name,
            passed=passed,
            details={
                "pairs_affected": affected,
                "total_missing": total_missing,
                "total_extra": total_extra,
                "issues": details_list[:50]  # Begrenzung
            }
        )
