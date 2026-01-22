#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Neutral Pairing Service (ehemals pairing_service)

Ausgelagerte intelligente Dateipaarungs-Logik.

Bereitgestellte API:
  - PairingService(event_bus=None, similarity_threshold=0.6)
  - get_pairing_service(event_bus=None) -> Singleton
  - FilePair Dataclass

Unabhängig von GUI / Design-System.
"""
from __future__ import annotations
import os
import re
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Iterable, Any, Tuple

try:  # Optionale EventBus Einbindung
    from infra.event_bus import EventBus  # type: ignore
except Exception:  # pragma: no cover
    EventBus = None  # type: ignore

try:  # Logging Fallback
    import logging
    logger = logging.getLogger(__name__)
except Exception:  # pragma: no cover
    class _Dummy:
        def __getattr__(self, _):
            return lambda *a, **k: None
    logger = _Dummy()


@dataclass
class FilePair:
    source: str
    translation: str
    similarity: float
    source_name: str
    translation_name: str


class PairingService:
    """Kapselt Smart File Pairing.
    API:
      pair(source_files, translation_files) -> (pairs, unmatched_source, unmatched_translation)
      get_last_pairs() -> List[FilePair]
    """

    def __init__(self, event_bus: Optional[Any] = None, similarity_threshold: float = 0.6):
        self.event_bus = event_bus
        self.similarity_threshold = similarity_threshold
        self._last_pairs: List[FilePair] = []
        self._last_unmatched: Dict[str, List[str]] = {"source": [], "translation": []}
        self._metrics: Dict[str, Any] = {}

    def pair(self, source_files: Iterable[str], translation_files: Iterable[str]) -> Tuple[List[FilePair], List[str], List[str]]:
        start = time.time()
        source_files = list(source_files)
        translation_files = list(translation_files)
        if not source_files or not translation_files:
            self._store([], list(source_files), list(translation_files))
            return [], list(source_files), list(translation_files)

        unmatched_translation = list(translation_files)
        pairs: List[FilePair] = []
        unmatched_source: List[str] = []

        for s in source_files:
            sn = self._normalize(s)
            best = None
            best_score = 0.0
            for t in unmatched_translation:
                tn = self._normalize(t)
                score = self._similarity(sn, tn)
                if score > best_score and score >= self.similarity_threshold:
                    best = t
                    best_score = score
            if best:
                pairs.append(FilePair(
                    source=s,
                    translation=best,
                    similarity=best_score,
                    source_name=os.path.basename(s),
                    translation_name=os.path.basename(best)
                ))
                unmatched_translation.remove(best)
            else:
                unmatched_source.append(s)

        self._store(pairs, unmatched_source, unmatched_translation)
        duration = time.time() - start
        self._emit_event("pairing.completed", {
            "pairs": len(pairs),
            "unmatched_source": len(unmatched_source),
            "unmatched_translation": len(unmatched_translation),
            "duration_ms": int(duration * 1000),
            "threshold": self.similarity_threshold
        })
        logger.info(
            "✅ PairingService: %s pairs, %s unmatched source, %s unmatched translation (%.1f ms)",
            len(pairs), len(unmatched_source), len(unmatched_translation), duration * 1000
        )
        return pairs, unmatched_source, unmatched_translation

    def get_last_pairs(self) -> List[FilePair]:
        return self._last_pairs

    def get_unmatched(self) -> Dict[str, List[str]]:
        return self._last_unmatched

    def _store(self, pairs: List[FilePair], unmatched_source: List[str], unmatched_translation: List[str]):
        self._last_pairs = pairs
        self._last_unmatched = {"source": unmatched_source, "translation": unmatched_translation}
        self._metrics["last_total_pairs"] = len(pairs)

    def _normalize(self, path: str) -> str:
        try:
            filename = os.path.splitext(os.path.basename(path))[0].lower()
            patterns = [
                '_source', '_target', '_translation', '_translated', '_trans',
                '_original', '_orig', '_src', '_übersetzung', '_übersetzt',
                '_quelle', '_ziel', 'source_', 'target_', 'trans_', 'orig_'
            ]
            for p in patterns:
                filename = filename.replace(p, '')
            filename = re.sub(r'_v?\d+$', '', filename)
            filename = re.sub(r'_\d+$', '', filename)
            return filename.strip('_- ')
        except Exception:
            return os.path.basename(path).lower()

    def _similarity(self, a: str, b: str) -> float:
        try:
            if a == b:
                return 1.0
            ratio = SequenceMatcher(None, a, b).ratio()
            if a in b or b in a:
                ratio += 0.2
            words1 = set(a.split('_'))
            words2 = set(b.split('_'))
            if words1 or words2:
                common = len(words1 & words2)
                total = len(words1 | words2)
                if total:
                    word_sim = common / total
                    ratio = (ratio + word_sim) / 2
            return min(ratio, 1.0)
        except Exception:
            return 0.0

    def _emit_event(self, topic: str, payload: Dict[str, Any]):
        if self.event_bus is None:
            return
        try:
            self.event_bus.publish(topic, payload)
        except Exception:  # pragma: no cover
            logger.debug("Event publish failed", exc_info=True)


_def_instance: Optional[PairingService] = None


def get_pairing_service(event_bus: Optional[Any] = None) -> PairingService:
    global _def_instance
    if _def_instance is None:
        _def_instance = PairingService(event_bus=event_bus)
    return _def_instance

__all__ = ["FilePair", "PairingService", "get_pairing_service"]
