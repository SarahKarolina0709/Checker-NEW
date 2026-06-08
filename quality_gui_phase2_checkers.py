"""quality_gui_phase2_checkers – umbenanntes Modul (ehemals qa_phase2_checkers)."""
from __future__ import annotations
import os, re, json
import logging
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Dict, Tuple, Iterable, Optional, Set, Any

_logger = logging.getLogger(__name__)

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
NUMBER_PATTERN = re.compile(r"(?<![\w\-])[+\-]?\d+[\d.,]*\b")  # Roh-Erkennung mit optionalem Vorzeichen; Normalisierung folgt
# Einheiten direkt an Zahlen
UNIT_NEAR_NUMBER = re.compile(
    r"(?P<num>\d[\d.,]*)\s*(?P<unit>"
    r"kg|g|t|km|m|cm|mm|gb|mb|kb|%|°\s?c|°\s?f|fahrenheit|celsius|"
    r"€|£|eur|usd|gbp|ms|s|mio\.|"
    # US-Imperial / Englisch
    r"miles|mile|mi|ft|feet|foot|inch|inches|in|"
    r"lbs|lb|pounds|pound|oz|ounce|ounces|"
    r"gal|gallon|gallons|liter|litre|"
    r"ha|acres|acre|sqft|sq\s?ft"
    r")(?!\w)",
    re.IGNORECASE
)
# Einheiten vor der Zahl (€, $, %, eur/usd)
UNIT_BEFORE_NUMBER = re.compile(r"(?P<unit>€|eur|usd|£|gbp|\$|%)\s*(?P<num>\d[\d.,]*)(?!\w)", re.IGNORECASE)

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

# --- Patterns für _extract_proper_names() – einmalig kompiliert ---
_TITLE_NAME_PATTERN = re.compile(
    r'\b((?:Prof\.\s*)?Dr\.|Prof\.|Herr|Frau|Mr\.|Mrs\.|Ms\.|Dipl\.-Ing\.|Mag\.|Ing\.|RA|StB)'
    r'\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)'
    r'(?:\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?))?'
    r'(?:\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?))?\b'
)
_NAME_PAIR_PATTERN = re.compile(
    r'\b([A-ZÄÖÜ][a-zäöüß]{2,12})\s+([A-ZÄÖÜ][a-zäöüß]{2,15})\b'
)
_NAME_TRIPLE_PATTERN = re.compile(
    r'\b([A-ZÄÖÜ][a-zäöüß]{2,12})\s+([A-ZÄÖÜ][a-zäöüß]{2,12})\s+([A-ZÄÖÜ][a-zäöüß]{2,15})\b'
)
_CONTEXT_BEFORE_NAME_PATTERNS = [
    re.compile(
        rf'{ctx}\s+([A-ZÄÖÜ][a-zäöüß]{{2,15}})(?:\s+([A-ZÄÖÜ][a-zäöüß]{{2,15}}))?\b',
        re.IGNORECASE
    )
    for ctx in [
        r'(?:sagt|sagte|erklärt|erklärte|betont|betonte|meint|meinte)',
        r'(?:laut|so|gemäß|zufolge)',
        r'(?:Geschäftsführer(?:in)?|CEO|CFO|COO|CTO|Vorstand|Direktor(?:in)?)',
        r'(?:Leiter(?:in)?|Manager(?:in)?|Chef(?:in)?|Vorsitzende[rn]?)',
        r'(?:Autor(?:in)?|Sprecher(?:in)?|Experte|Expertin)',
        r'(?:Kollege|Kollegin|Mitarbeiter(?:in)?)',
    ]
]

# Patterns für check_punctuation_spacing – einmalig kompiliert
_PUNCT_SPACE_BEFORE_COLON_PATTERN = re.compile(r'[a-zäöüß]\s+:')
_PUNCT_COLON_DIGIT_PATTERN = re.compile(r'\d\s+:')
_PUNCT_HTTP_COLON_PATTERN = re.compile(r'http\s*:')
_PUNCT_SPACE_BEFORE_EXCL_PATTERN = re.compile(r'\s+[!?](?!\w)')
_PUNCT_FR_MISSING_SPACE = re.compile(r'[a-zA-Zàâäéèêëïîôùûüÿç][!?;:]')
_PUNCT_NO_SPACE_AFTER = re.compile(r'[!?][A-ZÄÖÜ]')
_PUNCT_SPACE_BEFORE_COMMA = re.compile(r'\w\s+,')
_PUNCT_NO_SPACE_AFTER_COMMA = re.compile(r',[A-Za-zÄÖÜäöüß]')

# Whitespace-Normalisierung – einmalig kompiliert
_WS_PATTERN = re.compile(r'\s+')

# ---- Weitere häufig verwendete Patterns – einmalig kompiliert ----
_WORD_COUNT_PATTERN = re.compile(r'\b\w+\b')       # Wortanzahl (check_coverage_ratio)
_WORD_SIMPLE_PATTERN = re.compile(r'\w+')           # Tokenisierung (_tokenize_lower, Token-Overlap)
_DIGIT_PATTERN = re.compile(r'\d')                 # Ziffernsuche (_normalize_number_token)
_DOT_COMMA_STRIP = re.compile(r'[.,]')             # Trennzeichen-Entfernung (_normalize_number_token)
_DIGITS_SPACES_PATTERN = re.compile(r'[.,\s]')     # Ziffernreinigung (_extract_significant_numbers)

# Patterns für _extract_significant_numbers – außerhalb der Funktion für Performance
_ENUM_MARKER_A    = re.compile(r'\([a-z0-9]\)', re.IGNORECASE)
_ENUM_MARKER_B    = re.compile(r'(?<![a-zA-Z0-9])[a-z]\)', re.IGNORECASE)
_ENUM_MARKER_C    = re.compile(r'(?<![0-9])\d\)')
_ENUM_SECTION_SYM = re.compile(r'§\s*\d+')
_ENUM_NR_PATTERN  = re.compile(r'Nr\.\s*\d+', re.IGNORECASE)
_ENUM_NUMMER_PAT  = re.compile(r'Nummer\s*\d+', re.IGNORECASE)
_DATE_ISO_REMOVE  = re.compile(r'\d{4}[-/]\d{2}[-/]\d{2}')
_DATE_EU_REMOVE   = re.compile(r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}')
# Datumsangaben mit Monatsnamen (DE/EN), z.B. "March 24, 2026", "24. März 2026",
# "24 March 2026", "March 2026". Sonst leckt die Jahreszahl als nackte Zahl
# durch (deutsche Quelle nutzt oft 24.03.2026 -> entfernt, englisches Ziel
# "March 24, 2026" -> Jahr blieb stehen -> False-Positive "Zahl neu im Ziel").
_MONTH_NAME_GROUP = (
    r'(?:Jan(?:uar|uary)?|Feb(?:ruar|ruary)?|Mär(?:z)?|March|Mar|Apr(?:il)?|'
    r'Mai|May|Jun[ie]?|Jul[iy]?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|'
    r'Okt(?:ober)?|Oct(?:ober)?|Nov(?:ember)?|Dez(?:ember)?|Dec(?:ember)?)'
)
_DATE_WORD_REMOVE = re.compile(
    r'(?:'
    r'\d{1,2}\.?\s+' + _MONTH_NAME_GROUP + r'(?:\s+\d{2,4})?'              # 24. März 2026 / 24 March
    r'|' + _MONTH_NAME_GROUP + r'\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{2,4}'   # March 24, 2026
    r'|' + _MONTH_NAME_GROUP + r'\s+\d{4}'                                  # March 2026
    r')',
    re.IGNORECASE,
)
_TIME_REMOVE      = re.compile(r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:Uhr|AM|PM|h))?', re.IGNORECASE)
_OCLOCK_REMOVE    = re.compile(r"\d{1,2}\s*(?:Uhr|o'?clock)", re.IGNORECASE)
_VERSION_REMOVE   = re.compile(r'[vV](?:ersion)?\s*\d+(?:\.\d+)+')
_PHONE_REMOVE     = re.compile(r'\+?\d{1,4}[\s\-]\(?\d{2,5}\)?[\s\-]?\d{3,}[\s\-]?\d*')

# Firmenbezeichnungen die NICHT übersetzt werden dürfen (Do Not Translate)
COMPANY_SUFFIXES_DNT = {
    # Deutsch (HINWEIS: 'mbH' entfernt - ist Substring von 'GmbH' und erzeugte False Positives)
    'GmbH', 'AG', 'KG', 'OHG', 'GbR', 'eG', 'e.V.', 'eV', 'KGaA', 'UG',
    'GmbH & Co. KG', 'GmbH & Co. OHG', 'AG & Co. KG',
    # Österreich/Schweiz
    'Ges.m.b.H.', 'GesmbH', 'GenmbH',
    # International (auch nicht übersetzen wenn im Source)
    'Ltd', 'LLC', 'Inc', 'Corp', 'PLC', 'LLP', 'S.A.', 'S.L.', 'S.r.l.', 'B.V.', 'N.V.',
}

# Whitelist für Eigennamen-False-Positives (Wochentage/Monate + häufige deutsche Substantive)
# Im Deutschen werden ALLE Substantive großgeschrieben - diese sind KEINE Eigennamen!
DEFAULT_PROPER_WHITELIST = {
    # Wochentage/Monate
    "Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag",
    "Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember",
    # Englische Wochentage/Monate
    "Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday",
    "January","February","March","April","May","June","July","August","September","October","November","December",
    # Häufige deutsche Substantive (KEINE Eigennamen!)
    "Die","Der","Das","Ein","Eine","Sie","Ihr","Wir","Uns",
    "Jahr","Jahre","Jahren","Monat","Monate","Monaten","Tag","Tage","Tagen","Woche","Wochen",
    "Zeit","Zeiten","Mal","Euro","Dollar","Prozent","Nummer","Zahl","Zahlen",
    "Firma","Firmen","Unternehmen","Gesellschaft","Konzern","Betrieb","Betriebe",
    "Mitarbeiter","Mitarbeitern","Mitarbeiterin","Mitarbeiterinnen","Angestellte","Angestellten",
    "Chef","Chefs","Geschäftsführer","Vorstand","Vorstände","Direktor","Leiter","Leiterin",
    "Kunde","Kunden","Kundin","Kundinnen","Partner","Partnern","Lieferant","Lieferanten",
    "Umsatz","Umsätze","Gewinn","Gewinne","Verlust","Verluste","Kosten","Preis","Preise",
    "Steigerung","Erhöhung","Senkung","Reduktion","Wachstum","Rückgang","Entwicklung",
    "Bericht","Berichte","Geschäftsbericht","Jahresbericht","Quartalsbericht",
    "Hauptniederlassung","Niederlassung","Niederlassungen","Filiale","Filialen","Standort","Standorte",
    "Produkt","Produkte","Produkten","Dienstleistung","Dienstleistungen","Service","Services",
    "Markt","Märkte","Märkten","Branche","Branchen","Industrie","Sektor","Bereich","Bereiche",
    "Arbeit","Projekt","Projekte","Projekten","Aufgabe","Aufgaben","Ziel","Ziele","Plan","Pläne",
    "Information","Informationen","Daten","Dokument","Dokumente","Datei","Dateien",
    "System","Systeme","Prozess","Prozesse","Verfahren","Methode","Methoden",
    "Lösung","Lösungen","Problem","Probleme","Frage","Fragen","Antwort","Antworten",
    "Ergebnis","Ergebnisse","Erfolg","Erfolge","Leistung","Leistungen","Qualität",
    "Anfang","Ende","Beginn","Abschluss","Start","Schluss",
    "Grund","Gründe","Ursache","Ursachen","Folge","Folgen","Wirkung","Auswirkung",
    "Teil","Teile","Teilen","Hälfte","Drittel","Viertel","Rest",
    "Seite","Seiten","Punkt","Punkte","Artikel","Position","Positionen",
    "Land","Länder","Ländern","Stadt","Städte","Region","Regionen","Ort","Orte",
    "Haus","Häuser","Gebäude","Büro","Büros","Raum","Räume","Zimmer",
    "Telefon","Tel","Fax","Mail","Brief","Briefe","Nachricht","Nachrichten",
    "Name","Namen","Titel","Bezeichnung","Begriff","Begriffe",
    "Art","Arten","Typ","Typen","Form","Formen","Weise","Weisen",
    "Wert","Werte","Betrag","Beträge","Summe","Summen","Menge","Mengen",
    "Herr","Frau","Herrn","Dame","Damen","Person","Personen","Mensch","Menschen",
    "Vorjahr","Vorjahre","Vorjahren","Quartal","Quartale","Halbjahr",
    "Anteil","Anteile","Antrag","Anträge","Vertrag","Verträge","Vereinbarung",
    "Recht","Rechte","Pflicht","Pflichten","Gesetz","Gesetze","Regel","Regeln",
    "Änderung","Änderungen","Anpassung","Anpassungen","Korrektur","Korrekturen",
}

