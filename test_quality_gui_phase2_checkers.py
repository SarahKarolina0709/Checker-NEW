"""Tests für Phase 2 Checker (HTML / Security / Zahlen-Einheiten).

Abgedeckt:
 - Void-Tags (br, img) erzeugen kein HTML_UNBALANCED
 - Event-Handler nur wenn wirklich als Attribut in Tag vorhanden
 - Inline onclick Text ohne Tag kein SECURITY_EVENT_HANDLER
 - UNIT_DRIFT nur wenn echte Abweichung (Einheit an Zahl gebunden)
"""
from __future__ import annotations

import pytest

from quality_gui_phase2_checkers import run_phase2_checks, QAIssue


def _codes(issues):
    return sorted({i.code for i in issues})


def test_void_tags_not_flagged():
    pairs = [("<p>Test</p><br><img src='a.png'>", "<p>Test</p><br><img src='a.png'>")]
    issues = run_phase2_checks(pairs)
    assert "HTML_UNBALANCED" not in _codes(issues)


def test_event_handler_attribute_detected():
    pairs = [("<div>Hallo</div>", "<div onclick=\"run()\">Hallo</div>")]
    issues = run_phase2_checks(pairs)
    assert "SECURITY_EVENT_HANDLER" in _codes(issues)


def test_onclick_word_not_attribute():
    # onclick= erscheint ohne vorangehendes Tag – darf keinen Handler erzeugen
    pairs = [("Text ohne", "Nur Text onclick=\"run()\" hier")]
    issues = run_phase2_checks(pairs)
    assert "SECURITY_EVENT_HANDLER" not in _codes(issues)


def test_unit_drift_only_for_number_bound_units():
    # Quelle hat "10 kg" Ziel hat nur "10" – sollte UNIT_DRIFT melden
    pairs = [("Das Paket wiegt 10 kg.", "Das Paket wiegt 10.")]
    issues = run_phase2_checks(pairs)
    assert "UNIT_DRIFT" in _codes(issues)
    # Einheit erscheint isoliert ohne Zahl -> sollte nicht zählen (keine Drift)
    pairs2 = [("10 kg geliefert", "10 geliefert kg")]
    issues2 = run_phase2_checks(pairs2)
    # Ziel hat keine Zahl direkt vor kg, Quelle schon → Drift (weiterhin erkannt)
    assert "UNIT_DRIFT" in _codes(issues2)
