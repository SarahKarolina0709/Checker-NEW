"""Tests für Phase2 Checks: Coverage Ratio & Proper Names (aktualisierte Codes).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quality_gui_phase2_checkers import run_phase2_checks


def _codes(issues):
    return {i.code for i in issues}


def test_coverage_ratio_flags_short_target():
    src = "<p>" + ("Sehr wichtiger ausführlicher Quelltext " * 5) + "Ende.</p>"
    tgt = "Kurzer Zieltext."
    issues = run_phase2_checks([(src, tgt)])
    found = _codes(issues)
    # Code kann COVERAGE_RATIO_LOW oder COMPLETENESS_TOO_SHORT sein
    assert found & {"COVERAGE_RATIO_LOW", "COMPLETENESS_TOO_SHORT", "COMPLETENESS_WORDS_MISSING"}, \
        f"Kein Vollständigkeits-Problem erkannt: {found}"


def test_proper_name_missing():
    src = "Die Lösung von Acme Corp wird von NASA unterstützt."
    tgt = "Die Lösung wird unterstützt."
    issues = run_phase2_checks([(src, tgt)])
    found = _codes(issues)
    # Code kann PROPER_NAME_MISSING oder COMPANY_NAME_MISSING sein
    assert found & {"PROPER_NAME_MISSING", "COMPANY_NAME_MISSING", "ACRONYM_MISSING"}, \
        f"Kein Eigenname-Problem erkannt: {found}"
