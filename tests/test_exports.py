# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.exports."""
import os
import sys
import tempfile
import shutil
import zipfile
from dataclasses import dataclass

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nicegui_app import exports as E


@dataclass
class _F:
    severity: str = 'major'
    code: str = 'X1'
    message: str = 'msg'
    source_text: str = ''
    target_text: str = ''
    category: str = ''


def _findings():
    return [
        _F('critical', 'C1', 'Kritischer Fehler', 'src1', 'tgt1', 'numbers'),
        _F('major', 'M1', 'Wichtig <html> & co', 'src2', 'tgt2', 'terminology'),
        _F('minor', 'm1', 'Klein', '', '', 'style'),
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class TestHelpers:
    def test_xml_clean_strips_control_chars(self):
        assert E._xml_clean('a\x00b\x07c') == 'abc'

    def test_xml_clean_keeps_tabs_newlines(self):
        assert E._xml_clean('a\tb\nc\rd') == 'a\tb\nc\rd'

    def test_xml_clean_passthrough_non_str(self):
        assert E._xml_clean(42) == 42
        assert E._xml_clean(None) is None

    def test_xml_escape(self):
        assert E._xml_escape('<a & b>') == '&lt;a &amp; b&gt;'

    def test_xml_escape_empty(self):
        assert E._xml_escape('') == ''
        assert E._xml_escape(None) == ''


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------
class TestTxt:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic(self):
        path = E.export_txt(_findings(), 75, self.tmp)
        assert os.path.isfile(path)
        content = open(path, encoding='utf-8').read()
        assert 'Score: 75/100' in content
        assert 'Kritischer Fehler' in content
        assert 'src1' in content
        assert 'tgt1' in content

    def test_creates_output_dir(self):
        new_dir = os.path.join(self.tmp, 'new', 'sub')
        path = E.export_txt(_findings(), 50, new_dir)
        assert os.path.isfile(path)

    def test_empty_findings(self):
        path = E.export_txt([], 100, self.tmp)
        assert os.path.isfile(path)
        assert 'Findings: 0' in open(path, encoding='utf-8').read()


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------
class TestExcel:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic(self):
        try:
            import openpyxl  # noqa
        except ImportError:
            pytest.skip('openpyxl missing')
        path = E.export_excel(_findings(), self.tmp)
        assert os.path.isfile(path)
        wb = openpyxl.load_workbook(path)
        ws = wb.active
        # Header + 3 Datenzeilen
        rows = list(ws.iter_rows(values_only=True))
        assert len(rows) == 4
        assert rows[0][0] == 'Nr'
        assert rows[1][2] == 'C1'

    def test_strips_illegal_xml_chars(self):
        try:
            import openpyxl  # noqa
        except ImportError:
            pytest.skip('openpyxl missing')
        bad = [_F('major', 'X', 'hi\x00there', 'a\x07b', '', '')]
        path = E.export_excel(bad, self.tmp)
        wb = openpyxl.load_workbook(path)
        rows = list(wb.active.iter_rows(values_only=True))
        assert rows[1][4] == 'hithere'  # message
        assert rows[1][5] == -1         # segment_index (default)
        assert rows[1][6] == 'ab'       # source


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
class TestPdf:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic(self):
        try:
            import reportlab  # noqa
        except ImportError:
            pytest.skip('reportlab missing')
        path = E.export_pdf(_findings(), 80, self.tmp)
        assert os.path.isfile(path)
        # PDF Header-Magic
        with open(path, 'rb') as f:
            assert f.read(4) == b'%PDF'

    def test_special_chars_no_crash(self):
        # Bug-Regression: <, &, > in messages duerfen ReportLab nicht crashen
        try:
            import reportlab  # noqa
        except ImportError:
            pytest.skip('reportlab missing')
        path = E.export_pdf([_F('major', 'X<>&', 'a < b & c > d')], 50, self.tmp)
        assert os.path.isfile(path)


# ---------------------------------------------------------------------------
# Korrekturpaket
# ---------------------------------------------------------------------------
class TestZipPackage:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        # Ein paar Demo-Files
        self.src1 = os.path.join(self.tmp, 'src', 'a.txt')
        self.tgt1 = os.path.join(self.tmp, 'tgt', 'a.txt')
        os.makedirs(os.path.dirname(self.src1))
        os.makedirs(os.path.dirname(self.tgt1))
        open(self.src1, 'w', encoding='utf-8').write('S')
        open(self.tgt1, 'w', encoding='utf-8').write('T')

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_zip(self):
        out = E.export_correction_package(
            _findings(), 70, [self.src1], [self.tgt1], self.tmp,
        )
        assert out and os.path.isfile(out)
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert any(n.startswith('01_Ausgangstexte/') for n in names)
            assert any(n.startswith('02_Uebersetzungen/') for n in names)
            assert 'corrections.txt' in names
            assert any(n.startswith('bericht/') for n in names)

    def test_filename_collision_dedup(self):
        # Zweite source-Datei mit gleichem Basename in anderem Ordner
        other = os.path.join(self.tmp, 'src2', 'a.txt')
        os.makedirs(os.path.dirname(other))
        open(other, 'w', encoding='utf-8').write('S2')
        out = E.export_correction_package(
            _findings(), 70, [self.src1, other], [], self.tmp,
        )
        with zipfile.ZipFile(out) as zf:
            ausgangs = [n for n in zf.namelist() if n.startswith('01_Ausgangstexte/')]
            assert len(ausgangs) == 2
            # Zweiter darf NICHT gleichen Pfad haben
            assert len(set(ausgangs)) == 2

    def test_skips_missing_files(self):
        out = E.export_correction_package(
            _findings(), 70, [self.src1, '/nonexistent/x.txt'], [], self.tmp,
        )
        with zipfile.ZipFile(out) as zf:
            ausgangs = [n for n in zf.namelist() if n.startswith('01_Ausgangstexte/')]
            assert len(ausgangs) == 1

    def test_empty_files_lists(self):
        out = E.export_correction_package(_findings(), 50, [], [], self.tmp)
        assert out and os.path.isfile(out)
        with zipfile.ZipFile(out) as zf:
            assert 'corrections.txt' in zf.namelist()
