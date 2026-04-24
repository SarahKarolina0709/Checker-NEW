# -*- coding: utf-8 -*-
"""Tests fuer den Glossary-Loader (_load_glossary in quality_gui_phase2_checkers)."""
import json
import os
import sys
import tempfile
import shutil

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quality_gui_phase2_checkers import _load_glossary


class TestJsonLoader:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, data, *, raw=False):
        p = os.path.join(self.tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(data if raw else json.dumps(data, ensure_ascii=False))
        return p

    def test_simple_dict(self):
        p = self._write('g.json', {'Vertrag': 'contract'})
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']

    def test_list_translations(self):
        p = self._write('g.json', {'Vertrag': ['contract', 'agreement']})
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract', 'agreement']

    def test_short_key_skipped(self):
        p = self._write('g.json', {'a': 'b', 'Vertrag': 'contract'})
        g = _load_glossary(p)
        assert 'a' not in g
        assert 'vertrag' in g

    def test_invalid_value_skipped_not_whole(self):
        # Eintrag mit None ueberspringen, aber nicht das ganze Glossar
        p = self._write('g.json', {'Vertrag': 'contract', 'Other': None})
        g = _load_glossary(p)
        assert 'vertrag' in g
        assert 'other' not in g

    def test_empty_value_uses_key(self):
        p = self._write('g.json', {'Vertrag': ''})
        g = _load_glossary(p)
        assert g['vertrag'] == ['Vertrag']

    def test_corrupt_json_returns_empty(self):
        p = self._write('g.json', '{not valid', raw=True)
        assert _load_glossary(p) == {}

    def test_non_dict_root_returns_empty(self):
        p = self._write('g.json', '["a","b"]', raw=True)
        assert _load_glossary(p) == {}

    def test_unicode(self):
        p = self._write('g.json', {'Geschäftsführer': 'CEO'})
        g = _load_glossary(p)
        assert g.get('geschäftsführer') == ['CEO']


class TestCsvLoader:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, content, encoding='utf-8'):
        p = os.path.join(self.tmp, name)
        with open(p, 'w', encoding=encoding, newline='') as f:
            f.write(content)
        return p

    def test_comma_separated(self):
        p = self._write('g.csv', 'Vertrag,contract\nFirma,company')
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']
        assert g.get('firma') == ['company']

    def test_semicolon_separated(self):
        p = self._write('g.csv', 'Vertrag;contract\nFirma;company')
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']

    def test_tab_separated(self):
        p = self._write('g.tsv', 'Vertrag\tcontract\nFirma\tcompany')
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']

    def test_utf8_bom_stripped(self):
        # Excel CSV-Export: utf-8-sig
        p = self._write('g.csv', 'Vertrag,contract', encoding='utf-8-sig')
        g = _load_glossary(p)
        assert 'vertrag' in g

    def test_header_skipped(self):
        p = self._write('g.csv', 'Quelle,Ziel\nVertrag,contract')
        g = _load_glossary(p)
        assert 'quelle' not in g
        assert g.get('vertrag') == ['contract']

    def test_multi_translations(self):
        p = self._write('g.csv', 'Vertrag,contract,agreement,deal')
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract', 'agreement', 'deal']

    def test_empty_translation_uses_term(self):
        p = self._write('g.csv', 'Vertrag,')
        g = _load_glossary(p)
        assert g.get('vertrag') == ['Vertrag']

    def test_short_term_skipped(self):
        p = self._write('g.csv', 'a,b\nVertrag,contract')
        g = _load_glossary(p)
        assert 'a' not in g
        assert 'vertrag' in g

    def test_empty_lines_skipped(self):
        p = self._write('g.csv', 'Vertrag,contract\n\nFirma,company\n\n')
        g = _load_glossary(p)
        assert len(g) == 2


class TestXlsxLoader:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic_xlsx(self):
        try:
            import openpyxl
        except ImportError:
            pytest.skip('openpyxl missing')
        p = os.path.join(self.tmp, 'g.xlsx')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Quelle', 'Ziel'])
        ws.append(['Vertrag', 'contract'])
        ws.append(['Firma', 'company'])
        wb.save(p)
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']
        assert g.get('firma') == ['company']

    def test_xlsx_empty_cells(self):
        try:
            import openpyxl
        except ImportError:
            pytest.skip('openpyxl missing')
        p = os.path.join(self.tmp, 'g.xlsx')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Vertrag', 'contract', None, ''])
        wb.save(p)
        g = _load_glossary(p)
        assert g.get('vertrag') == ['contract']


class TestEdgeCases:
    def test_no_path(self):
        assert _load_glossary('') == {}

    def test_missing_file(self):
        assert _load_glossary('/nonexistent/glossary.json') == {}

    def test_unknown_extension_treated_as_csv(self):
        # Fallback: alles ohne json/xlsx-Extension wird als CSV gelesen
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write('Vertrag,contract')
            p = f.name
        try:
            g = _load_glossary(p)
            assert 'vertrag' in g
        finally:
            os.unlink(p)
