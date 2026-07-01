# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.ocr_paths (gebuendelte Tesseract-/Poppler-Pfade)."""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui_app import ocr_paths


def _make_bundle(root, langs=('deu', 'eng'), with_tessdata=True, with_poppler=True):
    """Baut die erwartete Buendel-Struktur in einem tmp-Verzeichnis nach."""
    tess = root / 'tesseract' / 'Tesseract-OCR'
    tess.mkdir(parents=True)
    (tess / 'tesseract.exe').write_bytes(b'fake-exe')
    if with_tessdata:
        (tess / 'tessdata').mkdir()
        for lang in langs:
            (tess / 'tessdata' / f'{lang}.traineddata').write_bytes(b'fake-lang')
    if with_poppler:
        pop = root / 'poppler' / 'bin'
        pop.mkdir(parents=True)
        (pop / 'pdftoppm.exe').write_bytes(b'fake-exe')
        (pop / 'pdfinfo.exe').write_bytes(b'fake-exe')
    return root


class TestBundledPaths:
    def test_tesseract_exe_found(self, tmp_path):
        _make_bundle(tmp_path)
        exe = ocr_paths.bundled_tesseract_exe(tmp_path)
        assert exe is not None
        assert exe.endswith('tesseract.exe')
        assert os.path.isfile(exe)

    def test_tesseract_exe_missing(self, tmp_path):
        assert ocr_paths.bundled_tesseract_exe(tmp_path) is None

    def test_tessdata_dir_found(self, tmp_path):
        _make_bundle(tmp_path)
        d = ocr_paths.bundled_tessdata_dir(tmp_path)
        assert d is not None
        assert os.path.isdir(d)

    def test_tessdata_dir_missing(self, tmp_path):
        _make_bundle(tmp_path, with_tessdata=False)
        assert ocr_paths.bundled_tessdata_dir(tmp_path) is None

    def test_poppler_bin_found(self, tmp_path):
        _make_bundle(tmp_path)
        d = ocr_paths.bundled_poppler_bin(tmp_path)
        assert d is not None
        assert os.path.isfile(os.path.join(d, 'pdftoppm.exe'))

    def test_poppler_bin_missing(self, tmp_path):
        assert ocr_paths.bundled_poppler_bin(tmp_path) is None

    def test_poppler_bin_dir_without_exe(self, tmp_path):
        # bin-Verzeichnis existiert, aber ohne Binaries -> PATH-Fallback
        (tmp_path / 'poppler' / 'bin').mkdir(parents=True)
        assert ocr_paths.bundled_poppler_bin(tmp_path) is None

    def test_poppler_bin_without_pdfinfo(self, tmp_path):
        # pdf2image ruft zuerst pdfinfo auf — ohne pdfinfo.exe ist das
        # Buendel unbrauchbar und PATH-Fallback die bessere Wahl
        pop = tmp_path / 'poppler' / 'bin'
        pop.mkdir(parents=True)
        (pop / 'pdftoppm.exe').write_bytes(b'fake-exe')
        assert ocr_paths.bundled_poppler_bin(tmp_path) is None

    def test_repo_bundle_is_complete(self):
        # Das echte Buendel im Repo: alle drei Pfade muessen aufloesen,
        # inkl. deutscher Sprachdaten (deu.traineddata)
        exe = ocr_paths.bundled_tesseract_exe()
        tessdata = ocr_paths.bundled_tessdata_dir()
        poppler = ocr_paths.bundled_poppler_bin()
        assert exe and os.path.isfile(exe)
        assert tessdata and os.path.isfile(os.path.join(tessdata, 'deu.traineddata'))
        assert poppler and os.path.isfile(os.path.join(poppler, 'pdftoppm.exe'))


class TestConfigurePytesseract:
    def test_configures_cmd_and_tessdata(self, tmp_path, monkeypatch):
        _make_bundle(tmp_path)
        # setenv (statt delenv) garantiert Restore beim Teardown, auch wenn
        # die Variable vor dem Test gar nicht gesetzt war
        monkeypatch.setenv('TESSDATA_PREFIX', 'wert-vor-dem-test')
        fake = SimpleNamespace(pytesseract=SimpleNamespace(tesseract_cmd='tesseract'))
        assert ocr_paths.configure_pytesseract(fake, tmp_path) is True
        assert fake.pytesseract.tesseract_cmd.endswith('tesseract.exe')
        assert os.environ['TESSDATA_PREFIX'].endswith('tessdata')

    def test_overrides_system_tessdata_prefix(self, tmp_path, monkeypatch):
        _make_bundle(tmp_path)
        monkeypatch.setenv('TESSDATA_PREFIX', r'C:\Program Files\Tesseract-OCR\tessdata')
        fake = SimpleNamespace(pytesseract=SimpleNamespace(tesseract_cmd='tesseract'))
        assert ocr_paths.configure_pytesseract(fake, tmp_path) is True
        assert 'Program Files' not in os.environ['TESSDATA_PREFIX']

    def test_no_bundle_leaves_module_untouched(self, tmp_path, monkeypatch):
        monkeypatch.setenv('TESSDATA_PREFIX', 'unangetastet')
        fake = SimpleNamespace(pytesseract=SimpleNamespace(tesseract_cmd='tesseract'))
        assert ocr_paths.configure_pytesseract(fake, tmp_path) is False
        assert fake.pytesseract.tesseract_cmd == 'tesseract'
        assert os.environ['TESSDATA_PREFIX'] == 'unangetastet'

    def test_none_module_is_noop(self, tmp_path):
        _make_bundle(tmp_path)
        assert ocr_paths.configure_pytesseract(None, tmp_path) is False

    def test_bundle_without_tessdata_is_not_used(self, tmp_path, monkeypatch):
        # exe ohne Sprachdaten = unbrauchbares Teil-Buendel; darf ein
        # funktionierendes System-Tesseract im PATH nicht aushebeln
        _make_bundle(tmp_path, with_tessdata=False)
        monkeypatch.setenv('TESSDATA_PREFIX', 'unangetastet')
        fake = SimpleNamespace(pytesseract=SimpleNamespace(tesseract_cmd='tesseract'))
        assert ocr_paths.configure_pytesseract(fake, tmp_path) is False
        assert fake.pytesseract.tesseract_cmd == 'tesseract'
        assert os.environ['TESSDATA_PREFIX'] == 'unangetastet'

    def test_bundle_with_missing_language_is_not_used(self, tmp_path, monkeypatch):
        # tessdata existiert, aber deu.traineddata fehlt -> PATH-Fallback
        _make_bundle(tmp_path, langs=('eng',))
        monkeypatch.setenv('TESSDATA_PREFIX', 'unangetastet')
        fake = SimpleNamespace(pytesseract=SimpleNamespace(tesseract_cmd='tesseract'))
        assert ocr_paths.configure_pytesseract(fake, tmp_path) is False
        assert fake.pytesseract.tesseract_cmd == 'tesseract'
        assert os.environ['TESSDATA_PREFIX'] == 'unangetastet'
