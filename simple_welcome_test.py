#!/usr/bin/env python3
"""Simple test for direct welcome screen."""

import customtkinter as ctk

class SimpleWelcomeTest:
    def __init__(self):
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create root window
        self.root = ctk.CTk()
        self.root.title("Simple Welcome Test")
        self.root.geometry("800x600")
        self.root.configure(fg_color="#E0E0E0")
        
        # Create main frame with bright colors
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=3,
            border_color="#FF0000"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Large title
        title = ctk.CTkLabel(
            main_frame,
            text="🏠 WILLKOMMEN BEI CHECKER PRO SUITE",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#000000",
            fg_color="#FFFF00"
        )
        title.pack(pady=30)
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Diese Anzeige sollte VOLLSTÄNDIG SICHTBAR sein!\nWenn Sie diesen Text sehen, funktioniert die GUI.",
            font=ctk.CTkFont(size=16),
            text_color="#333333"
        )
        subtitle.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        btn1 = ctk.CTkButton(
            button_frame,
            text="📁 Neues Projekt",
            height=50,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6"
        )
        btn1.pack(side="left", padx=10)
        
        btn2 = ctk.CTkButton(
            button_frame,
            text="📤 Upload",
            height=50,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981"
        )
        btn2.pack(side="left", padx=10)
        
        btn3 = ctk.CTkButton(
            button_frame,
            text="⚙️ Workflows", 
            height=50,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8B5CF6"
        )
        btn3.pack(side="left", padx=10)
        
        # Status
        status = ctk.CTkLabel(
            main_frame,
            text="✅ System Ready • Alle Komponenten geladen",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#059669",
            fg_color="#F0FDF4"
        )
        status.pack(pady=20)
        
        print("✅ Simple welcome screen created")
        
    def run(self):
        print("🚀 Starting simple welcome test...")
        self.root.mainloop()

if __name__ == "__main__":
    test = SimpleWelcomeTest()
    test.run()
