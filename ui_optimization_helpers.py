"""UI-Optimierungen für Analyse-Ergebnisse im Übersetzungs-Checker.

Verbessert die Darstellung für professionelle Übersetzer:
- Kategorie-Icons (ohne Emojis, nur Text)
- Lösungsvorschläge prominent
- Bessere Kontext-Anzeige
- Hilfetexte für Fehlertypen
"""
from typing import Dict, Any

# ============================================================================
# Kategorie-Definitionen mit Beschreibungen
# ============================================================================

CATEGORY_INFO = {
    'placeholders': {
        'label': 'Platzhalter',
        'prefix': '[PH]',
        'description': 'Fehlende, zusätzliche oder falsch angeordnete Platzhalter',
        'impact': 'KRITISCH - führt zu Laufzeitfehlern',
        'examples': '{name}, %s, {{var}}',
    },
    'references': {
        'label': 'Verweise',
        'prefix': '[REF]',
        'description': 'URLs, E-Mails und externe Referenzen',
        'impact': 'KRITISCH - Links funktionieren nicht',
        'examples': 'http://..., mailto:...',
    },
    'whitespace': {
        'label': 'Leerzeichen',
        'prefix': '[WS]',
        'description': 'Whitespace-Probleme und unsichtbare Zeichen',
        'impact': 'HOCH - zerstört UI-Layouts',
        'examples': 'Führende/nachgestellte Spaces, NBSP',
    },
    'structure': {
        'label': 'Struktur',
        'prefix': '[STR]',
        'description': 'Klammern, Tags und strukturelle Elemente',
        'impact': 'HOCH - Syntaxfehler möglich',
        'examples': '(), [], <tag>',
    },
    'quotes': {
        'label': 'Anführungszeichen',
        'prefix': '[QT]',
        'description': 'Balance und Typografie von Quotes',
        'impact': 'MITTEL - Parser-Fehler oder schlechte Lesbarkeit',
        'examples': '"..."  „..."',
    },
    'html': {
        'label': 'HTML',
        'prefix': '[HTML]',
        'description': 'HTML-Tags und Attribute',
        'impact': 'KRITISCH - Rendering-Fehler',
        'examples': '<b>, <div>, href="..."',
    },
    'style': {
        'label': 'Stil',
        'prefix': '[STY]',
        'description': 'Sprachstil und Anrede-Konsistenz',
        'impact': 'MITTEL - unprofessioneller Eindruck',
        'examples': 'Du/Sie-Mischung',
    },
    'terminology': {
        'label': 'Terminologie',
        'prefix': '[TERM]',
        'description': 'Glossarbegriffe und Eigennamen',
        'impact': 'HOCH - Inkonsistenz, falsche Begriffe',
        'examples': 'Firmen, Produkte, Fachbegriffe',
    },
    'punctuation': {
        'label': 'Satzzeichen',
        'prefix': '[PUNC]',
        'description': 'Interpunktion und Typografie',
        'impact': 'NIEDRIG - kosmetisch',
        'examples': '. ! ? , :',
    },
    'consistency': {
        'label': 'Konsistenz',
        'prefix': '[CONS]',
        'description': 'Zahlen, Einheiten, Duplikate',
        'impact': 'HOCH - Daten-Inkonsistenz',
        'examples': '1.234 vs 1,234',
    },
    'security': {
        'label': 'Sicherheit',
        'prefix': '[SEC]',
        'description': 'Sicherheitskritische Änderungen',
        'impact': 'KRITISCH - XSS, Injection-Risiko',
        'examples': 'javascript:, <script>, onclick=',
    },
    'completeness': {
        'label': 'Vollständigkeit',
        'prefix': '[COMP]',
        'description': 'Unübersetzte oder leere Segmente',
        'impact': 'KRITISCH - fehlt komplett',
        'examples': 'Copy-Paste-Fehler, leere Übersetzungen',
    },
    'formatting': {
        'label': 'Formatierung',
        'prefix': '[FMT]',
        'description': 'Soft-Hyphens und Steuerzeichen',
        'impact': 'HOCH - Word-Artefakte',
        'examples': 'Soft-Hyphen, NULL-Zeichen',
    },
    'typography': {
        'label': 'Typografie',
        'prefix': '[TYP]',
        'description': 'Leerzeichen um Satzzeichen',
        'impact': 'NIEDRIG - Lesbarkeit',
        'examples': 'Hallo !  vs  Hallo!',
    },
    'readability': {
        'label': 'Lesbarkeit',
        'prefix': '[READ]',
        'description': 'Satzlänge und Komplexität',
        'impact': 'NIEDRIG - Verständlichkeit',
        'examples': 'Zu lange Sätze, LIX-Index',
    },
    'risk': {
        'label': 'Risiko',
        'prefix': '[RISK]',
        'description': 'Neue Domains, verdächtige Inhalte',
        'impact': 'HOCH - Sicherheit/Qualität',
        'examples': 'Neue URLs, Base64-Blöcke',
    },
}

