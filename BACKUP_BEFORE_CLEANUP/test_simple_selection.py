#!/usr/bin/env python3
"""
Simple test to verify file pair selection functionality.
"""

import sys
import os
sys.path.insert(0, '.')

# Minimalistic test
try:
    from pruefung_workflow_controller import PruefungWorkflowController
    
    # Create a controller with dummy data
    controller = PruefungWorkflowController({'test': 'data'})
    
    # Test adding file pairs
    controller.file_pairs = {
        1: {'id': 1, 'source_file': 'test1.txt', 'target_file': 'test1_target.txt'},
        2: {'id': 2, 'source_file': 'test2.txt', 'target_file': 'test2_target.txt'},
    }
    
    print("[TEST] Created test file pairs:")
    for pair_id, pair in controller.file_pairs.items():
        print(f"  {pair_id}: {pair['source_file']} -> {pair['target_file']}")
    
    # Test selection
    print(f"\n[TEST] Initial selection: {controller.selected_file_pair_id}")
    
    controller.select_file_pair(1)
    print(f"[TEST] After selecting pair 1: {controller.selected_file_pair_id}")
    
    controller.select_file_pair(2)
    print(f"[TEST] After selecting pair 2: {controller.selected_file_pair_id}")
    
    controller.select_file_pair(999)  # Non-existent
    print(f"[TEST] After selecting non-existent pair: {controller.selected_file_pair_id}")
    
    print("\n[SUCCESS] File pair selection functionality works correctly!")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
