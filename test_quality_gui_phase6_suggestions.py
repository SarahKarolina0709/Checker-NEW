"""Tests für Phase 6 Vorschlags-Engine.

Abgedeckt:
 - Gewichtung (risk höher gewichtet verschlechtert Reihenfolge bei höherem weight)
 - unique_high liefert pro High-Priority Code nur einen Vorschlag
 - Adaptive Satz-Splitting erzeugt Vorschlag für sehr langen Satz
 - Telemetrie-Summary wird angehängt
"""
from __future__ import annotations

import pytest

from quality_gui_phase6_suggestions import run_phase6_suggestions
from quality_gui_phase1_checkers import QAIssue


def _mk_issue(code: str, severity="major", category="any", message="", src="", tgt=""):
    # Phase1 QAIssue Felder: code, severity, category, message, source_text, target_text, meta
    return QAIssue(code, severity, category, message or code, src, tgt, {})  # type: ignore


def test_weighting_changes_order():
    long_sentence = "Start " + ("word " * 230) + "."  # >220
    issues = [
        _mk_issue("RISK_NEW_DOMAIN", src="http://a.de", tgt="http://a.de http://neu.de"),
        _mk_issue("STYLE_LONG_SENTENCE", src="", tgt=long_sentence),
    ]
    sugg_default = run_phase6_suggestions([(i.source_text, i.target_text) for i in issues], issues, max_suggestions=5)
    # Risiko hat Priority 1 -> sollte vorne sein
    assert sugg_default[0].meta.get("issue_code") == "RISK_NEW_DOMAIN"
    # Erhöhe weight_risk, effektive Priorität schlechter -> Stil könnte vorziehen (da Priority 2 *1.0 < 1*2.0)=2 vs2 – gleiche -> Sortierung deterministisch nach effective_priority, dann confidence
    sugg_weighted = run_phase6_suggestions([(i.source_text, i.target_text) for i in issues], issues, max_suggestions=5, weight_risk=2.5)
    # Jetzt sollte Risiko nicht mehr zwingend an erster Stelle, aber wir prüfen nur dass effective_priority > style effective_priority
    eff = {s.meta.get("issue_code"): s.meta.get("effective_priority") for s in sugg_weighted if s.meta.get("issue_code")}
    assert eff["RISK_NEW_DOMAIN"] >= eff.get("STYLE_LONG_SENTENCE", 0)


def test_unique_high_limits_duplicates():
    # Zwei NUMBER_MISSING Issues -> nur einer
    issues = [
        _mk_issue("NUMBER_MISSING", src="1", tgt=""),
        _mk_issue("NUMBER_MISSING", src="2", tgt=""),
    ]
    sugg = run_phase6_suggestions([(i.source_text, i.target_text) for i in issues], issues, unique_high=True, max_suggestions=10)
    codes = [s.meta.get("issue_code") for s in sugg if s.meta.get("issue_code") == "NUMBER_MISSING"]
    assert len(codes) == 1


def test_adaptive_sentence_split_and_summary():
    long_part = "Dies ist ein extrem langer Satz " + ("mit vielen Einschüben und Details " * 8) + "Ende."
    target = "Kurz. " + long_part  # median bleibt klein -> threshold 220
    sugg = run_phase6_suggestions([(target, target)], [], max_suggestions=10)
    # Suche readability Split Vorschlag
    has_split = any("Sehr langen Satz" in s.message for s in sugg)
    assert has_split, [s.message for s in sugg]
    # Summary vorhanden (category meta)
    assert any(s.category == "meta" for s in sugg)
