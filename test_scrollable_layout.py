#!/usr/bin/env python3
"""Layout debug test for workflow section"""

import customtkinter as ctk
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from ui_theme import UITheme

def create_test_app():
    """Create a test application to debug the workflow section layout"""
    app = ctk.CTk()
    app.title("Workflow Section Layout Debug")
    app.geometry("800x600")
    
    # Create a test frame
    main_frame = ctk.CTkFrame(app, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Test 1: Regular frame with workflow cards
    test1_frame = ctk.CTkFrame(main_frame, fg_color=UITheme.COLOR_SURFACE)
    test1_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    test1_label = ctk.CTkLabel(test1_frame, text="Test 1: Regular Frame", font=ctk.CTkFont(size=16, weight="bold"))
    test1_label.pack(pady=10)
    
    # Add some workflow cards manually
    for i in range(4):
        card = ctk.CTkFrame(test1_frame, fg_color=UITheme.COLOR_CARD, height=80)
        card.pack(fill="x", pady=5, padx=10)
        card.pack_propagate(False)
        
        label = ctk.CTkLabel(card, text=f"Workflow {i+1}", font=ctk.CTkFont(size=14))
        label.pack(pady=20)
    
    # Test 2: ScrollableFrame with workflow cards
    test2_frame = ctk.CTkFrame(main_frame, fg_color=UITheme.COLOR_SURFACE)
    test2_frame.pack(fill="both", expand=True)
    
    test2_label = ctk.CTkLabel(test2_frame, text="Test 2: ScrollableFrame", font=ctk.CTkFont(size=16, weight="bold"))
    test2_label.pack(pady=10)
    
    scrollable_frame = ctk.CTkScrollableFrame(test2_frame, height=200)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    scrollable_frame.grid_columnconfigure(0, weight=1)
    
    # Add some workflow cards with grid layout
    for i in range(4):
        card = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_CARD, height=80)
        card.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
        card.grid_propagate(False)
        
        label = ctk.CTkLabel(card, text=f"Workflow {i+1}", font=ctk.CTkFont(size=14))
        label.pack(pady=20)
    
    print("✓ Test app created - you should see 4 workflow cards in each section")
    print("✓ If you only see 1 card in the ScrollableFrame, that's the issue!")
    
    app.mainloop()

if __name__ == "__main__":
    create_test_app()
