"""Grammatik- & Rechtschreibprüfung (hybride Implementierung).

Diese Datei ist die umbenannte und weiter geführte Fassung von 'grammar_quality.py'.
Alle zukünftigen Imports bitte über 'quality_gui_grammar' vornehmen.

Ziele:
- Optionale Nutzung externer Bibliotheken (language_tool_python, hunspell) nur wenn vorhanden
- Schnelle Heuristiken als Vorfilter
- Languagetool Tiefen-Analyse nur bei Bedarf (Heuristik-Schwelle)
- Optionale KI (Ollama) Tiefen-Pass für stark fehlerverdächtige Segmente
- Auto-Spracherkennung (leichtgewichtig) mit Fallback

Ergebnis-Einträge (Finding Dict):
{
  'rule_id': str,
  'severity': 'minor'|'major'|'critical',
  'message': str,
  'suggestion': str,
  'source_excerpt': str,
  'segment_index': int,
  'checker': 'heuristic'|'hunspell'|'languagetool'|'ollama'
}
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import re, json, os, bisect, importlib, logging

# Modul-Logger für einmalige Warnungen
_logger = logging.getLogger(__name__)
_LT_UNSUPPORTED_WARNED: set = set()  # Verhindert Log-Spam bei wiederholten LT-Sprachfehlern

# -------------------- Optionale Imports --------------------

def _import_optional(name: str):
    """Importiert ein Modul optional - gibt None zurück wenn nicht verfügbar.
    
    Verwendet importlib.import_module() statt __import__ für sauberere Semantik.
    """
    try:
        return importlib.import_module(name)
    except Exception:
        return None

_language_tool = _import_optional('language_tool_python')
_hunspell = _import_optional('hunspell')  # Benötigt evtl. System-Wörterbücher

# -------------------- Regex & Konstanten --------------------
# Erweitert: Auch "..." (Ellipse/Auslassungspunkte) und "…" (Unicode-Ellipse) als gültiges Satzende
_SENT_END = re.compile(r"(?:\.{2,}|\u2026|[\.!?])[\s\"'»«""‚'')\\]]*$")
_MULTI_SPACES = re.compile(r"\s{3,}")
_DOUBLE_PUNCT = re.compile(r"[\?!]{2,}")
_START_LOWER_SENT = re.compile(r"^[a-zäöüß]")
COMMON_LOWER_PROPER = {"deutschland","montag","januar"}


class GrammarChecker:
    """Hybrider Grammatik-/Rechtschreib-Checker.

    Parameter
    ---------
    enable_languagetool : bool
        LanguageTool Nutzung (falls Bibliothek verfügbar)
    enable_hunspell : bool
        Hunspell Nutzung (sofern Wörterbücher auffindbar)
    enable_ollama : bool
        KI Tiefen-Pass aktivieren
    ratio_threshold : float
        Anteil (0..1) der Segmente mit heuristischen Findings, ab dem Tiefen-Analyse startet
    batch_lt_min_segments : int
        Ab dieser Segmentanzahl wird LanguageTool als Batch über den Gesamttest ausgeführt
    """

    def __init__(self,
                 enable_languagetool: bool = True,
                 enable_hunspell: bool = True,
                 enable_ollama: bool = True,
                 ratio_threshold: float = 0.15,
                 batch_lt_min_segments: int = 40):
        """Initialisiert den hybriden Checker und speichert Laufzeit-Flags.

        Alle Parameter besitzen sichere Default-Werte. Optionale Bibliotheken
        werden nur aktiviert, falls importierbar.
        """
        self.enable_languagetool = enable_languagetool and (_language_tool is not None)
        self.enable_hunspell = enable_hunspell and (_hunspell is not None)
        self.enable_ollama = enable_ollama  # Verfügbarkeit später geprüft
        self.ratio_threshold = max(0.0, min(1.0, ratio_threshold))
        self.batch_lt_min_segments = max(5, batch_lt_min_segments)
        # LanguageTool Runtime Objekte
        self._lt_tool = None
        self._lt_code = None  # aktuell initialisierter LanguageTool Code (de-DE/en-US)
        # Detektierte Sprache für Run (Hunspell Guard)
        self._detected_lang_for_run = None

    # -------- Sprache erkennen (erweitert für mehr Sprachen) --------
    # Mapping von langdetect-Codes zu LanguageTool-Codes
    # HINWEIS: Nicht alle LT-Installationen unterstützen alle Sprachen!
    # Besonders zh (Chinesisch), ja (Japanisch), ar (Arabisch) etc. sind oft nicht verfügbar.
    # Bei fehlender Unterstützung wird einmalig gewarnt und auf en-US gefallbackt.
    LANG_TO_LT_CODE = {
        'de': 'de-DE', 'en': 'en-US', 'fr': 'fr', 'es': 'es',
        'it': 'it', 'pt': 'pt-PT', 'nl': 'nl', 'pl': 'pl-PL',
        'ru': 'ru-RU', 'uk': 'uk-UA', 'cs': 'cs-CZ', 'sk': 'sk-SK',
        'ro': 'ro-RO', 'ca': 'ca-ES', 'gl': 'gl-ES', 'ast': 'ast-ES',
        'ja': 'ja-JP', 'zh': 'zh-CN', 'ar': 'ar', 'fa': 'fa',  # Diese oft nicht unterstützt!
        'el': 'el-GR', 'da': 'da-DK', 'sv': 'sv', 'nb': 'nb', 'nn': 'nn-NO',
        'be': 'be-BY', 'sl': 'sl-SI', 'tl': 'tl-PH', 'ta': 'ta-IN',
        'br': 'br-FR', 'km': 'km-KH', 'eo': 'eo', 'ga': 'ga-IE',
    }
    
    # Unterstützte Sprachen für Heuristiken
    SUPPORTED_LANGUAGES = {'de', 'en', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru'}
    
    def _detect_language(self, segments: List[str]) -> str:
        """Erkennt die Sprache automatisch - unterstützt mehr Sprachen als nur DE/EN."""
        try:
            _ld = _import_optional('langdetect')
            if _ld:
                sample = "\n".join(segments)[:6000]
                try:
                    # Reproduzierbare Ergebnisse
                    if hasattr(_ld, 'DetectorFactory'):
                        _ld.DetectorFactory.seed = 0
                    lang = _ld.detect(sample)
                    if isinstance(lang, str):
                        # Hauptsprache extrahieren (z.B. 'zh-cn' -> 'zh')
                        base_lang = lang.split('-')[0].lower()
                        if base_lang in self.SUPPORTED_LANGUAGES or base_lang in self.LANG_TO_LT_CODE:
                            return base_lang
                except Exception:
                    pass
        except Exception:
            pass
        
        # Fallback: Erweiterte Heuristik für mehrere Sprachen
        return self._heuristic_language_detection(segments)
    
    def _heuristic_language_detection(self, segments: List[str]) -> str:
        """Fallback-Heuristik für Spracherkennung wenn langdetect nicht verfügbar."""
        try:
            text = " ".join(segments)[:8000].lower()
            if not text:
                return 'de'
            # Padding mit Spaces, damit Wort-Lookup `f' {word} '` auch fuer
            # Begriffe am Anfang/Ende des Textes greift.
            padded_text = ' ' + text + ' '
            
            # Sprachindikatoren mit Gewichtung
            indicators = {
                'de': {
                    'chars': 'äöüß', 'weight': 3,
                    'words': {'und', 'der', 'die', 'das', 'ist', 'für', 'mit', 'nicht', 'werden', 'haben', 'wird', 'sind', 'nach', 'über', 'auch', 'kann', 'einer', 'diese', 'diesem'}
                },
                'en': {
                    'chars': '', 'weight': 0,
                    'words': {'the', 'and', 'is', 'for', 'with', 'are', 'this', 'that', 'have', 'from', 'will', 'not', 'been', 'which', 'can', 'would', 'their', 'there', 'about'}
                },
                'fr': {
                    'chars': 'éèêëàâùûôîïç', 'weight': 2,
                    'words': {'le', 'la', 'les', 'un', 'une', 'des', 'est', 'pour', 'dans', 'que', 'qui', 'sur', 'avec', 'cette', 'sont', 'nous', 'vous', 'être', 'avoir', "c'est", "n'est"}
                },
                'es': {
                    'chars': 'ñáéíóú¿¡', 'weight': 3,
                    'words': {'el', 'la', 'los', 'las', 'una', 'del', 'que', 'es', 'para', 'con', 'por', 'como', 'más', 'pero', 'sus', 'entre', 'desde', 'hasta', 'sobre'}
                },
                'it': {
                    'chars': 'àèéìòù', 'weight': 2,
                    'words': {'il', 'la', 'le', 'una', 'della', 'che', 'per', 'con', 'non', 'sono', 'come', 'questo', 'questa', 'più', 'anche', 'loro', 'essere', 'stato', 'tutti'}
                },
                'pt': {
                    'chars': 'ãõçáéíóúâêô', 'weight': 2,
                    'words': {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'que', 'para', 'com', 'não', 'por', 'como', 'mais', 'seu', 'sua', 'são', 'está', 'foi'}
                },
                'nl': {
                    'chars': '', 'weight': 0,
                    'words': {'de', 'het', 'een', 'van', 'en', 'is', 'op', 'te', 'dat', 'voor', 'met', 'zijn', 'niet', 'aan', 'er', 'ook', 'maar', 'bij', 'naar', 'worden'}
                },
            }
            
            scores = {}
            for lang, data in indicators.items():
                score = 0
                # Sonderzeichen werten
                if data['chars']:
                    score += sum(text.count(c) for c in data['chars']) * data['weight']
                # Wörter zählen
                for word in data['words']:
                    if f' {word} ' in padded_text:
                        score += 2
                scores[lang] = score
            
            best_lang = max(scores, key=scores.get)
            return best_lang if scores[best_lang] >= 4 else 'de'
        except Exception:
            return 'de'

    # -------- Öffentliche API --------
    def analyze_segments(self, segments: List[str], language: str = 'de') -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        if not segments:
            return findings
        if not language or language.lower() in ('auto','detect'):
            language = self._detect_language(segments)
        # für spätere Passes (Hunspell Sprach-Guard)
        self._detected_lang_for_run = language

        heuristic_scores = []
        for idx, seg in enumerate(segments):
            seg_findings = self._heuristics(seg, idx)
            findings.extend(seg_findings)
            heuristic_scores.append(len(seg_findings))
            if self.enable_hunspell:
                findings.extend(self._hunspell_pass(seg, idx))

        flagged = sum(1 for c in heuristic_scores if c > 0)
        ratio_flagged = flagged / max(1, len(segments))
        deeper_needed = ratio_flagged >= self.ratio_threshold

        if deeper_needed and self.enable_languagetool:
            findings.extend(self._languagetool_pass(segments, language))

        if deeper_needed and self.enable_ollama:
            # Lesbarere Bildung der stark auffälligen Segmente (Original-Index, Text)
            heavy_pairs: List[Tuple[int, str]] = [ (i, s) for i, s in enumerate(segments) if heuristic_scores[i] >= 2 ]
            if heavy_pairs:
                findings.extend(self._ollama_pass(heavy_pairs, language))
        return findings

    # -------- Heuristiken --------
    def _heuristics(self, text: str, idx: int) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if not text or len(text.strip()) < 4:
            return out
        stripped = text.strip()
        # Satzende-Prüfung: Nur bei echten Sätzen (nicht bei Kontaktzeilen, Listen, Überschriften)
        _is_contact_or_list = bool(re.search(r'@[\w.-]+\.\w|https?://|Tel\.|Fax[:\s]|\+\d{2}|\d{3,}$|:$', stripped))
        if not _SENT_END.search(stripped) and len(stripped.split()) >= 8 and not _is_contact_or_list:
            out.append(self._mk("heuristic.no_sentence_end", "Satz endet nicht mit Punkt/!/?", stripped[-40:], idx, 'minor'))
        if _MULTI_SPACES.search(stripped):
            out.append(self._mk("heuristic.multi_spaces", "Mehrfache Leerzeichen", stripped[:60], idx, 'minor'))
        if _DOUBLE_PUNCT.search(stripped):
            out.append(self._mk("heuristic.double_punct", "Übermäßige Interpunktion", stripped[:60], idx, 'minor'))
        m = re.match(r"[A-Za-zÄÖÜäöüß]+", stripped)
        first_word = m.group(0).lower() if m else ""
        if _START_LOWER_SENT.match(stripped) and first_word not in COMMON_LOWER_PROPER:
            out.append(self._mk("heuristic.lower_start", "Satz beginnt mit Kleinbuchstaben", stripped[:60], idx, 'minor'))
        return out

    # -------- Hunspell --------
    def _hunspell_pass(self, text: str, idx: int) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        try:
            if not self.enable_hunspell or _hunspell is None:
                return out
            # Einfache Sprachwache: aktuell nur Deutsch aktiv prüfen
            lang = getattr(self, "_detected_lang_for_run", None)
            if lang and not str(lang).lower().startswith("de"):
                return out
            hs = getattr(self, '_hunspell_obj', None)
            if hs is None:
                # Kandidatenpfade für Wörterbücher
                candidates = []
                base_candidates = [
                    '/usr/share/hunspell', '/usr/share/myspell', '/Library/Spelling',
                    os.path.expanduser('~/.hunspell'), 'C:/Hunspell', 'C:/Program Files/Hunspell'
                ]
                for base in base_candidates:
                    dic = os.path.join(base, 'de_DE.dic')
                    aff = os.path.join(base, 'de_DE.aff')
                    if os.path.exists(dic) and os.path.exists(aff):
                        candidates.append((dic, aff))
                # Fallback: aktuelles Verzeichnis
                if os.path.exists('de_DE.dic') and os.path.exists('de_DE.aff'):
                    candidates.append(('de_DE.dic', 'de_DE.aff'))
                loaded = False
                for dic, aff in candidates:
                    try:
                        self._hunspell_obj = _hunspell.HunSpell(dic, aff)  # type: ignore
                        hs = self._hunspell_obj
                        loaded = True
                        break
                    except Exception:
                        continue
                if not loaded:
                    # Letzter Versuch: Standardnamen (wie vorher)
                    try:
                        self._hunspell_obj = _hunspell.HunSpell('de_DE.dic', 'de_DE.aff')  # type: ignore
                        hs = self._hunspell_obj
                        loaded = True
                    except Exception:
                        pass
                if not loaded:
                    self.enable_hunspell = False
                    return out
            tokens = [w for w in re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'-]{2,}", text)]
            for w in tokens:
                try:
                    if not hs.spell(w):  # type: ignore
                        sugg = hs.suggest(w)[:3] if hasattr(hs, 'suggest') else []  # type: ignore
                        out.append(self._mk("hunspell.spelling", f"Möglicher Rechtschreibfehler: {w}", w, idx, 'minor', suggestion=", ".join(sugg)))
                except Exception:
                    continue
        except Exception:
            pass
        return out

    # -------- LanguageTool --------
    def _get_lt_code(self, language: str) -> str:
        """Konvertiert erkannte Sprache zu LanguageTool-Code mit erweiterten Sprachen."""
        lang_lower = language.lower().split('-')[0] if language else 'de'
        # Direkt aus Mapping holen oder Fallback
        if lang_lower in self.LANG_TO_LT_CODE:
            return self.LANG_TO_LT_CODE[lang_lower]
        # Legacy-Fallbacks
        if lang_lower.startswith('de'):
            return 'de-DE'
        if lang_lower.startswith('en'):
            return 'en-US'
        if lang_lower.startswith('fr'):
            return 'fr'
        if lang_lower.startswith('es'):
            return 'es'
        if lang_lower.startswith('it'):
            return 'it'
        if lang_lower.startswith('pt'):
            return 'pt-PT'
        if lang_lower.startswith('nl'):
            return 'nl'
        if lang_lower.startswith('pl'):
            return 'pl-PL'
        if lang_lower.startswith('ru'):
            return 'ru-RU'
        # Default zu Deutsch
        return 'de-DE'
    
    def _languagetool_pass(self, segments: List[str], language: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if not self.enable_languagetool or _language_tool is None:
            return out
        try:
            code = self._get_lt_code(language)
            # Neu-Initialisierung bei Sprachwechsel oder erstmaliger Nutzung
            if self._lt_tool is None or self._lt_code != code:
                # Bei Sprachwechsel altes Tool sauber schliessen, sonst leakt
                # LanguageTool den lokalen Java-Subprozess (jeweils mehrere
                # hundert MB RAM pro vergessener Instanz).
                if self._lt_tool is not None and self._lt_code != code:
                    try:
                        close = getattr(self._lt_tool, 'close', None)
                        if callable(close):
                            close()
                    except Exception:
                        pass
                    self._lt_tool = None
                try:
                    self._lt_tool = _language_tool.LanguageTool(code)  # type: ignore
                    self._lt_code = code
                except Exception as e:
                    # Sprache nicht unterstützt - einmalig warnen
                    if code not in _LT_UNSUPPORTED_WARNED:
                        _LT_UNSUPPORTED_WARNED.add(code)
                        _logger.warning("[LanguageTool] Sprache '%s' nicht unterstützt: %s", code, e)
                    # Fallback zu Englisch falls noch kein Tool initialisiert
                    if self._lt_tool is None:
                        try:
                            self._lt_tool = _language_tool.LanguageTool('en-US')  # type: ignore
                            self._lt_code = 'en-US'
                        except Exception:
                            self.enable_languagetool = False
                            return out
            use_batch = len(segments) >= self.batch_lt_min_segments
            if not use_batch:
                # Einzelprüfung (bestehendes Verhalten)
                for idx, seg in enumerate(segments):
                    if not seg or len(seg.strip()) < 4:
                        continue
                    try:
                        matches = self._lt_tool.check(seg)  # type: ignore
                    except Exception as lt_err:
                        _logger.debug("[LanguageTool] check failed for segment %d: %s", idx, lt_err)
                        continue
                    out.extend(self._lt_matches_to_findings(matches, seg, idx))
            else:
                # Batch: Segmente joinen und Offsets mappen
                separator = "\n"
                joined = separator.join(segments)
                # Startoffsets berechnen
                starts = []
                pos = 0
                for s in segments:
                    starts.append(pos)
                    pos += len(s) + len(separator)
                try:
                    matches = self._lt_tool.check(joined)  # type: ignore
                except Exception as lt_batch_err:
                    _logger.warning("[LanguageTool] batch check failed: %s", lt_batch_err)
                    return out
                for m in matches:
                    try:
                        offset = getattr(m, 'offset', 0)
                        # Position Segment index via bisect
                        idx = bisect.bisect_right(starts, offset) - 1
                        if idx < 0 or idx >= len(segments):
                            continue
                        seg = segments[idx]
                        local_offset = offset - starts[idx]
                        excerpt = ''
                        try:
                            excerpt = seg[max(0, local_offset-20):local_offset+40]
                        except Exception:
                            excerpt = seg[:60]
                        # Temporäre Einzel-Match Liste reuse
                        out.extend(self._lt_matches_to_findings([m], seg, idx, custom_excerpt=excerpt))
                    except Exception:
                        continue
        except Exception:
            pass
        return out

    def _lt_matches_to_findings(self, matches, seg: str, idx: int, custom_excerpt: str | None = None) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for m in matches:
            try:
                rule_id = getattr(m, 'ruleId', 'LT_RULE')
                category_obj = getattr(m, 'category', None)
                category = (
                    getattr(getattr(m, 'ruleIssueType', None), 'name', '')
                    or getattr(category_obj, 'id', '')
                    or (category_obj.get('id') if isinstance(category_obj, dict) else '')
                )
                msg = getattr(m, 'message', '')
                repl = self._lt_replacements_str(m)
                severity = self._map_lt_severity(rule_id, category, msg)
                excerpt = custom_excerpt if custom_excerpt is not None else ''
                if not excerpt:
                    try:
                        offset = getattr(m, 'offset', 0)
                        excerpt = seg[max(0, offset-20):offset+40]
                    except Exception:
                        excerpt = seg[:60]
                out.append(self._mk(f"grammar.lt.{rule_id}", msg, excerpt, idx, severity, suggestion=repl))
            except Exception:
                continue
        return out

    def _map_lt_severity(self, rule_id: str, category: str, msg: str) -> str:
        rid = (rule_id or '').upper()
        cat = (category or '').upper()
        lower_msg = (msg or '').lower()
        if 'MORFOLOGIK' in rid or 'SPELL' in rid or 'TYPOS' in cat:
            return 'minor'
        if any(k in rid for k in ('GRAMMAR','AGREEMENT','TENSE','VERB','CASE')) or any(k in cat for k in ('GRAMMAR','AGREEMENT')):
            if any(x in lower_msg for x in ('falsche kongruenz','falsche kasus','grundlegender grammatikfehler','satzfragment')):
                return 'critical'
            return 'major'
        if 'CONFUSED_WORDS' in rid and ('bedeutung' in lower_msg or 'verwechselt' in lower_msg):
            return 'major'
        return 'minor'

    def _lt_replacements_str(self, m) -> str:
        """Extrahiert bis zu drei Replacement-Kandidaten robust (String, Dict mit 'value', Objekt mit .value)."""
        try:
            reps = getattr(m, 'replacements', None)
            if not reps:
                return ''
            out = []
            for r in reps[:3]:  # type: ignore
                if isinstance(r, str):
                    out.append(r)
                elif isinstance(r, dict) and 'value' in r:
                    out.append(str(r['value']))
                else:
                    val = getattr(r, 'value', None)
                    if val:
                        out.append(str(val))
            return ", ".join(out)
        except Exception:
            return ''

    # -------- Ollama --------
    def _ollama_pass(self, segments_with_ids: List[Tuple[int, str]], language: str) -> List[Dict[str, Any]]:
        """Ollama Analyse mit Batching; behält Original-Segment-IDs bei und entfernt Duplikate."""
        out: List[Dict[str, Any]] = []
        _call_fn = None
        try:
            from ki_module import _call_ollama  # type: ignore
            _call_fn = _call_ollama
        except Exception:
            pass
        if _call_fn is None:
            try:
                from quality_gui_ollama_suggestions import _call_ollama as _fallback_call  # type: ignore
                _call_fn = _fallback_call
            except Exception:
                pass
        if _call_fn is None:
            return out

        if not segments_with_ids:
            return out

        MAX_PER_BATCH = 24

        def _build_prompt(batch: List[Tuple[int, str]]) -> str:
            lang_hint = "deutsch" if str(language).lower().startswith("de") else "englisch"
            header = (
                "Analysiere nur KRITISCHE oder klare Grammatik-/Rechtschreibfehler (keine Stilfragen). "
                "Sprache: " + lang_hint + ". "
                "Gib ausschließlich JSON-LINES aus, eine Zeile pro Fehler, ohne zusätzlichen Text. "
                "Schema-Schlüssel: segment_index(int), rule_id(str), severity('minor'|'major'|'critical'), "
                "message(str), suggestion(str), excerpt(str). "
                "Nutze für segment_index genau die Nummer in eckigen Klammern. "
                "Wenn keine Fehler gefunden werden, gib GAR NICHTS aus."
            )
            joined = "\n".join(f"[{orig}] {text}" for (orig, text) in batch)
            return f"{header}\n\n{joined}\n"

        def _parse_json_like(raw: str) -> List[Dict[str, Any]]:
            """Robuster Parser: JSON-Lines oder gesamtes JSON, entfernt optional Codefences (```json ... ```)."""
            parsed: List[Dict[str, Any]] = []
            if not isinstance(raw, str):
                return parsed
            s = raw.strip()
            # Codefences entfernen
            if s.startswith("```"):
                # erste Zeile mit evtl. Sprache entfernen
                s = re.sub(r"^```[\w-]*\n", "", s)
                if s.endswith("```"):
                    s = s[:-3].rstrip()
            # JSON-Lines Versuch
            for line in s.splitlines():
                line = line.strip()
                if not line or not (line.startswith("{") and line.endswith("}")):
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        parsed.append(obj)
                except Exception:
                    pass
            if parsed:
                return parsed
            # Gesamtes JSON
            try:
                data = json.loads(s)
                if isinstance(data, list):
                    parsed.extend([x for x in data if isinstance(x, dict)])
                elif isinstance(data, dict):
                    parsed.append(data)
            except Exception:
                pass
            return parsed

        # Modell & Timeout konfigurierbar via Umgebungsvariablen
        model = os.getenv("QUALITY_GUI_OLLAMA_MODEL", "mistral")
        try:
            timeout = int(os.getenv("QUALITY_GUI_OLLAMA_TIMEOUT", "90"))
        except Exception:
            timeout = 90

        for start in range(0, len(segments_with_ids), MAX_PER_BATCH):
            batch = segments_with_ids[start:start + MAX_PER_BATCH]
            try:
                raw = _call_fn(_build_prompt(batch), model=model, timeout=timeout)
            except Exception as ollama_err:
                _logger.warning("[Ollama grammar] batch %d failed: %s", start // MAX_PER_BATCH, ollama_err)
                continue
            objs = _parse_json_like(raw)
            for obj in objs:
                try:
                    idx = obj.get("segment_index")
                    if isinstance(idx, str) and idx.isdigit():
                        idx = int(idx)
                    if not isinstance(idx, int):
                        m2 = re.search(r"\[(\d+)\]", str(obj.get("excerpt", "")))
                        idx = int(m2.group(1)) if m2 else -1
                    # rule_id normalisieren: immer 'ollama.' Prefix erzwingen
                    raw_rule = obj.get("rule_id") or "grammar"
                    if not str(raw_rule).startswith("ollama."):
                        rule_id = f"ollama.{raw_rule}"
                    else:
                        rule_id = str(raw_rule)
                    sev = (obj.get("severity") or "minor").lower()
                    if sev not in ("minor", "major", "critical"):
                        sev = "minor"
                    msg = obj.get("message") or "Unklare Meldung"
                    # critical nur bei begründeten Schlüsselwörtern
                    if sev == "critical" and not any(
                        k in msg.lower() for k in ("schwer", "critical", "grober", "fatal", "fragment", "satzfragment", "unverständlich", "severe", "ungrammatical")
                    ):
                        sev = "major"
                    out.append({
                        "rule_id": rule_id,
                        "severity": sev,
                        "message": msg,
                        "suggestion": obj.get("suggestion") or "",
                        "source_excerpt": obj.get("excerpt") or "",
                        "segment_index": idx,
                        "checker": "ollama",
                    })
                except Exception:
                    continue

        seen = set()
        uniq: List[Dict[str, Any]] = []
        for f in out:
            key = (f.get("segment_index"), f.get("rule_id"), f.get("message"), f.get("source_excerpt"))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(f)
        return uniq

    # -------- Helper --------
    def _infer_checker(self, rule_id: str) -> str:
        """Ermittle den Checker-Namen aus dem rule_id Pattern."""
        rid = str(rule_id)
        if rid.startswith("heuristic."):
            return "heuristic"
        if rid.startswith("hunspell."):
            return "hunspell"
        if rid.startswith("ollama"):
            return "ollama"
        if ".lt." in rid or rid.startswith("languagetool."):
            return "languagetool"
        return rid.split(".")[0] or "other"

    def close(self) -> None:
        """Gibt LanguageTool-Ressourcen frei (Server-Prozess beenden)."""
        if self._lt_tool is not None:
            try:
                self._lt_tool.close()  # type: ignore
            except Exception:
                pass
            self._lt_tool = None

    def _mk(self, rule_id: str, message: str, excerpt: str, segment_index: int, severity: str, suggestion: str = '') -> Dict[str, Any]:
        checker = self._infer_checker(rule_id)
        if checker in ('heuristic','hunspell'):
            severity = 'minor'
        if severity not in ('minor','major','critical'):
            severity = 'minor'
        return {
            'rule_id': rule_id,
            'message': message,
            'source_excerpt': excerpt,
            'segment_index': segment_index,
            'severity': severity,
            'suggestion': suggestion,
            'checker': checker,
        }


_default_checker: GrammarChecker | None = None

def run_grammar_analysis(segments: List[str], language: str = 'de') -> List[Dict[str, Any]]:
    """Convenience-Funktion mit gecachtem GrammarChecker (für wiederholte Aufrufe)."""
    global _default_checker
    if _default_checker is None:
        _default_checker = GrammarChecker()
    return _default_checker.analyze_segments(segments, language)


__all__ = [
    'GrammarChecker',
    'run_grammar_analysis',
]
