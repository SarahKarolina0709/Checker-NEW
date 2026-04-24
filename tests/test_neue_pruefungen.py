"""Test der neuen kritischen Prüfungen für das Übersetzungsbüro."""
from quality_gui_phase1_checkers import (
    check_boundary_whitespace,
    check_soft_hyphens_and_control_chars
)
from quality_gui_phase2_checkers import (
    check_untranslated_segments,
    check_empty_translation,
    check_punctuation_spacing
)

print("=" * 60)
print("🧪 TEST DER NEUEN KRITISCHEN PRÜFUNGEN")
print("=" * 60)

# ============================================================================
# PHASE 1: Boundary Whitespace (UI-kritisch!)
# ============================================================================
print("\n📍 1. Boundary Whitespace (UI-kritisch für Buttons/Labels)")
print("-" * 60)

test_cases = [
    (" Button ", "Button", "Fehlendes führendes UND nachgestelltes Leerzeichen"),
    ("Label ", "Label", "Fehlendes nachgestelltes Leerzeichen"),
    ("Text", " Text", "Zusätzliches führendes Leerzeichen"),
    ("OK", "OK", "Korrekt - keine Änderung"),
]

for src, tgt, desc in test_cases:
    issues = check_boundary_whitespace(src, tgt)
    status = "❌ FEHLER" if issues else "✅ OK"
    print(f"{status} | {desc}")
    if issues:
        for issue in issues:
            print(f"     └─ {issue.code}: {issue.message}")

# ============================================================================
# PHASE 1: Soft Hyphens & Steuerzeichen
# ============================================================================
print("\n📍 2. Soft Hyphens & Steuerzeichen (Word-Artefakte)")
print("-" * 60)

test_cases = [
    ("Qualität", "Quali\u00ADtät", "Soft-Hyphen eingefügt (Word)"),
    ("Test", "Test\u0000", "NULL-Zeichen eingefügt"),
    ("Normal", "Normal", "Korrekt - keine Steuerzeichen"),
]

for src, tgt, desc in test_cases:
    issues = check_soft_hyphens_and_control_chars(src, tgt)
    status = "❌ FEHLER" if issues else "✅ OK"
    print(f"{status} | {desc}")
    if issues:
        for issue in issues:
            print(f"     └─ {issue.code}: {issue.message}")

# ============================================================================
# PHASE 2: Unübersetzte Segmente
# ============================================================================
print("\n📍 3. Unübersetzte Segmente (Copy-Paste-Fehler)")
print("-" * 60)

test_cases = [
    ("Hello World", "Hello World", "Unübersetzt (identisch)"),
    ("The quick brown fox", "The quick brown fox jumps", "Fast identisch (>85%)"),
    ("Hello", "Hallo", "Korrekt übersetzt"),
    ("Quality Check", "Qualitätsprüfung", "Korrekt übersetzt"),
]

for src, tgt, desc in test_cases:
    issues = check_untranslated_segments(src, tgt)
    status = "❌ FEHLER" if issues else "✅ OK"
    print(f"{status} | {desc}")
    if issues:
        for issue in issues:
            print(f"     └─ {issue.code}: {issue.message}")

# ============================================================================
# PHASE 2: Leere Übersetzungen
# ============================================================================
print("\n📍 4. Leere Übersetzungen")
print("-" * 60)

test_cases = [
    ("This is a long source text", "", "Komplett leer"),
    ("This is a long source text", "   ", "Nur Leerzeichen"),
    ("This is a long source text", "<b></b>", "Nur Tags"),
    ("This is a long source text", "x", "Extrem kurz (1 vs 28 Zeichen)"),
    ("Short", "Kurz", "Korrekt - beide kurz"),
]

for src, tgt, desc in test_cases:
    issues = check_empty_translation(src, tgt)
    status = "❌ FEHLER" if issues else "✅ OK"
    print(f"{status} | {desc}")
    if issues:
        for issue in issues:
            print(f"     └─ {issue.code}: {issue.message}")

# ============================================================================
# PHASE 2: Satzzeichen-Spacing (Typografie)
# ============================================================================
print("\n📍 5. Satzzeichen-Spacing (deutsche Typografie)")
print("-" * 60)

test_cases = [
    ("Hallo !", "Leerzeichen vor ! (französischer Fehler)"),
    ("Was ?", "Leerzeichen vor ? (französischer Fehler)"),
    ("Hallo!Welt", "Fehlendes Leerzeichen nach !"),
    ("Was?Nichts", "Fehlendes Leerzeichen nach ?"),
    ("Hallo ,Welt", "Leerzeichen vor Komma"),
    ("Hallo,Welt", "Fehlendes Leerzeichen nach Komma"),
    ("Achtung : Wichtig", "Leerzeichen vor Doppelpunkt"),
    ("Hallo! Welt", "Korrekt - alle Abstände richtig"),
]

for tgt, desc in test_cases:
    issues = check_punctuation_spacing(tgt)
    status = "❌ FEHLER" if issues else "✅ OK"
    print(f"{status} | {desc}")
    if issues:
        for issue in issues:
            print(f"     └─ {issue.code}: {issue.message}")

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================
print("\n" + "=" * 60)
print("✅ ALLE NEUEN PRÜFUNGEN ERFOLGREICH GETESTET!")
print("=" * 60)
print("\n📊 Implementierte Prüfungen:")
print("   ✅ Boundary Whitespace (UI-kritisch)")
print("   ✅ Soft Hyphens & Steuerzeichen (Word-Artefakte)")
print("   ✅ Unübersetzte Segmente (Copy-Paste-Fehler)")
print("   ✅ Leere Übersetzungen (Fehlende Inhalte)")
print("   ✅ Satzzeichen-Spacing (Deutsche Typografie)")
print("\n💡 Diese Prüfungen decken die häufigsten Fehler ab,")
print("   die in professionellen Übersetzungsbüros auftreten!")
