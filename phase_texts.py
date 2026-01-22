"""Ausgelagerte Phase-Texte und Prüfpunkte (DE, i18n über app._t).

Konventionen:
- Nur Light-Mode Texte, keine Icons/Emojis.
- Kurz, prägnant, konsistent zum Welcome-Screen Wording.
- Greift auf app._t zu; fällt bei fehlendem app auf Rohstrings zurück.
"""
from __future__ import annotations
from typing import Any, List, Optional


def _t(app: Any, s: str) -> str:
    try:
        return app._t(s)
    except Exception:
        return s


def get_phase_explain(app: Any, label: str) -> Optional[str]:
    mapping = {
        'Phase 1': _t(app, 'Prüft Zahlen, Datumsangaben und Maßeinheiten auf Übereinstimmung zwischen Quelle und Ziel.'),
        'Phase 2': _t(app, 'Analysiert die Länge der Segmente (Zeichen) und erkennt untypische Abweichungen.'),
        'Phase 3': _t(app, 'Überprüft Vollständigkeit: Fehlen Teile oder bleiben Segmente unübersetzt?'),
        'Phase 4': _t(app, 'Konsolidiert vorherige Befunde und berechnet Risiko-Score.'),
        'Phase 5': _t(app, 'Durchsetzung & optionale Auto-Korrekturen (Regeln / Gates).'),
        'Phase 6': _t(app, 'Heuristische Verbesserungsvorschläge basierend auf aggregierten Issues.'),
    }
    return mapping.get(label)


def get_phase_points(app: Any, label: str) -> List[str]:
    if label == 'Phase 1':
        return [
            _t(app, 'Platzhalter: Anzahl, Reihenfolge, fehlende / zusätzliche'),
            _t(app, 'URLs & E-Mails: 1:1 Übernahme, keine neuen'),
            _t(app, 'Zahlen & Maße: identische Werte / Einheiten'),
            _t(app, 'Unsichtbare Zeichen & Whitespace bereinigen'),
            _t(app, 'Klammern / Anführungszeichen paarig & konsistent'),
        ]
    if label == 'Phase 2':
        return [
            _t(app, 'HTML Tags & Attribute: fehlend / zusätzlich / Reihenfolge'),
            _t(app, 'Terminologie: Glossar-Sollformen vorhanden'),
            _t(app, 'Zahlen / Einheiten Drift erkennen'),
            _t(app, 'Eigennamen & Wiederholungen konsistent'),
            _t(app, 'Sicherheitsmuster (script, event, data:, javascript:)'),
        ]
    if label == 'Phase 3':
        return [
            _t(app, 'Lange Sätze / Passivanteile bewerten'),
            _t(app, 'Lesbarkeit (LIX) & Satzstruktur prüfen'),
            _t(app, 'Semantische Ähnlichkeit Quelle ↔ Übersetzung'),
            _t(app, 'Risikoindikatoren (Domains, Base64, Inline-Stile)'),
            _t(app, 'Stil & Groß/Kleinschreibung vereinheitlichen'),
        ]
    if label == 'Phase 4':
        return [
            _t(app, 'Aggregation aller Issues'),
            _t(app, 'Risikobewertung / Score Berechnung'),
            _t(app, 'Schweregrad-Verteilung'),
            _t(app, 'Konsolidierung doppelter Muster'),
            _t(app, 'Priorisierte Korrekturreihenfolge'),
        ]
    if label == 'Phase 5':
        return [
            _t(app, 'Anwendbare Auto-Fixes (z.B. Whitespace, Quotes)'),
            _t(app, 'Gate-Bedingungen prüfen'),
            _t(app, 'Nicht behebbares Rest-Set markieren'),
            _t(app, 'Verbleibende Risiken hervorheben'),
            _t(app, 'Optionaler Abbruch bei Blockern'),
        ]
    if label == 'Phase 6':
        return [
            _t(app, 'Heuristische Quick-Fixes ableiten'),
            _t(app, 'Struktur-/Terminologie-Konsistenz stärken'),
            _t(app, 'Lesbarkeit & Stil verbessern'),
            _t(app, 'Risikoindikatoren reduzieren'),
            _t(app, 'Semantische Drift adressieren'),
        ]
    return []