# ============================================
# EINHEITEN-ÄQUIVALENZEN - DEAKTIVIERT
# Bei technischen Übersetzungen dürfen Einheiten NICHT konvertiert werden!
# °C muss °C bleiben, km muss km bleiben, kg muss kg bleiben
# Wenn Einheiten geändert wurden OHNE gültige Konvertierung, ist das ein FEHLER.
# Gültige Äquivalenzen: z.B. miles↔km, lbs↔kg, °F↔°C werden akzeptiert.
# ============================================
UNIT_EQUIVALENTS: Dict[str, set] = {
    # Länge
    'km': {'miles', 'mi'},
    'miles': {'km'}, 'mi': {'km'},
    'm': {'feet', 'ft', 'yard', 'yd'},
    'feet': {'m'}, 'ft': {'m'},
    'cm': {'inch', 'in'},
    'inch': {'cm'}, 'in': {'cm'},
    'mm': {'inch', 'in'},
    # Gewicht
    'kg': {'lbs', 'pounds', 'lb'},
    'lbs': {'kg'}, 'lb': {'kg'}, 'pounds': {'kg'},
    'g': {'oz', 'ounce', 'ounces'},
    'oz': {'g'}, 'ounce': {'g'}, 'ounces': {'g'},
    # Temperatur
    'celsius': {'fahrenheit'},
    'fahrenheit': {'celsius'},
    # Volumen
    'liter': {'gal', 'gallon', 'gallons'},
    'gal': {'liter'}, 'gallon': {'liter'}, 'gallons': {'liter'},
    # Fläche
    'ha': {'acres', 'acre'},
    'acres': {'ha'}, 'acre': {'ha'},
    'sqft': {'m'}, 'sq ft': {'m'},
    # Währungen (gleiche Währung, verschiedene Schreibweisen)
    'eur': {'euro', 'euros', '€'},
    'euro': {'eur', 'euros', '€'},
    'euros': {'eur', 'euro', '€'},
    '€': {'eur', 'euro', 'euros'},
    'usd': {'dollar', 'dollars', '$'},
    'dollar': {'usd', 'dollars', '$'},
    'dollars': {'usd', 'dollar', '$'},
    '$': {'usd', 'dollar', 'dollars'},
    'gbp': {'pound', 'pounds', '£'},
    'pound': {'gbp', 'pounds', '£'},
    'pounds': {'gbp', 'pound', '£'},
    '£': {'gbp', 'pound', 'pounds'},
}

def _strip_tags(text: str) -> str:
    return TAG_PATTERN.sub('', text or '')

def _load_phase2_config(path: str = 'checker_config.json') -> Dict[str, object]:
    try:
        p = Path(path)
        if not p.is_file():
            return {}
        data = json.loads(p.read_text(encoding='utf-8'))
        result = data.get('analysis', {}).get('phase2', {}) or {}
        return result
    except json.JSONDecodeError as e:
        _logger.warning("checker_config.json ist fehlerhaft (JSON): %s — Phase 2 läuft mit Defaults", e)
        return {}
    except Exception as e:
        _logger.warning("Phase 2 Config konnte nicht geladen werden: %s — nutze Defaults", e)
        return {}

# Erwartetes Zeichen-Laengenverhaeltnis Ziel/Quelle je Sprachrichtung. Sprachen
# komprimieren/expandieren unterschiedlich (Englisch ist kuerzer als Deutsch,
# Deutsch laenger als Englisch usw.) -> die Vollstaendigkeits-Schwellen werden
# sprachpaar-gerecht statt einer starren festen Zahl. Unbekanntes/gleiches
# Paar -> 1.0 (neutral, = bisheriges Verhalten).
_EXPECTED_LEN_RATIO: Dict[Tuple[str, str], float] = {
    ('de', 'en'): 0.90, ('en', 'de'): 1.15,
    ('de', 'fr'): 1.05, ('fr', 'de'): 0.92,
    ('en', 'fr'): 1.10, ('fr', 'en'): 0.90,
    ('en', 'es'): 1.15, ('es', 'en'): 0.88,
    ('de', 'es'): 1.05, ('es', 'de'): 1.00,
    ('fr', 'es'): 1.05, ('es', 'fr'): 0.95,
}


def expected_length_ratio(src_lang: str, tgt_lang: str) -> float:
    """Erwartetes Ziel/Quelle-Zeichenverhaeltnis fuer die Sprachrichtung (1.0 = neutral)."""
    s = (src_lang or '').strip().lower()[:2]
    t = (tgt_lang or '').strip().lower()[:2]
    if not s or not t or s == t:
        return 1.0
    return _EXPECTED_LEN_RATIO.get((s, t), 1.0)


def check_coverage_ratio(src: str, tgt: str, *, min_ratio: float = 0.5, max_ratio: float = 2.0,
                         min_src_len: int = 30, src_lang: str = '', tgt_lang: str = '') -> List[QAIssue]:
    """Prüft Vollständigkeit: Zieltext sollte ähnliche Länge wie Quelle haben.

    Erkennt:
      - Zu kurz (Auslassung/Omission): ratio < min_ratio
      - Zu lang (Hinzufügung/Addition): ratio > max_ratio
    """
    issues: List[QAIssue] = []
    src_plain = _strip_tags(src).strip()
    tgt_plain = _strip_tags(tgt).strip()
    if not src_plain or not tgt_plain:
        return issues
    if len(src_plain) < min_src_len:
        return issues
    
    ratio = len(tgt_plain) / max(1, len(src_plain))
    # Sprachpaar-gerecht: an der ERWARTETEN Laenge messen, nicht starr an der
    # Quelllaenge. coverage = 1.0 -> Ziel hat genau die fuer die Richtung
    # erwartete Laenge; < min_ratio -> deutlich zu kurz; > max_ratio -> zu lang.
    expected = expected_length_ratio(src_lang, tgt_lang)
    coverage = ratio / expected

    # Zu kurz → mögliche Auslassung
    if coverage < min_ratio:
        diff_chars = len(src_plain) - len(tgt_plain)
        issues.append(QAIssue(
            "COMPLETENESS_TOO_SHORT", "major", "completeness",
            f"Übersetzung zu kurz ({ratio:.0%} der Quelle, {diff_chars} Zeichen fehlen) – mögliche Auslassung",
            src, tgt, -1, {"ratio": round(ratio, 3), "missing_chars": diff_chars,
                           "expected_ratio": round(expected, 2), "coverage": round(coverage, 3)}
        ))

    # Zu lang → mögliche Hinzufügung
    elif coverage > max_ratio:
        diff_chars = len(tgt_plain) - len(src_plain)
        issues.append(QAIssue(
            "COMPLETENESS_TOO_LONG", "minor", "completeness",
            f"Übersetzung deutlich länger ({ratio:.0%} der Quelle, +{diff_chars} Zeichen) – prüfen",
            src, tgt, -1, {"ratio": round(ratio, 3), "extra_chars": diff_chars,
                           "expected_ratio": round(expected, 2), "coverage": round(coverage, 3)}
        ))
    
    # Zusätzlich: Wortanzahl vergleichen
    src_words = len(_WORD_COUNT_PATTERN.findall(src_plain))
    tgt_words = len(_WORD_COUNT_PATTERN.findall(tgt_plain))
    if src_words >= 5:
        word_ratio = tgt_words / max(1, src_words)
        if word_ratio < 0.4:
            issues.append(QAIssue(
                "COMPLETENESS_WORDS_MISSING", "major", "completeness", 
                f"Übersetzung hat nur {tgt_words} von {src_words} Wörtern ({word_ratio:.0%})",
                src, tgt, -1, {"src_words": src_words, "tgt_words": tgt_words}
            ))
    
    return issues

_KNOWN_FIRST_NAMES: set = {
    # Deutsche männliche Vornamen
    'hans', 'peter', 'michael', 'thomas', 'andreas', 'stefan', 'christian',
    'martin', 'markus', 'frank', 'klaus', 'wolfgang', 'jürgen', 'dieter',
    'helmut', 'werner', 'gerhard', 'heinz', 'manfred', 'ralf', 'uwe',
    'bernd', 'karl', 'ernst', 'walter', 'horst', 'günter', 'herbert',
    'alexander', 'matthias', 'daniel', 'tobias', 'florian', 'sebastian',
    'jan', 'tim', 'lukas', 'felix', 'maximilian', 'paul', 'leon', 'jonas',
    'johannes', 'philipp', 'niklas', 'moritz', 'simon', 'david', 'benjamin',
    'dominik', 'patrick', 'manuel', 'marcel', 'dennis', 'sascha', 'oliver',
    'friedrich', 'heinrich', 'rudolf', 'otto', 'franz', 'josef', 'georg',
    'rainer', 'norbert', 'detlef', 'holger', 'carsten', 'torsten', 'sven',
    # Deutsche weibliche Vornamen
    'maria', 'anna', 'sabine', 'monika', 'petra', 'ursula', 'elisabeth',
    'renate', 'helga', 'karin', 'brigitte', 'ingrid', 'erika', 'andrea',
    'claudia', 'susanne', 'barbara', 'gabriele', 'nicole', 'christine',
    'julia', 'sarah', 'laura', 'lisa', 'lena', 'emma', 'hannah', 'sophie',
    'katharina', 'stefanie', 'melanie', 'jennifer', 'jessica', 'sandra',
    'martina', 'birgit', 'heike', 'silke', 'anja', 'tanja', 'katrin',
    'angelika', 'margarete', 'hildegard', 'gertrud', 'irmgard', 'ilse',
    'eva', 'charlotte', 'elke', 'gisela', 'christa', 'doris', 'marion',
    # Englische Vornamen
    'john', 'james', 'william', 'david', 'robert', 'richard', 'charles',
    'joseph', 'edward', 'george', 'henry', 'samuel', 'benjamin', 'daniel',
    'matthew', 'christopher', 'anthony', 'mark', 'steven', 'andrew', 'brian',
    'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'susan', 'margaret',
    'dorothy', 'karen', 'nancy', 'betty', 'helen', 'donna',
    'emily', 'olivia', 'sophia', 'isabella', 'amelia',
    # Französische Vornamen
    'jean', 'pierre', 'marie', 'françois', 'jacques', 'michel', 'philippe',
    'andré', 'louis', 'nicolas', 'antoine', 'bernard', 'alain', 'claude',
    'anne', 'catherine', 'isabelle', 'nathalie', 'céline', 'valérie',
    # Spanische Vornamen
    'jose', 'juan', 'carlos', 'miguel', 'francisco', 'antonio',
    'pedro', 'luis', 'rafael', 'diego', 'pablo', 'fernando', 'alejandro',
    'carmen', 'lucia', 'elena', 'isabel', 'rosa', 'pilar', 'dolores',
    # Italienische Vornamen
    'giuseppe', 'marco', 'paolo', 'francesco', 'giovanni', 'luigi',
    'roberto', 'stefano', 'alessandro', 'lorenzo', 'luca', 'matteo',
    'giulia', 'francesca', 'chiara', 'valentina', 'alessandra', 'federica',
    # Polnische Vornamen
    'piotr', 'andrzej', 'krzysztof', 'stanislaw', 'tomasz', 'pawel',
    'marek', 'michal', 'adam', 'wojciech', 'zbigniew', 'jerzy', 'tadeusz',
    'katarzyna', 'malgorzata', 'agnieszka', 'ewa',
    # Russische Vornamen (transliteriert)
    'ivan', 'dmitri', 'sergei', 'alexei', 'andrei', 'mikhail', 'nikolai',
    'vladimir', 'viktor', 'boris', 'oleg', 'igor', 'yuri', 'maxim',
    'olga', 'natalia', 'tatiana', 'irina', 'svetlana', 'marina',
    'ekaterina', 'anastasia', 'yulia', 'oksana', 'larisa', 'galina',
    # Skandinavische Vornamen
    'erik', 'lars', 'anders', 'magnus', 'olaf', 'bjorn',
    'nils', 'per', 'johan', 'gustav', 'fredrik', 'henrik',
    'astrid', 'sigrid',
    # Niederländische Vornamen
    'pieter', 'hendrik', 'willem', 'cornelis', 'gerrit',
    'johanna', 'wilhelmina', 'cornelia', 'hendrika',
    # Türkische Vornamen
    'mehmet', 'mustafa', 'ahmet', 'ali', 'hasan', 'huseyin', 'ibrahim',
    'fatma', 'ayse', 'emine', 'hatice', 'zeynep', 'elif', 'merve',
    # Arabische Vornamen
    'mohamed', 'mohammed', 'ahmad', 'omar', 'hassan', 'hussein',
    'fatima', 'aisha', 'maryam', 'layla', 'nour', 'hana',
    # Asiatische Vornamen (häufige)
    'yuki', 'kenji', 'takeshi', 'hiroshi', 'akira', 'chen', 'wei',
    'ming', 'jin', 'kim', 'park', 'lee', 'wong', 'zhang',
}

