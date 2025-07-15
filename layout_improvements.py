"""
Layout & Strukturverbesserungen für Checker App
===============================================

Diese Datei implementiert die Layout- und Strukturverbesserungen:
1. Strikte Trennung: pack() nur für Root-Level (Menu/Status), grid() für Content
2. Einheitliche Abstände durch einfache Konstanten
3. Bessere Spaltengewichtung für responsive Design
"""

import customtkinter as ctk
import logging
from typing import Optional, Any

# Einfache Layout-Konstanten
SPACING_XS = 2
SPACING_S = 4  
SPACING_M = 8
SPACING_L = 12
CORNER_RADIUS = 6


class ImprovedLayoutManager:
    """Verbesserte Layout-Manager-Klasse mit strikter pack/grid Trennung."""
    
    def __init__(self, root: ctk.CTk, logger: Optional[logging.Logger] = None):
        self.root = root
        self.logger = logger or logging.getLogger(__name__)
        self.main_container: Optional[ctk.CTkFrame] = None
        
    def create_optimized_main_container(self) -> ctk.CTkFrame:
        """
        Create the main container with strict pack/grid separation and responsive design.
        
        Returns:
            ctk.CTkFrame: Der optimierte Main Container
        """
        try:
            # Create main container that takes remaining space with pack
            # This creates strict separation: pack() for Root-Level, grid() for Content
            self.main_container = ctk.CTkFrame(
                self.root,
                fg_color="transparent",  # Verwende transparenten Hintergrund
                corner_radius=0,     # Kein Radius für Container
                border_width=0
            )
            
            # STRICT PACK LAYOUT: Nur für Root-Level Komponenten
            self.main_container.pack(
                side="top", 
                fill="both", 
                expand=True, 
                padx=2,      # Einfache Pixel-Werte
                pady=(1, 2)  # Einfache Pixel-Werte
            )
            
            # GRID CONFIGURATION: Bereitet Grid-Layout für Content vor
            # Optimierte Spalten- und Zeilengewichtung für responsive Design
            self._configure_responsive_grid()
            
            self.logger.info("[LAYOUT] Main container created with strict pack/grid separation and responsive design")
            return self.main_container
            
        except Exception as e:
            self.logger.error(f"[LAYOUT] Error creating main container: {e}")
            raise
    
    def _configure_responsive_grid(self) -> None:
        """Configure responsive grid layout for the main container."""
        if not self.main_container:
            return
            
        # Basis-Grid Konfiguration für Single-Column Layout
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Erweiterte Grid-Konfiguration für Multi-Column Layouts
        # Diese können je nach Inhalt aktiviert werden
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(2, weight=1)
        
        # Für flexible Höhenanpassung bei mehreren Zeilen
        self.main_container.grid_rowconfigure(1, weight=0)  # Header/Footer fixed
        self.main_container.grid_rowconfigure(2, weight=0)  # Header/Footer fixed
    
    def create_responsive_welcome_layout(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """
        Create responsive three-column welcome screen layout.
        
        Args:
            parent: Parent container
            
        Returns:
            ctk.CTkFrame: Welcome layout container
        """
        try:
            # Welcome container mit transparentem Hintergrund
            welcome_container = ctk.CTkFrame(parent, fg_color="transparent")
            welcome_container.grid(
                row=0, column=0, 
                sticky="nsew", 
                padx=SPACING_M, 
                pady=SPACING_M
            )
            
            # Three-column responsive grid configuration
            welcome_container.grid_columnconfigure(0, weight=1, uniform="col")  # Projekte
            welcome_container.grid_columnconfigure(1, weight=1, uniform="col")  # Upload
            welcome_container.grid_columnconfigure(2, weight=1, uniform="col")  # Workflows
            welcome_container.grid_rowconfigure(0, weight=1)
            
            # Minimum column widths for responsive behavior
            welcome_container.grid_columnconfigure(0, minsize=400)
            welcome_container.grid_columnconfigure(1, minsize=400)
            welcome_container.grid_columnconfigure(2, minsize=400)
            
            self.logger.info("[LAYOUT] Responsive welcome layout created")
            return welcome_container
            
        except Exception as e:
            self.logger.error(f"[LAYOUT] Error creating welcome layout: {e}")
            raise
    
    def create_section_container(self, parent: ctk.CTkFrame, column: int = 0) -> ctk.CTkFrame:
        """
        Create a standardized section container with consistent styling.
        
        Args:
            parent: Parent container
            column: Grid column position
            
        Returns:
            ctk.CTkFrame: Section container
        """
        try:
            section = ctk.CTkFrame(
                parent,
                fg_color="transparent",
                corner_radius=CORNER_RADIUS,
                border_width=1,
                border_color="#E0E0E0"
            )
            
            # Grid placement with consistent spacing
            section.grid(
                row=0, column=column,
                sticky="nsew",
                padx=(0 if column == 0 else SPACING_S, 
                      0 if column == 2 else SPACING_S),
                pady=0
            )
            
            # Internal grid configuration
            section.grid_rowconfigure(0, weight=0)  # Header
            section.grid_rowconfigure(1, weight=1)  # Content
            section.grid_columnconfigure(0, weight=1)
            
            return section
            
        except Exception as e:
            self.logger.error(f"[LAYOUT] Error creating section container: {e}")
            raise
    
    def apply_consistent_spacing(self, widget, 
                                spacing_type: str = "default") -> None:
        """
        Apply consistent spacing to widgets based on UITheme.
        
        Args:
            widget: The widget to apply spacing to
            spacing_type: Type of spacing ("tight", "default", "loose")
        """
        try:
            spacing_map = {
                "tight": {
                    "padx": SPACING_XS,
                    "pady": SPACING_XS
                },
                "default": {
                    "padx": SPACING_S,
                    "pady": SPACING_S
                },
                "loose": {
                    "padx": SPACING_M,
                    "pady": SPACING_M
                }
            }
            
            spacing = spacing_map.get(spacing_type, spacing_map["default"])
            
            # Apply spacing based on widget's layout manager
            manager = widget.winfo_manager()
            if manager == "grid":
                widget.grid_configure(**spacing)
            elif manager == "pack":
                widget.pack_configure(**spacing)
                
        except Exception as e:
            self.logger.error(f"[LAYOUT] Error applying spacing: {e}")
    
    def ensure_layout_consistency(self, container: ctk.CTkFrame) -> None:
        """
        Ensure layout consistency by checking for mixed layout managers.
        
        Args:
            container: Container to check
        """
        try:
            managers = set()
            for child in container.winfo_children():
                manager = child.winfo_manager()
                if manager:
                    managers.add(manager)
            
            if len(managers) > 1:
                self.logger.warning(
                    f"[LAYOUT] Mixed layout managers detected in container: {managers}. "
                    f"This may cause layout conflicts."
                )
            else:
                self.logger.info(f"[LAYOUT] Layout consistency verified: {managers}")
                
        except Exception as e:
            self.logger.error(f"[LAYOUT] Error checking layout consistency: {e}")


def patch_main_container_creation(ui_initializer):
    """
    Monkey-patch the UIInitializer to use improved layout.
    
    Args:
        ui_initializer: UIInitializer instance to patch
    """
    try:
        # Create improved layout manager
        layout_manager = ImprovedLayoutManager(ui_initializer.root, ui_initializer.logger)
        
        # Replace the create_main_container method
        def improved_create_main_container():
            """Improved main container creation with layout best practices."""
            ui_initializer.main_container = layout_manager.create_optimized_main_container()
        
        # Patch the method
        ui_initializer.create_main_container = improved_create_main_container
        ui_initializer.layout_manager = layout_manager
        
        ui_initializer.logger.info("[LAYOUT] UIInitializer patched with improved layout manager")
        
    except Exception as e:
        ui_initializer.logger.error(f"[LAYOUT] Error patching UIInitializer: {e}")
        raise


def validate_layout_rules(widget) -> bool:
    """
    Validate that layout follows the established rules.
    
    Args:
        widget: Widget to validate
        
    Returns:
        bool: True if layout is valid
    """
    try:
        # Check for mixed layout managers in the same container
        if hasattr(widget, 'winfo_children'):
            managers = set()
            for child in widget.winfo_children():
                manager = child.winfo_manager()
                if manager:
                    managers.add(manager)
            
            if len(managers) > 1:
                logging.warning(f"Layout rule violation: Mixed managers {managers} in {widget}")
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error validating layout: {e}")
        return False


# Example usage for integration
def integrate_layout_improvements(app):
    """
    Integrate layout improvements into the main application.
    
    Args:
        app: CheckerApp instance
    """
    try:
        # Patch the UI initializer if available
        if hasattr(app, 'ui_initializer'):
            patch_main_container_creation(app.ui_initializer)
        
        # Create layout manager for the app
        app.layout_manager = ImprovedLayoutManager(app.root, app.logger)
        
        app.logger.info("[LAYOUT] Layout improvements successfully integrated")
        
    except Exception as e:
        app.logger.error(f"[LAYOUT] Error integrating layout improvements: {e}")
        raise
