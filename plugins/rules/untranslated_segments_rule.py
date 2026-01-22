"""Erkennt unübersetzte (identische) Segmente zwischen Source und Translation.

Heuristik: identische Zeilen > 25 Zeichen. Erwartet Kontext:
  - source_texts
  - translation_texts
Optional nutzt vorhandene 'pairs' falls später pro Paar Auswertung gewünscht.
"""
from __future__ import annotations
from plugins.base_rule import BaseRule, RuleResult


class UntranslatedSegmentsRule(BaseRule):
    name = "untranslated_segments"
    version = "0.1"

    def analyze(self, context: dict) -> RuleResult:
        sources = context.get("source_texts") or []
        translations = context.get("translation_texts") or []
        total_segments = 0
        untranslated = 0
        sample = []
        for src, trg in zip(sources, translations):
            if not src or not trg:
                continue
            src_lines = [l.strip() for l in src.splitlines() if l.strip()]
            trg_lines = set(l.strip() for l in trg.splitlines() if l.strip())
            for l in src_lines:
                if len(l) > 25:
                    total_segments += 1
                    if l in trg_lines:
                        untranslated += 1
                        if len(sample) < 25:
                            sample.append(l[:160])
        ratio = untranslated / (total_segments or 1)
        # Schwelle: mehr als 8% identische Segmente => failed
        passed = ratio <= 0.08
        return RuleResult(
            rule=self.name,
            passed=passed,
            details={
                "total_segments": total_segments,
                "untranslated_segments": untranslated,
                "untranslated_ratio": round(ratio, 4),
                "sample": sample
            }
        )
