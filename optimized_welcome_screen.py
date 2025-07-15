#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimierte Welcome Screen Implementierung für Checker Pro Suite
Ersetzt die komplexe Welcome-Screen-Funktion durch eine strukturierte Version
"""

def create_optimized_welcome_screen(self):
    """Erstellt den optimierten Willkommensbildschirm mit klarer Struktur."""
    try:
        # Welcome Frame mit klarer Hierarchie
        welcome_frame = ctk.CTkFrame(self.view_stack.container, fg_color="#F8FAFC")
        welcome_frame.grid_columnconfigure(0, weight=1)
        welcome_frame.grid_rowconfigure(0, weight=0)  # Header - fest
        welcome_frame.grid_rowconfigure(1, weight=0)  # Navigation - fest  
        welcome_frame.grid_rowconfigure(2, weight=0)  # Upload Center - fest
        welcome_frame.grid_rowconfigure(3, weight=1)  # Dashboard - flexibel
        
        # === HEADER BEREICH ===
        header_frame = ctk.CTkFrame(welcome_frame, height=120, fg_color="#FFFFFF", corner_radius=0)
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
        
        # Logo mit Fallback
        try:
            from PIL import Image
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
        
        # === NAVIGATION BEREICH ===
        nav_frame = ctk.CTkFrame(welcome_frame, height=80, fg_color="#F8FAFC", corner_radius=0, border_width=1, border_color="#E5E7EB")
        nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 1))
        nav_frame.grid_propagate(False)
        
        # Navigation Content
        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        nav_buttons_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
        nav_buttons_frame.pack(anchor="center")
        
        # Navigation Buttons mit korrekten Kommandos
        nav_buttons = [
            ("👥 Kunden", "#2563EB", lambda: self.show_customer_management_view()),
            ("📁 Projekte", "#059669", lambda: self.show_projects_view()),
            ("📤 Upload", "#F59E0B", lambda: self._select_upload_files()),
            ("🔧 Tools", "#7C3AED", lambda: self.show_tools_view()),
            ("📊 Reports", "#EF4444", lambda: self._show_reports())
        ]
        
        # Farbzuordnung für Hover-Effekte
        color_map = {
            "#2563EB": "#1D4ED8",
            "#059669": "#047857", 
            "#F59E0B": "#D97706",
            "#7C3AED": "#6D28D9",
            "#EF4444": "#DC2626"
        }
        
        for text, color, command in nav_buttons:
            hover_color = color_map.get(color, color)
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=text,
                width=140,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=hover_color,
                corner_radius=12,
                command=command
            )
            btn.pack(side="left", padx=8)
        
        # === UPLOAD CENTER ===
        upload_section = ctk.CTkFrame(welcome_frame, fg_color="#EFF6FF", corner_radius=20, border_width=2, border_color="#3B82F6")
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
        drop_zone = ctk.CTkFrame(upload_grid, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
        drop_zone.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Hover-Effekte für Drop Zone
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
        
        # Upload-Historie laden
        self._load_recent_uploads(recent_frame)
        
        # === DASHBOARD BEREICH ===
        dashboard_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        dashboard_frame.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        # Dashboard Grid
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure(0, weight=1)
        
        # Helper-Funktionen für Statistiken
        def get_customer_count():
            try:
                if self.customer_manager and hasattr(self.customer_manager, 'customers_data'):
                    return len(self.customer_manager.customers_data)
                elif self.kunden_manager:
                    return len(self.kunden_manager.alle_kunden())
                return 0
            except:
                return 0
        
        def get_project_count():
            try:
                import os
                base_path = "Checker_Projekte"
                project_count = 0
                
                if os.path.exists(base_path):
                    for customer_folder in os.listdir(base_path):
                        customer_path = os.path.join(base_path, customer_folder)
                        if os.path.isdir(customer_path):
                            projects = [p for p in os.listdir(customer_path) if os.path.isdir(os.path.join(customer_path, p))]
                            project_count += len(projects)
                return project_count
            except:
                return 0
        
        def create_dashboard_card(parent, row, col, title, bg_color, accent_color, stat_number, stat_text, items):
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
        
        # Kunden Card
        create_dashboard_card(
            dashboard_frame, 0, 0,
            "👥 KUNDEN", "#E3F2FD", "#2563EB",
            get_customer_count(), "Registrierte Kunden",
            ["Neue Kunden hinzufügen", "Kundendaten verwalten", "Projekte zuweisen"]
        )
        
        # Projekte Card
        create_dashboard_card(
            dashboard_frame, 0, 1,
            "📁 PROJEKTE", "#E8F5E8", "#059669",
            get_project_count(), "Aktive Projekte",
            ["Neues Projekt erstellen", "Dateien hochladen", "Status verfolgen"]
        )
        
        # Workflows Card
        create_dashboard_card(
            dashboard_frame, 0, 2,
            "🔧 WORKFLOWS", "#F3E5F5", "#7C3AED",
            "8", "Verfügbare Tools",
            ["Qualitätsprüfung", "Export/Import", "Automatisierung"]
        )
        
        # ViewStack hinzufügen
        self.view_stack.add_view("welcome", welcome_frame)
        self.view_stack.show_view("welcome")
        
        return welcome_frame
        
    except Exception as e:
        self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
        # Fallback zur ursprünglichen Ansicht
        return None

def add_helper_methods(self):
    """Fügt die Helper-Methoden für die optimierte Welcome-Screen hinzu."""
    
    def _show_reports(self):
        """Zeigt Reports an."""
        self.update_status("Reports-Funktion wird entwickelt...", "info")
        
    # Füge die Methode zur Klasse hinzu
    self._show_reports = _show_reports.__get__(self, self.__class__)

if __name__ == "__main__":
    print("Optimierte Welcome Screen Implementierung bereit")
