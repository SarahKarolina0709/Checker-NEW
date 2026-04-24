"""quality_gui_ocr_checker – OCR-spezifische Fehlerprüfung.

Erkennt häufige OCR-Fehler die durch optische Zeichenerkennung entstehen:
- l/1 Verwechslung (Kleinbuchstabe L vs. Ziffer 1)
- O/0 Verwechslung (Großbuchstabe O vs. Ziffer 0)
- rn/m Verwechslung (rn sieht aus wie m)
- cl/d Verwechslung
- vv/w Verwechslung
- Doppelte/fehlende Buchstaben
- Häufige Ligatur-Probleme (fi, fl, ff)

Ergebnis-Einträge (Finding Dict):
{
  'rule_id': 'OCR_*',
  'severity': 'minor'|'major',
  'message': str,
  'source_excerpt': str,
  'target_excerpt': str,
  'segment_index': int,
  'category': 'ocr'
}
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Set, Any, Optional, Iterable
from dataclasses import dataclass, field
import re

# ============================================================================
# OCR-Verwechslungspaare (visuell ähnliche Zeichen)
# ============================================================================

# Zeichen die häufig verwechselt werden
OCR_CONFUSABLES = {
    # Ziffer/Buchstabe Verwechslungen
    ('l', '1'),  # Kleinbuchstabe L vs. Eins
    ('I', '1'),  # Großbuchstabe I vs. Eins
    ('O', '0'),  # Großbuchstabe O vs. Null
    ('o', '0'),  # Manchmal auch Kleinbuchstabe
    ('S', '5'),  # S vs. 5
    ('B', '8'),  # B vs. 8
    ('G', '6'),  # G vs. 6
    ('Z', '2'),  # Z vs. 2
    
    # Buchstaben-Verwechslungen
    ('rn', 'm'),  # rn sieht aus wie m
    ('cl', 'd'),  # cl sieht aus wie d
    ('vv', 'w'),  # vv sieht aus wie w
    ('nn', 'm'),  # nn kann wie m aussehen
    ('ii', 'u'),  # ii kann wie u aussehen
    ('ri', 'n'),  # ri kann wie n aussehen
    ('li', 'h'),  # li kann wie h aussehen
    
    # Interpunktion
    ('.', ','),   # Punkt vs. Komma
    ("'", '`'),   # Apostroph-Varianten
    ('"', "''"),  # Anführungszeichen
    ('-', '–'),   # Bindestrich vs. Gedankenstrich
}

# Ligatur-Probleme (werden manchmal nicht erkannt oder falsch aufgelöst)
LIGATURE_ISSUES = {
    'fi': ['fi', 'ﬁ'],
    'fl': ['fl', 'ﬂ'],
    'ff': ['ff', 'ﬀ'],
    'ffi': ['ffi', 'ﬃ'],
    'ffl': ['ffl', 'ﬄ'],
}

# Wörter die häufig durch OCR-Fehler entstehen
OCR_ERROR_PATTERNS = [
    # Pattern, korrekter Wert, Beschreibung
    (r'\brn(?=[aeiou])', 'm', "rn->m vor Vokal"),
    (r'\b1(?=[a-z]{2,})', 'l', "1 am Wortanfang (sollte l sein)"),
    (r'(?<=[a-z])1(?=[a-z])', 'l', "1 zwischen Buchstaben"),
    (r'\b0(?=[a-z]{2,})', 'O', "0 am Wortanfang (sollte O sein)"),
    (r'(?<=[A-Z])0(?=[A-Z])', 'O', "0 zwischen Großbuchstaben"),
    (r'(?<=[a-z])0(?=[a-z])', 'o', "0 zwischen Kleinbuchstaben"),
    (r'c1(?=[aeiou])', 'cl/d', "c1 könnte cl oder d sein"),
    (r'vv', 'w', "vv sollte w sein"),
]

# Bekannte OCR-Fehlerwörter (falsch -> korrekt)
KNOWN_OCR_ERRORS = {
    # Deutsch
    'rnit': 'mit',
    'dern': 'dem',
    'seirn': 'sein',
    'beirn': 'beim',
    'vvird': 'wird',
    'vvir': 'wir',
    'vvas': 'was',
    'vvenn': 'wenn',
    'vvie': 'wie',
    'vvo': 'wo',
    'vveil': 'weil',
    'vvaren': 'waren',
    'vvurde': 'wurde',
    'lch': 'Ich',
    'ln': 'In',
    'lhr': 'Ihr',
    'lhre': 'Ihre',
    'lhnen': 'Ihnen',
    'lst': 'Ist',
    'lm': 'Im',
    'clas': 'das',
    'uncl': 'und',
    'sincl': 'sind',
    'wircl': 'wird',
    'Hancl': 'Hand',
    'Lancl': 'Land',
    # Englisch
    'rnake': 'make',
    'rnay': 'may',
    'rnore': 'more',
    'rnust': 'must',
    'tirne': 'time',
    'narne': 'name',
    'sarne': 'same',
    'corne': 'come',
    'horne': 'home',
    'sorne': 'some',
    'frorn': 'from',
    'thern': 'them',
    'systern': 'system',
    'problern': 'problem',
    'l\'m': "I'm",
    'l\'ll': "I'll",
    'l\'ve': "I've",
    'lt': 'It',
    'lf': 'If',
    'ls': 'Is',
    'ln': 'In',
}

# Regex für Wort-Extraktion (unicode-sicher)
WORD_PATTERN = re.compile(r"\b[A-Za-z\u00C0-\u017F][A-Za-z\u00C0-\u017F'\-]*\b")


@dataclass
class OCRFinding:
    """Ein OCR-Fehler-Finding."""
    rule_id: str
    severity: str  # 'minor' oder 'major'
    message: str
    source_excerpt: str
    target_excerpt: str
    segment_index: int
    error_type: str  # 'confusable', 'ligature', 'pattern', 'known_error'
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'severity': self.severity,
            'message': self.message,
            'source_excerpt': self.source_excerpt,
            'target_excerpt': self.target_excerpt,
            'segment_index': self.segment_index,
            'category': 'ocr',
            'meta': {
                'error_type': self.error_type,
                'suggestion': self.suggestion,
            }
        }


class OCRChecker:
    """Prüft auf häufige OCR-Fehler in Übersetzungen.
    
    Vergleicht Quell- und Zieltexte und findet Muster die auf
    OCR-Fehler hindeuten.
    """
    
    def __init__(self,
                 check_known_errors: bool = True,
                 check_patterns: bool = True,
                 check_confusables: bool = True,
                 min_word_length: int = 2,
                 custom_errors: Optional[Dict[str, str]] = None):
        """Initialisiert den OCR-Checker.
        
        Args:
            check_known_errors: Bekannte OCR-Fehlerwörter prüfen
            check_patterns: Regex-Pattern für OCR-Fehler prüfen
            check_confusables: Verwechselbare Zeichen prüfen
            min_word_length: Mindestlänge für Wortprüfung
            custom_errors: Zusätzliche bekannte Fehler {falsch: richtig}
        """
        self.check_known_errors = check_known_errors
        self.check_patterns = check_patterns
        self.check_confusables = check_confusables
        self.min_word_length = min_word_length
        
        # Bekannte Fehler zusammenführen
        self.known_errors = KNOWN_OCR_ERRORS.copy()
        if custom_errors:
            self.known_errors.update(custom_errors)
        
        # Kompilierte Pattern
        self.compiled_patterns = []
        for pattern, correction, desc in OCR_ERROR_PATTERNS:
            try:
                self.compiled_patterns.append((re.compile(pattern), correction, desc))
            except re.error:
                pass
    
    def _extract_words(self, text: str) -> List[str]:
        """Extrahiert Wörter aus Text."""
        if not text:
            return []
        return [w for w in WORD_PATTERN.findall(text) if len(w) >= self.min_word_length]
    
    def _check_known_error(self, word: str) -> Optional[Tuple[str, str]]:
        """Prüft ob ein Wort ein bekannter OCR-Fehler ist.
        
        Returns:
            Tuple (korrektes_wort, beschreibung) oder None
        """
        # Exakter Match
        if word in self.known_errors:
            return (self.known_errors[word], f"'{word}' → '{self.known_errors[word]}'")
        
        # Lowercase Match
        word_lower = word.lower()
        if word_lower in self.known_errors:
            correction = self.known_errors[word_lower]
            # Großschreibung beibehalten wenn nötig
            if word[0].isupper():
                correction = correction[0].upper() + correction[1:]
            return (correction, f"'{word}' → '{correction}'")
        
        return None
    
    def _check_patterns(self, text: str) -> List[Tuple[str, str, str]]:
        """Prüft Text auf OCR-Fehler-Pattern.
        
        Returns:
            Liste von (gefunden, korrektur, beschreibung) Tuples
        """
        findings = []
        for pattern, correction, desc in self.compiled_patterns:
            for match in pattern.finditer(text):
                found = match.group()
                findings.append((found, correction, desc))
        return findings
    
    def _check_confusable_pairs(self, source: str, target: str) -> List[Tuple[str, str, str]]:
        """Prüft auf verwechselbare Zeichen zwischen Quelle und Ziel.
        
        Sucht nach Fällen wo ein Zeichen in der Quelle durch ein
        visuell ähnliches in der Übersetzung ersetzt wurde.
        
        Returns:
            Liste von (gefunden, erwartet, beschreibung) Tuples
        """
        findings = []
        
        # Extrahiere Wörter aus beiden Texten
        source_words = set(self._extract_words(source))
        target_words = self._extract_words(target)
        
        for target_word in target_words:
            # Prüfe ob Wort verdächtige Zeichen enthält
            for char1, char2 in OCR_CONFUSABLES:
                if char1 in target_word or char2 in target_word:
                    # Erstelle mögliche Korrekturen
                    if char1 in target_word:
                        corrected = target_word.replace(char1, char2)
                        if corrected in source_words or corrected.lower() in {w.lower() for w in source_words}:
                            findings.append((
                                target_word, 
                                corrected, 
                                f"OCR-Verwechslung: '{char1}'→'{char2}'"
                            ))
                    if char2 in target_word:
                        corrected = target_word.replace(char2, char1)
                        if corrected in source_words or corrected.lower() in {w.lower() for w in source_words}:
                            findings.append((
                                target_word, 
                                corrected, 
                                f"OCR-Verwechslung: '{char2}'→'{char1}'"
                            ))
        
        return findings
    
    def _find_context(self, text: str, word: str, context_chars: int = 25) -> str:
        """Findet den Kontext um ein Wort herum."""
        if not text or not word:
            return text[:50] if text else ""
        
        pos = text.find(word)
        if pos == -1:
            pos = text.lower().find(word.lower())
        if pos == -1:
            return text[:50]
        
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(word) + context_chars)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def analyze_segment(self, source: str, target: str, segment_index: int) -> List[OCRFinding]:
        """Analysiert ein einzelnes Segment auf OCR-Fehler.
        
        Args:
            source: Quelltext
            target: Zieltext (Übersetzung)
            segment_index: Index des Segments
            
        Returns:
            Liste von OCRFinding Objekten
        """
        findings: List[OCRFinding] = []
        
        if not target:
            return findings
        
        # 1. Bekannte OCR-Fehler prüfen
        if self.check_known_errors:
            target_words = self._extract_words(target)
            for word in target_words:
                result = self._check_known_error(word)
                if result:
                    correction, desc = result
                    findings.append(OCRFinding(
                        rule_id='OCR_KNOWN_ERROR',
                        severity='major',
                        message=f"Bekannter OCR-Fehler: {desc}",
                        source_excerpt=self._find_context(source, correction),
                        target_excerpt=self._find_context(target, word),
                        segment_index=segment_index,
                        error_type='known_error',
                        suggestion=correction
                    ))
        
        # 2. OCR-Pattern prüfen
        if self.check_patterns:
            pattern_findings = self._check_patterns(target)
            for found, correction, desc in pattern_findings:
                findings.append(OCRFinding(
                    rule_id='OCR_PATTERN',
                    severity='minor',
                    message=f"Möglicher OCR-Fehler: {desc} ('{found}')",
                    source_excerpt=self._find_context(source, found),
                    target_excerpt=self._find_context(target, found),
                    segment_index=segment_index,
                    error_type='pattern',
                    suggestion=correction
                ))
        
        # 3. Verwechselbare Zeichen zwischen Quelle und Ziel
        if self.check_confusables and source:
            confusable_findings = self._check_confusable_pairs(source, target)
            for found, expected, desc in confusable_findings:
                findings.append(OCRFinding(
                    rule_id='OCR_CONFUSABLE',
                    severity='minor',
                    message=f"{desc}: '{found}' sollte '{expected}' sein",
                    source_excerpt=self._find_context(source, expected),
                    target_excerpt=self._find_context(target, found),
                    segment_index=segment_index,
                    error_type='confusable',
                    suggestion=expected
                ))
        
        return findings
    
    def analyze(self, pairs: Iterable[Tuple[str, str]]) -> List[OCRFinding]:
        """Analysiert alle Segment-Paare auf OCR-Fehler.
        
        Args:
            pairs: Iterable von (source, target) Tuples
            
        Returns:
            Liste von OCRFinding Objekten
        """
        all_findings: List[OCRFinding] = []
        
        for idx, (src, tgt) in enumerate(pairs):
            segment_findings = self.analyze_segment(src, tgt, idx)
            all_findings.extend(segment_findings)
        
        # Sortiere nach Schweregrad und Segment
        all_findings.sort(key=lambda f: (0 if f.severity == 'major' else 1, f.segment_index))
        
        return all_findings
    
    def analyze_to_dicts(self, pairs: Iterable[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Analysiert und gibt Ergebnisse als Dicts zurück."""
        findings = self.analyze(pairs)
        return [f.to_dict() for f in findings]


