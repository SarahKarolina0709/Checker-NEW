#!/usr/bin/env python3
"""
Simple test script to verify button functionality in Prüfungs-Workflow
"""

import sys
import os
import tkinter as tk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from pruefung_workflow import PruefungWorkflow

# Create a simple test application
root = ctk.CTk()
root.title("Button Test")
root.geometry("800x600")

# Create a text widget for logging
log_text = ctk.CTkTextbox(root, height=400, width=700)
log_text.pack(padx=20, pady=20)

def log(message):
    log_text.insert(ctk.END, message + "\n")
    log_text.see(ctk.END)
    print(message)

# Create a wrapper for the back callback
def dummy_back_callback():
    log("[TEST] Back callback called")

# Create the workflow instance
log("[TEST] Creating PruefungWorkflow instance...")
workflow = PruefungWorkflow(root, back_callback=dummy_back_callback)

# Create test files
log("[TEST] Preparing test files...")
test_file_a = os.path.join(os.path.dirname(__file__), "test_file_a.txt")
test_file_b = os.path.join(os.path.dirname(__file__), "test_file_b.txt")

# Set test files in workflow
workflow.text_a_file = test_file_a
workflow.text_b_file = test_file_b
log(f"[TEST] Test files set: {test_file_a}, {test_file_b}")

# Test button existence
log("[TEST] Testing button existence...")
if hasattr(workflow, 'start_button'):
    log(f"[TEST] ✓ start_button exists")
    try:
        button_cmd = workflow.start_button.cget('command')
        log(f"[TEST] ✓ Button command points to: {button_cmd.__name__}")
    except Exception as e:
        log(f"[TEST] Warning: Could not get button command: {e}")
else:
    log("[TEST] ✗ start_button not found!")

# Test on_start_check method
log("[TEST] Testing on_start_check method...")
if hasattr(workflow, 'on_start_check'):
    log("[TEST] ✓ on_start_check method exists")
else:
    log("[TEST] ✗ on_start_check method not found!")

# Add a button to manually trigger on_start_check
def test_on_start_check():
    log("[TEST] Manually calling on_start_check...")
    try:
        workflow.on_start_check()
        log("[TEST] ✓ on_start_check executed successfully")
    except Exception as e:
        log(f"[TEST] ✗ Error calling on_start_check: {e}")
        import traceback
        log(traceback.format_exc())

test_button = ctk.CTkButton(root, text="Test on_start_check", command=test_on_start_check)
test_button.pack(pady=10)

# Add a button to close the test
def close_test():
    log("[TEST] Test completed.")
    root.destroy()

close_button = ctk.CTkButton(root, text="Close Test", command=close_test)
close_button.pack(pady=10)

# Start the application
log("[TEST] Test application started. Click 'Test on_start_check' to test the method.")
root.mainloop()
