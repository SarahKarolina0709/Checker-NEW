"""Tests für quality_gui_phase1_checkers — Format & Struktur Checks.

Testet jede Check-Funktion mit echten Übersetzungsbeispielen,
um sowohl korrekte Erkennung als auch False-Positive-Freiheit zu prüfen.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from quality_gui_phase1_checkers import (
    QAIssue,
    run_phase1_checks,
    check_urls_emails,
    check_whitespace_and_zero_width,
    check_boundary_whitespace,
    check_soft_hyphens_and_control_chars,
    check_brackets_basic,
    check_quotes_basic,
)


def codes(issues):
    return {i.code for i in issues}

def has_code(issues, code):
    return any(i.code == code for i in issues)


class TestUrlsEmails:
    def test_matching_urls_no_issue(self):
        assert not check_urls_emails("Siehe https://example.com", "See https://example.com", 0)

    def test_missing_url_in_target(self):
        issues = check_urls_emails("Siehe https://example.com und https://docs.example.com", "Siehe https://example.com", 0)
        assert has_code(issues, "URL_MISSING")

    def test_matching_emails_no_issue(self):
        assert not check_urls_emails("Kontakt: info@example.com", "Contact: info@example.com", 0)

    def test_missing_email(self):
        issues = check_urls_emails("Mail an support@firma.de", "Bitte kontaktieren Sie uns", 0)
        assert has_code(issues, "EMAIL_MISSING")

    def test_empty_strings(self):
        assert not check_urls_emails("", "", 0)

    def test_url_with_query_params(self):
        url = "https://api.example.com/v2?key=abc&format=json"
        assert not check_urls_emails(f"Link: {url}", f"Link: {url}", 0)


class TestWhitespace:
    def test_clean_text(self):
        assert not check_whitespace_and_zero_width("Normaler Text.", "Normal text.", 0)

    def test_zero_width_space(self):
        issues = check_whitespace_and_zero_width("Normal", "Nor\u200Bmal", 0)
        assert has_code(issues, "ZERO_WIDTH_CHAR")

    def test_double_spaces(self):
        issues = check_whitespace_and_zero_width("Ein Text", "Ein  Text", 0)
        assert has_code(issues, "WS_DOUBLE_SPACE")


class TestBoundaryWhitespace:
    def test_clean(self):
        assert not check_boundary_whitespace("Hello", "Hallo", 0)

    def test_leading_space(self):
        issues = check_boundary_whitespace("OK", " OK", 0)
        assert has_code(issues, "BOUNDARY_SPACE_START_ADDED")

    def test_trailing_space(self):
        issues = check_boundary_whitespace("Text", "Text ", 0)
        assert has_code(issues, "BOUNDARY_SPACE_END_ADDED")


class TestSoftHyphensAndControlChars:
    def test_clean(self):
        assert not check_soft_hyphens_and_control_chars("Normal", "Normal", 0)

    def test_soft_hyphen(self):
        issues = check_soft_hyphens_and_control_chars("Qualität", "Quali\u00ADtät", 0)
        assert has_code(issues, "SOFT_HYPHEN_ADDED")

    def test_null_char_is_major(self):
        issues = check_soft_hyphens_and_control_chars("Text", "Text\x00", 0)
        assert has_code(issues, "CONTROL_CHARS_FOUND")
        ctrl = [i for i in issues if i.code == "CONTROL_CHARS_FOUND"][0]
        assert ctrl.severity == "major"

    def test_harmless_control_char_is_minor(self):
        issues = check_soft_hyphens_and_control_chars("Text", "Text\x01", 0)
        assert has_code(issues, "CONTROL_CHARS_FOUND")
        ctrl = [i for i in issues if i.code == "CONTROL_CHARS_FOUND"][0]
        assert ctrl.severity == "minor"


class TestBrackets:
    def test_balanced(self):
        assert not check_brackets_basic("Wert (Anhang)", "Value (Appendix)", 0)

    def test_missing_closing(self):
        issues = check_brackets_basic("Wert (Anhang)", "Value (Appendix", 0)
        assert has_code(issues, "BRACKET_UNCLOSED")

    def test_enumeration_ok(self):
        assert not has_code(
            check_brackets_basic("a) Erster b) Zweiter", "a) First b) Second", 0),
            "BRACKET_MISMATCH"
        )

    def test_nested(self):
        assert not check_brackets_basic("(mit [inneren] Klammern)", "(with [inner] brackets)", 0)


class TestQuotes:
    def test_matching(self):
        assert not check_quotes_basic('Er sagte "Hallo".', 'He said "Hello".', 0)

    def test_german_typographic(self):
        assert not check_quotes_basic('Er sagte \u201EHallo\u201C.', 'Er sagte \u201EHallo\u201C.', 0)

    def test_apostrophes_not_quotes(self):
        assert not check_quotes_basic("I don't know what he's saying.", "Ich weiß nicht was er sagt.", 0)


class TestRunPhase1:
    def test_clean_pair(self):
        assert run_phase1_checks([("Hallo Welt", "Hello World")]) == []

    def test_multiple_issues(self):
        pairs = [
            ("Siehe https://example.com", "See website"),
            ("Text (Klammer)", "Text (Bracket"),
        ]
        issues = run_phase1_checks(pairs)
        found = codes(issues)
        assert "URL_MISSING" in found
        assert "BRACKET_UNCLOSED" in found

    def test_segment_index_set(self):
        pairs = [("Ok", "Ok"), ("Siehe https://x.com", "Nein")]
        issues = run_phase1_checks(pairs)
        assert all(i.segment_index == 1 for i in issues)

    def test_empty(self):
        assert run_phase1_checks([]) == []

    def test_real_world_no_false_positives(self):
        src = "Die Geschäftsführung hat beschlossen, die Investitionen im Bereich erneuerbare Energien um 25% zu erhöhen."
        tgt = "The management has decided to increase investments in renewable energy by 25%."
        issues = run_phase1_checks([(src, tgt)])
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0, f"False Positives: {[i.code for i in critical]}"
