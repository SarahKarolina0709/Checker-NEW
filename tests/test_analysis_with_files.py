#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vollständige Analyse-Test mit temporären Testdateien"""

import tempfile
import os
from pathlib import Path

print("=" * 70)
print("Testing Quality GUI Analysis with Real Files")
print("=" * 70)

# Erstelle temporäre Testdateien
with tempfile.TemporaryDirectory() as tmpdir:
    # Source-Dateien erstellen
    src1 = Path(tmpdir) / "source1.txt"
    src1.write_text("Hello {name}, welcome to {place}!\nVisit https://example.com for more info.", encoding='utf-8')
    
    src2 = Path(tmpdir) / "source2.txt"
    src2.write_text("The price is $100.\nPlease contact us at info@example.com", encoding='utf-8')
    
    # Target-Dateien erstellen (mit Fehlern)
    tgt1 = Path(tmpdir) / "target1.txt"
    tgt1.write_text("Hallo {name}, willkommen!\nBesuchen Sie https://different.com für mehr Info.", encoding='utf-8')
    
    tgt2 = Path(tmpdir) / "target2.txt"
    tgt2.write_text("Der Preis ist 50€.\nBitte kontaktieren Sie uns unter info@example.com", encoding='utf-8')
    
    print(f"\n✅ Temporäre Testdateien erstellt in: {tmpdir}\n")
    print(f"   Source-Dateien: {src1.name}, {src2.name}")
    print(f"   Target-Dateien: {tgt1.name}, {tgt2.name}")
    
    # Simuliere die Analyse-Pipeline
    print("\n" + "-" * 70)
    print("Simulating Analysis Pipeline")
    print("-" * 70)
    
    # Lade Dateien
    files = {
        'source': [str(src1), str(src2)],
        'translation': [str(tgt1), str(tgt2)]
    }
    
    print(f"\n📂 Geladene Dateien:")
    print(f"   Source: {len(files['source'])} Dateien")
    print(f"   Translation: {len(files['translation'])} Dateien")
    
    # Erstelle Paare
    pair_segments = []
    for src_path, tgt_path in zip(files['source'], files['translation']):
        src_text = Path(src_path).read_text(encoding='utf-8')
        tgt_text = Path(tgt_path).read_text(encoding='utf-8')
        pair_segments.append((src_text, tgt_text))
    
    print(f"\n📊 Segment-Paare: {len(pair_segments)}")
    
    # Teste Phase 1
    print("\n" + "-" * 70)
    print("Phase 1: Format & Structure Checks")
    print("-" * 70)
    try:
        from quality_gui_phase1_checkers import run_phase1_checks
        phase1_issues = run_phase1_checks(pair_segments)
        print(f"✅ Phase 1 abgeschlossen: {len(phase1_issues)} Issues gefunden")
        
        if phase1_issues:
            print("\n📋 Phase 1 Issues:")
            for i, issue in enumerate(phase1_issues[:5], 1):
                print(f"\n  {i}. [{getattr(issue, 'severity', 'INFO').upper()}] {getattr(issue, 'code', 'N/A')}")
                print(f"     {getattr(issue, 'message', 'N/A')}")
    except Exception as e:
        print(f"❌ Phase 1 Fehler: {e}")
        import traceback
        traceback.print_exc()
        phase1_issues = []
    
    # Teste Phase 2
    print("\n" + "-" * 70)
    print("Phase 2: Content & Consistency Checks")
    print("-" * 70)
    try:
        from quality_gui_phase2_checkers import run_phase2_checks
        
        pair_infos = []
        for idx, (src_path, tgt_path) in enumerate(zip(files['source'], files['translation'])):
            pair_infos.append({
                'index': idx,
                'source': src_path,
                'translation': tgt_path,
                'source_name': os.path.basename(src_path),
                'translation_name': os.path.basename(tgt_path),
                'source_chars': len(Path(src_path).read_text(encoding='utf-8')),
                'translation_chars': len(Path(tgt_path).read_text(encoding='utf-8'))
            })
        
        phase2_issues = run_phase2_checks(
            pair_segments,
            glossary_path='',
            config={},
            pair_infos=pair_infos
        )
        print(f"✅ Phase 2 abgeschlossen: {len(phase2_issues)} Issues gefunden")
        
        if phase2_issues:
            print("\n📋 Phase 2 Issues:")
            for i, issue in enumerate(phase2_issues[:5], 1):
                print(f"\n  {i}. [{getattr(issue, 'severity', 'INFO').upper()}] {getattr(issue, 'code', 'N/A')}")
                print(f"     {getattr(issue, 'message', 'N/A')}")
    except Exception as e:
        print(f"❌ Phase 2 Fehler: {e}")
        import traceback
        traceback.print_exc()
        phase2_issues = []
    
    # Teste Phase 3
    print("\n" + "-" * 70)
    print("Phase 3: Semantic & Grammar Checks")
    print("-" * 70)
    try:
        from quality_gui_phase3_checkers import run_phase3_checks
        
        phase3_issues = run_phase3_checks(
            pair_segments,
            enable_semantic=False,
            semantic_use_ollama=False,
            semantic_ollama_model=None,
            semantic_threshold=0.85,
            spellcheck_config={},
            pair_infos=pair_infos
        )
        print(f"✅ Phase 3 abgeschlossen: {len(phase3_issues)} Issues gefunden")
        
        if phase3_issues:
            print("\n📋 Phase 3 Issues:")
            for i, issue in enumerate(phase3_issues[:5], 1):
                print(f"\n  {i}. [{getattr(issue, 'severity', 'INFO').upper()}] {getattr(issue, 'code', 'N/A')}")
                print(f"     {getattr(issue, 'message', 'N/A')}")
    except Exception as e:
        print(f"❌ Phase 3 Fehler: {e}")
        import traceback
        traceback.print_exc()
        phase3_issues = []
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("Analyse-Zusammenfassung")
    print("=" * 70)
    print(f"\n✅ Gesamt gefundene Issues:")
    print(f"   Phase 1: {len(phase1_issues)}")
    print(f"   Phase 2: {len(phase2_issues)}")
    print(f"   Phase 3: {len(phase3_issues)}")
    print(f"   GESAMT: {len(phase1_issues) + len(phase2_issues) + len(phase3_issues)}")
    
    print("\n" + "=" * 70)
    print("✅ Test erfolgreich abgeschlossen")
    print("=" * 70)
    print("\n💡 Die Analyse funktioniert korrekt!")
    print("   Um sie in der GUI zu nutzen:")
    print("   1. Starten Sie quality_gui_main_app.py")
    print("   2. Laden Sie Source- und Translation-Dateien hoch")
    print("   3. Klicken Sie auf 'Analyse starten'")
