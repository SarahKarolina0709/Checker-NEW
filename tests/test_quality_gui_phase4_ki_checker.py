"""Tests für Phase 4 KI-Checker — Parsing & Segment-Zuordnung.

Der eigentliche Ollama-Aufruf (`ki_qualitaetspruefung_vergleich`) wird gemockt,
damit die Tests ohne laufenden Ollama-Dienst deterministisch laufen.

Abgedeckt:
 - JSON-Parsing der KI-Antwort (auch in Markdown-Codeblöcken)
 - Severity-Ableitung aus der Erklärung
 - Segment-Zuordnung über context-Feld und Pfeil-Format ("quelle -> ziel")
"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json

import pytest

import quality_gui_phase4_ki_checker as p4
from quality_gui_phase4_ki_checker import (
    run_ki_checks,
    _parse_ki_response,
    _severity_from_explanation,
    _to_bcp47,
)


def _patch_ki(monkeypatch, payload):
    """Mockt den Ollama-Aufruf in ki_module mit fester Antwort."""
    import ki_module
    monkeypatch.setattr(
        ki_module,
        'ki_qualitaetspruefung_vergleich',
        lambda **kwargs: payload,
    )


class TestParseResponse:
    def test_plain_json_array(self):
        resp = '[{"error_text": "a", "context": "b", "explanation": "c"}]'
        out = _parse_ki_response(resp)
        assert len(out) == 1
        assert out[0]['error_text'] == 'a'

    def test_json_in_markdown_block(self):
        resp = 'Hier ist meine Antwort:\n```json\n[{"error_text": "x"}]\n```'
        out = _parse_ki_response(resp)
        assert out == [{'error_text': 'x'}]

    def test_empty_array(self):
        assert _parse_ki_response('[]') == []

    def test_error_message_skipped(self):
        assert _parse_ki_response('KI-Analyse übersprungen, da ...') == []
        assert _parse_ki_response('Ollama konnte nicht erreicht werden') == []

    def test_garbage_returns_empty(self):
        assert _parse_ki_response('völlig kaputt ohne klammern') == []


class TestSeverity:
    def test_critical(self):
        assert _severity_from_explanation('Das ist eine falsche Bedeutung') == 'critical'

    def test_major(self):
        assert _severity_from_explanation('inhaltlich falsch übersetzt') == 'major'

    def test_minor_default(self):
        assert _severity_from_explanation('kleine Abweichung') == 'minor'

    def test_negation_not_critical(self):
        # "nicht kritisch" darf nicht als critical durchschlagen
        assert _severity_from_explanation('Das ist nicht kritisch') != 'critical'


class TestBcp47:
    def test_known_code(self):
        assert _to_bcp47('de') == 'de-DE'
        assert _to_bcp47('it') == 'it-IT'

    def test_already_bcp(self):
        assert _to_bcp47('en-GB') == 'en-GB'

    def test_empty_defaults_de(self):
        assert _to_bcp47('') == 'de-DE'


class TestSegmentAttribution:
    """Kernregression: Befunde müssen dem richtigen Segment zugeordnet werden."""

    PAIRS = [
        ('Das Produkt kostet 100 Euro.', 'Il prodotto costa 1000 euro.'),
        ('Die Ampel ist rot.', 'Il semaforo e blu.'),
        ('Bitte schalten Sie das Gerät aus.', 'Si prega di spegnere il dispositivo.'),
    ]

    def test_attribution_via_context_field(self, monkeypatch):
        # Modell liefert Quellsatz im context-Feld OHNE [N]-Klammer
        payload = json.dumps([
            {'error_text': 'rot -> blu', 'context': 'Die Ampel ist rot.',
             'explanation': 'Die Farbe wurde falsch übersetzt.'},
        ])
        _patch_ki(monkeypatch, payload)
        issues = run_ki_checks(self.PAIRS, src_lang='de', tgt_lang='it')
        assert len(issues) == 1
        # "Die Ampel ist rot." ist Segment-Index 1
        assert issues[0].segment_index == 1

    def test_attribution_via_arrow_target_part(self, monkeypatch):
        # Kein context, aber Pfeil-Format mit Ziel-Substring "dispositivo"
        payload = json.dumps([
            {'error_text': 'Gerät -> dispositivo', 'context': '',
             'explanation': 'Der Name des Geräts wurde falsch übersetzt.'},
        ])
        _patch_ki(monkeypatch, payload)
        issues = run_ki_checks(self.PAIRS, src_lang='de', tgt_lang='it')
        assert len(issues) == 1
        assert issues[0].segment_index == 2

    def test_attribution_via_explicit_bracket(self, monkeypatch):
        # Explizite [N]-Klammer hat höchste Priorität
        payload = json.dumps([
            {'error_text': 'irgendwas', 'context': 'siehe Segment [1]',
             'explanation': 'Fehler in [1].'},
        ])
        _patch_ki(monkeypatch, payload)
        issues = run_ki_checks(self.PAIRS, src_lang='de', tgt_lang='it')
        assert len(issues) == 1
        assert issues[0].segment_index == 0

    def test_all_three_segments_distinct(self, monkeypatch):
        payload = json.dumps([
            {'error_text': '100 -> 1000', 'context': 'Das Produkt kostet 100 Euro.',
             'explanation': 'Zahl falsch.'},
            {'error_text': 'rot -> blu', 'context': 'Die Ampel ist rot.',
             'explanation': 'Farbe falsch.'},
            {'error_text': 'Gerät -> dispositivo', 'context': 'Bitte schalten Sie das Gerät aus.',
             'explanation': 'Begriff falsch.'},
        ])
        _patch_ki(monkeypatch, payload)
        issues = run_ki_checks(self.PAIRS, src_lang='de', tgt_lang='it')
        assert [i.segment_index for i in issues] == [0, 1, 2]

    def test_unreachable_ollama_returns_empty(self, monkeypatch):
        _patch_ki(monkeypatch, 'KI-Analyse übersprungen, da der Dienst ...')
        issues = run_ki_checks(self.PAIRS, src_lang='de', tgt_lang='it')
        assert issues == []


class TestSegmentAttributionEdgeCases:
    """Erweiterte Robustheits-Tests der Segment-Zuordnung.

    Deckt schwierige reale Muster ab: Mehrdeutigkeit (Disambiguierung über
    context bzw. Zielwort), Substring-in-Wort-Fallen, alle Pfeil-Varianten,
    ungültige Klammer-Indizes, Groß/Klein- & Whitespace-Normalisierung sowie
    den konservativen „kein Match"-Fallback.
    """

    def _run(self, monkeypatch, pairs, errors):
        _patch_ki(monkeypatch, json.dumps(errors))
        return run_ki_checks(pairs, src_lang='de', tgt_lang='it')

    def test_ambiguous_source_resolved_by_context(self, monkeypatch):
        # 'rot' steht in beiden Quellsätzen -> context muss disambiguieren
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'rot -> blu', 'context': 'Das Auto ist rot.', 'explanation': 'Farbe falsch'}])
        assert [i.segment_index for i in issues] == [1]

    def test_ambiguous_source_resolved_by_target_word(self, monkeypatch):
        # Kein context, 'rot' in beiden Quellen -> Zielwort 'blu' (nur Seg 1) löst auf
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'rot -> blu', 'context': '', 'explanation': 'Farbe falsch'}])
        assert [i.segment_index for i in issues] == [1]

    def test_target_only_match(self, monkeypatch):
        # Nur das Zielwort ist eindeutig (Quellwort käme in beiden vor)
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'rossa -> rosso', 'context': '', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [0]

    @pytest.mark.parametrize('arrow', ['->', '=>', '-->', '==>', '→', '–>', '—>'])
    def test_arrow_variants(self, monkeypatch, arrow):
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': f'rot {arrow} blu', 'context': '', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_multidash_arrow_no_malformed_candidate(self, monkeypatch):
        # Regressions-Falle: '-->' darf nicht zu 'rot -' zerfallen.
        # Segment 0 enthält buchstäblich 'rot -' ("Brot -"), würde also vom
        # alten, fehlerhaften Kandidaten 'rot -' fälschlich getroffen.
        pairs = [('Das Brot - frisch gebacken.', 'Il pane - appena sfornato.'),
                 ('Die Ampel ist rot.', "Il semaforo è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'rot --> blu', 'context': '', 'explanation': 'x'}])
        # Muss Segment 1 (rot/blu) treffen, nicht Segment 0 wegen 'rot -' in 'Brot -'
        assert [i.segment_index for i in issues] == [1]

    def test_substring_in_word_not_false_matched(self, monkeypatch):
        # 'rot' ist Substring von 'Karotte' -> darf Segment 0 NICHT treffen;
        # context auf Segment 1 muss gewinnen.
        pairs = [('Ich esse eine Karotte.', 'Mangio una carota.'),
                 ('Die Ampel ist rot.', 'Il semaforo è blu.')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'rot -> blu', 'context': 'Die Ampel ist rot.', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_invalid_bracket_falls_back_to_text(self, monkeypatch):
        # [99] ist out-of-range -> Text-Fallback greift
        pairs = [('Hund', 'cane'), ('Katze', 'gatto')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'Katze', 'context': 'irgendwo [99]', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_zero_bracket_is_invalid(self, monkeypatch):
        # [0] ist 1-basiert ungültig -> Text-Fallback ('Katze' -> Seg 1)
        pairs = [('Hund', 'cane'), ('Katze', 'gatto')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'Katze', 'context': '[0]', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_three_way_ambiguity_resolved_by_context(self, monkeypatch):
        pairs = [('Wert ist hoch.', 'Valore alto.'),
                 ('Preis ist hoch.', 'Prezzo alto.'),
                 ('Risiko ist hoch.', 'Rischio alto.')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'hoch', 'context': 'Risiko ist hoch.', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [2]

    def test_ten_segments_hit_in_middle(self, monkeypatch):
        pairs = [(f'Satz Nummer {i} hier.', f'Frase numero {i} qui.') for i in range(10)]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'sieben -> sette', 'context': 'Satz Nummer 7 hier.', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [7]

    def test_case_and_whitespace_normalized(self, monkeypatch):
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'X', 'context': '  DAS AUTO IST ROT.  ', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_quoted_error_text(self, monkeypatch):
        pairs = [('Ich esse eine Karotte.', 'Mangio una carota.'),
                 ('Die Ampel ist rot.', 'Il semaforo è blu.')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': '"rot" statt "blu"', 'context': 'Die Ampel ist rot.', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [1]

    def test_no_match_returns_minus_one(self, monkeypatch):
        # Kein Bezug zu irgendeinem Segment -> konservativ -1 (keine Falschzuordnung)
        pairs = [('Die Tür ist rot.', 'La porta è rossa.'),
                 ('Das Auto ist rot.', "L'auto è blu.")]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'völlig anderer text zzz', 'context': 'unbekannt qqq', 'explanation': 'x'}])
        assert [i.segment_index for i in issues] == [-1]

    def test_no_match_keeps_context_as_fallback_text(self, monkeypatch):
        # Bei seg_index -1 muss context/error_text als Anzeige-Text erhalten bleiben
        pairs = [('Die Tür ist rot.', 'La porta è rossa.')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'xyzfehler', 'context': 'kontext abc', 'explanation': 'Erklärung'}])
        assert len(issues) == 1
        assert issues[0].segment_index == -1
        assert issues[0].source_text == 'kontext abc'
        assert issues[0].target_text == 'xyzfehler'

    def test_first_bracket_wins_on_multiple(self, monkeypatch):
        pairs = [('A eins', 'A uno'), ('B zwei', 'B due'), ('C drei', 'C tre')]
        issues = self._run(monkeypatch, pairs, [
            {'error_text': 'x', 'context': 'Segmente [2] und [3]', 'explanation': 'y'}])
        # Erste Klammer [2] -> Index 1
        assert [i.segment_index for i in issues] == [1]

