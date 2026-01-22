#!/usr/bin/env python3
"""
Simple test script to verify findings data flow through the analysis pipeline.
"""

import sys
import json
from pathlib import Path

# Add checker to path
checker_path = Path(__file__).parent
sys.path.insert(0, str(checker_path))

def test_data_flow():
    """Test that findings flow correctly through the analysis pipeline."""
    print("=" * 80)
    print("TEST: Findings Data Flow")
    print("=" * 80)
    
    # Create a minimal mock analysis result
    test_analysis_result = {
        'findings': [
            {
                'phase': 'phase1',
                'code': 'TEST1',
                'severity': 'major',
                'category': 'test_category',
                'message': 'This is a test finding',
                'source': 'Test source text',
                'target': 'Test target text',
                'source_excerpt': 'Test source text',
                'target_excerpt': 'Test target text',
            }
        ],
        'issues_phase1': [
            {
                'phase': 'phase1',
                'code': 'PHASE1_TEST',
                'severity': 'critical',
                'category': 'test_phase1',
                'message': 'Phase 1 test finding',
                'source': 'Source',
                'target': 'Target',
            }
        ],
        'issues_phase2': [],
        'issues_phase3': [],
        'summary': {'test': 'value'},
        'metrics': {'pair_count': 1},
        'phases': {},
        'phase_issue_counts': {'phase1': 1, 'phase2': 0, 'phase3': 0}
    }
    
    print(f"\n1. Initial test data:")
    print(f"   - findings: {len(test_analysis_result['findings'])} items")
    print(f"   - issues_phase1: {len(test_analysis_result['issues_phase1'])} items")
    print(f"   - issues_phase2: {len(test_analysis_result['issues_phase2'])} items")
    print(f"   - issues_phase3: {len(test_analysis_result['issues_phase3'])} items")
    
    # Now test the normalize function
    try:
        from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
        
        # Create a minimal app instance
        app = ProfessionelleUebersetzungsqualitaetsApp()
        
        print(f"\n2. Testing _normalize_analysis_results_structure()...")
        normalized = app._normalize_analysis_results_structure(test_analysis_result)
        
        print(f"   - Normalized findings: {len(normalized.get('findings', []))} items")
        if normalized.get('findings'):
            print(f"   - First finding: {normalized['findings'][0]}")
        print(f"   - issues_phase1: {len(normalized.get('issues_phase1', []))} items")
        print(f"   - issues_phase2: {len(normalized.get('issues_phase2', []))} items")
        print(f"   - issues_phase3: {len(normalized.get('issues_phase3', []))} items")
        
        # Verify that findings were populated
        assert len(normalized.get('findings', [])) > 0, "Findings should not be empty after normalization!"
        print("\n✓ Findings are populated correctly!")
        
        # Test that the rendering functions can access this
        print(f"\n3. Testing that findings reach the UI renderer...")
        print(f"   - Simulating app.analysis_results = normalized")
        app.analysis_results = normalized
        
        findings_in_app = app.analysis_results.get('findings', [])
        print(f"   - Findings accessible from app.analysis_results: {len(findings_in_app)} items")
        
        if len(findings_in_app) > 0:
            print("✓ Findings successfully flow through to app.analysis_results!")
        else:
            print("✗ PROBLEM: Findings are empty when accessed from app.analysis_results!")
            
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
    except ImportError as e:
        print(f"✗ Failed to import QualityGUIApp: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_data_flow()
    sys.exit(0 if success else 1)
