# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.source_proofing (Word-Rechtschreibmarker aus DOCX)."""
import os
import sys
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nicegui_app import source_proofing as sp

_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def _make_docx(tmp_path, body_inner: str, name: str = 'test.docx') -> str:
    """Erzeugt eine minimale .docx mit dem gegebenen w:body-Inhalt."""
    document = (
        f'<w:document xmlns:w="{_W}"><w:body>{body_inner}</w:body></w:document>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.document.main+xml"/></Types>'
    )
    path = os.path.join(str(tmp_path), name)
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('word/document.xml', document)
    return path


def _para_with_spell(word: str) -> str:
    return (
        '<w:p>'
        '<w:proofErr w:type="spellStart"/>'
        f'<w:r><w:t>{word}</w:t></w:r>'
        '<w:proofErr w:type="spellEnd"/>'
        '<w:r><w:t> Text danach</w:t></w:r>'
        '</w:p>'
    )


def test_extract_single_spelling_error(tmp_path):
    path = _make_docx(tmp_path, _para_with_spell('eutscher'))
    errs = sp.extract_word_proof_errors(path)
    assert errs == [{'word': 'eutscher', 'kind': 'spelling'}]


def test_extract_grammar_region(tmp_path):
    body = (
        '<w:p>'
        '<w:proofErr w:type="gramStart"/>'
        '<w:r><w:t>die Haus</w:t></w:r>'
        '<w:proofErr w:type="gramEnd"/>'
        '</w:p>'
    )
    path = _make_docx(tmp_path, body)
    errs = sp.extract_word_proof_errors(path)
    assert errs == [{'word': 'die Haus', 'kind': 'grammar'}]


def test_word_split_across_runs(tmp_path):
    body = (
        '<w:p>'
        '<w:proofErr w:type="spellStart"/>'
        '<w:r><w:t>eut</w:t></w:r>'
        '<w:r><w:t>scher</w:t></w:r>'
        '<w:proofErr w:type="spellEnd"/>'
        '</w:p>'
    )
    path = _make_docx(tmp_path, body)
    errs = sp.extract_word_proof_errors(path)
    assert errs == [{'word': 'eutscher', 'kind': 'spelling'}]


def test_deduplicates_repeated_words(tmp_path):
    body = _para_with_spell('eutscher') + _para_with_spell('eutscher')
    path = _make_docx(tmp_path, body)
    errs = sp.extract_word_proof_errors(path)
    assert errs == [{'word': 'eutscher', 'kind': 'spelling'}]


def test_no_errors_returns_empty(tmp_path):
    body = '<w:p><w:r><w:t>Alles korrekt geschrieben</w:t></w:r></w:p>'
    path = _make_docx(tmp_path, body)
    assert sp.extract_word_proof_errors(path) == []


def test_non_docx_returns_empty(tmp_path):
    txt = os.path.join(str(tmp_path), 'foo.txt')
    with open(txt, 'w', encoding='utf-8') as fh:
        fh.write('hello')
    assert sp.extract_word_proof_errors(txt) == []


def test_missing_file_returns_empty():
    assert sp.extract_word_proof_errors('does_not_exist.docx') == []


def test_corrupt_docx_returns_empty(tmp_path):
    bad = os.path.join(str(tmp_path), 'bad.docx')
    with open(bad, 'wb') as fh:
        fh.write(b'not a zip file')
    assert sp.extract_word_proof_errors(bad) == []


def test_max_items_limit(tmp_path):
    body = ''.join(_para_with_spell(f'wort{i}') for i in range(10))
    path = _make_docx(tmp_path, body)
    errs = sp.extract_word_proof_errors(path, max_items=3)
    assert len(errs) == 3


def test_build_findings_spelling(tmp_path):
    path = _make_docx(tmp_path, _para_with_spell('eutscher'))
    findings = sp.build_proofing_findings(path, src_text='eutscher Text', tgt_text='english')
    assert len(findings) == 1
    f = findings[0]
    assert f.code == 'SOURCE_SPELL'
    assert f.severity == 'info'
    assert f.category == 'source_quality'
    assert 'eutscher' in f.message
    assert f.meta.get('hint_only') is True
    assert f.meta.get('proof_word') == 'eutscher'
    assert f.source_file == path
    assert f.segment_index == -1


def test_build_findings_grammar_code(tmp_path):
    body = (
        '<w:p><w:proofErr w:type="gramStart"/>'
        '<w:r><w:t>die Haus</w:t></w:r>'
        '<w:proofErr w:type="gramEnd"/></w:p>'
    )
    path = _make_docx(tmp_path, body)
    findings = sp.build_proofing_findings(path, segment_index=2)
    assert len(findings) == 1
    assert findings[0].code == 'SOURCE_GRAMMAR'
    assert findings[0].segment_index == 2


def test_build_findings_no_errors(tmp_path):
    body = '<w:p><w:r><w:t>Alles korrekt</w:t></w:r></w:p>'
    path = _make_docx(tmp_path, body)
    assert sp.build_proofing_findings(path) == []
