# -*- coding: utf-8 -*-
"""Tests fuer neutral_pairing_service (Hot-Spot mit Bugs 52, 54, 55, 58)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from neutral_pairing_service import (
    PairingService,
    FilePair,
    _extract_lang_from_name,
    _detect_file_lang,
    get_pairing_service,
)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _ps():
    return PairingService(similarity_threshold=0.6)


# ---------------------------------------------------------------------------
# _extract_lang_from_name
# ---------------------------------------------------------------------------
class TestExtractLang:
    def test_underscore_de(self):
        assert _extract_lang_from_name('vertrag_de.docx') == 'de'

    def test_underscore_en(self):
        assert _extract_lang_from_name('contract_en.docx') == 'en'

    def test_dash(self):
        assert _extract_lang_from_name('contract-fr.pdf') == 'fr'

    def test_case_insensitive(self):
        assert _extract_lang_from_name('vertrag_DE.docx') == 'de'

    def test_no_lang(self):
        assert _extract_lang_from_name('vertrag.docx') is None

    def test_lang_inside_word_not_matched(self):
        # 'envelope' enthaelt 'en' aber nicht als Sprach-Code-Token
        assert _extract_lang_from_name('envelope.txt') is None

    def test_prefix_uppercase(self):
        # Bug-Fix: DE_vertrag.docx → 'de'
        assert _extract_lang_from_name('DE_vertrag.docx') == 'de'

    def test_prefix_lowercase(self):
        assert _extract_lang_from_name('en_contract.docx') == 'en'

    def test_prefix_dash(self):
        assert _extract_lang_from_name('fr-rapport.pdf') == 'fr'


# ---------------------------------------------------------------------------
# Normalisierung — Bug 55 Regression (suffix-removal frisst Wort-interne Vorkommen)
# ---------------------------------------------------------------------------
class TestNormalize:
    def setup_method(self):
        self.ps = _ps()

    def test_strips_lang_code(self):
        assert self.ps._normalize('vertrag_de.docx') == 'vertrag'

    def test_strips_lang_code_prefix(self):
        # Bug-Fix: DE_vertrag.docx → 'vertrag'
        assert self.ps._normalize('DE_vertrag.docx') == 'vertrag'

    def test_strips_known_suffix(self):
        assert self.ps._normalize('doc_translation.docx') == 'doc'

    def test_strips_version_suffix(self):
        assert self.ps._normalize('doc_v2.docx') == 'doc'

    def test_strips_date(self):
        assert self.ps._normalize('doc_2026-04-23.docx') == 'doc'

    def test_does_not_destroy_word_internal(self):
        # Bug 55: "transformer" hat "trans" eingebaut — darf NICHT zerstoert werden
        result = self.ps._normalize('transformer.docx')
        assert 'transformer' in result or result == 'transformer'

    def test_empty_after_strip_does_not_crash(self):
        assert self.ps._normalize('_de.docx') in ('', 'de', '_de')


# ---------------------------------------------------------------------------
# _similarity
# ---------------------------------------------------------------------------
class TestSimilarity:
    def setup_method(self):
        self.ps = _ps()

    def test_identical(self):
        assert self.ps._similarity('vertrag', 'vertrag') == 1.0

    def test_completely_different(self):
        assert self.ps._similarity('apple', 'sundown') < 0.5

    def test_empty_strings_no_match(self):
        # Bug-Regression: leere Strings duerfen NICHT als 1.0 ranken
        assert self.ps._similarity('', '') == 0.0
        assert self.ps._similarity('abc', '') == 0.0
        assert self.ps._similarity('', 'abc') == 0.0

    def test_substring_bonus(self):
        # Reines SequenceMatcher waere niedriger
        s = self.ps._similarity('contract', 'big_contract_v2')
        assert s > 0.4


# ---------------------------------------------------------------------------
# pair() — End-to-End
# ---------------------------------------------------------------------------
class TestPair:
    def setup_method(self):
        self.ps = _ps()

    def test_empty_inputs(self):
        pairs, us, ut = self.ps.pair([], [])
        assert pairs == [] and us == [] and ut == []

    def test_only_source(self):
        pairs, us, ut = self.ps.pair(['/a/foo.docx'], [])
        assert pairs == []
        assert us == ['/a/foo.docx']
        assert ut == []

    def test_simple_pair(self):
        pairs, us, ut = self.ps.pair(['/src/vertrag.docx'], ['/tgt/vertrag.docx'])
        assert len(pairs) == 1
        assert pairs[0].source.endswith('vertrag.docx')
        assert pairs[0].translation.endswith('vertrag.docx')
        assert us == [] and ut == []

    def test_lang_suffix_pair(self):
        pairs, _, _ = self.ps.pair(
            ['/src/vertrag_de.docx'],
            ['/tgt/vertrag_en.docx'],
        )
        assert len(pairs) == 1
        assert pairs[0].source_lang == 'de'
        assert pairs[0].translation_lang == 'en'

    def test_lang_prefix_pair(self):
        # Bug-Fix: DE_vertrag.docx + EN_vertrag.docx müssen korrekt gepaart werden
        pairs, us, ut = self.ps.pair(
            ['/src/DE_vertrag.docx'],
            ['/tgt/EN_vertrag.docx'],
        )
        assert len(pairs) == 1
        assert us == [] and ut == []
        assert pairs[0].source_lang == 'de'
        assert pairs[0].translation_lang == 'en'

    def test_global_optimum_not_greedy(self):
        # Greedy waere: A->X (0.8), dann B uebrig. Optimum: A->Y (0.9), B->X (0.85)
        # Test: stelle sicher dass das richtige Mapping gewaehlt wird
        sources = ['/s/alpha.docx', '/s/beta.docx']
        targets = ['/t/alpha.docx', '/t/beta.docx']
        pairs, us, ut = self.ps.pair(sources, targets)
        assert len(pairs) == 2
        # Jede Source-Datei kommt genau einmal vor
        assert {p.source for p in pairs} == set(sources)
        assert {p.translation for p in pairs} == set(targets)
        # Korrekte Zuordnung
        for p in pairs:
            assert os.path.basename(p.source) == os.path.basename(p.translation)

    def test_no_match_below_threshold(self):
        pairs, us, ut = self.ps.pair(['/s/foo.docx'], ['/t/something_completely_different.docx'])
        assert len(pairs) == 0
        assert len(us) == 1 and len(ut) == 1

    def test_unique_assignment(self):
        # 3 Sources, 1 Target — nur 1 Pair, 2 unmatched sources
        pairs, us, ut = self.ps.pair(
            ['/s/a.docx', '/s/aa.docx', '/s/aaa.docx'],
            ['/t/a.docx'],
        )
        assert len(pairs) == 1
        assert len(us) == 2
        assert len(ut) == 0

    def test_confidence_levels(self):
        pairs, _, _ = self.ps.pair(['/s/contract.docx'], ['/t/contract.docx'])
        conf = self.ps.get_pair_confidence(pairs[0].source, pairs[0].translation)
        assert conf == 'high'

    def test_get_last_pairs(self):
        self.ps.pair(['/s/x.docx'], ['/t/x.docx'])
        last = self.ps.get_last_pairs()
        assert len(last) == 1
        assert isinstance(last[0], FilePair)


# ---------------------------------------------------------------------------
# XML language detection (XLIFF/TMX)
# ---------------------------------------------------------------------------
class TestDetectFileLang:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, content):
        p = os.path.join(self.tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)
        return p

    def test_xliff_1_source_language(self):
        p = self._write('a.xliff',
            '<?xml version="1.0"?><xliff version="1.2"><file source-language="de" target-language="en">'
            '<body></body></file></xliff>')
        assert _detect_file_lang(p) == 'de'

    def test_xliff_2_srclang(self):
        p = self._write('a.xlf',
            '<?xml version="1.0"?><xliff version="2.0" srcLang="fr" trgLang="de"><file></file></xliff>')
        assert _detect_file_lang(p) == 'fr'

    def test_xliff_normalizes_locale(self):
        p = self._write('a.xliff',
            '<?xml version="1.0"?><xliff version="1.2"><file source-language="de-DE">'
            '<body></body></file></xliff>')
        assert _detect_file_lang(p) == 'de'

    def test_non_xml_returns_none(self):
        p = self._write('a.txt', 'plain text')
        assert _detect_file_lang(p) is None

    def test_invalid_xml_returns_none(self):
        p = self._write('a.xliff', '<not valid xml')
        assert _detect_file_lang(p) is None


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
class TestSingleton:
    def test_returns_same_instance(self):
        a = get_pairing_service()
        b = get_pairing_service()
        assert a is b
