"""Demo der UI-Optimierungen für Analyse-Ergebnisse."""
from ui_optimization_helpers import (
    get_enriched_finding_info,
    format_finding_help_text,
    get_quick_actions,
    CATEGORY_INFO
)

print("=" * 70)
print("🎨 UI-OPTIMIERUNG: VORHER/NACHHER DEMO")
print("=" * 70)

# Beispiel-Finding: Unübersetztes Segment
finding1 = {
    'rule_id': 'UNTRANSLATED_SEGMENT',
    'rule': 'UNTRANSLATED_SEGMENT',
    'category': 'completeness',
    'severity': 'critical',
    'message': 'Segment scheint unübersetzt (Ähnlichkeit: 100%)',
    'source_text': 'Quality Check',
    'target_text': 'Quality Check',
    'meta': {'similarity': 1.0}
}

# Beispiel-Finding: Boundary Whitespace
finding2 = {
    'rule_id': 'BOUNDARY_SPACE_END_MISSING',
    'rule': 'BOUNDARY_SPACE_END_MISSING',
    'category': 'whitespace',
    'severity': 'major',
    'message': 'Nachgestelltes Leerzeichen fehlt im Ziel (UI-Layout!)',
    'source_text': ' Button ',
    'target_text': ' Button',
}

# Beispiel-Finding: Satzzeichen-Spacing
finding3 = {
    'rule_id': 'PUNCT_SPACE_BEFORE',
    'rule': 'PUNCT_SPACE_BEFORE',
    'category': 'typography',
    'severity': 'minor',
    'message': 'Leerzeichen vor ! oder ? (französischer Fehler)',
    'target_text': 'Hallo !',
}

findings = [finding1, finding2, finding3]

for i, finding in enumerate(findings, 1):
    print(f"\n{'='*70}")
    print(f"BEISPIEL {i}: {finding['rule_id']}")
    print("="*70)
    
    # VORHER: Standard-Darstellung
    print("\n📦 VORHER (Standard):")
    print(f"  [{finding['severity'].upper()}] {finding['rule']}")
    print(f"  {finding['message']}")
    
    # NACHHER: Optimierte Darstellung
    print("\n✨ NACHHER (Optimiert):")
    enriched = get_enriched_finding_info(finding)
    
    # Kategorie-Badge
    cat_prefix = enriched.get('category_prefix', '')
    cat_label = enriched.get('category_label', '')
    print(f"  {cat_prefix} [{finding['severity'].upper()}]")
    print(f"  {cat_label}: {finding['rule']}")
    print(f"  {finding['message']}")
    
    # Auswirkung
    if enriched.get('impact_level'):
        print(f"  ⚡ Auswirkung: {enriched['impact_level']}")
    
    # Lösung
    solution = enriched.get('rule_help', {}).get('solution')
    if solution:
        print(f"  💡 LÖSUNG: {solution}")
    
    # Beispiel
    example = enriched.get('rule_help', {}).get('example')
    if example:
        print(f"  📋 Beispiel: {example}")
    
    # Kategorie-Info
    cat_info = enriched.get('category_info', {})
    if cat_info:
        print(f"\n  📚 Kategorie-Info:")
        print(f"     {cat_info.get('description', '')}")
        print(f"     Beispiele: {cat_info.get('examples', '')}")

print("\n" + "="*70)
print("📊 ZUSAMMENFASSUNG DER VERBESSERUNGEN")
print("="*70)
print("\n✅ HINZUGEFÜGT:")
print("  1. Kategorie-Prefix in Badge ([PH], [WS], [COMP] etc.)")
print("  2. Kategorie-Label im Titel (z.B. 'Vollständigkeit: ...')")
print("  3. Auswirkung-Level (KRITISCH, HOCH, MITTEL, NIEDRIG)")
print("  4. Lösungsvorschlag prominent hervorgehoben")
print("  5. Praktisches Beispiel für korrektes Format")
print("  6. Detaillierte Kategorie-Beschreibung")
print("  7. Visuell hervorgehobene Lösung (farbiger Frame)")
print("\n💡 NUTZEN FÜR ÜBERSETZER:")
print("  ✓ Schnellere Fehleridentifikation durch Kategorie-Prefix")
print("  ✓ Direkte Lösung ohne langes Suchen")
print("  ✓ Praktische Beispiele zum Nachvollziehen")
print("  ✓ Verständnis der Auswirkung (Priorität)")
print("  ✓ Bessere Lernkurve durch Kontext-Informationen")
print("\n🎯 ERGEBNIS:")
print("  Von 'Was ist das?' zu 'So fixe ich das!' in Sekunden!")
