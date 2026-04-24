"""Tests für Phase 3 Checker — Semantik, Stil, Lesbarkeit, Grammatik.

Abgedeckt:
 - Passiv-Erkennung (Deutsch)
 - Lesbarkeit (LIX)
 - Stil-Checks
 - Integration: Reale Übersetzungspaare
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from quality_gui_phase3_checkers import run_phase3_checks


def _codes(issues):
    return {i.code for i in issues}


class TestPassive:
    def test_german_passive_heavy(self):
        """Viele Passiv-Sätze sollten erkannt werden."""
        tgt = (
            "Das Modul wird gebaut. "
            "Die Komponente wird gründlich getestet. "
            "Die Anwendung wurde erfolgreich geliefert. "
            "Analyse abgeschlossen. "
            "Kurzer Abschlusssatz."
        )
        issues = run_phase3_checks([("", tgt)], enable_semantic=False)
        assert "STYLE_PASSIVE_HEAVY_DE" in _codes(issues), _codes(issues)

    def test_active_text_no_passive_flag(self):
        """Aktiver Text sollte keinen Passiv-Flag erzeugen."""
        tgt = (
            "Das Team entwickelt die Software. "
            "Der Kunde prüft die Ergebnisse. "
            "Wir liefern pünktlich. "
            "Die Analyse zeigt gute Werte. "
            "Alle Kriterien sind erfüllt."
        )
        issues = run_phase3_checks([("", tgt)], enable_semantic=False)
        assert "STYLE_PASSIVE_HEAVY_DE" not in _codes(issues)


class TestReadability:
    def test_complex_text_flagged(self):
        """Sehr lange Sätze sollten Lesbarkeits-Warnung erzeugen."""
        tgt = (
            "Die durch das im vergangenen Quartal implementierte und "
            "unter Berücksichtigung aller relevanten regulatorischen "
            "Anforderungen der europäischen Datenschutzgrundverordnung "
            "sowie der nationalen Ausführungsbestimmungen durchgeführte "
            "Überprüfung der informationstechnologischen Infrastruktur "
            "hat ergeben dass sämtliche Systeme den Vorgaben entsprechen."
        )
        issues = run_phase3_checks([("", tgt)], enable_semantic=False)
        lix_codes = {i.code for i in issues if "LIX" in i.code or "READABILITY" in i.code}
        assert len(lix_codes) > 0, f"Keine Lesbarkeits-Warnung für komplexen Text"


class TestIntegration:
    def test_clean_pair_minimal_issues(self):
        """Sauberes DE→EN Paar sollte keine kritischen Issues haben."""
        src = "Die Firma hat 500 Mitarbeiter und einen Umsatz von 50 Millionen Euro."
        tgt = "The company has 500 employees and a revenue of 50 million euros."
        issues = run_phase3_checks([(src, tgt)], enable_semantic=False)
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0, f"False Positives: {[(i.code, i.message) for i in critical]}"

    def test_empty_pairs(self):
        assert run_phase3_checks([], enable_semantic=False) == []

    def test_semantic_disabled(self):
        """Mit enable_semantic=False sollte kein Embedding-Import passieren."""
        src = "Kurzer Text."
        tgt = "Short text."
        # Sollte nicht crashen auch ohne sentence-transformers
        issues = run_phase3_checks([(src, tgt)], enable_semantic=False)
        # Kein crash = Erfolg
        assert isinstance(issues, list)
