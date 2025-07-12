#!/usr/bin/env python3
"""
Simple test to fix the button issue in pruefung_workflow.py
"""

import sys
import os
import tkinter as tk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from pruefung_workflow import PruefungWorkflow

def fix_button_issue():
    """Fix the button issue in PruefungWorkflow"""
    
    # Original file path
    file_path = os.path.join(os.path.dirname(__file__), "pruefung_workflow.py")
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find and fix the problematic create_start_button_fixed method
    if "def create_start_button_fixed(self):" in content:
        print("[FIX] Found create_start_button_fixed method")
        
        # Check if there's an incomplete for loop
        if "for widget in self.bottom_frame.winfo_children():" in content and \
           "            " in content:
            print("[FIX] Found incomplete for loop, fixing...")
            
            # Replace the method with the fixed version
            start_marker = "def create_start_button_fixed(self):"
            end_marker = "self.start_button.pack(pady=10, padx=30, side=\"left\")"
            
            start_idx = content.find(start_marker)
            if start_idx != -1:
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    end_idx += len(end_marker)
                    
                    # Original method code
                    original_method = content[start_idx:end_idx]
                    print(f"[DEBUG] Original method:\n{original_method}")
                    
                    # Fixed method code
                    fixed_method = '''def create_start_button_fixed(self):
        # Remove all existing buttons first
        for widget in self.bottom_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
                
        # Create the start button
        self.start_button = ctk.CTkButton(
            self.bottom_frame,
            text="🚀 Prüfung starten",
            command=self.on_start_check,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#0078D4",
            hover_color="#005A9E",
            text_color="white",
            height=48,
            corner_radius=12
        )
        self.start_button.pack(pady=10, padx=30, side="left")'''
                    
                    # Replace the method in the content
                    fixed_content = content[:start_idx] + fixed_method + content[end_idx:]
                    
                    # Backup the original file
                    backup_path = file_path + ".backup"
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[FIX] Original file backed up to {backup_path}")
                    
                    # Write the fixed content
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)
                    print(f"[FIX] File updated with fixed method")
                    return True
                else:
                    print("[ERROR] Could not find end of method")
            else:
                print("[ERROR] Could not find start of method")
        else:
            print("[INFO] No incomplete for loop found")
    else:
        print("[ERROR] Could not find create_start_button_fixed method")
    
    return False

if __name__ == "__main__":
    success = fix_button_issue()
    if success:
        print("\n[RESULT] ✓ Button fix applied successfully")
    else:
        print("\n[RESULT] ✗ Button fix failed")
