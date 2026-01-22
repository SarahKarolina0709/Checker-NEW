"""DEPRECATED WRAPPER (Übergangsphase)

Implementation nach `quality_gui_grammar.py` verschoben.
Bitte künftig verwenden:
    from quality_gui_grammar import GrammarChecker

Dieser Wrapper wird nach der Cleanup-Phase entfernt.
"""
from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "grammar_quality ist veraltet – quality_gui_grammar verwenden (Entfernung geplant)",
    DeprecationWarning,
    stacklevel=2,
)
try:  # pragma: no cover - simpler re-export
    from quality_gui_grammar import GrammarChecker, run_grammar_analysis, _language_tool, _hunspell  # type: ignore
except Exception:  # Fallback Stub
    class GrammarChecker:  # type: ignore
        def __init__(self, *_, **__):
            pass
        def analyze_segments(self, *_a, **_k):
            return []
    def run_grammar_analysis(*_a, **_k):  # type: ignore
        return []
