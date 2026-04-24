"""quality_gui_phase3_checkers – finale Migration (ursprünglich qa_phase3_checkers).

Semantik / Stil / Risiko / Lesbarkeit (Phase 3). Optional semantische Ähnlichkeit.
"""
from __future__ import annotations
from typing import Iterable, Tuple, List, Dict, Optional, Any
import re
import os
import logging
from collections import Counter

_logger = logging.getLogger(__name__)

try:
    from quality_gui_grammar import GrammarChecker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    GrammarChecker = None  # type: ignore

try:
    import language_tool_python  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    language_tool_python = None  # type: ignore

try:
    from spellchecker import SpellChecker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SpellChecker = None  # type: ignore

try:
    from quality_gui_consistency_checker import ConsistencyChecker, check_consistency_as_issues  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ConsistencyChecker = None  # type: ignore
    check_consistency_as_issues = None  # type: ignore

try:
    from quality_gui_ocr_checker import OCRChecker, check_ocr_as_issues  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OCRChecker = None  # type: ignore
    check_ocr_as_issues = None  # type: ignore

try:
    from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:  # Fallback Mini-Dataclass
    from dataclasses import dataclass, field
    @dataclass
    class QAIssue:  # type: ignore
        code: str
        severity: str
        category: str
        message: str
        source_text: str
        target_text: str
        segment_index: int = -1
        meta: dict = field(default_factory=dict)

ABBR = r"(z\. ?B\.|u\. ?a\.|d\. ?h\.|bzw\.|ca\.|Nr\.|vgl\.)"
# VERBESSERT: Erweitertes Abkürzungs-Pattern für DE + EN
ABBR_RX = re.compile(
    r'\b(?:'
    # Deutsche Abkürzungen
    r'z\. ?B\.|u\. ?a\.|d\. ?h\.|bzw\.|ca\.|Nr\.|vgl\.|usw\.|etc\.|'
    # Englische Abkürzungen
    r'Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.|Inc\.|Ltd\.|Corp\.|No\.|Fig\.|'
    r'e\.g\.|i\.e\.|vs\.|'
    # Einzelbuchstaben-Abkürzungen (z.B. "A. Smith", "J. F. Kennedy")
    r'[A-Z]\.'
    r')'
)
PLHDR = '§'
WORD_SPLIT = re.compile(r'[^\W_]+', re.UNICODE)
# VERBESSERT: Base64-Sequenzen mit echten Wortgrenzen (nicht vor/nach alnum+/=)
# Verhindert False Positives bei langen technischen IDs
BASE64_SEQ = re.compile(r'(?<![A-Za-z0-9+/=])[A-Za-z0-9+/=]{44,}(?![A-Za-z0-9+/=])')
BASE64_PATTERN = re.compile(r'(?i)^[A-Za-z0-9+/]{44,}={0,2}$')
# Upper Bound für Base64-Tokens im Report (sehr lange Blobs kürzen)
BASE64_MAX_REPORT_LEN = 120
LANGUAGE_TOOL_CODES = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "es": "es-ES",
    "it": "it-IT"
}

