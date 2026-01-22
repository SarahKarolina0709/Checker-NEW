"""quality_gui_phase2_checkers – umbenanntes Modul (ehemals qa_phase2_checkers)."""
from __future__ import annotations
import re, json
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Dict, Tuple, Iterable, Optional, Set, Any

from quality_gui_phase1_checkers import QAIssue  # Schema Reuse

TAG_PATTERN = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9:-]*)([^>]*)>")
# Attribute: sowohl name=... als auch boolsche Attribute ohne '=' erfassen
ATTR_NAME_EQ_PATTERN = re.compile(r"\b([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=")
ATTR_NAME_BOOL_PATTERN = re.compile(r"\b([A-Za-z_:][-A-Za-z0-9_:.]*)(?=\s|>|/>)")
# Event-Handler präziser: erlaubt on-foo/on_bar etc., vermeidet once=
EVENT_HANDLER_ATTR_PATTERN = re.compile(r"\bon[a-z0-9_:-]*\s*=", re.IGNORECASE)  # echte Handler-Attribute mit Wortgrenze
JS_SCHEME_PATTERN = re.compile(r"javascript:\s*", re.IGNORECASE)
SCRIPT_TAG_PATTERN = re.compile(r"<\s*script\b", re.IGNORECASE)

GERMAN_DU = {"du","dich","dir","dein","deine","deinen","deinem","deiner","euch","euer","eure","euren","eurem","eurer"}
FORMAL_SIE_PATTERN = re.compile(r"(?<![A-Za-zÄÖÜäöüß])Sie(?![A-Za-zÄÖÜäöüß])")  # robuster: erkennt auch (Sie „Sie

END_PUNCT = {'.','!','?'}
NUMBER_PATTERN = re.compile(r"\b\d+[\d.,]*\b")  # Roh-Erkennung; Normalisierung folgt
UNIT_PATTERN = re.compile(r"\b(kg|g|t|km|m|cm|mm|gb|mb|kb|%|°c|€|eur|usd|ms|s|mio\.|Mio\.)\b", re.IGNORECASE)  # Legacy (belassen für evtl. spätere Nutzung)
# Nur Einheiten direkt an Zahlen (reduziert False Positives)
UNIT_NEAR_NUMBER = re.compile(
    r"(?P<num>\d[\d.,]*)\s*(?P<unit>kg|g|t|km|m|cm|mm|gb|mb|kb|%|°\s?c|€|eur|usd|ms|s|mio\.)\b",
    re.IGNORECASE
)
# Einheiten vor der Zahl (€, $, %, eur/usd)
UNIT_BEFORE_NUMBER = re.compile(r"(?P<unit>€|eur|usd|%)\s*(?P<num>\d[\d.,]*)\b", re.IGNORECASE)

# HTML-Void-Tags (nicht schließen / nicht als unclosed melden)
VOID_TAGS = {"area","base","br","col","embed","hr","img","input","link",
             "meta","param","source","track","wbr"}
DATA_URI_PATTERN = re.compile(r"data:\s*[a-z]+/[a-z0-9+.-]+", re.IGNORECASE)
DOUBLE_PUNCT_PATTERN = re.compile(r"[.!?]{2,}")
STRAIGHT_QUOTE_PATTERN = re.compile(r'"')
GERMAN_SMART_QUOTES = {"„","“"}

# Locale & Kontext Erweiterungen
ISO_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
GERMAN_DATE_PATTERN = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")
TIME_PATTERN = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
DECIMAL_NUMBER_PATTERN = re.compile(r"\b\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d+)?\b")
ORDERED_MARKER_PATTERN = re.compile(r"^\s*(\d+)[\.)]\s+")
BULLET_MARKER_PATTERN = re.compile(r"^\s*([*\-•·])\s+")

# Erweiterungen
STYLE_ATTR_PATTERN = re.compile(r"\bstyle\s*=")

# Neue Checks (Coverage Ratio & Eigennamen)
PROPER_NAME_PATTERN = re.compile(r"\b[A-ZÄÖÜ][a-zäöüß]+(?:[- ][A-ZÄÖÜ][a-zäöüß]+)*\b")
ACRONYM_PATTERN = re.compile(r"\b[A-Z0-9]{3,}\b")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Whitelist für Eigennamen-False-Positives (Wochentage/Monate)
DEFAULT_PROPER_WHITELIST = {
    "Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag",
    "Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"
}

def _strip_tags(text: str) -> str:
    return TAG_PATTERN.sub('', text or '')

def _load_phase2_config(path: str = 'checker_config.json') -> Dict[str, object]:
    try:
        p = Path(path)
        if not p.is_file():
            return {}
        data = json.loads(p.read_text(encoding='utf-8'))
        return data.get('analysis', {}).get('phase2', {}) or {}
    except Exception:
        return {}

