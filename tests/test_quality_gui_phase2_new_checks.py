"""Tests für Phase2 Checks: Coverage Ratio & Proper Names (aktualisierte Codes).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quality_gui_phase2_checkers import run_phase2_checks, check_coverage_ratio


def _codes(issues):
    return {i.code for i in issues}


def test_coverage_is_language_pair_aware():
    # Gleiches Laengenverhaeltnis (Ziel ~65% der Quelle), aber die Richtung
    # entscheidet, ob es "zu kurz" ist:
    src = "x" * 200
    tgt = "y" * 130  # ratio 0.65
    # EN->DE: Deutsch sollte LAENGER sein (erwartet ~115%) -> 65% ist zu kurz
    en_de = check_coverage_ratio(src, tgt, min_ratio=0.6, src_lang='en', tgt_lang='de')
    assert any(i.code == 'COMPLETENESS_TOO_SHORT' for i in en_de)
    # DE->EN: Englisch ist von Natur kuerzer (erwartet ~90%) -> 65% ist ok
    de_en = check_coverage_ratio(src, tgt, min_ratio=0.6, src_lang='de', tgt_lang='en')
    assert not any(i.code == 'COMPLETENESS_TOO_SHORT' for i in de_en)


def test_coverage_neutral_when_lang_unknown():
    # Ohne Sprachinfo neutral (erwartet 100%) -> bisheriges Verhalten
    src = "x" * 200
    tgt = "y" * 80  # ratio 0.40 < 0.6
    issues = check_coverage_ratio(src, tgt, min_ratio=0.6)
    assert any(i.code == 'COMPLETENESS_TOO_SHORT' for i in issues)


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