# HINWEIS: Fallback-Lexikon ist SEHR begrenzt - nur für Demo/kurze Texte!
# Für Produktivbetrieb: wordfreq oder lokale Wortliste verwenden.
# Aktiviere Fallback nur bei kurzen Texten (<50 Wörter) oder mit hoher Confidence-Schwelle.
FALLBACK_LEXICONS: Dict[str, Counter[str]] = {
    "de": Counter({
        # === FUNKTIONSWÖRTER (Artikel, Pronomen, Präpositionen, Konjunktionen) ===
        "und": 50, "der": 45, "die": 45, "das": 40, "in": 38, "ist": 35,
        "von": 33, "den": 32, "mit": 30, "für": 28, "auf": 26, "nicht": 25,
        "eine": 24, "ein": 24, "als": 23, "auch": 22, "es": 21, "an": 20,
        "werden": 19, "aus": 18, "er": 17, "hat": 16, "dass": 15, "sie": 14,
        "nach": 13, "bei": 12, "um": 11, "am": 10, "sind": 10, "noch": 9,
        "wie": 9, "einem": 8, "über": 8, "so": 7, "zum": 7, "kann": 7,
        "nur": 6, "ihr": 6, "seine": 6, "ihrer": 5, "allem": 5, "wurde": 5,
        "oder": 22, "aber": 20, "wenn": 18, "dann": 16, "weil": 14,
        "dieser": 12, "diese": 12, "dieses": 10, "diesem": 10, "diesen": 10,
        "jeder": 8, "jede": 8, "jedes": 8, "jedem": 7, "jeden": 7,
        "kein": 10, "keine": 10, "keinem": 8, "keinen": 8, "keiner": 8,
        "mein": 8, "meine": 8, "meinem": 7, "meinen": 7, "meiner": 7,
        "dein": 7, "deine": 7, "deinem": 6, "deinen": 6, "deiner": 6,
        "unser": 7, "unsere": 7, "unserem": 6, "unseren": 6, "unserer": 6,
        "sich": 18, "ich": 16, "du": 14, "wir": 12, "ihr": 10,
        "mich": 10, "mir": 10, "dich": 8, "dir": 8, "uns": 10, "euch": 7,
        "ihn": 8, "ihm": 8, "ihnen": 8, "man": 12, "was": 12, "wer": 8,
        "wo": 8, "wann": 7, "warum": 7, "welcher": 6, "welche": 6, "welches": 6,
        "ob": 10, "denn": 8, "doch": 8, "schon": 8, "ja": 8, "nein": 7,
        "vor": 12, "zwischen": 10, "unter": 10, "neben": 8, "hinter": 7,
        "durch": 10, "gegen": 8, "ohne": 8, "bis": 8, "seit": 7, "während": 7,
        "zur": 10, "vom": 10, "beim": 8, "ins": 8, "im": 14, "ans": 6,
        "des": 12, "dem": 12, "deren": 7, "dessen": 7,
        # === VERBEN (häufige + Konjugationsformen) ===
        "sein": 20, "haben": 18, "war": 15, "hatte": 12, "wird": 14,
        "worden": 8, "geworden": 7, "gewesen": 7, "gehabt": 6,
        "können": 12, "müssen": 11, "sollen": 10, "wollen": 10, "dürfen": 8,
        "muss": 10, "soll": 9, "will": 9, "darf": 7, "mag": 6, "möchte": 8,
        "konnte": 7, "musste": 6, "sollte": 7, "wollte": 6, "durfte": 5,
        "machen": 12, "macht": 10, "gemacht": 8, "gehen": 10, "geht": 9,
        "gegangen": 6, "kommen": 10, "kommt": 9, "gekommen": 6,
        "geben": 10, "gibt": 10, "gegeben": 6, "nehmen": 8, "nimmt": 7,
        "genommen": 5, "sehen": 8, "sieht": 7, "gesehen": 6,
        "stehen": 8, "steht": 7, "finden": 8, "findet": 7, "gefunden": 6,
        "sagen": 8, "sagt": 7, "gesagt": 6, "wissen": 8, "weiß": 7,
        "lassen": 7, "lässt": 6, "halten": 7, "hält": 6, "bleiben": 7,
        "liegen": 7, "liegt": 7, "bringen": 7, "bringt": 6, "gebracht": 5,
        "zeigen": 7, "zeigt": 6, "führen": 7, "führt": 6, "spielen": 6,
        "arbeiten": 7, "arbeitet": 6, "denken": 6, "denkt": 5, "sprechen": 6,
        "brauchen": 7, "braucht": 6, "heißen": 6, "heißt": 6, "bedeuten": 6,
        "nutzen": 6, "nutzt": 5, "setzen": 6, "stellen": 6, "legen": 5,
        "bieten": 6, "bietet": 5, "folgen": 5, "folgt": 5, "beginnen": 5,
        "erreichen": 5, "erreicht": 5, "erhalten": 6, "erhält": 5,
        "verwenden": 6, "verwendet": 5, "erstellen": 5, "erstellt": 5,
        "freuen": 5, "freut": 5, "gefreut": 4, "helfen": 5, "hilft": 5,
        "schreiben": 5, "schreibt": 5, "geschrieben": 4, "lesen": 5, "liest": 5,
        "tragen": 5, "trägt": 4, "gelten": 5, "gilt": 5,
        "prüfen": 6, "prüft": 5, "geprüft": 5, "bestehen": 5, "besteht": 5,
        "enthalten": 5, "enthält": 4, "entsprechen": 5, "entspricht": 4,
        # === ADJEKTIVE / ADVERBIEN ===
        "groß": 8, "große": 7, "großen": 6, "großer": 5, "großes": 5,
        "klein": 7, "kleine": 6, "kleinen": 5, "kleiner": 5, "kleines": 5,
        "gut": 10, "gute": 8, "guten": 7, "guter": 6, "gutes": 5, "besser": 6, "beste": 5,
        "neu": 8, "neue": 7, "neuen": 6, "neuer": 5, "neues": 5,
        "alt": 6, "alte": 5, "alten": 5,
        "lang": 6, "lange": 5, "langen": 5, "kurz": 6, "kurze": 5,
        "hoch": 6, "hohe": 5, "hohen": 5, "höher": 5, "höchste": 4,
        "wichtig": 7, "wichtige": 6, "wichtigen": 5, "möglich": 7, "möglicherweise": 5,
        "schnell": 6, "schnelle": 5, "richtig": 6, "richtige": 5,
        "verschieden": 5, "verschiedene": 5, "verschiedenen": 5,
        "folgend": 5, "folgende": 5, "folgenden": 5,
        "bestimmt": 5, "bestimmte": 5, "bestimmten": 5,
        "ander": 5, "andere": 6, "anderen": 6, "anderer": 5, "anderes": 5,
        "viel": 8, "viele": 7, "vielen": 6, "mehr": 8, "weniger": 6,
        "wenig": 6, "wenige": 5, "einige": 6, "einigen": 5, "einiger": 5,
        "ganz": 7, "sehr": 8, "etwas": 7, "genau": 6, "etwa": 5,
        "hier": 7, "dort": 6, "heute": 6, "jetzt": 7, "immer": 7,
        "bereits": 6, "wieder": 6, "zusammen": 5, "weiter": 5, "zuerst": 5,
        "jedoch": 6, "dabei": 6, "außerdem": 5, "deshalb": 5, "daher": 5,
        "insbesondere": 5, "beispielsweise": 4, "grundsätzlich": 4,
        "entsprechend": 5, "jeweilig": 4, "jeweilige": 4, "jeweiligen": 4,
        # === SUBSTANTIVE (allgemein) ===
        "zeit": 10, "tag": 8, "tage": 7, "tagen": 6, "jahr": 8, "jahre": 7,
        "jahren": 6, "monat": 6, "monate": 5, "woche": 5, "wochen": 5,
        "mensch": 7, "menschen": 7, "frau": 6, "frauen": 5, "herr": 6,
        "kind": 6, "kinder": 5, "kindern": 5, "teil": 7, "teile": 6,
        "seite": 6, "seiten": 5, "hand": 5, "kopf": 5, "auge": 5, "augen": 5,
        "wort": 6, "wörter": 5, "satz": 5, "text": 7, "sprache": 6,
        "frage": 6, "fragen": 5, "antwort": 5, "antworten": 5,
        "grund": 6, "gründe": 5, "weise": 5, "art": 6, "form": 5,
        "zahl": 5, "zahlen": 5, "nummer": 5, "prozent": 5,
        "ende": 6, "anfang": 5, "mitte": 5, "ort": 5, "platz": 5,
        "weg": 6, "straße": 5, "stadt": 6, "land": 6, "länder": 5,
        "haus": 6, "raum": 5, "zimmer": 5, "tür": 5, "fenster": 5,
        "wasser": 5, "luft": 5, "erde": 5, "feuer": 4, "licht": 5,
        "geld": 6, "preis": 5, "preise": 5, "kosten": 5, "wert": 5,
        "arbeit": 7, "aufgabe": 5, "aufgaben": 5, "stelle": 5,
        "schritt": 6, "schritte": 5, "schritten": 4,
        "name": 6, "namen": 5, "punkt": 5, "punkte": 5,
        "ebene": 5, "stufe": 4, "stufen": 4, "lage": 5,
        "folge": 5, "folgen": 5, "fall": 6, "fälle": 5,
        # === SUBSTANTIVE (Geschäft/Technik/Übersetzung) ===
        "qualität": 20, "übersetzung": 20, "übersetzungen": 15,
        "bitte": 18, "danke": 15,
        "kunde": 12, "kunden": 10, "projekt": 12, "projekte": 10,
        "bericht": 11, "berichte": 9, "prüfung": 10, "prüfungen": 8,
        "lieferung": 10, "hinweis": 8, "hinweise": 7, "analyse": 8,
        "liste": 6, "ergebnis": 7, "ergebnisse": 6, "fehler": 8, "fehlers": 6,
        "dokument": 7, "dokumente": 6, "datei": 7, "dateien": 6,
        "system": 7, "programm": 6, "software": 6, "version": 6,
        "daten": 7, "information": 6, "informationen": 6,
        "beispiel": 7, "beispiele": 5, "lösung": 6, "problem": 6, "probleme": 5,
        "änderung": 6, "änderungen": 5, "aktualisierung": 5,
        "anforderung": 5, "anforderungen": 5, "bedingung": 5, "bedingungen": 5,
        "prozess": 6, "verfahren": 5, "methode": 5, "methoden": 5,
        "unternehmen": 7, "firma": 5, "gesellschaft": 5, "organisation": 5,
        "mitarbeiter": 6, "mitarbeitern": 5, "team": 5, "gruppe": 5,
        "produkt": 6, "produkte": 5, "service": 5, "leistung": 5, "leistungen": 5,
        "markt": 5, "branche": 5, "bereich": 6, "bereiche": 5, "bereichen": 5,
        "entwicklung": 6, "forschung": 5, "fortschritt": 4,
        "sicherheit": 5, "schutz": 5, "kontrolle": 5, "management": 5,
        "ziel": 6, "ziele": 5, "zweck": 4, "sinn": 5, "nutzen": 5,
        "inhalt": 5, "inhalte": 5, "thema": 5, "themen": 5,
        "vertrag": 5, "vereinbarung": 5, "regelung": 5, "gesetz": 5,
        "recht": 5, "rechte": 5, "pflicht": 5, "pflichten": 5,
        "termin": 5, "frist": 5, "zeitraum": 5, "zeitpunkt": 5,
        "nachricht": 5, "mitteilung": 4, "meldung": 4, "anzeige": 4,
        "zugang": 4, "zugriff": 4, "verbindung": 4, "eingabe": 4, "ausgabe": 4,
        "quelle": 5, "ausgangstext": 4, "zieltext": 4, "zielsprache": 4,
        "korrektur": 5, "korrekturen": 4, "vorschlag": 5, "vorschläge": 4,
        "übersetzer": 5, "übersetzerin": 4, "lektor": 4, "lektorat": 4,
        "glossar": 5, "terminologie": 5, "wörterbuch": 4,
        # === ERGÄNZUNG: fehlende Demonstrativpronomen, Adjektive, Modalverben ===
        "dies": 12, "solch": 5, "solche": 5, "solchen": 5, "solcher": 5,
        "welchem": 5, "derselbe": 4, "dieselbe": 4, "dasselbe": 4,
        "aktuell": 6, "aktuelle": 6, "aktuellen": 5, "aktueller": 5, "aktuelles": 5,
        "zahlreich": 5, "zahlreiche": 5, "zahlreichen": 5, "zahlreicher": 4,
        "mehrere": 6, "mehreren": 5, "mehrerer": 4,
        "weitere": 6, "weiteren": 5, "weiterer": 5, "weiteres": 5,
        "gesamt": 5, "gesamte": 5, "gesamten": 5,
        "einzeln": 4, "einzelne": 5, "einzelnen": 5, "einzelner": 4,
        "direkt": 5, "direkte": 5, "direkten": 4,
        "nötig": 4, "nötige": 4, "nötigen": 4, "notwendig": 5, "notwendige": 4,
        "positiv": 5, "positive": 4, "positiven": 4, "negativ": 4, "negative": 4,
        "intern": 4, "interne": 4, "internen": 4, "extern": 4, "externe": 4,
        "erfolgreich": 5, "erfolgreiche": 4, "erfolgreichen": 4,
        "vollständig": 5, "vollständige": 4, "vollständigen": 4,
        "regelmäßig": 4, "regelmäßige": 4, "automatisch": 4, "automatische": 4,
        "zusätzlich": 5, "zusätzliche": 4, "zusätzlichen": 4,
        "innerhalb": 6, "außerhalb": 5, "gegenüber": 5, "oberhalb": 4, "unterhalb": 4,
        "obwohl": 6, "trotzdem": 5, "sondern": 6, "damit": 7, "somit": 5,
        "sobald": 4, "sofern": 4, "soweit": 4, "weder": 4, "noch": 8,
        "abteilung": 5, "abteilungen": 5, "rechnung": 5, "rechnungen": 4,
        "qualität": 6, "bewertung": 5, "bewertungen": 4, "anpassung": 4,
        # === Modalverb-Konjugationen (fehlende Formen) ===
        "könnte": 7, "könnten": 6, "müsste": 5, "müssten": 5,
        "dürfte": 5, "dürften": 4, "möchten": 6, "mögen": 5,
        "sollten": 6, "wollten": 5, "würde": 7, "würden": 6, "würdest": 4,
        # === Passiv/Partizip-Formen ===
        "verwendet": 5, "verarbeitet": 4, "überprüft": 5, "festgestellt": 4,
        "durchgeführt": 5, "bereitgestellt": 4, "vorgenommen": 4,
        "abgeschlossen": 4, "eingesetzt": 4, "zugeordnet": 4,
    }),
    "en": Counter({
        # === FUNCTION WORDS (articles, pronouns, prepositions, conjunctions) ===
        "the": 60, "and": 50, "to": 48, "of": 45, "a": 42, "in": 40,
        "is": 38, "it": 35, "for": 33, "that": 32, "you": 30, "was": 28,
        "on": 26, "are": 25, "with": 24, "as": 23, "be": 22, "at": 21,
        "this": 20, "have": 19, "from": 18, "or": 17, "by": 16, "an": 15,
        "not": 14, "but": 13, "what": 12, "all": 11, "were": 10, "we": 10,
        "can": 9, "your": 9, "has": 8, "there": 8, "been": 7, "if": 7,
        "will": 6, "their": 6, "would": 5, "each": 5, "which": 5, "do": 5,
        "i": 18, "me": 10, "my": 10, "he": 12, "she": 10, "his": 10, "her": 10,
        "him": 8, "its": 8, "they": 10, "them": 8, "our": 8, "us": 7,
        "who": 8, "whom": 5, "whose": 5, "where": 7, "when": 7, "how": 7, "why": 6,
        "than": 8, "then": 7, "about": 8, "into": 7, "through": 6,
        "between": 6, "after": 7, "before": 6, "during": 5, "without": 5,
        "under": 5, "over": 5, "above": 4, "below": 4, "against": 5,
        "since": 5, "until": 5, "while": 5, "because": 6, "although": 5,
        "whether": 5, "though": 5, "however": 6, "therefore": 5, "also": 7,
        "any": 7, "some": 7, "many": 6, "much": 6, "few": 5, "more": 8, "most": 6,
        "other": 7, "another": 5, "such": 6, "no": 8, "only": 7, "just": 6,
        "own": 5, "same": 5, "both": 5, "very": 6, "even": 5, "well": 6,
        "still": 5, "already": 5, "again": 5, "too": 5, "here": 6, "now": 6,
        "those": 6, "these": 6, "does": 6, "did": 6, "had": 7, "could": 5,
        "should": 5, "may": 5, "might": 5, "must": 5, "shall": 4,
        # === VERBS (common) ===
        "make": 8, "made": 7, "go": 7, "going": 6, "gone": 5,
        "come": 7, "came": 5, "take": 7, "took": 5, "taken": 5,
        "get": 8, "got": 6, "give": 6, "gave": 5, "given": 5,
        "see": 7, "saw": 5, "seen": 5, "know": 7, "knew": 5, "known": 5,
        "think": 6, "thought": 5, "say": 6, "said": 7, "tell": 5, "told": 5,
        "find": 6, "found": 6, "keep": 5, "kept": 4, "leave": 5, "left": 5,
        "put": 5, "run": 5, "set": 5, "show": 6, "shown": 5, "try": 5,
        "use": 7, "used": 7, "using": 6, "work": 7, "worked": 5, "working": 5,
        "need": 6, "needed": 5, "want": 5, "wanted": 4, "help": 5,
        "call": 5, "called": 5, "start": 5, "started": 4, "move": 5,
        "follow": 5, "followed": 4, "turn": 5, "ask": 5, "asked": 4,
        "read": 5, "write": 5, "written": 5, "provide": 5, "provided": 5,
        "include": 5, "included": 5, "including": 5, "allow": 5, "require": 5,
        "create": 5, "created": 4, "change": 5, "changed": 4, "add": 5,
        "open": 5, "close": 5, "closed": 4, "check": 5, "ensure": 5,
        "consider": 4, "expect": 4, "support": 5, "available": 5,
        # === ADJECTIVES / ADVERBS ===
        "new": 8, "old": 5, "good": 7, "better": 5, "best": 5,
        "great": 5, "long": 6, "short": 5, "high": 6, "low": 5,
        "large": 5, "small": 5, "big": 5, "first": 7, "last": 5,
        "next": 5, "different": 5, "important": 5, "possible": 5,
        "certain": 4, "particular": 4, "specific": 4, "general": 4,
        "following": 5, "current": 5, "previous": 4, "additional": 4,
        "right": 5, "sure": 4, "able": 4, "full": 4, "free": 4,
        "clear": 4, "complete": 4, "necessary": 4, "real": 4, "true": 4,
        "always": 5, "never": 5, "often": 4, "usually": 4, "sometimes": 4,
        "today": 4, "together": 4, "enough": 4, "especially": 4,
        # === NOUNS (general) ===
        "time": 8, "day": 6, "days": 5, "year": 6, "years": 5,
        "month": 5, "months": 5, "week": 5, "weeks": 4,
        "people": 7, "person": 5, "man": 5, "woman": 5, "child": 4, "children": 4,
        "world": 5, "country": 5, "state": 5, "city": 4, "place": 5,
        "way": 7, "part": 6, "case": 6, "point": 5, "end": 5,
        "number": 5, "line": 5, "side": 4, "water": 4, "money": 5,
        "word": 5, "name": 5, "hand": 4, "head": 4, "life": 5,
        "fact": 5, "question": 5, "answer": 4, "reason": 4, "result": 5,
        "problem": 5, "example": 5, "thing": 5, "area": 4, "group": 5,
        # === NOUNS (business/technical/translation) ===
        "quality": 20, "translation": 20, "translations": 12,
        "please": 18, "thank": 15, "thanks": 10,
        "customer": 12, "customers": 8, "project": 12, "projects": 8,
        "report": 11, "reports": 7, "review": 10, "reviews": 6,
        "delivery": 10, "note": 8, "notes": 6, "analysis": 8,
        "list": 6, "error": 7, "errors": 6, "issue": 6, "issues": 5,
        "document": 7, "documents": 5, "file": 7, "files": 5,
        "system": 7, "software": 5, "program": 5, "version": 5,
        "data": 7, "information": 7, "process": 6, "method": 5,
        "solution": 5, "option": 4, "feature": 4, "function": 4,
        "company": 6, "organization": 4, "business": 5, "market": 5,
        "product": 5, "products": 4, "service": 5, "services": 4,
        "team": 5, "department": 4, "management": 5,
        "development": 5, "research": 4, "content": 5, "text": 6,
        "language": 6, "source": 6, "target": 6, "term": 5, "terms": 5,
        "glossary": 5, "terminology": 5, "dictionary": 4,
        "translator": 5, "editor": 4, "proofreader": 4,
        "correction": 5, "corrections": 4, "suggestion": 5, "suggestions": 4,
        "requirement": 4, "requirements": 4, "condition": 4, "conditions": 4,
        "contract": 4, "agreement": 4, "deadline": 4, "schedule": 4,
        "access": 4, "security": 4, "update": 5, "status": 4,
        "message": 5, "request": 5, "response": 4, "input": 4, "output": 4,
    }),
    "fr": Counter({
        # === Mots français les plus fréquents ===
        "le": 45, "la": 42, "les": 40, "de": 45, "des": 35, "du": 30,
        "un": 28, "une": 26, "et": 38, "en": 32, "est": 30, "que": 25,
        "qui": 22, "dans": 20, "ce": 18, "il": 18, "ne": 16, "sur": 15,
        "se": 15, "pas": 14, "plus": 12, "par": 12, "au": 12, "son": 10,
        "pour": 20, "avec": 15, "elle": 12, "sont": 12, "mais": 10,
        "nous": 10, "vous": 10, "ils": 8, "ou": 10, "cette": 8, "être": 12,
        "avoir": 10, "faire": 8, "dit": 6, "tout": 8, "tous": 6,
        "peut": 8, "aussi": 7, "entre": 6, "après": 5, "avant": 5,
        "même": 7, "autre": 6, "autres": 5, "comme": 8, "bien": 6,
        "très": 6, "sans": 5, "où": 5, "temps": 5, "depuis": 5,
        "qualité": 12, "traduction": 12, "document": 7, "projet": 7,
        "rapport": 6, "erreur": 5, "correction": 5, "langue": 5,
    }),
    "es": Counter({
        # === Palabras españolas más frecuentes ===
        "el": 45, "la": 42, "los": 35, "las": 32, "de": 45, "en": 35,
        "un": 28, "una": 26, "que": 30, "es": 28, "del": 22, "por": 20,
        "con": 18, "no": 16, "se": 18, "su": 14, "al": 12, "lo": 12,
        "para": 18, "como": 12, "más": 10, "pero": 8, "fue": 6,
        "este": 8, "esta": 8, "todo": 6, "son": 8, "entre": 5,
        "también": 6, "cuando": 5, "hay": 6, "sin": 5, "sobre": 5,
        "ser": 10, "estar": 8, "haber": 6, "tener": 6, "hacer": 6,
        "calidad": 12, "traducción": 12, "documento": 7, "proyecto": 7,
        "informe": 6, "error": 5, "corrección": 5, "idioma": 5,
    }),
    "it": Counter({
        # === Parole italiane più frequenti ===
        "il": 45, "la": 42, "di": 45, "che": 30, "è": 30, "un": 28,
        "in": 35, "una": 26, "del": 22, "per": 20, "non": 16, "con": 18,
        "si": 15, "da": 15, "le": 14, "al": 12, "lo": 12, "sono": 10,
        "dei": 10, "gli": 8, "più": 8, "ma": 8, "come": 8,
        "anche": 6, "questo": 6, "questa": 5, "tra": 5, "suo": 5,
        "essere": 10, "avere": 8, "fare": 6, "dire": 5,
        "qualità": 12, "traduzione": 12, "documento": 7, "progetto": 7,
    }),
}
# Minimale Textlänge für Fallback-Spellcheck (reduziert False Positives)
# Auf 20 gesenkt, da das Lexikon jetzt groß genug ist für sinnvolle Prüfung
FALLBACK_MIN_WORDS = 20