def check_coverage_ratio(src: str, tgt: str, *, min_ratio: float = 0.6, min_src_len: int = 40) -> List[QAIssue]:
    """Flaggt Segmente deren Zieltext signifikant kürzer ist als die Quelle.

    Bedingungen:
      - Länge Quelle (ohne Tags) >= min_src_len
      - ratio = len(tgt_plain) / len(src_plain) < min_ratio
    """
    issues: List[QAIssue] = []
    src_plain = _strip_tags(src).strip()
    tgt_plain = _strip_tags(tgt).strip()
    if not src_plain or not tgt_plain:
        return issues
    if len(src_plain) < min_src_len:
        return issues
    ratio = len(tgt_plain) / max(1, len(src_plain))
    if ratio < min_ratio:
        issues.append(QAIssue("COVERAGE_RATIO_LOW", "major", "structure", f"Zieltext kürzer (Ratio {ratio:.2f} < {min_ratio})", src, tgt, {"ratio": round(ratio,3)}))
    return issues

def _extract_proper_names(src: str) -> Set[str]:
    names: Set[str] = set()
    # Sätze trennen um erstes Wort zu ignorieren
    # Fallback: einfacher Split falls Regex fehlschlägt
    sentences = re.split(r'(?<=[.!?])\s+', src) if src else []
    first_words: Set[str] = set()
    for s in sentences:
        fw = re.match(r"^[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9-]*", s.strip() or '')
        if fw:
            first_words.add(fw.group(0))
    for m in PROPER_NAME_PATTERN.finditer(src or ''):
        token = m.group(0)
        if token in first_words:
            continue
        names.add(token)
    for m in ACRONYM_PATTERN.finditer(src or ''):
        token = m.group(0)
        if token in first_words:
            continue
        names.add(token)
    return names