_SURNAME_ENDINGS: tuple = (
    # Deutsch
    'mann', 'berg', 'stein', 'burg', 'dorf', 'feld', 'hof', 'bach',
    'meier', 'meyer', 'maier', 'mayer', 'müller', 'schmidt', 'schneider',
    'fischer', 'weber', 'bauer', 'wagner', 'becker', 'schulz', 'hoffmann',
    'richter', 'klein', 'wolf', 'schröder', 'neumann', 'schwarz', 'braun',
    # Slawisch
    'owski', 'ewski', 'inski', 'enko', 'ski', 'ska', 'wicz', 'czyk',
    # Skandinavisch
    'sen', 'son', 'sson', 'dahl', 'lund', 'gren', 'qvist', 'strom',
    # Niederländisch/Flämisch
    'mans', 'kens', 'aert', 'eert',
)

_SURNAME_ENDINGS_STRONG: tuple = ('mann', 'berg', 'stein', 'meyer', 'müller', 'schmidt')

_NOT_FIRST_NAMES: frozenset = frozenset({
    # Artikel
    'die', 'der', 'das', 'eine', 'einer', 'einem', 'einen', 'ein',
    # Pronomen / Demonstrative
    'diese', 'dieser', 'dieses', 'diesem', 'diesen',
    'jede', 'jeder', 'jedes', 'jedem', 'jeden',
    'alle', 'aller', 'alles', 'allem', 'allen',
    'keine', 'keiner', 'keines', 'keinem', 'keinen', 'kein',
    'meine', 'seine', 'ihre', 'unsere', 'eure',
    'welche', 'welcher', 'welches', 'welchem', 'welchen',
    # Häufige Satzanfänge die keine Namen sind
    'neue', 'neuer', 'neues', 'neuem', 'neuen',
    'erste', 'erster', 'erstes', 'zweite', 'dritte',
    'weitere', 'weiterer', 'weiteres',
    'andere', 'anderer', 'anderes',
    'letzte', 'letzter', 'letztes',
    'nächste', 'nächster', 'nächstes',
    'gute', 'guter', 'gutes', 'große', 'großer', 'großes',
    'wichtige', 'wichtiger', 'wichtiges',
    # Englische Artikel / häufige Satzanfänge
    'the', 'this', 'that', 'these', 'those', 'each', 'every', 'some', 'any',
    'our', 'your', 'their', 'its', 'new', 'first', 'last', 'next', 'other',
})

# Kompilierte Company-Suffix-Patterns (einmalig, nicht pro Aufruf)
# Artikel die NICHT Teil eines Firmennamens sind
_COMPANY_NAME_STOP_WORDS = frozenset({
    'Die', 'Der', 'Das', 'Ein', 'Eine', 'Dem', 'Den', 'Des',
    'The', 'A', 'An', 'Laut', 'Mit', 'Bei', 'Von', 'Für', 'Und',
})

_COMPANY_SUFFIX_PATTERNS: dict = {
    suffix: re.compile(
        # Case-SENSITIV für den Firmenname-Teil (Großbuchstabe am Anfang jedes Worts)
        # Case-INSENSITIV nur für den Suffix-Match (GmbH, gmbh, GMBH)
        rf'\b([A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9&\-\.]+(?:\s+[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9&\-\.]+){{0,3}})\s+(?i:{re.escape(suffix)})\b',
    )
    for suffix in COMPANY_SUFFIXES_DNT
}


def _clean_company_name(raw_match: str) -> str:
    """Entfernt führende Artikel/Präpositionen vom extrahierten Firmennamen."""
    parts = raw_match.split()
    while parts and parts[0] in _COMPANY_NAME_STOP_WORDS:
        parts.pop(0)
    return ' '.join(parts) if parts else raw_match

# Cross-Language-Kognaten für check_untranslated_segments (module-level)
_CROSS_LANG_COGNATES: frozenset = frozenset({
    'information', 'system', 'software', 'computer', 'management', 'digital',
    'internet', 'online', 'server', 'data', 'design', 'team', 'marketing',
    'service', 'app', 'web', 'tool', 'cloud', 'standard', 'test', 'format',
    'projekt', 'project', 'expert', 'partner', 'global', 'international',
    'professional', 'professionell', 'hotel', 'restaurant', 'taxi', 'bus',
    'pdf', 'html', 'xml', 'json', 'api', 'url', 'http', 'https',
    'email', 'newsletter', 'download', 'upload', 'update', 'login',
    'feedback', 'content', 'media', 'video', 'audio', 'podcast',
    'status', 'forum', 'blog', 'post', 'link', 'code', 'plugin',
    'dashboard', 'widget', 'interface', 'database', 'backup',
})


def _extract_proper_names(src: str) -> Set[str]:
    """Extrahiert echte Eigennamen aus dem Text.

    Strategie: Nur echte Personennamen erkennen durch:
    1. Namen nach Titeln/Anreden (Dr., Prof., Herr, Frau, etc.)
    2. Bekannte Vornamen + Nachname Kombinationen
    3. Kontext-Erkennung (nach "sagt", "erklärt", "laut" etc.)
    4. Typische Nachnamen-Endungen als Verstärker

    NICHT erkannt (normale Substantive):
    - Großgeschriebene Wörter am Satzanfang ohne Kontext
    - Zwei beliebige großgeschriebene Wörter ohne Namens-Indikatoren
    """
    names: Set[str] = set()
    if not src:
        return names

    # Pattern 1: Titel + Name(n) - erweitert für mehrteilige Titel wie "Prof. Dr."
    # z.B. "Dr. Hans Weber", "Frau Müller", "Prof. Dr. Karl-Heinz Schmidt"
    _TITLE_ONLY = frozenset({'herr', 'frau', 'dr', 'dr.', 'prof', 'prof.', 'herr dr', 'herr dr.', 'frau dr', 'frau dr.', 'mr', 'mr.', 'mrs', 'mrs.', 'ms', 'ms.'})
    for m in _TITLE_NAME_PATTERN.finditer(src):
        full_name = m.group(0).strip()
        # Nur hinzufügen wenn mindestens ein richtiger Name dabei ist (nicht nur Titel)
        if full_name.lower().rstrip('.') not in _TITLE_ONLY:
            names.add(full_name)
    
    # Pattern 2: Kontext + Name (Name nach Funktionsbezeichnung oder Redeeinleitung)
    # z.B. "Geschäftsführer Hans Weber", "sagt Maria Schmidt"
    for pattern in _CONTEXT_BEFORE_NAME_PATTERNS:
        for m in pattern.finditer(src):
            # Nur den Namen-Teil extrahieren, nicht den Kontext
            first = m.group(1)
            second = m.group(2)
            if second:
                name = f"{first} {second}"
            else:
                name = first
            # Prüfe ob es wie ein Name aussieht
            if first[0].isupper() and (not second or second[0].isupper()):
                names.add(name)
    
    # Pattern 3: Bekannter Vorname + Nachname
    # z.B. "Hans Weber", "Maria Schmidt"
    # Artikel und häufige Nicht-Vornamen ausschließen
    for m in _NAME_PAIR_PATTERN.finditer(src):
        first_word = m.group(1)
        second_word = m.group(2)
        full_name = m.group(0).strip()

        # Artikel ausschließen
        if first_word.lower() in _NOT_FIRST_NAMES:
            continue

        is_name = False

        # Check 1: Bekannter Vorname
        if first_word.lower() in _KNOWN_FIRST_NAMES:
            is_name = True

        # Check 2: Nachname hat typische Endung (verstärkt Vertrauen)
        if any(second_word.lower().endswith(end) for end in _SURNAME_ENDINGS):
            if first_word.lower() in _KNOWN_FIRST_NAMES:
                is_name = True
            elif any(second_word.lower().endswith(end) for end in _SURNAME_ENDINGS_STRONG):
                is_name = True

        # Check 3: Nicht am Satzanfang (zusätzliche Sicherheit)
        if is_name:
            pos = m.start()
            if pos > 0:
                before = src[:pos].rstrip()
                if before and before[-1] in '.!?:' and first_word.lower() not in _KNOWN_FIRST_NAMES:
                    is_name = False

        if is_name:
            names.add(full_name)

    # Pattern 4: Dreiteilige Namen (Vorname Zweitname Nachname oder Doppelname)
    for m in _NAME_TRIPLE_PATTERN.finditer(src):
        first = m.group(1)
        if first.lower() in _KNOWN_FIRST_NAMES:
            names.add(m.group(0).strip())
    
    return names

def _extract_company_names(text: str) -> Set[str]:
    """Extrahiert Firmenbezeichnungen wie 'Müller GmbH', 'Schmidt AG' etc."""
    companies: Set[str] = set()
    if not text:
        return companies

    # Nutze vorcompilierte Patterns (kein re.compile() pro Aufruf)
    for suffix, pattern in _COMPANY_SUFFIX_PATTERNS.items():
        for m in pattern.finditer(text):
            raw = m.group(0).strip()
            cleaned = _clean_company_name(raw)
            companies.add(cleaned)

    # Auch einzelne Rechtsformen erfassen (falls direkt ohne Namen)
    # Wortgrenzen-Check: "AG" in "AGB" ist kein Treffer
    for suffix in COMPANY_SUFFIXES_DNT:
        import re as _re_sfx
        if _re_sfx.search(rf'\b{_re_sfx.escape(suffix)}\b', text):
            companies.add(suffix)

    return companies

