"""
Checker-App - Hauptanwendung mit Welcome-Screen-basierter Workflow-Architektur

Diese Anwendung bietet verschiedene Workflows für Übersetzungsdienstleistungen:
- Angebotsanalyse (AC36)
- Prüfung (v1-v5)
- Finalisierung
- Projektübersicht

Alle Workflows sind über den zentralen Welcome-Screen zugänglich.
"""

# Standard Library Imports
import datetime
import gc
import json
import logging
import os
import platform
import subprocess
import sys
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional

# Third-Party Imports
import customtkinter as ctk
import psutil
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

# Local Application Imports
import nuclear_scaling_killer
from error_handlers import CrashRecoveryManager, EnhancedLogger, ErrorMonitor
from fluent_icons_manager import FluentIconManager
from improved_drag_drop import get_improved_dnd_manager
from kunden_manager import KundenManager
from kunden_manager_v2 import KundenManagerV2
from ui_theme import UITheme
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

# Workflow Imports
from angebots_workflow import AngebotsanalyseWorkflow


# Einheitlicher Button-Style wird in der Klasse nach Root-Erstellung initialisiert
BUTTON_STYLE = None


class CheckerApp:
    """
    Hauptanwendung für die Checker-App mit modernem Welcome-Screen
    und integriertem Kundenmanagement-System
    """
    
    def __init__(self):
        """Initialisiert die Checker-App"""
        print("[MAIN] Initializing CheckerApp...")
        
        # Logging setup
        self.setup_logging()
        
        # Core initialization
        self.init_core_components()
        
        # UI initialization
        self.init_ui_components()
        
        # Workflow initialization
        self.init_workflows()
        
        print("[MAIN] CheckerApp initialization complete")
    
    def on_closing(self):
        """Handles the application closing event"""
        try:
            self.logger.info("[MAIN] Application closing...")
            
            # Save any pending data
            if hasattr(self, 'welcome_screen') and self.welcome_screen:
                # Save recent projects or other data
                pass
            
            # Close the application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"[ERROR] Error during application closing: {e}")
            self.root.quit()
    
    @property
    def workflow_routes(self):
        """Returns workflow routes for the welcome screen"""
        return {
            'angebots_workflow': {
                'name': 'Angebotsanalyse',
                'icon': 'euro-money-2',
                'description': 'Erstelle professionelle Angebote',
                'callback': lambda: self.start_workflow_with_context('angebots_workflow')
            },
            'pruefung_workflow': {
                'name': 'Dateiprüfung',
                'icon': 'check',
                'description': 'Prüfe Übersetzungen auf Qualität',
                'callback': lambda: self.start_workflow_with_context('pruefung_workflow')
            },
            'finalisierung_workflow': {
                'name': 'Finalisierung',
                'icon': 'success',
                'description': 'Finalisiere Projekte',
                'callback': lambda: self.start_workflow_with_context('finalisierung_workflow')
            },
            'projekt_workflow': {
                'name': 'Projektübersicht',
                'icon': 'project',
                'description': 'Verwalte deine Projekte',
                'callback': lambda: self.start_workflow_with_context('projekt_workflow')
            }
        }
    
    def get_icon(self, icon_name, size=(24, 24)):
        """
        Returns an icon for the given name and size.
        Loads real PNG icons from assets/icons folder using CTkImage.
        """
        try:
            import customtkinter as ctk
            from PIL import Image
            import os
            
            # Map icon names to actual file names
            icon_mapping = {
                'home': 'home.png',
                'file': 'file.png',
                'customer': 'businesswoman.png',
                'workflow': 'toolbox.png',
                'tools': 'settings.png',
                'help': 'info.png',
                'settings': 'settings.png',
                'check': 'check-mark.png',
                'close': 'close.png',
                'play': 'play.png',
                'pdf': 'pdf-file.png',
                'doc': 'doc-file.png',
                'quality': 'quality.png',
                'report': 'report.png',
                'translation': 'translation.png',
                'team': 'team.png',
                'idea': 'idea.png',
                'restart': 'restart.png',
                'plus': 'plus.png',
                'upload': 'plus.png',  # Use plus icon for upload
                'euro-money-2': 'report.png',  # Use report icon for money
                'success': 'check-mark.png',  # Use check-mark for success
                'project': 'file.png'  # Use file icon for project
            }
            
            # Get the correct filename
            filename = icon_mapping.get(icon_name, f'{icon_name}.png')
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icons', filename)
            
            if not os.path.exists(icon_path):
                self.logger.warning(f"[ICON] Icon file not found: {icon_path}")
                return None
            
            # Load image using PIL
            image = Image.open(icon_path)
            image = image.convert("RGBA")  # Ensure RGBA for transparency
            
            # Create CTkImage for better scaling on HighDPI
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
            
            # Store reference to prevent garbage collection
            if not hasattr(self, '_icon_cache'):
                self._icon_cache = {}
            cache_key = f"{icon_name}_{size[0]}x{size[1]}"
            self._icon_cache[cache_key] = ctk_image
            
            return ctk_image
            
        except Exception as e:
            self.logger.error(f"[ICON] Error loading icon '{icon_name}': {e}")
            return None
    
    def setup_logging(self):
        """Setzt das Logging-System auf"""
        try:
            # Use basic logging for now
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("CheckerApp")
            self.logger.info("[INIT] Logging system initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize logging: {e}")
            # Fallback to print statements
            self.logger = logging.getLogger("CheckerApp")
    
    def init_core_components(self):
        """Initialisiert die Kernkomponenten"""
        try:
            # IMPROVED: Versuche zuerst CTk für bessere Layout-Kompatibilität
            try:
                self.root = ctk.CTk()
                self.root.title("Checker Pro Suite")
                self.root.geometry("1400x900")
                
                # Apply CustomTkinter theming
                ctk.set_appearance_mode("Light")
                ctk.set_default_color_theme("blue")
                
                # Versuche Drag & Drop zu aktivieren - falls möglich
                try:
                    from tkinterdnd2 import dnd_bind_drag_and_drop
                    # Aktiviere Drag & Drop für bestimmte Widgets später
                    self.logger.info("[INIT] Using CTk with limited drag & drop support")
                except ImportError:
                    self.logger.info("[INIT] Using CTk without drag & drop support")
                    
            except Exception as ctk_error:
                self.logger.warning(f"[INIT] CTk initialization failed: {ctk_error}")
                # Fallback zu TkinterDnD nur wenn CTk nicht funktioniert
                self.root = TkinterDnD.Tk()
                self.root.title("Checker Pro Suite")
                self.root.geometry("1400x900")
                
                # Apply CustomTkinter theming to the TkinterDnD window
                ctk.set_appearance_mode("Light")
                ctk.set_default_color_theme("blue")
                self.logger.info("[INIT] Using TkinterDnD fallback")
            
            # Initialisiere Button-Style nach Root-Erstellung
            global BUTTON_STYLE
            BUTTON_STYLE = {
                "font": ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                "fg_color": ("#F7F9FC", "#23272F"),
                "hover_color": ("#E0E7EF", "#353B48"),
                "text_color": ("#23272F", "#F7F9FC"),
                "corner_radius": 8,
                "border_width": 0
            }
            
            # Customer management
            self.kunden_manager = KundenManager()
            self.kunden_manager_v2 = KundenManagerV2()
            
            # Icon manager
            try:
                self.icon_manager = FluentIconManager()
            except Exception as e:
                self.logger.warning(f"[INIT] Could not initialize icon manager: {e}")
                self.icon_manager = None
            
            # Workflow status
            self.workflow_status = {
                'current_workflow': None,
                'workflow_history': [],
                'last_project_data': None
            }
            
            # Initialize workflows dict
            self.workflows = {}
            
            # Create menu bar
            self.create_menu_bar()
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Bind window resize event
            self.root.bind("<Configure>", self._on_window_resize)
            
            # Initialize improved drag & drop manager (optional)
            try:
                self.drag_drop_manager = get_improved_dnd_manager(self.root)
                self.logger.info("[INIT] Improved Drag & Drop Manager initialized")
            except Exception as e:
                self.logger.warning(f"[INIT] Could not initialize Drag & Drop Manager: {e}")
                self.drag_drop_manager = None
            
            # Drag & Drop overlay (initial versteckt)
            self.drag_drop_overlay = self._create_drag_drop_overlay(self.root)
            
            # Status bar
            self.status_bar = self._create_status_bar()
            
            self.logger.info("[INIT] Core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"[INIT] Error initializing core components: {e}")
            raise
    
    def init_ui_components(self):
        """Initialisiert die UI-Komponenten"""
        try:
            # Welcome Screen
            self.welcome_screen = UltraModernWelcomeScreen(
                master=self.root,
                app=self
            )
            
            # Show welcome screen initially
            self.show_welcome_screen()
            
            # Window management
            self.center_window_on_screen()
            
            # Initialize enhanced UI features
            try:
                self._add_keyboard_shortcuts()
            except Exception as e:
                self.logger.warning(f"[INIT] Could not add keyboard shortcuts: {e}")
            
            # Initialize notification system
            try:
                self._create_notification_system()
            except Exception as e:
                self.logger.warning(f"[INIT] Could not create notification system: {e}")
            
            # Show welcome notification
            try:
                self._show_notification("✨ Willkommen bei Checker Pro Suite! Alle Systeme bereit.", "success", 3000)
            except Exception as e:
                self.logger.warning(f"[INIT] Could not show welcome notification: {e}")
            
            self.logger.info("[INIT] UI components initialized with enhanced features")
            
        except Exception as e:
            self.logger.error(f"[INIT] Error initializing UI components: {e}")
            # Don't raise - continue with partial functionality
            self.logger.warning("[INIT] Continuing with partial UI functionality")
            
        # Copilot: Stelle sicher, dass nur der Welcome-Screen sichtbar ist nach der Initialisierung
        self.ensure_welcome_screen_visible()
    
    def init_workflows(self):
        """Initialisiert die Workflows mit verbesserter Fehlerbehandlung"""
        try:
            # Ensure workflows dict exists
            if not hasattr(self, 'workflows') or self.workflows is None:
                self.workflows = {}
            
            # Initialize workflow instances with enhanced error handling
            self._init_angebots_workflow()
            self._init_pruefung_workflow()
            self._init_finalisierung_workflow()
            self._init_projekt_workflow()
            
            workflows_count = len(self.workflows) if self.workflows else 0
            self.logger.info(f"[WORKFLOW_INIT] {workflows_count} workflows initialized successfully")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_INIT] Error initializing workflows: {e}")
            # Ensure workflows dict exists even on error
            if not hasattr(self, 'workflows') or self.workflows is None:
                self.workflows = {}
            self.logger.info(f"[WORKFLOW_INIT] Fallback: {len(self.workflows)} workflows available")
    
    def _init_angebots_workflow(self):
        """Initialisiert den Angebots-Workflow"""
        try:
            # Ensure required attributes exist
            if not hasattr(self, 'root') or self.root is None:
                raise ValueError("Root window not initialized")
            
            workflow = AngebotsanalyseWorkflow(
                root=self.root,
                app=self,
                back_to_welcome_callback=self.return_to_welcome
            )
            
            # Verify workflow was created successfully
            if workflow is not None:
                self.workflows['angebots_workflow'] = workflow
                self.logger.info("[WORKFLOW_INIT] Angebots workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_INIT] Angebots workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_INIT] Could not initialize angebots_workflow: {e}")
            # Create a stub workflow to prevent UI errors
            self._create_stub_workflow('angebots_workflow', 'Angebotsanalyse')
    
    def _init_pruefung_workflow(self):
        """Initialisiert den Prüfungs-Workflow"""
        try:
            from pruefung_workflow import PruefungWorkflow
            
            workflow = PruefungWorkflow(
                parent=self.root,
                app=self,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['pruefung_workflow'] = workflow
                self.logger.info("[WORKFLOW_INIT] Pruefung workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_INIT] Pruefung workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_INIT] Could not initialize pruefung_workflow: {e}")
            self._create_stub_workflow('pruefung_workflow', 'Dateiprüfung')
    
    def _init_finalisierung_workflow(self):
        """Initialisiert den Finalisierungs-Workflow"""
        try:
            from finalisierung_workflow2 import FinalisierungsWorkflow
            
            workflow = FinalisierungsWorkflow(
                parent=self.root,
                app=self,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['finalisierung_workflow'] = workflow
                self.logger.info("[WORKFLOW_INIT] Finalisierung workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_INIT] Finalisierung workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_INIT] Could not initialize finalisierung_workflow: {e}")
            self._create_stub_workflow('finalisierung_workflow', 'Finalisierung')
    
    def _init_projekt_workflow(self):
        """Initialisiert den Projekt-Workflow"""
        try:
            from projekt_workflow import ProjektWorkflow
            
            # ❌ FEHLER BEHOBEN: Kein Container mehr verwenden 
            # Das ProjektWorkflow sollte direkt mit self.root als parent erstellt werden
            workflow = ProjektWorkflow(
                parent=self.root,
                app=self,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['projekt_workflow'] = workflow
                self.logger.info("[WORKFLOW_INIT] Projekt workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_INIT] Projekt workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_INIT] Could not initialize projekt_workflow: {e}")
            self._create_stub_workflow('projekt_workflow', 'Projektübersicht')
    
    def _create_stub_workflow(self, workflow_name, display_name):
        """Erstellt einen Stub-Workflow als Fallback"""
        try:
            # Copilot: Stub-Workflow-Frame NICHT automatisch anzeigen
            stub_frame = ctk.CTkFrame(self.root)
            
            # Add a simple message
            message_label = ctk.CTkLabel(
                stub_frame,
                text=f"{display_name} wird geladen...",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
            )
            message_label.pack(expand=True, fill="both", padx=50, pady=50)
            
            # Add a back button
            back_button = ctk.CTkButton(
                stub_frame,
                text="Zurück zur Übersicht",
                command=self.return_to_welcome,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            )
            back_button.pack(pady=20)
            
            # WICHTIG: Stub sofort verstecken, damit Welcome-Screen sichtbar bleibt
            stub_frame.pack_forget()
            
            # Store the stub
            self.workflows[workflow_name] = stub_frame
            self.logger.info(f"[WORKFLOW_INIT] Created stub for {workflow_name}")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_INIT] Error creating stub for {workflow_name}: {e}")
    
    def center_window_on_screen(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        try:
            # Update window to get correct dimensions
            self.root.update_idletasks()
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Get window dimensions
            window_width = self.root.winfo_reqwidth()
            window_height = self.root.winfo_reqheight()
            
            # If window size is not set, use default
            if window_width <= 1:
                window_width = 1400
            if window_height <= 1:
                window_height = 900
            
            # Calculate position to center the window
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Set window position and ensure proper size
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Ensure minimum size
            self.root.minsize(1200, 800)
            
            # Ensure clean layout after centering
            self.root.after(100, self._ensure_clean_layout)
            
            self.logger.info(f"[WINDOW] Window centered at {x}x{y} with size {window_width}x{window_height}")
            
        except Exception as e:
            self.logger.error(f"[WINDOW] Error centering window: {e}")
    
    def show_welcome_screen(self):
        """
        Copilot: Zeigt den Welcome Screen an und versteckt alle Workflows.
        Diese Methode sollte der einzige Weg sein, zum Welcome-Screen zurückzukehren.
        """
        try:
            # Verwende die neue Methode für sauberes Layout
            self._ensure_clean_layout()
            
            self.logger.info("[NAVIGATION] Welcome screen shown and visible")
                
        except Exception as e:
            self.logger.error(f"[NAVIGATION] Error showing welcome screen: {e}")
    
    def ensure_welcome_screen_visible(self):
        """
        Copilot: Stellt sicher, dass nur der Welcome-Screen sichtbar ist und alle anderen Workflows versteckt sind.
        Diese Methode behebt das Problem, dass Workflows automatisch angezeigt werden.
        """
        try:
            # Verwende die neue Methode für sauberes Layout
            self._ensure_clean_layout()
            
            self.logger.info("[VISIBILITY] Welcome screen is now visible")
                
        except Exception as e:
            self.logger.error(f"[VISIBILITY] Error ensuring welcome screen visibility: {e}")
    
    def _add_tooltip(self, widget, text):
        """
        Adds a tooltip to a widget with modern styling and enhanced features.
        Tooltips improve user experience by providing helpful information.
        """
        try:
            def on_enter(event):
                """Show tooltip on mouse enter with smooth animation"""
                try:
                    # Create tooltip window with glassmorphism effect
                    tooltip = ctk.CTkToplevel(self.root)
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry("+{}+{}".format(event.x_root + 10, event.y_root + 10))
                    tooltip.configure(
                        fg_color=("#2B2B2B", "#F0F0F0"),
                        bg_color="transparent"
                    )
                    tooltip.attributes("-alpha", 0.95)  # Semi-transparent for glassmorphism
                    
                    # Add subtle border for modern look
                    tooltip.configure(border_width=1, border_color=("#4A4A4A", "#E0E0E0"))
                    
                    # Add tooltip text with enhanced styling
                    label = ctk.CTkLabel(
                        tooltip,
                        text=text,
                        font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),
                        text_color=("#FFFFFF", "#000000"),
                        wraplength=350,
                        justify="left",
                        corner_radius=8
                    )
                    label.pack(padx=12, pady=8)
                    
                    # Store tooltip reference
                    widget._tooltip = tooltip
                    
                    # Smooth fade-in animation
                    tooltip.attributes("-alpha", 0.0)
                    self._animate_tooltip_fade_in(tooltip)
                    
                    # Auto-hide after 6 seconds
                    self.root.after(6000, lambda: self._hide_tooltip(widget))
                    
                except Exception as e:
                    self.logger.debug(f"[TOOLTIP] Error showing enhanced tooltip: {e}")
            
            def on_leave(event):
                """Hide tooltip on mouse leave with smooth animation"""
                self._hide_tooltip(widget, animate=True)
            
            # Bind events
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
        except Exception as e:
            self.logger.debug(f"[TOOLTIP] Error adding enhanced tooltip: {e}")
    
    def _animate_tooltip_fade_in(self, tooltip, alpha=0.0, step=0.05):
        """Animates tooltip fade-in effect"""
        try:
            if alpha < 0.95:
                alpha += step
                tooltip.attributes("-alpha", alpha)
                self.root.after(10, lambda: self._animate_tooltip_fade_in(tooltip, alpha, step))
        except Exception as e:
            pass
    
    def _hide_tooltip(self, widget, animate=False):
        """Hides the tooltip for a widget with optional animation"""
        try:
            if hasattr(widget, '_tooltip') and widget._tooltip:
                if animate:
                    self._animate_tooltip_fade_out(widget._tooltip)
                else:
                    widget._tooltip.destroy()
                    widget._tooltip = None
        except Exception as e:
            self.logger.debug(f"[TOOLTIP] Error hiding tooltip: {e}")
    
    def _animate_tooltip_fade_out(self, tooltip, alpha=0.95, step=0.1):
        """Animates tooltip fade-out effect"""
        try:
            if alpha > 0:
                alpha -= step
                tooltip.attributes("-alpha", alpha)
                self.root.after(10, lambda: self._animate_tooltip_fade_out(tooltip, alpha, step))
            else:
                tooltip.destroy()
        except Exception as e:
            pass
    
    def _add_keyboard_shortcuts(self):
        """Adds keyboard shortcuts for improved user experience"""
        try:
            # File operations
            self.root.bind('<Control-n>', lambda e: self.create_new_project())
            self.root.bind('<Control-o>', lambda e: self.open_project())
            self.root.bind('<Control-s>', lambda e: self.save_project())
            self.root.bind('<Control-q>', lambda e: self.exit_application())
            
            # Theme and settings
            self.root.bind('<Control-t>', lambda e: self.toggle_theme())
            self.root.bind('<Control-comma>', lambda e: self.show_settings())
            
            # Workflow shortcuts (mit Ctrl für Sicherheit und Bestätigung)
            self.root.bind('<Control-F1>', lambda e: self.start_workflow_with_context("angebots_workflow", confirm=True))
            self.root.bind('<Control-F2>', lambda e: self.start_workflow_with_context("pruefung_workflow", confirm=True))
            self.root.bind('<Control-F3>', lambda e: self.start_workflow_with_context("finalisierung_workflow", confirm=True))
            self.root.bind('<Control-F4>', lambda e: self.start_workflow_with_context("projekt_workflow", confirm=True))
            
            # Navigation
            self.root.bind('<Escape>', lambda e: self.return_to_welcome())
            self.root.bind('<F5>', lambda e: self.reload_application())
            
            # Help (F1 ohne Konflikt)
            self.root.bind('<F1>', lambda e: self.show_help_menu())
            
            self.logger.info("[KEYBOARD] Keyboard shortcuts initialized")
            
        except Exception as e:
            self.logger.error(f"[KEYBOARD] Error adding keyboard shortcuts: {e}")
    
    def _add_glassmorphism_effects(self, widget, blur_radius=10, opacity=0.85):
        """Adds glassmorphism effects to widgets for modern appearance"""
        try:
            # Configure semi-transparent background
            widget.configure(
                fg_color=("#FFFFFF", "#2B2B2B"),
                bg_color="transparent",
                corner_radius=12
            )
            
            # Add subtle border
            widget.configure(
                border_width=1,
                border_color=("#E0E0E0", "#404040")
            )
            
            # Apply transparency
            if hasattr(widget, 'attributes'):
                widget.attributes("-alpha", opacity)
            
            self.logger.debug("[GLASS] Glassmorphism effects applied")
            
        except Exception as e:
            self.logger.debug(f"[GLASS] Error applying glassmorphism: {e}")
    
    def _add_hover_animations(self, widget, scale_factor=1.02, duration=100):
        """Adds subtle hover animations to widgets"""
        try:
            original_width = widget.cget("width")
            original_height = widget.cget("height")
            
            def on_enter(event):
                """Animate widget on hover"""
                try:
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    
                    # Smooth scale animation
                    widget.configure(width=new_width, height=new_height)
                    
                    # Add subtle shadow effect
                    widget.configure(
                        border_width=2,
                        border_color=("#3B82F6", "#60A5FA")
                    )
                    
                except Exception as e:
                    pass
            
            def on_leave(event):
                """Reset widget on leave"""
                try:
                    widget.configure(width=original_width, height=original_height)
                    widget.configure(
                        border_width=1,
                        border_color=("#E0E0E0", "#404040")
                    )
                except Exception as e:
                    pass
            
            # Bind hover events
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
        except Exception as e:
            self.logger.debug(f"[ANIMATION] Error adding hover animation: {e}")
    
    def _create_progress_indicator(self, parent, text="Loading...", progress=0.0):
        """Creates a modern progress indicator for workflow operations"""
        try:
            # Create progress container
            progress_frame = ctk.CTkFrame(
                parent,
                fg_color=("#F8F9FA", "#2B2B2B"),
                corner_radius=12,
                border_width=1,
                border_color=("#E0E0E0", "#404040")
            )
            
            # Progress label
            progress_label = ctk.CTkLabel(
                progress_frame,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=("#4A4A4A", "#E0E0E0")
            )
            progress_label.pack(pady=(15, 5))
            
            # Progress bar with modern styling
            progress_bar = ctk.CTkProgressBar(
                progress_frame,
                width=300,
                height=6,
                corner_radius=3,
                fg_color=("#E0E0E0", "#404040"),
                progress_color=("#3B82F6", "#60A5FA")
            )
            progress_bar.pack(pady=(0, 15))
            progress_bar.set(progress)
            
            return progress_frame, progress_bar, progress_label
            
        except Exception as e:
            self.logger.error(f"[PROGRESS] Error creating progress indicator: {e}")
            return None, None, None
    
    def _create_drag_drop_overlay(self, parent):
        """Creates a visual overlay for drag and drop operations"""
        try:
            # Create overlay frame
            overlay = ctk.CTkFrame(
                parent,
                fg_color=("#E3F2FD", "#1E3A8A"),
                border_width=2,
                border_color=("#3B82F6", "#60A5FA"),
                corner_radius=12
            )
            
            # Add drag & drop icon and text
            icon_label = ctk.CTkLabel(
                overlay,
                text="📁",
                font=ctk.CTkFont(family="Segoe UI", size=48),
                text_color=("#3B82F6", "#60A5FA")
            )
            icon_label.pack(pady=(40, 10))
            
            text_label = ctk.CTkLabel(
                overlay,
                text="Dateien hierher ziehen und ablegen",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=("#3B82F6", "#60A5FA")
            )
            text_label.pack(pady=(0, 40))
            
            # Initially hide overlay - sicherstellen, dass es versteckt ist
            overlay.place_forget()
            overlay.pack_forget()  # Zusätzlich auch pack_forget
            
            return overlay
            
        except Exception as e:
            self.logger.error(f"[DRAG_DROP] Error creating drag drop overlay: {e}")
            return None
    
    def _show_drag_drop_overlay(self, overlay):
        """Shows the drag & drop overlay with animation"""
        try:
            if overlay:
                overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.6)
                # Fade in animation
                overlay.configure(fg_color=("#F0F8FF", "#1A237E"))
                self.root.after(50, lambda: overlay.configure(fg_color=("#E3F2FD", "#1E3A8A")))
        except Exception as e:
            self.logger.debug(f"[DRAG_DROP] Error showing overlay: {e}")
    
    def _hide_drag_drop_overlay(self, overlay):
        """Hides the drag & drop overlay with animation"""
        try:
            if overlay:
                # Fade out animation
                overlay.configure(fg_color=("#F0F8FF", "#1A237E"))
                self.root.after(100, lambda: overlay.place_forget())
        except Exception as e:
            self.logger.debug(f"[DRAG_DROP] Error hiding overlay: {e}")
    
    def _create_status_bar(self):
        """Creates a modern status bar with glassmorphism effect"""
        try:
            # Create status bar container
            status_bar = ctk.CTkFrame(
                self.root,
                height=32,
                corner_radius=0,
                fg_color=("#F8F9FA", "#2B2B2B"),
                border_width=1,
                border_color=("#E0E0E0", "#404040")
            )
            status_bar.pack(fill="x", side="bottom", padx=0, pady=0)
            status_bar.pack_propagate(False)
            
            # Left side - Status text
            self.status_label = ctk.CTkLabel(
                status_bar,
                text="✅ Bereit",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            self.status_label.pack(side="left", padx=15, pady=6)
            
            # Right side - Version info
            version_label = ctk.CTkLabel(
                status_bar,
                text="v2.0.0 Pro",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            version_label.pack(side="right", padx=15, pady=6)
            
            # Store reference to status bar for cleanup
            self.status_bar_widget = status_bar
            
            return status_bar
            
        except Exception as e:
            self.logger.error(f"[STATUS] Error creating status bar: {e}")
            return None
    
    def _update_status(self, message, status_type="info"):
        """Updates the status bar with a message and icon"""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                # Status icons
                icons = {
                    "info": "ℹ️",
                    "success": "✅",
                    "warning": "⚠️",
                    "error": "❌",
                    "loading": "⏳"
                }
                
                icon = icons.get(status_type, "ℹ️")
                self.status_label.configure(text=f"{icon} {message}")
                
                # Auto-clear after 5 seconds for non-critical messages
                if status_type in ["info", "success"]:
                    self.root.after(5000, lambda: self._update_status("Bereit", "success"))
                    
        except Exception as e:
            self.logger.debug(f"[STATUS] Error updating status: {e}")
    
    def _add_context_menu_to_widget(self, widget, menu_items):
        """Adds a right-click context menu to any widget"""
        try:
            def show_context_menu(event):
                try:
                    # Create context menu
                    context_menu = tk.Menu(self.root, tearoff=0)
                    
                    for item in menu_items:
                        if isinstance(item, tuple) and len(item) == 2:
                            text, callback = item
                            if text == "---":
                                context_menu.add_separator()
                            else:
                                context_menu.add_command(label=text, command=callback)
                    
                    # Show menu at cursor position
                    context_menu.post(event.x_root, event.y_root)
                    
                except Exception as e:
                    self.logger.debug(f"[CONTEXT_MENU] Error showing context menu: {e}")
            
            # Bind right-click event
            widget.bind("<Button-3>", show_context_menu)  # Right-click
            
        except Exception as e:
            self.logger.debug(f"[CONTEXT_MENU] Error adding context menu: {e}")
    
    def _create_notification_system(self):
        """Creates a modern notification system"""
        try:
            self.notifications = []
            self.notification_container = ctk.CTkFrame(
                self.root,
                fg_color="transparent",
                bg_color="transparent"
            )
            # WICHTIG: Notification-Container initial verstecken
            self.notification_container.place_forget()
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error creating notification system: {e}")
    
    def _show_notification(self, message, notification_type="info", duration=4000):
        """Shows a modern notification with auto-dismiss"""
        try:
            if not hasattr(self, 'notification_container'):
                self._create_notification_system()
            
            # Sicherstellen, dass der Container sichtbar ist
            self.notification_container.place(relx=1.0, rely=0.1, anchor="ne", x=-20, y=20)
            
            # Notification colors and icons
            colors = {
                "info": ("#3B82F6", "#60A5FA"),
                "success": ("#10B981", "#34D399"),
                "warning": ("#F59E0B", "#FBBF24"),
                "error": ("#EF4444", "#F87171")
            }
            
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            
            bg_color, text_color = colors.get(notification_type, colors["info"])
            icon = icons.get(notification_type, "ℹ️")
            
            # Create notification frame
            notification = ctk.CTkFrame(
                self.notification_container,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=text_color
            )
            
            # Add notification content
            content_frame = ctk.CTkFrame(notification, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=12, pady=8)
            
            # Icon and message
            message_label = ctk.CTkLabel(
                content_frame,
                text=f"{icon} {message}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="white",
                wraplength=300
            )
            message_label.pack(side="left", fill="both", expand=True)
            
            # Close button
            close_btn = ctk.CTkButton(
                content_frame,
                text="✕",
                width=20,
                height=20,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("#F0F0F0", "#333333"),
                text_color="white",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                command=lambda: self._hide_notification(notification)
            )
            close_btn.pack(side="right", padx=(8, 0))
            
            # Position notification
            y_offset = len(self.notifications) * 70
            notification.place(relx=0, rely=0, anchor="nw", y=y_offset)
            
            # Store notification reference
            self.notifications.append(notification)
            
            # Auto-hide after duration
            self.root.after(duration, lambda: self._hide_notification(notification))
            
            # Slide-in animation
            self._animate_notification_slide_in(notification)
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error showing notification: {e}")
    
    def _hide_notification(self, notification):
        """Hides a notification with slide-out animation"""
        try:
            if notification in self.notifications:
                self.notifications.remove(notification)
                
                # Slide-out animation
                self._animate_notification_slide_out(notification)
                
                # Reposition remaining notifications
                for i, notif in enumerate(self.notifications):
                    notif.place(relx=0, rely=0, anchor="nw", y=i * 70)
                
                # Verstecke den Container wenn keine Notifications mehr vorhanden sind
                if not self.notifications:
                    self.notification_container.place_forget()
                    
        except Exception as e:
            self.logger.debug(f"[NOTIFICATION] Error hiding notification: {e}")
    
    def _animate_notification_slide_in(self, notification, x_offset=300):
        """Animates notification slide-in from right"""
        try:
            if x_offset > 0:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.root.after(10, lambda: self._animate_notification_slide_in(notification, x_offset - 15))
            else:
                notification.place(relx=1.0, rely=0, anchor="ne", x=0)
        except Exception as e:
            pass
    
    def _animate_notification_slide_out(self, notification, x_offset=0):
        """Animates notification slide-out to right"""
        try:
            if x_offset < 300:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.root.after(10, lambda: self._animate_notification_slide_out(notification, x_offset + 15))
            else:
                notification.destroy()
        except Exception as e:
            pass
    
    # ===== MENU BAR CREATION =====
    
    def create_menu_bar(self):
        """Creates the ultra-modern menu bar matching your previous beautiful design"""
        try:
            from ui_theme import UITheme
            menu_bar = ctk.CTkFrame(
                self.root, 
                height=65,  # Erhöht für bessere Sichtbarkeit
                corner_radius=0,
                fg_color=("#F7F9FC", "#1E1E1E"),
                border_width=0
            )
            menu_bar.pack(fill="x", padx=0, pady=0)
            menu_bar.pack_propagate(False)
            
            # Hauptcontainer für bessere Kontrolle
            main_container = ctk.CTkFrame(
                menu_bar,
                fg_color="transparent",
                corner_radius=0
            )
            main_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            menu_container = ctk.CTkFrame(
                main_container, 
                fg_color="transparent",
                corner_radius=0
            )
            menu_container.pack(side="left", padx=20, pady=2)
            
            controls_container = ctk.CTkFrame(
                main_container,
                fg_color="transparent", 
                corner_radius=0
            )
            controls_container.pack(side="right", padx=20, pady=2)
            menus = [
                ("file", "Datei", self.show_file_menu, "#6C757D"),
                ("customer", "Kunden", self.show_customer_menu, "#F59E0B"),
                ("workflow", "Workflows", self.show_workflow_menu, "#0078D7"),
                ("tools", "Tools", self.show_tools_menu, "#F59E0B"),
                ("help", "Hilfe", self.show_help_menu, "#0078D7")
            ]
            self.menu_buttons = []
            for i, (icon_name, text, command, accent_color) in enumerate(menus):
                btn_container = ctk.CTkFrame(
                    menu_container,
                    fg_color="transparent",
                    width=85,  # Leicht vergrößert für bessere Lesbarkeit
                    height=55  # Erhöht für bessere Sichtbarkeit
                )
                btn_container.pack(side="left", padx=3)
                btn_container.pack_propagate(False)
                btn = ctk.CTkButton(
                    btn_container,
                    text="",
                    command=command,
                    width=85,
                    height=55,
                    **BUTTON_STYLE
                )
                btn.pack(fill="both", expand=True, padx=1, pady=1)
                icon_image = self.get_icon(icon_name, size=(20, 20))  # Leicht größere Icons
                if icon_image:
                    icon_label = ctk.CTkLabel(
                        btn_container,
                        text="",
                        image=icon_image,
                        bg_color="transparent",
                        width=22,
                        height=22
                    )
                else:
                    fallback_icons = {
                        "file": "📁",
                        "customer": "👥", 
                        "workflow": "⚙️",
                        "tools": "🔧",
                        "help": "❓"
                    }
                    icon_label = ctk.CTkLabel(
                        btn_container,
                        text=fallback_icons.get(icon_name, "📁"),
                        font=ctk.CTkFont(family="Segoe UI", size=20, weight="normal"),  # Größere Icons
                        text_color=accent_color,
                        bg_color="transparent",
                        width=22,
                        height=22
                    )
                icon_label.place(relx=0.5, rely=0.28, anchor="center")  # Leicht höher positioniert
                text_label = ctk.CTkLabel(
                    btn_container,
                    text=text,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),  # Leicht kleinere Schrift
                    text_color=BUTTON_STYLE["text_color"],
                    bg_color="transparent",
                    width=82
                )
                text_label.place(relx=0.5, rely=0.72, anchor="center")  # Besser positioniert
                self._add_tooltip(btn, f"{text}: Klicken Sie hier für {text.lower()}-bezogene Aktionen")
                self._add_hover_animations(btn)
                self.menu_buttons.append(btn)
            self._create_modern_app_controls(controls_container)
            border_frame = ctk.CTkFrame(
                self.root,
                height=1,
                corner_radius=0,
                fg_color=("#E0E0E0", "#3A3A3A")
            )
            border_frame.pack(fill="x", padx=0, pady=0)
            self.logger.info("[MENU] Ultra-modern menu bar with real icons created")
        except Exception as e:
            self.logger.error(f"[MENU] Error creating ultra-modern menu bar: {e}")
            self._create_basic_menu_bar()

    def _create_modern_app_controls(self, container):
        """Creates compact app controls with enhanced tooltips and hover effects"""
        try:
            settings_icon = self.get_icon("settings", size=(16, 16))
            
            # Create theme button with improved sizing
            theme_btn = ctk.CTkButton(
                container,
                text="🌙",
                command=self.toggle_theme,
                width=38,  # Leicht größer
                height=38,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),  # Größerer Text
                fg_color=BUTTON_STYLE["fg_color"],
                hover_color=BUTTON_STYLE["hover_color"],
                text_color=BUTTON_STYLE["text_color"],
                corner_radius=19,
                border_width=0
            )
            theme_btn.pack(side="right", padx=6)
            
            # Create settings button with improved sizing
            if settings_icon:
                settings_btn = ctk.CTkButton(
                    container,
                    text="",
                    image=settings_icon,
                    command=self.show_settings,
                    width=38,
                    height=38,
                    font=BUTTON_STYLE["font"],
                    fg_color="#8B5CF6",
                    hover_color="#7C3AED",
                    text_color="white",
                    corner_radius=19,
                    border_width=0
                )
            else:
                settings_btn = ctk.CTkButton(
                    container,
                    text="⚙️",
                    command=self.show_settings,
                    width=38,
                    height=38,
                    font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                    fg_color="#8B5CF6",
                    hover_color="#7C3AED",
                    text_color="white",
                    corner_radius=19,
                    border_width=0
                )
            settings_btn.pack(side="right", padx=6)
            self._add_tooltip(theme_btn, "🌙/☀️ Theme umschalten: Zwischen Hell- und Dunkelmodus wechseln (Strg+T)")
            self._add_tooltip(settings_btn, "⚙️ Einstellungen: App-Konfiguration und erweiterte Optionen (Strg+,)")
            self._add_hover_animations(theme_btn)
            self._add_hover_animations(settings_btn)
        except Exception as e:
            self.logger.warning(f"[MENU] Could not create modern app controls: {e}")

    def _create_basic_menu_bar(self):
        """Creates a basic fallback menu bar"""
        try:
            menu_bar = ctk.CTkFrame(self.root, height=40)
            menu_bar.pack(fill="x", padx=0, pady=0)
            
            # Simple menu buttons
            menus = [
                ("Datei", self.show_file_menu),
                ("Kunden", self.show_customer_menu),
                ("Workflows", self.show_workflow_menu),
                ("Tools", self.show_tools_menu),
                ("Hilfe", self.show_help_menu)
            ]
            
            for text, command in menus:
                btn = ctk.CTkButton(
                    menu_bar,
                    text=text,
                    command=command,
                    width=80,
                    height=32
                )
                btn.pack(side="left", padx=5, pady=4)
                
            self.logger.info("[MENU] Basic menu bar created")
            
        except Exception as e:
            self.logger.error(f"[MENU] Error creating basic menu bar: {e}")

    def show_file_menu(self):
        """Shows the file menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Neues Projekt", command=self.create_new_project)
            menu.add_command(label="Projekt öffnen", command=self.open_project)
            menu.add_command(label="Projekt speichern", command=self.save_project)
            menu.add_separator()
            menu.add_command(label="Beenden", command=self.exit_application)
            
            # Show menu at current cursor position
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.logger.error(f"[MENU] Error showing file menu: {e}")

    def show_customer_menu(self):
        """Shows the customer menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Neuer Kunde", command=self.create_new_customer)
            menu.add_command(label="Kunde bearbeiten", command=self.edit_customer)
            menu.add_command(label="Kundenliste", command=self.show_customer_list)
            menu.add_separator()
            menu.add_command(label="Kundenimport", command=self.import_customers)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.logger.error(f"[MENU] Error showing customer menu: {e}")

    def show_workflow_menu(self):
        """Shows the workflow menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Angebotsanalyse", command=lambda: self.start_workflow_with_context("angebots_workflow"))
            menu.add_command(label="Dateiprüfung", command=lambda: self.start_workflow_with_context("pruefung_workflow"))
            menu.add_command(label="Finalisierung", command=lambda: self.start_workflow_with_context("finalisierung_workflow"))
            menu.add_command(label="Projektübersicht", command=lambda: self.start_workflow_with_context("projekt_workflow"))
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.logger.error(f"[MENU] Error showing workflow menu: {e}")

    def show_tools_menu(self):
        """Shows the tools menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Einstellungen", command=self.show_settings)
            menu.add_command(label="Theme umschalten", command=self.toggle_theme)
            menu.add_separator()
            menu.add_command(label="Debug-Modus", command=self.toggle_debug_mode)
            menu.add_command(label="Systeminfo", command=self.show_system_info)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.logger.error(f"[MENU] Error showing tools menu: {e}")

    def show_help_menu(self):
        """Shows the help menu"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Hilfe", command=self.show_help)
            menu.add_command(label="Tastaturkürzel", command=self.show_keyboard_shortcuts)
            menu.add_separator()
            menu.add_command(label="Über", command=self.show_about)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.logger.error(f"[MENU] Error showing help menu: {e}")

    def return_to_welcome(self):
        """Returns to the welcome screen"""
        try:
            self.show_welcome_screen()
            self._update_status("Zurück zum Willkommensbildschirm", "info")
            
        except Exception as e:
            self.logger.error(f"[NAVIGATION] Error returning to welcome: {e}")

    # Menu action methods
    def create_new_project(self):
        """Creates a new project"""
        messagebox.showinfo("Neues Projekt", "Funktion wird in Kürze verfügbar sein.")

    def open_project(self):
        """Opens an existing project"""
        file_path = filedialog.askopenfilename(
            title="Projekt öffnen",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Projekt öffnen", f"Projekt wird geladen: {file_path}")

    def save_project(self):
        """Saves the current project"""
        messagebox.showinfo("Projekt speichern", "Projekt wurde gespeichert.")

    def exit_application(self):
        """Exits the application"""
        self.on_closing()

    def create_new_customer(self):
        """Creates a new customer"""
        messagebox.showinfo("Neuer Kunde", "Kundenerstellung wird in Kürze verfügbar sein.")

    def edit_customer(self):
        """Edits an existing customer"""
        messagebox.showinfo("Kunde bearbeiten", "Kundenbearbeitung wird in Kürze verfügbar sein.")

    def show_customer_list(self):
        """Shows the customer list"""
        messagebox.showinfo("Kundenliste", "Kundenliste wird in Kürze verfügbar sein.")

    def import_customers(self):
        """Imports customers from file"""
        messagebox.showinfo("Kundenimport", "Kundenimport wird in Kürze verfügbar sein.")

    def show_settings(self):
        """Shows the settings dialog"""
        messagebox.showinfo("Einstellungen", "Einstellungen werden in Kürze verfügbar sein.")

    def toggle_theme(self):
        """Toggles between light and dark theme"""
        try:
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            self._update_status(f"Theme gewechselt zu {new_mode}", "success")
            
        except Exception as e:
            self.logger.error(f"[THEME] Error toggling theme: {e}")

    def toggle_debug_mode(self):
        """Toggles debug mode"""
        messagebox.showinfo("Debug-Modus", "Debug-Modus wird in Kürze verfügbar sein.")

    def show_system_info(self):
        """Shows system information"""
        info = f"Python: {sys.version}\nPlattform: {platform.platform()}\nCPU: {platform.processor()}"
        messagebox.showinfo("Systeminfo", info)

    def show_help(self):
        """Shows help information"""
        messagebox.showinfo("Hilfe", "Hilfe wird in Kürze verfügbar sein.")

    def show_keyboard_shortcuts(self):
        """Shows keyboard shortcuts"""
        shortcuts = """
Tastaturkürzel:
Strg+N - Neues Projekt
Strg+O - Projekt öffnen
Strg+S - Projekt speichern
Strg+Q - Beenden
Strg+T - Theme umschalten
Strg+, - Einstellungen
Strg+F1 - Angebotsanalyse-Workflow
Strg+F2 - Prüfungs-Workflow
Strg+F3 - Finalisierungs-Workflow
Strg+F4 - Projekt-Workflow
ESC - Zurück zum Willkommensbildschirm
F1 - Hilfe anzeigen
F5 - App neu laden
        """
        messagebox.showinfo("Tastaturkürzel", shortcuts)

    def show_about(self):
        """Shows about information"""
        messagebox.showinfo("Über", "Checker Pro Suite v2.0.0\nModerne Übersetzungsmanagement-Software")

    def start_workflow_with_context(self, workflow_name, confirm=False):
        """Starts a workflow with context and improved error handling"""
        try:
            # Bei Keyboard-Shortcuts: Bestätigung anfordern
            if confirm:
                workflow_names = {
                    'angebots_workflow': 'Angebotsanalyse',
                    'pruefung_workflow': 'Dateiprüfung', 
                    'finalisierung_workflow': 'Finalisierung',
                    'projekt_workflow': 'Projektübersicht'
                }
                
                workflow_display_name = workflow_names.get(workflow_name, workflow_name)
                result = messagebox.askyesno(
                    "Workflow starten", 
                    f"Möchten Sie den Workflow '{workflow_display_name}' starten?"
                )
                
                if not result:
                    self.logger.info(f"[WORKFLOW] User cancelled workflow start: {workflow_name}")
                    return
            
            # Check if workflow exists
            if workflow_name not in self.workflows:
                self._show_notification(f"Workflow '{workflow_name}' nicht verfügbar", "warning")
                self.logger.warning(f"[WORKFLOW] Workflow not found: {workflow_name}")
                return
            
            # Hide welcome screen
            if hasattr(self, 'welcome_screen') and self.welcome_screen:
                self.welcome_screen.pack_forget()
            
            # Hide all other workflows first
            for name, workflow in self.workflows.items():
                if name != workflow_name and hasattr(workflow, 'pack_forget'):
                    workflow.pack_forget()
            
            # Show the requested workflow
            workflow = self.workflows[workflow_name]
            
            # Handle different workflow types
            if hasattr(workflow, 'show_workflow'):
                # Full workflow with show_workflow method
                workflow.show_workflow()
            elif hasattr(workflow, 'pack'):
                # Simple frame workflow
                workflow.pack(fill="both", expand=True)
            else:
                # Unknown workflow type
                self.logger.warning(f"[WORKFLOW] Unknown workflow type for {workflow_name}")
                self._show_notification(f"Workflow '{workflow_name}' kann nicht gestartet werden", "error")
                return
            
            self._update_status(f"Workflow '{workflow_name}' gestartet", "info")
            self.logger.info(f"[WORKFLOW] Started workflow: {workflow_name}")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW] Error starting workflow {workflow_name}: {e}")
            self._show_notification(f"Fehler beim Starten des Workflows: {e}", "error")
            # Return to welcome screen on error
            self.return_to_welcome()

    def reload_application(self):
        """Reloads the application"""
        try:
            messagebox.showinfo("App neu laden", "App wird neu geladen...")
            self.root.quit()
            
        except Exception as e:
            self.logger.error(f"[APP] Error reloading application: {e}")

    def run(self):
        """Starts the application main loop"""
        try:
            self.logger.info("[MAIN] Starting application main loop")
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"[MAIN] Error in main loop: {e}")
            raise

    def _on_window_resize(self, event=None):
        """Handles window resize events to prevent layout issues"""
        try:
            # Nur auf Root-Fenster-Resize-Events reagieren
            if event and event.widget != self.root:
                return
            
            # Stelle sauberes Layout sicher
            self._ensure_clean_layout()
            
            # Update UI state
            self.root.update_idletasks()
            
        except Exception as e:
            self.logger.debug(f"[WINDOW] Error handling window resize: {e}")
    
    def _ensure_clean_layout(self):
        """Ensures all overlays and potential artifacts are properly hidden"""
        try:
            # Verstecke Drag-Drop-Overlay
            if hasattr(self, 'drag_drop_overlay') and self.drag_drop_overlay:
                self.drag_drop_overlay.place_forget()
                self.drag_drop_overlay.pack_forget()
            
            # Verstecke Notification-Container wenn leer
            if hasattr(self, 'notification_container') and not self.notifications:
                self.notification_container.place_forget()
            
            # Verstecke alle Workflows außer dem Welcome-Screen
            if hasattr(self, 'workflows') and self.workflows:
                for workflow_name, workflow in self.workflows.items():
                    if hasattr(workflow, 'pack_forget'):
                        workflow.pack_forget()
                    if hasattr(workflow, 'place_forget'):
                        workflow.place_forget()
                    if hasattr(workflow, 'grid_forget'):
                        workflow.grid_forget()
            
            # Verstecke Status-Bar temporär bei Resize um Layout-Konflikte zu verhindern
            if hasattr(self, 'status_bar_widget') and self.status_bar_widget:
                self.status_bar_widget.pack_forget()
                self.status_bar_widget.pack(fill="x", side="bottom", padx=0, pady=0)
            
            # Stelle sicher, dass Welcome-Screen sichtbar ist
            if hasattr(self, 'welcome_screen') and self.welcome_screen:
                self.welcome_screen.pack(fill="both", expand=True)
            
            self.logger.debug("[LAYOUT] Clean layout ensured")
            
        except Exception as e:
            self.logger.debug(f"[LAYOUT] Error ensuring clean layout: {e}")

# Main execution
if __name__ == "__main__":
    try:
        # Create and run the application
        app = CheckerApp()
        app.run()
    except Exception as e:
        print(f"Critical error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