def check_proper_names(src: str, tgt: str, glossary: Dict[str, List[str]], *, whitelist: Set[str], dnt: Set[str]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not src or not tgt:
        return issues
    tgt_plain = _strip_tags(tgt)
    names = _extract_proper_names(src)
    if not names:
        return issues
    # Glossar erlaubte Varianten map
    gloss_map: Dict[str, List[str]] = {k: v for k, v in glossary.items()}
    missing: List[str] = []
    tgt_lower = tgt_plain.lower()
    for name in names:
        if name in whitelist or name in DEFAULT_PROPER_WHITELIST:
            continue
        name_lower = name.lower()
        allowed = [a.lower() for a in gloss_map.get(name_lower, [])]
        # Accept if identical or any preferred variant present
        if (name not in tgt_plain) and not any(a in tgt_lower for a in allowed):
            missing.append(name)
    if missing:
        crit = [m for m in missing if m.lower() in {x.lower() for x in dnt}]
        sev = 'critical' if crit else 'major'
        issues.append(QAIssue("PROPER_NAME_MISSING", sev, "terminology", f"Eigennamen/Akronyme fehlen oder verändert: {missing}", src, tgt, {"missing": missing, "critical": crit}))
    return issues

def _normalize_number_token(token: str) -> str:
    """Normalisiert Zahlentoken (Tausendertrenner entfernen, Dezimal vereinheitlichen auf '.')."""
    t = (token or "").strip().replace('\u00A0', '')
    if not t:
        return t
    t = t.strip('.,')
    if not t or not re.search(r"\d", t):
        return t
    if '.' in t and ',' in t:
        last_sep = max(t.rfind('.'), t.rfind(','))
        int_part = re.sub(r'[.,]', '', t[:last_sep])
        dec_part = t[last_sep+1:]
        return f"{int_part}.{dec_part}" if dec_part else int_part
    if ',' in t and '.' not in t:
        return t.replace('.', '').replace(',', '.')
    if t.count('.') > 1:
        return t.replace('.', '')
    if t.count('.') == 1:
        a,b = t.split('.')
        if len(b) == 3:  # 1.000 => 1000
            return a + b
        return f"{a}.{b}" if b else a
    return t

def _normalize_unit_token(u: str) -> str:
    mapping = {'€':'eur','eur':'eur','$':'usd','usd':'usd','mio.':'mio','°c':'c','° c':'c'}
    ul = u.lower().replace(' ', '')
    return mapping.get(ul, ul)

def _load_glossary(path: str = 'glossary_terms.json') -> Dict[str, List[str]]:
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return {k.lower(): ([v] if isinstance(v, str) else [x for x in v if isinstance(x, str)]) for k,v in data.items()}
    except Exception:
        return {}

def _tokenize_lower(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

def _normalize_for_duplicate(src: str) -> str:
    s = (src or "").strip()
    s = TAG_PATTERN.sub("", s)
    s = s.strip('"'"'"'“”„‹›«»')
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip('.!?;:,')
    return s.lower()

def check_html_tags(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    def parse_tags(text: str):
        stack = []
        mismatches = []
        tag_name_counts = Counter()
        attr_name_counts = Counter()
        for m in TAG_PATTERN.finditer(text):
            closing, name, attrs = m.groups()
            name_low = name.lower()
            if closing:
                if not stack:
                    mismatches.append(("UNOPENED", name_low))
                else:
                    op = stack.pop()
                    if op != name_low:
                        mismatches.append(("MISMATCH", f"{op}->{name_low}"))
            else:
                is_self = attrs.strip().endswith('/') or (name_low in VOID_TAGS)
                # Attribute zählen: erst name=..., dann boolsche ohne '=' (konservativ ohne Doppelung)
                eq_attrs = [a.lower() for a in ATTR_NAME_EQ_PATTERN.findall(attrs)]
                for a in eq_attrs:
                    attr_name_counts[a] += 1
                # Boolean-Attribute ergänzen; wenn das Attribut schon als name= gezählt wurde, nicht erneut
                for a in ATTR_NAME_BOOL_PATTERN.findall(attrs):
                    al = a.lower()
                    # sehr konservativ: nur zählen, wenn im aktuellen Tag gar kein '=' vorkommt oder der Name nicht bereits gezählt wurde
                    if (al not in attr_name_counts) or ('=' not in attrs):
                        attr_name_counts[al] += 1
                if not is_self:
                    stack.append(name_low)
            tag_name_counts[name_low] += 1
        if stack:
            for s in stack:
                mismatches.append(("UNCLOSED", s))
        return mismatches, tag_name_counts, attr_name_counts
    mism_src, cnt_src, attr_src = parse_tags(src)
    mism_tgt, cnt_tgt, attr_tgt = parse_tags(tgt)
    if mism_tgt:
        issues.append(QAIssue(
            "HTML_UNBALANCED", "critical", "html",
            f"Nicht balancierte/verschachtelte Tags: {mism_tgt}", src, tgt,
            {"details": mism_tgt, "hint": "Stack order prüfen (z. B. <b><i></i></b>)"}
        ))
    diff_missing = [n for n in cnt_src if cnt_src[n] > cnt_tgt.get(n, 0)]
    diff_extra = [n for n in cnt_tgt if cnt_tgt[n] > cnt_src.get(n, 0)]
    if diff_missing:
        issues.append(QAIssue("HTML_TAG_MISSING", "major", "html", f"Fehlende Tags: {sorted(set(diff_missing))}", src, tgt))
    if diff_extra:
        issues.append(QAIssue("HTML_TAG_EXTRA", "major", "html", f"Zusätzliche Tags: {sorted(set(diff_extra))}", src, tgt))
    attr_missing = [n for n in attr_src if attr_src[n] > attr_tgt.get(n, 0)]
    attr_extra = [n for n in attr_tgt if attr_tgt[n] > attr_src.get(n, 0)]
    if attr_missing:
        issues.append(QAIssue("HTML_ATTR_MISSING", "major", "html", f"Fehlende Attribute: {sorted(set(attr_missing))}", src, tgt))
    if attr_extra:
        issues.append(QAIssue("HTML_ATTR_EXTRA", "major", "html", f"Zusätzliche Attribute: {sorted(set(attr_extra))}", src, tgt))
    return issues

def check_pronoun_consistency(target: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    toks = _tokenize_lower(target)
    du_found = any(t in GERMAN_DU for t in toks)
    formal_sie = bool(FORMAL_SIE_PATTERN.search(target))
    if du_found and formal_sie:
        issues.append(QAIssue("PRONOUN_MIX", "major", "style", "Mischung von Du/Sie Anrede im selben Segment", "", target))
    return issues

def _load_critical_terms_config(path: str = 'checker_config.json') -> List[str]:
    try:
        p = Path(path)
        if not p.is_file():
            return []
        data = json.loads(p.read_text(encoding='utf-8'))
        return data.get('analysis', {}).get('phase2', {}).get('terminology', {}).get('critical_terms', []) or []
    except Exception:
        return []

def check_terminology(src: str, tgt: str, glossary: Dict[str, List[str]], critical_terms: Optional[List[str]] = None) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not glossary:
        return issues
    if critical_terms is None:
        critical_terms = []
    src_tokens = set(_tokenize_lower(src))
    tgt_tokens = set(_tokenize_lower(tgt))
    for term, pref_list in glossary.items():
        if term in src_tokens:
            preferred_tokens = [p.lower() for p in pref_list]
            if not any(pt in tgt_tokens for pt in preferred_tokens):
                sev = "critical" if term in critical_terms else "major"
                issues.append(QAIssue("TERM_PREFERRED_MISSING", sev, "terminology", f"Bevorzugter Terminus fehlt für '{term}': erwartet {pref_list}", src, tgt, {"term": term, "preferred": pref_list}))
    return issues

def check_duplicate_translation_consistency(pairs: Iterable[Tuple[str,str]]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    mapping: Dict[str, str] = {}
    for src, tgt in pairs:
        norm_src = _normalize_for_duplicate(src)
        if not norm_src:
            continue
        prev = mapping.get(norm_src)
        norm_tgt = _normalize_for_duplicate(tgt)
        if prev is None:
            mapping[norm_src] = norm_tgt
        else:
            if prev != norm_tgt:
                issues.append(QAIssue("DUPLICATE_INCONSISTENT", "critical", "consistency", f"Uneinheitliche Übersetzung für '{src[:30]}...' => '{prev}' vs. '{norm_tgt}'", src, tgt, {"first": prev, "second": norm_tgt}))
    return issues

def check_sentence_case(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    def first_alpha(wording: str) -> str:
        m = re.search(r"[A-Za-zÄÖÜäöüß]", wording.lstrip('„“«»"\'( )'))
        return m.group(0) if m else ''
    s_first = first_alpha(src)
    t_first = first_alpha(tgt)
    if s_first and t_first and s_first.isupper() and t_first.islower():
        issues.append(QAIssue("S_CASE_INCONSISTENT", "minor", "style", "Satzanfang Großschreibung fehlt im Ziel", src, tgt))
    if s_first and t_first and s_first.islower() and t_first.isupper():
        issues.append(QAIssue("S_CASE_TARGET_CAPITALIZED", "minor", "style", "Ziel beginnt groß obwohl Quelle klein beginnt", src, tgt))
    return issues

def check_numbers_units(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    # Zahlen
    src_nums = Counter(_normalize_number_token(n) for n in NUMBER_PATTERN.findall(src))
    tgt_nums = Counter(_normalize_number_token(n) for n in NUMBER_PATTERN.findall(tgt))
    missing = [n for n in src_nums if src_nums[n] > tgt_nums.get(n, 0)]
    added   = [n for n in tgt_nums if tgt_nums[n] > src_nums.get(n, 0)]
    if missing:
        issues.append(QAIssue("NUMBER_MISSING", "major", "consistency", f"Zahlen fehlen im Ziel: {missing}", src, tgt))
    if added:
        issues.append(QAIssue("NUMBER_ADDED", "major", "consistency", f"Neue Zahlen im Ziel: {added}", src, tgt))
    # Einheiten nahe Zahlen
    def _units_near(text: str) -> Counter:
        units = []
        for m in UNIT_NEAR_NUMBER.finditer(text):
            units.append(_normalize_unit_token(m.group("unit")))
        for m in UNIT_BEFORE_NUMBER.finditer(text):
            units.append(_normalize_unit_token(m.group("unit")))
        return Counter(units)
    src_units = _units_near(src)
    tgt_units = _units_near(tgt)
    unit_missing = [u for u in src_units if src_units[u] > tgt_units.get(u, 0)]
    unit_added   = [u for u in tgt_units if tgt_units[u] > src_units.get(u, 0)]
    if unit_missing or unit_added:
        issues.append(QAIssue("UNIT_DRIFT", "major", "consistency", f"Einheiten-Differenzen: fehlend={unit_missing} neu={unit_added}", src, tgt))
    return issues

def check_punctuation(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    s = src.strip(); t = tgt.strip()
    if s and s[-1] in END_PUNCT and t and t[-1] not in END_PUNCT:
        issues.append(QAIssue("PUNCT_MISSING_END", "minor", "punctuation", "Satzendzeichen fehlt im Ziel", src, tgt))
    if DOUBLE_PUNCT_PATTERN.search(t):
        issues.append(QAIssue("PUNCT_DOUBLE", "minor", "punctuation", "Mehrfache Satzzeichen", src, tgt))
    t_no_html = TAG_PATTERN.sub('', t)  # Attribute entfernen für Quote-Analyse
    has_straight = bool(STRAIGHT_QUOTE_PATTERN.search(t_no_html))
    has_smart = any(q in t_no_html for q in GERMAN_SMART_QUOTES)
    if has_straight and not has_smart:
        issues.append(QAIssue("QUOTE_PLAIN", "minor", "punctuation", "Einfache Anführungszeichen statt typografischer", src, tgt))
    if has_straight and has_smart:
        issues.append(QAIssue("QUOTE_MIX", "minor", "punctuation", "Gemischte Anführungszeichenstile", src, tgt))
    return issues

def check_security(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if JS_SCHEME_PATTERN.search(tgt) and not JS_SCHEME_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_JS_LINK", "critical", "security", "Neuer javascript:-Link im Ziel", src, tgt))
    def _find_handlers(html: str) -> List[str]:
        handlers: List[str] = []
        for m in TAG_PATTERN.finditer(html):
            attrs = m.group(3) or ""
            handlers += EVENT_HANDLER_ATTR_PATTERN.findall(attrs)
        return handlers
    tgt_handlers = _find_handlers(tgt)
    if tgt_handlers:
        src_handlers = _find_handlers(src)
        if len(tgt_handlers) > len(src_handlers):
            issues.append(QAIssue("SECURITY_EVENT_HANDLER", "critical", "security", f"Neue Event-Handler Attribute: {tgt_handlers}", src, tgt, {"handlers": tgt_handlers}))
    if SCRIPT_TAG_PATTERN.search(tgt) and not SCRIPT_TAG_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_SCRIPT_TAG", "critical", "security", "Neues <script> Tag im Ziel", src, tgt))
    if DATA_URI_PATTERN.search(tgt) and not DATA_URI_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_DATA_URI", "critical", "security", "Neuer data:-URI im Ziel", src, tgt))
    if STYLE_ATTR_PATTERN.search(tgt) and not STYLE_ATTR_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_INLINE_STYLE", "major", "security", "Neues inline style Attribut im Ziel", src, tgt))
    return issues

def check_untranslated_segments(src: str, tgt: str, threshold: float = 0.85) -> List[QAIssue]:
    """Erkennt Segmente die der Übersetzer vergessen hat zu übersetzen."""
    issues: List[QAIssue] = []
    if not src or not tgt:
        return issues
    
    # Normalisiere beide Texte (ohne Tags, Platzhalter, Zahlen)
    src_clean = _strip_tags(src).strip()
    tgt_clean = _strip_tags(tgt).strip()
    
    # URLs und E-Mails entfernen (die sollen gleich bleiben)
    from quality_gui_phase1_checkers import extract_urls, extract_emails
    for url in extract_urls(src):
        src_clean = src_clean.replace(url, '')
        tgt_clean = tgt_clean.replace(url, '')
    for email in extract_emails(src):
        src_clean = src_clean.replace(email, '')
        tgt_clean = tgt_clean.replace(email, '')
    
    # Zahlen entfernen
    src_clean = NUMBER_PATTERN.sub('', src_clean)
    tgt_clean = NUMBER_PATTERN.sub('', tgt_clean)
    
    # Normalisieren für Vergleich
    src_norm = re.sub(r'\s+', ' ', src_clean).strip().lower()
    tgt_norm = re.sub(r'\s+', ' ', tgt_clean).strip().lower()
    
    if not src_norm or not tgt_norm or len(src_norm) < 5:
        return issues
    
    # SequenceMatcher für Ähnlichkeitsberechnung
    import difflib
    similarity = difflib.SequenceMatcher(None, src_norm, tgt_norm).ratio()
    
    if similarity > threshold:
        issues.append(QAIssue("UNTRANSLATED_SEGMENT", "critical", "completeness",
                             f"Segment scheint unübersetzt (Ähnlichkeit: {similarity:.0%})",
                             src, tgt, {"similarity": round(similarity, 3)}))
    
    return issues

def check_empty_translation(src: str, tgt: str) -> List[QAIssue]:
    """Erkennt leere oder nur mit Tags/Whitespace gefüllte Übersetzungen."""
    issues: List[QAIssue] = []
    
    src_content = _strip_tags(src).strip()
    tgt_content = _strip_tags(tgt).strip()
    
    # Quelle hat Inhalt, aber Ziel ist leer
    if src_content and not tgt_content:
        issues.append(QAIssue("EMPTY_TRANSLATION", "critical", "completeness",
                             "Übersetzung ist leer (nur Tags/Leerzeichen)", src, tgt))
    
    # Ziel ist extrem kurz verglichen mit Quelle (möglicherweise unvollständig)
    elif src_content and tgt_content and len(tgt_content) < 3 and len(src_content) > 20:
        issues.append(QAIssue("TRANSLATION_TOO_SHORT", "major", "completeness",
                             f"Übersetzung sehr kurz ({len(tgt_content)} vs {len(src_content)} Zeichen)",
                             src, tgt, {"src_len": len(src_content), "tgt_len": len(tgt_content)}))
    
    return issues

def check_punctuation_spacing(tgt: str) -> List[QAIssue]:
    """Prüft korrekte Leerzeichen um Satzzeichen (Deutsch: kein Leerzeichen VOR :!?)."""
    issues: List[QAIssue] = []
    
    # Falsch: "Hallo !" oder "Was ?" (französischer Stil)
    # Korrekt: "Hallo!" oder "Was?"
    if re.search(r'\s+[!?](?!\w)', tgt):
        issues.append(QAIssue("PUNCT_SPACE_BEFORE", "minor", "typography",
                             "Leerzeichen vor ! oder ? (französischer Fehler)", "", tgt))
    
    # Falsch: "Hallo!Welt" oder "Was?Nichts"
    # Korrekt: "Hallo! Welt" oder "Was? Nichts"
    if re.search(r'[!?][A-ZÄÖÜ]', tgt):
        issues.append(QAIssue("PUNCT_NO_SPACE_AFTER", "minor", "typography",
                             "Fehlendes Leerzeichen nach Satzzeichen", "", tgt))
    
    # Leerzeichen vor Doppelpunkt (oft falsch)
    # Ausnahme: Zeit "12 :30" oder "http ://" ignorieren
    if re.search(r'[a-zäöüß]\s+:', tgt) and not re.search(r'\d\s+:', tgt) and not re.search(r'http\s*:', tgt):
        issues.append(QAIssue("PUNCT_SPACE_BEFORE_COLON", "minor", "typography",
                             "Leerzeichen vor : (meist falsch im Deutschen)", "", tgt))
    
    # Leerzeichen vor Komma (fast immer falsch)
    if re.search(r'\w\s+,', tgt):
        issues.append(QAIssue("PUNCT_SPACE_BEFORE_COMMA", "minor", "typography",
                             "Leerzeichen vor Komma (falsch)", "", tgt))
    
    # Fehlendes Leerzeichen nach Komma
    if re.search(r',[A-Za-zÄÖÜäöüß]', tgt):
        issues.append(QAIssue("PUNCT_NO_SPACE_AFTER_COMMA", "minor", "typography",
                             "Fehlendes Leerzeichen nach Komma", "", tgt))
    
    return issues


def _format_date_by_pattern(dt: datetime, pattern: str) -> str:
    pattern = (pattern or "DD.MM.YYYY").upper()
    if pattern == "YYYY-MM-DD":
        return dt.strftime("%Y-%m-%d")
    if pattern == "DD.MM.YYYY":
        return dt.strftime("%d.%m.%Y")
    if pattern == "DD.MM.YY":
        return dt.strftime("%d.%m.%y")
    if pattern == "MM/DD/YYYY":
        return dt.strftime("%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")


def _format_number_locale(normalized: str, decimal_sep: str, thousand_sep: str) -> str:
    decimal_sep = decimal_sep or ","
    thousand_sep = thousand_sep or "."
    if not normalized:
        return normalized
    if "." in normalized:
        integer, fraction = normalized.split(".", 1)
    else:
        integer, fraction = normalized, ""
    sign = ""
    if integer.startswith("-"):
        sign = "-"
        integer = integer[1:]
    if thousand_sep:
        groups = []
        while len(integer) > 3:
            groups.append(integer[-3:])
            integer = integer[:-3]
        if integer:
            groups.append(integer)
        integer = thousand_sep.join(reversed(groups)) if groups else integer
    if fraction:
        return f"{sign}{integer}{decimal_sep}{fraction}"
    return f"{sign}{integer}"


def check_locale_formats(src: str, tgt: str, config: Dict[str, Any]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not config:
        return issues
    decimal_sep = str(config.get("decimal_separator", ","))
    thousand_sep = str(config.get("thousand_separator", "."))
    allow_iso = bool(config.get("allow_iso_dates", True))
    date_pattern = str(config.get("date_format", "DD.MM.YYYY"))
    src_text = src or ""
    tgt_text = tgt or ""

    for iso in ISO_DATE_PATTERN.findall(src_text):
        try:
            dt = datetime.strptime(iso, "%Y-%m-%d")
        except ValueError:
            continue
        expected = _format_date_by_pattern(dt, date_pattern)
        if expected and expected not in tgt_text:
            issues.append(QAIssue(
                "LOCALE_DATE_MISMATCH",
                "major",
                "locale",
                f"Datum sollte als {expected} erscheinen",
                src,
                tgt,
                {"date_iso": iso, "expected": expected}
            ))

    if not allow_iso:
        disallowed_iso = ISO_DATE_PATTERN.findall(tgt_text)
        if disallowed_iso:
            issues.append(QAIssue(
                "LOCALE_DATE_ISO_FORBIDDEN",
                "major",
                "locale",
                "ISO-Datumsformat im Ziel nicht erlaubt",
                src,
                tgt,
                {"dates": disallowed_iso}
            ))

    if decimal_sep:
        for token in DECIMAL_NUMBER_PATTERN.findall(src_text):
            norm = _normalize_number_token(token)
            if not norm:
                continue
            formatted = _format_number_locale(norm, decimal_sep, thousand_sep)
            if formatted and formatted not in tgt_text:
                actual_token = ""
                try:
                    tgt_numbers = DECIMAL_NUMBER_PATTERN.findall(tgt_text)
                    for cand in tgt_numbers:
                        if _normalize_number_token(cand) == norm:
                            if cand != formatted:
                                actual_token = cand
                                break
                except Exception:
                    actual_token = ""
                message = f"Zahlenformat erwartet {formatted}"
                if actual_token:
                    message += f" (aktuell: {actual_token})"
                issues.append(QAIssue(
                    "LOCALE_DECIMAL_MISMATCH",
                    "major",
                    "locale",
                    message,
                    src,
                    tgt,
                    {"number": norm, "expected": formatted, "actual": actual_token} if actual_token else {"number": norm, "expected": formatted}
                ))
    return issues


def check_blacklist_terms(src: str, tgt: str, config: Dict[str, Any]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not config or not config.get("enabled", True):
        return issues
    terms = [t for t in config.get("terms", []) if isinstance(t, str) and t.strip()]
    if not terms:
        return issues
    severity = str(config.get("severity", "critical") or "critical").lower()
    match_target = bool(config.get("match_target", True))
    match_source = bool(config.get("match_source", False))
    matches: Dict[str, List[str]] = {"source": [], "target": []}
    if match_source:
        src_lower = (src or "").lower()
        for term in terms:
            if term.lower() in src_lower:
                matches["source"].append(term)
    if match_target:
        tgt_lower = (tgt or "").lower()
        for term in terms:
            if term.lower() in tgt_lower:
                matches["target"].append(term)
    found = matches["source"] + matches["target"]
    if found:
        issues.append(QAIssue(
            "BLACKLIST_TERM",
            severity,
            "terminology",
            f"Verbotene Begriffe erkannt: {sorted(set(found))}",
            src,
            tgt,
            matches
        ))
    return issues


def _extract_list_markers(text: str) -> List[Dict[str, Any]]:
    markers: List[Dict[str, Any]] = []
    if not text:
        return markers
    for line_idx, line in enumerate(text.splitlines()):
        ordered = ORDERED_MARKER_PATTERN.match(line)
        if ordered:
            markers.append({
                "type": "ordered",
                "value": int(ordered.group(1)),
                "line": line_idx,
                "marker": ordered.group(0).strip()
            })
            continue
        bullet = BULLET_MARKER_PATTERN.match(line)
        if bullet:
            markers.append({
                "type": "bullet",
                "value": bullet.group(1),
                "line": line_idx,
                "marker": bullet.group(0).strip()
            })
    return markers


def _compare_marker_sets(src_markers: List[Dict[str, Any]], tgt_markers: List[Dict[str, Any]], config: Dict[str, Any], src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if config.get("ignore_single_items", True) and max(len(src_markers), len(tgt_markers)) <= 1:
        return issues
    if config.get("require_matching_markers", True):
        if len(src_markers) != len(tgt_markers):
            issues.append(QAIssue("LIST_STRUCTURE_MISMATCH", "major", "structure", "Anzahl der Listenmarker unterscheidet sich", src, tgt, {"source": src_markers, "target": tgt_markers}))
            return issues
        for sm, tm in zip(src_markers, tgt_markers):
            if sm.get("type") != tm.get("type"):
                issues.append(QAIssue("LIST_STRUCTURE_TYPE", "major", "structure", "Listentyp unterscheidet sich", src, tgt, {"source": sm, "target": tm}))
            elif sm.get("type") == "ordered" and sm.get("value") != tm.get("value"):
                issues.append(QAIssue("LIST_STRUCTURE_ORDER", "major", "structure", "Listennummerierung weicht ab", src, tgt, {"source": sm, "target": tm}))
            elif sm.get("type") == "bullet" and sm.get("value") != tm.get("value"):
                issues.append(QAIssue("LIST_STRUCTURE_BULLET", "minor", "structure", "Listenaufzählungszeichen unterscheiden sich", src, tgt, {"source": sm, "target": tm}))
    return issues


def check_list_structure_context(entries: List[Dict[str, Any]], config: Dict[str, Any]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not config or not config.get("enabled", True):
        return issues
    entry_map = {entry.get("index", idx): entry for idx, entry in enumerate(entries)}
    for entry in entries:
        issues.extend(_compare_marker_sets(entry.get("source_markers", []), entry.get("target_markers", []), config, entry.get("source_text", ""), entry.get("target_text", "")))
    if config.get("enforce_sequence", True):
        ordered_markers: List[Tuple[int, Dict[str, Any]]] = []
        for entry in entries:
            idx = entry.get("index", 0)
            for marker in entry.get("target_markers", []):
                if marker.get("type") == "ordered":
                    ordered_markers.append((idx, marker))
        prev_value: Optional[int] = None
        prev_index: Optional[int] = None
        for idx, marker in ordered_markers:
            value = marker.get("value")
            if not isinstance(value, int):
                continue
            if prev_value is None or value <= prev_value:
                prev_value = value
                prev_index = idx
                continue
            if value != prev_value + 1:
                prev_entry = entry_map.get(prev_index, {}) if prev_index is not None else {}
                current_entry = entry_map.get(idx, {})
                issues.append(QAIssue(
                    "LIST_SEQUENCE_BREAK",
                    "major",
                    "structure",
                    f"Listenfolge springt von {prev_value} auf {value}",
                    prev_entry.get("target_text", ""),
                    current_entry.get("target_text", ""),
                    {"previous": prev_value, "current": value, "previous_index": prev_index, "current_index": idx}
                ))
            prev_value = value
            prev_index = idx
    return issues


def check_metadata_constraints(pair_infos: List[Dict[str, Any]], config: Dict[str, Any]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not config or not config.get("enabled", False):
        return issues
    allowed = set(config.get("allowed_attributes", []) or [])
    required = set(config.get("required_attributes", []) or [])
    protected = config.get("protected_values", {}) or {}
    if not isinstance(protected, dict):
        protected = {}
    for info in pair_infos:
        if not isinstance(info, dict):
            continue
        meta = info.get("meta")
        if required and (not isinstance(meta, dict)):
            missing = sorted(required)
            issues.append(QAIssue("METADATA_MISSING", "critical", "metadata", f"Metadaten fehlen ({missing})", info.get("source"), info.get("translation"), {"expected": missing}))
            continue
        if not isinstance(meta, dict):
            continue
        if required:
            missing = [key for key in required if key not in meta]
            if missing:
                issues.append(QAIssue("METADATA_FIELD_MISSING", "critical", "metadata", f"Pflichtattribute fehlen: {missing}", info.get("source"), info.get("translation"), {"missing": missing}))
        if allowed:
            unexpected = [key for key in meta.keys() if key not in allowed]
            if unexpected:
                issues.append(QAIssue("METADATA_ATTRIBUTE_FORBIDDEN", "major", "metadata", f"Unerwartete Attribute: {unexpected}", info.get("source"), info.get("translation"), {"attributes": unexpected}))
        for field, expected_values in protected.items():
            if field in meta and isinstance(expected_values, (list, tuple, set)) and expected_values:
                if meta[field] not in expected_values:
                    issues.append(QAIssue("METADATA_PROTECTED_VALUE", "critical", "metadata", f"Unzulässiger Wert für {field}: {meta[field]}", info.get("source"), info.get("translation"), {"field": field, "expected": list(expected_values), "actual": meta[field]}))
    return issues

def check_terminology_global_consistency(pairs: Iterable[Tuple[str,str]], glossary: Dict[str,List[str]]) -> List[QAIssue]:
    """Stellt fest, ob für denselben Quell-Term mehrere bevorzugte Glossarvarianten benutzt werden."""
    usage: Dict[str,set] = {}
    for src, tgt in pairs:
        src_tokens = set(_tokenize_lower(src))
        tgt_tokens = set(_tokenize_lower(tgt))
        for term, pref_list in glossary.items():
            if term in src_tokens:
                chosen = [p.lower() for p in pref_list if p.lower() in tgt_tokens]
                if chosen:
                    usage.setdefault(term, set()).update(chosen)
    issues: List[QAIssue] = []
    for term, variants in usage.items():
        if len(variants) > 1:
            issues.append(QAIssue("TERM_INCONSISTENT", "major", "terminology", f"Uneinheitliche bevorzugte Übersetzungen für '{term}': {sorted(variants)}", term, ', '.join(sorted(variants)), {"variants": sorted(variants)}))
    return issues

def run_phase2_checks(
    pairs: Iterable[Tuple[str,str]],
    glossary_path: str = 'glossary_terms.json',
    *,
    config: Optional[Dict[str, Any]] = None,
    pair_infos: Optional[List[Dict[str, Any]]] = None
) -> List[QAIssue]:
    glossary = _load_glossary(glossary_path)
    phase2_cfg = _load_phase2_config()
    coverage_cfg = phase2_cfg.get('coverage', {}) if isinstance(phase2_cfg, dict) else {}
    names_cfg = phase2_cfg.get('names', {}) if isinstance(phase2_cfg, dict) else {}
    cov_enabled = bool(coverage_cfg.get('enabled', True))
    cov_min_ratio = float(coverage_cfg.get('min_ratio', 0.6))
    cov_min_src_len = int(coverage_cfg.get('min_source_len', 40))
    names_enabled = bool(names_cfg.get('enabled', True))
    whitelist = set(names_cfg.get('whitelist', []) or [])
    dnt = set(names_cfg.get('do_not_translate', []) or [])
    critical_terms = _load_critical_terms_config()
    validation_cfg = config or {}
    locale_cfg = validation_cfg.get('locale', {}) or {}
    if not isinstance(locale_cfg, dict):
        locale_cfg = {}
    blacklist_cfg = validation_cfg.get('blacklist', {}) or {}
    if not isinstance(blacklist_cfg, dict):
        blacklist_cfg = {}
    list_cfg = validation_cfg.get('lists', {}) or {}
    if not isinstance(list_cfg, dict):
        list_cfg = {}
    metadata_cfg = validation_cfg.get('metadata', {}) or {}
    if not isinstance(metadata_cfg, dict):
        metadata_cfg = {}
    locale_enabled = bool(locale_cfg.get('enabled', True)) if isinstance(locale_cfg, dict) else bool(locale_cfg)
    blacklist_enabled = bool(blacklist_cfg.get('enabled', True)) if isinstance(blacklist_cfg, dict) else bool(blacklist_cfg)
    list_enabled = bool(list_cfg.get('enabled', True)) if isinstance(list_cfg, dict) else bool(list_cfg)

    all_pairs = list(pairs)
    issues: List[QAIssue] = []
    list_entries: List[Dict[str, Any]] = []
    for idx, (src, tgt) in enumerate(all_pairs):
        issues.extend(check_untranslated_segments(src, tgt))
        issues.extend(check_empty_translation(src, tgt))
        issues.extend(check_html_tags(src, tgt))
        issues.extend(check_pronoun_consistency(tgt))
        issues.extend(check_terminology(src, tgt, glossary, critical_terms))
        issues.extend(check_punctuation(src, tgt))
        issues.extend(check_punctuation_spacing(tgt))
        issues.extend(check_sentence_case(src, tgt))
        issues.extend(check_numbers_units(src, tgt))
        issues.extend(check_security(src, tgt))
        if cov_enabled:
            issues.extend(check_coverage_ratio(src, tgt, min_ratio=cov_min_ratio, min_src_len=cov_min_src_len))
        if names_enabled:
            issues.extend(check_proper_names(src, tgt, glossary, whitelist=whitelist, dnt=dnt))
        if locale_enabled:
            issues.extend(check_locale_formats(src, tgt, locale_cfg))
        if blacklist_enabled:
            issues.extend(check_blacklist_terms(src, tgt, blacklist_cfg))
        if list_enabled:
            list_entries.append({
                "index": idx,
                "source_markers": _extract_list_markers(src),
                "target_markers": _extract_list_markers(tgt),
                "source_text": src,
                "target_text": tgt
            })
    issues.extend(check_duplicate_translation_consistency(all_pairs))
    issues.extend(check_terminology_global_consistency(all_pairs, glossary))
    if list_enabled and list_entries:
        issues.extend(check_list_structure_context(list_entries, list_cfg))
    if pair_infos and metadata_cfg:
        issues.extend(check_metadata_constraints(pair_infos, metadata_cfg))
    global_du = False; global_formal_sie = False
    for _, tgt in all_pairs:
        toks = _tokenize_lower(tgt)
        if any(t in GERMAN_DU for t in toks):
            global_du = True
        if FORMAL_SIE_PATTERN.search(tgt):
            global_formal_sie = True
    if global_du and global_formal_sie:
        issues.append(QAIssue("PRONOUN_GLOBAL_INCONSISTENT", "major", "style", "Uneinheitliche Anrede (Du/Sie) über Dokument", "", ""))
    return issues

__all__ = [
    'run_phase2_checks',
    'check_html_tags',
    'check_pronoun_consistency',
    'check_terminology',
    'check_duplicate_translation_consistency',
    'check_punctuation',
    'check_punctuation_spacing',
    'check_security',
    'check_sentence_case',
    'check_numbers_units',
    'check_terminology_global_consistency',
    'check_coverage_ratio',
    'check_proper_names',
    'check_locale_formats',
    'check_blacklist_terms',
    'check_list_structure_context',
    'check_metadata_constraints',
    'check_untranslated_segments',
    'check_empty_translation'
]
