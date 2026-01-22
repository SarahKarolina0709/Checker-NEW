"""Analysis Utility Helferfunktionen.

NICHT kritisch – ausgelagerte Logik aus quality_gui_main_app für bessere Testbarkeit.
Erweiterte, robuste Normalisierung & Fuzzy-Matching.

Änderungen (Upgrade):
 - normalize_number_token: zusätzliche Separatoren (\u202F, \u2009, \uFEFF), Klammer-Negativzahlen, konfigurierbare Dezimalstellenspanne,
     optionales Entfernen von Prozent & Währungssymbolen, sicherer Umgang mit Vorzeichen.
 - lev_dist_leq: optionaler Transpositions-Check (Damerau light) bei Distanz 1, konfigurierbare Max-Länge.
 - compute_dynamic_weights: Option keep_all_keys für stabile Schlüssel (inaktive => 0.0).
 - _selftest: Minimal-Assertions zur Schnellprüfung.
"""
from __future__ import annotations
import re
from functools import lru_cache
from typing import Dict, Tuple, Iterable

# ---------------- Zahlen-Normalisierung ---------------- #

def normalize_number_token(
    token: str,
    lang: str = 'de',
    *,
    allow_decimal_digits: Tuple[int, int] = (1, 9),
    strip_percent: bool = True,
    strip_currency: bool = True,
    remove_inner_currency: bool = False,
    currency_pattern: str | None = None,
    accept_scientific: bool = False,
) -> str:
    """Normalisiert Zahlentoken auf Punkt-Dezimalformat.

    Beispiele:
      '1.234,56'  (de) -> '1234.56'
      "(1 234,56)" (de) -> '-1234.56'
      "1,234.56" (en) -> '1234.56'
      "1'234.56" (en) -> '1234.56'

        Parameter:
            allow_decimal_digits: (min,max) erlaubte Ziffern nach Dezimaltrenner für Heuristik
            strip_percent: entfernt führende/trailing '%'
            strip_currency: entfernt einfache Währungssymbole an den Rändern
            remove_inner_currency: entfernt Währung auch innerhalb (z.B. "1.234€" -> "1.234")
            currency_pattern: optionaler Regex für zusätzliche Währungscodes (z.B. r'(?:CHF|PLN|zł|kr)')
            accept_scientific: akzeptiert wissenschaftliche Notation (1,23e-4) → 1.23e-4
    """
    if not token:
        return token
    raw = token.strip()
    # Negative in Klammern
    neg_paren = raw.startswith('(') and raw.endswith(')')
    if neg_paren:
        raw = raw[1:-1].strip()
    # Vorzeichen
    sign = ''
    if raw and raw[0] in '+-':
        sign, raw = raw[0], raw[1:]
    # Währungs-/Prozentzeichen nur an Rändern (erweitert)
    if strip_currency:
        # Multi-Char Codes explizit behandeln
        for code in ("CHF", "PLN", "zł", "kr"):
            if raw.startswith(code):
                raw = raw[len(code):].strip()
            if raw.endswith(code):
                raw = raw[:-len(code)].strip()
        # Einzelzeichen
        raw = raw.strip('€$£¥₽₩₹₿₫')
    if strip_percent:
        raw = raw.strip('%')
    if currency_pattern and strip_currency:
        # Nur an den Rändern – Regex-Anker ^|
        raw = re.sub(rf'^(?:{currency_pattern})+', '', raw).strip()
        raw = re.sub(rf'(?:{currency_pattern})+$', '', raw).strip()
    if remove_inner_currency and strip_currency:
        # Nur entfernen, wenn direkt an Ziffer angrenzend (verhindert Entfernen in Wörtern)
        inner_pat = currency_pattern or r'CHF|PLN|zł|kr|€|$|£|¥|₽|₩|₹|₿|₫'
        raw = re.sub(rf'(?<=\d)(?:{inner_pat})', '', raw)
        raw = re.sub(rf'(?:{inner_pat})(?=\d)', '', raw)
    # Separatoren vereinheitlichen
    raw = (raw
           .replace('\u00A0', ' ')  # NBSP
           .replace('\u202F', ' ')  # narrow NBSP
           .replace('\u2009', ' ')  # thin space
           .replace('\uFEFF', ' ')  # BOM
    )
    # Entferne Gruppentrenner (' und Spaces)
    raw_clean = raw.replace("'", '').replace(' ', '')
    # Wissenschaftliche Notation früh behandeln, falls gewünscht
    if accept_scientific and re.match(r'^[0-9]+([.,][0-9]+)?[eE][+-]?[0-9]+$', raw_clean):
        mantissa, exp = re.split(r'[eE]', raw_clean, 1)
        mantissa = mantissa.replace(',', '.')
        core = mantissa + 'e' + exp.lower()
        if neg_paren and not sign:
            sign = '-'
        return (sign + core) if sign else core
    # Kurzpfad
    if raw_clean.isdigit():
        core = raw_clean
    else:
        has_dot = '.' in raw_clean
        has_comma = ',' in raw_clean
        def _apply_decimal(last_sep: str, other_sep: str):
            nonlocal raw_clean
            last_idx = raw_clean.rfind(last_sep)
            left, right = raw_clean[:last_idx], raw_clean[last_idx+1:]
            mn, mx = allow_decimal_digits
            if right.isdigit() and mn <= len(right) <= mx:
                if other_sep:
                    left = left.replace(other_sep, '')
                raw_clean = left.replace(last_sep, '').replace(other_sep, '') + '.' + right
            else:
                raw_clean = raw_clean.replace(last_sep, '').replace(other_sep, '')
        # Idempotenz: Bereits kanonisch normalisierte Form (1234.56) bei de nicht erneut als Gruppentrennung interpretieren
        if has_dot and not has_comma and lang.startswith('de') and re.match(r'^\d+\.\d+$', raw_clean):
            # unverändert lassen
            pass
        elif has_dot and has_comma:
            if lang.startswith('de'):
                _apply_decimal(',', '.')
            else:
                _apply_decimal('.', ',')
        elif has_comma and not has_dot:
            # Einzelnes Komma: de -> Dezimaltrenner; en -> Gruppentrenner
            if lang.startswith('de'):
                _apply_decimal(',', '')
            else:
                raw_clean = raw_clean.replace(',', '')
        elif has_dot and not has_comma:
            # Einzelner Punkt: en -> Dezimaltrenner; de -> Gruppentrenner
            if lang.startswith('de'):
                raw_clean = raw_clean.replace('.', '')
            else:
                _apply_decimal('.', '')
        core = raw_clean
    # Clean erlaubte Zeichen
    core = re.sub(r'[^0-9\.-]', '', core)
    if core.count('.') > 1:
        first = core.find('.')
        core = core[:first+1] + core[first+1:].replace('.', '')
    # Abschließenden Dezimal-Punkt ohne Nachkommaziffern entfernen
    if core.endswith('.'):
        core = core[:-1]
    if core in ('', '.'):
        # Sichere Fallback – vermeide Doppel-Vorzeichen
        final_sign = '-' if (sign == '-' or neg_paren) else ('+' if sign == '+' else '')
        return final_sign + token
    # Endgültiges Vorzeichen bestimmen
    if neg_paren and not sign:
        sign = '-'
    return (sign + core) if sign else core

