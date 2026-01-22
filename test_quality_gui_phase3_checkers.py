"""Tests für Phase 3 Checker (Risk / Passiv / Base64 Heuristik).

Abgedeckt:
 - Base64 Sequenz nur wenn nicht im Source vorhanden
 - Erweiterte DE Passiv Erkennung (sein + ge* + worden)
"""
from __future__ import annotations

import pytest

from quality_gui_phase3_checkers import run_phase3_checks


def _codes(issues):
    return sorted({i.code for i in issues})


def test_base64_only_new_in_target():
    b64 = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # 32 Zeichen, Base64-Muster
    pairs = [("Plain", f"Text {b64} eingebettet")]  # nur im Ziel
    issues = run_phase3_checks(pairs, enable_semantic=False)
    assert "RISK_BASE64_SUSPECT" in _codes(issues)
    # Jetzt auch im Source – sollte verschwinden
    pairs2 = [(f"{b64} Plain", f"Text {b64} eingebettet")]
    issues2 = run_phase3_checks(pairs2, enable_semantic=False)
    assert "RISK_BASE64_SUSPECT" not in _codes(issues2)


def test_german_passive_sein_worden_pattern():
    # 5 Sätze, 3 Passiv (werden + ge-Partizip) => Anteil 0.6 > 0.4, >=3 Treffer
    tgt = (
        "Das Modul wird gebaut. "
        "Die Komponente wird gründlich getestet. "
        "Die Anwendung wurde erfolgreich geliefert. "
        "Analyse abgeschlossen. "
        "Kurzer Abschlusssatz."
    )
    issues = run_phase3_checks([("", tgt)], enable_semantic=False)
    assert "STYLE_PASSIVE_HEAVY_DE" in _codes(issues), _codes(issues)
