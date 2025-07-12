"""
Moderne Dashboard-Integration für die Checker-App
------------------------------------------------
Integriert alle UI-Verbesserungen in einem zentralen Dashboard-System
mit modernen Animationen, Glasmorphismus-Effekten und erweiterten Komponenten.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Any
import threading
import time
from datetime import datetime
import os

# Importiere alle modernen UI-Komponenten
from ui_theme import UITheme
from modern_animations import ModernAnimations, ModernHoverEffects, LoadingAnimations
from modern_ui_components import (
    ModernCard, ModernButton, ModernProgressBar, ModernSearchEntry,
    ModernNotificationCenter, ModernLoadingSpinner, ModernStatusIndicator,
    ModernTooltipManager, create_modern_section, create_modern_input_group
)
from advanced_visual_effects import (
    GlassmorphismEffect, GradientEffects, AdvancedAnimations,
    ParticleSystem, AdvancedColorTheming, create_modern_dashboard_section
)


class ModernDashboard(ctk.CTkFrame):
    """
    Zentrales Dashboard mit allen modernen UI-Verbesserungen
    """
    
    def __init__(self, parent, app_instance=None, **kwargs):
        super().__init__(
            parent,
            fg_color=UITheme.COLOR_BACKGROUND,
            corner_radius=0,
            **kwargs
        )
        
        self.app_instance = app_instance
        self.parent = parent
        
        # Dashboard-Komponenten
        self.notification_center = None
        self.status_indicators = {}
        self.progress_bars = {}
        self.loading_spinners = {}
        self.particle_systems = []
        
        # Dashboard-State
        self.dashboard_sections = {}
        self.is_initialized = False
        
        # Setup
        self.setup_dashboard()
        self.apply_modern_effects()
    
    def setup_dashboard(self):
        """Initialisiert das Dashboard"""
        try:
            # Hauptlayout konfigurieren
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            
            # Hauptcontainer mit Scrolling
            self.main_container = ctk.CTkScrollableFrame(
                self,
                fg_color="transparent",
                scrollbar_button_color=UITheme.COLOR_PRIMARY,
                scrollbar_button_hover_color=UITheme.COLOR_PRIMARY_HOVER
            )
            self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            # Dashboard-Header erstellen
            self.create_dashboard_header()
            
            # Benachrichtigungszentrum
            self.notification_center = ModernNotificationCenter(
                self.main_container,
                max_notifications=5
            )
            self.notification_center.grid(row=1, column=0, sticky="ew", pady=(0, 20))
            
            # Haupt-Dashboard-Bereich
            self.create_main_dashboard_area()
            
            # Footer-Bereich
            self.create_dashboard_footer()
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"Dashboard-Setup Fehler: {e}")
    
    def create_dashboard_header(self):
        """Erstellt den modernen Dashboard-Header"""
        try:
            # Header mit Gradient-Hintergrund
            header_frame = GradientEffects.create_gradient_frame(
                self.main_container,
                [UITheme.COLOR_GRADIENT_PRIMARY_START, UITheme.COLOR_GRADIENT_PRIMARY_END],
                800,
                80,
                "horizontal"
            )
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
            
            # Glasmorphismus-Effekt
            GlassmorphismEffect.apply_glass_effect(header_frame, opacity=0.9)
            
            # Header-Inhalt
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=20, pady=15)
            header_content.grid_columnconfigure(1, weight=1)
            
            # Logo/Titel
            title_label = ctk.CTkLabel(
                header_content,
                text="🚀 Checker-App Dashboard",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=24, weight="bold"),
                text_color=UITheme.COLOR_TEXT_ON_PRIMARY
            )
            title_label.grid(row=0, column=0, sticky="w")
            
            # Suchleiste
            self.search_entry = ModernSearchEntry(
                header_content,
                placeholder="Dashboard durchsuchen...",
                suggestions=["Kunden", "Workflows", "Projekte", "Einstellungen"],
                on_search=self.handle_dashboard_search
            )
            self.search_entry.grid(row=0, column=1, sticky="ew", padx=20)
            
            # Aktions-Buttons
            actions_frame = ctk.CTkFrame(header_content, fg_color="transparent")
            actions_frame.grid(row=0, column=2, sticky="e")
            
            # Benachrichtigungs-Button
            notify_btn = ModernButton(
                actions_frame,
                text="🔔",
                style="outline",
                width=40,
                height=40,
                with_tooltip="Benachrichtigungen",
                command=self.toggle_notifications
            )
            notify_btn.pack(side="left", padx=5)
            
            # Einstellungs-Button
            settings_btn = ModernButton(
                actions_frame,
                text="⚙️",
                style="outline",
                width=40,
                height=40,
                with_tooltip="Einstellungen",
                command=self.open_settings
            )
            settings_btn.pack(side="left", padx=5)
            
        except Exception as e:
            print(f"Dashboard-Header Fehler: {e}")
    
    def create_main_dashboard_area(self):
        """Erstellt den Hauptbereich des Dashboards"""
        try:
            # Hauptbereich-Container
            main_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
            main_area.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
            main_area.grid_columnconfigure(0, weight=1)
            main_area.grid_columnconfigure(1, weight=1)
            
            # Linke Spalte - Schnellzugriff
            left_column = self.create_quick_access_section(main_area)
            left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            # Rechte Spalte - Statistiken & Status
            right_column = self.create_statistics_section(main_area)
            right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            
            # Untere Reihe - Aktuelle Projekte
            projects_section = self.create_projects_section(main_area)
            projects_section.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(20, 0))
            
        except Exception as e:
            print(f"Hauptbereich Fehler: {e}")
    
    def create_quick_access_section(self, parent) -> ctk.CTkFrame:
        """Erstellt die Schnellzugriff-Sektion"""
        try:
            # Schnellzugriff-Karten
            quick_access_cards = [
                {"title": "📂 Neues Projekt", "subtitle": "Projekt erstellen", "action": self.create_new_project},
                {"title": "📋 Angebote", "subtitle": "Angebote verwalten", "action": self.manage_offers},
                {"title": "🔍 Prüfungen", "subtitle": "Qualitätsprüfungen", "action": self.manage_reviews},
                {"title": "✅ Finalisierung", "subtitle": "Projekte abschließen", "action": self.finalize_projects}
            ]
            
            cards_widgets = []
            for card_data in quick_access_cards:
                card = ModernCard(
                    parent,
                    title=card_data["title"],
                    subtitle=card_data["subtitle"],
                    hover_effect=True,
                    clickable=True,
                    click_callback=card_data["action"]
                )
                cards_widgets.append(card)
            
            # Dashboard-Sektion mit Glasmorphismus
            section_frame = create_modern_dashboard_section(
                parent,
                "🚀 Schnellzugriff",
                cards_widgets
            )
            
            return section_frame
            
        except Exception as e:
            print(f"Schnellzugriff-Sektion Fehler: {e}")
            return ctk.CTkFrame(parent)
    
    def create_statistics_section(self, parent) -> ctk.CTkFrame:
        """Erstellt die Statistiken-Sektion"""
        try:
            stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
            
            # Glasmorphismus-Effekt
            GlassmorphismEffect.apply_glass_effect(stats_frame, opacity=0.8)
            
            # Statistik-Widgets
            stats_widgets = []
            
            # Gesamtprojekte
            total_projects_card = ModernCard(
                stats_frame,
                title="📊 Gesamtprojekte",
                subtitle="142 Projekte"
            )
            stats_widgets.append(total_projects_card)
            
            # Aktive Projekte mit Fortschrittsbalken
            active_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            active_label = ctk.CTkLabel(
                active_frame,
                text="🔄 Aktive Projekte",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold")
            )
            active_label.pack(pady=(0, 10))
            
            active_progress = ModernProgressBar(
                active_frame,
                width=250,
                height=12,
                show_percentage=True
            )
            active_progress.pack()
            active_progress.set_progress(0.7, animated=True)
            
            stats_widgets.append(active_frame)
            
            # Status-Indikatoren
            status_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            status_label = ctk.CTkLabel(
                status_frame,
                text="📡 System-Status",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold")
            )
            status_label.pack(pady=(0, 10))
            
            # Status-Indikatoren Grid
            status_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
            status_grid.pack()
            
            status_items = [
                ("Server", "success"),
                ("Datenbank", "success"),
                ("Backup", "warning"),
                ("Sync", "working")
            ]
            
            for i, (name, status) in enumerate(status_items):
                indicator = ModernStatusIndicator(status_grid, status=status)
                indicator.grid(row=i//2, column=i%2*2, padx=5, pady=2)
                
                name_label = ctk.CTkLabel(
                    status_grid,
                    text=name,
                    font=ctk.CTkFont(size=10)
                )
                name_label.grid(row=i//2, column=i%2*2+1, padx=(0, 10), pady=2, sticky="w")
                
                self.status_indicators[name] = indicator
            
            stats_widgets.append(status_frame)
            
            # Dashboard-Sektion erstellen
            section_frame = create_modern_dashboard_section(
                parent,
                "📈 Statistiken & Status",
                stats_widgets
            )
            
            return section_frame
            
        except Exception as e:
            print(f"Statistiken-Sektion Fehler: {e}")
            return ctk.CTkFrame(parent)
    
    def create_projects_section(self, parent) -> ctk.CTkFrame:
        """Erstellt die Projekte-Sektion"""
        try:
            # Projekte-Tabelle (vereinfacht als Karten)
            projects_data = [
                {"name": "Übersetzung DE-EN", "client": "Kunde A", "progress": 0.8, "status": "In Bearbeitung"},
                {"name": "Lektorat Technisch", "client": "Kunde B", "progress": 0.4, "status": "Prüfung"},
                {"name": "Finalisierung Marketing", "client": "Kunde C", "progress": 0.95, "status": "Abschluss"}
            ]
            
            projects_widgets = []
            
            for project in projects_data:
                project_card = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_SURFACE)
                project_card.grid_columnconfigure(1, weight=1)
                
                # Projekt-Info
                info_frame = ctk.CTkFrame(project_card, fg_color="transparent")
                info_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
                info_frame.grid_columnconfigure(0, weight=1)
                
                # Projekttitel
                title_label = ctk.CTkLabel(
                    info_frame,
                    text=project["name"],
                    font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
                    anchor="w"
                )
                title_label.grid(row=0, column=0, sticky="w")
                
                # Kunde
                client_label = ctk.CTkLabel(
                    info_frame,
                    text=f"Kunde: {project['client']}",
                    font=ctk.CTkFont(size=11),
                    text_color=UITheme.COLOR_TEXT_SECONDARY,
                    anchor="w"
                )
                client_label.grid(row=1, column=0, sticky="w")
                
                # Fortschritt
                progress_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
                
                progress_bar = ModernProgressBar(
                    progress_frame,
                    width=200,
                    height=8,
                    show_percentage=True
                )
                progress_bar.pack()
                progress_bar.set_progress(project["progress"])
                
                # Status
                status_label = ctk.CTkLabel(
                    info_frame,
                    text=project["status"],
                    font=ctk.CTkFont(size=10),
                    text_color=UITheme.COLOR_SUCCESS if project["progress"] > 0.8 else UITheme.COLOR_WARNING
                )
                status_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
                
                projects_widgets.append(project_card)
            
            # Dashboard-Sektion erstellen
            section_frame = create_modern_dashboard_section(
                parent,
                "📋 Aktuelle Projekte",
                projects_widgets
            )
            
            return section_frame
            
        except Exception as e:
            print(f"Projekte-Sektion Fehler: {e}")
            return ctk.CTkFrame(parent)
    
    def create_dashboard_footer(self):
        """Erstellt den Dashboard-Footer"""
        try:
            footer_frame = ctk.CTkFrame(
                self.main_container,
                fg_color=UITheme.COLOR_SURFACE,
                height=50,
                corner_radius=UITheme.CORNER_RADIUS_MEDIUM
            )
            footer_frame.grid(row=3, column=0, sticky="ew")
            footer_frame.grid_columnconfigure(1, weight=1)
            
            # Footer-Inhalt
            footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
            footer_content.pack(fill="both", expand=True, padx=20, pady=10)
            footer_content.grid_columnconfigure(1, weight=1)
            
            # Version/Copyright
            version_label = ctk.CTkLabel(
                footer_content,
                text="Checker-App v2.0 • © 2025",
                font=ctk.CTkFont(size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            version_label.grid(row=0, column=0, sticky="w")
            
            # Laufzeit-Info
            runtime_label = ctk.CTkLabel(
                footer_content,
                text="Laufzeit: 00:00:00",
                font=ctk.CTkFont(size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            runtime_label.grid(row=0, column=1, sticky="e")
            
            # Laufzeit-Update starten
            self.update_runtime_display(runtime_label)
            
        except Exception as e:
            print(f"Dashboard-Footer Fehler: {e}")
    
    def apply_modern_effects(self):
        """Wendet moderne visuelle Effekte an"""
        try:
            # Glasmorphismus auf Hauptcontainer
            GlassmorphismEffect.apply_glass_effect(self.main_container, opacity=0.95)
            
            # Dynamische Farbthemierung für Karten
            if hasattr(self, 'dashboard_sections'):
                for section_widgets in self.dashboard_sections.values():
                    if isinstance(section_widgets, list):
                        AdvancedColorTheming.apply_dynamic_color_scheme(
                            section_widgets,
                            UITheme.COLOR_PRIMARY,
                            0.15
                        )
            
            # Sanfte Einblendung des Dashboards
            ModernAnimations.fade_in_animation(self, 0.8)
            
        except Exception as e:
            print(f"Moderne Effekte Fehler: {e}")
    
    def handle_dashboard_search(self, query: str):
        """Behandelt Dashboard-Suche"""
        try:
            if query.strip():
                self.show_notification(
                    f"Suche nach: '{query}'",
                    "info",
                    3000
                )
            
        except Exception as e:
            print(f"Dashboard-Suche Fehler: {e}")
    
    def show_notification(self, message: str, notification_type: str = "info", duration: int = 5000):
        """Zeigt eine Benachrichtigung an"""
        try:
            if self.notification_center:
                self.notification_center.show_notification(
                    message,
                    notification_type,
                    duration
                )
        except Exception as e:
            print(f"Benachrichtigung Fehler: {e}")
    
    def update_status_indicator(self, name: str, status: str):
        """Aktualisiert einen Status-Indikator"""
        try:
            if name in self.status_indicators:
                self.status_indicators[name].set_status(status, animated=True)
        except Exception as e:
            print(f"Status-Update Fehler: {e}")
    
    def update_runtime_display(self, runtime_label):
        """Aktualisiert die Laufzeit-Anzeige"""
        try:
            start_time = datetime.now()
            
            def update():
                if runtime_label.winfo_exists():
                    runtime = datetime.now() - start_time
                    runtime_str = str(runtime).split('.')[0]  # Entferne Mikrosekunden
                    runtime_label.configure(text=f"Laufzeit: {runtime_str}")
                    
                    # Nächstes Update in 1 Sekunde
                    self.after(1000, update)
            
            update()
            
        except Exception as e:
            print(f"Laufzeit-Update Fehler: {e}")
    
    # Event-Handler für Dashboard-Aktionen
    def toggle_notifications(self):
        """Schaltet Benachrichtigungen um"""
        self.show_notification("Benachrichtigungen umgeschaltet", "info", 2000)
    
    def open_settings(self):
        """Öffnet die Einstellungen"""
        self.show_notification("Einstellungen werden geöffnet...", "info", 2000)
    
    def create_new_project(self):
        """Erstellt ein neues Projekt"""
        self.show_notification("Neues Projekt wird erstellt...", "success", 3000)
    
    def manage_offers(self):
        """Verwaltet Angebote"""
        self.show_notification("Angebote-Verwaltung wird geöffnet...", "info", 3000)
    
    def manage_reviews(self):
        """Verwaltet Prüfungen"""
        self.show_notification("Prüfungs-Verwaltung wird geöffnet...", "info", 3000)
    
    def finalize_projects(self):
        """Finalisiert Projekte"""
        self.show_notification("Projekt-Finalisierung wird geöffnet...", "info", 3000)


def integrate_modern_dashboard(app_instance):
    """
    Integriert das moderne Dashboard in die bestehende App
    
    Args:
        app_instance: Die Haupt-App-Instanz
    """
    try:
        # Erstelle Dashboard-Tab oder -Fenster
        if hasattr(app_instance, 'main_container'):
            dashboard = ModernDashboard(app_instance.main_container, app_instance)
            
            # Füge Dashboard zur App hinzu
            dashboard.pack(fill="both", expand=True)
            
            # Zeige Willkommensnachricht
            dashboard.show_notification(
                "Willkommen im modernen Dashboard! 🚀",
                "success",
                5000
            )
            
            return dashboard
    
    except Exception as e:
        print(f"Dashboard-Integration Fehler: {e}")
        return None


# Test-Funktion für das Dashboard
def test_modern_dashboard():
    """
    Testet das moderne Dashboard in einem separaten Fenster
    """
    try:
        # Test-Fenster erstellen
        test_window = ctk.CTk()
        test_window.title("Modern Dashboard Test")
        test_window.geometry("1200x800")
        
        # Dashboard erstellen
        dashboard = ModernDashboard(test_window)
        dashboard.pack(fill="both", expand=True)
        
        # Test-Benachrichtigung
        dashboard.after(2000, lambda: dashboard.show_notification(
            "Dashboard erfolgreich geladen! 🎉",
            "success",
            4000
        ))
        
        # Fenster anzeigen
        test_window.mainloop()
        
    except Exception as e:
        print(f"Dashboard-Test Fehler: {e}")


if __name__ == "__main__":
    # Teste das Dashboard
    test_modern_dashboard()
