"""quality_gui_phase6_suggestions – NEU (Phase 6: Intelligente Verbesserungs-Vorschläge)

Ziel:
    Additive Phase 6 liefert priorisierte Korrektur-/Optimierungs-Vorschläge basierend auf
    den bestehenden Issues (Phasen 1–5) und heuristischen Qualitäts-Signalen.

Design-Prinzipien:
    - Rein additiv (keine Änderungen an bestehenden Datentypen / Workflows notwendig)
    - Fallback-first (läuft ohne ML/LLM Abhängigkeiten rein heuristisch)
    - Optionale LLM-Erweiterung (lokal Ollama / andere) – aktuell Stub mit sicherem Try/Except
    - Deterministisch ohne LLM (gleiche Eingaben → gleiche Vorschläge)
    - Performance-schonend: O(n) über Issues + leichte Heuristiken pro Segment

Integration:
    quality_gui_main_app.py ruft (sofern konfiguriert) run_phase6_suggestions() auf
    und fügt phase6_report dem summary hinzu. Aktivierung via config:
        analysis.phase6.enabled (bool, default False)
        analysis.phase6.max_suggestions (int, default 40)
        analysis.phase6.enable_llm (bool, default False)

Lieferumfang:
    Dataklasse QASuggestion
    run_phase6_suggestions(pairs, issues, **opts) → List[QASuggestion]
    Hilfsfunktionen zur Ableitung von Quick-Fixes + Stil-/Lesbarkeitsverbesserungen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Iterable, Tuple, Optional, Callable
import statistics, os, random
import re

try:  # QAIssue für Typreferenz – robustes Fallback falls Import fehlschlägt
    from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:  # pragma: no cover - Fallback Mini-Class (strukturkompatibel)
    @dataclass
    class QAIssue:  # type: ignore
        code: str; severity: str; category: str; message: str; source_text: str; target_text: str; meta: dict = field(default_factory=dict)  # noqa: E701


@dataclass
class QASuggestion:
    """Ein einzelner Verbesserungsvorschlag.

    Felder:
        id:            Stabile ID (hashbar) zur späteren Deduplikation / Baseline
        category:      semantische Kategorie (terminology|structure|style|readability|semantic|risk|quick_fix)
        message:       Kurzbeschreibung des Vorschlags (DE)
        rationale:     Erklärung / Warum sinnvoll
        priority:      1 (höchste Relevanz) .. 5 (niedrige Relevanz)
        confidence:    Heuristische Vertrauensstufe 0..1
        source_snippet Ziel-Snippet (Ausgang) – optional für Kontext
        target_snippet Ziel-Snippet (Übersetzung)
        meta:          Zusatzdaten (issue_refs, metrics, auto_fixable etc.)
    """
    id: str
    category: str
    message: str
    rationale: str
    priority: int
    confidence: float
    source_snippet: str
    target_snippet: str
    meta: Dict[str, object] = field(default_factory=dict)
    auto_fix_hint: bool = False  # Schneller UI-Flag ohne meta-Zugriff


# Mapping Issue → generische Verbesserungsidee
ISSUE_SUGGESTION_MAP: Dict[str, Dict[str, object]] = {
    'PLACEHOLDER_MISSING': {
        'category': 'structure',
        'message': 'Fehlende Platzhalter übernehmen',
        'rationale': 'Platzhalter 1:1 übernehmen um Laufzeitfehler zu verhindern',
        'priority': 1, 'confidence': 0.95
    },
    'PLACEHOLDER_EXTRA': {
        'category': 'structure',
        'message': 'Überzählige Platzhalter entfernen',
        'rationale': 'Nicht verwendete Platzhalter führen zu falscher Ausgabe',
        'priority': 1, 'confidence': 0.9
    },
    'RISK_NEW_DOMAIN': {
        'category': 'risk',
        'message': 'Neue Domain verifizieren',
        'rationale': 'Unbekannte Domains könnten Phishing / Tracking sein',
        'priority': 1, 'confidence': 0.85
    },
    'RISK_BASE64_SUSPECT': {
        'category': 'risk',
        'message': 'Verdächtige Base64 Sequenz prüfen',
        'rationale': 'Vermeidet versteckte Payload oder codierte Daten',
        'priority': 1, 'confidence': 0.9
    },
    'STYLE_LONG_SENTENCE': {
        'category': 'style',
        'message': 'Langen Satz teilen',
        'rationale': 'Kürzere Sätze erhöhen Lesbarkeit & Verarbeitbarkeit',
        'priority': 2, 'confidence': 0.8
    },
    'READABILITY_LIX_HIGH': {
        'category': 'readability',
        'message': 'Komplexe Strukturen vereinfachen',
        'rationale': 'Hoher LIX → schwer verständlich; vereinfachen erhöht Qualität',
        'priority': 2, 'confidence': 0.78
    },
    'SEMANTIC_LOW': {
        'category': 'semantic',
        'message': 'Semantisch abweichendes Segment angleichen',
        'rationale': 'Niedrige Ähnlichkeit kann inhaltliche Verschiebung bedeuten',
        'priority': 2, 'confidence': 0.75
    },
    'SEMANTIC_GLOBAL_LOW': {
        'category': 'semantic',
        'message': 'Globale Semantik konsolidieren',
        'rationale': 'Viele Segmente mit niedriger Ähnlichkeit → systematischer Drift',
        'priority': 1, 'confidence': 0.72
    },
    'WS_DOUBLE_SPACE': {
        'category': 'quick_fix',
        'message': 'Mehrfach-Leerzeichen reduzieren',
        'rationale': 'Kosmetischer Fix – erhöht formale Konsistenz',
        'priority': 4, 'confidence': 0.95
    },
    'ZERO_WIDTH_CHAR': {
        'category': 'quick_fix',
        'message': 'Unsichtbare Zeichen entfernen',
        'rationale': 'Verhindert unerwartetes Verhalten beim Rendern/Parsing',
        'priority': 2, 'confidence': 0.9
    },
    # --- Integrität / Struktur ---
    'URL_MISSING':   {'category':'structure','message':'Fehlende URL übernehmen','rationale':'Referenzen müssen 1:1 bleiben','priority':1,'confidence':0.92},
    'URL_EXTRA':     {'category':'structure','message':'Zusätzliche URL entfernen','rationale':'Neue Links sind riskant/ungewollt','priority':1,'confidence':0.9},
    'EMAIL_MISSING': {'category':'structure','message':'Fehlende E-Mail übernehmen','rationale':'Kontaktinfos müssen konsistent sein','priority':1,'confidence':0.9},
    'EMAIL_EXTRA':   {'category':'structure','message':'Zusätzliche E-Mail entfernen','rationale':'Unerwartete Kontaktdaten vermeiden','priority':1,'confidence':0.88},
    'PLACEHOLDER_ORDER': {'category':'structure','message':'Platzhalter-Reihenfolge angleichen','rationale':'Reihenfolge kann Laufzeitformatierung beeinflussen','priority':2,'confidence':0.85},
    'HTML_UNBALANCED': {'category':'structure','message':'HTML-Struktur balancieren','rationale':'Fehlende/verschachtelte Tags brechen Rendering','priority':1,'confidence':0.95},
    'HTML_TAG_MISSING': {'category':'structure','message':'Fehlende HTML-Tags ergänzen','rationale':'Strukturerhalt notwendig','priority':1,'confidence':0.9},
    'HTML_TAG_EXTRA':   {'category':'structure','message':'Überflüssige HTML-Tags entfernen','rationale':'Verhindert Layout-/A11y-Probleme','priority':1,'confidence':0.88},
    'HTML_ATTR_MISSING':{'category':'structure','message':'Fehlende Attribute ergänzen','rationale':'Semantik/A11y sicherstellen','priority':2,'confidence':0.85},
    'HTML_ATTR_EXTRA':  {'category':'structure','message':'Überflüssige Attribute entfernen','rationale':'Noise & Risiken reduzieren','priority':2,'confidence':0.82},
    # --- Terminologie / Konsistenz ---
    'TERM_PREFERRED_MISSING': {'category':'terminology','message':'Glossar-Sollform einsetzen','rationale':'Terminologie konsistent halten','priority':2,'confidence':0.9},
    'DUPLICATE_INCONSISTENT': {'category':'semantic','message':'Duplikat-Übersetzungen konsolidieren','rationale':'Gleicher Source ⇒ gleiche Zielvariante','priority':1,'confidence':0.92},
    # --- Satzzeichen / Typografie / Case ---
    'PUNCT_MISSING_END': {'category':'quick_fix','message':'Fehlendes Satzendzeichen ergänzen','rationale':'Vollständige Sätze wirken professionell','priority':4,'confidence':0.9},
    'PUNCT_DOUBLE':      {'category':'quick_fix','message':'Mehrfache Satzzeichen reduzieren','rationale':'Wirkt ruhiger/seriöser','priority':4,'confidence':0.95},
    'QUOTE_PLAIN':       {'category':'quick_fix','message':'Typografische Anführungszeichen nutzen („…“)','rationale':'Bessere Lesbarkeit/Typografie','priority':4,'confidence':0.9},
    'QUOTE_MIX':         {'category':'quick_fix','message':'Einheitlichen Anführungsstil wählen','rationale':'Inkonsequenz irritiert Leser','priority':4,'confidence':0.85},
    'S_CASE_INCONSISTENT':{'category':'style','message':'Satzanfang korrekt groß schreiben','rationale':'Formale Konsistenz','priority':4,'confidence':0.85},
    # --- Zahlen/Einheiten ---
    'NUMBER_MISSING': {'category':'structure','message':'Fehlende Zahlen übernehmen','rationale':'Inhaltliche Korrektheit','priority':1,'confidence':0.92},
    'NUMBER_ADDED':   {'category':'structure','message':'Neue Zahlen entfernen','rationale':'Kein Mehr-/Fehleintrag','priority':1,'confidence':0.9},
    'UNIT_DRIFT':     {'category':'structure','message':'Einheiten an Quelle angleichen','rationale':'Vermeidet Messwert-Verwirrung','priority':2,'confidence':0.88},
    # --- Sicherheit / Risiko ---
    'SECURITY_JS_LINK':     {'category':'risk','message':'javascript:-Links entfernen/ersetzen','rationale':'XSS/Clickjacking-Risiko senken','priority':1,'confidence':0.96},
    'SECURITY_EVENT_HANDLER':{'category':'risk','message':'Neue on* Event-Handler entfernen','rationale':'Inline-Handler sind Angriffsfläche','priority':1,'confidence':0.95},
    'SECURITY_SCRIPT_TAG':  {'category':'risk','message':'Neue <script>-Tags entfernen','rationale':'Unerlaubte Skriptausführung verhindern','priority':1,'confidence':0.96},
    'SECURITY_DATA_URI':    {'category':'risk','message':'data:-URIs prüfen/entfernen','rationale':'Privacy/Content-Security beachten','priority':1,'confidence':0.92},
    'RISK_DATA_URI':        {'category':'risk','message':'data:-URIs prüfen/entfernen','rationale':'Privacy/Content-Security beachten','priority':1,'confidence':0.9},
    'RISK_INLINE_STYLE':    {'category':'risk','message':'Inline-Styles vermeiden','rationale':'Besseres CSP/Auslagerung in CSS','priority':3,'confidence':0.75},
    # --- Stil / Lesbarkeit / Semantik ---
    'STYLE_PASSIVE_HEAVY_DE': {'category':'style','message':'Passiv reduzieren – aktiv schreiben','rationale':'Aktiv ist klarer und direkter','priority':3,'confidence':0.75},
    'STYLE_PASSIVE_HEAVY_EN': {'category':'style','message':'Passiv (EN) reduzieren – aktiv schreiben','rationale':'Aktiv kommuniziert präziser','priority':3,'confidence':0.75},
    'READABILITY_TOO_LONG':   {'category':'readability','message':'Satzlänge reduzieren','rationale':'Kompakter = besser lesbar','priority':3,'confidence':0.75},
    'READABILITY_MANY_LONG':  {'category':'readability','message':'Mehrere lange Sätze kürzen','rationale':'Flüssigere Lektüre','priority':3,'confidence':0.75},
    'READABILITY_STACCATTO':  {'category':'readability','message':'Viele Kurzsätze verbinden','rationale':'Besserer Textfluss','priority':3,'confidence':0.72},
}


LONG_SENTENCE_THRESHOLD = 220  # konsistent zu Phase 3


def _truncate(text: str, limit: int = 160) -> str:
    if text is None:
        return ''
    t = text.strip().replace('\n', ' ')
    return t[:limit] + ('…' if len(t) > limit else '')


def _hash_components(*parts: str) -> str:
    import hashlib
    raw = '|'.join(p or '' for p in parts)
    return hashlib.md5(raw.encode('utf-8', 'ignore')).hexdigest()[:12]


AUTO_FIXABLE_CODES = {
    'WS_DOUBLE_SPACE','WS_TRAILING','WS_LEADING','PUNCT_DOUBLE',
    'QUOTE_PLAIN','QUOTE_MIX','ZERO_WIDTH_CHAR'
}

def _generic_fallback_issue_suggestion(code: str) -> Dict[str, object]:
    # Heuristische Kategorie-Erkennung
    lower = code.lower()
    if 'placeholder' in lower:
        cat = 'structure'; msg = 'Platzhalter überprüfen'
        rat = 'Platzhalter konsistent zur Quelle halten'
        prio = 1
    elif 'html' in lower:
        cat = 'structure'; msg = 'HTML-Struktur prüfen'
        rat = 'Korrekte Tags verhindern Render-Probleme'
        prio = 1
    elif 'risk' in lower or 'security' in lower:
        cat = 'risk'; msg = 'Sicherheitsrelevanten Fund verifizieren'
        rat = 'Sicherheits- / Risiko-Indikator prüfen'
        prio = 1
    elif 'semantic' in lower:
        cat = 'semantic'; msg = 'Semantische Abweichung prüfen'
        rat = 'Inhaltliche Konsistenz sicherstellen'
        prio = 2
    elif 'readability' in lower or 'style' in lower:
        cat = 'readability'; msg = 'Lesbarkeit/Stil optimieren'
        rat = 'Verbesserte Lesbarkeit steigert Qualität'
        prio = 3
    else:
        cat = 'quick_fix'; msg = 'Segment überprüfen'
        rat = 'Allgemeine Qualitätsverbesserung möglich'
        prio = 3
    return {'category': cat, 'message': msg, 'rationale': rat, 'priority': prio, 'confidence': 0.5}


def _derive_issue_based_suggestions(issues: List[QAIssue], max_items: int, *, unique_high: bool) -> List[QASuggestion]:
    suggestions: List[QASuggestion] = []
    seen_ids = set()
    high_codes_seen = set()
    # Deterministische Reihenfolge: sortiere nach (code, severity, message)
    sorted_issues = sorted(issues, key=lambda i: (i.code, i.severity, getattr(i, 'message', '')))
    for idx, iss in enumerate(sorted_issues):
        m = ISSUE_SUGGESTION_MAP.get(iss.code) or _generic_fallback_issue_suggestion(iss.code)
        # unique_high: jede Priority 1 nur einmal (Issue Code reicht)
        if unique_high and m['priority'] == 1 and iss.code in high_codes_seen:
            continue
        s_text = getattr(iss, 'source_text', getattr(iss, 'source', '')) or ''
        t_text = getattr(iss, 'target_text', getattr(iss, 'target', '')) or ''
        # Stabile ID ohne Abhängigkeit vom Index: Issue-Code + Snippets
        sid = _hash_components(iss.code, s_text[:40], t_text[:40])
        if sid in seen_ids:
            continue
        seen_ids.add(sid)
        if m['priority'] == 1:
            high_codes_seen.add(iss.code)
        suggestions.append(QASuggestion(
            id=sid,
            category=m['category'],
            message=m['message'],
            rationale=m['rationale'],
            priority=m['priority'],
            confidence=m['confidence'],
            source_snippet=_truncate(s_text),
            target_snippet=_truncate(t_text),
            meta={'issue_code': iss.code, 'severity': iss.severity, 'auto_fixable': bool(iss.code in AUTO_FIXABLE_CODES)},
            auto_fix_hint=bool(iss.code in AUTO_FIXABLE_CODES)
        ))
        if len(suggestions) >= max_items:
            break
        if unique_high and len(high_codes_seen) >= 15:  # harte Grenze für frühes Stoppen
            # Falls viele high Codes – Performance Abbruch
            break
    return suggestions


def _derive_heuristic_sentence_splits(pairs: Iterable[Tuple[str, str]], already: int, max_total: int) -> List[QASuggestion]:
    """Erzeugt Vorschläge zum Teilen sehr langer Sätze (adaptiver Grenzwert).

    Adaptiver Schwellenwert: max(220, int(1.2 * Median Satzlänge über alle Targets))
    """
    suggestions: List[QASuggestion] = []
    if already >= max_total:
        return suggestions
    try:
        # Satz-Längen sammeln – robustere Tokenizer optional (nltk/spacy), sonst Regex-Fallback
        all_sent_lens: List[int] = []
        sent_pattern = re.compile(r'[^.!?]+[.!?]')
        cache_targets: List[Tuple[str,str]] = []
        for src, tgt in pairs:
            cache_targets.append((src, tgt))
            if tgt:
                used = False
                try:
                    # nltk Fallback
                    from nltk.tokenize import sent_tokenize  # type: ignore
                    for s in sent_tokenize(tgt):
                        if s:
                            all_sent_lens.append(len(s))
                    used = True
                except Exception:
                    pass
                if not used:
                    try:
                        # spacy Fallback – erwartet en/de Modelle; heuristisch
                        import spacy  # type: ignore
                        try:
                            nlp = spacy.blank('de')
                        except Exception:
                            nlp = spacy.blank('xx')
                        doc = nlp(tgt)
                        sents = [s.text for s in getattr(doc, 'sents', [])]
                        if sents:
                            for s in sents:
                                all_sent_lens.append(len(s))
                            used = True
                    except Exception:
                        pass
                if not used:
                    for sm in sent_pattern.finditer(tgt):
                        all_sent_lens.append(len(sm.group(0)))
        if all_sent_lens:
            try:
                med = statistics.median(all_sent_lens)
            except Exception:
                med = 220
        else:
            med = 220
        threshold = max(220, int(1.2 * med))
        long_re = re.compile(r'[^.!?]{'+str(threshold)+r',}[.!?]')
        for src, tgt in cache_targets:
            if not tgt:
                continue
            for m in long_re.finditer(tgt):
                seg = m.group(0)
                sid = _hash_components('SPLIT', str(threshold), seg[:40])
                suggestions.append(QASuggestion(
                    id=sid,
                    category='readability',
                    message='Sehr langen Satz in 2–3 kürzere Sätze aufteilen',
                    rationale=f'Satz über adaptiver Länge (>{threshold}) kürzen',
                    priority=3,
                    confidence=0.6,
                    source_snippet=_truncate(src),
                    target_snippet=_truncate(seg),
                    meta={'length': len(seg), 'adaptive_threshold': threshold}
                ))
                if len(suggestions) + already >= max_total:
                    return suggestions
    except Exception:
        return suggestions
    return suggestions


def _rank_and_prune(suggestions: List[QASuggestion], limit: int, *, weight_map: Dict[str,float], compact: bool) -> List[QASuggestion]:
    # Effektive Priorität (niedriger besser) * Kategorie-Gewichtung
    for s in suggestions:
        w = weight_map.get(s.category, 1.0)
        eff = s.priority * max(w, 0.05)
        s.meta['effective_priority'] = eff
    # Optional compact: filtere nach base priority <=3 vor Sortierung
    base = [s for s in suggestions if (not compact) or s.priority <= 3]
    # Stabilere Tie-Breaker: (effective_priority, -confidence, id)
    base.sort(key=lambda s: (s.meta.get('effective_priority', s.priority), -s.confidence, s.id))
    suggestions = base
    pruned: List[QASuggestion] = []
    seen_ids = set()
    for s in suggestions:
        if s.id in seen_ids:
            continue
        seen_ids.add(s.id)
        pruned.append(s)
        if len(pruned) >= limit:
            break
    return pruned

def _derive_doc_level_suggestions(issues: List[QAIssue], existing: int, max_total: int) -> List[QASuggestion]:
    """Dokumentweite Empfehlungen (Pronomen, Glossar, Security-Häufung)."""
    out: List[QASuggestion] = []
    if existing >= max_total or not issues:
        return out
    from collections import Counter
    codes = Counter(i.code for i in issues)
    def _add(id_key: str, msg: str, rat: str, cat='style', prio=2, conf=0.8):
        out.append(QASuggestion(
            id=_hash_components('DOC', id_key),
            category=cat,
            message=msg,
            rationale=rat,
            priority=prio,
            confidence=conf,
            source_snippet='',
            target_snippet='',
            meta={'doc_level': True}
        ))
    if codes.get('PRONOUN_GLOBAL_INCONSISTENT',0) > 0:
        _add('PRONOUN', 'Dokumentweit einheitliche Anrede (Du/Sie) festlegen',
             'Mischformen verwirren Leser:innen und wirken unprofessionell', cat='style', prio=1, conf=0.9)
    if codes.get('TERM_PREFERRED_MISSING',0) >= 3:
        _add('GLOSSARY', 'Glossar-Lücken systematisch schließen',
             'Mehrere Terminologie-Abweichungen erkannt – Glossar-Review hilft', cat='terminology', prio=2, conf=0.85)
    if (codes.get('SECURITY_JS_LINK',0)+codes.get('SECURITY_EVENT_HANDLER',0)+codes.get('SECURITY_SCRIPT_TAG',0)+codes.get('SECURITY_DATA_URI',0)+codes.get('RISK_DATA_URI',0)) >= 1:
        _add('SECURITY', 'Security-Review durchführen (Links/Handler/Data-URIs)',
             'Sicherheitsrelevante Funde erfordern gezielte Prüfung', cat='risk', prio=1, conf=0.92)
    return out


def _maybe_extend_with_llm(suggestions: List[QASuggestion], pairs: List[Tuple[str, str]], enable: bool, limit: int, *, seed: Optional[int], log_errors: bool, llm_model: str = 'llama3', llm_timeout: int = 8) -> None:
    """Optionale (stub) LLM-Erweiterung – generiert paraphrasierte Stil-Tipps.

    Aktuell bewusst minimal / offline-freundlich:
        - Wenn enable False → noop
        - Wenn keine lokale Ollama Instanz erreichbar → silently skip
        - Fügt max 3 zusätzliche Vorschläge hinzu
    """
    if not enable or not pairs:
        return
    try:  # Ollama Embedding/Generate Versuch (fail safe)
        import requests, json
        if seed is not None:
            random.seed(seed)
        host = 'http://localhost:11434'
        test = requests.get(host, timeout=1)
        if test.status_code >= 500:
            return
        # Wähle 1–2 repräsentative Zielsegmente mittlerer Länge
        mid_segments = [t for (_s, t) in pairs if t and 40 < len(t) < 280]
        if not mid_segments:
            return
        random.shuffle(mid_segments)
        sample = mid_segments[:2]
        prompt = (
            "Erzeuge kompakte (max 90 Zeichen) Verbesserungshinweise auf Deutsch zu Stil/Lesbarkeit für folgende Übersetzungssegmente. "
            "Keine Aufzählungszeichen, nur einzelne prägnante Sätze. Segmente:\n" + '\n'.join(f'- {x[:160]}' for x in sample)
        )
        resp = requests.post(f"{host}/api/generate", json={"model": llm_model, "prompt": prompt, "stream": False}, timeout=max(1, int(llm_timeout)))
        if not resp.ok:
            return
        data = resp.json()
        text = (data.get('response') or '')[:4000]  # Truncation vor Parsing
        # Heuristisch Zeilen separieren
        lines = [l.strip('-• ').strip() for l in re.split(r'[\r\n]+', text) if l.strip()]
        added = 0
        for line in lines:
            if len(line) < 15 or len(line) > 95:
                continue
            sid = _hash_components('LLM', line[:40])
            suggestions.append(QASuggestion(
                id=sid,
                category='style',
                message=line[:160],
                rationale='LLM-basierter Stilverbesserungs-Hinweis',
                priority=3,
                confidence=0.55,
                source_snippet='',
                target_snippet='',
                meta={'llm': True},
                auto_fix_hint=False
            ))
            added += 1
            if added >= 3 or len(suggestions) >= limit:
                break
    except Exception as e:
        if log_errors:
            suggestions.append(QASuggestion(
                id=_hash_components('LLM','ERR', str(e)[:30]),
                category='semantic',
                message='LLM-Erweiterung fehlgeschlagen – Heuristik genutzt',
                rationale='Fallback sichert deterministisches Verhalten',
                priority=5,
                confidence=0.3,
                source_snippet='',
                target_snippet='',
                meta={'llm_error': str(e)[:200]},
                auto_fix_hint=False
            ))
        return


def run_phase6_suggestions(pairs: Iterable[Tuple[str, str]], issues: List[QAIssue], *,
                            max_suggestions: int = 40,
                            enable_llm: bool = False,
                            weight_semantic: float = 1.0,
                            weight_risk: float = 1.0,
                            unique_high: bool = False,
                            compact: bool = False,
                            deterministic_seed: Optional[int] = None,
                            log_llm_errors: bool = False,
                            enable_sentence_splits: bool = True,
                            enable_doc_suggestions: bool = True,
                            llm_model: str = 'llama3',
                            llm_timeout: int = 8) -> List[QASuggestion]:
    """Erzeugt priorisierte Vorschläge (Phase 6).

    Parameters
    ----------
    pairs : Iterable[Tuple[str,str]]
        Sequenz (source, target) Segmente
    issues : List[QAIssue]
        Akkumulierte Issues (Phasen 1–5) – optional (kann leer sein)
    max_suggestions : int
        Obergrenze Ergebnisliste (default 40)
    enable_llm : bool
        Versuche LLM-Erweiterung (lokal) – heuristische Vorschläge bleiben als Basis
    """
    try:
        pairs_list = list(pairs)
    except Exception:
        pairs_list = []

    heuristics: List[QASuggestion] = []
    try:
        heuristics.extend(_derive_issue_based_suggestions(issues, max_suggestions, unique_high=unique_high))
    except Exception:
        pass
    if enable_sentence_splits:
        try:
            heuristics.extend(_derive_heuristic_sentence_splits(pairs_list, len(heuristics), max_suggestions))
        except Exception:
            pass
    if enable_doc_suggestions:
        try:
            # Dokumentweite Empfehlungen (z. B. Pronomen, Glossar, Security)
            heuristics.extend(_derive_doc_level_suggestions(issues, len(heuristics), max_suggestions))
        except Exception:
            pass

    # Optionale LLM Erweiterung – in-place Append
    try:
        _maybe_extend_with_llm(heuristics, pairs_list, enable_llm, max_suggestions, seed=deterministic_seed, log_errors=log_llm_errors, llm_model=llm_model, llm_timeout=llm_timeout)
    except Exception:
        pass

    # Ranking + Limit + Gewichtung
    weight_map = {'semantic': weight_semantic, 'risk': weight_risk}
    try:
        ranked = _rank_and_prune(heuristics, max_suggestions, weight_map=weight_map, compact=compact)
    except Exception:
        ranked = heuristics[:max_suggestions]

    # Telemetrie-Summary anhängen (falls Platz)
    try:
        if len(ranked) < max_suggestions:
            total_pairs = len(pairs_list)
            auto_fixables = sum(1 for s in ranked if s.auto_fix_hint)
            ratio = (auto_fixables / max(1, len(ranked)))
            # severity_distribution aus Issues ableiten
            from collections import Counter
            sev_dist = Counter(getattr(i,'severity','info') for i in (issues or []))
            ranked.append(QASuggestion(
                id=_hash_components('META','SUMMARY', str(total_pairs)),
                category='meta',
                message='Phase6 Zusammenfassung',
                rationale='Überblick Telemetrie',
                priority=5,
                confidence=1.0,
                source_snippet='',
                target_snippet='',
                meta={'total_pairs': total_pairs, 'suggestion_count': len(ranked), 'auto_fixable_ratio': round(ratio,3), 'count_auto_fixable': auto_fixables, 'severity_distribution': dict(sev_dist)},
                auto_fix_hint=False
            ))
    except Exception:
        pass
    return ranked


__all__ = [
    'QASuggestion',
    'run_phase6_suggestions'
]
