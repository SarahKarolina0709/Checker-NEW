# -*- coding: utf-8 -*-
"""Sprach-Erkennung fuer die "Auto-Erkennung"-Option der Sprach-Dropdowns.

Reine, testbare Funktionen ohne UI-Abhaengigkeit. `langdetect` ist eine
optionale Dependency: fehlt sie, fallen die Funktionen graceful auf den
uebergebenen Fallback-Code zurueck.

Verwendung in main.run_analysis_sync(): wenn der Nutzer "Auto-Erkennung"
waehlt, wird hier aus den tatsaechlichen Quell-/Zieltexten der Sprachcode
bestimmt, statt den Platzhalter 'auto' an die Checker weiterzureichen.
"""
from __future__ import annotations

from typing import Iterable, List

try:  # optionale Dependency
    from langdetect import detect_langs, DetectorFactory  # type: ignore
    # Deterministische Ergebnisse (langdetect ist sonst zufallsabhaengig)
    DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
except ImportError:  # pragma: no cover - nur ohne Dependency
    detect_langs = None  # type: ignore
    _HAS_LANGDETECT = False

# langdetect liefert teils laenderspezifische Codes; auf 2-Letter normalisieren.
_NORMALIZE = {
    'zh-cn': 'zh', 'zh-tw': 'zh', 'nb': 'no', 'nn': 'no',
}

# Minimaler Stichproben-Umfang, ab dem wir der Erkennung vertrauen.
_MIN_CHARS = 20


def is_auto(code: str) -> bool:
    """True, wenn der Code die Auto-Erkennung anfordert ('auto' oder leer)."""
    return not code or code.strip().lower() == 'auto'


def detect_lang_code(text: str) -> str:
    """Erkennt den 2-Letter-Sprachcode eines Textes.

    Returns: 2-Letter-Code (z. B. 'de') oder '' wenn keine sichere Erkennung
    moeglich ist (zu kurz, keine Dependency, Fehler).
    """
    if not _HAS_LANGDETECT or not text:
        return ''
    sample = text.strip()
    if len(sample) < _MIN_CHARS:
        return ''
    try:
        results = detect_langs(sample)
    except Exception:
        return ''
    if not results:
        return ''
    best = results[0]
    code = str(getattr(best, 'lang', '') or '').lower()
    code = _NORMALIZE.get(code, code)
    return code[:2] if code else ''


def detect_from_texts(texts: Iterable[str]) -> str:
    """Erkennt die dominante Sprache aus mehreren Textsegmenten.

    Aggregiert ueber alle Segmente und gibt den haeufigsten erkannten Code
    zurueck (robuster als ein einzelnes, evtl. kurzes Segment).
    """
    counts: dict[str, int] = {}
    joined_parts: List[str] = []
    for t in texts:
        if not t:
            continue
        joined_parts.append(t)
        code = detect_lang_code(t)
        if code:
            counts[code] = counts.get(code, 0) + 1
    if counts:
        return max(counts.items(), key=lambda kv: kv[1])[0]
    # Fallback: alles zusammenhaengen (falls einzelne Segmente zu kurz waren)
    return detect_lang_code(' '.join(joined_parts))


def resolve_lang(code: str, texts: Iterable[str], fallback: str) -> str:
    """Loest 'auto'/leer in einen echten Sprachcode auf.

    - Ist `code` ein konkreter Code (z. B. 'de'), wird er unveraendert
      zurueckgegeben.
    - Bei 'auto'/leer wird aus `texts` erkannt; schlaegt das fehl, greift
      `fallback`.
    """
    if not is_auto(code):
        return code
    detected = detect_from_texts(texts)
    return detected or fallback
