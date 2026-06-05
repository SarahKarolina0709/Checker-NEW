"""quality_gui_phase1_checkers – umbenanntes Modul (ehemals qa_phase1_checkers).

Funktionalität: URLs/E-Mails, Whitespace, Klammern, Quotes.
Platzhalter-Prüfung wurde entfernt (zu viele False Positives).
"""
from __future__ import annotations

import re
import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Iterable, Optional

_logger = logging.getLogger(__name__)

@dataclass
class QAIssue:
    code: str
    severity: str
    category: str
    message: str
    source_text: str
    target_text: str
    segment_index: int = -1  # NEU: Segment-Index für UI-Report
    source_file: str = ''  # Datei-Pfad oder -Name (Per-File-Attribution)
    target_file: str = ''
    meta: Dict[str, object] = field(default_factory=dict)

# --- Patterns für URLs, E-Mails, Whitespace ---
# URL-Pattern: großzügig matchen, dann smart trimmen
URL_PATTERN = re.compile(
    r"https?://[\w.-]+(?:[/~\w\-./;?%&=+#()]*)",
    re.IGNORECASE
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# MAILTO: Non-capturing für kompletten Match
MAILTO_URL_PATTERN = re.compile(r"mailto:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s+[^>]*?)?>")
# Zero-width + NBSP (\u00A0) + NNBSP (\u202F) + FIGURE SPACE (\u2007)
ZERO_WIDTH_PATTERN = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF\u00A0\u202F\u2007]")
# Französische NBSP-Muster (einzelne Treffer, nicht global)
FRENCH_NBSP_PATTERN = re.compile(r"[\u00A0\u202F](?=[:;!?\u00BB])|(?<=\u00AB)[\u00A0\u202F]")
DUP_SPACE_PATTERN = re.compile(r" {2,}")
TRAIL_SPACE_PATTERN = re.compile(r"[ \t]+$", re.MULTILINE)
LEAD_SPACE_PATTERN = re.compile(r"^[ \t]+", re.MULTILINE)

# GEÄNDERT: < > entfernt - zu viele False Positives bei "x < y" oder "<10%" in Tech-Texten
BRACKET_PAIRS = {"(":")", "[":"]", "{":"}"}
OPENING = set(BRACKET_PAIRS.keys())
CLOSING = set(BRACKET_PAIRS.values())

# Aufzählungsmuster (a), b), 1), ii) etc.) – einmalig kompiliert statt pro Aufruf
_ENUMERATION_PATTERN = re.compile(r'(?:^|[\s(])([a-zA-Z]|[ivxIVX]+|\d+)\)(?=[\s,;:\.\-]|$)')

GERMAN_QUOTE_OPEN  = '„'
# Deutsche Quotes: mehrere schließende Varianten (typografisch korrekt + häufige Mischungen)
GERMAN_QUOTE_CLOSE_VARIANTS = ['"', '\u201C', '\u201D']  # ASCII U+0022, U+201C, U+201D
DE_QUOTES = [('„', '"'), ('„', '"'), ('\u201A', '\u2018'), ('«', '»'), ('»', '«')]  # DE + FR Varianten

# Steuerzeichen-Tabelle – einmalig aufgebaut, nicht pro Aufruf
_CONTROL_CHARS: tuple = (
    ('\u0000', 'NULL'), ('\u0001', 'SOH'), ('\u0002', 'STX'),
    ('\u0003', 'ETX'), ('\u0004', 'EOT'), ('\u0005', 'ENQ'),
    ('\u0006', 'ACK'), ('\u0007', 'BEL'), ('\u0008', 'BS'),
    ('\u000B', 'VT'),  ('\u000C', 'FF'),  ('\u000E', 'SO'),
    ('\u000F', 'SI'),
)

# Apostroph-Muster für _count_quotes_safely – einmalig kompiliert
_RE_APOSTROPHE_INWORD      = re.compile(r"(?<=\w)'(?=\w)")        # don't, l'école
_RE_APOSTROPHE_POSSESSIVE  = re.compile(r"(?<=\w)'(?=s\b)")       # John's
_RE_APOSTROPHE_PLURAL      = re.compile(r"(?<=s)'(?=\s|$|[.,;:!?])")  # students'