def check_proper_names(src: str, tgt: str, glossary: Dict[str, List[str]], *, whitelist: Set[str], dnt: Set[str]) -> List[QAIssue]:
    """Prüft Eigennamen, Firmennamen und Akronyme zwischen Source und Target.
    
    Erkennt:
      - Fehlende Namen im Ziel (PROPER_NAME_MISSING)
      - Firmenbezeichnungen falsch übersetzt (COMPANY_NAME_TRANSLATED) 
      - Neue Namen im Ziel die nicht in Quelle sind (PROPER_NAME_ADDED)
    """
    issues: List[QAIssue] = []
    if not src or not tgt:
        return issues
    
    src_plain = _strip_tags(src)
    tgt_plain = _strip_tags(tgt)
    
    # ============================================
    # 1. FIRMENBEZEICHNUNGEN - MÜSSEN EXAKT BLEIBEN
    # ============================================
    src_companies = _extract_company_names(src_plain)
    
    # VERBESSERUNG: Deduplizierung - sortiere nach Länge (längste zuerst)
    # So wird "Die Müller GmbH" vor "GmbH" geprüft
    companies_by_length = sorted(src_companies, key=len, reverse=True)
    reported_companies: Set[str] = set()  # Track bereits gemeldete
    
    for company in companies_by_length:
        # Skip wenn dieser Name Teil eines bereits gemeldeten längeren Namens ist
        if any(company in reported and company != reported for reported in reported_companies):
            continue
            
        # Prüfe ob EXAKT im Target vorhanden
        if company not in tgt_plain:
            # Prüfe auch case-insensitive
            if company.lower() not in tgt_plain.lower():
                issues.append(QAIssue(
                    "COMPANY_NAME_MISSING", "critical", "terminology",
                    f"Firmenname fehlt/verändert: '{company}' muss exakt übernommen werden",
                    src, tgt, -1, {"company": company}
                ))
                reported_companies.add(company)
            else:
                # Groß/Kleinschreibung falsch
                issues.append(QAIssue(
                    "COMPANY_NAME_CASE", "major", "terminology",
                    f"Firmenname Schreibweise falsch: '{company}' (Groß-/Kleinschreibung prüfen)",
                    src, tgt, -1, {"company": company}
                ))
                reported_companies.add(company)
    
    # Prüfe Rechtsformen einzeln (GmbH, AG etc.) - diese sollten NICHT übersetzt werden
    # Dieser Check ist wichtig auch wenn Firmenname schon gemeldet - zeigt den GRUND des Fehlers
    for suffix in COMPANY_SUFFIXES_DNT:
        if suffix in src_plain:
            if suffix not in tgt_plain:
                # Wurde die Rechtsform übersetzt? (GmbH -> Ltd ist ein Fehler!)
                wrong_translations = {
                    'GmbH': ['Ltd', 'LLC', 'Limited', 'Inc'],
                    'AG': ['Corp', 'Corporation', 'PLC', 'Inc'],
                    'KG': ['LP', 'Limited Partnership'],
                    'e.V.': ['association', 'registered association'],
                }
                translated_to = None
                for wrong in wrong_translations.get(suffix, []):
                    if wrong in tgt_plain or wrong.lower() in tgt_plain.lower():
                        translated_to = wrong
                        break
                
                if translated_to:
                    # Dieser Fehler ist immer wichtig - zeigt den konkreten Übersetzungsfehler
                    issues.append(QAIssue(
                        "COMPANY_SUFFIX_TRANSLATED", "critical", "terminology",
                        f"Rechtsform '{suffix}' wurde fälschlich zu '{translated_to}' übersetzt. Deutsche Rechtsformen bleiben unübersetzt!",
                        src, tgt, -1, {"original": suffix, "translated": translated_to}
                    ))
                # Keine separate SUFFIX_MISSING Meldung - redundant wenn Firmenname fehlt
    
    # ============================================
    # 2. EIGENNAMEN (Personen, Orte etc.)
    # ============================================
    # VERBESSERT: Entferne Firmenbereiche aus dem Text BEVOR Namen extrahiert werden
    src_plain_no_companies = src_plain
    for company in src_companies:
        src_plain_no_companies = src_plain_no_companies.replace(company, '')
    
    src_names = _extract_proper_names(src_plain_no_companies)
    tgt_names = _extract_proper_names(tgt)
    
    # Zusätzlich: Entferne vollständige Firmenmatches (nicht einzelne Wörter!)
    for company in src_companies:
        src_names.discard(company)
    
    if not src_names and not tgt_names:
        return issues
    
    # Glossar erlaubte Varianten map
    gloss_map: Dict[str, List[str]] = {k.lower(): [v.lower() for v in vals] for k, vals in glossary.items()}
    
    # VERBESSERUNG: Dedupliziere überlappende Namen
    # Wenn "Dr. Hans Weber" und "Hans Weber" beide erkannt werden, behalte nur den längeren
    def _dedupe_names(names: Set[str]) -> Set[str]:
        sorted_names = sorted(names, key=len, reverse=True)
        result: Set[str] = set()
        for name in sorted_names:
            # Prüfe ob dieser Name Teil eines bereits hinzugefügten längeren Namens ist
            if not any(name in longer and name != longer for longer in result):
                result.add(name)
        return result
    
    src_names = _dedupe_names(src_names)
    tgt_names = _dedupe_names(tgt_names)
    
    # VERBESSERUNG: Hilfsfunktion für Namens-Varianten-Matching
    def _is_name_variant(name_a: str, name_b: str) -> bool:
        """Prüft ob name_a und name_b Varianten desselben Namens sind (bidirektional).

        Akzeptiert:
        - "Dr. Weber" ↔ "Dr. Hans Weber"
        - "Weber" ↔ "Hans Weber" (Nachname allein)
        - "Hans Weber" ↔ "Dr. Hans Weber" (Titel hinzugefügt)
        """
        def _one_direction(full_parts, short_parts):
            if not full_parts or not short_parts:
                return False
            # Exakt gleich
            if full_parts == short_parts:
                return True
            # Nachname-Match: "Weber" allein
            if len(short_parts) == 1:
                return short_parts[0] in full_parts
            # Titel-Match: Erstes + Letztes Wort gleich ("Dr. Weber" ↔ "Dr. Hans Weber")
            if len(full_parts) >= 2 and len(short_parts) >= 2:
                if full_parts[0] == short_parts[0] and full_parts[-1] == short_parts[-1]:
                    return True
                # Nachnamen gleich (letztes Wort)
                if full_parts[-1] == short_parts[-1]:
                    return True
            return False

        parts_a = name_a.split()
        parts_b = name_b.split()
        # Prüfe in beide Richtungen (längerer als "full", kürzerer als "short")
        if len(parts_a) >= len(parts_b):
            return _one_direction(parts_a, parts_b)
        else:
            return _one_direction(parts_b, parts_a)
    
    # Prüfe: Namen aus Source fehlen im Target?
    missing: List[str] = []
    tgt_lower = tgt_plain.lower()
    for name in src_names:
        if name in whitelist or name in DEFAULT_PROPER_WHITELIST:
            continue
        if name in COMPANY_SUFFIXES_DNT:
            continue  # Bereits oben geprüft
        name_lower = name.lower()
        # Erlaubte Varianten aus Glossar
        allowed = gloss_map.get(name_lower, [])
        
        # Check 1: Exakt vorhanden
        if name in tgt_plain or name_lower in tgt_lower:
            continue
            
        # Check 2: Glossar-Varianten
        if any(a in tgt_lower for a in allowed):
            continue
        
        # Check 3: VERBESSERUNG - Ist eine Kurzform im Target?
        # z.B. "Dr. Hans Weber" -> "Dr. Weber" ist OK
        name_variant_found = False
        for tgt_name in tgt_names:
            if _is_name_variant(name, tgt_name):
                name_variant_found = True
                break
        if name_variant_found:
            continue
        
        missing.append(name)
    
    if missing:
        crit = [m for m in missing if m.lower() in {x.lower() for x in dnt}]
        sev = 'critical' if crit else 'major'
        issues.append(QAIssue(
            "PROPER_NAME_MISSING", sev, "terminology", 
            f"Eigennamen fehlen in Übersetzung: {missing}", 
            src, tgt, -1, {"missing": missing, "critical": crit}
        ))
    
    # 3. Prüfe: Neue Namen im Target die nicht in Source sind?
    src_lower = src_plain.lower()
    added: List[str] = []
    for name in tgt_names:
        if name in whitelist or name in DEFAULT_PROPER_WHITELIST:
            continue
        if name in COMPANY_SUFFIXES_DNT:
            continue
        name_lower = name.lower()
        
        # Ist der Name im Source vorhanden?
        if name in src_plain or name_lower in src_lower:
            continue
            
        # VERBESSERUNG: Ist es eine Variante eines Source-Namens?
        is_variant_of_source = False
        for src_name in src_names:
            if _is_name_variant(src_name, name):
                is_variant_of_source = True
                break
        if is_variant_of_source:
            continue
        
        # Prüfe ob es eine Glossar-Variante von einem Source-Namen ist
        is_glossar_variant = False
        for src_name in src_names:
            allowed = gloss_map.get(src_name.lower(), [])
            if name_lower in allowed or src_name.lower() in gloss_map.get(name_lower, []):
                is_glossar_variant = True
                break
        if is_glossar_variant:
            continue
            
        added.append(name)
    
    if added:
        # Neue Namen könnten OK sein (Transliteration, Lokalisierung)
        issues.append(QAIssue(
            "PROPER_NAME_ADDED", "minor", "terminology", 
            f"Neue Namen in Übersetzung (prüfen): {added}", 
            src, tgt, -1, {"added": added}
        ))
    
    return issues

def _normalize_number_token(token: str) -> str:
    """Normalisiert Zahlentoken - entfernt alle Tausendertrenner (. , Leerzeichen), 
    vereinheitlicht Dezimaltrennzeichen auf '.'.
    
    Beispiele:
    - 15.750.000 (DE Tausendertrenner) → 15750000
    - 15,750,000 (EN Tausendertrenner) → 15750000  
    - 15.750,00 (DE Dezimal) → 15750.00
    - 15,750.00 (EN Dezimal) → 15750.00
    """
    t = (token or "").strip().replace('\u00A0', '').replace(' ', '')
    if not t:
        return t
    t = t.strip('.,')
    if not t or not _DIGIT_PATTERN.search(t):
        return t

    # Fall 1: Enthält beide Zeichen (. und ,) - letztes ist Dezimaltrennzeichen
    if '.' in t and ',' in t:
        last_dot = t.rfind('.')
        last_comma = t.rfind(',')
        if last_comma > last_dot:
            # Komma ist Dezimaltrennzeichen (DE: 15.750,00)
            int_part = _DOT_COMMA_STRIP.sub('', t[:last_comma])
            dec_part = t[last_comma+1:]
        else:
            # Punkt ist Dezimaltrennzeichen (EN: 15,750.00)
            int_part = _DOT_COMMA_STRIP.sub('', t[:last_dot])
            dec_part = t[last_dot+1:]
        return f"{int_part}.{dec_part}" if dec_part else int_part
    
    # Fall 2: Nur Kommas - könnten Tausendertrenner (EN) oder Dezimal (DE) sein
    if ',' in t and '.' not in t:
        parts = t.split(',')
        # Wenn alle Teile außer dem ersten 3 Ziffern haben → Tausendertrenner
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            return t.replace(',', '')  # Tausendertrenner entfernen
        # Sonst: letztes Komma ist Dezimaltrennzeichen
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            return f"{parts[0]}.{parts[1]}"
        # Ansonsten alle Kommas entfernen
        return t.replace(',', '')
    
    # Fall 3: Nur Punkte - könnten Tausendertrenner (DE) oder Dezimal (EN) sein
    if '.' in t and ',' not in t:
        parts = t.split('.')
        # Wenn alle Teile außer dem ersten 3 Ziffern haben → Tausendertrenner
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            return t.replace('.', '')  # Tausendertrenner entfernen
        # Ein Punkt mit 1-2 Ziffern danach → Dezimaltrennzeichen
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            return t  # Bereits im richtigen Format
        # Mehrere Punkte → Tausendertrenner
        if len(parts) > 2:
            return t.replace('.', '')
        # Ein Punkt mit 3 Ziffern → Tausendertrenner (z.B. 1.000)
        if len(parts) == 2 and len(parts[1]) == 3:
            return t.replace('.', '')
        return t
    
    return t

