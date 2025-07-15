"""
Visuelles Design & Moderne UI Verbesserungen für Checker App
===========================================================

Diese Datei implementiert die visuellen Design-Verbesserungen:
1. Harmonisiertes Farbschema mit konsistenten Primär-/Sekundärfarben
2. Moderne Karten-Layouts mit Schatten-Effekten und Hover-Animationen
3. Verbesserte Typografie mit einheitlichen Schriftgrößen und -gewichten
4. Moderne Fluent Design Icons statt Emojis
"""

import customtkinter as ctk
import logging
from typing import Optional, Dict, Any, Tuple, Union
from ui_theme import UITheme
from PIL import Image, ImageDraw, ImageFilter
import os


class ModernVisualDesignManager:
    """Manager für moderne visuelle Design-Elemente und UI-Verbesserungen."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._setup_modern_color_scheme()
        self._setup_modern_typography()
        self._setup_modern_shadows()
        self._setup_fluent_icons()
        
    def _setup_modern_color_scheme(self):
        """Setup elegant and professional color scheme."""
        self.colors = {
            # Professional Primary Colors - Elegant & Trustworthy
            "primary": "#2563EB",           # Professional Blue
            "primary_hover": "#1D4ED8",     # Darker blue for hover
            "primary_light": "#EEF2FF",     # Very light blue backgrounds
            "primary_dark": "#1E40AF",      # Dark blue for contrast
            
            # Sophisticated Secondary Colors - Calm & Professional
            "secondary": "#64748B",         # Slate Gray
            "secondary_hover": "#475569",   # Darker slate hover
            "secondary_light": "#F1F5F9",   # Light slate backgrounds
            "secondary_dark": "#334155",    # Dark slate for contrast
            
            # Refined Accent Colors - Subtle & Elegant
            "accent_success": "#059669",    # Professional Green
            "accent_warning": "#D97706",    # Professional Orange
            "accent_info": "#0284C7",       # Professional Light Blue
            "accent_error": "#DC2626",      # Professional Red
            
            # Clean Neutral Colors - Minimal & Modern
            "background_primary": "#FFFFFF",    # Pure white
            "background_secondary": "#F8FAFC",  # Very light gray
            "background_tertiary": "#F1F5F9",   # Light gray
            "surface": "#FFFFFF",               # Pure white
            "surface_elevated": "#FFFFFF",      # White with subtle shadow
            
            # Professional Text Colors - High Readability
            "text_primary": "#0F172A",       # Very dark slate
            "text_secondary": "#475569",     # Medium slate
            "text_tertiary": "#64748B",      # Light slate
            "text_on_primary": "#FFFFFF",    # White on primary
            "text_muted": "#94A3B8",         # Very light slate
            
            # Subtle Border & Divider Colors - Clean Lines
            "border_light": "#F1F5F9",       # Very subtle
            "border_medium": "#E2E8F0",      # Light and clean
            "border_strong": "#CBD5E1",      # More visible
            "divider": "#F8FAFC",            # Barely visible divider
            
            # Professional Status Colors - Clear & Trustworthy
            "success": "#059669",            # Professional Green
            "success_light": "#F0FDF4",      # Very light green
            "warning": "#D97706",            # Professional Orange
            "warning_light": "#FFFBEB",      # Very light orange
            "error": "#DC2626",              # Professional Red
            "error_light": "#FEF2F2",        # Very light red
            "info": "#0284C7",               # Professional Blue
            "info_light": "#F0F9FF",         # Very light blue
        }
        
    def _setup_modern_typography(self):
        """Setup clean and professional typography system."""
        self.typography = {
            # Font Families - Clean & Professional
            "primary_font": "Segoe UI",          # Windows standard
            "secondary_font": "Arial",           # Clean alternative
            "monospace_font": "Consolas",        # Code font
            
            # Heading Sizes - Elegant Hierarchy
            "heading_xl": {"size": 28, "weight": "bold"},      # Main titles (reduced from 32)
            "heading_l": {"size": 22, "weight": "bold"},       # Section titles (reduced from 24)
            "heading_m": {"size": 18, "weight": "bold"},       # Subsection titles (reduced from 20)
            "heading_s": {"size": 16, "weight": "bold"},       # Card titles
            "heading_xs": {"size": 14, "weight": "bold"},      # Small titles
            
            # Body Text Sizes - Comfortable Reading
            "body_xl": {"size": 16, "weight": "normal"},       # Large body text (reduced from 18)
            "body_l": {"size": 14, "weight": "normal"},        # Standard body (reduced from 16)
            "body_m": {"size": 13, "weight": "normal"},        # Medium body (reduced from 14)
            "body_s": {"size": 12, "weight": "normal"},        # Small body
            "body_xs": {"size": 11, "weight": "normal"},       # Tiny text (increased from 10)
            
            # Special Text Styles - Refined
            "caption": {"size": 11, "weight": "normal"},       # Captions
            "overline": {"size": 10, "weight": "bold"},        # Overlines
            "button": {"size": 13, "weight": "bold"},          # Button text (reduced from 14)
            "input": {"size": 13, "weight": "normal"},         # Input text (reduced from 14)
        }
        
    def _setup_modern_shadows(self):
        """Setup modern shadow system for elevated elements."""
        self.shadows = {
            # Card Shadows - Subtle Elevation
            "card_small": {
                "offset": (0, 1),
                "blur": 3,
                "color": "rgba(0, 0, 0, 0.1)"
            },
            "card_medium": {
                "offset": (0, 4),
                "blur": 6,
                "color": "rgba(0, 0, 0, 0.1)"
            },
            "card_large": {
                "offset": (0, 10),
                "blur": 15,
                "color": "rgba(0, 0, 0, 0.1)"
            },
            
            # Button Shadows - Interactive Feedback
            "button_rest": {
                "offset": (0, 2),
                "blur": 4,
                "color": "rgba(0, 0, 0, 0.1)"
            },
            "button_hover": {
                "offset": (0, 4),
                "blur": 8,
                "color": "rgba(0, 0, 0, 0.15)"
            },
            "button_pressed": {
                "offset": (0, 1),
                "blur": 2,
                "color": "rgba(0, 0, 0, 0.2)"
            },
            
            # Container Shadows - Depth Layers
            "container": {
                "offset": (0, 2),
                "blur": 8,
                "color": "rgba(0, 0, 0, 0.06)"
            },
            "dialog": {
                "offset": (0, 20),
                "blur": 25,
                "color": "rgba(0, 0, 0, 0.15)"
            }
        }
        
    def _setup_fluent_icons(self):
        """Setup Fluent Design icon system to replace emojis."""
        self.fluent_icons = {
            # Navigation Icons
            "home": "🏠",           # Temporary fallback - will be replaced with SVG
            "settings": "⚙️",       # Temporary fallback
            "search": "🔍",         # Temporary fallback
            "menu": "☰",            # Temporary fallback
            
            # Action Icons
            "add": "➕",            # Temporary fallback
            "edit": "✏️",           # Temporary fallback
            "delete": "🗑️",         # Temporary fallback
            "save": "💾",           # Temporary fallback
            "upload": "📤",         # Temporary fallback
            "download": "📥",       # Temporary fallback
            
            # Status Icons
            "success": "✅",        # Temporary fallback
            "warning": "⚠️",        # Temporary fallback
            "error": "❌",          # Temporary fallback
            "info": "ℹ️",           # Temporary fallback
            
            # Content Icons
            "document": "📄",       # Temporary fallback
            "folder": "📁",         # Temporary fallback
            "user": "👤",           # Temporary fallback
            "team": "👥",           # Temporary fallback
        }

    def create_modern_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """
        Create a modern card with elevated design and subtle shadows.
        
        Args:
            parent: Parent widget
            **kwargs: Additional CTkFrame arguments
            
        Returns:
            ctk.CTkFrame: Modern card widget
        """
        try:
            # Default modern card styling
            card_defaults = {
                "fg_color": self.colors["surface"],
                "corner_radius": 12,
                "border_width": 1,
                "border_color": self.colors["border_light"],
            }
            
            # Merge with user-provided kwargs
            card_options = {**card_defaults, **kwargs}
            
            # Create the card
            card = ctk.CTkFrame(parent, **card_options)
            
            # Apply hover effects
            self._apply_card_hover_effects(card)
            
            self.logger.info("[VISUAL] Modern card created with elevated design")
            return card
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error creating modern card: {e}")
            raise

    def create_modern_button(self, parent, text: str, style: str = "primary", **kwargs) -> ctk.CTkButton:
        """
        Create a modern button with consistent styling and hover effects.
        
        Args:
            parent: Parent widget
            text: Button text
            style: Button style ("primary", "secondary", "accent", "outline")
            **kwargs: Additional CTkButton arguments
            
        Returns:
            ctk.CTkButton: Modern button widget
        """
        try:
            # Style configurations
            styles = {
                "primary": {
                    "fg_color": self.colors["primary"],
                    "hover_color": self.colors["primary_hover"],
                    "text_color": self.colors["text_on_primary"],
                    "border_width": 0,
                },
                "secondary": {
                    "fg_color": self.colors["secondary"],
                    "hover_color": self.colors["secondary_hover"],
                    "text_color": self.colors["text_on_primary"],
                    "border_width": 0,
                },
                "accent": {
                    "fg_color": self.colors["accent_orange"],
                    "hover_color": "#FF8F00",  # Lighter orange
                    "text_color": self.colors["text_on_primary"],
                    "border_width": 0,
                },
                "outline": {
                    "fg_color": "transparent",
                    "hover_color": self.colors["primary_light"],
                    "text_color": self.colors["primary"],
                    "border_width": 2,
                    "border_color": self.colors["primary"],
                }
            }
            
            # Get style configuration
            style_config = styles.get(style, styles["primary"])
            
            # Default button styling
            button_defaults = {
                "corner_radius": 8,
                "height": 40,
                "font": ctk.CTkFont(
                    family=self.typography["primary_font"],
                    size=self.typography["button"]["size"],
                    weight=self.typography["button"]["weight"]
                ),
                **style_config
            }
            
            # Merge with user-provided kwargs
            button_options = {**button_defaults, **kwargs}
            
            # Create the button
            button = ctk.CTkButton(parent, text=text, **button_options)
            
            self.logger.info(f"[VISUAL] Modern {style} button created: {text}")
            return button
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error creating modern button: {e}")
            raise

    def create_modern_heading(self, parent, text: str, level: str = "m", **kwargs) -> ctk.CTkLabel:
        """
        Create a modern heading with consistent typography.
        
        Args:
            parent: Parent widget
            text: Heading text
            level: Heading level ("xl", "l", "m", "s", "xs")
            **kwargs: Additional CTkLabel arguments
            
        Returns:
            ctk.CTkLabel: Modern heading widget
        """
        try:
            # Get typography configuration
            typo_config = self.typography.get(f"heading_{level}", self.typography["heading_m"])
            
            # Default heading styling
            heading_defaults = {
                "text_color": self.colors["text_primary"],
                "font": ctk.CTkFont(
                    family=self.typography["primary_font"],
                    size=typo_config["size"],
                    weight=typo_config["weight"]
                ),
                "anchor": "w"
            }
            
            # Merge with user-provided kwargs
            heading_options = {**heading_defaults, **kwargs}
            
            # Create the heading
            heading = ctk.CTkLabel(parent, text=text, **heading_options)
            
            self.logger.info(f"[VISUAL] Modern heading created: {text} (level: {level})")
            return heading
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error creating modern heading: {e}")
            raise

    def create_modern_body_text(self, parent, text: str, size: str = "m", **kwargs) -> ctk.CTkLabel:
        """
        Create modern body text with consistent typography.
        
        Args:
            parent: Parent widget
            text: Body text
            size: Text size ("xl", "l", "m", "s", "xs")
            **kwargs: Additional CTkLabel arguments
            
        Returns:
            ctk.CTkLabel: Modern body text widget
        """
        try:
            # Get typography configuration
            typo_config = self.typography.get(f"body_{size}", self.typography["body_m"])
            
            # Default body text styling
            body_defaults = {
                "text_color": self.colors["text_secondary"],
                "font": ctk.CTkFont(
                    family=self.typography["primary_font"],
                    size=typo_config["size"],
                    weight=typo_config["weight"]
                ),
                "anchor": "w"
            }
            
            # Merge with user-provided kwargs
            body_options = {**body_defaults, **kwargs}
            
            # Create the body text
            body_text = ctk.CTkLabel(parent, text=text, **body_options)
            
            return body_text
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error creating modern body text: {e}")
            raise

    def create_fluent_icon(self, parent, icon_name: str, size: int = 24, **kwargs) -> ctk.CTkLabel:
        """
        Create a Fluent Design icon (with emoji fallback).
        
        Args:
            parent: Parent widget
            icon_name: Icon name from fluent_icons
            size: Icon size in pixels
            **kwargs: Additional CTkLabel arguments
            
        Returns:
            ctk.CTkLabel: Icon widget
        """
        try:
            # Get icon character (emoji fallback for now)
            icon_char = self.fluent_icons.get(icon_name, "❓")
            
            # Default icon styling
            icon_defaults = {
                "text": icon_char,
                "font": ctk.CTkFont(size=size),
                "text_color": self.colors["text_secondary"],
                "width": size,
                "height": size,
            }
            
            # Merge with user-provided kwargs
            icon_options = {**icon_defaults, **kwargs}
            
            # Create the icon
            icon = ctk.CTkLabel(parent, **icon_options)
            
            return icon
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error creating fluent icon: {e}")
            raise

    def _apply_card_hover_effects(self, card: ctk.CTkFrame):
        """Apply hover effects to a card for better interactivity."""
        try:
            original_border_color = card.cget("border_color")
            hover_border_color = self.colors["border_medium"]
            
            def on_enter(event):
                card.configure(border_color=hover_border_color)
                
            def on_leave(event):
                card.configure(border_color=original_border_color)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error applying card hover effects: {e}")

    def apply_modern_theme_to_container(self, container: ctk.CTkFrame):
        """Apply modern visual theme to an entire container and its children."""
        try:
            # Apply modern background
            container.configure(fg_color=self.colors["background_primary"])
            
            # Apply modern styling to child widgets
            for child in container.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    # Apply card styling to frames
                    if child.cget("fg_color") != "transparent":
                        child.configure(
                            fg_color=self.colors["surface"],
                            border_color=self.colors["border_light"],
                            corner_radius=12
                        )
                elif isinstance(child, ctk.CTkLabel):
                    # Apply modern typography to labels
                    if not child.cget("font"):  # Only if no font is set
                        child.configure(
                            font=ctk.CTkFont(
                                family=self.typography["primary_font"],
                                size=self.typography["body_m"]["size"]
                            ),
                            text_color=self.colors["text_primary"]
                        )
                elif isinstance(child, ctk.CTkButton):
                    # Apply modern button styling
                    if not child.cget("font"):  # Only if no font is set
                        child.configure(
                            font=ctk.CTkFont(
                                family=self.typography["primary_font"],
                                size=self.typography["button"]["size"],
                                weight=self.typography["button"]["weight"]
                            ),
                            corner_radius=8
                        )
            
            self.logger.info("[VISUAL] Modern theme applied to container")
            
        except Exception as e:
            self.logger.error(f"[VISUAL] Error applying modern theme: {e}")

    def get_color(self, color_name: str) -> str:
        """Get a color from the modern color scheme."""
        return self.colors.get(color_name, "#000000")
    
    def get_typography(self, style_name: str) -> Dict[str, Any]:
        """Get typography configuration."""
        return self.typography.get(style_name, self.typography["body_m"])


# Global instance for easy access
visual_design_manager = ModernVisualDesignManager()


def create_modern_welcome_section(parent, title: str, subtitle: str = "", 
                                icon_name: str = "", column: int = 0) -> ctk.CTkFrame:
    """
    Create a modern welcome screen section with consistent styling.
    
    Args:
        parent: Parent container
        title: Section title
        subtitle: Section subtitle
        icon_name: Icon name for the section
        column: Grid column position
        
    Returns:
        ctk.CTkFrame: Modern section container
    """
    try:
        # Create section card
        section = visual_design_manager.create_modern_card(parent)
        section.grid(
            row=0, column=column,
            sticky="nsew",
            padx=(0 if column == 0 else UITheme.SPACING_S, 
                  0 if column == 2 else UITheme.SPACING_S),
            pady=0
        )
        
        # Configure internal grid
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)  # Content area expandable
        
        # Header area
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=UITheme.SPACING_M, pady=(UITheme.SPACING_M, UITheme.SPACING_S))
        header.grid_columnconfigure(1, weight=1)
        
        # Icon
        if icon_name:
            icon = visual_design_manager.create_fluent_icon(header, icon_name, size=24)
            icon.grid(row=0, column=0, sticky="w", padx=(0, UITheme.SPACING_S))
        
        # Title and subtitle container
        text_container = ctk.CTkFrame(header, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="ew")
        
        # Title
        title_label = visual_design_manager.create_modern_heading(text_container, title, level="s")
        title_label.pack(anchor="w")
        
        # Subtitle
        if subtitle:
            subtitle_label = visual_design_manager.create_modern_body_text(
                text_container, subtitle, size="s"
            )
            subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Content area
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_M, pady=(0, UITheme.SPACING_M))
        content.grid_columnconfigure(0, weight=1)
        
        visual_design_manager.logger.info(f"[VISUAL] Modern welcome section created: {title}")
        return section, content
        
    except Exception as e:
        visual_design_manager.logger.error(f"[VISUAL] Error creating modern welcome section: {e}")
        raise


def apply_modern_visual_improvements(app):
    """
    Apply modern visual improvements to the entire application.
    
    Args:
        app: CheckerApp instance
    """
    try:
        # Add visual design manager to app
        app.visual_design_manager = visual_design_manager
        
        # Apply modern theme to main container if available
        if hasattr(app, 'main_container') and app.main_container:
            visual_design_manager.apply_modern_theme_to_container(app.main_container)
        
        # Apply modern theme to welcome screen if available
        if hasattr(app, 'welcome_screen') and app.welcome_screen:
            visual_design_manager.apply_modern_theme_to_container(app.welcome_screen)
        
        app.logger.info("[VISUAL] Modern visual improvements successfully applied")
        
    except Exception as e:
        app.logger.error(f"[VISUAL] Error applying modern visual improvements: {e}")
        raise
