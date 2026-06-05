# -*- coding: utf-8 -*-
"""Tests fuer die deutschen Kategorie-Labels der Top-Kategorien-Heatmap."""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_MAIN = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nicegui_app', 'main.py'))
_spec = importlib.util.spec_from_file_location('checker_main_cat', _MAIN)
main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(main)

category_label_de = main.category_label_de


def test_known_categories_are_german():
    assert category_label_de('whitespace') == 'Leerzeichen'
    assert category_label_de('completeness') == 'Vollständigkeit'
    assert category_label_de('consistency') == 'Konsistenz'
    assert category_label_de('terminology') == 'Terminologie'
    assert category_label_de('grammar') == 'Grammatik'
    assert category_label_de('ki_semantic') == 'KI-Analyse'


def test_case_insensitive_lookup():
    assert category_label_de('WHITESPACE') == 'Leerzeichen'
    assert category_label_de('Consistency') == 'Konsistenz'


def test_empty_defaults_to_sonstige():
    assert category_label_de('') == 'Sonstige'
    assert category_label_de(None) == 'Sonstige'  # type: ignore[arg-type]


def test_unknown_category_humanized():
    assert category_label_de('foo_bar') == 'Foo bar'
    assert category_label_de('some_new_check') == 'Some new check'


def test_all_checker_categories_have_label():
    # Alle real von den Checkern erzeugten Kategorien muessen ein deutsches
    # Label haben (kein Roh-Code in der UI).
    real_categories = {
        'completeness', 'consistency', 'formatting', 'html', 'metadata',
        'punctuation', 'quotes', 'readability', 'references', 'risk',
        'security', 'semantic', 'structure', 'style', 'terminology',
        'typography', 'whitespace', 'grammar', 'numbers', 'ocr', 'ki_semantic',
    }
    for cat in real_categories:
        label = category_label_de(cat)
        assert label and label != cat, f'{cat} hat kein deutsches Label'
        assert label in main.CATEGORY_LABELS_DE.values()
