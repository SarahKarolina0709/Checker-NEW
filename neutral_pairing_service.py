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


_XML_LANG_EXTS = frozenset({'.xliff', '.xlf', '.sdlxliff', '.mqxliff', '.tmx'})
_LANG_CODE_RE = re.compile(
    r'[_\-\.](?P<lang>de|en|fr|es|it|nl|pl|pt|ru|zh|ja|ko'
    r'|cs|sv|da|fi|nb|nn|hu|ro|bg|hr|sk|sl|et|lv|lt|el|tr|ar|he)'
    r'(?=[_\-\.]|$)',
    re.IGNORECASE,
)
# Zusätzlich: Sprachcode am ANFANG des Dateinamens, z.B. "DE_vertrag" oder "EN-contract"
_LANG_CODE_PREFIX_RE = re.compile(
    r'^(?P<lang>de|en|fr|es|it|nl|pl|pt|ru|zh|ja|ko'
    r'|cs|sv|da|fi|nb|nn|hu|ro|bg|hr|sk|sl|et|lv|lt|el|tr|ar|he)'
    r'(?=[_\-\.])',
    re.IGNORECASE,
)


def _extract_lang_from_name(path: str) -> Optional[str]:
    """Extrahiert einen Sprachcode aus dem Dateinamen.
    
    Erkennt Suffix-Codes ('vertrag_de.docx') und Präfix-Codes ('DE_vertrag.docx').
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    m = _LANG_CODE_RE.search(stem) or _LANG_CODE_PREFIX_RE.match(stem)
    return m.group('lang').lower() if m else None
_XML_NS_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def _detect_file_lang(path: str) -> Optional[str]:
    """Extrahiert den primären Sprachcode aus XLIFF/TMX XML-Metadaten.

    XLIFF 1.x: <file source-language="de">
    XLIFF 2.x: <xliff srcLang="de">
    TMX:       <header srclang="de"> oder <tuv xml:lang="de">

    Gibt den normalisierten 2-Buchstaben-Code zurück (z.B. 'de', 'en') oder None.
    """
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext not in _XML_LANG_EXTS:
            return None
        import xml.etree.ElementTree as ET
        tree = ET.parse(path)
        root = tree.getroot()

        # XLIFF 2.x root attrs
        for attr in ('srcLang', 'source-language'):
            val = root.get(attr)
            if val:
                return val.split('-')[0].lower()  # 'de-DE' → 'de'

        # XLIFF 1.x: first <file> element with source-language
        for elem in root.iter():
            for attr in ('source-language', 'srcLang'):
                val = elem.get(attr)
                if val:
                    return val.split('-')[0].lower()

        # TMX: <header srclang="...">
        for elem in root.iter():
            val = elem.get('srclang')
            if val and val.lower() != '*all*':
                return val.split('-')[0].lower()

        # Fallback: xml:lang on root or first child
        val = root.get(_XML_NS_LANG)
        if val:
            return val.split('-')[0].lower()

        return None
    except Exception:
        return None


@dataclass
class FilePair:
    source: str
    translation: str
    similarity: float
    source_name: str
    translation_name: str
    source_lang: Optional[str] = None       # z.B. 'de' – aus XML-Metadaten oder Dateiname
    translation_lang: Optional[str] = None  # z.B. 'en' – aus XML-Metadaten oder Dateiname


class PairingService:
    """Kapselt Smart File Pairing.
    API:
      pair(source_files, translation_files) -> (pairs, unmatched_source, unmatched_translation)
      get_last_pairs() -> List[FilePair]
    """

    # Konfigurierbare Confidence-Schwellen
    DEFAULT_HIGH_CONFIDENCE = 0.85
    DEFAULT_MEDIUM_CONFIDENCE = 0.70
    DEFAULT_ADAPTIVE_REDUCTION = 0.10   # Wie viel der Threshold für den 2. Pass reduziert wird
    DEFAULT_ADAPTIVE_MIN = 0.40         # Untere Grenze für den adaptiven Threshold

    def __init__(self,
                 event_bus: Optional[Any] = None,
                 similarity_threshold: float = 0.6,
                 high_confidence: float = DEFAULT_HIGH_CONFIDENCE,
                 medium_confidence: float = DEFAULT_MEDIUM_CONFIDENCE):
        self.event_bus = event_bus
        self.similarity_threshold = similarity_threshold
        self.high_confidence = high_confidence
        self.medium_confidence = medium_confidence
        self._last_pairs: List[FilePair] = []
        self._last_unmatched: Dict[str, List[str]] = {"source": [], "translation": []}
        self._metrics: Dict[str, Any] = {}
        self._pair_confidence: Dict[Tuple[str, str], str] = {}

    def pair(self, source_files: Iterable[str], translation_files: Iterable[str]) -> Tuple[List[FilePair], List[str], List[str]]:
        """Optimiertes Pairing mit globalem Score-Ranking statt greedy first-file-wins."""
        start = time.time()
        source_files = list(source_files)
        translation_files = list(translation_files)
        if not source_files or not translation_files:
            self._store([], list(source_files), list(translation_files))
            return [], list(source_files), list(translation_files)

        # Reset per-run state
        self._pair_confidence = {}

        # Pre-Normalisierung
        source_normalized = {s: self._normalize(s) for s in source_files}
        translation_normalized = {t: self._normalize(t) for t in translation_files}

        # XML-Sprach-Erkennung für XLIFF/TMX (einmalig pro Datei)
        source_langs: Dict[str, Optional[str]] = {s: _detect_file_lang(s) for s in source_files}
        translation_langs: Dict[str, Optional[str]] = {t: _detect_file_lang(t) for t in translation_files}

        # Vollständige Score-Matrix berechnen
        all_scores: List[Tuple[str, str, float]] = []
        for s in source_files:
            sn = source_normalized[s]
            sl = source_langs[s]
            for t in translation_files:
                tn = translation_normalized[t]
                tl = translation_langs[t]
                score = self._similarity(sn, tn)
                # XML-Metadaten-Boost: unterschiedliche erkannte Sprachen → sehr hohes Vertrauen
                if sl and tl:
                    if sl != tl:
                        score = max(score, 0.92)   # Unterschiedliche Sprachen = klares Paar
                    else:
                        score = min(score, 0.45)   # Gleiche Sprache = kein Translations-Paar
                if score >= self.similarity_threshold:
                    all_scores.append((s, t, score))

        # Sortiere nach höchstem Score absteigend → globales Optimum statt greedy
        all_scores.sort(key=lambda x: x[2], reverse=True)

        # Greedy von oben: Jede Source und Translation nur einmal vergeben
        used_sources: set = set()
        used_translations: set = set()
        pairs: List[FilePair] = []

        for s, t, score in all_scores:
            if s in used_sources or t in used_translations:
                continue
            confidence = 'high' if score >= self.high_confidence else ('medium' if score >= self.medium_confidence else 'low')
            pairs.append(FilePair(
                source=s,
                translation=t,
                similarity=score,
                source_name=os.path.basename(s),
                translation_name=os.path.basename(t),
                source_lang=source_langs.get(s) or _extract_lang_from_name(s),
                translation_lang=translation_langs.get(t) or _extract_lang_from_name(t),
            ))
            self._pair_confidence[(s, t)] = confidence
            used_sources.add(s)
            used_translations.add(t)

        unmatched_source = [s for s in source_files if s not in used_sources]
        unmatched_translation_set = set(translation_files) - used_translations

        # Second pass: Reduzierter Threshold für noch ungematchte Dateien
        if unmatched_source and unmatched_translation_set:
            adaptive_threshold = max(self.similarity_threshold - self.DEFAULT_ADAPTIVE_REDUCTION,
                                     self.DEFAULT_ADAPTIVE_MIN)
            second_pass_scores: List[Tuple[str, str, float]] = []
            for s in unmatched_source:
                sn = source_normalized[s]
                sl = source_langs.get(s)
                for t in unmatched_translation_set:
                    tn = translation_normalized[t]
                    tl = translation_langs.get(t)
                    score = self._similarity(sn, tn)
                    if sl and tl:
                        if sl != tl:
                            score = max(score, 0.92)
                        else:
                            score = min(score, 0.45)
                    if score >= adaptive_threshold:
                        second_pass_scores.append((s, t, score))
            second_pass_scores.sort(key=lambda x: x[2], reverse=True)

            still_unmatched_source: List[str] = []
            for s, t, score in second_pass_scores:
                if s in used_sources or t in used_translations:
                    continue
                confidence = 'low'
                pairs.append(FilePair(
                    source=s,
                    translation=t,
                    similarity=score,
                    source_name=os.path.basename(s),
                    translation_name=os.path.basename(t),
                    source_lang=source_langs.get(s) or _extract_lang_from_name(s),
                    translation_lang=translation_langs.get(t) or _extract_lang_from_name(t),
                ))
                self._pair_confidence[(s, t)] = confidence
                used_sources.add(s)
                used_translations.add(t)
                unmatched_translation_set.discard(t)

            unmatched_source = [s for s in source_files if s not in used_sources]

        unmatched_translation_list = list(unmatched_translation_set)
        self._store(pairs, unmatched_source, unmatched_translation_list)
        duration = time.time() - start

        # Statistiken
        high_conf = sum(1 for v in self._pair_confidence.values() if v == 'high')
        med_conf = sum(1 for v in self._pair_confidence.values() if v == 'medium')
        low_conf = sum(1 for v in self._pair_confidence.values() if v == 'low')

        self._emit_event("pairing.completed", {
            "pairs": len(pairs),
            "high_confidence": high_conf,
            "medium_confidence": med_conf,
            "low_confidence": low_conf,
            "unmatched_source": len(unmatched_source),
            "unmatched_translation": len(unmatched_translation_list),
            "duration_ms": int(duration * 1000),
            "threshold": self.similarity_threshold
        })
        logger.info(
            "PairingService: %s pairs (H:%s M:%s L:%s), %s unmatched source, %s unmatched translation (%.1f ms)",
            len(pairs), high_conf, med_conf, low_conf,
            len(unmatched_source), len(unmatched_translation_list), duration * 1000
        )
        return pairs, unmatched_source, unmatched_translation_list
    
    def get_pair_confidence(self, source: str, translation: str) -> str:
        """🔧 NEU: Gibt das Confidence-Level eines Paares zurück."""
        if not hasattr(self, '_pair_confidence'):
            return 'unknown'
        return self._pair_confidence.get((source, translation), 'unknown')

    def get_last_pairs(self) -> List[FilePair]:
        return self._last_pairs

    def get_unmatched(self) -> Dict[str, List[str]]:
        return self._last_unmatched

    def _store(self, pairs: List[FilePair], unmatched_source: List[str], unmatched_translation: List[str]):
        self._last_pairs = pairs
        self._last_unmatched = {"source": unmatched_source, "translation": unmatched_translation}
        self._metrics["last_total_pairs"] = len(pairs)

    def _normalize(self, path: str) -> str:
        """Normalisiert Dateinamen für Paarung mit Language-Code-Handling."""
        try:
            filename = os.path.splitext(os.path.basename(path))[0].lower()
            
            # Language-Codes entfernen (de, en, fr, etc.) für fairen Vergleich
            # Suffix-Position: _de, -en, .fr, …
            filename = re.sub(
                r'[_\-\.](?:de|en|fr|es|it|nl|pl|pt|ru|zh|ja|ko|cs|sv|da|fi|nb|nn|hu|ro|bg|hr|sk|sl|et|lv|lt|el|tr|ar|he)(?=[_\-\.]|$)',
                '', filename
            )
            # Präfix-Position: DE_, EN-, fr. etc.
            filename = re.sub(
                r'^(?:de|en|fr|es|it|nl|pl|pt|ru|zh|ja|ko|cs|sv|da|fi|nb|nn|hu|ro|bg|hr|sk|sl|et|lv|lt|el|tr|ar|he)(?=[_\-\.])',
                '', filename
            )
            
            # Suffix/Prefix-Liste — NUR an Wortgrenzen entfernen, sonst zerstoeren
            # Tokens wie "transformer_" mit Suffix "trans_" das Wort (-> "former_").
            suffixes = [
                '_source', '_target', '_translation', '_translated', '_trans',
                '_original', '_orig', '_src', '_übersetzung', '_übersetzt',
                '_quelle', '_ziel', '_final', '_korrektur', '_review',
                '_draft', '_v2', '_neu', '_clean', '_edited',
                '_proofread', '_lektoriert',
            ]
            prefixes = ['source_', 'target_', 'trans_', 'orig_']
            changed = True
            while changed:
                changed = False
                for suf in suffixes:
                    if filename.endswith(suf) and len(filename) > len(suf):
                        filename = filename[:-len(suf)]
                        changed = True
                for pre in prefixes:
                    if filename.startswith(pre) and len(filename) > len(pre):
                        filename = filename[len(pre):]
                        changed = True
            # Versionsnummern entfernen
            filename = re.sub(r'_v?\d+$', '', filename)
            filename = re.sub(r'_\d+$', '', filename)
            # Datumsformate entfernen
            filename = re.sub(r'_\d{4}[-_]?\d{2}[-_]?\d{2}', '', filename)
            filename = re.sub(r'_\d{2}[-_]\d{2}[-_]\d{4}', '', filename)
            return filename.strip('_- ')
        except Exception:
            return os.path.basename(path).lower()

    def _similarity(self, a: str, b: str) -> float:
        """Similarity mit Token-Boost und Präfix-Matching."""
        try:
            # Leere Strings (z.B. weil Normalisierung alles entfernt hat)
            # liefern KEIN Pairing-Signal → 0.0, nicht 1.0
            if not a or not b:
                return 0.0
            if a == b:
                return 1.0
            
            # Token-basierter Check
            tokens_a = set(re.split(r'[\W_]+', a))
            tokens_b = set(re.split(r'[\W_]+', b))
            tokens_a.discard('')
            tokens_b.discard('')
            
            # Konservativer early-return: nur wenn beide lang UND SequenceMatcher niedrig
            if tokens_a and tokens_b:
                common_tokens = len(tokens_a & tokens_b)
                if common_tokens == 0 and len(a) > 8 and len(b) > 8:
                    if not (a in b or b in a):
                        quick_ratio = SequenceMatcher(None, a, b).ratio()
                        if quick_ratio < 0.3:
                            return 0.0
            
            ratio = SequenceMatcher(None, a, b).ratio()
            
            # Substring-Bonus (proportional zur Abdeckung)
            # Mindestlänge schützt vor "" in "abc" Trivial-Match (oben bereits abgefangen,
            # aber doppelt sicher) sowie vor 1-Zeichen-Triggern
            if len(a) >= 3 and a in b:
                ratio += 0.2 * (len(a) / len(b))
            elif len(b) >= 3 and b in a:
                ratio += 0.2 * (len(b) / len(a))
            
            # Präfix-Boost
            prefix_len = 0
            for i, (ca, cb) in enumerate(zip(a, b)):
                if ca == cb:
                    prefix_len = i + 1
                else:
                    break
            if prefix_len >= 4:
                prefix_boost = min(0.1, prefix_len / max(len(a), len(b)) * 0.2)
                ratio += prefix_boost
            
            # Cap ratio BEVOR gewichteter Durchschnitt
            ratio = min(ratio, 1.0)
            
            # Token-basierte Ähnlichkeit
            if tokens_a and tokens_b:
                common = len(tokens_a & tokens_b)
                total = len(tokens_a | tokens_b)
                if total:
                    word_sim = common / total
                    ratio = (ratio * 0.6) + (word_sim * 0.4)
            
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
    """Gibt die Singleton-Instanz zurück; erstellt sie bei Bedarf mit event_bus."""
    global _def_instance
    if _def_instance is None:
        _def_instance = PairingService(event_bus=event_bus)
    elif event_bus is not None and _def_instance.event_bus is None:
        # Nachträgliche EventBus-Registrierung wenn noch keine vorhanden
        _def_instance.event_bus = event_bus
    return _def_instance

__all__ = ["FilePair", "PairingService", "get_pairing_service"]
