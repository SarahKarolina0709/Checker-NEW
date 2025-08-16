#!/usr/bin/env python3
"""
🔤 TYPOGRAPHY VALIDATION TOOL
Validiert die Einhaltung der Font-Regeln in welcome_screen.py
"""

from datetime import datetime
import json
import re

def validate_typography_compliance():
    """Validiert Typography-Compliance"""

    print("🔤 TYPOGRAPHY COMPLIANCE VALIDATION")
    print("=" * 60)

    try:
        with open('welcome_screen.py', 'r', encoding='utf-8') as f:
            content = f.read()

        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_lines": len(content.split('\n')),
            "compliance_score": 0,
            "violations": [],
            "recommendations": [],
            "statistics": {}
        }

        # 1. Direkte CTkFont-Aufrufe prüfen
        print("\n🔍 1. PRÜFUNG: Direkte CTkFont-Aufrufe")
        ctkfont_pattern = r'CTkFont\([^)]*size=(\d+)[^)]*\)'
        ctkfont_matches = re.findall(ctkfont_pattern, content)

        if ctkfont_matches:
            results["violations"].append({
                "type": "direct_ctkfont_calls",
                "count": len(ctkfont_matches),
                "severity": "HIGH",
                "description": f"{len(ctkfont_matches)} direkte CTkFont-Aufrufe gefunden"
            })
            print(f"   ❌ {len(ctkfont_matches)} direkte CTkFont-Aufrufe gefunden")

            # Top Größen anzeigen
            from collections import Counter
            size_counter = Counter(ctkfont_matches)
            print(f"   📊 Häufigste Größen: {dict(size_counter.most_common(3))}")
        else:
            print("   ✅ Keine direkten CTkFont-Aufrufe gefunden")

        # 2. get_typography() Verwendung prüfen
        print("\n🔍 2. PRÜFUNG: get_typography() Verwendung")
        typography_pattern = r'get_typography\([\'"]([^\'"]+)[\'"]\)'
        typography_matches = re.findall(typography_pattern, content)

        if typography_matches:
            print(f"   ✅ {len(typography_matches)} get_typography() Aufrufe gefunden")

            # Häufigste Typography-Typen
            from collections import Counter
            type_counter = Counter(typography_matches)
            print(f"   📊 Top Typography-Typen: {dict(type_counter.most_common(5))}")

            results["statistics"]["typography_calls"] = len(typography_matches)
            results["statistics"]["typography_types"] = len(set(typography_matches))
        else:
            results["violations"].append({
                "type": "no_typography_calls",
                "count": 0,
                "severity": "CRITICAL",
                "description": "Keine get_typography() Aufrufe gefunden"
            })
            print("   ❌ Keine get_typography() Aufrufe gefunden")

        # 3. Hartcodierte Schriftgrößen prüfen
        print("\n🔍 3. PRÜFUNG: Hartcodierte Schriftgrößen")
        hardcoded_pattern = r'size=(\d+)'
        hardcoded_matches = re.findall(hardcoded_pattern, content)

        if hardcoded_matches:
            results["violations"].append({
                "type": "hardcoded_sizes",
                "count": len(hardcoded_matches),
                "severity": "MEDIUM",
                "description": f"{len(hardcoded_matches)} hartcodierte Schriftgrößen gefunden"
            })
            print(f"   ⚠️ {len(hardcoded_matches)} hartcodierte Schriftgrößen gefunden")
        else:
            print("   ✅ Keine hartcodierten Schriftgrößen gefunden")

        # 4. Semantic Font Names prüfen
        print("\n🔍 4. PRÜFUNG: Semantic Font Names")
        valid_semantic_names = [
            "micro", "micro_normal", "micro_large",
            "caption", "caption_bold", "small", "small_normal",
            "body_sm", "body", "body_bold", "body_lg",
            "label", "label_bold", "button_md",
            "subheading", "heading_sm", "heading", "heading_lg",
            "title", "title_lg", "display", "display_lg",
            "menu", "status", "metric_value", "code"
        ]

        invalid_names = []
        for match in typography_matches:
            if match not in valid_semantic_names:
                invalid_names.append(match)

        if invalid_names:
            results["violations"].append({
                "type": "invalid_semantic_names",
                "count": len(invalid_names),
                "severity": "MEDIUM",
                "description": f"Ungültige semantische Namen: {set(invalid_names)}"
            })
            print(f"   ⚠️ Ungültige semantische Namen: {set(invalid_names)}")
        else:
            print("   ✅ Alle semantischen Namen sind gültig")

        # 5. Font-Caching Prüfung
        print("\n🔍 5. PRÜFUNG: Font-Caching Implementation")
        caching_patterns = [
            r'def get_typography',
            r'@lru_cache',
            r'_typography_cache',
            r'font.*cache'
        ]

        caching_found = False
        for pattern in caching_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                caching_found = True
                break

        if caching_found:
            print("   ✅ Font-Caching Implementation gefunden")
        else:
            results["violations"].append({
                "type": "no_font_caching",
                "count": 0,
                "severity": "LOW",
                "description": "Keine Font-Caching Implementation gefunden"
            })
            print("   ⚠️ Keine Font-Caching Implementation gefunden")

        # 6. Performance-Metriken berechnen
        print("\n📊 PERFORMANCE-METRIKEN:")

        total_font_calls = len(ctkfont_matches) + len(typography_matches)
        if total_font_calls > 0:
            typography_ratio = len(typography_matches) / total_font_calls * 100
            results["statistics"]["typography_ratio"] = typography_ratio
            print(f"   🎯 Typography-Ratio: {typography_ratio:.1f}%")

            if typography_ratio >= 80:
                print("   🏆 EXZELLENT: >80% Typography-Verwendung")
                compliance_score = 95
            elif typography_ratio >= 60:
                print("   ✅ GUT: >60% Typography-Verwendung")
                compliance_score = 75
            elif typography_ratio >= 40:
                print("   ⚠️ VERBESSERUNGSBEDARF: >40% Typography-Verwendung")
                compliance_score = 50
            else:
                print("   ❌ KRITISCH: <40% Typography-Verwendung")
                compliance_score = 25
        else:
            compliance_score = 0

        # Reduktion für Violations
        violation_penalty = len(results["violations"]) * 10
        compliance_score = max(0, compliance_score - violation_penalty)
        results["compliance_score"] = compliance_score

        # 7. Empfehlungen generieren
        print("\n💡 EMPFEHLUNGEN:")

        if len(ctkfont_matches) > 0:
            results["recommendations"].append({
                "priority": "HIGH",
                "action": f"Konvertiere {len(ctkfont_matches)} direkte CTkFont-Aufrufe zu get_typography()",
                "benefit": "Zentrale Font-Verwaltung und bessere Performance"
            })
            print(f"   🔄 HIGH: Konvertiere {len(ctkfont_matches)} direkte CTkFont-Aufrufe")

        if len(typography_matches) < 50:
            results["recommendations"].append({
                "priority": "MEDIUM",
                "action": "Erweitere Typography-System Verwendung",
                "benefit": "Bessere Konsistenz und Wartbarkeit"
            })
            print("   📈 MEDIUM: Erweitere Typography-System Verwendung")

        if not caching_found:
            results["recommendations"].append({
                "priority": "LOW",
                "action": "Implementiere Font-Caching für Performance",
                "benefit": "Reduzierte Memory-Verwendung und bessere Performance"
            })
            print("   ⚡ LOW: Implementiere Font-Caching")

        # 8. Compliance Score anzeigen
        print(f"\n🏆 COMPLIANCE SCORE: {compliance_score}/100")

        if compliance_score >= 90:
            status = "🏆 EXZELLENT"
            color = "GREEN"
        elif compliance_score >= 70:
            status = "✅ GUT"
            color = "BLUE"
        elif compliance_score >= 50:
            status = "⚠️ VERBESSERUNGSBEDARF"
            color = "YELLOW"
        else:
            status = "❌ KRITISCH"
            color = "RED"

        print(f"📊 STATUS: {status}")
        results["status"] = status

        # 9. Detaillierte Statistiken
        print("\n📈 DETAILLIERTE STATISTIKEN:")
        print(f"   📝 Gesamt Font-Aufrufe: {total_font_calls}")
        print(f"   ✅ Typography-Aufrufe: {len(typography_matches)}")
        print(f"   ❌ Direkte CTkFont-Aufrufe: {len(ctkfont_matches)}")
        print(f"   🎯 Typography-Varianten: {len(set(typography_matches))}")

        if len(typography_matches) > 0:
            reuse_factor = len(typography_matches) / len(set(typography_matches))
            print(f"   🔄 Wiederverwendungs-Faktor: {reuse_factor:.1f}x")
            results["statistics"]["reuse_factor"] = reuse_factor

        # 10. Report speichern
        report_filename = f"typography_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report gespeichert: {report_filename}")

        return results

    except Exception as e:
        print(f"❌ Fehler bei Validation: {e}")
        return None

