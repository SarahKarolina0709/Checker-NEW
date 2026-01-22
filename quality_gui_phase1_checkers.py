"""quality_gui_phase1_checkers – umbenanntes Modul (ehemals qa_phase1_checkers).

Beibehaltung der vollständigen Funktionalität (Platzhalter, URLs/E-Mails,
Whitespace, Klammern, Quotes). Alle bisherigen öffentlichen Symbole bleiben erhalten.
"""
from __future__ import annotations

# Originalinhalt aus qa_phase1_checkers (unverändert außer Modulname)
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Iterable, Optional

@dataclass
class QAIssue:
    code: str
    severity: str
    category: str
    message: str
    source_text: str
    target_text: str
    meta: Dict[str, object] = field(default_factory=dict)

# --- Verbesserter modularer Platzhalter-Parser ---
# 1) {name} / {0}
BRACE_PLACE_PATTERN = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}|\{\d+\}")
# 2) ICU flach (kein Deep-Nesting)
ICU_FLAT_PATTERN = re.compile(r"\{\w+,\s*(?:plural|select|selectordinal)\s*,[^{}]*\{[^{}]*\}[^}]*\}")
# 3) printf / Python %-Format (inkl. %(name)s) – '%%' wird später gefiltert
PCT_PLACE_PATTERN = re.compile(
    r"%(?:\([A-Za-z_][A-Za-z0-9_]*\))?"      # %(name)s
    r"(?:\d+\$)?"                            # 2$ positional
    r"[+#0\- ]?"                             # flags
    r"(?:\d+|\*)?"                          # width
    r"(?:\.(?:\d+|\*))?"                   # precision
    r"(?:hh|h|l|ll|L)?"                       # length
    r"[cCdiouxXeEfFgGaAsSp@]"                  # type (Prozent entfernt, '@' für Obj-C)
)
PCT_ESCAPED_PATTERN = re.compile(r"%%")
# 4) Mustache / Handlebars
MUSTACHE_PATTERN = re.compile(r"\{\{[^{}]+\}\}")
# 5) JS Template ${name}
DOLLAR_BRACE_PATTERN = re.compile(r"\$\{[^{}]+\}")
# 6) :slug (nur ohne vorheriges Wortzeichen)
COLON_SLUG_PATTERN = re.compile(r"(?<!\w):[A-Za-z_][\w-]*")
URL_PATTERN = re.compile(
    r"https?://[\w.-]+(?:/[~\w\-./;?%&=+#]*)?(?<![),.:;!?])",
    re.IGNORECASE
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_URL_PATTERN = re.compile(r"mailto:" + EMAIL_PATTERN.pattern, re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s+[^>]*?)?>")
# 7) Zero-width + NBSP (\u00A0) + NNBSP (\u202F) + FIGURE SPACE (\u2007)
ZERO_WIDTH_PATTERN = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF\u00A0\u202F\u2007]")
DUP_SPACE_PATTERN = re.compile(r" {2,}")
TRAIL_SPACE_PATTERN = re.compile(r"[ \t]+$", re.MULTILINE)
LEAD_SPACE_PATTERN = re.compile(r"^[ \t]+", re.MULTILINE)

BRACKET_PAIRS = {"(":")", "[":"]", "{":"}", "<":">"}  # Fix: kein Leerzeichen vor )
OPENING = set(BRACKET_PAIRS.keys())
CLOSING = set(BRACKET_PAIRS.values())

GERMAN_QUOTE_OPEN  = "„"
GERMAN_QUOTE_CLOSE = "“"
DE_QUOTES = [("„","“"), ("‚","‘"), ("«","»")]

# Vorcompilierte Hilfs-Regexe für printf-Format
PCT_POS_RX = re.compile(r"%\d+\$")
PCT_NAM_RX = re.compile(r"%\([A-Za-z_]\w*\)")

