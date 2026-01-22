#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEPRECATED WRAPPER

Ehemaliger Implementierungsort der Pairing-Logik.
Neue neutrale Implementierung in neutral_pairing_service.py
"""
from __future__ import annotations

try:  # Bevorzugt neue neutrale Implementierung
    from neutral_pairing_service import (  # type: ignore
        PairingService,
        FilePair,
        get_pairing_service
    )
    __all__ = ["PairingService", "FilePair", "get_pairing_service"]
except Exception:  # Fallback falls neue Datei (noch) fehlt
    import os, re, time
    from dataclasses import dataclass
    from difflib import SequenceMatcher
    from typing import List, Dict, Optional, Iterable, Any, Tuple

    @dataclass
    class FilePair:
        source: str
        translation: str
        similarity: float
        source_name: str
        translation_name: str

    class PairingService:
        def __init__(self, event_bus: Optional[Any] = None, similarity_threshold: float = 0.6):
            self.event_bus = event_bus
            # Basis-Threshold – kann später dynamisch abgesenkt werden
            self.similarity_threshold = similarity_threshold
            self._last_pairs: List[FilePair] = []
            self._last_unmatched: Dict[str, List[str]] = {"source": [], "translation": []}
            # Cache für Normalisierung & Similarity zur Performance-Verbesserung bei großen Listen
            self._norm_cache: Dict[str, str] = {}
            self._sim_cache: Dict[Tuple[str,str], float] = {}

        def pair(self, source_files: Iterable[str], translation_files: Iterable[str]):
            """Zweistufiges Matching:
            1. Exakter & hochgradiger Match (>= Threshold)
            2. Opportunistischer Second-Pass für knapp darunter liegende Kandidaten
            Verbesserungen:
            - Entfernt Sprachkürzel (de, en, fr, es ...) am Ende oder in Klammern
            - Entfernt numerische Versionierungen (v2, v03, _final, _revA)
            - Wortbasierte Gewichtung + Sequenzähnlichkeit
            - Caching für Normalisierung & Similarity
            """
            source_files = list(source_files)
            translation_files = list(translation_files)
            unmatched_translation = list(translation_files)
            pairs: List[FilePair] = []
            unmatched_source: List[str] = []

            # Vorab normalisieren & index für schnellere Suche
            norm_trans = {t: self._normalize(t) for t in unmatched_translation}

            def _best_match(norm_source: str):
                best_tuple = (None, 0.0)
                for t, nt in norm_trans.items():
                    score = self._similarity(norm_source, nt)
                    if score > best_tuple[1]:
                        best_tuple = (t, score)
                return best_tuple

            # First pass (hoher Threshold)
            for s in source_files:
                sn = self._normalize(s)
                best, best_score = _best_match(sn)
                if best and best_score >= self.similarity_threshold:
                    pairs.append(FilePair(s, best, best_score, os.path.basename(s), os.path.basename(best)))
                    unmatched_translation.remove(best)
                    norm_trans.pop(best, None)
                else:
                    unmatched_source.append(s)

            # Second pass: Versuche restliche Source-Dateien unter abgesenktem adaptiven Threshold
            if unmatched_source and norm_trans:
                adaptive_threshold = max(self.similarity_threshold - 0.1, 0.45)
                still_unmatched: List[str] = []
                for s in unmatched_source:
                    sn = self._normalize(s)
                    best, best_score = _best_match(sn)
                    # Sicherheitsregel: Score muss mindestens 0.5 ODER (>= adaptiver Threshold & Wortüberdeckung >=50%) sein
                    if best and best_score >= adaptive_threshold:
                        word_cov = self._word_coverage(sn, self._normalize(best))
                        if best_score >= 0.5 or word_cov >= 0.5:
                            pairs.append(FilePair(s, best, best_score, os.path.basename(s), os.path.basename(best)))
                            unmatched_translation.remove(best)
                            norm_trans.pop(best, None)
                            continue
                    still_unmatched.append(s)
                unmatched_source = still_unmatched

            # Ergebnis speichern
            self._last_pairs = pairs
            self._last_unmatched = {"source": unmatched_source, "translation": unmatched_translation}
            # Optionale Event-Bus Meldung
            try:
                if self.event_bus:
                    self.event_bus.publish('pairing.completed', {
                        'pairs': len(pairs),
                        'unmatched_source': len(unmatched_source),
                        'unmatched_translation': len(unmatched_translation)
                    })
            except Exception:
                pass
            return pairs, unmatched_source, unmatched_translation

        def get_last_pairs(self):
            return self._last_pairs

        def get_unmatched(self):
            return self._last_unmatched

        def _normalize(self, path: str) -> str:
            if path in self._norm_cache:
                return self._norm_cache[path]
            try:
                filename = os.path.splitext(os.path.basename(path))[0].lower()
                # Entferne häufige Suffixe
                suffixes = ['_source','_target','_translation','_translated','_trans','_original','_orig','_src','-source','-target']
                for p in suffixes:
                    if p in filename:
                        filename = filename.replace(p, '')
                # Entferne Sprachkürzel (de,en,fr,es,it,pt,nl,pl,cs,sv,da,fi) am Ende oder in Klammern
                filename = re.sub(r'([_\-\s]|\()?(de|en|fr|es|it|pt|nl|pl|cs|sv|da|fi)(\))?$', '', filename)
                # Entferne Versions-/Statusmarker
                filename = re.sub(r'(?:[_\-]v\d+|[_\-]rev[a-z]?|[_\-](final|clean|neu|new))$', '', filename)
                # Zahlensuffixe
                filename = re.sub(r'[_\-]?\d{1,3}$', '', filename)
                cleaned = filename.strip('_- .')
            except Exception:
                cleaned = os.path.basename(path).lower()
            self._norm_cache[path] = cleaned
            return cleaned

        def _similarity(self, a: str, b: str) -> float:
            key = (a, b)
            if key in self._sim_cache:
                return self._sim_cache[key]
            try:
                if a == b:
                    score = 1.0
                else:
                    seq = SequenceMatcher(None, a, b).ratio()
                    # Tokenisierte Wort-Sets (Unterstrich & Minus als Trenner)
                    words1 = set(filter(None, re.split(r'[_\-\s]+', a)))
                    words2 = set(filter(None, re.split(r'[_\-\s]+', b)))
                    if words1 and words2:
                        common = len(words1 & words2)
                        total = len(words1 | words2)
                        word_sim = common / total if total else seq
                    else:
                        word_sim = seq
                    containment_boost = 0.12 if (a in b or b in a) else 0.0
                    score = min(1.0, (seq * 0.55) + (word_sim * 0.35) + containment_boost)
                self._sim_cache[key] = score
                return score
            except Exception:
                return 0.0

        def _word_coverage(self, a: str, b: str) -> float:
            try:
                wa = set(filter(None, re.split(r'[_\-\s]+', a)))
                wb = set(filter(None, re.split(r'[_\-\s]+', b)))
                if not wa or not wb:
                    return 0.0
                return len(wa & wb) / len(wa | wb)
            except Exception:
                return 0.0

    _def_instance: Optional[PairingService] = None

    def get_pairing_service(event_bus: Optional[Any] = None) -> PairingService:  # type: ignore
        global _def_instance
        if _def_instance is None:
            _def_instance = PairingService(event_bus=event_bus)
        return _def_instance

    __all__ = ["PairingService", "FilePair", "get_pairing_service"]
