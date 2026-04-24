"""Tests für Phase 2 Checker — Inhalt & Konsistenz.

Abgedeckt:
 - HTML-Tags (Void-Tags, Security)
 - Zahlen & Einheiten
 - Eigennamen (False-Positive-Reduktion)
 - Terminologie
 - Unübersetzte Segmente
 - Zeichensetzung
 - Reale Übersetzungspaare (False-Positive-Freiheit)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from quality_gui_phase2_checkers import (
    run_phase2_checks,
    check_html_tags,
    check_numbers_units,
    check_proper_names,
    check_untranslated_segments,
    check_empty_translation,
    check_punctuation,
    check_security,
    check_sentence_case,
    QAIssue,
)


def _codes(issues):
    return {i.code for i in issues}


# ============================================================================
# HTML Tags
# ============================================================================
class TestHtmlTags:
    def test_void_tags_not_flagged(self):
        pairs = [("<p>Test</p><br><img src='a.png'>", "<p>Test</p><br><img src='a.png'>")]
        issues = run_phase2_checks(pairs)
        assert "HTML_UNBALANCED" not in _codes(issues)

    def test_missing_tag_in_target(self):
        issues = check_html_tags("<b>Wichtig</b>", "Wichtig")
        assert any("HTML" in i.code for i in issues)

    def test_matching_tags_no_issue(self):
        assert not check_html_tags("<p>Text</p>", "<p>Text</p>")


# ============================================================================
# Security
# ============================================================================
class TestSecurity:
    def test_event_handler_detected(self):
        pairs = [("<div>Hallo</div>", '<div onclick="run()">Hallo</div>')]
        issues = run_phase2_checks(pairs)
        assert "SECURITY_EVENT_HANDLER" in _codes(issues)

    def test_onclick_word_not_attribute(self):
        pairs = [("Text", 'Nur Text onclick="run()" hier')]
        issues = run_phase2_checks(pairs)
        assert "SECURITY_EVENT_HANDLER" not in _codes(issues)

    def test_javascript_scheme(self):
        issues = check_security("<a href='safe'>", "<a href='javascript:alert(1)'>")
        assert any("SECURITY" in i.code for i in issues)


# ============================================================================
# Zahlen & Einheiten
# ============================================================================
class TestNumbersUnits:
    def test_matching_numbers(self):
        issues = check_numbers_units("Der Preis beträgt 100 Euro.", "The price is 100 Euro.")
        num_issues = [i for i in issues if "NUMBER" in i.code]
        assert len(num_issues) == 0

    def test_missing_number(self):
        issues = check_numbers_units("Der Wert ist 42.", "Der Wert ist groß.")
        assert any("NUMBER" in i.code for i in issues)

    def test_unit_drift(self):
        pairs = [("Das Paket wiegt 10 kg.", "Das Paket wiegt 10.")]
        issues = run_phase2_checks(pairs)
        assert "UNIT_DRIFT" in _codes(issues)

    def test_percentage_preserved(self):
        issues = check_numbers_units("Steigerung um 25%", "Increase by 25%")
        num_issues = [i for i in issues if "NUMBER" in i.code]
        assert len(num_issues) == 0

    def test_date_not_flagged_as_number(self):
        """Datumsbestandteile sollten nicht als fehlende Zahlen gemeldet werden."""
        issues = check_numbers_units("Am 15. März 2024", "On March 15, 2024")
        critical = [i for i in issues if i.severity == "critical" and "NUMBER" in i.code]
        assert len(critical) == 0


# ============================================================================
# Eigennamen
# ============================================================================
class TestProperNames:
    def test_name_preserved(self):
        """Echte Eigennamen (Dr. + Nachname) sollten erkannt werden."""
        issues = check_proper_names(
            "Dr. Hans Weber erklärt die Methode.",
            "Dr. Hans Weber explains the method.",
            {}, whitelist=set(), dnt=set()
        )
        # Name ist in beiden -> kein Fehler
        name_issues = [i for i in issues if "NAME" in i.code]
        assert len(name_issues) == 0

    def test_name_missing_in_target(self):
        issues = check_proper_names(
            "Dr. Hans Weber erklärt die Methode.",
            "Der Arzt erklärt die Methode.",
            {}, whitelist=set(), dnt=set()
        )
        assert any("NAME" in i.code for i in issues)

    def test_no_false_positive_for_common_nouns(self):
        """'Neue Implementierung', 'Diese Lösung' sind KEINE Eigennamen."""
        issues = check_proper_names(
            "Diese Lösung ist besser als die Neue Implementierung.",
            "This solution is better than the new implementation.",
            {}, whitelist=set(), dnt=set()
        )
        name_issues = [i for i in issues if "NAME" in i.code]
        assert len(name_issues) == 0, f"False Positives: {[i.message for i in name_issues]}"

    def test_company_name_dnt(self):
        """Firmenbezeichnungen (GmbH, AG) sollten als DNT erkannt werden."""
        issues = check_proper_names(
            "Die Müller GmbH produziert Stahl.",
            "Müller GmbH produces steel.",
            {}, whitelist=set(), dnt=set()
        )
        # Müller GmbH sollte in beiden sein -> kein Fehler
        company_issues = [i for i in issues if "COMPANY" in i.code.upper() or "DNT" in i.code.upper()]
        assert len(company_issues) == 0


# ============================================================================
# Unübersetzte Segmente
# ============================================================================
class TestUntranslated:
    def test_identical_text_detected(self):
        issues = check_untranslated_segments(
            "Der schnelle braune Fuchs",
            "Der schnelle braune Fuchs"
        )
        assert any("UNTRANSLATED" in i.code for i in issues)

    def test_translated_text_ok(self):
        issues = check_untranslated_segments(
            "Der schnelle braune Fuchs",
            "The quick brown fox"
        )
        assert not any("UNTRANSLATED" in i.code for i in issues)

    def test_empty_translation(self):
        issues = check_empty_translation("Source text", "")
        assert len(issues) > 0


# ============================================================================
# Integration: Reale Übersetzungspaare
# ============================================================================
class TestProperNameVariants:
    """Regression-Tests für Bug #3: Asymmetrischer Namensvergleich."""

    def test_title_added_in_target_not_flagged(self):
        """'Hans Weber' (src) → 'Dr. Hans Weber' (tgt) ist KEIN neuer Name."""
        issues = check_proper_names(
            "Der Bericht von Hans Weber zeigt gute Ergebnisse.",
            "The report by Dr. Hans Weber shows good results.",
            {}, whitelist=set(), dnt=set()
        )
        added = [i for i in issues if i.code == "PROPER_NAME_ADDED"]
        assert len(added) == 0, f"False Positive: {[i.message for i in added]}"

    def test_shortened_name_with_title_in_target(self):
        """'Hans Weber' (src) → 'Dr. Weber' (tgt) ist OK (Titel + Nachname)."""
        issues = check_proper_names(
            "Hans Weber erklärt die Methode.",
            "Dr. Weber explains the method.",
            {}, whitelist=set(), dnt=set()
        )
        missing = [i for i in issues if i.code == "PROPER_NAME_MISSING"]
        assert len(missing) == 0, f"False Positive: {[i.message for i in missing]}"

    def test_completely_missing_name_detected(self):
        """Komplett fehlender Name MUSS gemeldet werden."""
        issues = check_proper_names(
            "Dr. Hans Weber erklärt die Methode.",
            "Der Arzt erklärt die Methode.",
            {}, whitelist=set(), dnt=set()
        )
        assert any("NAME" in i.code for i in issues)