def extract_placeholders(text: str) -> List[str]:
    """Erkennt diverse Platzhalterarten in Dokumentreihenfolge, ohne Überschneidungen.

    Erfasst:
      - {name}, {0}
      - ICU (flach)
      - %(name)s, %s, %2$d (ohne '%%')
      - {{name}}
      - ${name}
      - :slug (nur wenn vorher kein Wortzeichen)
    """
    if not text:
        return []
    patterns = [
        ("icu", ICU_FLAT_PATTERN),
        ("brace", BRACE_PLACE_PATTERN),
        ("pct", PCT_PLACE_PATTERN),
        ("mustache", MUSTACHE_PATTERN),
        ("dollarb", DOLLAR_BRACE_PATTERN),
        ("colon", COLON_SLUG_PATTERN),
    ]
    hits: List[Tuple[int, int, str]] = []
    for _, rx in patterns:
        for m in rx.finditer(text):
            s, e = m.span()
            if s == e:
                continue
            hits.append((s, e, text[s:e]))
    # Escaped %% rausfiltern
    for m in PCT_ESCAPED_PATTERN.finditer(text):
        s, e = m.span()
        hits = [h for h in hits if not (h[0] >= s and h[1] <= e)]
    # Überschneidungen vermeiden (greedy non-overlapping)
    hits.sort(key=lambda t: (t[0], -(t[1]-t[0])))
    result: List[Tuple[int, int, str]] = []
    last_end = -1
    for s, e, val in hits:
        if s < last_end:
            continue
        result.append((s, e, val))
        last_end = e
    return [v for _, _, v in result]

def extract_urls(text: str) -> List[str]:
    t = text or ""
    return URL_PATTERN.findall(t) + MAILTO_URL_PATTERN.findall(t)

def extract_emails(text: str) -> List[str]:
    return EMAIL_PATTERN.findall(text or "")

def extract_zero_width(text: str) -> List[str]:
    return ZERO_WIDTH_PATTERN.findall(text or "")

def _strip_html_tags(text: str) -> str:
    try:
        return HTML_TAG_PATTERN.sub('', text or '')
    except Exception:
        return text or ''

def _has_positional_pct(lst: List[str]) -> bool:
    return any(PCT_POS_RX.search(x) for x in lst)

def _has_named_pct(lst: List[str]) -> bool:
    return any(PCT_NAM_RX.search(x) for x in lst)

