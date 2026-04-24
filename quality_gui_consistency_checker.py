"""quality_gui_consistency_checker – Konsistenzprüfung über mehrere Segmente/Dateien.

Prüft ob gleiche Quellterme konsistent übersetzt werden:
- Extrahiert signifikante Terme aus Quelltexten
- Gruppiert Segmente nach Quelltermen
- Findet Inkonsistenzen (gleicher Quellterm → verschiedene Übersetzungen)

Ergebnis-Einträge (Finding Dict):
{
  'rule_id': 'CONSISTENCY_*',
  'severity': 'minor'|'major',
  'message': str,
  'source_term': str,
  'translations': list[str],
  'segment_indices': list[int],
  'category': 'consistency'
}
"""
from __future__ import annotations
import logging
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

_logger = logging.getLogger(__name__)

# Minimum Termlänge für Konsistenzprüfung
MIN_TERM_LENGTH = 3
# Minimum Vorkommen eines Terms für Prüfung
MIN_TERM_OCCURRENCES = 2
# Maximale Terme pro Analyse (Performance-Limit)
MAX_TERMS_TO_CHECK = 500

# Stoppwörter die nicht als Terme gelten (mehrsprachig)
STOPWORDS = {
    # Deutsch
    'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines', 'einem', 'einen',
    'und', 'oder', 'aber', 'wenn', 'weil', 'dass', 'als', 'auch', 'nur', 'noch', 'schon',
    'mit', 'für', 'von', 'auf', 'aus', 'bei', 'nach', 'vor', 'über', 'unter', 'durch',
    'ist', 'sind', 'war', 'waren', 'wird', 'werden', 'hat', 'haben', 'kann', 'können',
    'nicht', 'kein', 'keine', 'keinen', 'keinem', 'keiner', 'keines',
    'sich', 'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'man',
    'diese', 'dieser', 'dieses', 'diesem', 'diesen', 'jede', 'jeder', 'jedes',
    'alle', 'alles', 'allem', 'allen', 'aller',
    'sehr', 'mehr', 'viel', 'viele', 'wenig', 'wenige', 'einige',
    'hier', 'dort', 'dann', 'wann', 'wie', 'was', 'wer', 'wo', 'warum',
    # Englisch
    'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'also', 'only', 'still',
    'with', 'for', 'from', 'on', 'at', 'by', 'to', 'in', 'of', 'about', 'into',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'will', 'would', 'could', 'should',
    'has', 'have', 'had', 'do', 'does', 'did', 'can', 'may', 'might', 'must',
    'not', 'no', 'none', 'nor', 'neither',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those', 'which', 'who', 'whom', 'whose',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'very', 'much', 'many', 'little', 'few',
    'here', 'there', 'when', 'where', 'why', 'how', 'what',
    # Französisch
    'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais', 'si',
    'pour', 'avec', 'dans', 'sur', 'par', 'est', 'sont', 'être', 'avoir',
    'ce', 'cette', 'ces', 'qui', 'que', 'quoi', 'dont', 'où',
    # Spanisch
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero',
    'para', 'con', 'en', 'por', 'es', 'son', 'ser', 'estar',
    # Italienisch
    'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'e', 'o', 'ma',
    'per', 'con', 'in', 'è', 'sono', 'essere', 'avere',
}

# Regex für Wort-Extraktion
WORD_PATTERN = re.compile(r'\b[A-Za-zÄÖÜäöüßéèêëàâùûôîïçñáíóú][A-Za-zÄÖÜäöüßéèêëàâùûôîïçñáíóú\'-]*[A-Za-zÄÖÜäöüßéèêëàâùûôîïçñáíóú]\b|\b[A-Za-zÄÖÜäöüßéèêëàâùûôîïçñáíóú]{2,}\b')

# Multi-Wort-Terme (2-3 Wörter)
MULTIWORD_PATTERN = re.compile(r'\b([A-Za-zÄÖÜäöüß]{3,}(?:\s+[A-Za-zÄÖÜäöüß]{3,}){1,2})\b')


@dataclass
class TermOccurrence:
    """Repräsentiert ein Vorkommen eines Terms."""
    segment_index: int
    source_text: str
    target_text: str
    source_context: str = ""  # Kontext um den Term
    target_context: str = ""