class TestCompanyNameExtraction:
    """Regression-Tests für Company-Name-Bugs."""

    def test_article_stripped(self):
        """'Die Müller GmbH' → Firmenname ist 'Müller GmbH', nicht 'Die Müller GmbH'."""
        issues = run_phase2_checks([
            ("Die Müller GmbH produziert Stahl.", "Müller GmbH produces steel.")
        ])
        company_issues = [i for i in issues if "COMPANY" in i.code]
        assert len(company_issues) == 0, f"False Positive: {[i.message for i in company_issues]}"

    def test_long_prefix_not_included(self):
        """'der Vertrag der Müller GmbH' → Nur 'Müller GmbH', nicht der ganze Satz."""
        issues = run_phase2_checks([
            ("Laut Vertrag der Müller GmbH gilt folgendes.", "According to the contract of Müller GmbH the following applies.")
        ])
        company_issues = [i for i in issues if "COMPANY" in i.code]
        assert len(company_issues) == 0, f"False Positive: {[i.message for i in company_issues]}"


class TestRealWorldPairs:
    def test_business_text_de_en(self):
        """Realistischer Geschäftsbericht DE→EN: keine kritischen False Positives."""
        src = (
            "Die Geschäftsführung hat beschlossen, die Investitionen "
            "im Bereich erneuerbare Energien um 25% zu erhöhen. "
            "Dies betrifft sowohl Solar- als auch Windenergie-Projekte "
            "in Deutschland und Österreich."
        )
        tgt = (
            "The management has decided to increase investments in "
            "renewable energy by 25%. This affects both solar and wind "
            "energy projects in Germany and Austria."
        )
        issues = run_phase2_checks([(src, tgt)])
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0, f"False Positives: {[(i.code, i.message) for i in critical]}"

    def test_technical_manual_de_en(self):
        """Technisches Handbuch mit Zahlen und Einheiten."""
        src = "Die maximale Betriebstemperatur beträgt 85°C bei einer Spannung von 230V."
        tgt = "The maximum operating temperature is 85°C at a voltage of 230V."
        issues = run_phase2_checks([(src, tgt)])
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0, f"False Positives: {[(i.code, i.message) for i in critical]}"

    def test_legal_text_with_proper_names(self):
        """Juristischer Text mit Eigennamen."""
        src = "Laut Dr. Schmidt ist der Vertrag der Müller GmbH gültig."
        tgt = "According to Dr. Schmidt, the contract of Müller GmbH is valid."
        issues = run_phase2_checks([(src, tgt)])
        name_issues = [i for i in issues if "NAME" in i.code]
        assert len(name_issues) == 0, f"False Positives: {[(i.code, i.message) for i in name_issues]}"