def _normalize_unit_token(u: str) -> str:
    """Normalisiert Einheiten für Vergleich (case-insensitive, Alias-Mapping)."""
    mapping = {
        # Währungen
        '€': 'eur', 'eur': 'eur', '$': 'usd', 'usd': 'usd', '£': 'gbp', 'gbp': 'gbp',
        # Millionen
        'mio.': 'mio', 'mio': 'mio',
        # Temperatur - alle auf Basisform normalisieren
        '°c': 'celsius', '° c': 'celsius', 'celsius': 'celsius', 'c': 'celsius',
        '°f': 'fahrenheit', '° f': 'fahrenheit', 'fahrenheit': 'fahrenheit', 'f': 'fahrenheit',
        # Länge
        'km': 'km', 'kilometer': 'km',
        'mi': 'miles', 'mile': 'miles', 'miles': 'miles',
        'm': 'm', 'meter': 'm', 'metre': 'm',
        'ft': 'feet', 'feet': 'feet', 'foot': 'feet',
        'cm': 'cm', 'centimeter': 'cm',
        'in': 'inch', 'inch': 'inch', 'inches': 'inch',
        # Gewicht
        'kg': 'kg', 'kilogram': 'kg',
        'lb': 'lbs', 'lbs': 'lbs', 'pound': 'lbs', 'pounds': 'lbs',
        'g': 'g', 'gram': 'g', 'gramm': 'g',
        'oz': 'oz', 'ounce': 'oz', 'ounces': 'oz',
    }
    ul = u.lower().replace(' ', '')
    return mapping.get(ul, ul)

_GLOSSARY_HEADER_NAMES = frozenset({
    'quellbegriff', 'source', 'term', 'begriff', 'original', 'key',
    'source term', 'ausgangstext', 'source_term', 'quelle',
})


def _load_glossary(path: str = 'glossary_terms.json') -> Dict[str, List[str]]:
    """Lädt Glossar aus JSON oder CSV/TSV.

    JSON-Format: {"Quellbegriff": "Zielbegriff"} oder {"Quellbegriff": ["Variante1", "Variante2"]}
    CSV/TSV-Format: Erste Spalte = Quellbegriff, zweite Spalte = Zielbegriff (optional)
    """
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}

    # JSON versuchen
    if p.suffix.lower() == '.json':
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}
        if not isinstance(data, dict):
            _logger.warning('Glossar-JSON ist kein Dict: %s', p.name)
            return {}
        result: Dict[str, List[str]] = {}
        for k, v in data.items():
            if not isinstance(k, str) or len(k.strip()) < 2:
                continue
            if isinstance(v, str):
                translations = [v] if v.strip() else []
            elif isinstance(v, (list, tuple)):
                translations = [x for x in v if isinstance(x, str) and x.strip()]
            else:
                # None/Zahl/Dict – ignoriere diesen Eintrag, nicht das ganze Glossar
                continue
            result[k.strip().lower()] = translations if translations else [k.strip()]
        return result

    # Excel (.xlsx)
    if p.suffix.lower() == '.xlsx':
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
            result: Dict[str, List[str]] = {}
            ws = wb.active
            first_row = True
            for row in ws.iter_rows(values_only=True):
                cells = [str(c).strip() if c is not None else '' for c in row]
                if first_row:
                    first_row = False
                    if cells and cells[0].lower() in _GLOSSARY_HEADER_NAMES:
                        continue
                term = cells[0] if cells else ''
                if not term or len(term) < 2:
                    continue
                translations = [c for c in cells[1:] if c]
                result[term.lower()] = translations if translations else [term]
            wb.close()
            return result
        except ImportError:
            _logger.warning("openpyxl nicht installiert — Excel-Glossar kann nicht geladen werden")
            return {}
        except Exception:
            return {}

    # CSV/TSV — Auto-Detect Delimiter (Komma, Semikolon, Tab)
    try:
        import csv
        result: Dict[str, List[str]] = {}
        # Auto-detect: Lies erste Zeile und zähle Trennzeichen
        # encoding='utf-8-sig' entfernt automatisch UTF-8-BOM (Excel CSV-Export)
        with open(str(p), 'r', encoding='utf-8-sig', errors='ignore') as f:
            first_line = f.readline()
        if p.suffix.lower() == '.tsv' or first_line.count('\t') > first_line.count(','):
            delimiter = '\t'
        elif first_line.count(';') > first_line.count(','):
            delimiter = ';'  # Deutsche Excel-Exporte
        else:
            delimiter = ','
        with open(str(p), 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f, delimiter=delimiter)
            first_row = True
            for row in reader:
                if first_row:
                    first_row = False
                    if row and row[0].strip().lower() in _GLOSSARY_HEADER_NAMES:
                        continue
                if not row:
                    continue
                term = row[0].strip()
                if not term or len(term) < 2:
                    continue
                translations = [col.strip() for col in row[1:] if col.strip()]
                result[term.lower()] = translations if translations else [term]
        return result
    except Exception:
        return {}

def _tokenize_lower(text: str) -> List[str]:
    return _WORD_SIMPLE_PATTERN.findall(text.lower())

def _normalize_for_duplicate(src: str) -> str:
    s = (src or "").strip()
    s = TAG_PATTERN.sub("", s)
    s = s.strip('"‘’“”„‹›«»')
    s = _WS_PATTERN.sub(" ", s).strip()
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
                    # VERBESSERT: Bei Mismatch versuche das passende Tag zu finden
                    # statt blind zu poppen (verhindert Kaskaden-Fehler)
                    if stack[-1] == name_low:
                        stack.pop()  # Korrektes Match
                    elif name_low in stack:
                        # Tag ist irgendwo im Stack - zurückspulen bis dahin
                        mismatches.append(("MISMATCH", f"{stack[-1]}->{name_low}"))
                        while stack and stack[-1] != name_low:
                            stack.pop()
                        if stack:
                            stack.pop()
                    else:
                        # Tag gar nicht im Stack - nur melden, nicht poppen
                        mismatches.append(("MISMATCH", f"{stack[-1]}->{name_low}"))
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
            -1, {"details": mism_tgt, "hint": "Stack order prüfen (z. B. <b><i></i></b>)"}
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

def _text_contains_phrase(text: str, phrase: str) -> bool:
    """Prüft ob ein Mehrwort-Terminus im Text vorkommt (case-insensitive)."""
    text_norm = _WS_PATTERN.sub(' ', text.lower().strip())
    phrase_norm = _WS_PATTERN.sub(' ', phrase.lower().strip())
    return phrase_norm in text_norm

def check_terminology(src: str, tgt: str, glossary: Dict[str, List[str]], critical_terms: Optional[List[str]] = None) -> List[QAIssue]:
    """Prüft Terminologie.
    
    VERBESSERT: Unterstützt jetzt auch Mehrwort-Termini (z.B. "quality assurance").
    - Einwort-Termini: Token-Match (schnell)
    - Mehrwort-Termini: Phrase-Match auf normalisiertem Text
    """
    issues: List[QAIssue] = []
    if not glossary:
        return issues
    if critical_terms is None:
        critical_terms = []
    
    src_tokens = set(_tokenize_lower(src))
    tgt_tokens = set(_tokenize_lower(tgt))
    src_lower = src.lower()
    tgt_lower = tgt.lower()
    
    for raw_term, pref_list in glossary.items():
        # Defensive: Glossary-Keys auf lowercase normalisieren
        term = raw_term.lower() if isinstance(raw_term, str) else raw_term
        # Phrase-Match wenn Term Whitespace ODER Nicht-Wortzeichen (Bindestrich,
        # Slash, Punkt) enthaelt — _tokenize_lower wuerde sonst splitten.
        needs_phrase = bool(re.search(r'[^\w]', term))
        # Prüfe ob Term im Source vorkommt
        term_in_src = False
        if needs_phrase:
            term_in_src = _text_contains_phrase(src, term)
        else:
            # Einwort-Terminus: Token-Match (schneller)
            term_in_src = term in src_tokens

        if term_in_src:
            # Prüfe ob bevorzugte Übersetzung im Target vorkommt
            preferred_found = False
            for pref in pref_list:
                pref_lower = pref.lower()
                if re.search(r'[^\w]', pref_lower):
                    if _text_contains_phrase(tgt, pref):
                        preferred_found = True
                        break
                else:
                    # Einwort-Präferenz: Token-Match
                    if pref_lower in tgt_tokens:
                        preferred_found = True
                        break
            
            if not preferred_found:
                crit_lc = [c.lower() for c in critical_terms if isinstance(c, str)]
                sev = "critical" if term in crit_lc else "major"
                issues.append(QAIssue("TERM_PREFERRED_MISSING", sev, "terminology", 
                                      f"Bevorzugter Terminus fehlt für '{term}': erwartet {pref_list}", 
                                      src, tgt, -1, {"term": term, "preferred": pref_list}))
    return issues

def check_duplicate_translation_consistency(pairs: Iterable[Tuple[str,str]]) -> List[QAIssue]:
    """Prüft ob identische Quellsegmente konsistent übersetzt wurden."""
    issues: List[QAIssue] = []
    # Speichere: norm_src -> (norm_tgt, original_index)
    mapping: Dict[str, Tuple[str, int]] = {}
    for idx, (src, tgt) in enumerate(pairs):
        norm_src = _normalize_for_duplicate(src)
        if not norm_src:
            continue
        prev = mapping.get(norm_src)
        norm_tgt = _normalize_for_duplicate(tgt)
        if prev is None:
            mapping[norm_src] = (norm_tgt, idx)
        else:
            prev_tgt, _ = prev  # Wir haben jetzt den ersten Index, aber melden den aktuellen
            if prev_tgt != norm_tgt:
                # 🔧 FIX: segment_index als 7. Parameter hinzufügen
                issues.append(QAIssue("DUPLICATE_INCONSISTENT", "critical", "consistency", f"Uneinheitliche Übersetzung für '{src[:30]}...' => '{prev_tgt}' vs. '{norm_tgt}'", src, tgt, idx, {"first": prev_tgt, "second": norm_tgt}))
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
        # Im Deutschen werden Nomen großgeschrieben — kein Fehler bei DE-Zielsprache
        # target_lang wird vom Aufrufer übergeben (default: 'de')
        pass  # Check deaktiviert für DE — deutsche Nomen-Großschreibung ist korrekt
    return issues

