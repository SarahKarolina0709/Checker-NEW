#!/usr/bin/env python3
"""
Diagnose: Warum sind Findings leer?

This script directly tests:
1. Findings generation in _run_analysis_pipeline
2. Findings storage in app.analysis_results
3. Findings extraction in _render_results_ui
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
import customtkinter as ctk

# Create minimal app
root = ctk.CTk()
root.withdraw()  # Hide window

try:
    app = ProfessionelleUebersetzungsqualitaetsApp()
    print("\n" + "="*60)
    print("FINDINGS DIAGNOSIS TEST")
    print("="*60)
    
    # 1. Check initial app state
    print("\n1. Initial app.analysis_results:")
    print(f"   Type: {type(app.analysis_results)}")
    print(f"   Keys: {list(app.analysis_results.keys()) if isinstance(app.analysis_results, dict) else 'NOT A DICT'}")
    print(f"   findings count: {len(app.analysis_results.get('findings', []) or [])}")
    
    # 2. Create test data
    print("\n2. Creating test dataset...")
    test_files = [
        {
            'type': 'source_segment',
            'path': 'test_source.md',
            'content': 'This is a test segment. The quality is good.',
            'encoding': 'utf-8'
        },
        {
            'type': 'target_segment',
            'path': 'test_target.md',
            'content': 'Dies ist ein Testsegment. Die Qualität ist gut.',
            'encoding': 'utf-8'
        }
    ]
    
    # Create temp files
    import tempfile
    temp_dir = tempfile.mkdtemp()
    for f in test_files:
        fpath = os.path.join(temp_dir, f['path'])
        with open(fpath, 'w', encoding=f['encoding']) as fp:
            fp.write(f['content'])
    print(f"   Created temp dir: {temp_dir}")
    print(f"   Files: {[f['path'] for f in test_files]}")
    
    # 3. Run analysis
    print("\n3. Running analysis pipeline...")
    print("   (This generates findings)")
    
    # Mock the UI components that analysis might need
    app._main_container = ctk.CTkFrame(root)
    app._main_container.pack()
    
    # Run analysis using internal method
    results = app._run_analysis_pipeline(test_files)
    
    print(f"\n4. After _run_analysis_pipeline:")
    print(f"   Type: {type(results)}")
    print(f"   Keys: {list(results.keys()) if isinstance(results, dict) else 'NOT A DICT'}")
    
    if isinstance(results, dict):
        findings_in_results = results.get('findings', [])
        print(f"   findings in results: {len(findings_in_results)} items")
        if findings_in_results:
            print(f"   First finding: {findings_in_results[0]}")
        
        # Check other phase data
        p1 = results.get('issues_phase1', [])
        p2 = results.get('issues_phase2', [])
        p3 = results.get('issues_phase3', [])
        print(f"   issues_phase1: {len(p1)} items")
        print(f"   issues_phase2: {len(p2)} items")
        print(f"   issues_phase3: {len(p3)} items")
    
    # 5. Store in app and check again
    print("\n5. Storing in app.analysis_results...")
    app.analysis_results = results
    
    print(f"\n6. After storing in app.analysis_results:")
    findings_in_app = app.analysis_results.get('findings', [])
    print(f"   findings count: {len(findings_in_app)}")
    if findings_in_app:
        print(f"   First finding: {findings_in_app[0]}")
    else:
        print(f"   ⚠️  EMPTY!")
    
    # 6. Simulate what _render_results_ui does
    print("\n7. Simulating _render_results_ui extraction:")
    data = app.analysis_results
    findings = data.get('findings', []) if isinstance(data.get('findings'), list) else []
    print(f"   Extracted findings: {len(findings)}")
    print(f"   findings is list: {isinstance(findings, list)}")
    print(f"   findings bool: {bool(findings)}")
    
    if not findings:
        print(f"   → Aggregating from phase issues instead...")
        for phase_key in ('issues_phase1', 'issues_phase2', 'issues_phase3'):
            phase_issues = data.get(phase_key, [])
            if isinstance(phase_issues, list) and phase_issues:
                print(f"     Adding {len(phase_issues)} from {phase_key}")
                findings.extend(phase_issues)
        print(f"   → After aggregation: {len(findings)} findings")
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY:")
    print("="*60)
    print(f"✓ Analysis pipeline returned: {len(results.get('findings', []) or [])} findings")
    print(f"✓ App.analysis_results contains: {len(app.analysis_results.get('findings', []) or [])} findings")
    print(f"✓ UI extraction would see: {len(findings)} findings")
    
    if len(findings) == 0:
        print(f"\n⚠️  PROBLEM: No findings available to UI!")
        print(f"   - Check if analysis generated any findings")
        print(f"   - Check if phase issues are being created")
    else:
        print(f"\n✓ Findings should display correctly in UI")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\nCleaned up temp dir: {temp_dir}")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {e}")
    print(traceback.format_exc())
finally:
    root.destroy()
    print("\nDone.\n")
