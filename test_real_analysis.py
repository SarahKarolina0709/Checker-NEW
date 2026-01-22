#!/usr/bin/env python3
"""
Test: Erstelle echte Dateien und führe echte Analyse durch
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Set encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Create sample files
temp_dir = tempfile.mkdtemp(prefix='checker_test_')

# Source translation
source_md = temp_dir + "/source.md"
with open(source_md, 'w', encoding='utf-8') as f:
    f.write("""# English Document

## Introduction
This is a test document for quality checking.

## Main Section
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
The quick brown fox jumps over the lazy dog.

## Conclusion
This concludes our test document.
""")

# Target translation (with intentional issues)
target_md = temp_dir + "/target.md"
with open(target_md, 'w', encoding='utf-8') as f:
    f.write("""# German Document

## Introduction  
Das ist ein Test-Dokument zur Qualitätsprüfung.

## Main Section
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Der schnelle braune Fuchs springt über den faulen Hund.

## Conclusion
Das endet unser Test-Dokumentation.
""")

print(f"\nCreated test files in: {temp_dir}")
print(f"  - {source_md}")
print(f"  - {target_md}")

# Now run analysis
try:
    from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
    import customtkinter as ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    app = ProfessionelleUebersetzungsqualitaetsApp()
    
    # Run analysis on real files
    files = [
        {'type': 'source_segment', 'path': source_md, 'content': open(source_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
        {'type': 'target_segment', 'path': target_md, 'content': open(target_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
    ]
    
    print(f"\n" + "="*60)
    print("Running analysis...")
    print("="*60)
    
    # Call the pipeline directly
    results = app._run_analysis_pipeline(files, rule_profile='default')
    
    print(f"\nAnalysis complete!")
    print(f"Results type: {type(results)}")
    print(f"Results keys: {list(results.keys()) if isinstance(results, dict) else 'NOT DICT'}")
    
    if isinstance(results, dict):
        # Check findings
        findings = results.get('findings', [])
        print(f"\nFindings: {len(findings)} items")
        if findings:
            print("First finding:")
            print(json.dumps(findings[0], indent=2, ensure_ascii=False, default=str))
        
        # Check phase issues
        for phase in ('issues_phase1', 'issues_phase2', 'issues_phase3'):
            phase_issues = results.get(phase, [])
            print(f"\n{phase}: {len(phase_issues)} items")
        
        # Check metrics
        metrics = results.get('metrics')
        if metrics and isinstance(metrics, dict):
            print(f"\nMetrics keys: {list(metrics.keys())}")
        
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\nCleaned up: {temp_dir}")
    
    root.destroy()
    
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc())
    
    # Cleanup on error
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