def _smart_trim_url(url: str) -> str:
    """Trimmt URL-Ende intelligent - behält balancierte Klammern.
    
    Entfernt typische Satzzeichen am Ende, aber nur wenn sie nicht
    zu einer balancierten Klammer gehören (wichtig für Wikipedia-URLs etc.).
    """
    if not url:
        return url
    # Trim-Kandidaten am Ende
    while url and url[-1] in ').,;:!?':
        ch = url[-1]
        if ch == ')':
            # Klammer-Balance prüfen: wenn mehr ( als ) → ) behalten
            open_count = url.count('(')
            close_count = url.count(')')
            if open_count >= close_count:
                break  # ) ist Teil der URL (z.B. Wikipedia)
        url = url[:-1]
    return url


def extract_urls(text: str) -> List[str]:
    """Extrahiert URLs und mailto:-Links mit smartem Trimming."""
    t = text or ""
    # Normale URLs
    raw_urls = URL_PATTERN.findall(t)
    # Smart trimmen
    urls = [_smart_trim_url(u) for u in raw_urls if u]
    # mailto: URLs via finditer für kompletten Match
    for m in MAILTO_URL_PATTERN.finditer(t):
        urls.append(m.group(0))
    # Deduplizieren (Reihenfolge beibehalten, Leere entfernen)
    seen: dict[str, None] = {}
    for u in urls:
        if u:
            seen[u] = None
    return list(seen)

def extract_emails(text: str) -> List[str]:
    return EMAIL_PATTERN.findall(text or "")

def extract_zero_width(text: str) -> List[str]:
    return ZERO_WIDTH_PATTERN.findall(text or "")

def _strip_html_tags(text: str) -> str:
    try:
        return HTML_TAG_PATTERN.sub('', text or '')
    except Exception:
        return text or ''

def _diff_list_multiset(src_vals: List[str], tgt_vals: List[str]) -> tuple[List[str], List[str]]:
    cs, ct = Counter(src_vals), Counter(tgt_vals)
    missing = list((cs - ct).elements())
    extra = list((ct - cs).elements())
    return missing, extra