def check_numbers_units(src: str, tgt: str) -> List[QAIssue]:
    issues: List[QAIssue] = []
    
    # ============================================
    # VERBESSERTE ZAHLEN-EXTRAKTION
    # Ignoriert: Aufzählungen (1), a), §1, Datumsbestandteile
    # ============================================
    def _extract_significant_numbers(text: str) -> List[str]:
        """Extrahiert nur relevante Zahlen (keine Aufzählungen/Einzelziffern)."""
        # Entferne Aufzählungsmarker wie (1), 1), a), b), §1 etc.
        text_clean = _ENUM_MARKER_A.sub('', text)            # (a), (1)
        text_clean = _ENUM_MARKER_B.sub('', text_clean)       # a), b)
        text_clean = _ENUM_MARKER_C.sub('', text_clean)       # 1), 2) am Anfang
        text_clean = _ENUM_SECTION_SYM.sub('', text_clean)    # §1, § 12
        text_clean = _ENUM_NR_PATTERN.sub('', text_clean)     # Nr. 123
        text_clean = _ENUM_NUMMER_PAT.sub('', text_clean)     # Nummer 123

        # Entferne vollständige Datumsangaben (werden separat geprüft)
        # WICHTIG: Längere/spezifischere Patterns zuerst!
        text_clean = _DATE_ISO_REMOVE.sub('', text_clean)     # 1965-06-16, 1965/06/16 (ISO)
        text_clean = _DATE_EU_REMOVE.sub('', text_clean)      # 16.06.1965, 16/06/1965, 16-06-1965
        text_clean = _DATE_WORD_REMOVE.sub('', text_clean)    # March 24, 2026 / 24. März 2026

        # Entferne Zeitangaben
        text_clean = _TIME_REMOVE.sub('', text_clean)         # 14:30, 2:30 PM
        text_clean = _OCLOCK_REMOVE.sub('', text_clean)       # 14 Uhr, 2 o'clock

        # Entferne Versionsnummern (v1.2.3, Version 2.0)
        text_clean = _VERSION_REMOVE.sub('', text_clean)      # v1.2.3, Version 2.0.1

        # Entferne Telefonnummern (verschiedene Formate)
        text_clean = _PHONE_REMOVE.sub('', text_clean)        # +49 89 12345
        
        # Finde alle Zahlen
        raw_numbers = NUMBER_PATTERN.findall(text_clean)
        
        # Filtere: nur Zahlen mit ≥2 Ziffern ODER Dezimalzahlen/Geldbeträge behalten
        significant = []
        for num in raw_numbers:
            # Anzahl der Ziffern (ohne Trennzeichen)
            digits_only = _DIGITS_SPACES_PATTERN.sub('', num)
            
            # Ignoriere einstellige Zahlen komplett
            if len(digits_only) < 2:
                continue
            
            # Ignoriere zweistellige Zahlen NUR wenn sie in einem Datumskontext stehen
            # (z.B. "15.03.2025" oder "am 23. Januar") — nicht generell alle 1-31
            if len(digits_only) == 2:
                try:
                    val = int(digits_only)
                    if 1 <= val <= 31:
                        # Prüfe ob Datumskontext (Punkt/Slash danach oder davor)
                        idx = text.find(num)
                        if idx >= 0:
                            after = text[idx+len(num):idx+len(num)+2] if idx+len(num) < len(text) else ''
                            before = text[max(0,idx-2):idx]
                            if '.' in after or '/' in after or '-' in after or '.' in before or '/' in before:
                                continue  # Tatsächlicher Datumsteil
                            # Sonst: behalten (z.B. "15 Mitarbeiter")
                except ValueError:
                    pass
            
            significant.append(num)
        
        return significant
    
    def _extract_numbers_with_units(text: str) -> List[tuple]:
        """Extrahiert Zahlen MIT ihren Einheiten als Tupel (zahl, einheit).
        Beruecksichtigt sowohl Einheit nach der Zahl (5 km, 100 €) als auch
        Waehrungssymbol vor der Zahl ($100, €50) — sonst wird eine
        Waehrungs-Konvertierung nicht erkannt und Zahlen werden als
        fehlend/zusaetzlich gemeldet.
        """
        pairs = []
        for m in UNIT_NEAR_NUMBER.finditer(text):
            pairs.append((m.group("num"), _normalize_unit_token(m.group("unit"))))
        for m in UNIT_BEFORE_NUMBER.finditer(text):
            pairs.append((m.group("num"), _normalize_unit_token(m.group("unit"))))
        return pairs
    
    # Zahlen extrahieren (nur signifikante)
    src_nums = Counter(_normalize_number_token(n) for n in _extract_significant_numbers(src))
    tgt_nums = Counter(_normalize_number_token(n) for n in _extract_significant_numbers(tgt))
    
    # Extrahiere Zahlen MIT Einheiten für Konvertierungs-Check
    src_with_units = _extract_numbers_with_units(src)
    tgt_with_units = _extract_numbers_with_units(tgt)
    
    # Prüfe ob Einheiten-Konvertierung stattfand
    def _has_unit_conversion(src_pairs: List[tuple], tgt_pairs: List[tuple]) -> bool:
        """Prüft ob eine bekannte Einheiten-Konvertierung stattfand."""
        for src_num, src_unit in src_pairs:
            src_unit_lower = src_unit.lower()
            equivalents = UNIT_EQUIVALENTS.get(src_unit_lower, set())
            for tgt_num, tgt_unit in tgt_pairs:
                if tgt_unit.lower() in equivalents:
                    return True
        return False
    
    has_conversion = _has_unit_conversion(src_with_units, tgt_with_units)
    
    # Vorhandensein statt Haeufigkeit vergleichen: Eine Zahl gilt nur dann als
    # fehlend, wenn sie im Ziel GAR NICHT vorkommt (und umgekehrt). Ein reiner
    # Anzahl-Vergleich (Counter) erzeugt False Positives, wenn der Quelltext
    # eine Zahl oefter wiederholt als die Uebersetzung — z.B. doppelte
    # Textbloecke oder zu einem Satz zusammengefasste Wiederholungen.
    missing = [n for n in src_nums if tgt_nums.get(n, 0) == 0]
    added   = [n for n in tgt_nums if src_nums.get(n, 0) == 0]
    
    # ============================================
    # INTELLIGENTE FILTERUNG
    # Bei Einheiten-Konvertierung: Zahlen dürfen sich ändern!
    # ============================================
    
    # Wenn eine bekannte Einheiten-Konvertierung erkannt wurde,
    # unterdrücke Zahlen-Warnungen für die konvertierten Werte
    if has_conversion:
        # Entferne Zahlen die mit konvertierbaren Einheiten verbunden sind
        src_unit_numbers = {_normalize_number_token(n) for n, u in src_with_units 
                           if u.lower() in UNIT_EQUIVALENTS}
        tgt_unit_numbers = {_normalize_number_token(n) for n, u in tgt_with_units 
                           if any(u.lower() in UNIT_EQUIVALENTS.get(su.lower(), set()) 
                                  for _, su in src_with_units)}
        
        missing = [n for n in missing if n not in src_unit_numbers]
        added = [n for n in added if n not in tgt_unit_numbers]
    
    # Wenn Source kaum Zahlen hat aber Target viele → wahrscheinlich OK (erweiterte Übersetzung)
    src_has_few = len(src_nums) <= 2
    tgt_has_many = len(added) > 5
    
    if missing:
        issues.append(QAIssue("NUMBER_MISSING", "major", "consistency", 
                              f"Zahlen fehlen im Ziel: {missing}", src, tgt))
    
    if added and not (src_has_few and tgt_has_many):
        # Normale Meldung nur wenn nicht "Quelle kurz, Ziel ausführlich"
        severity = "minor" if len(added) <= 3 else "major"
        issues.append(QAIssue("NUMBER_ADDED", severity, "consistency", 
                              f"Neue Zahlen im Ziel: {added}", src, tgt))
    elif added and src_has_few and tgt_has_many:
        # Hinweis statt Fehler: Ziel enthält mehr Details (hint_only für UI-Filter)
        issues.append(QAIssue("NUMBER_ADDED", "minor", "consistency", 
                              f"Ziel enthält zusätzliche Zahlen (prüfen ob korrekt): {len(added)} neue", src, tgt,
                              -1, {"hint_only": True, "added_count": len(added)}))
    # Einheiten nahe Zahlen
    def _units_near(text: str) -> Counter:
        units = []
        for m in UNIT_NEAR_NUMBER.finditer(text):
            units.append(_normalize_unit_token(m.group("unit")))
        for m in UNIT_BEFORE_NUMBER.finditer(text):
            units.append(_normalize_unit_token(m.group("unit")))
        return Counter(units)
    
    def _are_units_equivalent(src_unit: str, tgt_units: Counter) -> bool:
        """Prüft ob eine Quell-Einheit ein Äquivalent im Ziel hat (z.B. km→miles)."""
        src_lower = src_unit.lower()
        # Direkter Match
        if src_lower in tgt_units:
            return True
        # Äquivalenz-Match
        equivalents = UNIT_EQUIVALENTS.get(src_lower, set())
        for equiv in equivalents:
            if equiv.lower() in tgt_units:
                return True
        return False
    
    src_units = _units_near(src)
    tgt_units = _units_near(tgt)
    
    # Filtere: Einheiten mit bekannten Äquivalenzen sind OK
    unit_missing = []
    for u in src_units:
        if src_units[u] > tgt_units.get(u, 0):
            # Prüfe ob eine äquivalente Einheit im Ziel existiert
            if not _are_units_equivalent(u, tgt_units):
                unit_missing.append(u)
    
    unit_added = []
    for u in tgt_units:
        if tgt_units[u] > src_units.get(u, 0):
            # Prüfe ob diese Einheit ein Äquivalent einer Quell-Einheit ist
            is_equivalent = False
            for src_u in src_units:
                if _are_units_equivalent(src_u, Counter({u: 1})):
                    is_equivalent = True
                    break
            if not is_equivalent:
                unit_added.append(u)
    
    if unit_missing or unit_added:
        # Fehlende Einheiten sind ernster als neue (könnten Format-Unterschied sein)
        sev = "major" if unit_missing else "minor"
        issues.append(QAIssue("UNIT_DRIFT", sev, "consistency", f"Einheiten-Differenzen: fehlend={unit_missing} neu={unit_added}", src, tgt))
    return issues

