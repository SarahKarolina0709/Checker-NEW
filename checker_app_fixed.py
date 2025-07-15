#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker App Minimal - Reparierte Version
"""

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
import json

class CheckerApp:
    VERSION = "2.1.0"
    
    def __init__(self):
        """Initialisiert die Checker Pro Suite."""
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        # Hauptfenster
        self.root = ctk.CTk()
        self.root.title("Checker Pro Suite")
        self.root.geometry("1200x800")
        
        # ViewStack simulieren
        self.view_stack = type('ViewStack', (), {
            'container': self.root,
            'views': {},
            'add_view': lambda view_name, frame: setattr(self, f'view_{view_name}', frame),
            'show_view': lambda view_name: getattr(self, f'view_{view_name}', None)
        })()
        
        # Welcome Screen erstellen
        self._create_welcome_screen()
        
    def _create_welcome_screen(self):
        """Erstellt den optimierten Willkommensbildschirm."""
        try:
            # Welcome Frame mit klarer Hierarchie
            welcome_frame = ctk.CTkFrame(self.root, fg_color="#F8FAFC")
            welcome_frame.pack(fill="both", expand=True)
            welcome_frame.grid_columnconfigure(0, weight=1)
            welcome_frame.grid_rowconfigure(0, weight=0)  # Header
            welcome_frame.grid_rowconfigure(1, weight=0)  # Navigation
            welcome_frame.grid_rowconfigure(2, weight=0)  # Upload Center
            welcome_frame.grid_rowconfigure(3, weight=1)  # Dashboard
            
            # === HEADER BEREICH ===
            self._create_optimized_header(welcome_frame)
            
            # === NAVIGATION BEREICH ===
            self._create_navigation_bar(welcome_frame)
            
            # === UPLOAD CENTER ===
            self._create_upload_center(welcome_frame)
            
            # === DASHBOARD BEREICH ===
            self._create_dashboard_section(welcome_frame)
            
            return welcome_frame
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
            return None
    
    def _create_optimized_header(self, parent):
        """Erstellt den optimierten Header-Bereich."""
        header_frame = ctk.CTkFrame(parent, height=120, fg_color="#FFFFFF", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Header Content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Logo und Titel Container
        logo_title_container = ctk.CTkFrame(header_content, fg_color="transparent")
        logo_title_container.pack(fill="x")
        
        # Logo (links)
        logo_frame = ctk.CTkFrame(logo_title_container, fg_color="transparent")
        logo_frame.pack(side="left")
        
        # Logo laden mit Fallback
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(80, 80))
                
                logo_bg = ctk.CTkFrame(logo_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
                logo_bg.pack(side="left", padx=(0, 20))
                logo_bg.pack_propagate(False)
                
                logo_label = ctk.CTkLabel(logo_bg, image=logo_photo, text="")
                logo_label.pack(expand=True)
            else:
                raise FileNotFoundError("Logo nicht gefunden")
        except:
            # Fallback Logo
            logo_bg = ctk.CTkFrame(logo_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
            logo_bg.pack(side="left", padx=(0, 20))
            logo_bg.pack_propagate(False)
            
            logo_label = ctk.CTkLabel(logo_bg, text="🔍", font=ctk.CTkFont(size=40), text_color="white")
            logo_label.pack(expand=True)
        
        # Titel und Info (Mitte)
        title_info_frame = ctk.CTkFrame(logo_title_container, fg_color="transparent")
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
        
        version_label = ctk.CTkLabel(version_badge, text=f"v{self.VERSION}", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        version_label.pack(padx=12, pady=6)
        
        status_badge = ctk.CTkFrame(status_frame, fg_color="#3B82F6", corner_radius=15)
        status_badge.pack(side="left")
        
        status_label = ctk.CTkLabel(status_badge, text="✅ Betriebsbereit", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        status_label.pack(padx=12, pady=6)
    
    def _create_navigation_bar(self, parent):
        """Erstellt die horizontale Navigationsleiste."""
        nav_frame = ctk.CTkFrame(parent, height=80, fg_color="#F8FAFC", corner_radius=0, border_width=1, border_color="#E5E7EB")
        nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 1))
        nav_frame.grid_propagate(False)
        
        # Navigation Content
        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        nav_buttons_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
        nav_buttons_frame.pack(anchor="center")
        
        # Navigation Buttons
        nav_buttons = [
            ("👥 Kunden", "#2563EB", self._show_customers),
            ("📁 Projekte", "#059669", self._show_projects),
            ("📤 Upload", "#F59E0B", self._select_upload_files),
            ("🔧 Tools", "#7C3AED", self._show_tools),
            ("📊 Reports", "#EF4444", self._show_reports)
        ]
        
        for text, color, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=text,
                width=140,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=12,
                command=command
            )
            btn.pack(side="left", padx=8)
    
    def _create_upload_center(self, parent):
        """Erstellt das prominente Upload Center."""
        upload_section = ctk.CTkFrame(parent, fg_color="#EFF6FF", corner_radius=20, border_width=2, border_color="#3B82F6")
        upload_section.grid(row=2, column=0, sticky="ew", padx=30, pady=20)
        
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
        upload_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Drop Zone
        self._create_drop_zone(upload_grid)
        
        # Supported Formats
        self._create_formats_display(upload_grid)
        
        # Recent Uploads
        self._create_recent_uploads_display(upload_grid)
    
    def _create_dashboard_section(self, parent):
        """Erstellt den Dashboard-Bereich mit Cards."""
        dashboard_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dashboard_frame.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        # Dashboard Grid
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure(0, weight=1)
        
        # Kunden Card
        self._create_dashboard_card(
            dashboard_frame, 0, 0,
            "👥 KUNDEN", "#E3F2FD", "#2563EB",
            "5", "Registrierte Kunden",
            ["Neue Kunden hinzufügen", "Kundendaten verwalten", "Projekte zuweisen"]
        )
        
        # Projekte Card
        self._create_dashboard_card(
            dashboard_frame, 0, 1,
            "📁 PROJEKTE", "#E8F5E8", "#059669",
            "12", "Aktive Projekte",
            ["Neues Projekt erstellen", "Dateien hochladen", "Status verfolgen"]
        )
        
        # Workflows Card
        self._create_dashboard_card(
            dashboard_frame, 0, 2,
            "🔧 WORKFLOWS", "#F3E5F5", "#7C3AED",
            "8", "Verfügbare Tools",
            ["Qualitätsprüfung", "Export/Import", "Automatisierung"]
        )
    
    def _create_drop_zone(self, parent):
        """Erstellt die Drag & Drop Zone."""
        drop_zone = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
        drop_zone.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Hover-Effekte
        def on_enter(event):
            drop_zone.configure(border_color="#3B82F6", fg_color="#F0F8FF")
            
        def on_leave(event):
            drop_zone.configure(border_color="#DBEAFE", fg_color="white")
        
        drop_zone.bind("<Enter>", on_enter)
        drop_zone.bind("<Leave>", on_leave)
        drop_zone.bind("<Button-1>", lambda e: self._select_upload_files())
        
        drop_icon = ctk.CTkLabel(drop_zone, text="📁", font=ctk.CTkFont(size=48))
        drop_icon.pack(pady=(20, 10))
        drop_icon.bind("<Button-1>", lambda e: self._select_upload_files())
        
        drop_text = ctk.CTkLabel(
            drop_zone,
            text="Dateien hierher ziehen\noder klicken",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1F2937",
            justify="center"
        )
        drop_text.pack(pady=(0, 10))
        drop_text.bind("<Button-1>", lambda e: self._select_upload_files())
        
        upload_btn = ctk.CTkButton(
            drop_zone,
            text="📂 Dateien auswählen",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._select_upload_files
        )
        upload_btn.pack(pady=(0, 20), padx=15, fill="x")
    
    def _create_formats_display(self, parent):
        """Erstellt die Anzeige unterstützter Formate."""
        formats_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
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
    
    def _create_recent_uploads_display(self, parent):
        """Erstellt die Anzeige letzter Uploads."""
        recent_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
        recent_frame.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="nsew")
        
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="🕒 Letzte Uploads",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        recent_title.pack(pady=(15, 10))
        
        # Placeholder für letzte Uploads
        recent_items = ["dokument.pdf", "text.docx", "daten.xlsx"]
        for item in recent_items:
            item_label = ctk.CTkLabel(recent_frame, text=f"📄 {item}", font=ctk.CTkFont(size=11), text_color="#6B7280")
            item_label.pack(pady=2)
    
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
        
        stat_num = ctk.CTkLabel(stats_frame, text=str(stat_number), font=ctk.CTkFont(size=24, weight="bold"), text_color=accent_color)
        stat_num.pack(pady=(10, 0))
        
        stat_desc = ctk.CTkLabel(stats_frame, text=stat_text, font=ctk.CTkFont(size=12), text_color="#6B7280")
        stat_desc.pack(pady=(0, 10))
        
        # Items
        items_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        items_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        for item in items:
            item_label = ctk.CTkLabel(items_frame, text=f"• {item}", font=ctk.CTkFont(size=11), text_color="#374151", anchor="w")
            item_label.pack(anchor="w", padx=10, pady=2)
    
    # Helper-Methoden
    def _darken_color(self, color):
        """Dunkelt eine Farbe ab für Hover-Effekte."""
        color_map = {
            "#2563EB": "#1D4ED8",
            "#059669": "#047857", 
            "#F59E0B": "#D97706",
            "#7C3AED": "#6D28D9",
            "#EF4444": "#DC2626"
        }
        return color_map.get(color, color)
    
    # Placeholder-Methoden für Navigation
    def _show_customers(self):
        print("Kunden-Ansicht wird geladen...")
        
    def _show_projects(self):
        print("Projekte-Ansicht wird geladen...")
        
    def _show_tools(self):
        print("Tools-Ansicht wird geladen...")
        
    def _show_reports(self):
        print("Reports-Ansicht wird geladen...")
        
    def _select_upload_files(self):
        """Öffnet Dateiauswahl-Dialog."""
        files = filedialog.askopenfilenames(
            title="Dateien für Upload auswählen",
            filetypes=[
                ("Alle unterstützten Formate", "*.pdf;*.docx;*.xlsx;*.pptx;*.txt"),
                ("PDF-Dateien", "*.pdf"),
                ("Word-Dokumente", "*.docx"),
                ("Excel-Dateien", "*.xlsx"),
                ("PowerPoint-Präsentationen", "*.pptx"),
                ("Text-Dateien", "*.txt"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if files:
            print(f"Ausgewählte Dateien: {files}")
            messagebox.showinfo("Upload", f"{len(files)} Datei(en) ausgewählt für Upload")
    
    def run(self):
        """Startet die Anwendung."""
        self.root.mainloop()

if __name__ == "__main__":
    app = CheckerApp()
    app.run()
