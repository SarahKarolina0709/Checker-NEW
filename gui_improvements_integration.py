"""
GUI Verbesserungen Zusammenfassung - Modern UI Integration
========================================================
Integriert alle modernen GUI-Verbesserungen in die bestehende Checker App.
"""

import customtkinter as ctk
from typing import Optional, Dict, List
import logging
import traceback

# Import der erweiterten UI-Komponenten
from modern_ui_components import (
    ModernCard, ModernButton, ModernProgressBar, 
    ModernSearchEntry, ModernNotificationCenter,
    ModernLoadingSpinner, ModernStatusIndicator
)
from modern_animations import ModernAnimations
from ui_theme import UITheme


class ModernUIIntegration:
    """
    Integriert moderne UI-Verbesserungen in die bestehende Checker App.
    """
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        self.modern_components = {}
        self.animations_enabled = True
        
        # Integration der modernen Komponenten
        self._integrate_modern_components()
    
    def _integrate_modern_components(self):
        """Integriert moderne Komponenten in die bestehende UI."""
        try:
            # Verbessere Welcome Screen
            self._enhance_welcome_screen()
            
            # Verbessere Container
            self._enhance_containers()
            
            # Füge moderne Animationen hinzu
            self._add_modern_animations()
            
            # Verbessere Buttons
            self._enhance_buttons()
            
            # Füge Benachrichtigungen hinzu
            self._add_notification_system()
            
            self.logger.info("Moderne UI-Komponenten erfolgreich integriert")
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Integration moderner UI-Komponenten: {e}")
            traceback.print_exc()
    
    def _enhance_welcome_screen(self):
        """Verbessert den Welcome Screen mit modernen Komponenten."""
        if not hasattr(self.app, 'welcome_screen'):
            return
        
        try:
            welcome_screen = self.app.welcome_screen
            
            # Füge moderne Suchfunktion hinzu
            if hasattr(welcome_screen, 'main_container'):
                self._add_modern_search(welcome_screen.main_container)
            
            # Verbessere Container mit modernen Effekten
            self._apply_modern_container_effects(welcome_screen)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern des Welcome Screens: {e}")
    
    def _add_modern_search(self, parent):
        """Fügt moderne Suchfunktion hinzu."""
        try:
            search_frame = ctk.CTkFrame(parent, fg_color="transparent")
            search_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
            
            modern_search = ModernSearchEntry(
                search_frame,
                placeholder="Projekte, Kunden oder Workflows suchen...",
                on_search=self._on_global_search
            )
            modern_search.pack(expand=True, fill="x", padx=50)
            
            self.modern_components['search'] = modern_search
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der modernen Suche: {e}")
    
    def _apply_modern_container_effects(self, welcome_screen):
        """Wendet moderne Effekte auf Container an."""
        try:
            # Verbessere Customer Section
            if hasattr(welcome_screen, 'customer_section'):
                self._enhance_section(welcome_screen.customer_section, "customer")
            
            # Verbessere Upload Section
            if hasattr(welcome_screen, 'upload_section'):
                self._enhance_section(welcome_screen.upload_section, "upload")
            
            # Verbessere Workflow Section
            if hasattr(welcome_screen, 'workflow_section'):
                self._enhance_section(welcome_screen.workflow_section, "workflow")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden moderner Container-Effekte: {e}")
    
    def _enhance_section(self, section, section_type: str):
        """Verbessert eine Sektion mit modernen Effekten."""
        try:
            # Füge Hover-Effekte hinzu
            ModernAnimations.scale_on_hover(section, 1.02)
            
            # Füge Fade-in Animation hinzu
            ModernAnimations.fade_in_animation(section, 0.8)
            
            # Spezifische Verbesserungen je nach Sektionstyp
            if section_type == "upload":
                self._enhance_upload_section(section)
            elif section_type == "workflow":
                self._enhance_workflow_section(section)
            elif section_type == "customer":
                self._enhance_customer_section(section)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der {section_type} Sektion: {e}")
    
    def _enhance_upload_section(self, section):
        """Verbessert die Upload-Sektion."""
        try:
            # Füge modernen Fortschrittsbalken hinzu (wenn nicht vorhanden)
            if not hasattr(section, 'progress_bar'):
                progress_frame = ctk.CTkFrame(section, fg_color="transparent")
                progress_frame.grid(row=99, column=0, sticky="ew", padx=20, pady=10)
                
                section.progress_bar = ModernProgressBar(
                    progress_frame,
                    width=300,
                    height=8,
                    show_percentage=True
                )
                section.progress_bar.pack(fill="x")
                
                # Verstecke zunächst
                progress_frame.grid_remove()
                
            # Füge Status-Indikator hinzu
            if not hasattr(section, 'status_indicator'):
                section.status_indicator = ModernStatusIndicator(section, status="idle")
                section.status_indicator.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der Upload-Sektion: {e}")
    
    def _enhance_workflow_section(self, section):
        """Verbessert die Workflow-Sektion."""
        try:
            # Füge moderne Workflow-Karten hinzu
            if hasattr(section, 'workflow_cards'):
                for card in section.workflow_cards:
                    # Füge Hover-Animationen hinzu
                    ModernAnimations.scale_on_hover(card, 1.05)
                    
                    # Füge Ripple-Effekt hinzu
                    self._add_ripple_effect(card)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der Workflow-Sektion: {e}")
    
    def _enhance_customer_section(self, section):
        """Verbessert die Customer-Sektion."""
        try:
            # Füge moderne Eingabefelder hinzu (wenn möglich)
            if hasattr(section, 'customer_entry'):
                # Verbessere Eingabefeld-Styling
                section.customer_entry.configure(
                    border_color=UITheme.COLOR_CONTAINER_CUSTOMER,
                    border_width=2
                )
                
                # Füge Focus-Effekte hinzu
                def on_focus_in(event):
                    section.customer_entry.configure(border_color=UITheme.COLOR_PRIMARY)
                    ModernAnimations.scale_animation(section.customer_entry, 1.0, 1.02, 0.2)
                
                def on_focus_out(event):
                    section.customer_entry.configure(border_color=UITheme.COLOR_CONTAINER_CUSTOMER)
                    ModernAnimations.scale_animation(section.customer_entry, 1.02, 1.0, 0.2)
                
                section.customer_entry.bind("<FocusIn>", on_focus_in)
                section.customer_entry.bind("<FocusOut>", on_focus_out)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der Customer-Sektion: {e}")
    
    def _enhance_containers(self):
        """Verbessert alle Container mit modernen Effekten."""
        try:
            # Alle CTkFrame-Widgets in der App finden und verbessern
            for widget_name in dir(self.app):
                widget = getattr(self.app, widget_name)
                if isinstance(widget, ctk.CTkFrame):
                    self._apply_container_improvements(widget)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der Container: {e}")
    
    def _apply_container_improvements(self, container):
        """Wendet Verbesserungen auf einen Container an."""
        try:
            # Verbessere Ecken-Radius
            current_radius = container.cget('corner_radius')
            if current_radius < UITheme.CORNER_RADIUS_LARGE:
                container.configure(corner_radius=UITheme.CORNER_RADIUS_LARGE)
            
            # Füge subtile Schatten-Simulation hinzu
            self._add_shadow_effect(container)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden von Container-Verbesserungen: {e}")
    
    def _add_shadow_effect(self, widget):
        """Fügt einen subtilen Schatten-Effekt hinzu."""
        try:
            # Erstelle einen Schatten-Frame
            shadow_frame = ctk.CTkFrame(
                widget.master,
                fg_color=UITheme.COLOR_SHADOW_LIGHT,
                corner_radius=widget.cget('corner_radius'),
                border_width=0
            )
            
            # Positioniere den Schatten
            def update_shadow():
                try:
                    if widget.winfo_exists() and shadow_frame.winfo_exists():
                        x = widget.winfo_x() + 3
                        y = widget.winfo_y() + 3
                        width = widget.winfo_width()
                        height = widget.winfo_height()
                        
                        shadow_frame.place(x=x, y=y, width=width, height=height)
                        shadow_frame.lower()
                except:
                    pass
            
            # Binde Update-Funktion an Configure-Event
            widget.bind('<Configure>', lambda e: update_shadow())
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Schatten-Effekts: {e}")
    
    def _add_modern_animations(self):
        """Fügt moderne Animationen zur App hinzu."""
        try:
            # Füge Fade-in Animation für das Hauptfenster hinzu
            if hasattr(self.app, 'root'):
                ModernAnimations.fade_in_animation(self.app.root, 1.0)
            
            # Füge Animationen für wichtige UI-Elemente hinzu
            self._add_button_animations()
            self._add_container_animations()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen moderner Animationen: {e}")
    
    def _add_button_animations(self):
        """Fügt Animationen für Buttons hinzu."""
        try:
            # Finde alle Buttons in der App
            buttons = self._find_all_buttons()
            
            for button in buttons:
                # Füge Hover-Effekte hinzu
                ModernAnimations.scale_on_hover(button, 1.05)
                
                # Füge Klick-Effekte hinzu
                self._add_click_animation(button)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen von Button-Animationen: {e}")
    
    def _find_all_buttons(self) -> List[ctk.CTkButton]:
        """Findet alle Buttons in der App."""
        buttons = []
        
        def find_buttons_recursive(widget):
            try:
                if isinstance(widget, ctk.CTkButton):
                    buttons.append(widget)
                
                # Durchsuche Kinder-Widgets
                for child in widget.winfo_children():
                    find_buttons_recursive(child)
            except:
                pass
        
        # Beginne mit dem Hauptfenster
        if hasattr(self.app, 'root'):
            find_buttons_recursive(self.app.root)
        
        return buttons
    
    def _add_click_animation(self, button):
        """Fügt Klick-Animation zu einem Button hinzu."""
        try:
            original_command = button.cget('command')
            
            def animated_command():
                # Klick-Animation
                ModernAnimations.scale_animation(button, 1.0, 0.95, 0.1)
                
                # Warte kurz und führe dann den ursprünglichen Command aus
                def restore_and_execute():
                    ModernAnimations.scale_animation(button, 0.95, 1.0, 0.1)
                    if original_command:
                        original_command()
                
                button.after(100, restore_and_execute)
            
            button.configure(command=animated_command)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Klick-Animation: {e}")
    
    def _add_container_animations(self):
        """Fügt Animationen für Container hinzu."""
        try:
            # Finde alle Container
            containers = self._find_all_containers()
            
            for container in containers:
                # Füge subtile Atmungs-Animation hinzu
                ModernAnimations.breathing_effect(container, 3.0)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen von Container-Animationen: {e}")
    
    def _find_all_containers(self) -> List[ctk.CTkFrame]:
        """Findet alle Container in der App."""
        containers = []
        
        def find_containers_recursive(widget):
            try:
                if isinstance(widget, ctk.CTkFrame):
                    containers.append(widget)
                
                # Durchsuche Kinder-Widgets
                for child in widget.winfo_children():
                    find_containers_recursive(child)
            except:
                pass
        
        # Beginne mit dem Hauptfenster
        if hasattr(self.app, 'root'):
            find_containers_recursive(self.app.root)
        
        return containers
    
    def _enhance_buttons(self):
        """Verbessert alle Buttons mit modernen Styles."""
        try:
            buttons = self._find_all_buttons()
            
            for button in buttons:
                # Verbessere Button-Styling
                self._apply_modern_button_style(button)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verbessern der Buttons: {e}")
    
    def _apply_modern_button_style(self, button):
        """Wendet moderne Styles auf einen Button an."""
        try:
            # Verbessere Corner-Radius
            button.configure(corner_radius=UITheme.CORNER_RADIUS_MEDIUM)
            
            # Verbessere Farben (wenn Standardfarben verwendet werden)
            current_fg = button.cget('fg_color')
            if current_fg == ctk.DEFAULT_COLOR:
                button.configure(fg_color=UITheme.COLOR_PRIMARY)
                button.configure(hover_color=UITheme.COLOR_PRIMARY_HOVER)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden moderner Button-Styles: {e}")
    
    def _add_notification_system(self):
        """Fügt ein Benachrichtigungssystem hinzu."""
        try:
            if hasattr(self.app, 'root'):
                # Erstelle Benachrichtigungscenter
                self.notification_center = ModernNotificationCenter(
                    self.app.root,
                    max_notifications=5
                )
                
                # Positioniere in der oberen rechten Ecke
                self.notification_center.place(
                    relx=1.0, rely=0.0, anchor="ne", x=-20, y=20
                )
                
                self.modern_components['notifications'] = self.notification_center
                
                # Begrüßungsbenachrichtigung
                self.notification_center.show_notification(
                    "GUI-Verbesserungen aktiviert! 🎉",
                    "success",
                    5000
                )
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Benachrichtigungssystems: {e}")
    
    def _add_ripple_effect(self, widget):
        """Fügt Ripple-Effekt zu einem Widget hinzu."""
        try:
            def create_ripple(event):
                # Vereinfachter Ripple-Effekt
                ModernAnimations.scale_animation(widget, 1.0, 1.05, 0.1)
                widget.after(100, lambda: ModernAnimations.scale_animation(widget, 1.05, 1.0, 0.1))
            
            widget.bind('<Button-1>', create_ripple)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Ripple-Effekts: {e}")
    
    def _on_global_search(self, query: str):
        """Behandelt globale Suchanfragen."""
        try:
            if self.modern_components.get('notifications'):
                self.modern_components['notifications'].show_notification(
                    f"Suche: '{query}' wird verarbeitet...",
                    "info",
                    3000
                )
                
            # Hier würde die tatsächliche Suchlogik stehen
            self.logger.info(f"Globale Suche: {query}")
            
        except Exception as e:
            self.logger.error(f"Fehler bei der globalen Suche: {e}")
    
    def show_notification(self, message: str, notification_type: str = "info", duration: int = 4000):
        """Zeigt eine Benachrichtigung an."""
        try:
            if self.modern_components.get('notifications'):
                self.modern_components['notifications'].show_notification(
                    message, notification_type, duration
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Anzeigen der Benachrichtigung: {e}")
    
    def update_progress(self, section: str, progress: float):
        """Aktualisiert den Fortschritt einer Sektion."""
        try:
            if section == "upload" and hasattr(self.app, 'welcome_screen'):
                upload_section = getattr(self.app.welcome_screen, 'upload_section', None)
                if upload_section and hasattr(upload_section, 'progress_bar'):
                    upload_section.progress_bar.set_progress(progress, animated=True)
                    
                    # Zeige Fortschrittsbalken
                    progress_frame = upload_section.progress_bar.master
                    if progress_frame and hasattr(progress_frame, 'grid'):
                        progress_frame.grid()
                        
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Fortschritts: {e}")
    
    def set_section_status(self, section: str, status: str):
        """Setzt den Status einer Sektion."""
        try:
            if section == "upload" and hasattr(self.app, 'welcome_screen'):
                upload_section = getattr(self.app.welcome_screen, 'upload_section', None)
                if upload_section and hasattr(upload_section, 'status_indicator'):
                    upload_section.status_indicator.set_status(status, animated=True)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen des Sektionsstatus: {e}")
    
    def get_modern_component(self, component_name: str):
        """Gibt eine moderne Komponente zurück."""
        return self.modern_components.get(component_name)
    
    def toggle_animations(self, enabled: bool):
        """Schaltet Animationen ein/aus."""
        self.animations_enabled = enabled
        
        if enabled:
            self.show_notification("Animationen aktiviert", "success", 2000)
        else:
            self.show_notification("Animationen deaktiviert", "info", 2000)


# Hilfsfunktion für die Integration
def integrate_modern_ui(app_instance):
    """
    Integriert moderne UI-Verbesserungen in eine bestehende App-Instanz.
    
    Args:
        app_instance: Die Checker-App-Instanz
    
    Returns:
        ModernUIIntegration: Die UI-Integration-Instanz
    """
    try:
        integration = ModernUIIntegration(app_instance)
        return integration
    except Exception as e:
        print(f"Fehler bei der Integration der modernen UI: {e}")
        return None