def check_urls_emails(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Prüft URLs und E-Mails auf Übereinstimmung."""
    issues: List[QAIssue] = []
    s_urls, t_urls = extract_urls(src), extract_urls(tgt)
    # Erst URLs prüfen
    for label, vals_src, vals_tgt, miss_code, extra_code in (
        ("URL", s_urls, t_urls, "URL_MISSING", "URL_EXTRA"),
    ):
        s_vals, t_vals = vals_src, vals_tgt
        miss, extra = _diff_list_multiset(s_vals, t_vals)
        if miss:
            issues.append(QAIssue(miss_code, "critical", "references", f"{label}s fehlen: {miss}", src, tgt, segment_index, {"source": s_vals, "target": t_vals}))
        if extra:
            issues.append(QAIssue(extra_code, "major", "references", f"{label}s zusätzlich: {extra}", src, tgt, segment_index, {"source": s_vals, "target": t_vals}))
        if not miss and not extra and s_vals != t_vals:
            issues.append(QAIssue(f"{label.upper()}_ORDER", "minor", "references", f"{label}-Reihenfolge weicht ab", src, tgt, segment_index, {"source": s_vals, "target": t_vals}))
    # Dann E-Mails prüfen, aber solche aus mailto: nicht doppelt zählen
    s_eml, t_eml = extract_emails(src), extract_emails(tgt)
    def strip_mailto(emails: List[str], urls: List[str]) -> List[str]:
        # KORRIGIERT: Prüft ob E-Mail in irgendeiner mailto: URL enthalten ist
        mailto_emails = set()
        for url in urls:
            if url.lower().startswith('mailto:'):
                mailto_emails.add(url[7:].lower())  # E-Mail-Teil extrahieren
        return [e for e in emails if e.lower() not in mailto_emails]
    s_eml = strip_mailto(s_eml, s_urls + t_urls)
    t_eml = strip_mailto(t_eml, s_urls + t_urls)
    miss, extra = _diff_list_multiset(s_eml, t_eml)
    if miss:
        issues.append(QAIssue("EMAIL_MISSING", "critical", "references", f"E-Mails fehlen: {miss}", src, tgt, segment_index, {"source": s_eml, "target": t_eml}))
    if extra:
        issues.append(QAIssue("EMAIL_EXTRA", "major", "references", f"E-Mails zusätzlich: {extra}", src, tgt, segment_index, {"source": s_eml, "target": t_eml}))
    if not miss and not extra and s_eml != t_eml:
        issues.append(QAIssue("EMAIL_ORDER", "minor", "references", "E-Mail-Reihenfolge weicht ab", src, tgt, segment_index, {"source": s_eml, "target": t_eml}))
    return issues

def check_whitespace_and_zero_width(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Prüft Whitespace und unsichtbare Zeichen mit verbesserter NBSP-Erkennung."""
    issues: List[QAIssue] = []
    for label, text in (("source", src), ("target", tgt)):
        if DUP_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_DOUBLE_SPACE", "minor", "whitespace", f"Doppelte Leerzeichen in {label}", src, tgt, segment_index))
        if TRAIL_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_TRAILING", "minor", "whitespace", f"Trailing Whitespace in {label}", src, tgt, segment_index))
        if LEAD_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_LEADING", "minor", "whitespace", f"Führende Leerzeichen in {label}", src, tgt, segment_index))
        zw = extract_zero_width(text)
        if zw:
            # VERBESSERT: Nur NBSP/NNBSP ignorieren die IN französischen Mustern vorkommen
            french_nbsp_positions = set()
            for m in FRENCH_NBSP_PATTERN.finditer(text):
                french_nbsp_positions.add(m.start())
            
            names = []
            for i, ch in enumerate(text):
                if ch not in "\u00A0\u202F\u200B\u200C\u200D\u2060\uFEFF\u2007":
                    continue
                # Überspringe nur NBSP/NNBSP an französischen Positionen
                if ch in "\u00A0\u202F" and i in french_nbsp_positions:
                    continue
                    
                if ch == "\u00A0":
                    names.append("NBSP(\\u00A0)")
                elif ch == "\u202F":
                    names.append("NNBSP(\\u202F)")
                elif ch == "\u200B":
                    names.append("ZWSP(\\u200B)")
                elif ch == "\u200C":
                    names.append("ZWNJ(\\u200C)")
                elif ch == "\u200D":
                    names.append("ZWJ(\\u200D)")
                elif ch == "\u2060":
                    names.append("WJ(\\u2060)")
                elif ch == "\uFEFF":
                    names.append("BOM/ZWNBSP(\\uFEFF)")
                elif ch == "\u2007":
                    names.append("FIGURE SPACE(\\u2007)")
                else:
                    names.append(f"U+{ord(ch):04X}")
            # Deduplizieren und melden
            unique_names = list(dict.fromkeys(names))  # Erhält Reihenfolge
            if unique_names:
                issues.append(QAIssue("ZERO_WIDTH_CHAR", "minor", "whitespace", 
                    f"Unsichtbare/geschützte Zeichen in {label}: {unique_names}", src, tgt, segment_index, {"chars": zw}))
    return issues

def check_brackets_basic(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Prüft Klammer-Balance, ignoriert Aufzählungen wie a), b), c), 1), 2) etc.
    
    VERBESSERT: Sammelt bis zu 3 Issues pro Text statt beim ersten abzubrechen.
    """
    issues: List[QAIssue] = []
    MAX_ISSUES_PER_TEXT = 3
    
    for label, raw in (("source", src), ("target", tgt)):
        text = _strip_html_tags(raw)

        # Entferne Aufzählungen vor der Klammer-Prüfung (verwendet vorcompiliertes Modul-Pattern)
        text_cleaned = _ENUMERATION_PATTERN.sub(r' \1 ', text)
        
        stack: List[str] = []
        issue_count = 0
        for ch in text_cleaned:
            if issue_count >= MAX_ISSUES_PER_TEXT:
                break
            if ch in OPENING:
                stack.append(ch)
            elif ch in CLOSING:
                if not stack:
                    issues.append(QAIssue("BRACKET_UNBALANCED", "minor", "structure", 
                        f"Ungepaarte Klammer '{ch}' in {'Ausgangstext' if label == 'source' else 'Übersetzung'}", src, tgt, segment_index))
                    issue_count += 1
                    continue  # Weiter sammeln statt break
                op = stack.pop()
                if BRACKET_PAIRS[op] != ch:
                    issues.append(QAIssue("BRACKET_MISMATCH", "minor", "structure", 
                        f"Klammer-Typ stimmt nicht überein: '{op}' geöffnet, '{ch}' geschlossen", src, tgt, segment_index))
                    issue_count += 1
        # Offene Klammern am Ende
        if stack and issue_count < MAX_ISSUES_PER_TEXT:
            unclosed = ', '.join(f"'{b}'" for b in stack[:3])  # Max 3 zeigen
            issues.append(QAIssue("BRACKET_UNCLOSED", "minor", "structure", 
                f"Offene Klammer(n) nicht geschlossen: {unclosed}", src, tgt, segment_index))
    return issues

def _count_quotes_safely(t: str) -> tuple[int,int]:
    """Zählt Anführungszeichen mit Apostroph-Normalisierung.
    
    VERBESSERT: Normalisiert typografische Apostrophe ' (U+2019) → ' vor dem Zählen.
    """
    t = _strip_html_tags(t or "")
    # VERBESSERT: Typografische Apostrophe normalisieren
    t = t.replace('\u2019', "'")  # ' → '
    t = t.replace('\u2018', "'")  # ' → '
    # Deutsche Anfuehrungszeichen-Paare entfernen, bevor ASCII-`"` gezaehlt wird —
    # sonst zaehlt z.B. „Hallo Welt" das `"` doppelt (als ASCII-Quote UND als
    # de_close-Variante) und produziert false-positive QUOTE_UNBALANCED.
    t_dequote = re.sub(r'„[^„"\u201C\u201D]*?["\u201C\u201D]', '', t, flags=re.DOTALL)
    # Apostrophe ignorieren:
    # 1. Innerhalb von Wörtern (don't, l'école)
    # 2. Possessiv am Ende (John's, James')
    # 3. Genitiv/Plural (the students' books)
    t_wo = _RE_APOSTROPHE_INWORD.sub("", t_dequote)
    t_wo = _RE_APOSTROPHE_POSSESSIVE.sub("", t_wo)
    t_wo = _RE_APOSTROPHE_PLURAL.sub("", t_wo)
    return t_wo.count('"'), t_wo.count("'")

def _count_german_quote_pairs(text: str) -> tuple[int, int]:
    """Pair-Matching für deutsche Quotes: zählt öffnende und schließende korrekt.

    Liefert (open_count, close_count) – ausgeglichen = kein Fehler.
    Unterschied zu simplem count(): mehrere Paare „A" und „B" werden korrekt
    als 2 öffnend / 2 schließend erkannt, nicht als Missmatch.
    """
    open_count = text.count(GERMAN_QUOTE_OPEN)
    # Schließende: alle Varianten, aber kein Doppelzählen wenn Zeichen identisch
    close_chars = set(GERMAN_QUOTE_CLOSE_VARIANTS)
    close_count = sum(text.count(c) for c in close_chars)
    return open_count, close_count


def check_quotes_basic(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Quote-Balance mit Ignorieren wortinterner Apostrophe und deutscher Quotes.
    
    Verwendet Pair-Matching für deutsche Quotes (verhindert False Positives
    bei mehreren Paaren wie „Satz 1" und „Satz 2").
    """
    issues: List[QAIssue] = []
    counts = {}
    for label, text in (("source", src), ("target", tgt)):
        dbl, sng = _count_quotes_safely(text)
        stripped = _strip_html_tags(text or "")
        de_open, de_close = _count_german_quote_pairs(stripped)
        counts[label] = {"dbl": dbl, "sng": sng, "de_open": de_open, "de_close": de_close}
        if dbl % 2 != 0:
            issues.append(QAIssue("QUOTE_UNBALANCED","minor","quotes", f'Ungerade Anzahl von " in {label}', src, tgt, segment_index))
        if sng % 2 != 0:
            issues.append(QAIssue("QUOTE_UNBALANCED","minor","quotes", f"Ungerade Anzahl von ' in {label}", src, tgt, segment_index))
        if de_open > 0 and de_open != de_close:
            issues.append(QAIssue("QUOTE_DE_MISMATCH","minor","quotes", f"Deutsche Anführungszeichen unausgeglichen in {label} (öffnend: {de_open}, schließend: {de_close})", src, tgt, segment_index, {"open": de_open, "close": de_close}))
        # Weitere typografische Varianten balancieren
        for open_q, close_q in DE_QUOTES:
            if open_q == GERMAN_QUOTE_OPEN:
                continue  # Bereits oben geprüft
            o = stripped.count(open_q)
            c = stripped.count(close_q)
            if o != c:
                issues.append(QAIssue(
                    "QUOTE_DE_MISMATCH","minor","quotes",
                    f"Typographische Anführungszeichen unausgeglichen ({open_q}{close_q}) in {label}",
                    src, tgt, segment_index, {"open": o, "close": c, "pair": (open_q, close_q)}
                ))
    # Quote-Anzahl-Mismatch zwischen src/tgt (Paare = count // 2 + de_open)
    src_pairs = counts["source"]["dbl"] // 2 + counts["source"]["de_open"]
    tgt_pairs = counts["target"]["dbl"] // 2 + counts["target"]["de_open"]
    if src_pairs != tgt_pairs:
        issues.append(QAIssue(
            "QUOTE_COUNT_MISMATCH", "major", "quotes",
            f"Anzahl Anführungszeichen-Paare unterschiedlich (Quelle: {src_pairs}, Ziel: {tgt_pairs})",
            src, tgt, segment_index, {"src_pairs": src_pairs, "tgt_pairs": tgt_pairs}
        ))
    return issues

