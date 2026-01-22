#!/usr/bin/env python3
"""
Test: FULL FLOW - From Analysis to UI Rendering
Tests if findings make it all the way to the UI
"""
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Mock the UI rendering to capture what would be displayed
findings_displayed = []

def mock_ctk_label(parent, text, **kwargs):
    """Mock CTkLabel to capture text that would be displayed"""
    class MockLabel:
        def __init__(self, text):
            self.text = text
        def pack(self, **kwargs):
            findings_displayed.append(self.text)
            print(f"[UI] Would display: {self.text}")
    return MockLabel(text)

def mock_ctk_frame(parent, **kwargs):
    """Mock CTkFrame"""
    class MockFrame:
        def __init__(self):
            self.children = []
        def pack(self, **kwargs):
            pass
        def configure(self, **kwargs):
            pass
    return MockFrame()

# Patch CTkinter before importing the app
import customtkinter as ctk
original_label = ctk.CTkLabel
original_frame = ctk.CTkFrame

try:
    # Now test
    from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
    import tempfile
    import json
    
    # Create root
    root = ctk.CTk()
    root.withdraw()
    
    print("\n" + "="*70)
    print("FULL FLOW TEST: Analysis to UI Rendering")
    print("="*70)
    
    # Create app
    print("\n1. Creating app...")
    app = ProfessionelleUebersetzungsqualitaetsApp()
    
    # Create test files
    temp_dir = tempfile.mkdtemp(prefix='checker_fullflow_')
    source_md = temp_dir + "/source.md"
    with open(source_md, 'w', encoding='utf-8') as f:
        f.write("English text. This is a test.")
    
    target_md = temp_dir + "/target.md"
    with open(target_md, 'w', encoding='utf-8') as f:
        f.write("Deutscher Text. Das ist ein Test.")
    
    print(f"2. Created test files in {temp_dir}")
    
    # Run analysis
    print("\n3. Running analysis pipeline...")
    files = [
        {'type': 'source_segment', 'path': source_md, 'content': open(source_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
        {'type': 'target_segment', 'path': target_md, 'content': open(target_md, encoding='utf-8').read(), 'encoding': 'utf-8'},
    ]
    
    results_from_pipeline = app._run_analysis_pipeline(files, rule_profile='default')
    print(f"   Pipeline returned: {len(results_from_pipeline.get('findings', []))} findings")
    
    # Normalize (as happens in run_quality_checks)
    print("\n4. Normalizing results (as done in run_quality_checks)...")
    normalized_results = app._normalize_analysis_results_structure(results_from_pipeline)
    print(f"   After normalization: {len(normalized_results.get('findings', []))} findings")
    
    # Store in app (as happens in run_quality_checks)
    print("\n5. Storing in app.analysis_results...")
    app.analysis_results = normalized_results
    print(f"   app.analysis_results has {len(app.analysis_results.get('findings', []))} findings")
    
    # Now simulate UI rendering
    print("\n6. Simulating _render_results_ui call (as done by show_analysis_results)...")
    
    # Import the renderer
    from quality_gui_components_analysis_results import _render_results_ui
    
    # This will try to use CTk, so we need to mock it or use real CTk
    # Let's use real CTk for now
    
    # The renderer expects certain app properties
    if not hasattr(app, 'root'):
        app.root = root
    if not hasattr(app, '_main_container'):
        app._main_container = ctk.CTkFrame(root)
    
    # Create a container for the renderer output
    test_container = ctk.CTkFrame(app._main_container)
    
    # Call the renderer
    print("   Calling _render_results_ui(app)...")
    try:
        _render_results_ui(app)
        print("   _render_results_ui completed successfully!")
    except Exception as e:
        print(f"   ERROR in _render_results_ui: {e}")
        import traceback
        traceback.print_exc()
    
    # Check the app state
    print("\n7. Final status check:")
    print(f"   app.analysis_results type: {type(app.analysis_results)}")
    print(f"   app.analysis_results has findings key: {'findings' in app.analysis_results}")
    findings_count = len(app.analysis_results.get('findings', []))
    print(f"   findings count: {findings_count}")
    
    if findings_count > 0:
        print(f"\nSUCCESS: Findings made it to app.analysis_results")
        print(f"  First finding: {app.analysis_results['findings'][0].get('message', 'N/A')}")
    else:
        print(f"\nPROBLEM: No findings in app.analysis_results!")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    root.destroy()
    
    print("\n" + "="*70)
    
except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    print(traceback.format_exc())
    root.destroy()