class _SpellcheckEngine:
    """Kapselt optionale Spell-/Grammar-Prüfung mit Fallback."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.language = (config.get("target_language") or "de").lower()
        self.max_issues = int(config.get("max_issues_per_segment", 3) or 3)
        self.use_language_tool = bool(config.get("use_language_tool", False))
        self.custom_words = {w.lower(): True for w in config.get("custom_dictionary", []) if isinstance(w, str)}
        self._engine = None
        self._backend = "fallback"
        self._init_backend()

    def _init_backend(self) -> None:
        if self.use_language_tool and language_tool_python:
            code = LANGUAGE_TOOL_CODES.get(self.language, self.language)
            try:
                self._engine = language_tool_python.LanguageTool(code)  # type: ignore
                self._backend = "language_tool"
                return
            except Exception:
                self._engine = None
        if SpellChecker:
            try:
                checker = SpellChecker(language=self.language)
                for word in self.custom_words:
                    checker.word_frequency.add(word)
                self._engine = checker
                self._backend = "spellchecker"
                return
            except Exception:
                self._engine = None
        self._backend = "fallback"

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in WORD_SPLIT.findall(text or "") if len(w) > 1]

    def _fallback_unknown(self, tokens: List[str]) -> List[str]:
        """Fallback-Spellcheck mit begrenztem Lexikon.
        
        VERBESSERT:
        - Aktiviert nur bei genügend Tokens (sonst zu viele False Positives)
        - Bidirektionale Umlaut-Normalisierung (ü↔ue, ö↔oe, ä↔ae, ß→ss)
        - Compound-Wort-Toleranz für lange deutsche Wörter (>12 Zeichen):
          wenn ein bekanntes Wort (≥4 Zeichen) als Teilstring enthalten ist
        - Reine Zahlentokens werden übersprungen
        """
        # Bei zu wenig Tokens: Fallback komplett deaktivieren (zu unzuverlässig)
        if len(tokens) < FALLBACK_MIN_WORDS:
            return []  # Keine Fehler melden bei kurzen Texten
        
        lexicon = FALLBACK_LEXICONS.get(self.language, FALLBACK_LEXICONS.get("en", Counter()))
        
        # Vorkompilierte Stems für Compound-Check (DE: Wörter ≥4 Zeichen)
        _compound_stems: Optional[List[str]] = None
        if self.language == "de":
            _compound_stems = [w for w in lexicon if len(w) >= 4]
        
        unknown = []
        for token in tokens:
            if token in self.custom_words:
                continue
            # Reine Zahlen / Zahlen-Token überspringen
            if token.isdigit():
                continue
            # Direkt-Lookup
            if token in lexicon:
                continue
            # Umlaut-Normalisierung: beide Richtungen prüfen
            ascii_form = token.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
            umlaut_form = token.replace('ae', 'ä').replace('oe', 'ö').replace('ue', 'ü')
            if ascii_form in lexicon or umlaut_form in lexicon:
                continue
            # Compound-Wort-Toleranz (nur Deutsch, >12 Zeichen)
            if _compound_stems and len(token) > 12:
                has_known_stem = any(stem in token for stem in _compound_stems)
                if has_known_stem:
                    continue
            unknown.append(token)
        return unknown

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []
        if self._backend == "language_tool" and self._engine:
            try:
                matches = self._engine.check(text)  # type: ignore[attr-defined]
                recommendations: List[Dict[str, Any]] = []
                for match in matches[: self.max_issues]:
                    word = text[match.offset : match.offset + match.errorLength]  # type: ignore[index]
                    recommendations.append({
                        "word": word,
                        "message": match.message,  # type: ignore[attr-defined]
                        "suggestions": list(match.replacements)[:3]  # type: ignore[attr-defined]
                    })
                return recommendations
            except Exception:
                pass
        if self._backend == "spellchecker" and self._engine:
            tokens = self._tokenize(text)
            try:
                unknown = list(self._engine.unknown(tokens))  # type: ignore[attr-defined]
            except Exception:
                unknown = []
            issues: List[Dict[str, Any]] = []
            for token in unknown[: self.max_issues]:
                suggest = []
                try:
                    suggest = self._engine.candidates(token)  # type: ignore[attr-defined]
                except Exception:
                    suggest = []
                issues.append({
                    "word": token,
                    "message": "Möglicher Rechtschreibfehler",
                    "suggestions": list(suggest)[:3]
                })
            return issues
        tokens = self._tokenize(text)
        unknown = self._fallback_unknown(tokens)
        return [
            {"word": token, "message": "Unbekanntes Wort erkannt", "suggestions": []}
            for token in unknown[: self.max_issues]
        ]

# Ausschlüsse für Base64 False Positives
HEX_LONG = re.compile(r'^[0-9a-fA-F]{40,}$')
JWT_PATTERN = re.compile(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$')

# VERBESSERT: Robusteres Domain-Pattern (echte Domains, keine IPs)
# Fängt sub.example.co.uk, example.com:8080 etc.
DOMAIN_PATTERN = re.compile(r'https?://([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}(?::\d+)?', re.IGNORECASE)
# Fallback: urllib.parse für komplexe Fälle
def _extract_domain_safe(url: str) -> str:
    """Extrahiert Domain aus URL mit urllib.parse als robuster Fallback."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path.split('/')[0]
        # Port entfernen
        if ':' in host:
            host = host.split(':')[0]
        return host.lower()
    except Exception:
        # Regex-Fallback
        m = re.search(r'https?://([^\s/:]+)', url, re.IGNORECASE)
        return m.group(1).lower() if m else ''

