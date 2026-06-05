# -*- coding: utf-8 -*-
"""Quelltext-Pruefung: liest von Microsoft Word markierte Rechtschreib- und
Grammatikfehler aus DOCX-Dateien aus.

Hintergrund
-----------
Word markiert Woerter, die seine eigene Rechtschreib-/Grammatikpruefung
beanstandet, im Dokument-XML mit Markern::

    <w:proofErr w:type="spellStart"/> ... <w:proofErr w:type="spellEnd"/>
    <w:proofErr w:type="gramStart"/> ... <w:proofErr w:type="gramEnd"/>

Diese Information geht beim reinen Text-Extrahieren verloren. Hier lesen wir
sie aus und melden sie als Hinweis-Befund, damit Tippfehler im
Ausgangsdokument (z.B. ein versehentlich geloeschter Anfangsbuchstabe wie
"eutscher" statt "Deutscher") nicht unbemerkt bleiben.

Die Befunde sind reine Hinweise (``meta['hint_only'] = True``) und zaehlen
NICHT zum Score — es sind Probleme im Ausgangstext, nicht in der Uebersetzung.

Reine Funktionen. Optionale Dependency python-docx wird nicht benoetigt
(wir lesen das DOCX-ZIP direkt); fehlt das QAIssue-Modul, liefern die
Builder eine leere Liste statt zu crashen.
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree as ET

try:
    from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:  # pragma: no cover - QAIssue sollte immer verfuegbar sein
    QAIssue = None  # type: ignore

# WordprocessingML-Namespace
_W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def _q(tag: str) -> str:
    return f'{{{_W_NS}}}{tag}'


def _scan_proof_regions(root: ET.Element) -> List[Dict[str, str]]:
    """Durchlaeuft die XML-Elemente in Dokument-Reihenfolge und sammelt den
    Text zwischen ``proofErr``-Start/Ende-Markern.

    Returns Liste von ``{'word': str, 'kind': 'spelling'|'grammar'}`` in
    Dokument-Reihenfolge (noch nicht dedupliziert).
    """
    proof_err = _q('proofErr')
    w_t = _q('t')
    type_attr = _q('type')

    spell_buf: List[str] = []
    gram_buf: List[str] = []
    in_spell = False
    in_gram = False
    found: List[Dict[str, str]] = []

    for el in root.iter():
        tag = el.tag
        if tag == proof_err:
            t = el.get(type_attr, '')
            if t == 'spellStart':
                in_spell = True
                spell_buf = []
            elif t == 'spellEnd':
                word = ''.join(spell_buf).strip()
                if word:
                    found.append({'word': word, 'kind': 'spelling'})
                in_spell = False
                spell_buf = []
            elif t == 'gramStart':
                in_gram = True
                gram_buf = []
            elif t == 'gramEnd':
                word = ''.join(gram_buf).strip()
                if word:
                    found.append({'word': word, 'kind': 'grammar'})
                in_gram = False
                gram_buf = []
        elif tag == w_t:
            # w:t kann zwischen Start- und Ende-Marker liegen (DFS = Dokument-
            # Reihenfolge), ein Wort kann ueber mehrere Runs verteilt sein.
            if in_spell:
                spell_buf.append(el.text or '')
            if in_gram:
                gram_buf.append(el.text or '')
    return found


def extract_word_proof_errors(docx_path: str, max_items: int = 50) -> List[Dict[str, str]]:
    """Liest von Word markierte Rechtschreib-/Grammatikbereiche aus einer DOCX.

    Beruecksichtigt Haupttext sowie Kopf-/Fusszeilen. Ergebnis ist
    dedupliziert (gleiches Wort + Art nur einmal) und auf ``max_items``
    begrenzt. Wirft nie eine Exception — bei Problemen leere Liste.
    """
    if not docx_path or not os.path.isfile(docx_path):
        return []
    if Path(docx_path).suffix.lower() != '.docx':
        return []

    regions: List[Dict[str, str]] = []
    try:
        with zipfile.ZipFile(docx_path) as zf:
            names = zf.namelist()
            parts = [
                n for n in names
                if n == 'word/document.xml'
                or (n.startswith('word/header') and n.endswith('.xml'))
                or (n.startswith('word/footer') and n.endswith('.xml'))
            ]
            # document.xml zuerst, damit Haupttext-Funde vorne stehen
            parts.sort(key=lambda n: (n != 'word/document.xml', n))
            for part in parts:
                try:
                    xml = zf.read(part)
                except (KeyError, zipfile.BadZipFile):
                    continue
                try:
                    root = ET.fromstring(xml)
                except ET.ParseError:
                    continue
                regions.extend(_scan_proof_regions(root))
    except (zipfile.BadZipFile, OSError):
        return []

    out: List[Dict[str, str]] = []
    seen = set()
    for item in regions:
        key = (item['kind'], item['word'].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= max_items:
            break
    return out


def build_proofing_findings(
    src_path: str,
    src_text: str = '',
    tgt_text: str = '',
    segment_index: int = -1,
    max_items: int = 50,
) -> List["QAIssue"]:
    """Baut Hinweis-Befunde fuer von Word markierte Quelltext-Fehler.

    Jeder Befund ist ``severity='info'``, ``category='source_quality'`` und
    ``meta['hint_only']=True`` (zaehlt nicht zum Score). Bei fehlendem
    QAIssue-Modul oder ohne Funde: leere Liste.
    """
    if QAIssue is None:
        return []
    errors = extract_word_proof_errors(src_path, max_items=max_items)
    if not errors:
        return []

    findings: List["QAIssue"] = []
    for err in errors:
        word = err.get('word', '')
        kind = err.get('kind', 'spelling')
        if not word:
            continue
        if kind == 'grammar':
            code = 'SOURCE_GRAMMAR'
            message = (
                f'Mögliches Grammatikproblem im Ausgangstext: »{word}« '
                f'(von Word als Fehler markiert)'
            )
        else:
            code = 'SOURCE_SPELL'
            message = (
                f'Mögliches Rechtschreibproblem im Ausgangstext: »{word}« '
                f'(von Word als Fehler markiert)'
            )
        findings.append(QAIssue(
            code=code,
            severity='info',
            category='source_quality',
            message=message,
            source_text=src_text,
            target_text=tgt_text,
            segment_index=segment_index,
            source_file=src_path,
            meta={'hint_only': True, 'proof_word': word, 'proof_kind': kind},
        ))
    return findings
