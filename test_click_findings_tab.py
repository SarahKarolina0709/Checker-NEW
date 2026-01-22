#!/usr/bin/env python3
"""
Test: Click on 'Befunde' tab and capture debug output
"""
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'

import tempfile
import threading
import time

try:
    from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
    import customtkinter as ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    print("\n" + "="*70)
    print("TEST: Click Befunde Tab and Render")
    print("="*70)
    
    # Create app
    app = ProfessionelleUebersetzungsqualitaetsApp()
    
    # Setup UI components
    if not hasattr(app, 'root'):
        app.root = root
    if not hasattr(app, '_main_container'):
        app._main_container = ctk.CTkFrame(root)
        app._main_container.pack(fill='both', expand=True)
    
    # Create output frame
    app.output_frame = ctk.CTkFrame(app._main_container, fg_color=app.get_color('transparent'))
    app.output_frame.pack(fill='both', expand=True)
    
    # Create test files with GOOD translation (should have fewer findings)
    temp_dir = tempfile.mkdtemp(prefix='checker_click_')
    source_md = temp_dir + "/source.md"
    target_md = temp_dir + "/target.md"
    
    with open(source_md, 'w', encoding='utf-8') as f:
        f.write("Hello World")
    
    with open(target_md, 'w', encoding='utf-8') as f:
        f.write("Hallo Welt")
    
    print(f"Created test files in {temp_dir}")
    
    # Run analysis
    print("\nRunning analysis...")
    files = [
        {'type': 'source_segment', 'path': source_md, 'content': open(source_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
        {'type': 'target_segment', 'path': target_md, 'content': open(target_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
    ]
    
    results = app._run_analysis_pipeline(files, rule_profile='default')
    normalized = app._normalize_analysis_results_structure(results)
    app.analysis_results = normalized
    
    print(f"Analysis complete: {len(app.analysis_results.get('findings', []))} findings")
    
    # Now render the UI
    print("\nRendering UI...")
    from quality_gui_components_analysis_results import _render_results_ui
    _render_results_ui(app)
    
    print("\n" + "="*70)
    print("RENDERING COMPLETE")
    print("="*70)
    print("\nThe app UI has been rendered.")
    print("In a real app, you would click on the 'Befunde' button to switch tabs.")
    print("\nCheck the debug output above for 'DEBUG _render_findings' messages.")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    root.destroy()

except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    print(traceback.format_exc())
    root.destroy()
