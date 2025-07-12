#!/usr/bin/env python3
import sys
import os
import traceback

# Suppress the debug output by redirecting stdout temporarily
class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, *args):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

try:
    with SuppressOutput():
        from pruefung_workflow_controller import PruefungWorkflowController
        controller = PruefungWorkflowController()
    
    print("Controller imported and created successfully!")
    
    # Check methods
    methods = ['select_all_checks', 'clear_all_file_pairs', 'deselect_all_checks', 
               'start_checking_process', 'stop_checking_process', 'export_results_as_pdf']
    
    for method in methods:
        exists = hasattr(controller, method)
        print(f"{method}: {'✓' if exists else '✗'}")
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
