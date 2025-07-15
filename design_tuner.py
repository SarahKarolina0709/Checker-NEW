"""
Design Tuner - Interaktive Anpassung der GUI-Farben
"""
import customtkinter as ctk
import json
from pathlib import Path

class DesignTuner:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Checker Design Tuner")
        self.root.geometry("800x600")
        
        # Current design settings
        self.current_colors = {
            "primary": "#2563EB",
            "success": "#059669",
            "neutral": "#64748B",
            "background": "#F8FAFC",
            "card_bg": "#FFFFFF",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "border": "#E2E8F0"
        }
        
        self.create_interface()
        
    def create_interface(self):
        """Create the tuning interface."""
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Checker Design Tuner",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#0F172A"
        )
        title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Passen Sie die Farben der GUI nach Ihren Wünschen an",
            font=ctk.CTkFont(size=14),
            text_color="#475569"
        )
        subtitle.pack(pady=(0, 30))
        
        # Color controls frame
        controls_frame = ctk.CTkFrame(main_frame, fg_color="#F8FAFC")
        controls_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Color categories
        categories = [
            ("Primärfarbe (Buttons)", "primary"),
            ("Erfolgsfarbe (Upload)", "success"),
            ("Neutrale Farbe (Navigation)", "neutral"),
            ("Hintergrund", "background"),
            ("Kartenfarbe", "card_bg"),
            ("Haupttext", "text_primary"),
            ("Sekundärtext", "text_secondary"),
            ("Rahmenfarbe", "border")
        ]
        
        self.color_vars = {}
        self.preview_frames = {}
        
        for i, (label, key) in enumerate(categories):
            row = i // 2
            col = i % 2
            
            # Color control frame
            color_frame = ctk.CTkFrame(controls_frame, fg_color="#FFFFFF")
            color_frame.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
            controls_frame.grid_columnconfigure(col, weight=1)
            
            # Label
            color_label = ctk.CTkLabel(
                color_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            color_label.pack(pady=(10, 5))
            
            # Color entry
            self.color_vars[key] = ctk.StringVar(value=self.current_colors[key])
            color_entry = ctk.CTkEntry(
                color_frame,
                textvariable=self.color_vars[key],
                width=120
            )
            color_entry.pack(pady=5)
            
            # Preview frame
            preview_frame = ctk.CTkFrame(
                color_frame,
                width=100,
                height=30,
                fg_color=self.current_colors[key],
                corner_radius=5
            )
            preview_frame.pack(pady=(5, 10))
            self.preview_frames[key] = preview_frame
            
            # Update preview on change
            color_entry.bind("<KeyRelease>", lambda e, k=key: self.update_preview(k))
        
        # Control buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20)
        
        # Preview button
        preview_btn = ctk.CTkButton(
            button_frame,
            text="Vorschau anzeigen",
            command=self.show_preview,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        preview_btn.pack(side="left", padx=(0, 10))
        
        # Apply button
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Änderungen anwenden",
            command=self.apply_changes,
            fg_color="#059669",
            hover_color="#047857"
        )
        apply_btn.pack(side="left", padx=10)
        
        # Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Zurücksetzen",
            command=self.reset_colors,
            fg_color="#64748B",
            hover_color="#475569"
        )
        reset_btn.pack(side="left", padx=10)
        
        # Presets
        presets_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        presets_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        presets_label = ctk.CTkLabel(
            presets_frame,
            text="Farbschemata:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        presets_label.pack(side="left", padx=(0, 10))
        
        # Preset buttons
        presets = [
            ("Elegant", self.preset_elegant),
            ("Klassisch", self.preset_classic),
            ("Warm", self.preset_warm),
            ("Modern", self.preset_modern)
        ]
        
        for name, command in presets:
            preset_btn = ctk.CTkButton(
                presets_frame,
                text=name,
                width=80,
                height=28,
                command=command,
                fg_color="#E2E8F0",
                text_color="#64748B",
                hover_color="#CBD5E1"
            )
            preset_btn.pack(side="left", padx=5)
    
    def update_preview(self, key):
        """Update color preview."""
        try:
            color = self.color_vars[key].get()
            if color.startswith("#") and len(color) == 7:
                self.preview_frames[key].configure(fg_color=color)
        except:
            pass
    
    def show_preview(self):
        """Show preview window with current colors."""
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("Farbvorschau")
        preview_window.geometry("500x400")
        
        # Get current colors
        colors = {k: v.get() for k, v in self.color_vars.items()}
        
        # Preview content
        preview_frame = ctk.CTkFrame(
            preview_window,
            fg_color=colors["background"]
        )
        preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            preview_frame,
            text="Checker Pro Suite",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            preview_frame,
            text="Vorschau der neuen Farben",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"]
        )
        subtitle.pack(pady=(0, 20))
        
        # Sample card
        card = ctk.CTkFrame(
            preview_frame,
            fg_color=colors["card_bg"],
            border_width=1,
            border_color=colors["border"]
        )
        card.pack(fill="x", padx=40, pady=20)
        
        # Sample buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(pady=20)
        
        btn1 = ctk.CTkButton(
            button_frame,
            text="Primär",
            fg_color=colors["primary"],
            width=100
        )
        btn1.pack(side="left", padx=10)
        
        btn2 = ctk.CTkButton(
            button_frame,
            text="Erfolg",
            fg_color=colors["success"],
            width=100
        )
        btn2.pack(side="left", padx=10)
        
        btn3 = ctk.CTkButton(
            button_frame,
            text="Neutral",
            fg_color=colors["neutral"],
            width=100
        )
        btn3.pack(side="left", padx=10)
    
    def apply_changes(self):
        """Apply changes to the main application."""
        colors = {k: v.get() for k, v in self.color_vars.items()}
        
        # Save to config file
        config_path = Path("design_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(colors, f, indent=2)
        
        print("✅ Designänderungen gespeichert in design_config.json")
        print("🔄 Starten Sie die Hauptanwendung neu, um die Änderungen zu sehen.")
    
    def reset_colors(self):
        """Reset to default colors."""
        for key, var in self.color_vars.items():
            var.set(self.current_colors[key])
            self.update_preview(key)
    
    def preset_elegant(self):
        """Apply elegant color scheme."""
        elegant_colors = {
            "primary": "#1E40AF",
            "success": "#047857",
            "neutral": "#374151",
            "background": "#F9FAFB",
            "card_bg": "#FFFFFF",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
            "border": "#D1D5DB"
        }
        self.apply_preset(elegant_colors)
    
    def preset_classic(self):
        """Apply classic color scheme."""
        classic_colors = {
            "primary": "#1F2937",
            "success": "#065F46",
            "neutral": "#4B5563",
            "background": "#F3F4F6",
            "card_bg": "#FFFFFF",
            "text_primary": "#1F2937",
            "text_secondary": "#6B7280",
            "border": "#E5E7EB"
        }
        self.apply_preset(classic_colors)
    
    def preset_warm(self):
        """Apply warm color scheme."""
        warm_colors = {
            "primary": "#B45309",
            "success": "#059669",
            "neutral": "#78716C",
            "background": "#FEF7ED",
            "card_bg": "#FFFFFF",
            "text_primary": "#1C1917",
            "text_secondary": "#78716C",
            "border": "#E7E5E4"
        }
        self.apply_preset(warm_colors)
    
    def preset_modern(self):
        """Apply modern color scheme."""
        modern_colors = {
            "primary": "#7C3AED",
            "success": "#10B981",
            "neutral": "#6366F1",
            "background": "#FAFAFA",
            "card_bg": "#FFFFFF",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "border": "#E2E8F0"
        }
        self.apply_preset(modern_colors)
    
    def apply_preset(self, colors):
        """Apply a color preset."""
        for key, color in colors.items():
            if key in self.color_vars:
                self.color_vars[key].set(color)
                self.update_preview(key)
    
    def run(self):
        """Start the design tuner."""
        self.root.mainloop()

if __name__ == "__main__":
    tuner = DesignTuner()
    tuner.run()