# ============================================================================
# Regel-spezifische Hilfetexte und Lösungen
# ============================================================================

RULE_HELP = {
    # Phase 1 - Format & Struktur
    'PLACEHOLDER_MISSING': {
        'help': 'Platzhalter aus der Quelle fehlen in der Übersetzung',
        'solution': 'Kopieren Sie alle Platzhalter exakt aus der Quelle',
        'example': 'EN: "Hello {name}" → DE: "Hallo {name}"',
    },
    'PLACEHOLDER_EXTRA': {
        'help': 'Zusätzliche Platzhalter, die nicht in der Quelle sind',
        'solution': 'Entfernen Sie die zusätzlichen Platzhalter',
        'example': 'Falsch: "Hallo {name} {extra}"',
    },
    'PLACEHOLDER_ORDER': {
        'help': 'Platzhalter in anderer Reihenfolge als in der Quelle',
        'solution': 'Bei nummerierten Platzhaltern (%1$s) Reihenfolge beachten',
        'example': 'EN: "%1$s von %2$s" → DE: "%1$s von %2$s" (nicht umdrehen!)',
    },
    'URL_MISSING': {
        'help': 'URLs aus der Quelle fehlen',
        'solution': 'Kopieren Sie alle URLs unverändert',
        'example': 'https://example.com darf nicht fehlen',
    },
    'EMAIL_MISSING': {
        'help': 'E-Mail-Adressen fehlen',
        'solution': 'Kopieren Sie alle E-Mails unverändert',
        'example': 'support@firma.de muss übernommen werden',
    },
    'BOUNDARY_SPACE_START_MISSING': {
        'help': 'Führendes Leerzeichen fehlt - UI-Layout wird zerstört!',
        'solution': 'Fügen Sie das Leerzeichen am Anfang hinzu',
        'example': 'Quelle: " Button" → Ziel: " Button" (mit Space!)',
        'ui_critical': True,
    },
    'BOUNDARY_SPACE_END_MISSING': {
        'help': 'Nachgestelltes Leerzeichen fehlt - UI-Layout wird zerstört!',
        'solution': 'Fügen Sie das Leerzeichen am Ende hinzu',
        'example': 'Quelle: "Label " → Ziel: "Beschriftung " (mit Space!)',
        'ui_critical': True,
    },
    'SOFT_HYPHEN_ADDED': {
        'help': 'Soft-Hyphen eingefügt - meist Word-Artefakt',
        'solution': 'Entfernen Sie unsichtbare Soft-Hyphens (U+00AD)',
        'example': 'Quali­tät → Qualität (ohne versteckten Trennstrich)',
    },
    'CONTROL_CHARS_FOUND': {
        'help': 'Steuerzeichen gefunden - kann zu Fehlern führen',
        'solution': 'Entfernen Sie alle Steuerzeichen',
        'example': 'NULL, BS, VT etc. entfernen',
    },
    
    # Phase 2 - Inhalt & Konsistenz
    'UNTRANSLATED_SEGMENT': {
        'help': 'Segment wurde nicht übersetzt (Copy-Paste-Fehler)',
        'solution': 'Übersetzen Sie den Text vollständig',
        'example': 'EN: "Quality Check" → DE: "Qualitätsprüfung" (nicht "Quality Check"!)',
        'critical': True,
    },
    'EMPTY_TRANSLATION': {
        'help': 'Übersetzung ist leer oder enthält nur Tags',
        'solution': 'Fügen Sie die vollständige Übersetzung hinzu',
        'example': 'Quelle hat Inhalt, Ziel darf nicht leer sein',
        'critical': True,
    },
    'TRANSLATION_TOO_SHORT': {
        'help': 'Übersetzung ist sehr kurz im Vergleich zur Quelle',
        'solution': 'Prüfen Sie, ob die Übersetzung vollständig ist',
        'example': '28 Zeichen Quelle → 1 Zeichen Ziel ist verdächtig',
    },
    'PUNCT_SPACE_BEFORE': {
        'help': 'Leerzeichen vor Satzzeichen (französischer Stil)',
        'solution': 'Entfernen Sie das Leerzeichen vor ! oder ?',
        'example': 'Falsch: "Hallo !" → Richtig: "Hallo!"',
    },
    'PUNCT_NO_SPACE_AFTER': {
        'help': 'Fehlendes Leerzeichen nach Satzzeichen',
        'solution': 'Fügen Sie ein Leerzeichen nach ! oder ? hinzu',
        'example': 'Falsch: "Hallo!Welt" → Richtig: "Hallo! Welt"',
    },
    'PUNCT_SPACE_BEFORE_COMMA': {
        'help': 'Leerzeichen vor Komma (falsch im Deutschen)',
        'solution': 'Entfernen Sie das Leerzeichen vor dem Komma',
        'example': 'Falsch: "Hallo ,Welt" → Richtig: "Hallo, Welt"',
    },
    'HTML_UNBALANCED': {
        'help': 'HTML-Tags sind nicht balanciert',
        'solution': 'Schließen Sie alle Tags korrekt: <b>Text</b>',
        'example': 'Falsch: <b>Text → Richtig: <b>Text</b>',
    },
    'NUMBER_MISSING': {
        'help': 'Zahlen aus der Quelle fehlen',
        'solution': 'Übernehmen Sie alle Zahlen (evtl. Format anpassen)',
        'example': 'EN: "1,234.56" → DE: "1.234,56"',
    },
    'PROPER_NAME_MISSING': {
        'help': 'Eigennamen oder Akronyme fehlen oder wurden verändert',
        'solution': 'Behalten Sie Eigennamen unverändert bei',
        'example': 'Microsoft, BMW, CEO dürfen nicht übersetzt werden',
    },
    'TERM_PREFERRED_MISSING': {
        'help': 'Glossar-Begriff wurde nicht verwendet',
        'solution': 'Verwenden Sie den bevorzugten Begriff aus dem Glossar',
        'example': 'Glossar sagt "Einstellungen" → nicht "Optionen"',
    },
    'DUPLICATE_INCONSISTENT': {
        'help': 'Identischer Quelltext wurde unterschiedlich übersetzt',
        'solution': 'Übersetzen Sie identische Segmente konsistent',
        'example': '"Settings" sollte immer "Einstellungen" sein',
    },
    'PRONOUN_MIX': {
        'help': 'Mischung von Du und Sie im selben Segment',
        'solution': 'Entscheiden Sie sich für eine Anrede-Form',
        'example': 'Entweder: "Klicke hier" ODER "Klicken Sie hier"',
    },
    'SECURITY_JS_LINK': {
        'help': 'Neuer javascript:-Link eingefügt - SICHERHEITSRISIKO!',
        'solution': 'Entfernen Sie javascript:-Links',
        'example': 'javascript:alert() ist eine XSS-Schwachstelle',
        'critical': True,
    },
    'SECURITY_SCRIPT_TAG': {
        'help': 'Neues <script>-Tag eingefügt - SICHERHEITSRISIKO!',
        'solution': 'Entfernen Sie alle <script>-Tags',
        'example': '<script>...</script> niemals hinzufügen',
        'critical': True,
    },
}

