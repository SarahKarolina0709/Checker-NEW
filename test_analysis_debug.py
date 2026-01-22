#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug-Script zum Testen der Analyse-Funktionalität"""

import sys
import os

# Prüfe ob Phase Checker Module importierbar sind
print("=" * 60)
print("Testing Analysis Phase Checkers")
print("=" * 60)

try:
    from quality_gui_phase1_checkers import run_phase1_checks
    print("✅ quality_gui_phase1_checkers erfolgreich importiert")
    print(f"   run_phase1_checks callable: {callable(run_phase1_checks)}")
except Exception as e:
    print(f"❌ quality_gui_phase1_checkers Import fehlgeschlagen: {e}")
    run_phase1_checks = None

try:
    from quality_gui_phase2_checkers import run_phase2_checks
    print("✅ quality_gui_phase2_checkers erfolgreich importiert")
    print(f"   run_phase2_checks callable: {callable(run_phase2_checks)}")
except Exception as e:
    print(f"❌ quality_gui_phase2_checkers Import fehlgeschlagen: {e}")
    run_phase2_checks = None

try:
    from quality_gui_phase3_checkers import run_phase3_checks
    print("✅ quality_gui_phase3_checkers erfolgreich importiert")
    print(f"   run_phase3_checks callable: {callable(run_phase3_checks)}")
except Exception as e:
    print(f"❌ quality_gui_phase3_checkers Import fehlgeschlagen: {e}")
    run_phase3_checks = None

print("\n" + "=" * 60)
print("Testing Phase 1 Checks mit Beispieldaten")
print("=" * 60)

if run_phase1_checks:
    try:
        # Test mit einfachen Beispieldaten
        test_segments = [
            ("Hello {name}, this is a test.", "Hallo {name}, das ist ein Test."),
            ("The URL is https://example.com", "Die URL ist https://example.com"),
            ("Email: test@example.com", "E-Mail: test@example.com")
        ]
        
        results = run_phase1_checks(test_segments)
        print(f"✅ Phase 1 erfolgreich ausgeführt")
        print(f"   Anzahl Ergebnisse: {len(results)}")
        
        if results:
            print(f"\n   Erste 3 Ergebnisse:")
            for i, issue in enumerate(results[:3], 1):
                print(f"     {i}. Code: {getattr(issue, 'code', 'N/A')}")
                print(f"        Severity: {getattr(issue, 'severity', 'N/A')}")
                print(f"        Message: {getattr(issue, 'message', 'N/A')[:80]}")
    except Exception as e:
        print(f"❌ Phase 1 Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  run_phase1_checks nicht verfügbar, Test übersprungen")

print("\n" + "=" * 60)
print("Testing Phase 2 Checks mit Beispieldaten")
print("=" * 60)

if run_phase2_checks:
    try:
        test_segments = [
            ("This is a test document.", "Dies ist ein Testdokument."),
            ("Quality assurance is important.", "Qualitätssicherung ist wichtig.")
        ]
        
        results = run_phase2_checks(test_segments, glossary_path=None, config={}, pair_infos=[])
        print(f"✅ Phase 2 erfolgreich ausgeführt")
        print(f"   Anzahl Ergebnisse: {len(results)}")
        
        if results:
            print(f"\n   Erste 3 Ergebnisse:")
            for i, issue in enumerate(results[:3], 1):
                print(f"     {i}. Code: {getattr(issue, 'code', 'N/A')}")
                print(f"        Severity: {getattr(issue, 'severity', 'N/A')}")
                print(f"        Message: {getattr(issue, 'message', 'N/A')[:80]}")
    except Exception as e:
        print(f"❌ Phase 2 Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  run_phase2_checks nicht verfügbar, Test übersprungen")

print("\n" + "=" * 60)
print("Testing Phase 3 Checks mit Beispieldaten")
print("=" * 60)

if run_phase3_checks:
    try:
        test_segments = [
            ("This is a test.", "Das ist ein Test."),
            ("Hello world!", "Hallo Welt!")
        ]
        
        results = run_phase3_checks(
            test_segments,
            enable_semantic=False,
            semantic_use_ollama=False,
            semantic_ollama_model=None,
            semantic_threshold=0.85,
            spellcheck_config={},
            pair_infos=[]
        )
        print(f"✅ Phase 3 erfolgreich ausgeführt")
        print(f"   Anzahl Ergebnisse: {len(results)}")
        
        if results:
            print(f"\n   Erste 3 Ergebnisse:")
            for i, issue in enumerate(results[:3], 1):
                print(f"     {i}. Code: {getattr(issue, 'code', 'N/A')}")
                print(f"        Severity: {getattr(issue, 'severity', 'N/A')}")
                print(f"        Message: {getattr(issue, 'message', 'N/A')[:80]}")
    except Exception as e:
        print(f"❌ Phase 3 Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  run_phase3_checks nicht verfügbar, Test übersprungen")

print("\n" + "=" * 60)
print("Test abgeschlossen")
print("=" * 60)
