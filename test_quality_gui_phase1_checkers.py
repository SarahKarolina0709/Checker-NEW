"""Tests für quality_gui_phase1_checkers Platzhalter-Parser & ORDER-Logik.

Abdeckt:
 - Einzelnes % kein Placeholder
 - Escaped %% kein Placeholder
 - printf %s, %2$s, %(name)s
 - ICU flach
 - Mustache {{name}}
 - JS Template ${name}
 - :slug ohne Wortzeichen davor
 - ORDER-Hinweis nur bei relevanter Reihenfolgeänderung
"""
from __future__ import annotations

import re
import pytest

from quality_gui_phase1_checkers import (
    extract_placeholders,
    check_placeholders,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("100% sicher", []),  # einzelnes % ignorieren
        ("Fortschritt %% fertig", []),  # escaped %% ignorieren
        ("Datei %s geladen", ["%s"]),
        ("Werte %2$s und %1$d", ["%2$s", "%1$d"]),
        ("Hallo %(user)s", ["%(user)s"]),
        ("{count, plural, one {1 Datei} other {# Dateien}}", ["{count, plural, one {1 Datei} other {# Dateien}}"]),
        ("{{name}} hat {{count}} Einträge", ["{{name}}", "{{count}}"]),
        ("Preis ${amount} gespeichert", ["${amount}"]),
        (":slug ist erlaubt, a:slug nicht", [":slug"]),
        ("{0} und {name} und %s", ["{0}", "{name}", "%s"]),
    ],
)
def test_extract_placeholders(text, expected):
    assert extract_placeholders(text) == expected


def _issue_codes(issues):
    return sorted(i.code for i in issues)


def test_order_issue_triggers_without_positional_or_named():
    src = "{0} {1} %s"
    tgt = "%s {1} {0}"  # gleiche Multiset, andere Reihenfolge
    issues = check_placeholders(src, tgt)
    codes = _issue_codes(issues)
    assert "PLACEHOLDER_ORDER" in codes, codes


def test_order_issue_suppressed_with_positional():
    src = "%1$s %2$s"
    tgt = "%2$s %1$s"  # Reihenfolge egal wegen Positionsangaben
    issues = check_placeholders(src, tgt)
    codes = _issue_codes(issues)
    assert "PLACEHOLDER_ORDER" not in codes, codes


def test_order_issue_suppressed_with_named_python():
    src = "%(user)s %(date)s"
    tgt = "%(date)s %(user)s"
    issues = check_placeholders(src, tgt)
    codes = _issue_codes(issues)
    assert "PLACEHOLDER_ORDER" not in codes, codes


def test_missing_and_extra_detection():
    src = "{0} %(user)s %s"
    tgt = "{0} %s"
    issues = check_placeholders(src, tgt)
    codes = _issue_codes(issues)
    assert "PLACEHOLDER_MISSING" in codes and "PLACEHOLDER_EXTRA" not in codes


def test_extra_detection():
    src = "{0} %s"
    tgt = "{0} %s %(user)s"
    issues = check_placeholders(src, tgt)
    codes = _issue_codes(issues)
    assert "PLACEHOLDER_EXTRA" in codes and "PLACEHOLDER_MISSING" not in codes