def check_placeholders(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    s_list, t_list = extract_placeholders(src), extract_placeholders(tgt)
    if s_list == t_list:
        return issues
    cs, ct = Counter(s_list), Counter(t_list)
    missing = list((cs - ct).elements())
    extra   = list((ct - cs).elements())
    if missing:
        issues.append(QAIssue("PLACEHOLDER_MISSING","critical","placeholders", f"Fehlende Platzhalter: {missing}", src, tgt, {"missing": missing}))
    if extra:
        issues.append(QAIssue("PLACEHOLDER_EXTRA","major","placeholders", f"Zusätzliche Platzhalter: {extra}", src, tgt, {"extra": extra}))
    if not missing and not extra:
        combined = s_list + t_list
        if not (_has_positional_pct(combined) or _has_named_pct(combined)):
            issues.append(QAIssue("PLACEHOLDER_ORDER","major","placeholders", "Abweichende Platzhalter-Reihenfolge", src, tgt, {"source": s_list, "target": t_list}))
    return issues

def _diff_list_multiset(src_vals: List[str], tgt_vals: List[str]) -> tuple[List[str], List[str]]:
    cs, ct = Counter(src_vals), Counter(tgt_vals)
    missing = list((cs - ct).elements())
    extra = list((ct - cs).elements())
    return missing, extra

def check_urls_emails(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    s_urls, t_urls = extract_urls(src), extract_urls(tgt)
    # Erst URLs prüfen
    for label, vals_src, vals_tgt, miss_code, extra_code in (
        ("URL", s_urls, t_urls, "URL_MISSING", "URL_EXTRA"),
    ):
        s_vals, t_vals = vals_src, vals_tgt
        miss, extra = _diff_list_multiset(s_vals, t_vals)
        if miss:
            issues.append(QAIssue(miss_code, "critical", "references", f"{label}s fehlen: {miss}", src, tgt, {"source": s_vals, "target": t_vals}))
        if extra:
            issues.append(QAIssue(extra_code, "major", "references", f"{label}s zusätzlich: {extra}", src, tgt, {"source": s_vals, "target": t_vals}))
        if not miss and not extra and s_vals != t_vals:
            issues.append(QAIssue(f"{label.upper()}_ORDER", "minor", "references", f"{label}-Reihenfolge weicht ab", src, tgt, {"source": s_vals, "target": t_vals}))
    # Dann E-Mails prüfen, aber solche aus mailto: nicht doppelt zählen
    s_eml, t_eml = extract_emails(src), extract_emails(tgt)
    def strip_mailto(lst: List[str]) -> List[str]:
        # Wenn die E-Mail in irgendeiner mailto: URL vorkommt, aus der Liste entfernen
        combined_urls = set(s_urls + t_urls)
        return [e for e in lst if ("mailto:" + e) not in combined_urls]
    s_eml, t_eml = strip_mailto(s_eml), strip_mailto(t_eml)
    miss, extra = _diff_list_multiset(s_eml, t_eml)
    if miss:
        issues.append(QAIssue("EMAIL_MISSING", "critical", "references", f"E-Mails fehlen: {miss}", src, tgt, {"source": s_eml, "target": t_eml}))
    if extra:
        issues.append(QAIssue("EMAIL_EXTRA", "major", "references", f"E-Mails zusätzlich: {extra}", src, tgt, {"source": s_eml, "target": t_eml}))
    if not miss and not extra and s_eml != t_eml:
        issues.append(QAIssue("EMAIL_ORDER", "minor", "references", "E-Mail-Reihenfolge weicht ab", src, tgt, {"source": s_eml, "target": t_eml}))
    return issues

def check_whitespace_and_zero_width(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    for label, text in (("source", src), ("target", tgt)):
        if DUP_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_DOUBLE_SPACE", "minor", "whitespace", f"Doppelte Leerzeichen in {label}", src, tgt))
        if TRAIL_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_TRAILING", "minor", "whitespace", f"Trailing Whitespace in {label}", src, tgt))
        if LEAD_SPACE_PATTERN.search(text):
            issues.append(QAIssue("WS_LEADING", "minor", "whitespace", f"Führende Leerzeichen in {label}", src, tgt))
        zw = extract_zero_width(text)
        if zw:
            unique = sorted(set(zw))
            names = []
            for ch in unique:
                if ch == "\u00A0":
                    names.append("NBSP(\\u00A0)")
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
                elif ch == "\u202F":
                    names.append("NNBSP(\\u202F)")
                elif ch == "\u2007":
                    names.append("FIGURE SPACE(\\u2007)")
                else:
                    names.append(f"U+{ord(ch):04X}")
            issues.append(QAIssue("ZERO_WIDTH_CHAR", "major", "whitespace", f"Unsichtbare/geschützte Zeichen in {label}: {names}", src, tgt, {"chars": zw}))
    return issues

def check_brackets_basic(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    for label, raw in (("source", src), ("target", tgt)):
        text = _strip_html_tags(raw)
        stack: List[str] = []
        for ch in text:
            if ch in OPENING:
                stack.append(ch)
            elif ch in CLOSING:
                if not stack:
                    issues.append(QAIssue("BRACKET_UNBALANCED", "major", "structure", f"Schließende Klammer ohne Öffnung in {label}: {ch}", src, tgt))
                    break
                op = stack.pop()
                if BRACKET_PAIRS[op] != ch:
                    issues.append(QAIssue("BRACKET_MISMATCH", "major", "structure", f"Klammer-Mismatch {op}->{ch} in {label}", src, tgt))
                    break
        else:
            if stack:
                issues.append(QAIssue("BRACKET_UNCLOSED", "major", "structure", f"Nicht geschlossene Klammern in {label}: {stack}", src, tgt))
    return issues

def _count_quotes_safely(t: str) -> tuple[int,int]:
    t = _strip_html_tags(t or "")
    # Apostrophe innerhalb von Wörtern (don't, l'école) ignorieren für Balance
    t_wo = re.sub(r"(?<=\w)'(?=\w)", "", t)
    return t_wo.count('"'), t_wo.count("'")

def check_quotes_basic(src: str, tgt: str) -> List[QAIssue]:
    """Quote-Balance mit Ignorieren wortinterner Apostrophe und deutscher Quotes."""
    issues: List[QAIssue] = []
    for label, text in (("source", src), ("target", tgt)):
        dbl, sng = _count_quotes_safely(text)
        stripped = _strip_html_tags(text or "")
        de_open  = stripped.count(GERMAN_QUOTE_OPEN)
        de_close = stripped.count(GERMAN_QUOTE_CLOSE)
        if dbl % 2 != 0:
            issues.append(QAIssue("QUOTE_UNBALANCED","minor","quotes", f'Ungerade Anzahl von " in {label}', src, tgt))
        if sng % 2 != 0:
            issues.append(QAIssue("QUOTE_UNBALANCED","minor","quotes", f"Ungerade Anzahl von ' in {label}", src, tgt))
        if de_open != de_close:
            issues.append(QAIssue("QUOTE_DE_MISMATCH","minor","quotes", f"Deutsche Anführungszeichen unausgeglichen in {label}", src, tgt, {"open": de_open, "close": de_close}))
        # Weitere typografische Varianten balancieren (ohne Duplikat für „“)
        for open_q, close_q in DE_QUOTES:
            if open_q == GERMAN_QUOTE_OPEN and close_q == GERMAN_QUOTE_CLOSE:
                continue
            o = stripped.count(open_q)
            c = stripped.count(close_q)
            if o != c:
                issues.append(QAIssue(
                    "QUOTE_DE_MISMATCH","minor","quotes",
                    f"Deutsche/typographische Anführungszeichen unausgeglichen ({open_q}{close_q}) in {label}",
                    src, tgt, {"open": o, "close": c, "pair": (open_q, close_q)}
                ))
    return issues

def check_boundary_whitespace(src: str, tgt: str) -> List[QAIssue]:
    """Prüft ob Start/Ende-Leerzeichen übernommen wurden (UI-kritisch für Buttons/Labels)."""
    issues: List[QAIssue] = []
    src_starts = src.startswith(' ') or src.startswith('\t')
    tgt_starts = tgt.startswith(' ') or tgt.startswith('\t')
    src_ends = src.endswith(' ') or src.endswith('\t')
    tgt_ends = tgt.endswith(' ') or tgt.endswith('\t')
    
    if src_starts and not tgt_starts:
        issues.append(QAIssue("BOUNDARY_SPACE_START_MISSING", "major", "whitespace",
                             "Führendes Leerzeichen fehlt im Ziel (UI-Layout!)", src, tgt))
    elif not src_starts and tgt_starts:
        issues.append(QAIssue("BOUNDARY_SPACE_START_ADDED", "major", "whitespace",
                             "Führendes Leerzeichen hinzugefügt (UI-Layout!)", src, tgt))
    
    if src_ends and not tgt_ends:
        issues.append(QAIssue("BOUNDARY_SPACE_END_MISSING", "major", "whitespace",
                             "Nachgestelltes Leerzeichen fehlt im Ziel (UI-Layout!)", src, tgt))
    elif not src_ends and tgt_ends:
        issues.append(QAIssue("BOUNDARY_SPACE_END_ADDED", "major", "whitespace",
                             "Nachgestelltes Leerzeichen hinzugefügt (UI-Layout!)", src, tgt))
    return issues

def check_soft_hyphens_and_control_chars(src: str, tgt: str) -> List[QAIssue]:
    """Erkennt Soft-Hyphens und andere Steuerzeichen (oft Word-Artefakte)."""
    issues: List[QAIssue] = []
    soft_hyphen = '\u00AD'  # Soft Hyphen
    
    # Soft Hyphen prüfen
    if soft_hyphen in tgt and soft_hyphen not in src:
        count = tgt.count(soft_hyphen)
        issues.append(QAIssue("SOFT_HYPHEN_ADDED", "major", "formatting",
                             f"Soft-Hyphen eingefügt ({count}x) - meist Word-Artefakt", src, tgt,
                             {"count": count}))
    
    # Weitere problematische Steuerzeichen
    control_chars = [
        ('\u0000', 'NULL'),
        ('\u0001', 'SOH'),
        ('\u0002', 'STX'),
        ('\u0003', 'ETX'),
        ('\u0004', 'EOT'),
        ('\u0005', 'ENQ'),
        ('\u0006', 'ACK'),
        ('\u0007', 'BEL'),
        ('\u0008', 'BS'),
        ('\u000B', 'VT'),
        ('\u000C', 'FF'),
        ('\u000E', 'SO'),
        ('\u000F', 'SI'),
    ]
    
    found_controls = []
    for char, name in control_chars:
        if char in tgt:
            found_controls.append(name)
    
    if found_controls:
        issues.append(QAIssue("CONTROL_CHARS_FOUND", "critical", "formatting",
                             f"Steuerzeichen im Ziel gefunden: {', '.join(found_controls)}",
                             src, tgt, {"chars": found_controls}))
    
    return issues

def run_phase1_checks(pairs: Iterable[Tuple[str, str]]) -> List[QAIssue]:
    all_issues: List[QAIssue] = []
    for src, tgt in pairs:
        all_issues.extend(check_placeholders(src, tgt))
        all_issues.extend(check_urls_emails(src, tgt))
        all_issues.extend(check_whitespace_and_zero_width(src, tgt))
        all_issues.extend(check_boundary_whitespace(src, tgt))
        all_issues.extend(check_soft_hyphens_and_control_chars(src, tgt))
        all_issues.extend(check_brackets_basic(src, tgt))
        all_issues.extend(check_quotes_basic(src, tgt))
    return all_issues

__all__ = [
    'QAIssue',
    'run_phase1_checks',
    'check_placeholders',
    'check_urls_emails',
    'check_whitespace_and_zero_width',
    'check_boundary_whitespace',
    'check_soft_hyphens_and_control_chars',
    'check_brackets_basic',
    'check_quotes_basic'
]
