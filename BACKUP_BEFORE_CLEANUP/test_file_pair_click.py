#!/usr/bin/env python3
"""
Quick test for file pair clicking functionality in the Prüfung workflow.
"""

import sys
sys.path.insert(0, '.')

import customtkinter as ctk
from pruefung_workflow_controller import PruefungWorkflowController
from ui_components.pruefung_workflow_view import PruefungWorkflowView
from ui_theme import UITheme

def test_file_pair_clicking():
    print("[TEST] Testing file pair clicking functionality...")
    
    # Create a test window
    root = ctk.CTk()
    root.geometry("800x600")
    root.title("File Pair Click Test")
    
    # Create controller with some test data
    test_project_data = {
        'kunde_name': 'Test Kunde',
        'auftragsnummer': 'TEST-001',
        'betreuer_name': 'Test Betreuer'
    }
    
    controller = PruefungWorkflowController(test_project_data)
    
    # Create view
    view = PruefungWorkflowView(root, controller, test_project_data)
    view.pack(fill="both", expand=True)
    controller.view = view
    
    # Add some test file pairs
    test_pairs = [
        {'id': 1, 'source_file': 'C:/test/source1.txt', 'target_file': 'C:/test/target1.txt'},
        {'id': 2, 'source_file': 'C:/test/source2.txt', 'target_file': 'C:/test/target2.txt'},
        {'id': 3, 'source_file': 'C:/test/source3.txt', 'target_file': 'C:/test/target3.txt'},
    ]
    
    # Manually add to controller
    for pair in test_pairs:
        controller.file_pairs[pair['id']] = pair
    
    # Update display
    view.update_file_pair_display(controller.file_pairs)
    
    print(f"[TEST] Added {len(test_pairs)} test file pairs")
    print("[TEST] Click on file pairs to test selection functionality")
    print("[TEST] Selected pairs should be highlighted with blue color")
    
    # Test selecting a file pair programmatically
    controller.select_file_pair(1)
    print(f"[TEST] Programmatically selected file pair 1")
    print(f"[TEST] Current selection: {controller.selected_file_pair_id}")
    
    root.mainloop()

if __name__ == "__main__":
    test_file_pair_clicking()
