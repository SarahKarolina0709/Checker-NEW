"""
Test für die modernen GUI-Verbesserungen
=====================================
Testet alle implementierten modernen UI-Komponenten und Animationen.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import os
import threading
import time

# Füge den Checker-Ordner zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_improvements_integration import ModernUIIntegration, integrate_modern_ui
from modern_ui_components import (
    ModernCard, ModernButton, ModernProgressBar, 
    ModernSearchEntry, ModernNotificationCenter,
    ModernLoadingSpinner, ModernStatusIndicator
)
from modern_animations import ModernAnimations
from ui_theme import UITheme


class ModernUITestApp(ctk.CTk):
    """Test-App für die modernen UI-Verbesserungen."""
    
    def __init__(self):
        super().__init__()
        
        # Fensterkonfiguration
        self.title("Moderne GUI-Verbesserungen - Test")
        self.geometry("1400x900")
        self.configure(fg_color=UITheme.COLOR_BACKGROUND)
        
        # Zentriere das Fenster
        self.center_window()
        
        # Setup der Test-UI
        self.setup_test_ui()
        
        # Integriere moderne UI-Verbesserungen
        self.ui_integration = ModernUIIntegration(self)
        
    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_test_ui(self):
        """Erstellt die Test-UI."""
        # Hauptlayout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollbarer Hauptbereich
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=UITheme.COLOR_PRIMARY,
            scrollbar_button_hover_color=UITheme.COLOR_PRIMARY_HOVER
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Test-Bereiche
        self.create_test_sections()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Erstellt den Header."""
        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=100
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎨 Moderne GUI-Verbesserungen Test",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Suchbereich
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew", padx=20)
        
        self.search_entry = ModernSearchEntry(
            search_frame,
            placeholder="Komponenten suchen...",
            on_search=self.on_search
        )
        self.search_entry.pack(side="left", padx=(0, 20))
        
        # Benachrichtigungen
        self.notification_center = ModernNotificationCenter(
            self,
            max_notifications=5
        )
        self.notification_center.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        # Begrüßungsbenachrichtigung
        self.notification_center.show_notification(
            "Willkommen im GUI-Test! 🚀",
            "success",
            5000
        )
    
    def create_test_sections(self):
        """Erstellt alle Test-Bereiche."""
        # Karten-Test
        self.create_card_test_section()
        
        # Button-Test
        self.create_button_test_section()
        
        # Fortschrittsbalken-Test
        self.create_progress_test_section()
        
        # Animations-Test
        self.create_animation_test_section()
        
        # Status-Indikator-Test
        self.create_status_test_section()
        
        # Loading-Spinner-Test
        self.create_loading_test_section()
    
    def create_card_test_section(self):
        """Erstellt den Karten-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="📋 Moderne Karten",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Karten-Beispiele
        cards_data = [
            ("Standard-Karte", "Einfache Karte mit Hover-Effekt", True, False),
            ("Klickbare Karte", "Karte mit Klick-Funktion", True, True),
            ("Stille Karte", "Karte ohne Hover-Effekt", False, False)
        ]
        
        for i, (title, subtitle, hover, clickable) in enumerate(cards_data):
            card = ModernCard(
                section_frame,
                title=title,
                subtitle=subtitle,
                hover_effect=hover,
                clickable=clickable,
                click_callback=lambda t=title: self.on_card_click(t)
            )
            card.grid(row=1, column=i, padx=20, pady=(0, 20), sticky="ew")
            
            # Füge Badge hinzu
            if i == 0:
                card.add_badge("Neu", "info")
            elif i == 1:
                card.add_badge("Aktiv", "success")
            
            # Füge Fortschrittsbalken hinzu
            if i == 2:
                card.add_progress_indicator(0.7)
    
    def create_button_test_section(self):
        """Erstellt den Button-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="🔘 Moderne Buttons",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=5, padx=20, pady=(20, 10), sticky="w")
        
        # Button-Beispiele
        button_styles = [
            ("Primary", "primary", "Hauptaktion"),
            ("Secondary", "secondary", "Zweitaktion"),
            ("Outline", "outline", "Randbutton"),
            ("Success", "success", "Erfolg"),
            ("Danger", "danger", "Gefahr")
        ]
        
        for i, (text, style, tooltip) in enumerate(button_styles):
            button = ModernButton(
                section_frame,
                text=text,
                style=style,
                with_tooltip=tooltip,
                command=lambda s=style: self.on_button_click(s)
            )
            button.grid(row=1, column=i, padx=10, pady=(0, 20))
    
    def create_progress_test_section(self):
        """Erstellt den Fortschrittsbalken-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="📊 Fortschrittsbalken",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Fortschrittsbalken
        progress_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bars = []
        
        # Mehrere Fortschrittsbalken
        for i in range(3):
            progress_bar = ModernProgressBar(
                progress_frame,
                width=400,
                height=12,
                show_percentage=True
            )
            progress_bar.grid(row=i, column=0, pady=10, sticky="ew")
            self.progress_bars.append(progress_bar)
        
        # Steuerbuttons
        control_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        control_frame.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        start_btn = ModernButton(
            control_frame,
            text="▶️ Start",
            style="success",
            command=self.start_progress_demo
        )
        start_btn.pack(side="left", padx=5)
        
        reset_btn = ModernButton(
            control_frame,
            text="🔄 Reset",
            style="secondary",
            command=self.reset_progress_demo
        )
        reset_btn.pack(side="left", padx=5)
    
    def create_animation_test_section(self):
        """Erstellt den Animations-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="✨ Animationen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Animations-Beispiele
        self.animation_cards = []
        
        for i in range(3):
            card = ModernCard(
                section_frame,
                title=f"Animation {i+1}",
                subtitle="Klicken für Animation",
                hover_effect=True,
                clickable=True,
                click_callback=lambda idx=i: self.trigger_animation(idx)
            )
            card.grid(row=1, column=i, padx=20, pady=(0, 20), sticky="ew")
            self.animation_cards.append(card)
        
        # Animations-Steuerung
        control_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        control_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 20))
        
        animations = [
            ("Fade In", self.demo_fade_in),
            ("Scale", self.demo_scale),
            ("Slide", self.demo_slide),
            ("Pulse", self.demo_pulse)
        ]
        
        for i, (text, command) in enumerate(animations):
            btn = ModernButton(
                control_frame,
                text=text,
                style="outline",
                command=command
            )
            btn.pack(side="left", padx=5)
    
    def create_status_test_section(self):
        """Erstellt den Status-Indikator-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="🚦 Status-Indikatoren",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=5, padx=20, pady=(20, 10), sticky="w")
        
        # Status-Indikatoren
        statuses = [
            ("Idle", "idle"),
            ("Working", "working"),
            ("Success", "success"),
            ("Error", "error"),
            ("Info", "info")
        ]
        
        self.status_indicators = []
        
        for i, (text, status) in enumerate(statuses):
            indicator_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            indicator_frame.grid(row=1, column=i, padx=10, pady=(0, 20))
            
            indicator = ModernStatusIndicator(indicator_frame, status=status)
            indicator.pack(pady=5)
            
            label = ctk.CTkLabel(
                indicator_frame,
                text=text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            label.pack()
            
            self.status_indicators.append(indicator)
        
        # Status-Steuerung
        control_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        control_frame.grid(row=2, column=0, columnspan=5, padx=20, pady=(0, 20))
        
        cycle_btn = ModernButton(
            control_frame,
            text="🔄 Status durchlaufen",
            style="primary",
            command=self.cycle_status_demo
        )
        cycle_btn.pack()
    
    def create_loading_test_section(self):
        """Erstellt den Loading-Spinner-Test-Bereich."""
        section_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE
        )
        section_frame.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Titel
        title_label = ctk.CTkLabel(
            section_frame,
            text="⏳ Loading-Spinner",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=18, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Spinner-Beispiele
        self.spinners = []
        
        spinner_sizes = [30, 50, 70]
        
        for i, size in enumerate(spinner_sizes):
            spinner_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            spinner_frame.grid(row=1, column=i, padx=20, pady=(0, 20))
            
            spinner = ModernLoadingSpinner(spinner_frame, size=size)
            spinner.pack(pady=10)
            
            size_label = ctk.CTkLabel(
                spinner_frame,
                text=f"{size}px",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            size_label.pack()
            
            self.spinners.append(spinner)
        
        # Spinner-Steuerung
        control_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        control_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 20))
        
        start_btn = ModernButton(
            control_frame,
            text="▶️ Start Spinner",
            style="success",
            command=self.start_spinners
        )
        start_btn.pack(side="left", padx=5)
        
        stop_btn = ModernButton(
            control_frame,
            text="⏹️ Stop Spinner",
            style="danger",
            command=self.stop_spinners
        )
        stop_btn.pack(side="left", padx=5)
    
    def create_footer(self):
        """Erstellt den Footer."""
        footer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=60
        )
        footer_frame.grid(row=7, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Status
        status_label = ctk.CTkLabel(
            footer_frame,
            text="✅ Alle Komponenten geladen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_SUCCESS
        )
        status_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Info
        info_label = ctk.CTkLabel(
            footer_frame,
            text="Moderne GUI-Verbesserungen für die Checker App",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
    
    # Event-Handler
    def on_search(self, query: str):
        """Behandelt Suchanfragen."""
        self.notification_center.show_notification(
            f"Suche nach: '{query}'",
            "info",
            2000
        )
    
    def on_card_click(self, title: str):
        """Behandelt Karten-Klicks."""
        self.notification_center.show_notification(
            f"Karte '{title}' geklickt!",
            "success",
            2000
        )
    
    def on_button_click(self, style: str):
        """Behandelt Button-Klicks."""
        self.notification_center.show_notification(
            f"Button-Style '{style}' geklickt!",
            "info",
            2000
        )
    
    def start_progress_demo(self):
        """Startet die Fortschrittsbalken-Demo."""
        def animate_progress():
            for i in range(101):
                progress = i / 100
                for bar in self.progress_bars:
                    bar.set_progress(progress, animated=False)
                time.sleep(0.05)
        
        threading.Thread(target=animate_progress, daemon=True).start()
        
        self.notification_center.show_notification(
            "Fortschrittsbalken-Demo gestartet",
            "success",
            2000
        )
    
    def reset_progress_demo(self):
        """Setzt die Fortschrittsbalken zurück."""
        for bar in self.progress_bars:
            bar.set_progress(0, animated=True)
        
        self.notification_center.show_notification(
            "Fortschrittsbalken zurückgesetzt",
            "info",
            2000
        )
    
    def trigger_animation(self, index: int):
        """Triggert eine Animation für eine bestimmte Karte."""
        if index < len(self.animation_cards):
            card = self.animation_cards[index]
            
            if index == 0:
                ModernAnimations.fade_in_animation(card, 0.5)
            elif index == 1:
                ModernAnimations.scale_animation(card, 1.0, 1.2, 0.3)
                card.after(300, lambda: ModernAnimations.scale_animation(card, 1.2, 1.0, 0.3))
            elif index == 2:
                ModernAnimations.slide_in_animation(card, "left", 0.5)
            
            self.notification_center.show_notification(
                f"Animation {index + 1} ausgeführt",
                "success",
                2000
            )
    
    def demo_fade_in(self):
        """Demonstriert Fade-In-Animation."""
        for card in self.animation_cards:
            ModernAnimations.fade_in_animation(card, 0.8)
        
        self.notification_center.show_notification(
            "Fade-In-Animation für alle Karten",
            "info",
            2000
        )
    
    def demo_scale(self):
        """Demonstriert Scale-Animation."""
        for i, card in enumerate(self.animation_cards):
            scale_factor = 1.1 + (i * 0.1)
            ModernAnimations.scale_animation(card, 1.0, scale_factor, 0.3)
            card.after(300, lambda c=card: ModernAnimations.scale_animation(c, scale_factor, 1.0, 0.3))
        
        self.notification_center.show_notification(
            "Scale-Animation für alle Karten",
            "info",
            2000
        )
    
    def demo_slide(self):
        """Demonstriert Slide-Animation."""
        directions = ["left", "right", "top"]
        
        for i, card in enumerate(self.animation_cards):
            direction = directions[i % len(directions)]
            ModernAnimations.slide_in_animation(card, direction, 0.5)
        
        self.notification_center.show_notification(
            "Slide-Animation für alle Karten",
            "info",
            2000
        )
    
    def demo_pulse(self):
        """Demonstriert Pulse-Animation."""
        for card in self.animation_cards:
            ModernAnimations.pulse_effect(card, 0.5, 2)
        
        self.notification_center.show_notification(
            "Pulse-Animation für alle Karten",
            "info",
            2000
        )
    
    def cycle_status_demo(self):
        """Demonstriert Status-Zyklus."""
        statuses = ["idle", "working", "success", "error", "info"]
        
        def cycle_status(index=0):
            if index < len(statuses):
                for indicator in self.status_indicators:
                    indicator.set_status(statuses[index], animated=True)
                
                self.after(1000, lambda: cycle_status(index + 1))
            else:
                # Zurück zu ursprünglichen Status
                original_statuses = ["idle", "working", "success", "error", "info"]
                for i, indicator in enumerate(self.status_indicators):
                    indicator.set_status(original_statuses[i], animated=True)
        
        cycle_status()
        
        self.notification_center.show_notification(
            "Status-Zyklus gestartet",
            "info",
            2000
        )
    
    def start_spinners(self):
        """Startet alle Spinner."""
        for spinner in self.spinners:
            spinner.start_spinning()
        
        self.notification_center.show_notification(
            "Alle Spinner gestartet",
            "success",
            2000
        )
    
    def stop_spinners(self):
        """Stoppt alle Spinner."""
        for spinner in self.spinners:
            spinner.stop_spinning()
        
        self.notification_center.show_notification(
            "Alle Spinner gestoppt",
            "info",
            2000
        )


def main():
    """Hauptfunktion zum Starten der Test-App."""
    # Konfiguriere CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    try:
        # Erstelle und starte die Test-App
        app = ModernUITestApp()
        
        # Zeige eine Willkommensnachricht
        print("🎨 Moderne GUI-Verbesserungen Test gestartet!")
        print("📝 Teste alle implementierten UI-Komponenten und Animationen.")
        print("🔄 Schließe das Fenster zum Beenden.")
        
        # Starte die App
        app.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler beim Starten der Test-App: {e}")
        messagebox.showerror("Fehler", f"Fehler beim Starten der Test-App:\n{e}")


if __name__ == "__main__":
    main()
