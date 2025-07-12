#!/usr/bin/env python3
"""
Cleaner version of the file pair management methods.
"""

# Clean versions of the problematic methods for copy-paste fix

def add_file_pair(self):
    """Add a new file pair to the workflow."""
    from tkinter import filedialog, messagebox
    
    source_file = filedialog.askopenfilename(title="Quelldatei auswählen", filetypes=[("Alle Dateien", "*.*")])
    if not source_file:
        return
    
    target_file = filedialog.askopenfilename(title="Zieldatei auswählen", filetypes=[("Alle Dateien", "*.*")])
    if not target_file:
        return
    
    pair_id = self.next_file_pair_id
    self.file_pairs[pair_id] = {
        "id": pair_id,
        "source_file": source_file,
        "target_file": target_file,
        "source_name": os.path.basename(source_file),
        "target_name": os.path.basename(target_file),
        "checks_running": False,
        "results": {}
    }
    self.next_file_pair_id += 1
    
    if self.view:
        self.view.update_file_pair_display(list(self.file_pairs.values()))

def remove_file_pair(self, pair_id):
    if pair_id in self.file_pairs:
        del self.file_pairs[pair_id]
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))

def clear_all_file_pairs(self):
    """Clear all file pairs from the workflow."""
    self.file_pairs.clear()
    self.next_file_pair_id = 1
    self.selected_file_pair_id = None  # Clear selection when clearing all pairs
    if self.view:
        self.view.update_file_pair_display(list(self.file_pairs.values()))
        # Also clear any results
        self.view.clear_all_results()

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
        print(f"  Source: {pair['source_file']}")
        print(f"  Target: {pair['target_file']}")
        # Here you could update a details panel in the UI if desired
