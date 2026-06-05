# -*- coding: utf-8 -*-
"""Severity-Konstanten und Hilfsfunktionen.

Konsolidiert die zuvor verstreute Severity-Logik aus main.py:
- Normalisierung der Severity-Strings (de/en + None-Schutz)
- Score-Berechnung
- UI-Label, Farb- und Border-Helfer

Severity-Werte (kanonisch): 'critical' | 'major' | 'minor' | 'info'
"""
from __future__ import annotations

from typing import Any, Iterable, Optional

# Kanonische Severities
CRITICAL = 'critical'
MAJOR = 'major'
MINOR = 'minor'
INFO = 'info'

# Score-Gewichte
SCORE_WEIGHTS = {CRITICAL: 8, MAJOR: 3, MINOR: 1, INFO: 1}

# Akzeptierte Synonyme -> kanonisch
_SEVERITY_ALIASES = {
    'critical': CRITICAL, 'kritisch': CRITICAL, 'error': CRITICAL, 'fatal': CRITICAL,
    'major': MAJOR, 'wichtig': MAJOR, 'warning': MAJOR, 'warn': MAJOR,
    'minor': MINOR, 'leicht': MINOR,
    'info': INFO, 'hinweis': INFO, 'note': INFO, 'notice': INFO,
}

# UI-Labels (deutsch)
_UI_LABELS = {CRITICAL: 'Kritisch', MAJOR: 'Wichtig', MINOR: 'Hinweis', INFO: 'Hinweis'}

# Farben
_UI_COLORS = {CRITICAL: '#dc2626', MAJOR: '#ea580c', MINOR: '#6b7280', INFO: '#6b7280'}


def normalize(sev: Any) -> str:
    """Normalisiert beliebigen Severity-Input auf kanonischen Wert.

    Schuetzt gegen None, Nicht-Strings und unbekannte Werte (-> 'info').
    """
    if sev is None:
        return INFO
    s = str(sev).strip().lower()
    if not s:
        return INFO
    return _SEVERITY_ALIASES.get(s, INFO)


def label(sev: Any) -> str:
    """UI-Label fuer Severity (deutsch)."""
    return _UI_LABELS[normalize(sev)]


def color(sev: Any) -> str:
    """Hex-Farbcode fuer Severity-Anzeige."""
    return _UI_COLORS[normalize(sev)]


def border(sev: Any) -> str:
    """CSS border-left fuer Severity-Cards."""
    return f'border-left:4px solid {color(sev)}'


def is_hint_only(finding: Any) -> bool:
    """True wenn das Finding via meta.hint_only als reiner Hinweis markiert ist."""
    meta = getattr(finding, 'meta', None) or {}
    if not isinstance(meta, dict):
        return False
    return bool(meta.get('hint_only'))


# Aliases für ui_findings.py (legacy-Kompatibilität)
severity_label = label
severity_color = color

_PHASE_CODE_PREFIXES: dict[str, tuple[str, ...]] = {
    'Phase 1': (
        'URL_', 'EMAIL_', 'WS_', 'ZERO_WIDTH', 'BRACKET_', 'QUOTE_',
        'BOUNDARY_', 'SOFT_HYPHEN_', 'CONTROL_',
    ),
    'Phase 2': (
        'NUMBER_', 'NUM_', 'UNIT_', 'HTML_', 'PRONOUN_', 'DUPLICATE_',
        'S_CASE_', 'PUNCT_', 'SECURITY_', 'TERM_', 'TERMINOLOGY_',
        'COMPANY_', 'GLOSSARY_', 'NAME_',
    ),
    'Phase 3': (
        'STYLE_', 'RISK_', 'READABILITY_', 'READ_', 'SEMANTIC_',
        'GRAMMAR_', 'PASSIVE_',
    ),
    'Phase 4': (
        'KI_', 'OLLAMA_', 'CONSISTENCY_',
    ),
}


def phase_from_code(code: str) -> str:
    """Bestimmt den Phase-Label anhand des Finding-Codes."""
    if not code:
        return ''
    if code.startswith('P') and len(code) > 1 and code[1].isdigit():
        return f'Phase {code[1]}'
    for phase_label, prefixes in _PHASE_CODE_PREFIXES.items():
        if any(code.startswith(p) for p in prefixes):
            return phase_label
    return ''


def compute_score(issues: Iterable[Any]) -> int:
    """Berechnet einen Score 0..100 aus einer Liste Findings.

    - hint_only-Findings werden komplett ignoriert.
    - Unbekannte Severities werden als 'info' (1 Punkt) gewertet.
    - 100 ist nur erreichbar wenn keine gezaehlten Findings existieren.
    - Untergrenze 5 wenn ueberhaupt Findings vorhanden waren.
    """
    issues = list(issues) if not isinstance(issues, list) else issues
    if not issues:
        return 100
    counted = 0
    penalty = 0
    for f in issues:
        if is_hint_only(f):
            continue
        sev = normalize(getattr(f, 'severity', None))
        penalty += SCORE_WEIGHTS.get(sev, SCORE_WEIGHTS[INFO])
        counted += 1
    if counted == 0:
        return 100
    score = max(0, 100 - penalty)
    if score >= 100:
        score = 99
    if score < 5:
        score = 5
    return score
