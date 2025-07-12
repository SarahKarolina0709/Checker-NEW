#!/usr/bin/env python3
"""
Test script to verify the improved premium animations.
Tests the refined animation engine with elegant, smooth effects.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from animation_engine import animation_engine
from ui_theme import UITheme
import time

class PremiumAnimationTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Premium Animation Test")
        self.root.geometry("800x600")
        self.root.configure(fg_color=UITheme.COLOR_BACKGROUND)
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        
        self.create_test_widgets()
        
    def create_test_widgets(self):
        """Create test widgets to demonstrate improved animations."""
        
        # Main container
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Premium Animation Engine Test",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title.pack(pady=(20, 30))
        
        # Test card 1 - Workflow-style card
        card1 = self.create_test_card(
            main_frame, 
            "Elegant Workflow Card",
            "Smooth hover effects with scale and glow",
            UITheme.COLOR_WORKFLOW_ANGEBOTS,
            "#E3F2FD"
        )
        card1.pack(fill="x", padx=40, pady=10)
        
        # Test card 2 - Different color scheme
        card2 = self.create_test_card(
            main_frame,
            "Premium Animation Card", 
            "Refined effects for better visual appeal",
            UITheme.COLOR_WORKFLOW_PRUEFUNG,
            "#E8F5E8"
        )
        card2.pack(fill="x", padx=40, pady=10)
        
        # Test buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=20)
        
        test_btn1 = ctk.CTkButton(
            button_frame,
            text="Test Button 1",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            fg_color=UITheme.COLOR_WORKFLOW_ANGEBOTS,
            hover_color="#0056b3",
            corner_radius=UITheme.CORNER_RADIUS,
            height=40
        )
        test_btn1.pack(side="left", padx=(0, 10))
        self.add_premium_button_effects(test_btn1, UITheme.COLOR_WORKFLOW_ANGEBOTS)
        
        test_btn2 = ctk.CTkButton(
            button_frame,
            text="Test Button 2",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            fg_color=UITheme.COLOR_WORKFLOW_FINALISIERUNG,
            hover_color="#e0a800",
            corner_radius=UITheme.CORNER_RADIUS,
            height=40
        )
        test_btn2.pack(side="left", padx=(0, 10))
        self.add_premium_button_effects(test_btn2, UITheme.COLOR_WORKFLOW_FINALISIERUNG)
        
        # Add entrance animations to cards
        self.add_entrance_animations([card1, card2])
        
    def create_test_card(self, parent, title_text, desc_text, primary_color, light_color):
        """Create a test card with premium animations."""
        card = ctk.CTkFrame(
            parent,
            fg_color=light_color,
            border_width=2,
            border_color=primary_color,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=80
        )
        card.grid_columnconfigure(1, weight=1)
        card.grid_propagate(False)
        
        # Icon area
        icon_bg = ctk.CTkFrame(
            card,
            fg_color=primary_color,
            corner_radius=UITheme.CORNER_RADIUS,
            width=50,
            height=50
        )
        icon_bg.grid(row=0, column=0, rowspan=2, sticky="w", padx=15, pady=15)
        
        # Icon emoji
        icon_label = ctk.CTkLabel(
            icon_bg,
            text="✨",
            font=ctk.CTkFont(size=24),
            text_color="white"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            card,
            text=title_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
            text_color=primary_color,
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="ew", padx=(15, 10), pady=(15, 5))
        
        # Description
        desc = ctk.CTkLabel(
            card,
            text=desc_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        desc.grid(row=1, column=1, sticky="nw", padx=(15, 10), pady=(0, 15))
        
        # Add hover effects
        self.add_premium_card_effects(card, primary_color, light_color)
        
        return card
    
    def add_premium_card_effects(self, card, primary_color, light_color):
        """Add premium hover effects to a card."""
        base_colors = {"fg_color": light_color, "border_color": primary_color}
        hover_colors = {"fg_color": "#FFFFFF", "border_color": "#666666"}
        
        card._is_hovered = False
        
        def on_enter(event):
            if card._is_hovered:
                return
            card._is_hovered = True
            
            card.configure(cursor="hand2")
            
            # Premium hover transition
            animation_engine.animate_premium_hover_transition(
                card, base_colors, hover_colors, scale_factor=1.02, duration=250
            )
            
            # Subtle glow pulse
            card.after(100, lambda: animation_engine.animate_subtle_glow_pulse(
                card, "#FFFFFF", "#F0F8FF", duration=2000, intensity=0.15
            ))
            
        def on_leave(event):
            if not card._is_hovered:
                return
            card._is_hovered = False
            
            card.configure(cursor="")\n            
            # Smooth return
            animation_engine.animate_premium_hover_transition(
                card, hover_colors, base_colors, scale_factor=1.0, duration=300
            )
        
        def on_click(event):
            # Premium click effect
            animation_engine.animate_premium_click_effect(
                card, flash_color="#FFD700", scale_factor=1.05, duration=200
            )
        
        def bind_recursive(widget):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            for child in widget.winfo_children():
                try:
                    bind_recursive(child)
                except:
                    pass
        
        bind_recursive(card)
    
    def add_premium_button_effects(self, button, primary_color):
        """Add premium button effects."""
        button._is_hovered = False
        
        def on_enter(event):
            if button._is_hovered:
                return
            button._is_hovered = True
            
            button.configure(cursor="hand2")
            animation_engine.animate_scale_smooth(button, scale_factor=1.05, duration=200)
            animation_engine.animate_subtle_glow_pulse(
                button, primary_color, "#FFD700", duration=2000, intensity=0.2
            )
            
        def on_leave(event):
            if not button._is_hovered:
                return
            button._is_hovered = False
            
            button.configure(cursor="")
            animation_engine.animate_scale_smooth(button, scale_factor=1.0, duration=250)
        
        def on_click(event):
            if button._is_hovered:
                animation_engine.animate_premium_click_effect(
                    button, flash_color="#FFFFFF", scale_factor=1.12, duration=150
                )
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_click)
    
    def add_entrance_animations(self, cards):
        """Add elegant entrance animations to cards."""
        for i, card in enumerate(cards):
            delay = i * 150  # Stagger timing
            animation_engine.animate_smooth_entrance(
                card, from_scale=0.9, to_scale=1.0, duration=500, delay=delay
            )
    
    def run(self):
        """Run the test application."""
        print("🎨 Starting Premium Animation Test...")
        print("✨ Hover over cards and buttons to see improved animations")
        print("🖱️  Click on elements to see premium click effects")
        self.root.mainloop()

if __name__ == "__main__":
    test_app = PremiumAnimationTest()
    test_app.run()
