"""pairing_utils

Testbare, pure Hilfsfunktionen für Dateipaarung.
"""
from __future__ import annotations
from typing import List, Tuple, Any, Callable


def smart_pair_files(source_files: List[str], translation_files: List[str], service_factory: Callable[[], Any]) -> Tuple[list, list, list]:
    """Führt Paarung über bereitgestellten Service aus.

    service_factory muss Objekt mit .pair(source, translation) liefern.
    Rückgabe: (pairs, unmatched_source, unmatched_translation)
    """
    service = service_factory()
    return service.pair(source_files, translation_files)