# ---------------- Fuzzy Distance (konfigurierbar) ---------------- #

@lru_cache(maxsize=4096)
def lev_dist_leq(a: str, b: str, max_d: int, allow_transpose: bool = False, max_token_len: int = 128) -> bool:
    """Prüft, ob Levenshtein-Distanz (optional mit einfacher Transposition) <= max_d.

    Parameter sind so gewählt, dass bestehende Aufrufe (a,b,max_d) unverändert funktionieren.
    """
    if a == b:
        return True
    if max_d <= 0:
        return False
    if len(a) > max_token_len or len(b) > max_token_len:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > max_d:
        return False
    if max_d == 1:
        if la == lb:
            # Früher Transpositions-Versuch (Damerau light)
            if allow_transpose and la >= 2:
                for i in range(la - 1):
                    if a[i] != b[i]:
                        if a[i] == b[i+1] and a[i+1] == b[i] and a[i+2:] == b[i+2:]:
                            return True  # reine Transposition
                        break  # kein Match -> normaler Distanzpfad
            diff = 0
            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    if diff > 1:
                        return False
            return True  # 0 oder 1 Unterschiede
        # Insert/Delete Fall
        if la < lb:
            a, b, la, lb = b, a, lb, la
        for i in range(la):
            if a[:i] + a[i+1:] == b:
                return True
        return False
    # Allgemeiner Band-Levenshtein
    if la < lb:
        a, b = b, a
        la, lb = lb, la
    prev = list(range(lb + 1))
    cur = [0] * (lb + 1)
    for i in range(1, la + 1):
        cur[0] = i
        start = max(1, i - max_d)
        end = min(lb, i + max_d)
        for j in range(1, start):
            cur[j] = max_d + 1
        for j in range(start, end + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        for j in range(end + 1, lb + 1):
            cur[j] = max_d + 1
        # Frühabbruch nur über aktives Band prüfen
        if min(cur[start:end+1]) > max_d:
            return False
        prev, cur = cur, prev
    return prev[lb] <= max_d

# ---------------- Gewichtungs-Helfer ---------------- #

def compute_dynamic_weights(
    base: Dict[str, float],
    availability: Dict[str, bool],
    *,
    keep_all_keys: bool = True,
    adjust_rounding_drift: bool = False
) -> Dict[str, float]:
    """Normalisiert Gewichte auf aktive Metriken.

    keep_all_keys=True liefert auch inaktive Keys mit 0.0 (stabile API).
    adjust_rounding_drift=True passt den größten aktiven Key minimal an, damit Summe exakt 1.0 (falls Drift < 1e-6).
    """
    active = {k: w for k, w in base.items() if availability.get(k, False) and w > 0}
    total = sum(active.values()) or 1.0
    scaled = {k: w / total for k, w in active.items()}
    if keep_all_keys:
        rounded = {k: round(scaled.get(k, 0.0), 6) for k in base.keys()}
    else:
        rounded = {k: round(v, 6) for k, v in scaled.items()}
    if adjust_rounding_drift and rounded:
        # Nur aktive Keys betrachten
        active_keys = [k for k, v in rounded.items() if v > 0]
        if active_keys:
            s = sum(rounded[k] for k in active_keys)
            drift = round(1.0 - s, 6)
            if abs(drift) <= 1e-6:
                # größten Key wählen
                largest = max(active_keys, key=lambda k: rounded[k])
                rounded[largest] = round(rounded[largest] + drift, 6)
    return rounded


def _selftest():  # schnelle interne Assertions (kein ausführliches Test-Framework nötig)
    assert normalize_number_token("1.234,56", "de") == "1234.56"
    assert normalize_number_token("1\u202F234,56", "de") == "1234.56"
    assert normalize_number_token("(1.234,56)", "de") == "-1234.56"
    assert normalize_number_token("1,234.56", "en") == "1234.56"
    assert normalize_number_token("1'234.56", "en") == "1234.56"
    assert normalize_number_token("-1 234", "de") == "-1234"
    # Einzel-Separator Heuristik
    assert normalize_number_token("12,345", "en") == "12345"  # Komma Gruppentrenner en
    assert normalize_number_token("12.345", "de") == "12345"  # Punkt Gruppentrenner de
    assert normalize_number_token("12,345", "de") == "12.345"  # Komma Dezimal de
    assert normalize_number_token("12.345", "en") == "12.345"  # Punkt Dezimal en
    x = normalize_number_token("1.234,56", "de"); assert normalize_number_token(x, "de") == x  # Idempotenz Check
    assert normalize_number_token("1,23456789", "de") == "1.23456789"
    assert normalize_number_token("1,23e-4", "de", accept_scientific=True) == "1.23e-4"
    # Inner Currency nur an Ziffern angrenzend entfernen
    assert normalize_number_token("123kr", "en", remove_inner_currency=True) == "123"
    assert normalize_number_token("kr123", "en", remove_inner_currency=True) == "123"
    assert normalize_number_token("Marke", "de", remove_inner_currency=True) == "Marke"
    assert lev_dist_leq("form", "from", 1, allow_transpose=True)
    w = compute_dynamic_weights({"a": 2, "b": 1, "c": 1}, {"a": True, "b": False, "c": True})
    assert abs(w["a"] - 0.666667) < 1e-6 and w["b"] == 0.0 and abs(w["c"] - 0.333333) < 1e-6


__all__ = [
    'normalize_number_token',
    'lev_dist_leq',
    'compute_dynamic_weights'
]
