#!/usr/bin/env python3
"""
Test: DIRECT CALL to _set_mode('findings') to simulate click
"""
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'

import tempfile

try:
    from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
    import customtkinter as ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    print("\n" + "="*70)
    print("TEST: Direct call to _set_mode('findings')")
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
    
    # Create test files
    temp_dir = tempfile.mkdtemp(prefix='checker_setmode_')
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
    
    # Render the UI (this will call _set_mode('overview'))
    print("\nRendering UI...")
    from quality_gui_components_analysis_results import show_analysis_results
    show_analysis_results(app)
    
    print("\n" + "-"*70)
    print("Now the UI is rendered with Overview tab active.")
    print("-"*70)
    
    # Now we need to find the _set_mode function and call it with 'findings'
    # But _set_mode is defined INSIDE _render_results_ui, so we can't call it directly!
    # We would need to refactor to make it accessible from outside...
    
    print("\nProblem: _set_mode is defined inside _render_results_ui")
    print("and we cannot call it directly from outside!")
    print("\nThis means we cannot simulate the tab click without refactoring.")
    print("\nSolution: The UI SHOULD display findings when rendered, NOT wait for tab click")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    root.destroy()

except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    print(traceback.format_exc())
    root.destroy()
