#!/usr/bin/env python3
"""
Quick fix script for file pair clicking functionality.
This script patches the existing controller to add file pair selection.
"""

import sys
import os

# Read the current controller file
controller_file = "pruefung_workflow_controller.py"

# Define the patches we need to make
patches = [
    # Fix 1: Ensure all update_file_pair_display calls use list(self.file_pairs.values())
    ('self.view.update_file_pair_display(self.file_pairs)', 'self.view.update_file_pair_display(list(self.file_pairs.values()))'),
    
    # Fix 2: Add missing import if needed
    # This will be handled by checking imports
]

print("[PATCH] Applying quick fixes to enable file pair clicking...")

# Read the file
try:
    with open(controller_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply patches
    for old, new in patches:
        if old in content:
            content = content.replace(old, new)
            print(f"[PATCH] Applied: {old[:50]}... -> {new[:50]}...")
    
    # Check if selected_file_pair_id is defined
    if 'self.selected_file_pair_id = None' not in content:
        # Find the file_pairs initialization and add the selection tracking
        if 'self.file_pairs = {}' in content:
            content = content.replace(
                'self.file_pairs = {}',
                'self.file_pairs = {}\n        self.selected_file_pair_id = None  # Track currently selected file pair'
            )
            print("[PATCH] Added selected_file_pair_id tracking")
    
    # Check if select_file_pair method exists
    if 'def select_file_pair(self, pair_id):' not in content:
        # Find a good place to insert the method (after clear_all_file_pairs)
        method_to_add = '''
    def select_file_pair(self, pair_id):
        """Select a file pair for display/interaction."""
        if pair_id in self.file_pairs:
            self.selected_file_pair_id = pair_id
            print(f"[DEBUG] Selected file pair {pair_id}: {self.file_pairs[pair_id]}")
            if self.view:
                # Refresh the file pair display to show selection
                self.view.update_file_pair_display(list(self.file_pairs.values()))
                # Optionally show details of the selected pair
                self._show_file_pair_details(pair_id)
        else:
            print(f"[WARNING] File pair {pair_id} not found")

    def _show_file_pair_details(self, pair_id):
        """Show details of the selected file pair (optional enhancement)."""
        if pair_id in self.file_pairs:
            pair = self.file_pairs[pair_id]
            print(f"[INFO] File pair details:")
            print(f"  Source: {pair.get('source_file', pair.get('source_path', 'Unknown'))}")
            print(f"  Target: {pair.get('target_file', pair.get('target_path', 'Unknown'))}")
            # Here you could update a details panel in the UI if desired
'''
        
        # Insert before the run_checks method or at the end of class
        if 'def run_checks(self, pair_id, check_ids=None):' in content:
            content = content.replace(
                'def run_checks(self, pair_id, check_ids=None):',
                method_to_add + '\n    def run_checks(self, pair_id, check_ids=None):'
            )
            print("[PATCH] Added select_file_pair method")
        else:
            # Just append at the end before the last lines
            lines = content.split('\n')
            insert_point = len(lines) - 5  # Insert 5 lines from the end
            lines.insert(insert_point, method_to_add)
            content = '\n'.join(lines)
            print("[PATCH] Added select_file_pair method at end")
    
    # Write the patched content back
    with open(controller_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[PATCH] File patched successfully!")
    print("[PATCH] The file pair clicking functionality should now work.")
    
except Exception as e:
    print(f"[ERROR] Failed to patch file: {e}")
    import traceback
    traceback.print_exc()
