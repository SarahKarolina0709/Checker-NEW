# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.lang_detect (Auto-Erkennung der Sprachen)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nicegui_app import lang_detect as ld


DE_TEXT = (
    'Das Schlafzimmer befindet sich im ersten Obergeschoss und verfuegt '
    'ueber ein grosses Fenster mit Blick auf den Garten.'
)
EN_TEXT = (
    'The bedroom is located on the first floor and has a large window '
    'overlooking the garden behind the house.'
)
FR_TEXT = (
    'La chambre se trouve au premier etage et dispose d une grande '
    'fenetre donnant sur le jardin derriere la maison.'
)


def test_is_auto():
    assert ld.is_auto('auto') is True
    assert ld.is_auto('Auto') is True
    assert ld.is_auto('') is True
    assert ld.is_auto(None) is True  # type: ignore[arg-type]
    assert ld.is_auto('de') is False
    assert ld.is_auto('en') is False


def test_detect_lang_code_german():
    if not ld._HAS_LANGDETECT:
        return
    assert ld.detect_lang_code(DE_TEXT) == 'de'


def test_detect_lang_code_english():
    if not ld._HAS_LANGDETECT:
        return
    assert ld.detect_lang_code(EN_TEXT) == 'en'


def test_detect_lang_code_too_short_returns_empty():
    assert ld.detect_lang_code('Hi') == ''
    assert ld.detect_lang_code('') == ''


def test_detect_from_texts_majority():
    if not ld._HAS_LANGDETECT:
        return
    assert ld.detect_from_texts([DE_TEXT, DE_TEXT, EN_TEXT]) == 'de'
    assert ld.detect_from_texts([EN_TEXT, FR_TEXT, EN_TEXT]) == 'en'


def test_resolve_lang_keeps_concrete_code():
    # Konkreter Code wird NIE ueberschrieben, auch nicht durch Texte anderer Sprache
    assert ld.resolve_lang('de', [EN_TEXT], 'xx') == 'de'
    assert ld.resolve_lang('en', [DE_TEXT], 'xx') == 'en'


def test_resolve_lang_auto_detects():
    if not ld._HAS_LANGDETECT:
        return
    assert ld.resolve_lang('auto', [DE_TEXT, DE_TEXT], 'en') == 'de'
    assert ld.resolve_lang('', [EN_TEXT, EN_TEXT], 'de') == 'en'


def test_resolve_lang_auto_falls_back_when_undetectable():
    # Zu kurze/leere Texte -> Fallback greift
    assert ld.resolve_lang('auto', ['', 'Hi'], 'de') == 'de'
    assert ld.resolve_lang('auto', [], 'en') == 'en'
