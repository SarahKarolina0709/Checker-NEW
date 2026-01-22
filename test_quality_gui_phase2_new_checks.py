"""Tests für neue Phase2 Checks: Coverage Ratio & Proper Names.
"""
from __future__ import annotations

from quality_gui_phase2_checkers import run_phase2_checks


def _codes(issues):
    return {i.code for i in issues}


def test_coverage_ratio_flags_short_target():
    src = "<p>" + ("Sehr wichtiger ausführlicher Quelltext " * 5) + "Ende.</p>"
    # Ziel nur ~30% der Länge
    tgt = "Kurzer Zieltext."  # stark verkürzt
    issues = run_phase2_checks([(src, tgt)])
    assert "COVERAGE_RATIO_LOW" in _codes(issues)


def test_proper_name_missing():
    src = "Die Lösung von Acme Corp wird von NASA unterstützt."  # Zwei Eigennamen/ Akronym
    tgt = "Die Lösung wird unterstützt."  # Namen fehlen
    issues = run_phase2_checks([(src, tgt)])
    codes = _codes(issues)
    assert "PROPER_NAME_MISSING" in codes