def generate_conversion_suggestions():
    """Generiert konkrete Konvertierungs-Vorschläge"""

    print("\n🔄 KONVERTIERUNGS-VORSCHLÄGE:")
    print("=" * 50)

    try:
        with open('welcome_screen.py', 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        suggestions = []

        # Finde CTkFont-Zeilen mit Kontext
        for i, line in enumerate(lines):
            if 'CTkFont(' in line and 'size=' in line:
                size_match = re.search(r'size=(\d+)', line)
                if size_match:
                    size = size_match.group(1)

                    # Empfohlene Konvertierung
                    conversion_map = {
                        '8': 'micro',
                        '10': 'micro_large',
                        '11': 'caption',
                        '12': 'small_normal',
                        '13': 'body_sm',
                        '14': 'body',
                        '15': 'body_lg',
                        '16': 'label',
                        '18': 'subheading',
                        '20': 'heading_sm',
                        '22': 'heading',
                        '24': 'heading_lg',
                        '26': 'title',
                        '32': 'display'
                    }

                    recommended = conversion_map.get(size, 'body')

                    suggestion = {
                        'line_number': i + 1,
                        'original_line': line.strip(),
                        'size': size,
                        'recommended_type': recommended,
                        'conversion': line.replace(
                            f'CTkFont(family="Segoe UI", size={size}',
                            f'CTkFont(*self.get_typography("{recommended}")'
                        ).replace(
                            f'CTkFont(size={size}',
                            f'CTkFont(*self.get_typography("{recommended}")'
                        )
                    }

                    suggestions.append(suggestion)

        # Top 5 Konvertierungen anzeigen
        for i, suggestion in enumerate(suggestions[:5]):
            print(f"\n📝 KONVERTIERUNG {i+1}:")
            print(f"   📍 Zeile {suggestion['line_number']}")
            print(f"   📏 Größe: {suggestion['size']}px → {suggestion['recommended_type']}")
            print(f"   ❌ Vorher: {suggestion['original_line'][:80]}...")
            print(f"   ✅ Nachher: {suggestion['conversion'][:80]}...")

        if len(suggestions) > 5:
            print(f"\n📋 ... und {len(suggestions) - 5} weitere Konvertierungen möglich")

        return suggestions

    except Exception as e:
        print(f"❌ Fehler bei Vorschlägen: {e}")
        return []

def main():
    """Hauptfunktion"""

    print("🚀 Starte Typography Validation...")

    # Compliance prüfen
    results = validate_typography_compliance()

    if results:
        # Konvertierungs-Vorschläge
        suggestions = generate_conversion_suggestions()

        print("\n" + "="*60)
        print("✅ TYPOGRAPHY VALIDATION ABGESCHLOSSEN")
        print("="*60)

        if results["compliance_score"] >= 80:
            print("🎉 GRATULATION! Hervorragende Typography-Compliance!")
        elif results["compliance_score"] >= 60:
            print("👍 Gute Typography-Compliance! Noch wenige Verbesserungen möglich.")
        else:
            print("⚠️ Verbesserungsbedarf bei Typography-Compliance erkannt.")

    else:
        print("❌ Validation fehlgeschlagen")

if __name__ == "__main__":
    main()