def run_ocr_check(pairs: Iterable[Tuple[str, str]],
                  check_known_errors: bool = True,
                  check_patterns: bool = True,
                  check_confusables: bool = True) -> List[Dict[str, Any]]:
    """Führt OCR-Fehlerprüfung durch.
    
    Args:
        pairs: Iterable von (source, target) Tuples
        check_known_errors: Bekannte Fehlerwörter prüfen
        check_patterns: Pattern-basierte Prüfung
        check_confusables: Verwechselbare Zeichen prüfen
        
    Returns:
        Liste von Finding-Dicts
    """
    checker = OCRChecker(
        check_known_errors=check_known_errors,
        check_patterns=check_patterns,
        check_confusables=check_confusables
    )
    return checker.analyze_to_dicts(pairs)


# Für QAIssue-Kompatibilität
def check_ocr_as_issues(pairs: Iterable[Tuple[str, str]], **kwargs) -> List[Any]:
    """Führt OCR-Prüfung durch und gibt QAIssue-Objekte zurück."""
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
            meta: dict = field(default_factory=dict)
    
    checker = OCRChecker(**kwargs)
    findings = checker.analyze(pairs)
    
    issues = []
    for f in findings:
        issues.append(QAIssue(
            code=f.rule_id,
            severity=f.severity,
            category='ocr',
            message=f.message,
            source_text=f.source_excerpt,
            target_text=f.target_excerpt,
            meta={
                'segment_index': f.segment_index,
                'error_type': f.error_type,
                'suggestion': f.suggestion,
            }
        ))
    
    return issues