# ============================================================================
# Hilfsfunktion: Erweiterte Fehlerinformationen holen
# ============================================================================

def get_enriched_finding_info(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Reichert einen Finding mit hilfreichen Zusatzinformationen an."""
    rule_id = finding.get('rule_id') or finding.get('rule') or finding.get('code') or ''
    category = finding.get('category') or ''
    
    result = {
        'rule_id': rule_id,
        'category': category,
        'category_info': CATEGORY_INFO.get(category, {}),
        'rule_help': RULE_HELP.get(rule_id, {}),
        'has_solution': bool(RULE_HELP.get(rule_id, {}).get('solution')),
        'has_example': bool(RULE_HELP.get(rule_id, {}).get('example')),
        'is_ui_critical': RULE_HELP.get(rule_id, {}).get('ui_critical', False),
        'is_security_critical': RULE_HELP.get(rule_id, {}).get('critical', False),
    }
    
    # Kategorie-Prefix für schnelle Erkennung
    cat_info = result['category_info']
    if cat_info:
        result['category_prefix'] = cat_info.get('prefix', '')
        result['category_label'] = cat_info.get('label', category)
        result['impact_level'] = cat_info.get('impact', 'MITTEL')
    
    return result

# ============================================================================
# Hilfsfunktion: Formatierte Hilfetexte generieren
# ============================================================================

def format_finding_help_text(finding: Dict[str, Any], enriched: Dict[str, Any]) -> str:
    """Erstellt einen formatierten Hilfetext für einen Finding."""
    lines = []
    
    # Kategorie-Info
    cat_info = enriched.get('category_info', {})
    if cat_info:
        lines.append(f"KATEGORIE: {cat_info.get('label', '')} - {cat_info.get('description', '')}")
        lines.append(f"AUSWIRKUNG: {cat_info.get('impact', 'MITTEL')}")
        lines.append("")
    
    # Regel-spezifische Hilfe
    rule_help = enriched.get('rule_help', {})
    if rule_help:
        if rule_help.get('help'):
            lines.append(f"PROBLEM: {rule_help['help']}")
        if rule_help.get('solution'):
            lines.append(f"LÖSUNG: {rule_help['solution']}")
        if rule_help.get('example'):
            lines.append(f"BEISPIEL: {rule_help['example']}")
    
    return '\n'.join(lines)

# ============================================================================
# Hilfsfunktion: Schnell-Aktionen generieren
# ============================================================================

def get_quick_actions(finding: Dict[str, Any], enriched: Dict[str, Any]) -> list:
    """Generiert Quick-Action-Buttons für häufige Korrekturen."""
    rule_id = enriched.get('rule_id', '')
    actions = []
    
    # Platzhalter-Aktionen
    if 'PLACEHOLDER_MISSING' in rule_id:
        missing = finding.get('meta', {}).get('missing', [])
        if missing:
            actions.append({
                'label': f'Platzhalter hinzufügen: {", ".join(missing)}',
                'action': 'copy_placeholders',
                'data': missing
            })
    
    # URL-Aktionen
    if 'URL_MISSING' in rule_id:
        source_urls = finding.get('meta', {}).get('source', [])
        if source_urls:
            actions.append({
                'label': f'URLs kopieren',
                'action': 'copy_urls',
                'data': source_urls
            })
    
    # Whitespace-Aktionen
    if 'BOUNDARY_SPACE' in rule_id:
        actions.append({
            'label': 'Leerzeichen korrigieren',
            'action': 'fix_boundary_spaces',
            'data': None
        })
    
    # Unübersetzt-Aktionen
    if 'UNTRANSLATED_SEGMENT' in rule_id:
        actions.append({
            'label': 'Zur Übersetzung markieren',
            'action': 'mark_for_translation',
            'data': None
        })
    
    return actions

print("✅ UI-Optimierungs-Module geladen:")
print(f"   - {len(CATEGORY_INFO)} Kategorien definiert")
print(f"   - {len(RULE_HELP)} Regel-Hilfetexte bereitgestellt")
print("   - Enrichment-Funktionen verfügbar")
