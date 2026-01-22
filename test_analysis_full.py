#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug-Script für vollständige Analyse-Pipeline"""

import sys
import os

print("=" * 60)
print("Testing Full Analysis Pipeline")
print("=" * 60)

# Test mit realistischeren Daten die Findings erzeugen sollten
test_segments = [
    # Platzhalter-Inkonsistenz
    ("Hello {name}, welcome to {place}!", "Hallo {name}, willkommen!"),
    
    # Unterschiedliche Längen
    ("This is a short text.", "Das ist ein sehr sehr sehr langer Text mit vielen zusätzlichen Wörtern die nicht im Original vorkommen."),
    
    # Potentiell unübersetzt
    ("Hello world", "Hello world"),
    
    # URL Inkonsistenz
    ("Visit https://example.com", "Besuchen Sie https://different.com"),
    
    # Zahlenwert-Inkonsistenz
    ("The price is $100", "Der Preis ist 50€"),
    
    # Mehr realistische Sätze
    ("Quality assurance is essential for translation.", "Qualitätssicherung ist essentiell für Übersetzungen."),
    ("Please review the document carefully.", "Bitte überprüfen Sie das Dokument sorgfältig."),
]

print(f"\n📝 Test mit {len(test_segments)} Segment-Paaren\n")

# Phase 1 Test
print("-" * 60)
print("Phase 1: Formatierungs- und Strukturprüfungen")
print("-" * 60)
try:
    from quality_gui_phase1_checkers import run_phase1_checks
    results = run_phase1_checks(test_segments)
    print(f"✅ Gefunden: {len(results)} Issues")
    for i, issue in enumerate(results, 1):
        print(f"\n  {i}. [{getattr(issue, 'severity', 'info').upper()}] {getattr(issue, 'code', 'N/A')}")
        print(f"     {getattr(issue, 'message', 'N/A')}")
        src = getattr(issue, 'source_text', '')[:50]
        tgt = getattr(issue, 'target_text', '')[:50]
        if src: print(f"     Source: {src}...")
        if tgt: print(f"     Target: {tgt}...")
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

# Phase 2 Test
print("\n" + "-" * 60)
print("Phase 2: Inhalts- und Konsistenzprüfungen")
print("-" * 60)
try:
    from quality_gui_phase2_checkers import run_phase2_checks
    
    # Erstelle pair_infos mit mehr Informationen
    pair_infos = []
    for idx, (src, tgt) in enumerate(test_segments):
        pair_infos.append({
            'index': idx,
            'source': f"test_source_{idx}.txt",
            'translation': f"test_target_{idx}.txt",
            'source_chars': len(src),
            'translation_chars': len(tgt)
        })
    
    results = run_phase2_checks(
        test_segments, 
        glossary_path='',  # Kein Glossar
        config={},
        pair_infos=pair_infos
    )
    print(f"✅ Gefunden: {len(results)} Issues")
    for i, issue in enumerate(results, 1):
        print(f"\n  {i}. [{getattr(issue, 'severity', 'info').upper()}] {getattr(issue, 'code', 'N/A')}")
        print(f"     {getattr(issue, 'message', 'N/A')}")
        src = getattr(issue, 'source_text', '')[:50]
        tgt = getattr(issue, 'target_text', '')[:50]
        if src: print(f"     Source: {src}...")
        if tgt: print(f"     Target: {tgt}...")
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

# Phase 3 Test
print("\n" + "-" * 60)
print("Phase 3: Semantik und Grammatik")
print("-" * 60)
try:
    from quality_gui_phase3_checkers import run_phase3_checks
    
    results = run_phase3_checks(
        test_segments,
        enable_semantic=False,  # Deaktiviert für schnellen Test
        semantic_use_ollama=False,
        semantic_ollama_model=None,
        semantic_threshold=0.85,
        spellcheck_config={},
        pair_infos=pair_infos
    )
    print(f"✅ Gefunden: {len(results)} Issues")
    for i, issue in enumerate(results, 1):
        print(f"\n  {i}. [{getattr(issue, 'severity', 'info').upper()}] {getattr(issue, 'code', 'N/A')}")
        print(f"     {getattr(issue, 'message', 'N/A')}")
        src = getattr(issue, 'source_text', '')[:50]
        tgt = getattr(issue, 'target_text', '')[:50]
        if src: print(f"     Source: {src}...")
        if tgt: print(f"     Target: {tgt}...")
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test abgeschlossen")
print("=" * 60)
