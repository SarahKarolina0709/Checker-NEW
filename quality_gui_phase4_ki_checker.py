"""Phase 4: KI-gestützte Semantikprüfung (Ausgangstext ↔ Übersetzung via Ollama).

Vergleicht jeden Ausgangstext mit seiner Übersetzung und meldet inhaltliche
Fehler (falsche Bedeutung, fehlende Passagen, Terminologie-Abweichungen).
Gibt List[QAIssue] zurück – dieselbe Struktur wie Phase 1-3.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Iterable, List, Tuple

logger = logging.getLogger(__name__)

# Sprachcode-Mapping kurz → BCP-47
_LANG_MAP: dict[str, str] = {
    'de': 'de-DE', 'en': 'en-US', 'fr': 'fr-FR',
    'es': 'es-ES', 'it': 'it-IT', 'pt': 'pt-PT',
    'nl': 'nl-NL', 'pl': 'pl-PL', 'ru': 'ru-RU',
    'ja': 'ja-JP', 'zh': 'zh-CN', 'ko': 'ko-KR',
    'ar': 'ar-SA', 'tr': 'tr-TR', 'sv': 'sv-SE',
    'da': 'da-DK', 'fi': 'fi-FI', 'nb': 'nb-NO',
    'cs': 'cs-CZ', 'hu': 'hu-HU', 'ro': 'ro-RO',
    'uk': 'uk-UA', 'el': 'el-GR', 'bg': 'bg-BG',
    'sk': 'sk-SK', 'sl': 'sl-SI', 'hr': 'hr-HR',
    'et': 'et-EE', 'lv': 'lv-LV', 'lt': 'lt-LT',
    'th': 'th-TH', 'vi': 'vi-VN', 'id': 'id-ID',
    'he': 'he-IL', 'hi': 'hi-IN',
}


def _to_bcp47(lang: str) -> str:
    """Normalisiert Sprachcode zu BCP-47 (z. B. 'de' → 'de-DE')."""
    if not lang:
        return 'de-DE'
    normalized = lang.strip().replace('_', '-')
    if '-' in normalized:
        return normalized
    code = normalized.lower()
    return _LANG_MAP.get(code, f'{code}-{code.upper()[:2]}')


def _parse_ki_response(response: str) -> list[dict]:
    """Parst JSON-Array aus Ollama-Antwort (robust gegen Markdown-Codeblöcke).

    Erwartet Format:
        [{"error_text": "...", "context": "...", "explanation": "..."}, ...]
    """
    if not response:
        return []
    stripped = response.strip()

    # Bekannte Fehler-/Abbruchantworten sofort überspringen
    skip_prefixes = (
        'KI-Analyse übersprungen', 'KI-Analyse uebersprungen',
        'Ollama', 'Fehler', 'Error:', 'Hinweis:',
    )
    if any(stripped.startswith(p) for p in skip_prefixes):
        logger.debug('Phase4: Ollama-Antwort ist Fehlermeldung – übersprungen')
        return []

    # JSON-Array suchen – auch eingebettet in Markdown-Codeblock oder Vortext.
    # Ollama schreibt manchmal "Hier ist [1] meine Antwort: [{...}]" – ein einfaches
    # find('[')/rfind(']') würde dann den falschen Substring extrahieren.
    # Strategie: alle Positionen von '[' und ']' sammeln und Paare so probieren,
    # dass möglichst große Kandidaten zuerst getestet werden.
    open_positions = [i for i, c in enumerate(stripped) if c == '[']
    close_positions = [i for i, c in enumerate(stripped) if c == ']']
    if not open_positions or not close_positions:
        logger.debug('Phase4: Kein JSON-Array in Antwort gefunden')
        return []

    # Kandidaten = (start, end) absteigend nach Länge sortiert
    candidates = [
        (s, e) for s in open_positions for e in close_positions if e > s
    ]
    candidates.sort(key=lambda se: se[1] - se[0], reverse=True)

    for s, e in candidates:
        snippet = stripped[s:e + 1]
        try:
            parsed = json.loads(snippet)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            # Nur echte Error-Dicts behalten – verhindert dass z.B. "[1]"
            # aus Vortext fälschlich als Befund interpretiert wird
            dicts = [item for item in parsed if isinstance(item, dict)]
            if dicts or not parsed:
                return dicts
            continue
        # Falls einzelnes Dict zurückgegeben wurde, in Liste packen
        if isinstance(parsed, dict):
            return [parsed]

    logger.warning('Phase4: Kein parsebares JSON-Array in Antwort gefunden')
    return []


def _severity_from_explanation(explanation: str) -> str:
    """Leitet Schweregrad aus der KI-Erklärung ab.

    Verwendet Match am Wortanfang und schließt Negationen aus, damit z.B.
    "unkritisch", "nicht kritisch" oder "not a critical issue" nicht
    fälschlich als 'critical' interpretiert wird.
    """
    low = explanation.lower()

    # Negationsphrasen, die unmittelbar vor dem Stichwort stehen können
    negation_re = re.compile(
        r'\b(nicht|kein(?:e[mnrs]?)?|non|not(?:\s+a)?|no)\s*[-]?\s*$'
    )

    def _has_word(text: str, word: str) -> bool:
        # Match am Wortanfang (deutsche Deklination wie 'kritischer' soll matchen)
        for m in re.finditer(r'\b' + re.escape(word), text):
            start = m.start()
            prefix = text[max(0, start - 20):start]
            if negation_re.search(prefix):
                continue
            return True
        return False

    critical_words = (
        'kritisch', 'critical', 'schwerwiegend', 'falsche bedeutung',
        'sinnentstellung', 'nicht übersetzt', 'missing', 'fehlt komplett',
        'completely wrong', 'völlig falsch',
    )
    if any(_has_word(low, w) for w in critical_words):
        return 'critical'

    major_words = (
        'major', 'erheblich', 'sinnentstellend',
        'falsch übersetzt', 'falsch wiedergegeben', 'inhaltlich falsch',
        'wesentlich', 'grob', 'stark verändert', 'unvollständig',
    )
    if any(_has_word(low, w) for w in major_words):
        return 'major'
    return 'minor'


def run_ki_checks(
    pairs: Iterable[Tuple[str, str]],
    *,
    src_lang: str = 'de',
    tgt_lang: str = 'it',
    fachgebiet: str = 'Allgemein',
    pruefstufe: str = 'v1',
    ollama_model: str = 'llama3.2:3b',
    max_segments: int = 30,
) -> List:
    """Phase-4 KI-Check: Vergleicht Ausgangstext mit Übersetzung via Ollama.

    Bündelt alle Segmente in einen einzigen Ollama-Aufruf (numerierte Blöcke),
    parst die JSON-Antwort und gibt QAIssue-Objekte zurück.

    Args:
        pairs:         Iterable von (ausgangstext, übersetzung) Tupeln.
        src_lang:      Quellsprache (kurz, z. B. 'de').
        tgt_lang:      Zielsprache (kurz, z. B. 'it').
        fachgebiet:    Fachgebiet für den KI-Prompt ('Allgemein', 'Technik', …).
        pruefstufe:    Prüfstufe ('v1' = detailliert, 'v2' = grobe Fehler, 'v3' = kritisch).
        ollama_model:  Ollama-Modell-Name.
        max_segments:  Maximale Segmentanzahl pro Aufruf (verhindert zu große Prompts).

    Returns:
        Liste von QAIssue-Objekten (leer wenn Ollama nicht erreichbar).
    """
    try:
        from quality_gui_phase1_checkers import QAIssue
    except ImportError:
        logger.error('Phase4: quality_gui_phase1_checkers nicht verfügbar')
        return []

    try:
        from ki_module import ki_qualitaetspruefung_vergleich
    except ImportError:
        logger.warning('Phase4: ki_module nicht verfügbar – KI-Prüfung übersprungen')
        return []

    pairs_list = list(pairs)[:max_segments]
    if not pairs_list:
        return []

    # Segmente zu nummerierten Blöcken zusammenfassen
    src_lines = '\n'.join(
        f'[{i + 1}] {s}' for i, (s, _) in enumerate(pairs_list)
    )
    tgt_lines = '\n'.join(
        f'[{i + 1}] {t}' for i, (_, t) in enumerate(pairs_list)
    )

    src_bcp = _to_bcp47(src_lang)
    tgt_bcp = _to_bcp47(tgt_lang)

    logger.info(
        'Phase4 KI-Prüfung: %d Segmente, %s→%s, Modell=%s, Fachgebiet=%s, Stufe=%s',
        len(pairs_list), src_lang, tgt_lang, ollama_model, fachgebiet, pruefstufe,
    )

    try:
        response = ki_qualitaetspruefung_vergleich(
            source_text=src_lines,
            target_text=tgt_lines,
            language_code=tgt_bcp,
            fachgebiet=fachgebiet,
            pruefstufe=pruefstufe,
            source_language_code=src_bcp,
            model=ollama_model,
        )
    except ConnectionError as exc:
        logger.warning('Phase4: Ollama nicht erreichbar: %s', exc)
        return []
    except TimeoutError as exc:
        logger.warning('Phase4: Ollama-Timeout: %s', exc)
        return []
    except Exception as exc:
        logger.warning('Phase4: Ollama-Aufruf fehlgeschlagen (%s): %s', type(exc).__name__, exc)
        return []

    errors = _parse_ki_response(response)
    if not errors:
        logger.debug('Phase4: Keine Fehler in Ollama-Antwort gefunden')
        return []

    issues: List = []
    for err in errors:
        if not isinstance(err, dict):
            continue

        error_text = str(err.get('error_text') or '').strip()
        context = str(err.get('context') or '').strip()
        explanation = str(err.get('explanation') or '').strip()

        if not explanation and not error_text:
            continue

        severity = _severity_from_explanation(explanation)

        # Segment-Index ermitteln: Priorität 1 – [N]-Bracket aus context/explanation
        seg_index = -1
        for search_in in (context, explanation, error_text):
            if not search_in:
                continue
            m = re.search(r'\[(\d+)\]', search_in)
            if m:
                n = int(m.group(1)) - 1
                if 0 <= n < len(pairs_list):
                    seg_index = n
                    break

        # Priorität 2 – Text-Match gegen Segmente.
        # Suchkandidaten aufbauen: Das Modell liefert oft den Quellsatz im
        # 'context'-Feld (ohne [N]-Klammer) und 'error_text' im Pfeil-Format
        # "quelle -> ziel". Beide Seiten des Pfeils sowie context werden als
        # eigene Match-Kandidaten geprüft, da "rot -> blu" in keinem Segment
        # als Substring vorkommt, "rot" bzw. der context-Satz aber schon.
        if seg_index < 0:
            from difflib import SequenceMatcher

            candidates: List[str] = []
            if context:
                candidates.append(context)
            if error_text:
                # Pfeil-Format "links -> rechts" auftrennen. Ein oder mehrere
                # Pfeil-Zeichen ([-–—=]) gefolgt von '>' (deckt ->, -->, =>, ==>,
                # –>, —> ab) oder das Unicode-Pfeilzeichen →. Wichtig: '+' statt
                # Einzelalternativen, damit '-->' nicht zu 'rot -' zerfällt.
                parts = re.split(r'\s*(?:[-–—=]+>|→)\s*', error_text)
                candidates.extend(p for p in parts if p.strip())
                candidates.append(error_text)

            # 2a – Exact Substring: eindeutiges Segment → sofort nehmen.
            for cand in candidates:
                cl = cand.strip().lower()
                if len(cl) < 3:
                    continue
                hits = [
                    i for i, (s, t) in enumerate(pairs_list)
                    if cl in s.lower() or cl in t.lower()
                ]
                if len(hits) == 1:
                    seg_index = hits[0]
                    break

            # 2b – Fuzzy-Match: bester Score über alle Segmente/Kandidaten,
            # nur wenn deutlich über Zufall (≥0.65).
            if seg_index < 0:
                best_score, best_idx = 0.0, -1
                for cand in candidates:
                    cl = cand.strip().lower()
                    if len(cl) < 5:
                        continue
                    for i, (s, t) in enumerate(pairs_list):
                        score = max(
                            SequenceMatcher(None, cl, s.lower()).ratio(),
                            SequenceMatcher(None, cl, t.lower()).ratio(),
                        )
                        if score > best_score:
                            best_score, best_idx = score, i
                if best_score >= 0.65:
                    seg_index = best_idx

        if seg_index < 0:
            logger.debug('Phase4: Segment-Index nicht ermittelbar für Fehler: %s', error_text[:60])

        src_text = pairs_list[seg_index][0] if seg_index >= 0 else context
        tgt_text = pairs_list[seg_index][1] if seg_index >= 0 else error_text

        issues.append(QAIssue(
            code='KI_SEMANTIC',
            severity=severity,
            category='ki_semantic',
            message=explanation or f'Übersetzungsfehler: {error_text[:120]}',
            source_text=src_text,
            target_text=tgt_text,
            segment_index=seg_index,
            meta={
                'error_text': error_text,
                'context': context,
                'ki_model': ollama_model,
                'src_lang': src_lang,
                'tgt_lang': tgt_lang,
            },
        ))

    logger.info('Phase4 KI-Prüfung abgeschlossen: %d Befunde', len(issues))
    return issues