def check_punctuation(src: str, tgt: str, config: Optional[Dict[str, Any]] = None) -> List[QAIssue]:
    """Prüft Interpunktion.
    
    VERBESSERT: QUOTE_PLAIN ist jetzt konfigurierbar (z.B. für UI/Code-Texte abschaltbar).
    Config-Keys:
      - check_smart_quotes: bool (Default: True) - Prüfung auf typografische Anführungszeichen
      - target_lang: str (Default: 'de') - Nur bei 'de' werden Smart Quotes erwartet
    """
    issues: List[QAIssue] = []
    cfg = config or {}
    check_smart_quotes = bool(cfg.get('check_smart_quotes', True))
    target_lang = str(cfg.get('target_lang', 'de'))[:2].lower()
    
    s = src.strip(); t = tgt.strip()
    if s and s[-1] in END_PUNCT and t and t[-1] not in END_PUNCT:
        issues.append(QAIssue("PUNCT_MISSING_END", "minor", "punctuation", "Satzendzeichen fehlt im Ziel", src, tgt))
    # Erkenne Typ-Mismatch (z.B. Frage -> Aussage), nicht nur fehlende Zeichen
    if s and t and s[-1] in END_PUNCT and t[-1] in END_PUNCT and s[-1] != t[-1]:
        # Spanisch '¿...?' / '¡...!' am Anfang als gleichwertig zulassen
        issues.append(QAIssue(
            "PUNCT_TYPE_MISMATCH", "major", "punctuation",
            f"Satzendzeichen-Typ unterschiedlich: Quelle endet auf '{s[-1]}', Ziel auf '{t[-1]}'",
            src, tgt))
    if DOUBLE_PUNCT_PATTERN.search(t):
        issues.append(QAIssue("PUNCT_DOUBLE", "minor", "punctuation", "Mehrfache Satzzeichen", src, tgt))
    
    # Quote-Prüfung nur wenn aktiviert UND Zielsprache Deutsch
    if check_smart_quotes and target_lang == 'de':
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
    def _find_handlers(html: str) -> Set[str]:
        """Extrahiert normalisierte Event-Handler Namen (ohne '=')."""
        handlers: Set[str] = set()
        for m in TAG_PATTERN.finditer(html):
            attrs = m.group(3) or ""
            for h in EVENT_HANDLER_ATTR_PATTERN.findall(attrs):
                # Normalisiere: "onclick=" → "onclick"
                handlers.add(h.lower().rstrip('=').strip())
        return handlers
    
    src_handlers = _find_handlers(src)
    tgt_handlers = _find_handlers(tgt)
    # VERBESSERT: Set-Diff statt nur Count - zeige welche NEU hinzukamen
    new_handlers = tgt_handlers - src_handlers
    if new_handlers:
        issues.append(QAIssue("SECURITY_EVENT_HANDLER", "critical", "security", 
                              f"Neue Event-Handler Attribute hinzugefügt: {sorted(new_handlers)}", 
                              src, tgt, -1, {"new_handlers": sorted(new_handlers), "all_target_handlers": sorted(tgt_handlers)}))
    if SCRIPT_TAG_PATTERN.search(tgt) and not SCRIPT_TAG_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_SCRIPT_TAG", "critical", "security", "Neues <script> Tag im Ziel", src, tgt))
    if DATA_URI_PATTERN.search(tgt) and not DATA_URI_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_DATA_URI", "critical", "security", "Neuer data:-URI im Ziel", src, tgt))
    if STYLE_ATTR_PATTERN.search(tgt) and not STYLE_ATTR_PATTERN.search(src):
        issues.append(QAIssue("SECURITY_INLINE_STYLE", "major", "security", "Neues inline style Attribut im Ziel", src, tgt))
    return issues

_UNTRANSLATED_PAIR_THRESHOLDS: Dict[str, float] = {
    'de-en': 0.85, 'en-de': 0.85,
    'de-fr': 0.82, 'fr-de': 0.82,
    'de-es': 0.82, 'es-de': 0.82,
    'de-it': 0.82, 'it-de': 0.82,
    'en-fr': 0.82, 'fr-en': 0.82,
    'en-es': 0.82, 'es-en': 0.82,
    'de-zh': 0.95, 'zh-de': 0.95,
    'de-ja': 0.95, 'ja-de': 0.95,
    'en-zh': 0.95, 'zh-en': 0.95,
    'en-ja': 0.95, 'ja-en': 0.95,
    'de-ru': 0.90, 'ru-de': 0.90,
    'en-ru': 0.90, 'ru-en': 0.90,
}


def check_untranslated_segments(
    src: str,
    tgt: str,
    threshold: float = 0.88,
    src_lang: str = '',
    tgt_lang: str = '',
) -> List[QAIssue]:
    """Erkennt Segmente die der Übersetzer vergessen hat zu übersetzen.

    Für Sprachpaare mit vielen Kognaten (z. B. DE↔EN, DE↔FR) wird eine
    niedrigere Ähnlichkeitsschwelle verwendet, um Falsch-Positive zu reduzieren.
    Für Sprachen mit anderer Schrift (DE↔ZH, DE↔JA) wird die Schwelle erhöht.

    VERBESSERT: Mehrere Heuristiken für Cross-Language-Erkennung:
    1. Exakte Gleichheit (nach Normalisierung)
    2. SequenceMatcher für gleiche Schrift (hohe Übereinstimmung = unübersetzt)
    3. Token-Overlap für unterschiedliche Sprachen (viele gemeinsame Wörter = verdächtig)
    4. Interpunktions-/Strukturvergleich als Verstärker
    """
    issues: List[QAIssue] = []
    if not src or not tgt:
        return issues

    # Sprachpaar-spezifische Schwelle bestimmen (Kognaten vs. andere Schrift)
    if src_lang or tgt_lang:
        pair_key = f'{src_lang[:2].lower()}-{tgt_lang[:2].lower()}'
        threshold = _UNTRANSLATED_PAIR_THRESHOLDS.get(pair_key, threshold)

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
    src_norm = _WS_PATTERN.sub(' ', src_clean).strip().lower()
    tgt_norm = _WS_PATTERN.sub(' ', tgt_clean).strip().lower()
    
    if not src_norm or not tgt_norm or len(src_norm) < 5:
        return issues

    # Wenn nach Normalisierung weniger als 20 Buchstaben übrig sind,
    # ist der Text hauptsächlich Zahlen/URLs/Sonderzeichen → kein sinnvoller Vergleich
    _alpha_count = sum(1 for c in src_norm if c.isalpha())
    if _alpha_count < 20:
        return issues

    # ============================================
    # Prüfung 1: Exakt gleicher Text = definitiv unübersetzt
    # ============================================
    if src_norm == tgt_norm and len(src_norm) > 10:
        issues.append(QAIssue("UNTRANSLATED_SEGMENT", "critical", "completeness",
                              "Segment ist identisch mit Ausgangstext",
                              src, tgt, -1, {"similarity": 1.0}))
        return issues
    
    # ============================================
    # Prüfung 2: Hohe SequenceMatcher-Ähnlichkeit
    # (funktioniert für gleiche Schrift, z.B. DE→EN)
    # ============================================
    from difflib import SequenceMatcher
    seq_ratio = SequenceMatcher(None, src_norm, tgt_norm).ratio()
    if seq_ratio > threshold:
        issues.append(QAIssue("UNTRANSLATED_SEGMENT", "critical", "completeness",
                              f"Segment scheint unübersetzt (Ähnlichkeit {seq_ratio*100:.0f}%)",
                              src, tgt, -1, {"similarity": round(seq_ratio, 3)}))
        return issues
    
    # ============================================
    # Prüfung 3: Token-Overlap (Cross-Language)
    # Viele geteilte Wörter = wahrscheinlich unübersetzt
    # Ignoriert kurze Wörter (<3 Zeichen) da die sprachübergreifend häufig sind
    # ============================================
    src_tokens = set(w for w in _WORD_SIMPLE_PATTERN.findall(src_norm) if len(w) >= 3)
    tgt_tokens = set(w for w in _WORD_SIMPLE_PATTERN.findall(tgt_norm) if len(w) >= 3)
    
    if src_tokens and tgt_tokens:
        common = src_tokens & tgt_tokens
        # Entferne bekannte sprachübergreifende Wörter (Kognaten, Fachbegriffe, Abkürzungen)
        common_significant = common - _CROSS_LANG_COGNATES
        # Zähle auch reine Zahlen/Kürzel nicht als Overlap
        common_significant = {w for w in common_significant if not w.isdigit() and len(w) > 2}
        
        min_tokens = min(len(src_tokens), len(tgt_tokens))
        overlap_ratio = len(common_significant) / min_tokens if min_tokens > 0 else 0
        
        # Nur flaggen wenn >70% der signifikanten Wörter identisch UND mind. 5 gemeinsame Wörter
        if overlap_ratio > 0.70 and len(common_significant) >= 5:
            issues.append(QAIssue("UNTRANSLATED_SEGMENT", "critical", "completeness",
                                  f"Segment scheint unübersetzt ({len(common_significant)} von {min_tokens} Wörtern identisch, {overlap_ratio*100:.0f}%)",
                                  src, tgt, -1, {"similarity": round(overlap_ratio, 3), "common_words": len(common_significant)}))
    
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
                             src, tgt, -1, {"src_len": len(src_content), "tgt_len": len(tgt_content)}))
    
    return issues

def check_punctuation_spacing(tgt: str, target_lang: str = 'de') -> List[QAIssue]:
    """Prüft korrekte Leerzeichen um Satzzeichen (sprachabhängig).
    
    Deutsch: kein Leerzeichen VOR :!?
    Französisch: Leerzeichen VOR :!? ist KORREKT
    """
    issues: List[QAIssue] = []
    target_lang = (target_lang or 'de').lower()[:2]
    
    # Französische Regeln sind umgekehrt!
    if target_lang == 'fr':
        # Im Französischen ist Leerzeichen vor :;!? korrekt - nur prüfen ob es FEHLT
        if _PUNCT_FR_MISSING_SPACE.search(tgt):
            issues.append(QAIssue("PUNCT_MISSING_SPACE_FR", "minor", "typography",
                                 "Fehlendes Leerzeichen vor :;!? (Französisch)", "", tgt))
    else:
        # Deutsche/Englische Regeln
        if _PUNCT_SPACE_BEFORE_EXCL_PATTERN.search(tgt):
            issues.append(QAIssue("PUNCT_SPACE_BEFORE", "minor", "typography",
                                 "Leerzeichen vor ! oder ? (nicht korrekt im Deutschen)", "", tgt))

        # Leerzeichen vor Doppelpunkt – Ausnahme: Zeitangaben und URLs
        if (_PUNCT_SPACE_BEFORE_COLON_PATTERN.search(tgt)
                and not _PUNCT_COLON_DIGIT_PATTERN.search(tgt)
                and not _PUNCT_HTTP_COLON_PATTERN.search(tgt)):
            issues.append(QAIssue("PUNCT_SPACE_BEFORE_COLON", "minor", "typography",
                                 "Leerzeichen vor : (meist falsch im Deutschen)", "", tgt))

    # Diese Regeln gelten für alle Sprachen:
    if _PUNCT_NO_SPACE_AFTER.search(tgt):
        issues.append(QAIssue("PUNCT_NO_SPACE_AFTER", "minor", "typography",
                             "Fehlendes Leerzeichen nach Satzzeichen", "", tgt))

    if _PUNCT_SPACE_BEFORE_COMMA.search(tgt):
        issues.append(QAIssue("PUNCT_SPACE_BEFORE_COMMA", "minor", "typography",
                             "Leerzeichen vor Komma (falsch)", "", tgt))

    if _PUNCT_NO_SPACE_AFTER_COMMA.search(tgt):
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


def check_locale_formats(src: str, tgt: str, config: Dict[str, Any]) -> List[QAIssue]:
    """Prüft Locale-spezifische Datumsformate.
    
    HINWEIS: Die Dezimalformat-Prüfung wurde entfernt, da sie bei Übersetzungen
    zwischen verschiedenen Locales (z.B. DE→EN) False Positives erzeugte.
    12,5 (DE) wird korrekt zu 12.5 (EN) übersetzt - das ist KEIN Fehler.
    12,5 (DE) wird korrekt zu 12.5 (EN) übersetzt - das ist KEIN Fehler.
    """
    issues: List[QAIssue] = []
    if not config:
        return issues
    # decimal_sep = str(config.get("decimal_separator", ","))  # Deaktiviert
    # thousand_sep = str(config.get("thousand_separator", "."))  # Deaktiviert
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
                -1, {"date_iso": iso, "expected": expected}
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
                -1, {"dates": disallowed_iso}
            ))

    # DEZIMALFORMAT-PRÜFUNG DEAKTIVIERT
    # Bei Übersetzungen ist die Formatanpassung an die Zielsprache korrekt:
    # - DE: 12,5 (Komma als Dezimaltrennzeichen)
    # - EN: 12.5 (Punkt als Dezimaltrennzeichen)
    # Die alte Prüfung erzeugte False Positives, weil sie das Quellformat im Ziel erwartete.
    
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
            -1, matches
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