@dataclass 
class ConsistencyFinding:
    """Ein Konsistenz-Finding."""
    rule_id: str
    severity: str  # 'minor' oder 'major'
    message: str
    source_term: str
    translations: List[str]
    segment_indices: List[int]
    occurrences: List[TermOccurrence] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'severity': self.severity,
            'message': self.message,
            'source_term': self.source_term,
            'translations': self.translations,
            'segment_indices': self.segment_indices,
            'category': 'consistency',
            'meta': {
                'occurrence_count': len(self.occurrences),
                'variant_count': len(self.translations),
            }
        }


class ConsistencyChecker:
    """Prüft Terminologie-Konsistenz über mehrere Segmente.
    
    Findet Fälle wo der gleiche Quellterm unterschiedlich übersetzt wurde.
    """
    
    # Cache für Term-Extraktion (class-level)
    _term_cache: Dict[str, List[str]] = {}
    _cache_hits: int = 0
    _cache_misses: int = 0
    _CACHE_MAX_ENTRIES: int = 2000  # Verhindert unbegrenztes Wachstum
    
    def __init__(self,
                 min_term_length: int = MIN_TERM_LENGTH,
                 min_occurrences: int = MIN_TERM_OCCURRENCES,
                 max_terms: int = MAX_TERMS_TO_CHECK,
                 case_sensitive: bool = False,
                 check_multiword: bool = True,
                 custom_stopwords: Optional[Set[str]] = None,
                 use_cache: bool = True):
        """Initialisiert den Konsistenz-Checker.
        
        Args:
            min_term_length: Minimale Zeichenlänge für Terme
            min_occurrences: Minimum Vorkommen für Prüfung
            max_terms: Maximum Terme die geprüft werden
            case_sensitive: Groß-/Kleinschreibung beachten
            check_multiword: Auch Multi-Wort-Terme prüfen
            custom_stopwords: Zusätzliche Stoppwörter
            use_cache: Term-Extraktion cachen
        """
        self.min_term_length = min_term_length
        self.min_occurrences = min_occurrences
        self.max_terms = max_terms
        self.case_sensitive = case_sensitive
        self.check_multiword = check_multiword
        self.use_cache = use_cache
        self.stopwords = STOPWORDS.copy()
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)
    
    @classmethod
    def clear_cache(cls):
        """Leert den Term-Extraktions-Cache."""
        cls._term_cache.clear()
        _logger.debug("Term cache cleared (hits: %d, misses: %d)", cls._cache_hits, cls._cache_misses)
        cls._cache_hits = 0
        cls._cache_misses = 0
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Gibt Cache-Statistiken zurück."""
        return {
            'size': len(cls._term_cache),
            'hits': cls._cache_hits,
            'misses': cls._cache_misses
        }
    
    def _normalize_term(self, term: str) -> str:
        """Normalisiert einen Term für Vergleiche."""
        if not self.case_sensitive:
            return term.lower().strip()
        return term.strip()
    
    def _is_valid_term(self, term: str) -> bool:
        """Prüft ob ein Term gültig ist für Konsistenzprüfung."""
        normalized = self._normalize_term(term)
        if len(normalized) < self.min_term_length:
            return False
        # Stoppwort-Vergleich immer case-insensitive – Stoppwörter sind lowercase
        if normalized.lower() in self.stopwords:
            return False
        # Nur Zahlen oder Sonderzeichen ausschließen
        if not any(c.isalpha() for c in normalized):
            return False
        return True
    
    def _extract_terms(self, text: str) -> List[str]:
        """Extrahiert alle relevanten Terme aus einem Text."""
        if not text:
            return []
        
        # Cache-Key basierend auf Text + ALLEN cache-relevanten Einstellungen.
        # min_term_length und stopwords beeinflussen _is_valid_term — wenn sie
        # nicht im Key stehen, liefert der class-level Cache False-Hits an
        # Instanzen mit anderer Konfiguration zurueck.
        if self.use_cache:
            sw_fp = hashlib.md5(
                ('|'.join(sorted(self.stopwords))).encode('utf-8')
            ).hexdigest()[:8]
            cache_key = (
                f"{hashlib.md5(text.encode('utf-8')).hexdigest()[:16]}:"
                f"{self.case_sensitive}:{self.check_multiword}:"
                f"{self.min_term_length}:{sw_fp}"
            )
            if cache_key in self._term_cache:
                ConsistencyChecker._cache_hits += 1
                return self._term_cache[cache_key].copy()
            ConsistencyChecker._cache_misses += 1
        
        terms = []
        
        # Einzelwörter
        for match in WORD_PATTERN.finditer(text):
            term = match.group()
            if self._is_valid_term(term):
                terms.append(self._normalize_term(term))
        
        # Multi-Wort-Terme (optional)
        if self.check_multiword:
            for match in MULTIWORD_PATTERN.finditer(text):
                term = match.group()
                # Prüfen ob alle Wörter valide sind
                words = term.split()
                if all(self._is_valid_term(w) for w in words):
                    terms.append(self._normalize_term(term))
        
        # Cache speichern (mit Größenbegrenzung)
        if self.use_cache:
            if len(self._term_cache) >= self._CACHE_MAX_ENTRIES:
                # Älteste 10 % entfernen
                evict_n = max(1, self._CACHE_MAX_ENTRIES // 10)
                for k in list(self._term_cache)[:evict_n]:
                    del self._term_cache[k]
            self._term_cache[cache_key] = terms.copy()

        return terms
    
    def _find_term_context(self, text: str, term: str, context_chars: int = 30) -> str:
        """Findet den Kontext um einen Term herum."""
        if not text or not term:
            return ""
        
        # Case-insensitive Suche
        text_lower = text.lower()
        term_lower = term.lower()
        
        pos = text_lower.find(term_lower)
        if pos == -1:
            return text[:60] + "..." if len(text) > 60 else text
        
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(term) + context_chars)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def _extract_translation_for_term(self, source: str, target: str, term: str) -> Optional[str]:
        """Versucht die Übersetzung eines Terms zu extrahieren.
        
        Einfache Heuristik: Sucht in der Übersetzung an ähnlicher Position.
        Bei komplexeren Fällen wird der gesamte Zieltext verwendet.
        """
        if not target:
            return None
        
        # Für kurze Segmente: gesamten Zieltext verwenden
        if len(target.split()) <= 5:
            return target.strip()
        
        # Versuche Position im Quelltext zu finden
        source_lower = source.lower()
        term_lower = term.lower()
        
        source_pos = source_lower.find(term_lower)
        if source_pos == -1:
            return target.strip()
        
        # Relative Position berechnen
        source_words = source.split()
        term_word_idx = 0
        char_count = 0
        for i, word in enumerate(source_words):
            char_count += len(word) + 1
            if char_count > source_pos:
                term_word_idx = i
                break
        
        # Ähnliche Position im Zieltext
        target_words = target.split()
        if not target_words:
            return target.strip()
        
        # Extrahiere Wörter um die geschätzte Position
        start_idx = max(0, term_word_idx - 1)
        end_idx = min(len(target_words), term_word_idx + 3)
        
        extracted = ' '.join(target_words[start_idx:end_idx])
        return extracted.strip() if extracted else target.strip()
    
    def _are_similar_translations(self, trans1: str, trans2: str, threshold: float = 0.7) -> bool:
        """Prüft ob zwei Übersetzungen ähnlich genug sind um als gleich zu gelten.
        
        Verwendet Wort-basierte Jaccard-Ähnlichkeit.
        """
        if not trans1 or not trans2:
            return False
        
        # Normalisieren – Groß-/Kleinschreibung nur ignorieren wenn case_sensitive=False
        if self.case_sensitive:
            words1 = set(w for w in WORD_PATTERN.findall(trans1) if len(w) >= 2)
            words2 = set(w for w in WORD_PATTERN.findall(trans2) if len(w) >= 2)
            if not words1 or not words2:
                return trans1.strip() == trans2.strip()
        else:
            words1 = set(w.lower() for w in WORD_PATTERN.findall(trans1) if len(w) >= 2)
            words2 = set(w.lower() for w in WORD_PATTERN.findall(trans2) if len(w) >= 2)
            if not words1 or not words2:
                return trans1.lower().strip() == trans2.lower().strip()
        
        # Jaccard-Ähnlichkeit
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return False
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def _group_similar_translations(self, translations: Dict[str, List[TermOccurrence]]) -> Dict[str, List[TermOccurrence]]:
        """Gruppiert ähnliche Übersetzungen zusammen."""
        if len(translations) <= 1:
            return translations
        
        # Sortiere nach Häufigkeit (häufigste zuerst)
        sorted_trans = sorted(translations.items(), key=lambda x: len(x[1]), reverse=True)
        
        grouped: Dict[str, List[TermOccurrence]] = {}
        used = set()
        
        for trans, occs in sorted_trans:
            if trans in used:
                continue
            
            # Diese Übersetzung wird zur Gruppe
            grouped[trans] = list(occs)
            used.add(trans)
            
            # Finde ähnliche und füge sie hinzu
            for other_trans, other_occs in sorted_trans:
                if other_trans in used:
                    continue
                if self._are_similar_translations(trans, other_trans):
                    grouped[trans].extend(other_occs)
                    used.add(other_trans)
        
        return grouped

    def analyze(self, pairs: Iterable[Tuple[str, str]], 
                pair_infos: Optional[List[Dict[str, Any]]] = None) -> List[ConsistencyFinding]:
        """Analysiert Segment-Paare auf Konsistenz.
        
        Args:
            pairs: Iterable von (source, target) Tuples
            pair_infos: Optionale Metadaten pro Paar
            
        Returns:
            Liste von ConsistencyFinding Objekten
        """
        all_pairs = list(pairs)
        if not all_pairs:
            return []
        
        # Term -> Liste von Vorkommen
        term_occurrences: Dict[str, List[TermOccurrence]] = defaultdict(list)
        
        # Schritt 1: Alle Terme aus Quelltexten sammeln
        for idx, (src, tgt) in enumerate(all_pairs):
            if not src:
                continue
            
            terms = self._extract_terms(src)
            
            for term in terms:
                occurrence = TermOccurrence(
                    segment_index=idx,
                    source_text=src,
                    target_text=tgt or "",
                    source_context=self._find_term_context(src, term),
                    target_context=self._find_term_context(tgt, term) if tgt else ""
                )
                term_occurrences[term].append(occurrence)
        
        # Schritt 2: Filtern auf Terme mit genug Vorkommen
        frequent_terms = {
            term: occs for term, occs in term_occurrences.items()
            if len(occs) >= self.min_occurrences
        }
        
        # Performance-Limit
        if len(frequent_terms) > self.max_terms:
            # Sortiere nach Häufigkeit und nimm die häufigsten
            sorted_terms = sorted(frequent_terms.items(), key=lambda x: len(x[1]), reverse=True)
            frequent_terms = dict(sorted_terms[:self.max_terms])
        
        # Schritt 3: Konsistenz prüfen
        findings: List[ConsistencyFinding] = []
        
        for term, occurrences in frequent_terms.items():
            # Übersetzungen sammeln
            translations: Dict[str, List[TermOccurrence]] = defaultdict(list)
            
            for occ in occurrences:
                if not occ.target_text:
                    continue
                
                # Extrahiere die vermutliche Übersetzung
                translation = self._extract_translation_for_term(
                    occ.source_text, occ.target_text, term
                )
                
                if translation:
                    # Normalisieren für Vergleich
                    trans_normalized = self._normalize_term(translation)
                    translations[trans_normalized].append(occ)
            
            # Gruppiere ähnliche Übersetzungen zusammen
            grouped_translations = self._group_similar_translations(translations)
            
            # Inkonsistenz wenn mehr als eine Übersetzungsvariante
            if len(grouped_translations) > 1:
                # Sortiere nach Häufigkeit
                sorted_translations = sorted(
                    grouped_translations.items(), 
                    key=lambda x: len(x[1]), 
                    reverse=True
                )
                
                # Häufigste Übersetzung als "Standard"
                main_translation = sorted_translations[0][0]
                main_count = len(sorted_translations[0][1])
                
                # Sammle alle Varianten
                all_variants = [t for t, _ in sorted_translations]
                all_indices = []
                all_occurrences = []
                
                for trans, occs in sorted_translations:
                    for occ in occs:
                        all_indices.append(occ.segment_index)
                        all_occurrences.append(occ)
                
                # Schweregrad basierend auf Varianten-Anzahl
                severity = 'major' if len(grouped_translations) >= 3 else 'minor'
                
                # Nachricht erstellen
                variant_count = len(grouped_translations)
                total_occurrences = sum(len(occs) for occs in grouped_translations.values())
                
                message = (
                    f"Inkonsistente Übersetzung: '{term}' hat {variant_count} "
                    f"verschiedene Übersetzungen ({total_occurrences} Vorkommen). "
                    f"Häufigste: '{main_translation}' ({main_count}x)"
                )
                
                finding = ConsistencyFinding(
                    rule_id='CONSISTENCY_TERM_VARIANT',
                    severity=severity,
                    message=message,
                    source_term=term,
                    translations=all_variants,
                    segment_indices=sorted(set(all_indices)),
                    occurrences=all_occurrences
                )
                findings.append(finding)
        
        # Sortiere nach Schweregrad und Term
        findings.sort(key=lambda f: (0 if f.severity == 'major' else 1, f.source_term))
        
        return findings
    
    def analyze_to_dicts(self, pairs: Iterable[Tuple[str, str]],
                         pair_infos: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Analysiert und gibt Ergebnisse als Dicts zurück."""
        findings = self.analyze(pairs, pair_infos)
        return [f.to_dict() for f in findings]


