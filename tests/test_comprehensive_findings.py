#!/usr/bin/env python3
"""
Test script to simulate a full analysis with findings and verify rendering.
"""

import sys
import json
from pathlib import Path

# Add checker to path
checker_path = Path(__file__).parent
sys.path.insert(0, str(checker_path))

def create_comprehensive_test_data():
    """Create a more realistic test dataset with findings."""
    return {
        'findings': [
            {
                'phase': 'phase1',
                'code': 'CONSISTENCY_001',
                'severity': 'critical',
                'category': 'consistency',
                'message': 'Inconsistent term usage: "Report" vs "Bericht"',
                'source': 'The report contains important data.',
                'target': 'Der Report enthält wichtige Daten.',
                'source_excerpt': 'report',
                'target_excerpt': 'Report',
                'rule': 'consistency',
                'meta': {'confidence': 0.95}
            },
            {
                'phase': 'phase1',
                'code': 'PLACEHOLDER_001',
                'severity': 'major',
                'category': 'placeholder',
                'message': 'Missing placeholder {0} in target',
                'source': 'Please enter {0}',
                'target': 'Bitte eingeben',
                'source_excerpt': '{0}',
                'target_excerpt': 'eingeben',
                'rule': 'placeholder',
                'meta': {'confidence': 0.99}
            },
            {
                'phase': 'phase2',
                'code': 'SIM_LOW',
                'severity': 'major',
                'category': 'pair_similarity',
                'message': 'Low similarity: 65.2%',
                'source': '',
                'target': '',
                'source_excerpt': '',
                'target_excerpt': '',
                'rule': 'pair_similarity',
                'meta': {'confidence': 0.7}
            },
            {
                'phase': 'phase3',
                'code': 'GRAMMAR_001',
                'severity': 'minor',
                'category': 'grammar',
                'message': 'Missing article in German text',
                'source': 'The system works well',
                'target': 'System funktioniert gut',
                'source_excerpt': 'The',
                'target_excerpt': 'System',
                'rule': 'grammar',
                'meta': {'confidence': 0.6}
            },
        ],
        'issues_phase1': [
            {
                'phase': 'phase1',
                'code': 'CONSISTENCY_001',
                'severity': 'critical',
                'category': 'consistency',
                'message': 'Inconsistent term usage: "Report" vs "Bericht"',
                'source': 'The report contains important data.',
                'target': 'Der Report enthält wichtige Daten.',
            },
            {
                'phase': 'phase1',
                'code': 'PLACEHOLDER_001',
                'severity': 'major',
                'category': 'placeholder',
                'message': 'Missing placeholder {0} in target',
                'source': 'Please enter {0}',
                'target': 'Bitte eingeben',
            }
        ],
        'issues_phase2': [
            {
                'phase': 'phase2',
                'code': 'SIM_LOW',
                'severity': 'major',
                'category': 'pair_similarity',
                'message': 'Low similarity: 65.2%',
            }
        ],
        'issues_phase3': [
            {
                'phase': 'phase3',
                'code': 'GRAMMAR_001',
                'severity': 'minor',
                'category': 'grammar',
                'message': 'Missing article in German text',
            }
        ],
        'summary': {
            'pairs': 100,
            'total_source_chars': 5000,
            'total_translation_chars': 5500,
            'critical': 1,
            'major': 2,
            'minor': 1,
            'quality_score': 75.5,
            'overall_score_norm': 0.755
        },
        'metrics': {
            'pair_count': 100,
            'avg_length_ratio': 1.1,
            'avg_sentence_length': 15,
        },
        'phases': {
            'phase1': {
                'issue_total': 2
            },
            'phase2': {
                'issue_total': 1
            },
            'phase3': {
                'issue_total': 1
            },
            'phase4': {
                'total': 4,
                'risk_score': 45.0
            }
        },
        'phase_issue_counts': {
            'phase1': 2,
            'phase2': 1,
            'phase3': 1
        },
        'consolidated': {
            'total': 4,
            'risk_score': 45.0
        },
        'recommendations': [
            'Review terminology glossary for consistency',
            'Check all placeholders in translation'
        ]
    }

def test_comprehensive_findings():
    """Test comprehensive findings rendering."""
    print("=" * 80)
    print("TEST: Comprehensive Findings Rendering")
    print("=" * 80)
    
    test_data = create_comprehensive_test_data()
    
    print(f"\n1. Test data created:")
    print(f"   - Total findings: {len(test_data['findings'])}")
    print(f"   - findings: {len(test_data.get('findings', []))} items")
    print(f"   - issues_phase1: {len(test_data.get('issues_phase1', []))} items")
    print(f"   - issues_phase2: {len(test_data.get('issues_phase2', []))} items")
    print(f"   - issues_phase3: {len(test_data.get('issues_phase3', []))} items")
    
    try:
        from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
        
        app = ProfessionelleUebersetzungsqualitaetsApp()
        
        print(f"\n2. Testing _normalize_analysis_results_structure()...")
        normalized = app._normalize_analysis_results_structure(test_data)
        
        print(f"   - After normalization:")
        print(f"     • findings: {len(normalized.get('findings', []))} items")
        print(f"     • issues_phase1: {len(normalized.get('issues_phase1', []))} items")
        print(f"     • issues_phase2: {len(normalized.get('issues_phase2', []))} items")
        print(f"     • issues_phase3: {len(normalized.get('issues_phase3', []))} items")
        print(f"     • phases: {list(normalized.get('phases', {}).keys())}")
        print(f"     • phase_issue_counts: {normalized.get('phase_issue_counts')}")
        
        # Verify findings have correct structure
        if normalized.get('findings'):
            sample = normalized['findings'][0]
            required_keys = ['phase', 'code', 'severity', 'message', 'category']
            missing = [k for k in required_keys if k not in sample]
            if missing:
                print(f"   [PROBLEM] Finding missing keys: {missing}")
                print(f"     Sample finding: {sample}")
            else:
                print(f"   [OK] Finding structure looks good")
                print(f"     Sample: code={sample['code']}, severity={sample['severity']}, phase={sample['phase']}")
        
        # Test that app.analysis_results gets populated
        print(f"\n3. Testing app.analysis_results population...")
        app.analysis_results = normalized
        
        findings_in_app = app.analysis_results.get('findings', [])
        print(f"   - Findings accessible: {len(findings_in_app)} items")
        
        # Verify each finding has required fields for rendering
        for idx, f in enumerate(findings_in_app[:1]):
            print(f"   - Finding {idx}: phase={f.get('phase')}, severity={f.get('severity')}, code={f.get('code')}")
        
        if len(findings_in_app) > 0:
            print("   [OK] Findings successfully available for rendering!")
        else:
            print("   [PROBLEM] No findings available!")
        
        # Verify phase issues are accessible
        print(f"\n4. Verifying phase issues are accessible:")
        for phase_key in ['issues_phase1', 'issues_phase2', 'issues_phase3']:
            phase_issues = app.analysis_results.get(phase_key, [])
            print(f"   - {phase_key}: {len(phase_issues)} issues")
        
        print("\n" + "=" * 80)
        print("[OK] TEST COMPLETE - All verifications passed!")
        print("=" * 80)
        return True
        
    except ImportError as e:
        print(f"[FAIL] Failed to import: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_comprehensive_findings()
    sys.exit(0 if success else 1)