def _compare_marker_sets(src_markers: List[Dict[str, Any]], tgt_markers: List[Dict[str, Any]], config: Dict[str, Any], src: str, tgt: str, segment_index: int = -1) -> List[QAIssue]:
    """Vergleicht Listenmarker zwischen Quelle und Ziel."""
    issues: List[QAIssue] = []
    if config.get("ignore_single_items", True) and max(len(src_markers), len(tgt_markers)) <= 1:
        return issues
    if config.get("require_matching_markers", True):
        if len(src_markers) != len(tgt_markers):
            # 🔧 FIX: segment_index hinzufügen
            issues.append(QAIssue("LIST_STRUCTURE_MISMATCH", "major", "structure", "Anzahl der Listenmarker unterscheidet sich", src, tgt, segment_index, {"source": src_markers, "target": tgt_markers}))
            return issues
        for sm, tm in zip(src_markers, tgt_markers):
            if sm.get("type") != tm.get("type"):
                issues.append(QAIssue("LIST_STRUCTURE_TYPE", "major", "structure", "Listentyp unterscheidet sich", src, tgt, segment_index, {"source": sm, "target": tm}))
            elif sm.get("type") == "ordered" and sm.get("value") != tm.get("value"):
                issues.append(QAIssue("LIST_STRUCTURE_ORDER", "major", "structure", "Listennummerierung weicht ab", src, tgt, segment_index, {"source": sm, "target": tm}))
            elif sm.get("type") == "bullet" and sm.get("value") != tm.get("value"):
                issues.append(QAIssue("LIST_STRUCTURE_BULLET", "minor", "structure", "Listenaufzählungszeichen unterscheiden sich", src, tgt, segment_index, {"source": sm, "target": tm}))
    return issues


def check_list_structure_context(entries: List[Dict[str, Any]], config: Dict[str, Any]) -> List[QAIssue]:
    issues: List[QAIssue] = []
    if not config or not config.get("enabled", True):
        return issues
    entry_map = {entry.get("index", idx): entry for idx, entry in enumerate(entries)}
    for idx, entry in enumerate(entries):
        segment_idx = entry.get("index", idx)  # 🔧 FIX: segment_index aus entry oder Iteration
        issues.extend(_compare_marker_sets(entry.get("source_markers", []), entry.get("target_markers", []), config, entry.get("source_text", ""), entry.get("target_text", ""), segment_idx))
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
                # 🔧 FIX: segment_index hinzufügen (current index)
                issues.append(QAIssue(
                    "LIST_SEQUENCE_BREAK",
                    "major",
                    "structure",
                    f"Listenfolge springt von {prev_value} auf {value}",
                    prev_entry.get("target_text", ""),
                    current_entry.get("target_text", ""),
                    idx,  # segment_index
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
    for idx, info in enumerate(pair_infos):
        if not isinstance(info, dict):
            continue
        # Segment-Index aus pair_info oder Iteration-Index verwenden
        segment_idx = info.get("index", idx)
        meta = info.get("meta")
        if required and (not isinstance(meta, dict)):
            missing = sorted(required)
            # 🔧 FIX: segment_index hinzufügen
            issues.append(QAIssue("METADATA_MISSING", "critical", "metadata", f"Metadaten fehlen ({missing})", info.get("source"), info.get("translation"), segment_idx, {"expected": missing}))
            continue
        if not isinstance(meta, dict):
            continue
        if required:
            missing = [key for key in required if key not in meta]
            if missing:
                # 🔧 FIX: segment_index hinzufügen
                issues.append(QAIssue("METADATA_FIELD_MISSING", "critical", "metadata", f"Pflichtattribute fehlen: {missing}", info.get("source"), info.get("translation"), segment_idx, {"missing": missing}))
        if allowed:
            unexpected = [key for key in meta.keys() if key not in allowed]
            if unexpected:
                # 🔧 FIX: segment_index hinzufügen
                issues.append(QAIssue("METADATA_ATTRIBUTE_FORBIDDEN", "major", "metadata", f"Unerwartete Attribute: {unexpected}", info.get("source"), info.get("translation"), segment_idx, {"attributes": unexpected}))
        for field, expected_values in protected.items():
            if field in meta and isinstance(expected_values, (list, tuple, set)) and expected_values:
                if meta[field] not in expected_values:
                    # 🔧 FIX: segment_index hinzufügen
                    issues.append(QAIssue("METADATA_PROTECTED_VALUE", "critical", "metadata", f"Unzulässiger Wert für {field}: {meta[field]}", info.get("source"), info.get("translation"), segment_idx, {"field": field, "expected": list(expected_values), "actual": meta[field]}))
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
            # 🔧 FIX: segment_index=-1 für globale Issues, die sich nicht auf ein einzelnes Segment beziehen
            issues.append(QAIssue("TERM_INCONSISTENT", "major", "terminology", f"Uneinheitliche bevorzugte Übersetzungen für '{term}': {sorted(variants)}", term, ', '.join(sorted(variants)), -1, {"variants": sorted(variants)}))
    return issues

# Glossar-Cache: path -> (mtime, glossary_dict)
_glossary_cache: dict = {}

def _load_glossary_cached(path: str):
    """Lädt Glossar mit mtime-Cache (vermeidet Disk-I/O bei wiederholter Analyse)."""
    if not path or not os.path.exists(path):
        return _load_glossary(path)
    mtime = os.path.getmtime(path)
    if path in _glossary_cache and _glossary_cache[path][0] == mtime:
        return _glossary_cache[path][1]
    result = _load_glossary(path)
    _glossary_cache[path] = (mtime, result)
    return result

def run_phase2_checks(
    pairs: Iterable[Tuple[str,str]],
    glossary_path: str = 'glossary_terms.json',
    *,
    config: Optional[Dict[str, Any]] = None,
    pair_infos: Optional[List[Dict[str, Any]]] = None
) -> List[QAIssue]:
    glossary = _load_glossary_cached(glossary_path) if glossary_path else {}
    phase2_cfg = _load_phase2_config()
    coverage_cfg = phase2_cfg.get('coverage', {}) if isinstance(phase2_cfg, dict) else {}
    names_cfg = phase2_cfg.get('names', {}) if isinstance(phase2_cfg, dict) else {}
    cov_enabled = bool(coverage_cfg.get('enabled', True))
    try:
        cov_min_ratio = float(coverage_cfg.get('min_ratio', 0.6))
    except (ValueError, TypeError):
        cov_min_ratio = 0.6
    try:
        cov_min_src_len = int(coverage_cfg.get('min_source_len', 40))
    except (ValueError, TypeError):
        cov_min_src_len = 40
    names_enabled = bool(names_cfg.get('enabled', True))
    whitelist = set(names_cfg.get('whitelist', []) or [])
    dnt = set(names_cfg.get('do_not_translate', []) or [])
    critical_terms = phase2_cfg.get('critical_terms', {})
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
    punctuation_cfg = validation_cfg.get('punctuation', {}) or {}
    if not isinstance(punctuation_cfg, dict):
        punctuation_cfg = {}
    locale_enabled = bool(locale_cfg.get('enabled', True)) if isinstance(locale_cfg, dict) else bool(locale_cfg)
    blacklist_enabled = bool(blacklist_cfg.get('enabled', True)) if isinstance(blacklist_cfg, dict) else bool(blacklist_cfg)
    list_enabled = bool(list_cfg.get('enabled', True)) if isinstance(list_cfg, dict) else bool(list_cfg)
    # VERBESSERT: target_lang aus Config (Default: 'de')
    target_lang = str(punctuation_cfg.get('target_lang', locale_cfg.get('target_lang', 'de')))
    # Sprachcodes für Falsch-Positiv-Schwelle bei unübersetzten Segmenten
    src_lang_code = str(validation_cfg.get('src_lang', '') or '')
    tgt_lang_code = str(validation_cfg.get('tgt_lang', '') or '')

    all_pairs = list(pairs)
    issues: List[QAIssue] = []
    list_entries: List[Dict[str, Any]] = []
    
    def _add_issues_with_index(new_issues: List[QAIssue], segment_idx: int) -> None:
        """Fügt Issues hinzu und setzt dabei den segment_index."""
        for issue in new_issues:
            if issue.segment_index == -1:  # Nur setzen wenn nicht bereits gesetzt
                issue.segment_index = segment_idx
            issues.append(issue)
    
    for idx, (src, tgt) in enumerate(all_pairs):
        _add_issues_with_index(check_untranslated_segments(src, tgt, src_lang=src_lang_code, tgt_lang=tgt_lang_code), idx)
        _add_issues_with_index(check_empty_translation(src, tgt), idx)
        _add_issues_with_index(check_html_tags(src, tgt), idx)
        _add_issues_with_index(check_pronoun_consistency(tgt), idx)
        _add_issues_with_index(check_terminology(src, tgt, glossary, critical_terms), idx)
        _add_issues_with_index(check_punctuation(src, tgt, punctuation_cfg), idx)
        _add_issues_with_index(check_punctuation_spacing(tgt, target_lang=target_lang), idx)
        _add_issues_with_index(check_sentence_case(src, tgt), idx)
        _add_issues_with_index(check_numbers_units(src, tgt), idx)
        _add_issues_with_index(check_security(src, tgt), idx)
        if cov_enabled:
            _add_issues_with_index(check_coverage_ratio(src, tgt, min_ratio=cov_min_ratio, min_src_len=cov_min_src_len,
                                                        src_lang=src_lang_code, tgt_lang=tgt_lang_code), idx)
        if names_enabled:
            _add_issues_with_index(check_proper_names(src, tgt, glossary, whitelist=whitelist, dnt=dnt), idx)
        if locale_enabled:
            _add_issues_with_index(check_locale_formats(src, tgt, locale_cfg), idx)
        if blacklist_enabled:
            _add_issues_with_index(check_blacklist_terms(src, tgt, blacklist_cfg), idx)
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
        # 🔧 FIX: segment_index=-1 für globale Issues (dokumentweit)
        issues.append(QAIssue("PRONOUN_GLOBAL_INCONSISTENT", "major", "style", "Uneinheitliche Anrede (Du/Sie) über Dokument", "", "", -1))
    
    # ============================================
    # DEDUPLIZIERUNG: Entferne doppelte Fehler
    # VERBESSERT: Code + Message + Source/Target-Snippet = eindeutiger Schlüssel
    # So bleiben echte Fehler in verschiedenen Segmenten erhalten!
    # ============================================
    seen_keys: set = set()
    deduplicated: List[QAIssue] = []
    for issue in issues:
        # Erstelle einen eindeutigen Schlüssel pro Issue inkl. Segment-Kontext
        msg_normalized = (issue.message or "")[:60].lower().strip()
        src_snippet = _normalize_for_duplicate(issue.source_text or "")[:80]
        tgt_snippet = _normalize_for_duplicate(issue.target_text or "")[:80]
        key = (
            issue.code,
            msg_normalized,
            src_snippet,
            tgt_snippet,
        )
        if key not in seen_keys:
            seen_keys.add(key)
            deduplicated.append(issue)

    # Fix #5: Wenn globale Pronomen-Warnung existiert, lokale PRONOUN_MIX entfernen
    has_global_pronoun = any(i.code == 'PRONOUN_GLOBAL_INCONSISTENT' for i in deduplicated)
    if has_global_pronoun:
        deduplicated = [i for i in deduplicated if i.code != 'PRONOUN_MIX']

    return deduplicated

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