ATTR_STYLE_PATTERN = re.compile(r'<[^>]*\sstyle\s*=', re.IGNORECASE)
DATA_URI_PATTERN = re.compile(r'data:\s*[a-z]+/[a-z0-9+.-]+(?:;base64)?', re.IGNORECASE)
# engeres werden-Passiv (kein sein+Partizip)
PASSIVE_DE_WERDEN = re.compile(r'\b(wird|wurden|wurde|werden)\b(?:\s+\w+){0,3}\s+ge\w+(?:t|en)\b', re.IGNORECASE)
PASSIVE_DE_SEIN_WORDEN = re.compile(r'\b(ist|sind|war|waren|sei|seien|gewesen)\b(?:\s+\w+){0,4}\s+ge\w+(?:t|en)\s+worden\b', re.IGNORECASE)
PASSIVE_EN_PATTERN = re.compile(r'\b(?:was|were|is|are|been|being)\b(?:\s+\w+){0,2}\s+\w+(?:ed|en)\b', re.IGNORECASE)

def _clean_domains(urls: Iterable[str]) -> List[str]:
    """Extrahiert und bereinigt Domains aus URLs.
    
    VERBESSERT: Nutzt urllib.parse statt nur Regex für robustere Extraktion.
    """
    cleaned: List[str] = []
    for url in urls:
        if not url:
            continue
        # Nutze sichere Domain-Extraktion
        domain = _extract_domain_safe(url)
        if not domain:
            continue
        # Randzeichen bereinigen
        while domain and domain[0] in "([{\"'":
            domain = domain[1:]
        while domain and domain[-1] in "),.;:'\"}]":
            domain = domain[:-1]
        if domain.startswith('www.'):
            domain = domain[4:]
        if domain:
            cleaned.append(domain)
    return cleaned

def _split_sentences(text: str) -> List[str]:
    """Teilt Text in Sätze auf.
    
    VERBESSERT: Besserer Abkürzungsschutz für DE + EN.
    """
    if not text:
        return []
    # HINWEIS: Frueher wurde hier ein '"' / '„' direkt gefolgt von Space
    # weggekuerzt, um Layout-Artefakte zu glaetten. Das hat aber Whitespace
    # nach abschliessenden Anfuehrungszeichen entfernt (." -> .") und damit
    # die Satzgrenzen-Erkennung kaputtgemacht: '"Hallo Welt." Sie sagte.'
    # wurde nur EIN Satz. Wir lassen den Text jetzt unangetastet.
    t = text
    # Schütze bekannte Abkürzungen
    protected = ABBR_RX.sub(lambda m: m.group(0).replace('.', PLHDR), t.strip())
    # Schütze Zahlen mit Punkten in Versions-/Dezimal-Notation (z.B. "1.2", "1.2.3"),
    # aber NICHT am Satzende (z.B. "Es kostet 5. Wir kaufen es."). Lookahead auf Ziffer.
    protected = re.sub(r'(\d)\.(?=\d)', r'\1' + PLHDR, protected)
    # Schütze Einzelbuchstaben-Abkürzungen die ABBR_RX nicht erfasst hat
    protected = re.sub(r'\b([A-Z])\. ', r'\1' + PLHDR + ' ', protected)
    parts = re.split(r'(?<=[.!?])\s+', protected)
    return [p.replace(PLHDR, '.').strip() for p in parts if p.strip()]

def _avg(values: List[float]) -> float:
    return sum(values)/len(values) if values else 0.0

