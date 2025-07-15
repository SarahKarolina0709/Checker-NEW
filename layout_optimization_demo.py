#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout-Optimierung Demo für Checker Pro Suite
Zeigt eine strukturierte, übersichtliche GUI-Anordnung
"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os

class OptimizedLayoutDemo:
    """Demo für optimiertes Layout mit klarer Struktur."""
    
    def __init__(self):
        # CustomTkinter Setup
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Hauptfenster
        self.root = ctk.CTk()
        self.root.title("🔍 Checker Pro Suite - Optimiertes Layout")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Layout erstellen
        self._create_optimized_layout()
        
    def _create_optimized_layout(self):
        """Erstellt das optimierte Layout mit klarer Struktur."""
        
        # === HEADER BEREICH ===
        header_frame = ctk.CTkFrame(self.root, height=120, fg_color="#FFFFFF", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header Content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Logo und Titel nebeneinander
        logo_title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        logo_title_frame.pack(fill="x")
        
        # Logo (links)
        logo_frame = ctk.CTkFrame(logo_title_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
        logo_frame.pack(side="left", padx=(0, 20))
        logo_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(logo_frame, text="🔍", font=ctk.CTkFont(size=40), text_color="white")
        logo_label.pack(expand=True)
        
        # Titel und Info (rechts)
        title_info_frame = ctk.CTkFrame(logo_title_frame, fg_color="transparent")
        title_info_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_info_frame,
            text="Checker Pro Suite",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#1F2937"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_info_frame,
            text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Status Badges (rechts)
        status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        status_frame.pack(side="right", anchor="ne")
        
        version_badge = ctk.CTkFrame(status_frame, fg_color="#10B981", corner_radius=15)
        version_badge.pack(side="left", padx=(0, 10))
        
        version_label = ctk.CTkLabel(version_badge, text="v2.1.0", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        version_label.pack(padx=12, pady=6)
        
        status_badge = ctk.CTkFrame(status_frame, fg_color="#3B82F6", corner_radius=15)
        status_badge.pack(side="left")
        
        status_label = ctk.CTkLabel(status_badge, text="✅ Betriebsbereit", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        status_label.pack(padx=12, pady=6)
        
        # === NAVIGATION BEREICH ===
        nav_frame = ctk.CTkFrame(self.root, height=80, fg_color="#F8FAFC", corner_radius=0, border_width=1, border_color="#E5E7EB")
        nav_frame.pack(fill="x", padx=0, pady=(0, 1))
        nav_frame.pack_propagate(False)
        
        # Navigation Buttons
        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        nav_buttons_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
        nav_buttons_frame.pack(anchor="center")
        
        # Navigation Buttons
        nav_buttons = [
            ("👥 Kunden", "#2563EB"),
            ("📁 Projekte", "#059669"),
            ("📤 Upload", "#F59E0B"),
            ("🔧 Tools", "#7C3AED"),
            ("📊 Reports", "#EF4444")
        ]
        
        for i, (text, color) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=text,
                width=140,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=12,
                command=lambda t=text: self._on_nav_click(t)
            )
            btn.pack(side="left", padx=8)
        
        # === MAIN CONTENT BEREICH ===
        main_frame = ctk.CTkFrame(self.root, fg_color="#F8FAFC", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Content Container mit Padding
        content_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # === UPLOAD CENTER (Hervorgehoben) ===
        upload_section = ctk.CTkFrame(content_container, fg_color="#EFF6FF", corner_radius=20, border_width=2, border_color="#3B82F6")
        upload_section.pack(fill="x", pady=(0, 20))
        
        # Upload Header
        upload_header = ctk.CTkFrame(upload_section, fg_color="#3B82F6", corner_radius=15)
        upload_header.pack(fill="x", padx=20, pady=(20, 10))
        
        upload_title = ctk.CTkLabel(
            upload_header,
            text="📤 DATEI-UPLOAD CENTER",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        upload_title.pack(pady=12)
        
        # Upload Content Grid
        upload_grid = ctk.CTkFrame(upload_section, fg_color="transparent")
        upload_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        # Upload Grid Layout (3 Spalten)
        upload_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Drop Zone
        drop_zone = ctk.CTkFrame(upload_grid, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
        drop_zone.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        drop_icon = ctk.CTkLabel(drop_zone, text="📁", font=ctk.CTkFont(size=48))
        drop_icon.pack(pady=(20, 10))
        
        drop_text = ctk.CTkLabel(
            drop_zone,
            text="Dateien hierher ziehen\noder klicken",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1F2937",
            justify="center"
        )
        drop_text.pack(pady=(0, 10))
        
        upload_btn = ctk.CTkButton(
            drop_zone,
            text="📂 Dateien auswählen",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._select_files
        )
        upload_btn.pack(pady=(0, 20), padx=15, fill="x")
        
        # Supported Formats
        formats_frame = ctk.CTkFrame(upload_grid, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
        formats_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        formats_title = ctk.CTkLabel(
            formats_frame,
            text="📋 Unterstützte Formate",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        formats_title.pack(pady=(15, 10))
        
        formats = ["📄 PDF", "📝 Word", "📊 Excel", "📑 PowerPoint", "📰 Text", "🖼️ Bilder"]
        for fmt in formats:
            fmt_label = ctk.CTkLabel(formats_frame, text=fmt, font=ctk.CTkFont(size=12), text_color="#6B7280")
            fmt_label.pack(pady=2)
        
        # Recent Uploads
        recent_frame = ctk.CTkFrame(upload_grid, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
        recent_frame.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="nsew")
        
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="🕒 Letzte Uploads",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        recent_title.pack(pady=(15, 10))
        
        no_uploads = ctk.CTkLabel(
            recent_frame,
            text="Noch keine Uploads\nvorhanden",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280",
            justify="center"
        )
        no_uploads.pack(pady=15)
        
        # === DASHBOARD CARDS ===
        dashboard_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Dashboard Grid (3 Spalten)
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure(0, weight=1)
        
        # Kunden Card
        self._create_dashboard_card(
            dashboard_frame, 0, 0,
            "👥 KUNDEN", "#E3F2FD", "#2563EB",
            "5", "Registrierte Kunden",
            ["Neue Kunden", "Aktive Projekte", "Letzte Aktivität"]
        )
        
        # Projekte Card
        self._create_dashboard_card(
            dashboard_frame, 0, 1,
            "📁 PROJEKTE", "#E8F5E8", "#059669",
            "12", "Aktive Projekte",
            ["In Bearbeitung", "Fertiggestellt", "Geplant"]
        )
        
        # Workflows Card
        self._create_dashboard_card(
            dashboard_frame, 0, 2,
            "🔧 WORKFLOWS", "#F3E5F5", "#7C3AED",
            "8", "Aktive Workflows",
            ["Qualitätsprüfung", "Übersetzung", "Review"]
        )
        
        # === STATUS BAR ===
        status_bar = ctk.CTkFrame(self.root, height=40, fg_color="#FFFFFF", corner_radius=0, border_width=1, border_color="#E5E7EB")
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        status_content = ctk.CTkFrame(status_bar, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=20, pady=8)
        
        # Status links
        status_left = ctk.CTkFrame(status_content, fg_color="transparent")
        status_left.pack(side="left")
        
        status_icon = ctk.CTkLabel(status_left, text="✅", font=ctk.CTkFont(size=14))
        status_icon.pack(side="left", padx=(0, 5))
        
        status_text = ctk.CTkLabel(status_left, text="System bereit", font=ctk.CTkFont(size=12), text_color="#059669")
        status_text.pack(side="left")
        
        # Zeit rechts
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(status_content, text=f"🕒 {current_time}", font=ctk.CTkFont(size=12), text_color="#6B7280")
        time_label.pack(side="right")
        
    def _create_dashboard_card(self, parent, row, col, title, bg_color, accent_color, stat_number, stat_text, items):
        """Erstellt eine Dashboard-Karte."""
        card = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=15, border_width=2, border_color=accent_color)
        card.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        
        # Header
        header = ctk.CTkFrame(card, fg_color=accent_color, corner_radius=12)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        header_label = ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        header_label.pack(pady=10)
        
        # Stats
        stats_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        stat_num = ctk.CTkLabel(stats_frame, text=stat_number, font=ctk.CTkFont(size=24, weight="bold"), text_color=accent_color)
        stat_num.pack(pady=(10, 0))
        
        stat_desc = ctk.CTkLabel(stats_frame, text=stat_text, font=ctk.CTkFont(size=12), text_color="#6B7280")
        stat_desc.pack(pady=(0, 10))
        
        # Items
        items_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        items_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        for item in items:
            item_label = ctk.CTkLabel(items_frame, text=f"• {item}", font=ctk.CTkFont(size=11), text_color="#374151", anchor="w")
            item_label.pack(anchor="w", padx=10, pady=2)
    
    def _darken_color(self, color):
        """Verdunkelt eine Hex-Farbe für Hover-Effekt."""
        color_map = {
            "#2563EB": "#1D4ED8",
            "#059669": "#047857",
            "#F59E0B": "#D97706",
            "#7C3AED": "#6D28D9",
            "#EF4444": "#DC2626"
        }
        return color_map.get(color, color)
    
    def _on_nav_click(self, text):
        """Handler für Navigation-Clicks."""
        print(f"Navigation geklickt: {text}")
    
    def _select_files(self):
        """Handler für Dateiauswahl."""
        print("Dateiauswahl geöffnet")
    
    def run(self):
        """Startet die Demo."""
        self.root.mainloop()

if __name__ == "__main__":
    print("🔍 Starte Layout-Optimierung Demo...")
    demo = OptimizedLayoutDemo()
    demo.run()