def check_boundary_whitespace(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Prüft ob Start/Ende-Leerzeichen übernommen wurden (UI-kritisch für Buttons/Labels).
    
    VERBESSERT: Bei kurzen Strings (≤30 Zeichen, typische UI-Strings) → severity=major.
    """
    issues: List[QAIssue] = []
    src_starts = src.startswith(' ') or src.startswith('\t')
    tgt_starts = tgt.startswith(' ') or tgt.startswith('\t')
    src_ends = src.endswith(' ') or src.endswith('\t')
    tgt_ends = tgt.endswith(' ') or tgt.endswith('\t')
    
    # UI-Signal: kurze Strings sind wahrscheinlich Buttons/Labels
    is_ui_string = len(src.strip()) <= 30
    severity = "major" if is_ui_string else "minor"
    
    if src_starts and not tgt_starts:
        issues.append(QAIssue("BOUNDARY_SPACE_START_MISSING", severity, "whitespace",
                             "Führendes Leerzeichen fehlt im Ziel", src, tgt, segment_index))
    elif not src_starts and tgt_starts:
        issues.append(QAIssue("BOUNDARY_SPACE_START_ADDED", severity, "whitespace",
                             "Führendes Leerzeichen hinzugefügt", src, tgt, segment_index))
    
    if src_ends and not tgt_ends:
        issues.append(QAIssue("BOUNDARY_SPACE_END_MISSING", severity, "whitespace",
                             "Nachgestelltes Leerzeichen fehlt im Ziel", src, tgt, segment_index))
    elif not src_ends and tgt_ends:
        issues.append(QAIssue("BOUNDARY_SPACE_END_ADDED", severity, "whitespace",
                             "Nachgestelltes Leerzeichen hinzugefügt", src, tgt, segment_index))
    return issues

def check_soft_hyphens_and_control_chars(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Erkennt Soft-Hyphens und andere Steuerzeichen (oft Word-Artefakte)."""
    issues: List[QAIssue] = []
    soft_hyphen = '\u00AD'  # Soft Hyphen
    
    # Soft Hyphen prüfen
    if soft_hyphen in tgt and soft_hyphen not in src:
        count = tgt.count(soft_hyphen)
        issues.append(QAIssue("SOFT_HYPHEN_ADDED", "major", "formatting",
                             f"Soft-Hyphen eingefügt ({count}x) - meist Word-Artefakt", src, tgt, segment_index,
                             {"count": count}))
    
    # Weitere problematische Steuerzeichen
    found_controls = []
    for char, name in _CONTROL_CHARS:
        if char in tgt:
            found_controls.append(name)
    
    if found_controls:
        # NUL und BEL sind echte Probleme, andere Steuerzeichen sind oft harmlose Copy/Paste-Artefakte
        _critical_controls = {'NULL', 'BEL'}
        has_critical = any(c in _critical_controls for c in found_controls)
        severity = "major" if has_critical else "minor"
        issues.append(QAIssue("CONTROL_CHARS_FOUND", severity, "formatting",
                             f"Steuerzeichen im Ziel gefunden: {', '.join(found_controls)}",
                             src, tgt, segment_index, {"chars": found_controls}))
    
    return issues

def run_phase1_checks(pairs: Iterable[Tuple[str, str]]) -> List[QAIssue]:
    """Führt alle Phase-1 Checks durch.
    
    VERBESSERT: Setzt segment_index für jeden Issue zur UI-Nachverfolgung.
    """
    all_issues: List[QAIssue] = []
    segment_count = 0
    for idx, (src, tgt) in enumerate(pairs):
        segment_count = idx + 1
        all_issues.extend(check_urls_emails(src, tgt, idx))
        all_issues.extend(check_whitespace_and_zero_width(src, tgt, idx))
        all_issues.extend(check_boundary_whitespace(src, tgt, idx))
        all_issues.extend(check_soft_hyphens_and_control_chars(src, tgt, idx))
        all_issues.extend(check_brackets_basic(src, tgt, idx))
        all_issues.extend(check_quotes_basic(src, tgt, idx))
    
    if all_issues:
        _logger.debug("Phase1: %d Issues in %d Segmenten", len(all_issues), segment_count)
    
    return all_issues

__all__ = [
    'QAIssue',
    'run_phase1_checks',
    'check_urls_emails',
    'check_whitespace_and_zero_width',
    'check_boundary_whitespace',
    'check_soft_hyphens_and_control_chars',
    'check_brackets_basic',
    'check_quotes_basic'
]