def check_style(src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    issues: List[QAIssue] = []
    sents = _split_sentences(tgt)
    if not sents:
        return issues
    # 🔧 FIX: Vergleiche mit Quelltext - wenn Quelle auch lange Sätze hat, kein Issue
    src_sents = _split_sentences(src)
    src_long_ratio = len([s for s in src_sents if len(s) > 220]) / max(1, len(src_sents)) if src_sents else 0
    long_sents = [s for s in sents if len(s) > 220]
    tgt_long_ratio = len(long_sents) / max(1, len(sents))
    # Nur Issue wenn Ziel MEHR lange Sätze hat als Quelle (mit Toleranz)
    if long_sents and tgt_long_ratio > src_long_ratio + 0.15:
        issues.append(QAIssue("STYLE_LONG_SENTENCE", "minor", "style",
                             f"{len(long_sents)} sehr lange Sätze (>220 Zeichen)", src, tgt, segment_index, {"examples": long_sents[:3]}))
    
    # 🔧 VERBESSERUNG: Spracherkennung mit langdetect statt ASCII-Ratio
    detected_lang = None
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0  # Reproduzierbarkeit
        if len(tgt) > 30:
            detected_lang = detect(tgt[:2000])
    except Exception:
        # Fallback: ASCII-Ratio Heuristik
        tokens = WORD_SPLIT.findall(tgt)
        if tokens:
            ascii_ratio = sum(1 for t in tokens if re.fullmatch(r'[a-zA-Z]+', t)) / len(tokens)
            detected_lang = 'en' if ascii_ratio > 0.55 else 'de'
    
    # DE Passiv (werden + sein+worden)
    if detected_lang == 'de':
        passive_hits_de = PASSIVE_DE_WERDEN.findall(tgt) + PASSIVE_DE_SEIN_WORDEN.findall(tgt)
        if len(passive_hits_de) >= 3 and len(passive_hits_de) / max(1, len(sents)) > 0.4:
            issues.append(QAIssue("STYLE_PASSIVE_HEAVY_DE", "info", "style",
                                 "Hoher Anteil Passiv (DE) - prüfen", src, tgt, segment_index,
                                 {"count": len(passive_hits_de), "hint_only": True, "detected_lang": detected_lang}))
    # EN Passiv
    elif detected_lang == 'en':
        passive_hits_en = PASSIVE_EN_PATTERN.findall(tgt)
        if len(passive_hits_en) >= 3 and len(passive_hits_en) / max(1, len(sents)) > 0.35:
            issues.append(QAIssue("STYLE_PASSIVE_HEAVY_EN", "minor", "style",
                         "Hoher Anteil Passiv (EN)", src, tgt, segment_index, {"count": len(passive_hits_en), "detected_lang": detected_lang}))
    
    return issues

def check_risk(src: str, tgt: str, *, complement_phase2: bool = True, segment_index: int = -1) -> List[QAIssue]:
    """Prüft Sicherheitsrisiken in der Übersetzung.
    
    VERBESSERT: segment_index für UI Jump-to-Issue.
    """
    issues: List[QAIssue] = []
    # VERBESSERT: Extrahiere URLs und dann Domains mit urllib.parse
    src_urls = re.findall(r'https?://[^\s<>"]+', src or '')
    tgt_urls = re.findall(r'https?://[^\s<>"]+', tgt or '')
    src_domains = set(_clean_domains(src_urls))
    tgt_domains = set(_clean_domains(tgt_urls))
    new_domains = [d for d in tgt_domains if d not in src_domains]
    if new_domains:
        issues.append(QAIssue("RISK_NEW_DOMAIN", "major", "risk", 
            f"Neue Domain(s) im Ziel: {new_domains[:5]}", src, tgt, segment_index,
            {"domains": new_domains[:10]}))
    # Base64 Sequenzen prüfen – Quelle als Rohtext berücksichtigen
    src_text = src or ''
    for m in BASE64_SEQ.finditer(tgt or ''):
        _tok = m.group(0)
        if token_is_base64_suspect(_tok, src_text):
            # VERBESSERT: Token kürzen für Report (max BASE64_MAX_REPORT_LEN)
            report_tok = _tok[:BASE64_MAX_REPORT_LEN] + ('...' if len(_tok) > BASE64_MAX_REPORT_LEN else '')
            issues.append(QAIssue("RISK_BASE64_SUSPECT", "major", "risk", 
                "Verdächtiger Base64-ähnlicher Block", src, tgt, segment_index,
                {"token": report_tok, "full_length": len(_tok)}))
            break
    if complement_phase2:
        # Inline-Style nur werten, wenn echtes HTML-Attribut
        if ATTR_STYLE_PATTERN.search(tgt) and not ATTR_STYLE_PATTERN.search(src_text):
            issues.append(QAIssue("RISK_INLINE_STYLE", "minor", "risk", 
                "Neues inline style Attribut", src, tgt, segment_index))
        if DATA_URI_PATTERN.search(tgt) and not DATA_URI_PATTERN.search(src_text):
            issues.append(QAIssue("RISK_DATA_URI", "major", "risk", 
                "Neuer data: URI im Ziel", src, tgt, segment_index))
    return issues

def _compute_lix(text: str) -> Optional[float]:
    sents = _split_sentences(text)
    words = WORD_SPLIT.findall(text)
    if not sents or not words:
        return None
    long_words = sum(1 for w in words if len(w) > 6)
    return (len(words)/len(sents)) + (long_words * 100.0 / len(words))

def check_readability(src: str, tgt: str, *,
                      avg_len_thr: int = 140,
                      very_long_len: int = 180,
                      very_long_ratio: float = 0.30,
                      staccato_short_len: int = 25,
                      staccato_min_short: int = 3,
                      staccato_ratio: float = 0.60,
                      lix_thr: float = 55.0,
                      staccato_gate_qe_ratio: float = 0.40,
                      segment_index: int = -1) -> List[QAIssue]:
    issues: List[QAIssue] = []
    sents = _split_sentences(tgt)
    if not sents:
        return issues
    # 🔧 FIX: Quelltext-Referenz für Vergleich
    src_sents = _split_sentences(src)
    src_lengths = [len(s) for s in src_sents] if src_sents else []
    src_avg_len = _avg(src_lengths) if src_lengths else 0
    lengths = [len(s) for s in sents]
    avg_len = _avg(lengths)
    very_short = sum(1 for l in lengths if l < staccato_short_len)
    very_long = sum(1 for l in lengths if l > very_long_len)
    # Nur Issue wenn Ziel signifikant länger als Quelle (nicht nur absolut)
    if avg_len > avg_len_thr and avg_len > src_avg_len * 1.3:
        issues.append(QAIssue("READABILITY_TOO_LONG", "minor", "readability", f"Hohe durchschnittliche Satzlänge ({int(avg_len)})", src, tgt, segment_index))
    # 🔧 FIX: Vergleiche auch sehr lange Sätze mit Quelle
    src_very_long = sum(1 for l in src_lengths if l > very_long_len) if src_lengths else 0
    src_very_long_ratio = src_very_long / max(1, len(src_sents)) if src_sents else 0
    tgt_very_long_ratio = very_long / max(1, len(sents))
    # Nur Issue wenn Ziel signifikant mehr sehr lange Sätze hat
    if very_long >= 2 and tgt_very_long_ratio > very_long_ratio and tgt_very_long_ratio > src_very_long_ratio + 0.15:
        issues.append(QAIssue("READABILITY_MANY_LONG", "minor", "readability", f"Viele sehr lange Sätze ({very_long})", src, tgt, segment_index))
    qe_ratio = (tgt.count('?') + tgt.count('!')) / max(1, len(sents))
    if qe_ratio < staccato_gate_qe_ratio:
        if (any(l > 60 for l in lengths) or avg_len > 60) and very_short >= staccato_min_short and very_short / max(1,len(sents)) > staccato_ratio:
            issues.append(QAIssue("READABILITY_STACCATTO", "minor", "readability", "Viele extrem kurze Sätze (Stakkato)", src, tgt, segment_index))
    lix = _compute_lix(tgt)
    if lix and lix > lix_thr:
        # Nur melden wenn Zieltext signifikant komplexer als Quelltext
        src_lix = _compute_lix(src) if src else None
        if src_lix is None or lix > src_lix + 10:
            issues.append(QAIssue("READABILITY_LIX_HIGH", "minor", "readability", f"Hoher LIX Index ({lix:.1f})", src, tgt, segment_index, {"lix": round(lix,1), "src_lix": round(src_lix, 1) if src_lix else None}))
    return issues

def token_is_base64_suspect(tok: str, src_text: str) -> bool:
    """Prüft ob ein Token verdächtig nach Base64 aussieht.
    
    VERBESSERT: Upper Bound für sehr lange Tokens.
    """
    if not tok:
        return False
    if tok in (src_text or ''):
        return False
    # Mindestlänge höher für geringere False Positives
    if len(tok) < 44 or len(tok) % 4 != 0:
        return False
    # Upper Bound: extrem lange Blobs sind per se verdächtig, aber kürzen für Report
    if len(tok) > 800:
        return True  # Sehr langer Block = definitiv Base64-verdächtig
    # Ausschlüsse: HEX-IDs, JWTs
    if HEX_LONG.match(tok) or JWT_PATTERN.match(tok):
        return False
    if not BASE64_PATTERN.match(tok):
        return False
    return True

# VERBESSERT: Model-Cache als Singleton für SentenceTransformer (vermeidet Neuinitialisierung)
_ST_MODEL_CACHE: Dict[str, Any] = {}
_OLLAMA_SESSION: Any = None  # requests.Session für Connection-Reuse
_OLLAMA_AVAILABLE_MODELS: set = set()  # 🔧 NEU: Cache für verfügbare Modelle

def _get_sentence_transformer(device: str) -> Any:
    """Cached SentenceTransformer Singleton."""
    global _ST_MODEL_CACHE
    key = f"paraphrase-MiniLM-L6-v2:{device}"
    if key not in _ST_MODEL_CACHE:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _ST_MODEL_CACHE[key] = SentenceTransformer('paraphrase-MiniLM-L6-v2', device=device)
    return _ST_MODEL_CACHE[key]

def _get_ollama_session():
    """🔧 VERBESSERT: Cached requests.Session mit Retry-Adapter für Ollama."""
    global _OLLAMA_SESSION
    if _OLLAMA_SESSION is None:
        import requests
        from urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        
        _OLLAMA_SESSION = requests.Session()
        
        # Retry-Strategie: 3 Versuche bei Timeouts/Verbindungsfehlern
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,  # 0.5s, 1s, 2s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=5, pool_maxsize=10)
        _OLLAMA_SESSION.mount("http://", adapter)
        _OLLAMA_SESSION.mount("https://", adapter)
        
    return _OLLAMA_SESSION

def _check_ollama_model_available(model: str, host: str = None) -> bool:
    """🔧 NEU: Prüft ob ein Ollama-Modell verfügbar ist."""
    global _OLLAMA_AVAILABLE_MODELS
    
    # Cache-Hit
    if model in _OLLAMA_AVAILABLE_MODELS:
        return True
    
    try:
        if host is None:
            host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
        session = _get_ollama_session()
        resp = session.get(f"{host}/api/tags", timeout=5)
        if resp.ok:
            data = resp.json()
            models = [m.get('name', '') for m in data.get('models', [])]
            # Auch kurze Namen matchen (llama3.2:3b -> llama3.2)
            for m in models:
                _OLLAMA_AVAILABLE_MODELS.add(m)
                if ':' in m:
                    _OLLAMA_AVAILABLE_MODELS.add(m.split(':')[0])
            return model in _OLLAMA_AVAILABLE_MODELS or any(model in m for m in _OLLAMA_AVAILABLE_MODELS)
    except Exception:
        pass
    return False

def check_semantic_similarity(pairs: Iterable[Tuple[str,str]], threshold: float = 0.70, *,
                              use_ollama: bool = False,
                              ollama_model: str = 'nomic-embed-text') -> List[QAIssue]:
    issues: List[QAIssue] = []
    try:
        import hashlib, json, os, time as _t
        cache_dir = os.environ.get('QUALITY_GUI_SEMANTIC_CACHE_DIR') or os.path.join(os.getcwd(), 'semantic_cache')
        try:
            if not os.path.isdir(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
        except Exception:
            cache_dir = None
        memory_cache = getattr(check_semantic_similarity, '_mem', None)
        if memory_cache is None:
            memory_cache = {}
            setattr(check_semantic_similarity, '_mem', memory_cache)
        # Optional Netzwerk komplett deaktivieren
        if os.environ.get('QUALITY_GUI_DISABLE_NETWORK', '0') == '1':
            use_ollama = False
        backend = 'st'
        model = None; tok = None; mdl = None; use_util = True
        if use_ollama:
            try:
                # 🔧 VERBESSERT: Zuerst Modell-Verfügbarkeit prüfen
                _host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
                if not _check_ollama_model_available(ollama_model, _host):
                    backend = 'st'  # Fallback wenn Modell nicht verfügbar
                else:
                    session = _get_ollama_session()
                    _resp = session.post(f"{_host}/api/embeddings", json={"model": ollama_model, "prompt": "test"}, timeout=8)
                    if _resp.ok:
                        backend = 'ollama'
                        
                        def _ollama_embed(texts):
                            """🔧 VERBESSERT: Ollama Embedding mit Retry und Fehlertoleranz."""
                            out = []
                            for _t_text in texts:
                                for attempt in range(2):  # Max 2 Versuche
                                    try:
                                        r = session.post(
                                            f"{_host}/api/embeddings", 
                                            json={"model": ollama_model, "prompt": _t_text[:4096]},  # Limit Prompt-Länge
                                            timeout=45  # Erhöhter Timeout
                                        )
                                        if r.ok:
                                            data = r.json()
                                            emb = data.get('embedding')
                                            if emb:
                                                out.append(emb)
                                                break
                                            else:
                                                out.append(None)
                                                break
                                        elif r.status_code == 404:
                                            # Modell nicht gefunden
                                            out.append(None)
                                            break
                                    except Exception:
                                        if attempt == 1:  # Letzter Versuch
                                            out.append(None)
                                        import time as _time
                                        _time.sleep(0.5)  # Kurze Pause vor Retry
                            return out
            except Exception:
                backend = 'st'
        if backend == 'st':
            try:
                # VERBESSERT: Nutze cached Model statt Neuinitialisierung
                _device = None
                try:
                    import torch  # type: ignore
                    if os.environ.get('QUALITY_GUI_DEVICE'):
                        _device = os.environ['QUALITY_GUI_DEVICE']
                    else:
                        _device = 'cuda' if torch.cuda.is_available() else 'cpu'
                except Exception:
                    _device = 'cpu'
                model = _get_sentence_transformer(_device)
                use_util = True
            except Exception:
                try:
                    from transformers import AutoTokenizer, AutoModel  # type: ignore
                    import torch  # type: ignore
                    tok = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-MiniLM-L6-v2')
                    mdl = AutoModel.from_pretrained('sentence-transformers/paraphrase-MiniLM-L6-v2')
                    if os.environ.get('QUALITY_GUI_DEVICE'):
                        _dev = os.environ['QUALITY_GUI_DEVICE']
                    else:
                        _dev = 'cuda' if torch.cuda.is_available() else 'cpu'
                    mdl.to(_dev)
                    use_util = False
                except Exception:
                    # ============================================
                    # FALLBACK: Leichtgewichtiger Token-Overlap-Vergleich
                    # Wenn weder SentenceTransformers noch Ollama verfügbar,
                    # nutze N-Gram-Overlap + Strukturvergleich als Heuristik.
                    # ============================================
                    backend = 'lightweight'
        if backend == 'lightweight':
            _logger.info("Semantic check: weder SentenceTransformers noch Ollama verfügbar → leichtgewichtiger Fallback")
            similarities: List[float] = []
            below_threshold = 0
            import re as _re_sem
            _NUM_RE = _re_sem.compile(r'\b\d+(?:[.,]\d+)*\b')
            _NAME_RE = _re_sem.compile(r'\b[A-ZÄÖÜ][a-zäöüß]{2,}\b')
            _SENT_RE = _re_sem.compile(r'(?<=[.!?])\s+')
            _WORD_RE = _re_sem.compile(r'\b\w{3,}\b')
            def _lightweight_similarity(src: str, tgt: str) -> float:
                """Leichtgewichtiger Ähnlichkeits-Score ohne ML-Modelle.
                
                Kombiniert 7 Heuristiken mit angepassten Neutralwerten,
                damit fehlende Merkmale nicht fälschlich hohe Scores erzeugen.
                  1. Wort-/Token-Overlap inkl. Kognaten-Erkennung (25%)
                  2. Zahlen-Übereinstimmung                       (15%)
                  3. Eigennamen-Overlap                           (15%)
                  4. Satzanzahl-Verhältnis                        (10%)
                  5. Längen-Verhältnis                            (15%)
                  6. Interpunktions-Muster                        (10%)
                  7. Character-Bigram Overlap                     (10%)
                """
                if not src or not tgt:
                    return 0.0
                score = 0.0
                src_lower = src.lower()
                tgt_lower = tgt.lower()
                
                # 1. Wort-/Token-Overlap (stärkstes Signal)
                # Übersetzungen teilen Zahlen, Eigennamen, Fachbegriffe, Kognaten
                src_tokens = set(_WORD_RE.findall(src_lower))
                tgt_tokens = set(_WORD_RE.findall(tgt_lower))
                if src_tokens and tgt_tokens:
                    direct_matches = src_tokens & tgt_tokens
                    # Kognaten-Erkennung: gemeinsamer Prefix ≥ 4 Zeichen
                    near = 0
                    src_unmatched = src_tokens - direct_matches
                    tgt_unmatched = tgt_tokens - direct_matches
                    for st in src_unmatched:
                        if len(st) < 4:
                            continue
                        for tt in tgt_unmatched:
                            if len(tt) >= 4 and st[:4] == tt[:4]:
                                near += 1
                                break
                    total_unique = len(src_tokens | tgt_tokens)
                    match_ratio = (len(direct_matches) + near * 0.5) / total_unique if total_unique else 0.0
                    # Skalierung: selbst 0.15 Overlap = gutes Signal
                    token_score = min(1.0, match_ratio * 5.0)
                    score += token_score * 0.25
                else:
                    score += 0.05  # Fast keine Tokens → minimaler Beitrag
                
                # 2. Zahlen: Gleiche Zahlen in Source und Target
                src_nums = set(_NUM_RE.findall(src))
                tgt_nums = set(_NUM_RE.findall(tgt))
                if src_nums or tgt_nums:
                    all_nums = src_nums | tgt_nums
                    common_nums = src_nums & tgt_nums
                    num_score = len(common_nums) / len(all_nums) if all_nums else 1.0
                    score += num_score * 0.15
                else:
                    score += 0.05  # Keine Zahlen → reduzierter Neutralwert
                
                # 3. Eigennamen: Müssen erhalten bleiben
                src_names = set(_NAME_RE.findall(src))
                tgt_names = set(_NAME_RE.findall(tgt))
                if src_names:
                    names_found = sum(1 for n in src_names if n.lower() in tgt_lower)
                    name_score = names_found / len(src_names)
                    score += name_score * 0.15
                else:
                    score += 0.05  # Keine Eigennamen → reduzierter Neutralwert
                
                # 4. Satzanzahl: Übersetzungen haben ähnliche Satzstruktur
                src_sents = len(_SENT_RE.split(src)) or 1
                tgt_sents = len(_SENT_RE.split(tgt)) or 1
                sent_ratio = min(src_sents, tgt_sents) / max(src_sents, tgt_sents)
                score += sent_ratio * 0.10
                
                # 5. Längen-Verhältnis: Übersetzungen haben ähnliche Länge
                len_ratio = min(len(src), len(tgt)) / max(len(src), len(tgt), 1)
                if len_ratio > 0.5:
                    len_score = min(1.0, len_ratio / 0.7)
                else:
                    len_score = len_ratio
                score += len_score * 0.15
                
                # 6. Interpunktions-Muster
                src_punct = _re_sem.findall(r'[.!?;:,()\[\]{}]', src)
                tgt_punct = _re_sem.findall(r'[.!?;:,()\[\]{}]', tgt)
                if src_punct or tgt_punct:
                    from collections import Counter as _Ctr
                    sp = _Ctr(src_punct)
                    tp = _Ctr(tgt_punct)
                    all_keys = set(sp) | set(tp)
                    punct_sim = sum(min(sp.get(k, 0), tp.get(k, 0)) for k in all_keys) / max(sum(sp.values()) + sum(tp.values()), 1) * 2
                    score += min(1.0, punct_sim) * 0.10
                # Keine Satzzeichen → 0 Beitrag (nicht neutral)
                
                # 7. Character-Bigram Overlap
                src_bigrams = set(src_lower[i:i+2] for i in range(len(src_lower)-1) if src_lower[i:i+2].strip())
                tgt_bigrams = set(tgt_lower[i:i+2] for i in range(len(tgt_lower)-1) if tgt_lower[i:i+2].strip())
                if src_bigrams and tgt_bigrams:
                    bigram_overlap = len(src_bigrams & tgt_bigrams) / max(len(src_bigrams | tgt_bigrams), 1)
                    score += bigram_overlap * 0.10
                else:
                    score += 0.02
                
                return score
            
            # Schwelle für Lightweight-Fallback ist niedriger (weniger genau)
            eff_thr = max(0.35, threshold - 0.20)
            for pair_idx, (src, tgt) in enumerate(pairs):
                if not src or not tgt or len(src.strip()) < 10:
                    continue
                sim = _lightweight_similarity(src, tgt)
                similarities.append(sim)
                if sim < eff_thr:
                    below_threshold += 1
                    issues.append(QAIssue("SEMANTIC_LOW", "minor", "semantic",
                        f"Strukturelle Ähnlichkeit niedrig ({sim:.2f} < {eff_thr:.2f}) [Lightweight-Fallback]",
                        src[:120], tgt[:120], pair_idx,
                        {"similarity": round(sim, 3), "threshold": eff_thr,
                         "backend": "lightweight", "src_len": len(src), "tgt_len": len(tgt)}))
            if similarities:
                avg_sim = sum(similarities) / len(similarities)
                ratio_low = below_threshold / len(similarities)
                if avg_sim < 0.50 and ratio_low > 0.35 and len(similarities) >= 5:
                    issues.append(QAIssue("SEMANTIC_GLOBAL_LOW", "minor", "semantic",
                        f"Globale Struktur-Ähnlichkeit schwach: Schnitt {avg_sim:.2f}, {ratio_low*100:.0f}% unter Schwelle [Lightweight-Fallback]",
                        "", "", -1,
                        {"avg": round(avg_sim, 3), "low_ratio": round(ratio_low, 3),
                         "count": len(similarities), "backend": "lightweight"}))
            return issues
        def _embed_pair(s: str, t: str) -> Optional[float]:
            try:
                model_id = f"{backend}:{ollama_model if backend=='ollama' else 'paraphrase-MiniLM-L6-v2'}"
                key_raw = f"{len(s)}:{len(t)}::{s[:1024]}|||{t[:1024]}|{model_id}".encode('utf-8','ignore')
                key = hashlib.sha256(key_raw).hexdigest()
                if key in memory_cache:
                    return memory_cache[key]
                if cache_dir:
                    disk_path = os.path.join(cache_dir, key[:2] + '.json')
                    try:
                        if os.path.isfile(disk_path):
                            with open(disk_path, 'r', encoding='utf-8') as _rf:
                                bucket = json.load(_rf)
                            if key in bucket:
                                memory_cache[key] = float(bucket[key]['sim']); return memory_cache[key]
                    except Exception:
                        pass
                if backend == 'ollama':
                    vecs = _ollama_embed([s, t])  # type: ignore
                    if not vecs[0] or not vecs[1]:
                        return None
                    # Pure-Python Cosine ohne NumPy
                    def _cos(u, v):
                        dot = 0.0
                        ss_u = 0.0; ss_v = 0.0
                        for x, y in zip(u, v):
                            dot += x * y
                            ss_u += x * x
                            ss_v += y * y
                        nu = ss_u ** 0.5; nv = ss_v ** 0.5
                        den = (nu * nv) or 1.0
                        return float(dot / den)
                    sim_val = _cos(vecs[0], vecs[1])
                else:
                    if use_util:
                        emb = model.encode([s, t], convert_to_tensor=True, normalize_embeddings=True)
                        sim_val = float((emb[0] @ emb[1]).item())
                    else:
                        try:
                            import torch  # type: ignore
                        except Exception:
                            return None
                        with torch.no_grad():
                            a_ids = tok(s, return_tensors='pt', truncation=True, max_length=256)
                            b_ids = tok(t, return_tensors='pt', truncation=True, max_length=256)
                            a_out = mdl(**a_ids).last_hidden_state.mean(dim=1)
                            b_out = mdl(**b_ids).last_hidden_state.mean(dim=1)
                            a_n = a_out / a_out.norm(dim=1, keepdim=True)
                            b_n = b_out / b_out.norm(dim=1, keepdim=True)
                            sim_val = float((a_n * b_n).sum())
                memory_cache[key] = sim_val
                if cache_dir:
                    try:
                        disk_path = os.path.join(cache_dir, key[:2] + '.json')
                        bucket = {}
                        if os.path.isfile(disk_path):
                            try:
                                with open(disk_path,'r',encoding='utf-8') as _rf:
                                    bucket = json.load(_rf)
                            except Exception:
                                bucket = {}
                        bucket[key] = {'sim': sim_val, 'ts': int(_t.time())}
                        if len(bucket) > 400:
                            try:
                                items = sorted(bucket.items(), key=lambda x: x[1].get('ts',0), reverse=True)[:350]
                                bucket = {k:v for k,v in items}
                            except Exception:
                                pass
                        with open(disk_path,'w',encoding='utf-8') as _f:
                            import json as _json
                            _json.dump(bucket, _f, ensure_ascii=False)
                    except Exception:
                        pass
                return sim_val
            except Exception:
                return None
        similarities: List[float] = []
        below_threshold = 0
        # Sampling / Pair Cap
        max_pairs = int(os.getenv("QUALITY_GUI_SEMANTIC_MAX_PAIRS", "400"))
        # Untergrenze setzen damit Sampling-Berechnung (max_pairs - 20) nie 0 oder negativ wird
        if max_pairs < 30:
            max_pairs = 30
        pairs_list = list(pairs)
        if len(pairs_list) > max_pairs:
            step = max(1, len(pairs_list) // (max_pairs - 20))
            pairs_list = pairs_list[:10] + pairs_list[10::step][:max_pairs-10]
        for pair_idx, (src, tgt) in enumerate(pairs_list):
            if not src or not tgt or len(src) < 15:
                continue
            sl = len(src)
            if backend == 'ollama':
                # nomic-embed-text und ähnliche Modelle sind monolingual (EN);
                # Cross-Language-Paare erreichen typischerweise nur 0.35-0.55
                dyn = 0.38 if sl < 60 else (0.42 if sl < 120 else 0.45)
            else:
                # Multilinguale ST-Modelle haben höhere Cross-Language-Ähnlichkeit
                dyn = 0.65 if sl < 60 else (0.70 if sl < 120 else 0.75)
            eff_thr = max(threshold, dyn)
            try:
                sim = _embed_pair(src, tgt)
                if sim is None:
                    continue
                similarities.append(sim)
                if sim < eff_thr:
                    below_threshold += 1
                    # 🔧 FIX: segment_index als separater Parameter (nicht in meta!)
                    issues.append(QAIssue("SEMANTIC_LOW", "minor", "semantic", 
                        f"Semantische Ähnlichkeit niedrig ({sim:.2f} < {eff_thr:.2f})", 
                        src[:120], tgt[:120], pair_idx,
                        {"similarity": round(sim,3), "threshold": eff_thr, 
                         "src_len": len(src), "tgt_len": len(tgt)}))
            except Exception:
                continue
        if similarities:
            avg_sim = sum(similarities)/len(similarities)
            ratio_low = below_threshold / len(similarities)
            if avg_sim < 0.72 and ratio_low > 0.35 and len(similarities) >= 5:
                issues.append(QAIssue("SEMANTIC_GLOBAL_LOW", "minor", "semantic", f"Globale Semantik schwach: Schnitt {avg_sim:.2f}, {ratio_low*100:.0f}% unter Schwelle", "", "", -1, {"avg": round(avg_sim,3), "low_ratio": round(ratio_low,3), "count": len(similarities)}))
    except Exception:
        return []
    return issues


def _select_segments_for_llm_check(pairs: List[Tuple[str, str]], max_count: int = 50) -> List[Tuple[int, str, str]]:
    """Intelligente Segment-Auswahl für LLM-Prüfung.
    
    Priorisiert:
    1. Lange/komplexe Segmente (mehr Fehlerrisiko)
    2. Segmente mit Zahlen/Namen (kritische Elemente)
    3. Segmente mit ungewöhnlichem Längenverhältnis
    4. Gleichmäßige Verteilung über das Dokument
    
    Returns: Liste von (original_index, source, target) Tupeln
    """
    if not pairs:
        return []
    
    
    # Score für jedes Segment berechnen
    scored_pairs: List[Tuple[float, int, str, str]] = []
    
    for idx, (src, tgt) in enumerate(pairs):
        if not src or not tgt or len(src.strip()) < 20:
            continue
        
        score = 0.0
        
        # 1. Länge (längere Segmente = mehr Fehlerrisiko)
        combined_len = len(src) + len(tgt)
        if combined_len > 500:
            score += 3.0
        elif combined_len > 200:
            score += 2.0
        elif combined_len > 100:
            score += 1.0
        
        # 2. Komplexität: Satzanzahl
        src_sentences = len(re.findall(r'[.!?]+', src))
        if src_sentences >= 3:
            score += 2.0
        elif src_sentences >= 2:
            score += 1.0
        
        # 3. Zahlen vorhanden (kritisch für Genauigkeit)
        src_numbers = re.findall(r'\d+(?:[.,]\d+)?', src)
        tgt_numbers = re.findall(r'\d+(?:[.,]\d+)?', tgt)
        if src_numbers:
            score += 2.5  # Zahlen sind kritisch
            # Bonus wenn Anzahl unterschiedlich
            if len(src_numbers) != len(tgt_numbers):
                score += 3.0
        
        # 4. Eigennamen (Großbuchstaben-Wörter)
        src_names = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*\b', src)
        if len(src_names) >= 2:
            score += 1.5
        
        # 5. Ungewöhnliches Längenverhältnis
        if len(src) > 0 and len(tgt) > 0:
            ratio = len(tgt) / len(src)
            if ratio < 0.5 or ratio > 2.0:
                score += 2.5  # Verdächtig kurz/lang
        
        # 6. Position im Dokument (erste und letzte Segmente oft wichtig)
        total = len(pairs)
        if idx < total * 0.1 or idx > total * 0.9:
            score += 0.5
        
        scored_pairs.append((score, idx, src, tgt))
    
    # Nach Score sortieren (höchster zuerst)
    scored_pairs.sort(key=lambda x: x[0], reverse=True)
    
    # Top-Segmente nehmen, aber auch Verteilung sicherstellen
    selected: List[Tuple[int, str, str]] = []
    selected_indices: set = set()
    
    # Erst die Top-Scored nehmen (70% des Budgets)
    top_budget = int(max_count * 0.7)
    for score, idx, src, tgt in scored_pairs[:top_budget]:
        selected.append((idx, src, tgt))
        selected_indices.add(idx)
    
    # Rest gleichmäßig verteilen (30% des Budgets)
    remaining_budget = max_count - len(selected)
    if remaining_budget > 0 and len(pairs) > len(selected):
        # Alle noch nicht selektierten Indizes sammeln
        available = [i for i in range(len(pairs)) if i not in selected_indices]
        if available:
            step = max(1, len(available) // remaining_budget)
            for pos in range(0, len(available), step):
                i = available[pos]
                if len(selected) >= max_count:
                    break
                src, tgt = pairs[i]
                if src and tgt and len(src.strip()) >= 20:
                    selected.append((i, src, tgt))
                    selected_indices.add(i)
    
    # Nach Original-Index sortieren für konsistente Verarbeitung
    selected.sort(key=lambda x: x[0])
    
    return selected[:max_count]


def check_translation_accuracy_llm(pairs: Iterable[Tuple[str,str]], *, 
                                   ollama_model: str = 'llama3.2:3b',
                                   max_pairs: int = 50) -> List[QAIssue]:
    """Tiefe LLM-basierte Prüfung der Übersetzungsqualität mit Ollama.
    
    🔧 VERBESSERUNG: Intelligente Segment-Auswahl statt nur erste N Paare.
    Priorisiert komplexe, lange und risikoreiche Segmente.
    
    Prüft:
    - Ist die Bedeutung korrekt übertragen?
    - Fehlen wichtige Informationen?
    - Wurden Informationen hinzugefügt, die nicht im Original stehen?
    - Sind Zahlen und Namen korrekt übernommen?
    """
    issues: List[QAIssue] = []
    import os
    
    # Nur wenn Ollama verfügbar
    if os.environ.get('QUALITY_GUI_DISABLE_NETWORK', '0') == '1':
        return issues
    
    try:
        import requests
        import json
        
        ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
        # Teste Ollama-Verbindung
        try:
            test_resp = requests.get(f"{ollama_host}/api/tags", timeout=3)
            if not test_resp.ok:
                return issues
        except Exception:
            return issues
        
        # 🔧 VERBESSERUNG: Intelligente Segment-Auswahl
        all_pairs = list(pairs)
        selected_segments = _select_segments_for_llm_check(all_pairs, max_pairs)
        _logger.debug("LLM-Check: %d Segmente von %d selektiert", len(selected_segments), len(all_pairs))
        
        for original_idx, src, tgt in selected_segments:
            # Kürze für LLM-Kontext
            src_excerpt = src[:1500] if len(src) > 1500 else src
            tgt_excerpt = tgt[:1500] if len(tgt) > 1500 else tgt
            
            prompt = f"""Du bist ein Übersetzungsqualitätsprüfer. Analysiere ob die Übersetzung den Ausgangstext korrekt wiedergibt.

AUSGANGSTEXT:
{src_excerpt}

ÜBERSETZUNG:
{tgt_excerpt}

Prüfe folgende Punkte und antworte NUR im JSON-Format:
{{
  "meaning_correct": true/false,
  "missing_info": ["Liste fehlender Informationen"] oder [],
  "added_info": ["Liste hinzugefügter Informationen"] oder [],
  "number_errors": ["Zahlen die falsch sind"] oder [],
  "name_errors": ["Namen die falsch sind"] oder [],
  "severity": "ok" | "minor" | "major" | "critical",
  "summary": "Kurze Zusammenfassung auf Deutsch (max 100 Zeichen)"
}}

Antworte NUR mit dem JSON, kein anderer Text."""

            try:
                resp = requests.post(
                    f"{ollama_host}/api/generate",
                    json={
                        "model": ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",  # Erzwingt syntaktisch korrektes JSON
                        "options": {"temperature": 0.1, "num_predict": 500}
                    },
                    timeout=90  # Mehr Zeit für komplexe Analyse
                )
                
                if not resp.ok:
                    continue
                
                result = resp.json()
                response_text = result.get('response', '')
                _logger.debug("LLM-Check Seg %d: Response-Länge=%d", original_idx, len(response_text))
                
                # VERBESSERT: Robustere JSON-Extraktion (greedy first { to last })
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
                    _logger.debug("LLM-Check Seg %d: Kein JSON gefunden in Response", original_idx)
                    continue
                
                json_blob = response_text[start_idx:end_idx + 1]
                
                try:
                    analysis = json.loads(json_blob)
                except json.JSONDecodeError:
                    # LLMs produzieren oft invalides JSON (z.B. "Katze" -> "Hund")
                    # Bereinigung: Arrow-Notation, trailing commas, etc.
                    cleaned = json_blob
                    # "A" -> "B" zu "A → B" (String-Inhalte normalisieren)
                    cleaned = re.sub(r'"([^"]*?)"\s*->\s*"([^"]*?)"', r'"\1 → \2"', cleaned)
                    # Trailing commas vor ] oder }
                    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
                    # true/false/null in beliebiger Groß-/Kleinschreibung
                    cleaned = re.sub(r'\bTrue\b', 'true', cleaned)
                    cleaned = re.sub(r'\bFalse\b', 'false', cleaned)
                    cleaned = re.sub(r'\bNone\b', 'null', cleaned)
                    try:
                        analysis = json.loads(cleaned)
                    except json.JSONDecodeError:
                        # Letzter Fallback: json5
                        try:
                            import json5  # type: ignore
                            analysis = json5.loads(json_blob)
                        except Exception:
                            continue
                
                # Schema-Validierung: Pflichtfelder prüfen
                required_keys = {'severity'}
                if not all(k in analysis for k in required_keys):
                    _logger.debug("LLM-Check Seg %d: Schema-Validierung fehlgeschlagen", original_idx)
                    continue
                if not isinstance(analysis.get('severity'), str):
                    continue
                
                severity = analysis.get('severity', 'ok')
                if severity == 'ok':
                    continue
                
                # Erstelle Issues basierend auf Analyse
                missing = analysis.get('missing_info', [])
                added = analysis.get('added_info', [])
                number_errors = analysis.get('number_errors', [])
                name_errors = analysis.get('name_errors', [])
                summary = analysis.get('summary', '')
                
                # 🔧 FIX: segment_index als separater Parameter
                issue_meta_base = {"llm_model": ollama_model}
                
                if missing and len(missing) > 0:
                    issues.append(QAIssue(
                        "LLM_MISSING_INFO",
                        "major" if len(missing) > 2 else "minor",
                        "accuracy",
                        f"Fehlende Informationen: {', '.join(str(m) for m in missing[:3])}",
                        src_excerpt[:200],
                        tgt_excerpt[:200],
                        original_idx,
                        {**issue_meta_base, "missing": missing}
                    ))
                
                if added and len(added) > 0:
                    issues.append(QAIssue(
                        "LLM_ADDED_INFO",
                        "minor",
                        "accuracy",
                        f"Hinzugefügte Informationen: {', '.join(str(a) for a in added[:3])}",
                        src_excerpt[:200],
                        tgt_excerpt[:200],
                        original_idx,
                        {**issue_meta_base, "added": added}
                    ))
                
                if number_errors and len(number_errors) > 0:
                    issues.append(QAIssue(
                        "LLM_NUMBER_ERROR",
                        "critical",
                        "accuracy",
                        f"Zahlenfehler: {', '.join(str(n) for n in number_errors[:3])}",
                        src_excerpt[:200],
                        tgt_excerpt[:200],
                        original_idx,
                        {**issue_meta_base, "errors": number_errors}
                    ))
                
                if name_errors and len(name_errors) > 0:
                    issues.append(QAIssue(
                        "LLM_NAME_ERROR",
                        "major",
                        "accuracy",
                        f"Namensfehler: {', '.join(str(n) for n in name_errors[:3])}",
                        src_excerpt[:200],
                        tgt_excerpt[:200],
                        original_idx,
                        {**issue_meta_base, "errors": name_errors}
                    ))
                
                # Allgemeiner Bedeutungsfehler
                if not analysis.get('meaning_correct', True) and not missing and not added:
                    issues.append(QAIssue(
                        "LLM_MEANING_ERROR",
                        severity if severity in ('minor', 'major', 'critical') else 'major',
                        "accuracy",
                        f"Bedeutungsfehler: {summary}" if summary else "Bedeutung nicht korrekt übertragen",
                        src_excerpt[:200],
                        tgt_excerpt[:200],
                        original_idx,
                        {**issue_meta_base, "summary": summary}
                    ))
                    
            except requests.exceptions.Timeout:
                _logger.debug("LLM-Check: Timeout für Segment %d", original_idx)
                continue
            except Exception as _llm_exc:
                _logger.debug("LLM-Check: Fehler Segment %d: %s", original_idx, type(_llm_exc).__name__)
                continue
                
    except Exception:
        return []
    
    return issues

def run_phase3_checks(pairs: Iterable[Tuple[str,str]], *, enable_semantic: bool = True,
                          enable_consistency: bool = True,
                          enable_ocr_check: bool = True,
                          semantic_use_ollama: bool = False,
                          semantic_ollama_model: str = 'nomic-embed-text',
                          risk_complement_phase2: bool = True,
                          # 🔧 FIX: Threshold von 0.70 auf 0.55 gesenkt für Cross-Language Übersetzungen
                          # Bei DE→EN haben auch korrekte Übersetzungen oft nur 0.5-0.65 Similarity
                          semantic_threshold: float = 0.55,
                          consistency_min_occurrences: int = 2,
                          # Readability tuning (optional)
                          avg_len_thr: int = 140,
                          very_long_len: int = 180,
                          very_long_ratio: float = 0.30,
                          staccato_short_len: int = 25,
                          staccato_min_short: int = 3,
                          staccato_ratio: float = 0.60,
                          lix_thr: float = 55.0,
                          staccato_gate_qe_ratio: float = 0.40,
                          spellcheck_config: Optional[Dict[str, Any]] = None,
                          pair_infos: Optional[List[Dict[str, Any]]] = None) -> List[QAIssue]:
    all_pairs = list(pairs)
    issues: List[QAIssue] = []
    grammar_checker = None
    grammar_findings: Dict[int, List[Dict[str, Any]]] = {}
    spell_engine: Optional[_SpellcheckEngine] = None
    grammar_limit = 0
    if spellcheck_config and spellcheck_config.get("enabled", True):
        grammar_limit = int(spellcheck_config.get("max_issues_per_segment", 0) or 0)
        if GrammarChecker is not None:
            try:
                grammar_checker = GrammarChecker(
                    enable_languagetool=bool(spellcheck_config.get("use_language_tool", True)),
                    enable_hunspell=bool(spellcheck_config.get("use_hunspell", True)),
                    enable_ollama=bool(spellcheck_config.get("use_ollama", True)),
                    ratio_threshold=float(spellcheck_config.get("ratio_threshold", 0.15) or 0.15),
                    batch_lt_min_segments=int(spellcheck_config.get("batch_lt_min_segments", 40) or 40)
                )
                target_segments = [tgt if isinstance(tgt, str) else str(tgt or "") for _, tgt in all_pairs]
                target_lang = spellcheck_config.get("target_language") or spellcheck_config.get("language") or spellcheck_config.get("locale")
                if isinstance(target_lang, dict):
                    target_lang = target_lang.get("target") or target_lang.get("language")
                language = str(target_lang or "auto")
                raw_grammar = grammar_checker.analyze_segments(target_segments, language=language)
                for entry in raw_grammar:
                    idx = entry.get("segment_index")
                    if not isinstance(idx, int) or idx < 0 or idx >= len(all_pairs):
                        continue
                    bucket = grammar_findings.setdefault(idx, [])
                    if grammar_limit and len(bucket) >= grammar_limit:
                        continue
                    bucket.append(entry)
            except Exception:
                grammar_checker = None
                grammar_findings.clear()
    if spellcheck_config and not grammar_checker:
        try:
            if spellcheck_config.get("enabled", True):
                spell_engine = _SpellcheckEngine(spellcheck_config)
        except Exception:
            spell_engine = None
    for idx, (src, tgt) in enumerate(all_pairs):
        pair_meta: Dict[str, Any] = {}
        if pair_infos and idx < len(pair_infos):
            candidate = pair_infos[idx]
            if isinstance(candidate, dict):
                pair_meta = candidate
        issues.extend(check_style(src, tgt, segment_index=idx))
        issues.extend(check_risk(src, tgt, complement_phase2=risk_complement_phase2, segment_index=idx))
        issues.extend(check_readability(
            src, tgt,
            avg_len_thr=avg_len_thr,
            very_long_len=very_long_len,
            very_long_ratio=very_long_ratio,
            staccato_short_len=staccato_short_len,
            staccato_min_short=staccato_min_short,
            staccato_ratio=staccato_ratio,
            lix_thr=lix_thr,
            staccato_gate_qe_ratio=staccato_gate_qe_ratio,
            segment_index=idx,
        ))
        if grammar_checker:
            for entry in grammar_findings.get(idx, []):
                severity = str(entry.get("severity", "minor") or "minor").lower()
                if severity not in ("minor", "major", "critical"):
                    severity = "minor"
                meta_payload: Dict[str, Any] = {
                    "checker": entry.get("checker"),
                    "suggestion": entry.get("suggestion"),
                    "excerpt": entry.get("source_excerpt")
                }
                if pair_meta:
                    meta_payload["pair"] = {
                        "index": pair_meta.get("index", idx),
                        "source": pair_meta.get("source_name"),
                        "target": pair_meta.get("translation_name")
                    }
                issues.append(QAIssue(
                    entry.get("rule_id", "GRAMMAR"),
                    severity,
                    "grammar",
                    entry.get("message", ""),
                    src,
                    tgt,
                    idx,  # 🔧 FIX: segment_index als 7. Parameter (nicht meta_payload!)
                    meta_payload
                ))
        elif spell_engine:
            for finding in spell_engine.analyze(tgt):
                meta_payload = {"details": finding}
                if pair_meta:
                    meta_payload["pair"] = {
                        "index": pair_meta.get("index", idx),
                        "source": pair_meta.get("source_name"),
                        "target": pair_meta.get("translation_name")
                    }
                issues.append(QAIssue(
                    "SPELLING_ERROR",
                    "major",
                    "orthografie",
                    f"Möglicher Rechtschreib-/Grammatikfehler: {finding.get('word', '')}",
                    src,
                    tgt,
                    idx,  # 🔧 FIX: segment_index als 7. Parameter (nicht meta_payload!)
                    meta_payload
                ))
    if enable_semantic:
        issues.extend(check_semantic_similarity(all_pairs, threshold=semantic_threshold, use_ollama=semantic_use_ollama, ollama_model=semantic_ollama_model))
    
    # LLM-basierte tiefe Übersetzungsprüfung (wenn Ollama verfügbar)
    if semantic_use_ollama and len(all_pairs) > 0:
        try:
            # 🔧 FIX: Embedding-Model (nomic-embed-text) zu Chat-Model (llama3.2:3b) für LLM-Check
            chat_model = semantic_ollama_model
            if 'embed' in chat_model.lower() or 'nomic' in chat_model.lower():
                chat_model = 'llama3.2:3b'  # Chat-Model für Übersetzungsprüfung
            llm_issues = check_translation_accuracy_llm(all_pairs, ollama_model=chat_model)
            issues.extend(llm_issues)
        except Exception:
            pass  # LLM-Prüfung ist optional
    
    # Konsistenzprüfung: gleicher Quellterm -> gleiche Übersetzung
    if enable_consistency and check_consistency_as_issues is not None and len(all_pairs) >= 5:
        try:
            consistency_issues = check_consistency_as_issues(
                all_pairs,
                min_occurrences=consistency_min_occurrences,
                check_multiword=True
            )
            issues.extend(consistency_issues)
        except Exception:
            pass  # Konsistenzprüfung ist optional
    
    # OCR-Fehlerprüfung: häufige OCR-Verwechslungen erkennen
    if enable_ocr_check and check_ocr_as_issues is not None:
        try:
            ocr_issues = check_ocr_as_issues(
                all_pairs,
                check_known_errors=True,
                check_patterns=True,
                check_confusables=True
            )
            issues.extend(ocr_issues)
        except Exception:
            pass  # OCR-Prüfung ist optional
    
    return issues

__all__ = [
    'run_phase3_checks',
    'check_style',
    'check_risk',
    'check_readability',
    'check_semantic_similarity',
    'check_translation_accuracy_llm',
    '_select_segments_for_llm_check',  # Für Tests/Debugging
    'check_consistency_as_issues',
    'check_ocr_as_issues'
]