def run_consistency_check(pairs: Iterable[Tuple[str, str]],
                          min_term_length: int = MIN_TERM_LENGTH,
                          min_occurrences: int = MIN_TERM_OCCURRENCES,
                          case_sensitive: bool = False,
                          check_multiword: bool = True) -> List[Dict[str, Any]]:
    """Führt Konsistenzprüfung durch.
    
    Args:
        pairs: Iterable von (source, target) Tuples
        min_term_length: Minimale Termlänge
        min_occurrences: Minimum Vorkommen für Prüfung
        case_sensitive: Groß-/Kleinschreibung beachten
        check_multiword: Auch Multi-Wort-Terme prüfen
        
    Returns:
        Liste von Finding-Dicts
    """
    checker = ConsistencyChecker(
        min_term_length=min_term_length,
        min_occurrences=min_occurrences,
        case_sensitive=case_sensitive,
        check_multiword=check_multiword
    )
    return checker.analyze_to_dicts(pairs)


# Für QAIssue-Kompatibilität
def check_consistency_as_issues(pairs: Iterable[Tuple[str, str]],
                                 **kwargs) -> List[Any]:
    """Führt Konsistenzprüfung durch und gibt QAIssue-Objekte zurück."""
    try:
        from quality_gui_phase1_checkers import QAIssue
    except ImportError:
        from dataclasses import dataclass, field
        @dataclass
        class QAIssue:
            code: str
            severity: str
            category: str
            message: str
            source_text: str
            target_text: str
            segment_index: int = -1
            meta: dict = field(default_factory=dict)
    
    checker = ConsistencyChecker(**kwargs)
    findings = checker.analyze(pairs)
    
    issues = []
    for f in findings:
        # Verwende erstes Segment als Beispiel
        if f.occurrences:
            src = f.occurrences[0].source_text
            tgt = f.occurrences[0].target_text
        else:
            src = tgt = ""
        
        first_segment_idx = f.segment_indices[0] if f.segment_indices else -1
        
        issues.append(QAIssue(
            code=f.rule_id,
            severity=f.severity,
            category='consistency',
            message=f.message,
            source_text=src,
            target_text=tgt,
            segment_index=first_segment_idx,
            meta={
                'source_term': f.source_term,
                'translations': f.translations,
                'segment_indices': f.segment_indices,
                'variant_count': len(f.translations),
            }
        ))
    
    return issues


# Export
__all__ = [
    'ConsistencyChecker',
    'ConsistencyFinding',
    'TermOccurrence',
    'run_consistency_check',
    'check_consistency_as_issues',
    'STOPWORDS',
    'MIN_TERM_LENGTH',
    'MIN_TERM_OCCURRENCES',
    'MAX_TERMS_TO_CHECK',
]
