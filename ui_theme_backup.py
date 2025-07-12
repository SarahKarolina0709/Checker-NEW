"""
Enhanced UI Theme for the Checker-App with Dataclass-based Color System
-----------------------------------------------------------------------
Centralized theme system with dependency injection support for hot-swapping themes.
Includes accessibility improvements and comprehensive color management.
"""
import customtkinter as ctk
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any, Protocol
from abc import ABC, abstractmethod

# =============================================================================
# THEME PROTOCOL AND INTERFACES
# =============================================================================

class ThemeProvider(Protocol):
    """Protocol for theme dependency injection."""
    
    def get_color(self, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color by name, optionally specifying light/dark mode."""
        ...
    
    def get_color_tuple(self, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        ...
    
    def get_workflow_colors(self, workflow_id: str) -> Dict[str, str]:
        """Get color scheme for a specific workflow."""
        ...

# =============================================================================
# DATACLASS-BASED COLOR DEFINITIONS
# =============================================================================

@dataclass(frozen=True)
class ColorScheme:
    """Immutable color scheme definition."""
    
    # Core Colors
    background: str
    surface: str
    card: str
    border: str
    
    # Primary Colors
    primary: str
    primary_hover: str
    primary_container: str
    primary_surface: str
    
    # Text Colors
    text_primary: str
    text_secondary: str
    text_on_primary: str
    text_on_dark: str
    
    # Semantic Colors
    success: str
    success_hover: str
    danger: str
    danger_hover: str
    warning: str
    info: str
    info_hover: str
    
    # Interactive Colors
    secondary: str
    secondary_hover: str
    accent: str
    accent_hover: str
    
    # Icon Colors
    icon: str
    icon_light: str
    icon_accent: str
    icon_danger: str
    icon_success: str
    icon_warning: str
    
    # Menu Colors
    menu_icon: str
    menu_hover: str
    
    # Control Colors
    header_icon: str
    control_hover: str
    
    # Surface Colors for alerts/banners
    danger_surface: str
    info_surface: str
    success_surface: str
    warning_surface: str

@dataclass(frozen=True)
class WorkflowColorScheme:
    """Color scheme for workflow cards."""
    primary: str
    hover: str
    light: str
    icon_bg: str
    shadow: str
    glow: str
    text: str = "#FFFFFF"
    
@dataclass(frozen=True)
class AccessibilityConfig:
    """Accessibility configuration settings."""
    
    # Keyboard navigation
    focus_indicator_color: str = "#0066CC"
    focus_indicator_width: int = 2
    
    # Screen reader support
    default_aria_labels: Dict[str, str] = field(default_factory=lambda: {
        'add_button': 'Hinzufügen',
        'delete_button': 'Löschen',
        'edit_button': 'Bearbeiten',
        'save_button': 'Speichern',
        'cancel_button': 'Abbrechen',
        'close_button': 'Schließen',
        'menu_button': 'Menü öffnen',
        'file_upload': 'Datei hochladen',
        'drag_drop_area': 'Dateien hierher ziehen oder klicken zum Auswählen',
    })
    
    # High contrast mode support
    high_contrast_mode: bool = False
    high_contrast_multiplier: float = 1.5
    
    # Text scaling
    min_font_size: int = 10
    max_font_size: int = 24
    default_font_scale: float = 1.0

# =============================================================================
# ENHANCED THEME MANAGER WITH DEPENDENCY INJECTION
# =============================================================================

class EnhancedUITheme:
    """Enhanced theme manager with dependency injection and hot-swapping support."""
    
    # Current theme instance
    _instance: Optional['EnhancedUITheme'] = None
    _current_theme: str = "default"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._themes: Dict[str, ColorScheme] = {}
            self._workflow_schemes: Dict[str, Dict[str, WorkflowColorScheme]] = {}
            self._accessibility = AccessibilityConfig()
            self._observers: list = []
            
            # Initialize default themes
            self._init_default_themes()
            self._init_workflow_schemes()
    
    def _init_default_themes(self):
        """Initialize the default light and dark themes."""
        
        # Light Theme
        light_theme = ColorScheme(
            # Core Colors
            background="#FAFBFC",
            surface="#FFFFFF",
            card="#FFFFFF",
            border="#E1E5E9",
            
            # Primary Colors
            primary="#0066CC",
            primary_hover="#0052A3",
            primary_container="#E6F3FF",
            primary_surface="#F0F8FF",
            
            # Text Colors
            text_primary="#1A1A1A",
            text_secondary="#5A6C7D",
            text_on_primary="#FFFFFF",
            text_on_dark="#FFFFFF",
            
            # Semantic Colors
            success="#28A745",
            success_hover="#218838",
            danger="#DC3545",
            danger_hover="#C82333",
            warning="#FFC107",
            info="#17A2B8",
            info_hover="#138496",
            
            # Interactive Colors
            secondary="#6C757D",
            secondary_hover="#5A6268",
            accent="#0066CC",
            accent_hover="#0052A3",
            
            # Icon Colors
            icon="#6C757D",
            icon_light="#8E9BAE",
            icon_accent="#007BFF",
            icon_danger="#DC3545",
            icon_success="#28A745",
            icon_warning="#F39C12",
            
            # Menu Colors
            menu_icon="#495057",
            menu_hover="#F8F9FA",
            
            # Control Colors
            header_icon="#6C757D",
            control_hover="#F1F3F4",
            
            # Surface Colors
            danger_surface="#F8D7DA",
            info_surface="#D1ECF1",
            success_surface="#D4EDDA",
            warning_surface="#FFF3CD"
        )
        
        # Dark Theme
        dark_theme = ColorScheme(
            # Core Colors
            background="#121212",
            surface="#1E1E1E",
            card="#1E1E1E",
            border="#2A2A2A",
            
            # Primary Colors
            primary="#0A84FF",
            primary_hover="#0060F0",
            primary_container="#1A2F4A",
            primary_surface="#0F1A2E",
            
            # Text Colors
            text_primary="#EAEAEB",
            text_secondary="#9E9EA4",
            text_on_primary="#FFFFFF",
            text_on_dark="#FFFFFF",
            
            # Semantic Colors
            success="#30D158",
            success_hover="#29B34C",
            danger="#FF453A",
            danger_hover="#E03A30",
            warning="#FBBF24",
            info="#4FC3F7",
            info_hover="#29B6F6",
            
            # Interactive Colors
            secondary="#363636",
            secondary_hover="#474747",
            accent="#0A84FF",
            accent_hover="#0060F0",
            
            # Icon Colors
            icon="#B0B3B8",
            icon_light="#8A8D91",
            icon_accent="#4FC3F7",
            icon_danger="#F87171",
            icon_success="#4ADE80",
            icon_warning="#FBBF24",
            
            # Menu Colors
            menu_icon="#E4E6EA",
            menu_hover="#2A2A2A",
            
            # Control Colors
            header_icon="#B0B3B8",
            control_hover="#2C2C2E",
            
            # Surface Colors
            danger_surface="#3D1A1A",
            info_surface="#1A2A3D",
            success_surface="#1A3D1A",
            warning_surface="#3D3D1A"
        )
        
        self._themes["light"] = light_theme
        self._themes["dark"] = dark_theme
    
    def _init_workflow_schemes(self):
        """Initialize workflow-specific color schemes."""
        
        # Light mode workflow schemes
        light_workflows = {
            'angebots_workflow': WorkflowColorScheme(
                primary='#0078D7',
                hover='#0056b3',
                light='#F0F8FF',
                icon_bg='#0078D7',
                shadow='#E3F2FD',
                glow='#B3D9FF'
            ),
            'pruefung_workflow': WorkflowColorScheme(
                primary='#28A745',
                hover='#1e7e34',
                light='#F0FFF0',
                icon_bg='#28A745',
                shadow='#E8F5E8',
                glow='#90EE90'
            ),
            'finalisierung_workflow': WorkflowColorScheme(
                primary='#FFC107',
                hover='#e0a800',
                light='#FFFEF0',
                icon_bg='#FFC107',
                shadow='#FFF9E6',
                glow='#FFE55C'
            ),
            'projekt_workflow': WorkflowColorScheme(
                primary='#17A2B8',
                hover='#117a8b',
                light='#F0FEFF',
                icon_bg='#17A2B8',
                shadow='#E0F7FA',
                glow='#87CEEB'
            )
        }
        
        # Dark mode workflow schemes (adjusted for better visibility)
        dark_workflows = {
            'angebots_workflow': WorkflowColorScheme(
                primary='#4FC3F7',
                hover='#29B6F6',
                light='#1A2F4A',
                icon_bg='#4FC3F7',
                shadow='#0F1A2E',
                glow='#87CEEB'
            ),
            'pruefung_workflow': WorkflowColorScheme(
                primary='#4ADE80',
                hover='#22C55E',
                light='#1A3D1A',
                icon_bg='#4ADE80',
                shadow='#0F2A0F',
                glow='#86EFAC'
            ),
            'finalisierung_workflow': WorkflowColorScheme(
                primary='#FBBF24',
                hover='#F59E0B',
                light='#3D3D1A',
                icon_bg='#FBBF24',
                shadow='#2A2A0F',
                glow='#FDE68A'
            ),
            'projekt_workflow': WorkflowColorScheme(
                primary='#06B6D4',
                hover='#0891B2',
                light='#1A3D3D',
                icon_bg='#06B6D4',
                shadow='#0F2A2A',
                glow='#67E8F9'
            )
        }
        
        self._workflow_schemes["light"] = light_workflows
        self._workflow_schemes["dark"] = dark_workflows
    
    # Theme Provider Protocol Implementation
    def get_color(self, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color by name, optionally specifying light/dark mode."""
        if mode is None:
            mode = ctk.get_appearance_mode().lower()
        
        theme = self._themes.get(mode, self._themes["light"])
        return getattr(theme, color_name, theme.primary)
    
    def get_color_tuple(self, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        light_color = self.get_color(color_name, "light")
        dark_color = self.get_color(color_name, "dark")
        return (light_color, dark_color)
    
    def get_workflow_colors(self, workflow_id: str) -> Dict[str, str]:
        """Get color scheme for a specific workflow."""
        mode = ctk.get_appearance_mode().lower()
        workflow_schemes = self._workflow_schemes.get(mode, self._workflow_schemes["light"])
        scheme = workflow_schemes.get(workflow_id, workflow_schemes["angebots_workflow"])
        
        return {
            'primary': scheme.primary,
            'hover': scheme.hover,
            'light': scheme.light,
            'icon_bg': scheme.icon_bg,
            'shadow': scheme.shadow,
            'glow': scheme.glow,
            'text': scheme.text
        }
    
    # Accessibility Support
    def get_accessibility_config(self) -> AccessibilityConfig:
        """Get current accessibility configuration."""
        return self._accessibility
    
    def update_accessibility_config(self, **kwargs):
        """Update accessibility configuration."""
        # Create new config with updates
        current_dict = self._accessibility.__dict__.copy()
        current_dict.update(kwargs)
        self._accessibility = AccessibilityConfig(**current_dict)
        self._notify_observers()
    
    # Theme Management
    def register_theme(self, name: str, light_scheme: ColorScheme, dark_scheme: ColorScheme):
        """Register a custom theme."""
        self._themes[f"{name}_light"] = light_scheme
        self._themes[f"{name}_dark"] = dark_scheme
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme (hot-swapping)."""
        if theme_name in self._themes:
            self._current_theme = theme_name
            self._notify_observers()
    
    # Observer Pattern for Hot-Swapping
    def add_observer(self, observer_callback):
        """Add observer for theme changes."""
        self._observers.append(observer_callback)
    
    def remove_observer(self, observer_callback):
        """Remove observer."""
        if observer_callback in self._observers:
            self._observers.remove(observer_callback)
    
    def _notify_observers(self):
        """Notify all observers of theme changes."""
        for observer in self._observers:
            try:
                observer()
            except Exception as e:
                print(f"Error notifying theme observer: {e}")

# =============================================================================
# ACCESSIBILITY HELPERS
# =============================================================================

class AccessibilityHelper:
    """Helper class for accessibility improvements."""
    
    @staticmethod
    def add_keyboard_navigation(widget, on_enter_callback=None, on_space_callback=None):
        """Add keyboard navigation to a widget."""
        def on_key_press(event):
            if event.keysym == "Return" and on_enter_callback:
                on_enter_callback()
            elif event.keysym == "space" and on_space_callback:
                on_space_callback()
        
        widget.bind("<KeyPress>", on_key_press)
        widget.focus_set()
    
    @staticmethod
    def add_focus_indicator(widget, theme_provider: ThemeProvider):
        """Add visual focus indicator to widget."""
        accessibility_config = theme_provider.get_accessibility_config()
        
        def on_focus_in(event):
            widget.configure(
                border_width=accessibility_config.focus_indicator_width,
                border_color=accessibility_config.focus_indicator_color
            )
        
        def on_focus_out(event):
            widget.configure(border_width=0)
        
        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)
    
    @staticmethod
    def set_aria_label(widget, label_key: str, theme_provider: ThemeProvider):
        """Set accessible label for screen readers."""
        accessibility_config = theme_provider.get_accessibility_config()
        aria_label = accessibility_config.default_aria_labels.get(label_key, label_key)
        
        # Set tooltip as fallback for screen readers
        try:
            from CTkToolTip import CTkToolTip
            CTkToolTip(widget, message=aria_label)
        except ImportError:
            # Fallback: set as widget attribute
            setattr(widget, '_aria_label', aria_label)

# =============================================================================
# SINGLETON INSTANCE AND LEGACY COMPATIBILITY
# =============================================================================

# Create singleton instance
enhanced_theme = EnhancedUITheme()

# Legacy compatibility - keep existing UITheme class
class UITheme:
    """Legacy UITheme class with enhanced theme system integration."""
    
    # Singleton theme provider
    _theme_provider = enhanced_theme
    
    # =============================================================================
    # BUTTON SPECIFICATIONS AND STYLES
    # =============================================================================
    
    # Button specifications
    BUTTON_SPECS = (12, "normal")
    
    # Button styles
    BUTTON_STYLE_OUTLINE = {
        "fg_color": "transparent",
        "hover_color": enhanced_theme.get_color("surface"),
        "border_width": 1,
        "border_color": enhanced_theme.get_color("border"),
        "text_color": enhanced_theme.get_color("text_primary"),
        "corner_radius": 8
    }

    # Additional button style constants for workflows
    BUTTON_STYLE_SUCCESS = {
        "fg_color": enhanced_theme.get_color("success"),
        "hover_color": enhanced_theme.get_color("success_hover"),
        "text_color": enhanced_theme.get_color("text_on_primary"),
        "corner_radius": 8,
        "border_width": 0
    }
    
    # Fix BUTTON_STYLE_SECONDARY to be a dictionary, not a method
    BUTTON_STYLE_SECONDARY = {
        "fg_color": enhanced_theme.get_color("secondary"),
        "hover_color": enhanced_theme.get_color("secondary_hover"),
        "text_color": enhanced_theme.get_color("text_primary"),
        "corner_radius": 8,
        "border_width": 1,
        "border_color": enhanced_theme.get_color("border")
    }
    
    # Add BUTTON_STYLE_PRIMARY as static dictionary
    BUTTON_STYLE_PRIMARY = {
        "fg_color": enhanced_theme.get_color("primary"),
        "hover_color": enhanced_theme.get_color("primary_hover"),
        "text_color": enhanced_theme.get_color("text_on_primary"),
        "corner_radius": 8,
        "border_width": 0
    }
    
    # Add BUTTON_STYLE_OUTLINE as static dictionary
    BUTTON_STYLE_OUTLINE = {
        "fg_color": "transparent",
        "hover_color": enhanced_theme.get_color("surface"),
        "border_width": 1,
        "border_color": enhanced_theme.get_color("border"),
        "text_color": enhanced_theme.get_color("text_primary"),
        "corner_radius": 8
    }
    
    # =============================================================================
    # COLOR CONSTANTS
    # =============================================================================
    
    # Primary colors
    COLOR_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_PRIMARY_CONTAINER = enhanced_theme.get_color("primary_container")
    COLOR_PRIMARY_SURFACE = enhanced_theme.get_color("primary_surface")
    COLOR_PRIMARY_ACCENT = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_ACCENT_HOVER = enhanced_theme.get_color("primary_hover")
    
    # Semantic colors
    COLOR_SUCCESS = enhanced_theme.get_color("success")
    COLOR_SUCCESS_HOVER = enhanced_theme.get_color("success_hover")
    COLOR_DANGER = enhanced_theme.get_color("danger")
    COLOR_DANGER_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_WARNING = enhanced_theme.get_color("warning")
    COLOR_INFO = enhanced_theme.get_color("info")
    COLOR_INFO_HOVER = enhanced_theme.get_color("info_hover")
    
    # Text colors
    COLOR_TEXT_PRIMARY = enhanced_theme.get_color("text_primary")
    COLOR_TEXT_SECONDARY = enhanced_theme.get_color("text_secondary")
    COLOR_TEXT_ON_PRIMARY = enhanced_theme.get_color("text_on_primary")
    COLOR_TEXT_ON_DARK = enhanced_theme.get_color("text_on_dark")
    
    # Icon colors
    COLOR_ICON = enhanced_theme.get_color("icon")
    COLOR_ICON_LIGHT = enhanced_theme.get_color("icon_light")
    COLOR_ICON_ACCENT = enhanced_theme.get_color("icon_accent")
    COLOR_ICON_DANGER = enhanced_theme.get_color("icon_danger")
    COLOR_ICON_SUCCESS = enhanced_theme.get_color("icon_success")
    COLOR_ICON_WARNING = enhanced_theme.get_color("icon_warning")
    
    # Menu and navigation colors
    COLOR_MENU_ICON = enhanced_theme.get_color("menu_icon")
    COLOR_MENU_HOVER = enhanced_theme.get_color("menu_hover")
    
    # Header and control colors
    COLOR_HEADER_ICON = enhanced_theme.get_color("header_icon")
    COLOR_CONTROL_HOVER = enhanced_theme.get_color("control_hover")
    
    # Workflow colors - dynamically generated
    COLOR_WORKFLOW_ANGEBOTS = enhanced_theme.get_workflow_colors("angebots_workflow")["primary"]
    COLOR_WORKFLOW_PRUEFUNG = enhanced_theme.get_workflow_colors("pruefung_workflow")["primary"]
    COLOR_WORKFLOW_FINALISIERUNG = enhanced_theme.get_workflow_colors("finalisierung_workflow")["primary"]
    COLOR_WORKFLOW_MULTI = enhanced_theme.get_workflow_colors("projekt_workflow")["primary"]
    
    # Surface Colors for alerts/banners
    COLOR_DANGER_SURFACE = enhanced_theme.get_color("danger_surface")
    COLOR_INFO_SURFACE = enhanced_theme.get_color("info_surface")
    COLOR_SUCCESS_SURFACE = enhanced_theme.get_color("success_surface")
    COLOR_WARNING_SURFACE = enhanced_theme.get_color("warning_surface")
    
    # Additional legacy colors (from original theme)
    COLOR_PURPLE = "#8B5CF6"
    COLOR_DANGER_BORDER_LIGHT = "#F5C6CB"
    COLOR_INFO_BORDER_LIGHT = "#BEE5EB"
    COLOR_SUCCESS_BORDER_LIGHT = "#C3E6CB"
    COLOR_WARNING_BORDER_LIGHT = "#FFEEBA"
    COLOR_SUCCESS_LIGHT = enhanced_theme.get_color("success_surface")
    COLOR_ERROR_LIGHT = enhanced_theme.get_color("danger_surface")
    COLOR_ERROR_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_BG_SECONDARY = "#F8F9FA"
    
    # Dark Mode Colors - now dynamically fetched
    COLOR_BACKGROUND_DARK = enhanced_theme.get_color("background", "dark")
    COLOR_SURFACE_DARK = enhanced_theme.get_color("surface", "dark")
    COLOR_CARD_DARK = enhanced_theme.get_color("card", "dark")
    COLOR_BORDER_DARK = enhanced_theme.get_color("border", "dark")
    COLOR_PRIMARY_DARK = enhanced_theme.get_color("primary", "dark")
    COLOR_PRIMARY_HOVER_DARK = enhanced_theme.get_color("primary_hover", "dark")
    COLOR_TEXT_PRIMARY_DARK = enhanced_theme.get_color("text_primary", "dark")
    COLOR_TEXT_SECONDARY_DARK = enhanced_theme.get_color("text_secondary", "dark")
    
    # Dark Mode Icon Colors
    COLOR_ICON_DARK = enhanced_theme.get_color("icon", "dark")
    COLOR_ICON_LIGHT_DARK = enhanced_theme.get_color("icon_light", "dark")
    COLOR_ICON_ACCENT_DARK = enhanced_theme.get_color("icon_accent", "dark")
    COLOR_ICON_DANGER_DARK = enhanced_theme.get_color("icon_danger", "dark")
    COLOR_ICON_SUCCESS_DARK = enhanced_theme.get_color("icon_success", "dark")
    COLOR_ICON_WARNING_DARK = enhanced_theme.get_color("icon_warning", "dark")
    
    # Menu and Navigation dark mode
    COLOR_MENU_ICON_DARK = enhanced_theme.get_color("menu_icon", "dark")
    COLOR_MENU_HOVER_DARK = enhanced_theme.get_color("menu_hover", "dark")
    COLOR_HEADER_ICON_DARK = enhanced_theme.get_color("header_icon", "dark")
    COLOR_CONTROL_HOVER_DARK = enhanced_theme.get_color("control_hover", "dark")
    
    # Dark Mode Surfaces
    COLOR_DANGER_SURFACE_DARK = enhanced_theme.get_color("danger_surface", "dark")
    COLOR_INFO_SURFACE_DARK = enhanced_theme.get_color("info_surface", "dark")
    COLOR_SUCCESS_SURFACE_DARK = enhanced_theme.get_color("success_surface", "dark")
    COLOR_WARNING_SURFACE_DARK = enhanced_theme.get_color("warning_surface", "dark")
    
    # Secondary, Success, Danger for dark mode
    COLOR_SECONDARY_DARK = enhanced_theme.get_color("secondary", "dark")
    COLOR_SECONDARY_HOVER_DARK = enhanced_theme.get_color("secondary_hover", "dark")
    COLOR_SUCCESS_DARK = enhanced_theme.get_color("success", "dark")
    COLOR_SUCCESS_HOVER_DARK = enhanced_theme.get_color("success_hover", "dark")
    COLOR_DANGER_DARK = enhanced_theme.get_color("danger", "dark")
    COLOR_DANGER_HOVER_DARK = enhanced_theme.get_color("danger_hover", "dark")
    
    # Surface hover colors
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Profile button colors
    COLOR_PROFILE_BUTTON_LIGHT = "#7B42F6"
    COLOR_PROFILE_BUTTON_HOVER_LIGHT = "#6A35D9"
    COLOR_PROFILE_BUTTON_DARK = "#8A5BF7"
    COLOR_PROFILE_BUTTON_HOVER_DARK = "#7B42F6"
    
    # Icon button colors
    COLOR_ICON_BUTTON_FG = ("gray85", "gray28")
    COLOR_ICON_BUTTON_HOVER = ("gray75", "gray38")
    
    # Enhanced Card Design
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_SHADOW = "#00000015"
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Modern Gradient Colors
    GRADIENT_PRIMARY_START = "#007BFF"
    GRADIENT_PRIMARY_END = "#0056B3"
    GRADIENT_SECONDARY_START = "#6C757D"
    GRADIENT_SECONDARY_END = "#495057"
    
    # Enhanced Status Colors
    COLOR_STATUS_ONLINE = enhanced_theme.get_color("success")
    COLOR_STATUS_OFFLINE = enhanced_theme.get_color("danger")
    COLOR_STATUS_PENDING = enhanced_theme.get_color("warning")
    COLOR_STATUS_PROCESSING = enhanced_theme.get_color("info")
    
    # Modern UI Elements
    COLOR_TOOLTIP_BG = "#343A40"
    COLOR_TOOLTIP_TEXT = "#FFFFFF"
    COLOR_OVERLAY = "#00000080"
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    @staticmethod
    def add_keyboard_drag_drop_support(widget, drop_callback=None):
        """
        Add keyboard drag and drop support to a widget.
        
        Args:
            widget: The widget to add support to
            drop_callback: Optional callback function for drop events
        """
        try:
            # Basic keyboard navigation support
            def on_key_press(event):
                if event.keysym == 'Return' or event.keysym == 'space':
                    if drop_callback:
                        # Simulate a drop event
                        drop_callback(event)
                    return "break"
                return None
            
            # Bind keyboard events
            widget.bind("<KeyPress>", on_key_press)
            widget.bind("<Button-1>", lambda e: widget.focus_set())
            
            # Make widget focusable
            widget.configure(takefocus=True)
            
        except Exception as e:
            # Silently ignore errors in keyboard support
            pass

    # =============================================================================
    # THEME-AWARE TUPLES (Enhanced)
    # =============================================================================
    
    # Using enhanced theme system for automatic light/dark switching
    TUPLE_BG = enhanced_theme.get_color_tuple("background")
    TUPLE_SURFACE = enhanced_theme.get_color_tuple("surface")
    TUPLE_CARD = enhanced_theme.get_color_tuple("card")
    TUPLE_BORDER = enhanced_theme.get_color_tuple("border")
    TUPLE_PRIMARY = enhanced_theme.get_color_tuple("primary")
    TUPLE_PRIMARY_HOVER = enhanced_theme.get_color_tuple("primary_hover")
    TUPLE_TEXT_PRIMARY = enhanced_theme.get_color_tuple("text_primary")
    TUPLE_TEXT_SECONDARY = enhanced_theme.get_color_tuple("text_secondary")
    TUPLE_SUCCESS = enhanced_theme.get_color_tuple("success")
    TUPLE_DANGER = enhanced_theme.get_color_tuple("danger")
    TUPLE_WARNING = (COLOR_WARNING, COLOR_WARNING)  # Same for both modes
    TUPLE_INFO = enhanced_theme.get_color_tuple("info")
    TUPLE_SECONDARY = enhanced_theme.get_color_tuple("secondary")
    
    # Enhanced input colors
    TUPLE_INPUT_BG = TUPLE_SURFACE
    TUPLE_INPUT_BORDER = TUPLE_BORDER
    TUPLE_INPUT_FOCUS = TUPLE_PRIMARY
    
    # Color tuples for CTk widgets
    TUPLE_BG_SECONDARY = (enhanced_theme.get_color("surface"), enhanced_theme.get_color("surface", "dark"))
    TUPLE_SECONDARY = (enhanced_theme.get_color("secondary"), enhanced_theme.get_color("secondary", "dark"))
    
    # Additional color tuples
    TUPLE_TEXT_ON_PRIMARY = (enhanced_theme.get_color("text_on_primary"), enhanced_theme.get_color("text_on_primary", "dark"))
    TUPLE_TEXT_PRIMARY = (enhanced_theme.get_color("text_primary"), enhanced_theme.get_color("text_primary", "dark"))

    # =============================================================================
    # ENHANCED COLOR ACCESS METHODS
    # =============================================================================
    
    @classmethod
    def get_color(cls, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color using the enhanced theme system."""
        return cls._theme_provider.get_color(color_name, mode)
    
    @classmethod
    def get_workflow_colors(cls, workflow_id: str) -> Dict[str, str]:
        """Get workflow colors using the enhanced theme system."""
        return cls._theme_provider.get_workflow_colors(workflow_id)
    
    @classmethod
    def get_theme_tuple(cls, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        return cls._theme_provider.get_color_tuple(color_name)
    
    # =============================================================================
    # FONT CONSTANTS
    # =============================================================================
    
    # Font families
    FONT_FAMILY_UI = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    
    # Font sizes
    FONT_SIZE_SMALL = 10
    FONT_SIZE_BODY_SMALL = 11
    FONT_SIZE_BODY = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_XXL = 24
    FONT_SIZE_TITLE = 28
    
    # Font specifications (size, weight)
    H1_SPECS = (24, "bold")
    H2_SPECS = (18, "bold")
    H3_SPECS = (16, "bold")
    H4_SPECS = (14, "bold")
    BODY_SPECS = (12, "normal")
    BODY_SMALL_SPECS = (11, "normal")
    CAPTION_SPECS = (10, "normal")
    
    @classmethod
    def get_font(cls, font_type: str) -> 'ctk.CTkFont':
        """Get a CTkFont instance for the specified font type."""
        import customtkinter as ctk
        
        font_specs = {
            "h1": cls.H1_SPECS,
            "h2": cls.H2_SPECS,
            "h3": cls.H3_SPECS,
            "h4": cls.H4_SPECS,
            "body": cls.BODY_SPECS,
            "body_small": cls.BODY_SMALL_SPECS,
            "caption": cls.CAPTION_SPECS,
        }
        
        if font_type.lower() in font_specs:
            size, weight = font_specs[font_type.lower()]
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=size, weight=weight)
        else:
            # Default to body font
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=cls.FONT_SIZE_BODY, weight="normal")
    
    @classmethod
    def get_custom_font(cls, size: int, weight: str = "normal", family: str = None) -> 'ctk.CTkFont':
        """Get a custom CTkFont instance."""
        import customtkinter as ctk
        return ctk.CTkFont(
            family=family or cls.FONT_FAMILY_UI,
            size=size,
            weight=weight
        )

    # =============================================================================
    # LAYOUT CONSTANTS
    # =============================================================================
    
    # Corner radius
    CORNER_RADIUS_SMALL = 4
    CORNER_RADIUS = 8
    CORNER_RADIUS_LARGE = 12
    CORNER_RADIUS_XL = 16
    
    # Spacing
    SPACING_XS = 4
    SPACING_S = 8
    SPACING_M = 12
    SPACING_L = 16
    SPACING_XL = 20
    SPACING_XXL = 24
    
    # Padding
    PADDING_XS = 4
    PADDING_S = 8
    PADDING_M = 12
    PADDING_L = 16
    PADDING_XL = 20
    
    # =============================================================================
    # COMPONENT DIMENSIONS
    # =============================================================================
    
    # Button heights
    BUTTON_HEIGHT_SMALL = 28
    BUTTON_HEIGHT_MEDIUM = 32
    BUTTON_HEIGHT_LARGE = 36
    
    # Card heights
    CARD_HEIGHT_COMPACT = 80
    CARD_HEIGHT_MEDIUM = 120
    CARD_HEIGHT_LARGE = 160
    
    # =============================================================================
    # CONTAINER COLORS
    # =============================================================================
    
    # Container specific colors
    COLOR_CONTAINER_UPLOAD = enhanced_theme.get_color("info")
    COLOR_CONTAINER_UPLOAD_LIGHT = enhanced_theme.get_color("info_surface")
    COLOR_CONTAINER_WORKFLOW = enhanced_theme.get_color("warning")
    COLOR_CONTAINER_CUSTOMER = enhanced_theme.get_color("success")
    
    # Additional surface colors
    COLOR_SURFACE_VARIANT = enhanced_theme.get_color("surface")
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Card colors
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Button colors
    COLOR_BUTTON_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_BUTTON_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_BUTTON_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_BUTTON_SUCCESS = enhanced_theme.get_color("success")
    COLOR_BUTTON_INFO = enhanced_theme.get_color("info")
    
    # =============================================================================
    # COMPONENT STYLES (Dictionary-based for easy application)
    # =============================================================================
    
    # Container styles
    @classmethod
    def get_container_style_upload(cls):
        return {
            "fg_color": cls.COLOR_CONTAINER_UPLOAD_LIGHT,
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_UPLOAD,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_workflow(cls):
        return {
            "fg_color": enhanced_theme.get_color("warning_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_WORKFLOW,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_customer(cls):
        return {
            "fg_color": enhanced_theme.get_color("success_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_CUSTOMER,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    # Static container styles for backward compatibility
    @classmethod
    def CONTAINER_STYLE_UPLOAD(cls):
        return cls.get_container_style_upload()
    
    @classmethod
    def CONTAINER_STYLE_WORKFLOW(cls):
        return cls.get_container_style_workflow()
    
    @classmethod
    def CONTAINER_STYLE_CUSTOMER(cls):
        return cls.get_container_style_customer()
    
    # Button styles
    @classmethod
    def get_button_style_primary(cls):
        return {
            "fg_color": cls.COLOR_PRIMARY,
            "hover_color": cls.COLOR_PRIMARY_HOVER,
            "text_color": cls.COLOR_TEXT_ON_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 0
        }
    
    @classmethod
    def get_button_style_secondary(cls):
        return {
            "fg_color": cls.COLOR_SECONDARY,
            "hover_color": cls.COLOR_SECONDARY_HOVER,
            "text_color": cls.COLOR_TEXT_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_card_style_elevated(cls):
        return {
            "fg_color": cls.COLOR_CARD_ELEVATED,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_input_style_modern(cls):
        return {
            "fg_color": cls.COLOR_SURFACE,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER,
            "corner_radius": cls.CORNER_RADIUS,
            "text_color": cls.COLOR_TEXT_PRIMARY
        }
    
    # Static style dictionaries for backward compatibility
    @classmethod
    def BUTTON_STYLE_PRIMARY(cls):
        return cls.get_button_style_primary()
    
    @classmethod
    def BUTTON_STYLE_SECONDARY(cls):
        return cls.get_button_style_secondary()
    
    @classmethod
    def CARD_STYLE_ELEVATED(cls):
        return cls.get_card_style_elevated()
    
    @classmethod
    def INPUT_STYLE_MODERN(cls):
        return cls.get_input_style_modern()
    
    # =============================================================================
    # LEGACY COLOR CONSTANTS (maintained for backward compatibility)
    # =============================================================================
    
    # Auto-generated from enhanced theme system
    @property
    @classmethod
    def COLOR_BACKGROUND(cls) -> str:
        return cls.get_color("background")
    
    @property
    @classmethod  
    def COLOR_PRIMARY(cls) -> str:
        return cls.get_color("primary")
    
    @property
    @classmethod
    def COLOR_PRIMARY_HOVER(cls) -> str:
        return cls.get_color("primary_hover")
    
    # =============================================================================
    # ORIGINAL CONSTANTS (preserved for immediate compatibility)
    # =============================================================================
    
    # 1. Modern Color Palette - Now references enhanced theme system
    COLOR_BACKGROUND = enhanced_theme.get_color("background")
    APP_BG_COLOR = COLOR_BACKGROUND
    COLOR_SURFACE = enhanced_theme.get_color("surface")
    COLOR_CARD = enhanced_theme.get_color("card")
    COLOR_BORDER = enhanced_theme.get_color("border")
    COLOR_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_PRIMARY_CONTAINER = enhanced_theme.get_color("primary_container")
    COLOR_PRIMARY_SURFACE = enhanced_theme.get_color("primary_surface")
    COLOR_PRIMARY_ACCENT = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_ACCENT_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_ACCENT = enhanced_theme.get_color("accent")
    COLOR_ACCENT_HOVER = enhanced_theme.get_color("accent_hover")
    COLOR_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_SUCCESS = enhanced_theme.get_color("success")
    COLOR_SUCCESS_HOVER = enhanced_theme.get_color("success_hover")
    COLOR_DANGER = enhanced_theme.get_color("danger")
    COLOR_DANGER_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_ERROR = COLOR_DANGER
    COLOR_WARNING = enhanced_theme.get_color("warning")
    COLOR_INFO = enhanced_theme.get_color("info")
    COLOR_INFO_HOVER = enhanced_theme.get_color("info_hover")
    COLOR_TEXT_PRIMARY = enhanced_theme.get_color("text_primary")
    COLOR_TEXT_SECONDARY = enhanced_theme.get_color("text_secondary")
    COLOR_TEXT_ON_PRIMARY = enhanced_theme.get_color("text_on_primary")
    COLOR_TEXT_ON_DARK = enhanced_theme.get_color("text_on_dark")
    COLOR_BUTTON_TEXT = enhanced_theme.get_color("text_on_primary")
    
    # Enhanced Icon Colors
    COLOR_ICON = enhanced_theme.get_color("icon")
    COLOR_ICON_LIGHT = enhanced_theme.get_color("icon_light")
    COLOR_ICON_ACCENT = enhanced_theme.get_color("icon_accent")
    COLOR_ICON_DANGER = enhanced_theme.get_color("icon_danger")
    COLOR_ICON_SUCCESS = enhanced_theme.get_color("icon_success")
    COLOR_ICON_WARNING = enhanced_theme.get_color("icon_warning")
    
    # Menu and Navigation
    COLOR_MENU_ICON = enhanced_theme.get_color("menu_icon")
    COLOR_MENU_HOVER = enhanced_theme.get_color("menu_hover")
    
    # Header and Control Colors
    COLOR_HEADER_ICON = enhanced_theme.get_color("header_icon")
    COLOR_CONTROL_HOVER = enhanced_theme.get_color("control_hover")
    
    # Workflow colors - dynamically generated
    COLOR_WORKFLOW_ANGEBOTS = enhanced_theme.get_workflow_colors("angebots_workflow")["primary"]
    COLOR_WORKFLOW_PRUEFUNG = enhanced_theme.get_workflow_colors("pruefung_workflow")["primary"]
    COLOR_WORKFLOW_FINALISIERUNG = enhanced_theme.get_workflow_colors("finalisierung_workflow")["primary"]
    COLOR_WORKFLOW_MULTI = enhanced_theme.get_workflow_colors("projekt_workflow")["primary"]
    
    # Surface Colors for alerts/banners
    COLOR_DANGER_SURFACE = enhanced_theme.get_color("danger_surface")
    COLOR_INFO_SURFACE = enhanced_theme.get_color("info_surface")
    COLOR_SUCCESS_SURFACE = enhanced_theme.get_color("success_surface")
    COLOR_WARNING_SURFACE = enhanced_theme.get_color("warning_surface")
    
    # Additional legacy colors (from original theme)
    COLOR_PURPLE = "#8B5CF6"
    COLOR_DANGER_BORDER_LIGHT = "#F5C6CB"
    COLOR_INFO_BORDER_LIGHT = "#BEE5EB"
    COLOR_SUCCESS_BORDER_LIGHT = "#C3E6CB"
    COLOR_WARNING_BORDER_LIGHT = "#FFEEBA"
    COLOR_SUCCESS_LIGHT = enhanced_theme.get_color("success_surface")
    COLOR_ERROR_LIGHT = enhanced_theme.get_color("danger_surface")
    COLOR_ERROR_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_BG_SECONDARY = "#F8F9FA"
    
    # Dark Mode Colors - now dynamically fetched
    COLOR_BACKGROUND_DARK = enhanced_theme.get_color("background", "dark")
    COLOR_SURFACE_DARK = enhanced_theme.get_color("surface", "dark")
    COLOR_CARD_DARK = enhanced_theme.get_color("card", "dark")
    COLOR_BORDER_DARK = enhanced_theme.get_color("border", "dark")
    COLOR_PRIMARY_DARK = enhanced_theme.get_color("primary", "dark")
    COLOR_PRIMARY_HOVER_DARK = enhanced_theme.get_color("primary_hover", "dark")
    COLOR_TEXT_PRIMARY_DARK = enhanced_theme.get_color("text_primary", "dark")
    COLOR_TEXT_SECONDARY_DARK = enhanced_theme.get_color("text_secondary", "dark")
    
    # Dark Mode Icon Colors
    COLOR_ICON_DARK = enhanced_theme.get_color("icon", "dark")
    COLOR_ICON_LIGHT_DARK = enhanced_theme.get_color("icon_light", "dark")
    COLOR_ICON_ACCENT_DARK = enhanced_theme.get_color("icon_accent", "dark")
    COLOR_ICON_DANGER_DARK = enhanced_theme.get_color("icon_danger", "dark")
    COLOR_ICON_SUCCESS_DARK = enhanced_theme.get_color("icon_success", "dark")
    COLOR_ICON_WARNING_DARK = enhanced_theme.get_color("icon_warning", "dark")
    
    # Menu and Navigation dark mode
    COLOR_MENU_ICON_DARK = enhanced_theme.get_color("menu_icon", "dark")
    COLOR_MENU_HOVER_DARK = enhanced_theme.get_color("menu_hover", "dark")
    COLOR_HEADER_ICON_DARK = enhanced_theme.get_color("header_icon", "dark")
    COLOR_CONTROL_HOVER_DARK = enhanced_theme.get_color("control_hover", "dark")
    
    # Dark Mode Surfaces
    COLOR_DANGER_SURFACE_DARK = enhanced_theme.get_color("danger_surface", "dark")
    COLOR_INFO_SURFACE_DARK = enhanced_theme.get_color("info_surface", "dark")
    COLOR_SUCCESS_SURFACE_DARK = enhanced_theme.get_color("success_surface", "dark")
    COLOR_WARNING_SURFACE_DARK = enhanced_theme.get_color("warning_surface", "dark")
    
    # Secondary, Success, Danger for dark mode
    COLOR_SECONDARY_DARK = enhanced_theme.get_color("secondary", "dark")
    COLOR_SECONDARY_HOVER_DARK = enhanced_theme.get_color("secondary_hover", "dark")
    COLOR_SUCCESS_DARK = enhanced_theme.get_color("success", "dark")
    COLOR_SUCCESS_HOVER_DARK = enhanced_theme.get_color("success_hover", "dark")
    COLOR_DANGER_DARK = enhanced_theme.get_color("danger", "dark")
    COLOR_DANGER_HOVER_DARK = enhanced_theme.get_color("danger_hover", "dark")
    
    # Surface hover colors
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Profile button colors
    COLOR_PROFILE_BUTTON_LIGHT = "#7B42F6"
    COLOR_PROFILE_BUTTON_HOVER_LIGHT = "#6A35D9"
    COLOR_PROFILE_BUTTON_DARK = "#8A5BF7"
    COLOR_PROFILE_BUTTON_HOVER_DARK = "#7B42F6"
    
    # Icon button colors
    COLOR_ICON_BUTTON_FG = ("gray85", "gray28")
    COLOR_ICON_BUTTON_HOVER = ("gray75", "gray38")
    
    # Enhanced Card Design
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_SHADOW = "#00000015"
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Modern Gradient Colors
    GRADIENT_PRIMARY_START = "#007BFF"
    GRADIENT_PRIMARY_END = "#0056B3"
    GRADIENT_SECONDARY_START = "#6C757D"
    GRADIENT_SECONDARY_END = "#495057"
    
    # Enhanced Status Colors
    COLOR_STATUS_ONLINE = enhanced_theme.get_color("success")
    COLOR_STATUS_OFFLINE = enhanced_theme.get_color("danger")
    COLOR_STATUS_PENDING = enhanced_theme.get_color("warning")
    COLOR_STATUS_PROCESSING = enhanced_theme.get_color("info")
    
    # Modern UI Elements
    COLOR_TOOLTIP_BG = "#343A40"
    COLOR_TOOLTIP_TEXT = "#FFFFFF"
    COLOR_OVERLAY = "#00000080"
    
    # =============================================================================
    # THEME-AWARE TUPLES (Enhanced)
    # =============================================================================
    
    # Using enhanced theme system for automatic light/dark switching
    TUPLE_BG = enhanced_theme.get_color_tuple("background")
    TUPLE_SURFACE = enhanced_theme.get_color_tuple("surface")
    TUPLE_CARD = enhanced_theme.get_color_tuple("card")
    TUPLE_BORDER = enhanced_theme.get_color_tuple("border")
    TUPLE_PRIMARY = enhanced_theme.get_color_tuple("primary")
    TUPLE_PRIMARY_HOVER = enhanced_theme.get_color_tuple("primary_hover")
    TUPLE_TEXT_PRIMARY = enhanced_theme.get_color_tuple("text_primary")
    TUPLE_TEXT_SECONDARY = enhanced_theme.get_color_tuple("text_secondary")
    TUPLE_SUCCESS = enhanced_theme.get_color_tuple("success")
    TUPLE_DANGER = enhanced_theme.get_color_tuple("danger")
    TUPLE_WARNING = (COLOR_WARNING, COLOR_WARNING)  # Same for both modes
    TUPLE_INFO = enhanced_theme.get_color_tuple("info")
    TUPLE_SECONDARY = enhanced_theme.get_color_tuple("secondary")
    
    # Enhanced input colors
    TUPLE_INPUT_BG = TUPLE_SURFACE
    TUPLE_INPUT_BORDER = TUPLE_BORDER
    TUPLE_INPUT_FOCUS = TUPLE_PRIMARY
    
    # Color tuples for CTk widgets
    TUPLE_BG_SECONDARY = (enhanced_theme.get_color("surface"), enhanced_theme.get_color("surface", "dark"))
    TUPLE_SECONDARY = (enhanced_theme.get_color("secondary"), enhanced_theme.get_color("secondary", "dark"))
    
    # Additional color tuples
    TUPLE_TEXT_ON_PRIMARY = (enhanced_theme.get_color("text_on_primary"), enhanced_theme.get_color("text_on_primary", "dark"))
    TUPLE_TEXT_PRIMARY = (enhanced_theme.get_color("text_primary"), enhanced_theme.get_color("text_primary", "dark"))

    # =============================================================================
    # ENHANCED COLOR ACCESS METHODS
    # =============================================================================
    
    @classmethod
    def get_color(cls, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color using the enhanced theme system."""
        return cls._theme_provider.get_color(color_name, mode)
    
    @classmethod
    def get_workflow_colors(cls, workflow_id: str) -> Dict[str, str]:
        """Get workflow colors using the enhanced theme system."""
        return cls._theme_provider.get_workflow_colors(workflow_id)
    
    @classmethod
    def get_theme_tuple(cls, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        return cls._theme_provider.get_color_tuple(color_name)
    
    # =============================================================================
    # FONT CONSTANTS
    # =============================================================================
    
    # Font families
    FONT_FAMILY_UI = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    
    # Font sizes
    FONT_SIZE_SMALL = 10
    FONT_SIZE_BODY_SMALL = 11
    FONT_SIZE_BODY = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_XXL = 24
    FONT_SIZE_TITLE = 28
    
    # Font specifications (size, weight)
    H1_SPECS = (24, "bold")
    H2_SPECS = (18, "bold")
    H3_SPECS = (16, "bold")
    H4_SPECS = (14, "bold")
    BODY_SPECS = (12, "normal")
    BODY_SMALL_SPECS = (11, "normal")
    CAPTION_SPECS = (10, "normal")
    
    @classmethod
    def get_font(cls, font_type: str) -> 'ctk.CTkFont':
        """Get a CTkFont instance for the specified font type."""
        import customtkinter as ctk
        
        font_specs = {
            "h1": cls.H1_SPECS,
            "h2": cls.H2_SPECS,
            "h3": cls.H3_SPECS,
            "h4": cls.H4_SPECS,
            "body": cls.BODY_SPECS,
            "body_small": cls.BODY_SMALL_SPECS,
            "caption": cls.CAPTION_SPECS,
        }
        
        if font_type.lower() in font_specs:
            size, weight = font_specs[font_type.lower()]
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=size, weight=weight)
        else:
            # Default to body font
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=cls.FONT_SIZE_BODY, weight="normal")
    
    @classmethod
    def get_custom_font(cls, size: int, weight: str = "normal", family: str = None) -> 'ctk.CTkFont':
        """Get a custom CTkFont instance."""
        import customtkinter as ctk
        return ctk.CTkFont(
            family=family or cls.FONT_FAMILY_UI,
            size=size,
            weight=weight
        )

    # =============================================================================
    # LAYOUT CONSTANTS
    # =============================================================================
    
    # Corner radius
    CORNER_RADIUS_SMALL = 4
    CORNER_RADIUS = 8
    CORNER_RADIUS_LARGE = 12
    CORNER_RADIUS_XL = 16
    
    # Spacing
    SPACING_XS = 4
    SPACING_S = 8
    SPACING_M = 12
    SPACING_L = 16
    SPACING_XL = 20
    SPACING_XXL = 24
    
    # Padding
    PADDING_XS = 4
    PADDING_S = 8
    PADDING_M = 12
    PADDING_L = 16
    PADDING_XL = 20
    
    # =============================================================================
    # COMPONENT DIMENSIONS
    # =============================================================================
    
    # Button heights
    BUTTON_HEIGHT_SMALL = 28
    BUTTON_HEIGHT_MEDIUM = 32
    BUTTON_HEIGHT_LARGE = 36
    
    # Card heights
    CARD_HEIGHT_COMPACT = 80
    CARD_HEIGHT_MEDIUM = 120
    CARD_HEIGHT_LARGE = 160
    
    # =============================================================================
    # CONTAINER COLORS
    # =============================================================================
    
    # Container specific colors
    COLOR_CONTAINER_UPLOAD = enhanced_theme.get_color("info")
    COLOR_CONTAINER_UPLOAD_LIGHT = enhanced_theme.get_color("info_surface")
    COLOR_CONTAINER_WORKFLOW = enhanced_theme.get_color("warning")
    COLOR_CONTAINER_CUSTOMER = enhanced_theme.get_color("success")
    
    # Additional surface colors
    COLOR_SURFACE_VARIANT = enhanced_theme.get_color("surface")
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Card colors
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Button colors
    COLOR_BUTTON_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_BUTTON_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_BUTTON_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_BUTTON_SUCCESS = enhanced_theme.get_color("success")
    COLOR_BUTTON_INFO = enhanced_theme.get_color("info")
    
    # =============================================================================
    # COMPONENT STYLES (Dictionary-based for easy application)
    # =============================================================================
    
    # Container styles
    @classmethod
    def get_container_style_upload(cls):
        return {
            "fg_color": cls.COLOR_CONTAINER_UPLOAD_LIGHT,
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_UPLOAD,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_workflow(cls):
        return {
            "fg_color": enhanced_theme.get_color("warning_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_WORKFLOW,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_customer(cls):
        return {
            "fg_color": enhanced_theme.get_color("success_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_CUSTOMER,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    # Static container styles for backward compatibility
    @classmethod
    def CONTAINER_STYLE_UPLOAD(cls):
        return cls.get_container_style_upload()
    
    @classmethod
    def CONTAINER_STYLE_WORKFLOW(cls):
        return cls.get_container_style_workflow()
    
    @classmethod
    def CONTAINER_STYLE_CUSTOMER(cls):
        return cls.get_container_style_customer()
    
    # Button styles
    @classmethod
    def get_button_style_primary(cls):
        return {
            "fg_color": cls.COLOR_PRIMARY,
            "hover_color": cls.COLOR_PRIMARY_HOVER,
            "text_color": cls.COLOR_TEXT_ON_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 0
        }
    
    @classmethod
    def get_button_style_secondary(cls):
        return {
            "fg_color": cls.COLOR_SECONDARY,
            "hover_color": cls.COLOR_SECONDARY_HOVER,
            "text_color": cls.COLOR_TEXT_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_card_style_elevated(cls):
        return {
            "fg_color": cls.COLOR_CARD_ELEVATED,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_input_style_modern(cls):
        return {
            "fg_color": cls.COLOR_SURFACE,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER,
            "corner_radius": cls.CORNER_RADIUS,
            "text_color": cls.COLOR_TEXT_PRIMARY
        }
    
    # Static style dictionaries for backward compatibility
    @classmethod
    def BUTTON_STYLE_PRIMARY(cls):
        return cls.get_button_style_primary()
    
    @classmethod
    def BUTTON_STYLE_SECONDARY(cls):
        return cls.get_button_style_secondary()
    
    @classmethod
    def CARD_STYLE_ELEVATED(cls):
        return cls.get_card_style_elevated()
    
    @classmethod
    def INPUT_STYLE_MODERN(cls):
        return cls.get_input_style_modern()
    
    # =============================================================================
    # LEGACY COLOR CONSTANTS (maintained for backward compatibility)
    # =============================================================================
    
    # Auto-generated from enhanced theme system
    @property
    @classmethod
    def COLOR_BACKGROUND(cls) -> str:
        return cls.get_color("background")
    
    @property
    @classmethod  
    def COLOR_PRIMARY(cls) -> str:
        return cls.get_color("primary")
    
    @property
    @classmethod
    def COLOR_PRIMARY_HOVER(cls) -> str:
        return cls.get_color("primary_hover")
    
    # =============================================================================
    # ORIGINAL CONSTANTS (preserved for immediate compatibility)
    # =============================================================================
    
    # 1. Modern Color Palette - Now references enhanced theme system
    COLOR_BACKGROUND = enhanced_theme.get_color("background")
    APP_BG_COLOR = COLOR_BACKGROUND
    COLOR_SURFACE = enhanced_theme.get_color("surface")
    COLOR_CARD = enhanced_theme.get_color("card")
    COLOR_BORDER = enhanced_theme.get_color("border")
    COLOR_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_PRIMARY_CONTAINER = enhanced_theme.get_color("primary_container")
    COLOR_PRIMARY_SURFACE = enhanced_theme.get_color("primary_surface")
    COLOR_PRIMARY_ACCENT = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_ACCENT_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_ACCENT = enhanced_theme.get_color("accent")
    COLOR_ACCENT_HOVER = enhanced_theme.get_color("accent_hover")
    COLOR_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_SUCCESS = enhanced_theme.get_color("success")
    COLOR_SUCCESS_HOVER = enhanced_theme.get_color("success_hover")
    COLOR_DANGER = enhanced_theme.get_color("danger")
    COLOR_DANGER_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_ERROR = COLOR_DANGER
    COLOR_WARNING = enhanced_theme.get_color("warning")
    COLOR_INFO = enhanced_theme.get_color("info")
    COLOR_INFO_HOVER = enhanced_theme.get_color("info_hover")
    COLOR_TEXT_PRIMARY = enhanced_theme.get_color("text_primary")
    COLOR_TEXT_SECONDARY = enhanced_theme.get_color("text_secondary")
    COLOR_TEXT_ON_PRIMARY = enhanced_theme.get_color("text_on_primary")
    COLOR_TEXT_ON_DARK = enhanced_theme.get_color("text_on_dark")
    COLOR_BUTTON_TEXT = enhanced_theme.get_color("text_on_primary")
    
    # Enhanced Icon Colors
    COLOR_ICON = enhanced_theme.get_color("icon")
    COLOR_ICON_LIGHT = enhanced_theme.get_color("icon_light")
    COLOR_ICON_ACCENT = enhanced_theme.get_color("icon_accent")
    COLOR_ICON_DANGER = enhanced_theme.get_color("icon_danger")
    COLOR_ICON_SUCCESS = enhanced_theme.get_color("icon_success")
    COLOR_ICON_WARNING = enhanced_theme.get_color("icon_warning")
    
    # Menu and Navigation
    COLOR_MENU_ICON = enhanced_theme.get_color("menu_icon")
    COLOR_MENU_HOVER = enhanced_theme.get_color("menu_hover")
    
    # Header and Control Colors
    COLOR_HEADER_ICON = enhanced_theme.get_color("header_icon")
    COLOR_CONTROL_HOVER = enhanced_theme.get_color("control_hover")
    
    # Workflow colors - dynamically generated
    COLOR_WORKFLOW_ANGEBOTS = enhanced_theme.get_workflow_colors("angebots_workflow")["primary"]
    COLOR_WORKFLOW_PRUEFUNG = enhanced_theme.get_workflow_colors("pruefung_workflow")["primary"]
    COLOR_WORKFLOW_FINALISIERUNG = enhanced_theme.get_workflow_colors("finalisierung_workflow")["primary"]
    COLOR_WORKFLOW_MULTI = enhanced_theme.get_workflow_colors("projekt_workflow")["primary"]
    
    # Surface Colors for alerts/banners
    COLOR_DANGER_SURFACE = enhanced_theme.get_color("danger_surface")
    COLOR_INFO_SURFACE = enhanced_theme.get_color("info_surface")
    COLOR_SUCCESS_SURFACE = enhanced_theme.get_color("success_surface")
    COLOR_WARNING_SURFACE = enhanced_theme.get_color("warning_surface")
    
    # Additional legacy colors (from original theme)
    COLOR_PURPLE = "#8B5CF6"
    COLOR_DANGER_BORDER_LIGHT = "#F5C6CB"
    COLOR_INFO_BORDER_LIGHT = "#BEE5EB"
    COLOR_SUCCESS_BORDER_LIGHT = "#C3E6CB"
    COLOR_WARNING_BORDER_LIGHT = "#FFEEBA"
    COLOR_SUCCESS_LIGHT = enhanced_theme.get_color("success_surface")
    COLOR_ERROR_LIGHT = enhanced_theme.get_color("danger_surface")
    COLOR_ERROR_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_BG_SECONDARY = "#F8F9FA"
    
    # Dark Mode Colors - now dynamically fetched
    COLOR_BACKGROUND_DARK = enhanced_theme.get_color("background", "dark")
    COLOR_SURFACE_DARK = enhanced_theme.get_color("surface", "dark")
    COLOR_CARD_DARK = enhanced_theme.get_color("card", "dark")
    COLOR_BORDER_DARK = enhanced_theme.get_color("border", "dark")
    COLOR_PRIMARY_DARK = enhanced_theme.get_color("primary", "dark")
    COLOR_PRIMARY_HOVER_DARK = enhanced_theme.get_color("primary_hover", "dark")
    COLOR_TEXT_PRIMARY_DARK = enhanced_theme.get_color("text_primary", "dark")
    COLOR_TEXT_SECONDARY_DARK = enhanced_theme.get_color("text_secondary", "dark")
    
    # Dark Mode Icon Colors
    COLOR_ICON_DARK = enhanced_theme.get_color("icon", "dark")
    COLOR_ICON_LIGHT_DARK = enhanced_theme.get_color("icon_light", "dark")
    COLOR_ICON_ACCENT_DARK = enhanced_theme.get_color("icon_accent", "dark")
    COLOR_ICON_DANGER_DARK = enhanced_theme.get_color("icon_danger", "dark")
    COLOR_ICON_SUCCESS_DARK = enhanced_theme.get_color("icon_success", "dark")
    COLOR_ICON_WARNING_DARK = enhanced_theme.get_color("icon_warning", "dark")
    
    # Menu and Navigation dark mode
    COLOR_MENU_ICON_DARK = enhanced_theme.get_color("menu_icon", "dark")
    COLOR_MENU_HOVER_DARK = enhanced_theme.get_color("menu_hover", "dark")
    COLOR_HEADER_ICON_DARK = enhanced_theme.get_color("header_icon", "dark")
    COLOR_CONTROL_HOVER_DARK = enhanced_theme.get_color("control_hover", "dark")
    
    # Dark Mode Surfaces
    COLOR_DANGER_SURFACE_DARK = enhanced_theme.get_color("danger_surface", "dark")
    COLOR_INFO_SURFACE_DARK = enhanced_theme.get_color("info_surface", "dark")
    COLOR_SUCCESS_SURFACE_DARK = enhanced_theme.get_color("success_surface", "dark")
    COLOR_WARNING_SURFACE_DARK = enhanced_theme.get_color("warning_surface", "dark")
    
    # Secondary, Success, Danger for dark mode
    COLOR_SECONDARY_DARK = enhanced_theme.get_color("secondary", "dark")
    COLOR_SECONDARY_HOVER_DARK = enhanced_theme.get_color("secondary_hover", "dark")
    COLOR_SUCCESS_DARK = enhanced_theme.get_color("success", "dark")
    COLOR_SUCCESS_HOVER_DARK = enhanced_theme.get_color("success_hover", "dark")
    COLOR_DANGER_DARK = enhanced_theme.get_color("danger", "dark")
    COLOR_DANGER_HOVER_DARK = enhanced_theme.get_color("danger_hover", "dark")
    
    # Surface hover colors
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Profile button colors
    COLOR_PROFILE_BUTTON_LIGHT = "#7B42F6"
    COLOR_PROFILE_BUTTON_HOVER_LIGHT = "#6A35D9"
    COLOR_PROFILE_BUTTON_DARK = "#8A5BF7"
    COLOR_PROFILE_BUTTON_HOVER_DARK = "#7B42F6"
    
    # Icon button colors
    COLOR_ICON_BUTTON_FG = ("gray85", "gray28")
    COLOR_ICON_BUTTON_HOVER = ("gray75", "gray38")
    
    # Enhanced Card Design
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_SHADOW = "#00000015"
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Modern Gradient Colors
    GRADIENT_PRIMARY_START = "#007BFF"
    GRADIENT_PRIMARY_END = "#0056B3"
    GRADIENT_SECONDARY_START = "#6C757D"
    GRADIENT_SECONDARY_END = "#495057"
    
    # Enhanced Status Colors
    COLOR_STATUS_ONLINE = enhanced_theme.get_color("success")
    COLOR_STATUS_OFFLINE = enhanced_theme.get_color("danger")
    COLOR_STATUS_PENDING = enhanced_theme.get_color("warning")
    COLOR_STATUS_PROCESSING = enhanced_theme.get_color("info")
    
    # Modern UI Elements
    COLOR_TOOLTIP_BG = "#343A40"
    COLOR_TOOLTIP_TEXT = "#FFFFFF"
    COLOR_OVERLAY = "#00000080"
    
    # =============================================================================
    # THEME-AWARE TUPLES (Enhanced)
    # =============================================================================
    
    # Using enhanced theme system for automatic light/dark switching
    TUPLE_BG = enhanced_theme.get_color_tuple("background")
    TUPLE_SURFACE = enhanced_theme.get_color_tuple("surface")
    TUPLE_CARD = enhanced_theme.get_color_tuple("card")
    TUPLE_BORDER = enhanced_theme.get_color_tuple("border")
    TUPLE_PRIMARY = enhanced_theme.get_color_tuple("primary")
    TUPLE_PRIMARY_HOVER = enhanced_theme.get_color_tuple("primary_hover")
    TUPLE_TEXT_PRIMARY = enhanced_theme.get_color_tuple("text_primary")
    TUPLE_TEXT_SECONDARY = enhanced_theme.get_color_tuple("text_secondary")
    TUPLE_SUCCESS = enhanced_theme.get_color_tuple("success")
    TUPLE_DANGER = enhanced_theme.get_color_tuple("danger")
    TUPLE_WARNING = (COLOR_WARNING, COLOR_WARNING)  # Same for both modes
    TUPLE_INFO = enhanced_theme.get_color_tuple("info")
    TUPLE_SECONDARY = enhanced_theme.get_color_tuple("secondary")
    
    # Enhanced input colors
    TUPLE_INPUT_BG = TUPLE_SURFACE
    TUPLE_INPUT_BORDER = TUPLE_BORDER
    TUPLE_INPUT_FOCUS = TUPLE_PRIMARY
    
    # Color tuples for CTk widgets
    TUPLE_BG_SECONDARY = (enhanced_theme.get_color("surface"), enhanced_theme.get_color("surface", "dark"))
    TUPLE_SECONDARY = (enhanced_theme.get_color("secondary"), enhanced_theme.get_color("secondary", "dark"))
    
    # Additional color tuples
    TUPLE_TEXT_ON_PRIMARY = (enhanced_theme.get_color("text_on_primary"), enhanced_theme.get_color("text_on_primary", "dark"))
    TUPLE_TEXT_PRIMARY = (enhanced_theme.get_color("text_primary"), enhanced_theme.get_color("text_primary", "dark"))

    # =============================================================================
    # ENHANCED COLOR ACCESS METHODS
    # =============================================================================
    
    @classmethod
    def get_color(cls, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color using the enhanced theme system."""
        return cls._theme_provider.get_color(color_name, mode)
    
    @classmethod
    def get_workflow_colors(cls, workflow_id: str) -> Dict[str, str]:
        """Get workflow colors using the enhanced theme system."""
        return cls._theme_provider.get_workflow_colors(workflow_id)
    
    @classmethod
    def get_theme_tuple(cls, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        return cls._theme_provider.get_color_tuple(color_name)
    
    # =============================================================================
    # FONT CONSTANTS
    # =============================================================================
    
    # Font families
    FONT_FAMILY_UI = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    
    # Font sizes
    FONT_SIZE_SMALL = 10
    FONT_SIZE_BODY_SMALL = 11
    FONT_SIZE_BODY = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_XXL = 24
    FONT_SIZE_TITLE = 28
    
    # Font specifications (size, weight)
    H1_SPECS = (24, "bold")
    H2_SPECS = (18, "bold")
    H3_SPECS = (16, "bold")
    H4_SPECS = (14, "bold")
    BODY_SPECS = (12, "normal")
    BODY_SMALL_SPECS = (11, "normal")
    CAPTION_SPECS = (10, "normal")
    
    @classmethod
    def get_font(cls, font_type: str) -> 'ctk.CTkFont':
        """Get a CTkFont instance for the specified font type."""
        import customtkinter as ctk
        
        font_specs = {
            "h1": cls.H1_SPECS,
            "h2": cls.H2_SPECS,
            "h3": cls.H3_SPECS,
            "h4": cls.H4_SPECS,
            "body": cls.BODY_SPECS,
            "body_small": cls.BODY_SMALL_SPECS,
            "caption": cls.CAPTION_SPECS,
        }
        
        if font_type.lower() in font_specs:
            size, weight = font_specs[font_type.lower()]
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=size, weight=weight)
        else:
            # Default to body font
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=cls.FONT_SIZE_BODY, weight="normal")
    
    @classmethod
    def get_custom_font(cls, size: int, weight: str = "normal", family: str = None) -> 'ctk.CTkFont':
        """Get a custom CTkFont instance."""
        import customtkinter as ctk
        return ctk.CTkFont(
            family=family or cls.FONT_FAMILY_UI,
            size=size,
            weight=weight
        )

    # =============================================================================
    # LAYOUT CONSTANTS
    # =============================================================================
    
    # Corner radius
    CORNER_RADIUS_SMALL = 4
    CORNER_RADIUS = 8
    CORNER_RADIUS_LARGE = 12
    CORNER_RADIUS_XL = 16
    
    # Spacing
    SPACING_XS = 4
    SPACING_S = 8
    SPACING_M = 12
    SPACING_L = 16
    SPACING_XL = 20
    SPACING_XXL = 24
    
    # Padding
    PADDING_XS = 4
    PADDING_S = 8
    PADDING_M = 12
    PADDING_L = 16
    PADDING_XL = 20
    
    # =============================================================================
    # COMPONENT DIMENSIONS
    # =============================================================================
    
    # Button heights
    BUTTON_HEIGHT_SMALL = 28
    BUTTON_HEIGHT_MEDIUM = 32
    BUTTON_HEIGHT_LARGE = 36
    
    # Card heights
    CARD_HEIGHT_COMPACT = 80
    CARD_HEIGHT_MEDIUM = 120
    CARD_HEIGHT_LARGE = 160
    
    # =============================================================================
    # CONTAINER COLORS
    # =============================================================================
    
    # Container specific colors
    COLOR_CONTAINER_UPLOAD = enhanced_theme.get_color("info")
    COLOR_CONTAINER_UPLOAD_LIGHT = enhanced_theme.get_color("info_surface")
    COLOR_CONTAINER_WORKFLOW = enhanced_theme.get_color("warning")
    COLOR_CONTAINER_CUSTOMER = enhanced_theme.get_color("success")
    
    # Additional surface colors
    COLOR_SURFACE_VARIANT = enhanced_theme.get_color("surface")
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Card colors
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Button colors
    COLOR_BUTTON_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_BUTTON_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_BUTTON_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_BUTTON_SUCCESS = enhanced_theme.get_color("success")
    COLOR_BUTTON_INFO = enhanced_theme.get_color("info")
    
    # =============================================================================
    # COMPONENT STYLES (Dictionary-based for easy application)
    # =============================================================================
    
    # Container styles
    @classmethod
    def get_container_style_upload(cls):
        return {
            "fg_color": cls.COLOR_CONTAINER_UPLOAD_LIGHT,
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_UPLOAD,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_workflow(cls):
        return {
            "fg_color": enhanced_theme.get_color("warning_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_WORKFLOW,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    @classmethod
    def get_container_style_customer(cls):
        return {
            "fg_color": enhanced_theme.get_color("success_surface"),
            "border_width": 1,
            "border_color": cls.COLOR_CONTAINER_CUSTOMER,
            "corner_radius": cls.CORNER_RADIUS_LARGE
        }
    
    # Static container styles for backward compatibility
    @classmethod
    def CONTAINER_STYLE_UPLOAD(cls):
        return cls.get_container_style_upload()
    
    @classmethod
    def CONTAINER_STYLE_WORKFLOW(cls):
        return cls.get_container_style_workflow()
    
    @classmethod
    def CONTAINER_STYLE_CUSTOMER(cls):
        return cls.get_container_style_customer()
    
    # Button styles
    @classmethod
    def get_button_style_primary(cls):
        return {
            "fg_color": cls.COLOR_PRIMARY,
            "hover_color": cls.COLOR_PRIMARY_HOVER,
            "text_color": cls.COLOR_TEXT_ON_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 0
        }
    
    @classmethod
    def get_button_style_secondary(cls):
        return {
            "fg_color": cls.COLOR_SECONDARY,
            "hover_color": cls.COLOR_SECONDARY_HOVER,
            "text_color": cls.COLOR_TEXT_PRIMARY,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_card_style_elevated(cls):
        return {
            "fg_color": cls.COLOR_CARD_ELEVATED,
            "corner_radius": cls.CORNER_RADIUS,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER
        }
    
    @classmethod
    def get_input_style_modern(cls):
        return {
            "fg_color": cls.COLOR_SURFACE,
            "border_width": 1,
            "border_color": cls.COLOR_BORDER,
            "corner_radius": cls.CORNER_RADIUS,
            "text_color": cls.COLOR_TEXT_PRIMARY
        }
    
    # Static style dictionaries for backward compatibility
    @classmethod
    def BUTTON_STYLE_PRIMARY(cls):
        return cls.get_button_style_primary()
    
    @classmethod
    def BUTTON_STYLE_SECONDARY(cls):
        return cls.get_button_style_secondary()
    
    @classmethod
    def CARD_STYLE_ELEVATED(cls):
        return cls.get_card_style_elevated()
    
    @classmethod
    def INPUT_STYLE_MODERN(cls):
        return cls.get_input_style_modern()
    
    # =============================================================================
    # LEGACY COLOR CONSTANTS (maintained for backward compatibility)
    # =============================================================================
    
    # Auto-generated from enhanced theme system
    @property
    @classmethod
    def COLOR_BACKGROUND(cls) -> str:
        return cls.get_color("background")
    
    @property
    @classmethod  
    def COLOR_PRIMARY(cls) -> str:
        return cls.get_color("primary")
    
    @property
    @classmethod
    def COLOR_PRIMARY_HOVER(cls) -> str:
        return cls.get_color("primary_hover")
    
    # =============================================================================
    # ORIGINAL CONSTANTS (preserved for immediate compatibility)
    # =============================================================================
    
    # 1. Modern Color Palette - Now references enhanced theme system
    COLOR_BACKGROUND = enhanced_theme.get_color("background")
    APP_BG_COLOR = COLOR_BACKGROUND
    COLOR_SURFACE = enhanced_theme.get_color("surface")
    COLOR_CARD = enhanced_theme.get_color("card")
    COLOR_BORDER = enhanced_theme.get_color("border")
    COLOR_PRIMARY = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_PRIMARY_CONTAINER = enhanced_theme.get_color("primary_container")
    COLOR_PRIMARY_SURFACE = enhanced_theme.get_color("primary_surface")
    COLOR_PRIMARY_ACCENT = enhanced_theme.get_color("primary")
    COLOR_PRIMARY_ACCENT_HOVER = enhanced_theme.get_color("primary_hover")
    COLOR_ACCENT = enhanced_theme.get_color("accent")
    COLOR_ACCENT_HOVER = enhanced_theme.get_color("accent_hover")
    COLOR_SECONDARY = enhanced_theme.get_color("secondary")
    COLOR_SECONDARY_HOVER = enhanced_theme.get_color("secondary_hover")
    COLOR_SUCCESS = enhanced_theme.get_color("success")
    COLOR_SUCCESS_HOVER = enhanced_theme.get_color("success_hover")
    COLOR_DANGER = enhanced_theme.get_color("danger")
    COLOR_DANGER_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_ERROR = COLOR_DANGER
    COLOR_WARNING = enhanced_theme.get_color("warning")
    COLOR_INFO = enhanced_theme.get_color("info")
    COLOR_INFO_HOVER = enhanced_theme.get_color("info_hover")
    COLOR_TEXT_PRIMARY = enhanced_theme.get_color("text_primary")
    COLOR_TEXT_SECONDARY = enhanced_theme.get_color("text_secondary")
    COLOR_TEXT_ON_PRIMARY = enhanced_theme.get_color("text_on_primary")
    COLOR_TEXT_ON_DARK = enhanced_theme.get_color("text_on_dark")
    COLOR_BUTTON_TEXT = enhanced_theme.get_color("text_on_primary")
    
    # Enhanced Icon Colors
    COLOR_ICON = enhanced_theme.get_color("icon")
    COLOR_ICON_LIGHT = enhanced_theme.get_color("icon_light")
    COLOR_ICON_ACCENT = enhanced_theme.get_color("icon_accent")
    COLOR_ICON_DANGER = enhanced_theme.get_color("icon_danger")
    COLOR_ICON_SUCCESS = enhanced_theme.get_color("icon_success")
    COLOR_ICON_WARNING = enhanced_theme.get_color("icon_warning")
    
    # Menu and Navigation
    COLOR_MENU_ICON = enhanced_theme.get_color("menu_icon")
    COLOR_MENU_HOVER = enhanced_theme.get_color("menu_hover")
    
    # Header and Control Colors
    COLOR_HEADER_ICON = enhanced_theme.get_color("header_icon")
    COLOR_CONTROL_HOVER = enhanced_theme.get_color("control_hover")
    
    # Workflow colors - dynamically generated
    COLOR_WORKFLOW_ANGEBOTS = enhanced_theme.get_workflow_colors("angebots_workflow")["primary"]
    COLOR_WORKFLOW_PRUEFUNG = enhanced_theme.get_workflow_colors("pruefung_workflow")["primary"]
    COLOR_WORKFLOW_FINALISIERUNG = enhanced_theme.get_workflow_colors("finalisierung_workflow")["primary"]
    COLOR_WORKFLOW_MULTI = enhanced_theme.get_workflow_colors("projekt_workflow")["primary"]
    
    # Surface Colors for alerts/banners
    COLOR_DANGER_SURFACE = enhanced_theme.get_color("danger_surface")
    COLOR_INFO_SURFACE = enhanced_theme.get_color("info_surface")
    COLOR_SUCCESS_SURFACE = enhanced_theme.get_color("success_surface")
    COLOR_WARNING_SURFACE = enhanced_theme.get_color("warning_surface")
    
    # Additional legacy colors (from original theme)
    COLOR_PURPLE = "#8B5CF6"
    COLOR_DANGER_BORDER_LIGHT = "#F5C6CB"
    COLOR_INFO_BORDER_LIGHT = "#BEE5EB"
    COLOR_SUCCESS_BORDER_LIGHT = "#C3E6CB"
    COLOR_WARNING_BORDER_LIGHT = "#FFEEBA"
    COLOR_SUCCESS_LIGHT = enhanced_theme.get_color("success_surface")
    COLOR_ERROR_LIGHT = enhanced_theme.get_color("danger_surface")
    COLOR_ERROR_HOVER = enhanced_theme.get_color("danger_hover")
    COLOR_BG_SECONDARY = "#F8F9FA"
    
    # Dark Mode Colors - now dynamically fetched
    COLOR_BACKGROUND_DARK = enhanced_theme.get_color("background", "dark")
    COLOR_SURFACE_DARK = enhanced_theme.get_color("surface", "dark")
    COLOR_CARD_DARK = enhanced_theme.get_color("card", "dark")
    COLOR_BORDER_DARK = enhanced_theme.get_color("border", "dark")
    COLOR_PRIMARY_DARK = enhanced_theme.get_color("primary", "dark")
    COLOR_PRIMARY_HOVER_DARK = enhanced_theme.get_color("primary_hover", "dark")
    COLOR_TEXT_PRIMARY_DARK = enhanced_theme.get_color("text_primary", "dark")
    COLOR_TEXT_SECONDARY_DARK = enhanced_theme.get_color("text_secondary", "dark")
    
    # Dark Mode Icon Colors
    COLOR_ICON_DARK = enhanced_theme.get_color("icon", "dark")
    COLOR_ICON_LIGHT_DARK = enhanced_theme.get_color("icon_light", "dark")
    COLOR_ICON_ACCENT_DARK = enhanced_theme.get_color("icon_accent", "dark")
    COLOR_ICON_DANGER_DARK = enhanced_theme.get_color("icon_danger", "dark")
    COLOR_ICON_SUCCESS_DARK = enhanced_theme.get_color("icon_success", "dark")
    COLOR_ICON_WARNING_DARK = enhanced_theme.get_color("icon_warning", "dark")
    
    # Menu and Navigation dark mode
    COLOR_MENU_ICON_DARK = enhanced_theme.get_color("menu_icon", "dark")
    COLOR_MENU_HOVER_DARK = enhanced_theme.get_color("menu_hover", "dark")
    COLOR_HEADER_ICON_DARK = enhanced_theme.get_color("header_icon", "dark")
    COLOR_CONTROL_HOVER_DARK = enhanced_theme.get_color("control_hover", "dark")
    
    # Dark Mode Surfaces
    COLOR_DANGER_SURFACE_DARK = enhanced_theme.get_color("danger_surface", "dark")
    COLOR_INFO_SURFACE_DARK = enhanced_theme.get_color("info_surface", "dark")
    COLOR_SUCCESS_SURFACE_DARK = enhanced_theme.get_color("success_surface", "dark")
    COLOR_WARNING_SURFACE_DARK = enhanced_theme.get_color("warning_surface", "dark")
    
    # Secondary, Success, Danger for dark mode
    COLOR_SECONDARY_DARK = enhanced_theme.get_color("secondary", "dark")
    COLOR_SECONDARY_HOVER_DARK = enhanced_theme.get_color("secondary_hover", "dark")
    COLOR_SUCCESS_DARK = enhanced_theme.get_color("success", "dark")
    COLOR_SUCCESS_HOVER_DARK = enhanced_theme.get_color("success_hover", "dark")
    COLOR_DANGER_DARK = enhanced_theme.get_color("danger", "dark")
    COLOR_DANGER_HOVER_DARK = enhanced_theme.get_color("danger_hover", "dark")
    
    # Surface hover colors
    COLOR_SURFACE_HOVER_LIGHT = "#F0F0F0"
    COLOR_SURFACE_HOVER_DARK = "#252525"
    
    # Profile button colors
    COLOR_PROFILE_BUTTON_LIGHT = "#7B42F6"
    COLOR_PROFILE_BUTTON_HOVER_LIGHT = "#6A35D9"
    COLOR_PROFILE_BUTTON_DARK = "#8A5BF7"
    COLOR_PROFILE_BUTTON_HOVER_DARK = "#7B42F6"
    
    # Icon button colors
    COLOR_ICON_BUTTON_FG = ("gray85", "gray28")
    COLOR_ICON_BUTTON_HOVER = ("gray75", "gray38")
    
    # Enhanced Card Design
    COLOR_CARD_ELEVATED = enhanced_theme.get_color("card")
    COLOR_CARD_SHADOW = "#00000015"
    COLOR_CARD_BORDER_HOVER = "#007BFF33"
    
    # Modern Gradient Colors
    GRADIENT_PRIMARY_START = "#007BFF"
    GRADIENT_PRIMARY_END = "#0056B3"
    GRADIENT_SECONDARY_START = "#6C757D"
    GRADIENT_SECONDARY_END = "#495057"
    
    # Enhanced Status Colors
    COLOR_STATUS_ONLINE = enhanced_theme.get_color("success")
    COLOR_STATUS_OFFLINE = enhanced_theme.get_color("danger")
    COLOR_STATUS_PENDING = enhanced_theme.get_color("warning")
    COLOR_STATUS_PROCESSING = enhanced_theme.get_color("info")
    
    # Modern UI Elements
    COLOR_TOOLTIP_BG = "#343A40"
    COLOR_TOOLTIP_TEXT = "#FFFFFF"
    COLOR_OVERLAY = "#00000080"
    