"""
Enhanced UI Theme for the Checker-App with Professional Design
-------------------------------------------------------------
Modern, professional color scheme with improved visual hierarchy,
elegant typography, and sophisticated visual elements.
"""
import customtkinter as ctk
import threading
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any, Protocol, Callable, List, Union
from abc import ABC, abstractmethod

# =============================================================================
# PROFESSIONAL COLOR PALETTE
# =============================================================================

@dataclass(frozen=True)
class ProfessionalColors:
    """Professional color palette for modern business applications."""

    # Primary Brand Colors - More vibrant
    PRIMARY_BLUE = "#64748B"           # Neutrales Slate-Grau statt Microsoft Blue
    PRIMARY_BLUE_HOVER = "#106EBE"     # Darker blue for hover
    PRIMARY_BLUE_LIGHT = "#E1F5FE"     # Light blue for backgrounds

    # Secondary Colors - More vibrant
    SECONDARY_TEAL = "#20B2AA"         # Light Sea Green (more vibrant)
    SECONDARY_TEAL_HOVER = "#008B8B"   # Dark Cyan
    SECONDARY_TEAL_LIGHT = "#E0F2F1"   # Light teal

    # Accent Colors - More vibrant
    ACCENT_ORANGE = "#FF7043"          # Deep Orange (more vibrant)
    ACCENT_ORANGE_HOVER = "#F4511E"    # Darker orange
    ACCENT_ORANGE_LIGHT = "#FFF3E0"    # Light orange

    # Additional vibrant colors
    VIBRANT_PURPLE = "#9C27B0"         # Material Purple
    VIBRANT_PURPLE_HOVER = "#7B1FA2"   # Darker purple
    VIBRANT_PURPLE_LIGHT = "#F3E5F5"   # Light purple

    VIBRANT_PINK = "#E91E63"           # Material Pink
    VIBRANT_PINK_HOVER = "#C2185B"     # Darker pink
    VIBRANT_PINK_LIGHT = "#FCE4EC"     # Light pink

    VIBRANT_INDIGO = "#3F51B5"         # Material Indigo
    VIBRANT_INDIGO_HOVER = "#303F9F"   # Darker indigo
    VIBRANT_INDIGO_LIGHT = "#E8EAF6"   # Light indigo

    VIBRANT_CYAN = "#00BCD4"           # Material Cyan
    VIBRANT_CYAN_HOVER = "#00ACC1"     # Darker cyan
    VIBRANT_CYAN_LIGHT = "#E0F4F3"     # Light cyan

    # Neutral Colors
    NEUTRAL_WHITE = "#FFFFFF"          # Pure white
    NEUTRAL_GRAY_50 = "#FAFBFC"        # Very light gray
    NEUTRAL_GRAY_100 = "#F4F6F8"       # Light gray
    NEUTRAL_GRAY_200 = "#E1E7EB"       # Light gray border
    NEUTRAL_GRAY_300 = "#CBD5E0"       # Medium gray
    NEUTRAL_GRAY_400 = "#9CA3AF"       # Gray text
    NEUTRAL_GRAY_500 = "#6B7280"       # Dark gray text
    NEUTRAL_GRAY_600 = "#4B5563"       # Darker gray
    NEUTRAL_GRAY_700 = "#374151"       # Very dark gray
    NEUTRAL_GRAY_800 = "#1F2937"       # Almost black
    NEUTRAL_GRAY_900 = "#111827"       # Dark text

    # Semantic Colors - More vibrant
    SUCCESS_GREEN = "#4CAF50"          # Material Green (more vibrant)
    SUCCESS_GREEN_HOVER = "#388E3C"    # Darker green
    SUCCESS_GREEN_LIGHT = "#E8F5E8"    # Light green

    WARNING_YELLOW = "#FFC107"         # Material Amber (more vibrant)
    WARNING_YELLOW_HOVER = "#FFA000"   # Darker yellow
    WARNING_YELLOW_LIGHT = "#FFF8E1"   # Light yellow

    ERROR_RED = "#F44336"              # Material Red (more vibrant)
    ERROR_RED_HOVER = "#D32F2F"        # Darker red
    ERROR_RED_LIGHT = "#FFEBEE"        # Light red

    INFO_BLUE = "#2196F3"              # Material Blue (more vibrant)
    INFO_BLUE_HOVER = "#1976D2"        # Darker info blue
    INFO_BLUE_LIGHT = "#E3F2FD"        # Light info blue

@dataclass(frozen=True)
class ProfessionalGradients:
    """Professional gradient definitions for modern UI elements."""

    # Primary Gradients - More vibrant
    PRIMARY_GRADIENT = "linear-gradient(135deg, #64748B 0%, #475569 100%)"  # Neutraler Gradient
    SECONDARY_GRADIENT = "linear-gradient(135deg, #20B2AA 0%, #008B8B 100%)"
    ACCENT_GRADIENT = "linear-gradient(135deg, #FF7043 0%, #F4511E 100%)"

    # New vibrant gradients
    PURPLE_GRADIENT = "linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)"
    PINK_GRADIENT = "linear-gradient(135deg, #E91E63 0%, #C2185B 100%)"
    INDIGO_GRADIENT = "linear-gradient(135deg, #3F51B5 0%, #303F9F 100%)"
    CYAN_GRADIENT = "linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%)"

    # Subtle Background Gradients
    CARD_GRADIENT = "linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%)"
    HEADER_GRADIENT = "linear-gradient(180deg, #FAFBFC 0%, #F4F6F8 100%)"

    # Success/Error Gradients - More vibrant
    SUCCESS_GRADIENT = "linear-gradient(135deg, #4CAF50 0%, #388E3C 100%)"
    ERROR_GRADIENT = "linear-gradient(135deg, #F44336 0%, #D32F2F 100%)"
    WARNING_GRADIENT = "linear-gradient(135deg, #FFC107 0%, #FFA000 100%)"
    INFO_GRADIENT = "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)"

    # Special effect gradients
    RAINBOW_GRADIENT = "linear-gradient(45deg, #FF6B35, #F7931E, #FFD700, #32CD32, #00CED1, #4169E1, #9370DB)"
    SUNSET_GRADIENT = "linear-gradient(135deg, #FF6B35 0%, #F7931E 35%, #FFD700 100%)"
    OCEAN_GRADIENT = "linear-gradient(135deg, #00BCD4 0%, #2196F3 50%, #3F51B5 100%)"

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
        'add_button': 'HinzufÃ¼gen',
        'delete_button': 'LÃ¶schen',
        'edit_button': 'Bearbeiten',
        'save_button': 'Speichern',
        'cancel_button': 'Abbrechen',
        'close_button': 'SchlieÃŸen',
        'menu_button': 'MenÃ¼ Ã¶ffnen',
        'file_upload': 'Datei hochladen',
        'drag_drop_area': 'Dateien hierher ziehen oder klicken zum AuswÃ¤hlen',
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

    # Current theme instance and thread lock
    _instance: Optional['EnhancedUITheme'] = None
    _lock = threading.Lock()

    def __new__(cls):
        # Double-checked locking pattern for thread safety
        if cls._instance is None:
            with cls._lock:
                # Check again in case another thread created the instance
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Thread-safe initialization with double-checked locking
        if not hasattr(self, '_initialized'):
            with self._lock:
                # Check again in case another thread initialized it
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    self._current_theme: str = "light"  # Initialize as instance variable
                    self._themes: Dict[str, ColorScheme] = {}
                    self._workflow_schemes: Dict[str, Dict[str, WorkflowColorScheme]] = {}
                    self._accessibility = AccessibilityConfig()
                    self._observers: List[Callable[[], None]] = []
                    self._strict_mode: bool = False  # Set to True to raise exceptions on typos

                    # Initialize default themes
                    self._init_default_themes()
                    self._init_workflow_schemes()

                    # Set initial theme based on current appearance mode
                    try:
                        current_mode = ctk.get_appearance_mode().lower()
                        if current_mode in self._themes:
                            self._current_theme = current_mode
                        else:
                            self._current_theme = "light"  # Fallback to light theme
                    except Exception:
                        self._current_theme = "light"  # Safe fallback

    def _init_default_themes(self) -> None:
        """Initialize the default light and dark themes."""

        # Light Theme - More vibrant colors
        light_theme = ColorScheme(
            # Core Colors
            background="#FAFBFC",
            surface="#FFFFFF",
            card="#FFFFFF",
            border="#E1E5E9",

            # Primary Colors - More vibrant
            primary="#64748B",         # Microsoft Blue
            primary_hover="#106EBE",   # Darker blue
            primary_container="#E1F5FE",
            primary_surface="#F0F8FF",

            # Text Colors
            text_primary="#1A1A1A",
            text_secondary="#5A6C7D",
            text_on_primary="#FFFFFF",
            text_on_dark="#FFFFFF",

            # Semantic Colors - More vibrant
            success="#4CAF50",         # Material Green
            success_hover="#388E3C",   # Darker green
            danger="#F44336",          # Material Red
            danger_hover="#D32F2F",    # Darker red
            warning="#FFC107",         # Material Amber
            info="#2196F3",            # Material Blue
            info_hover="#1976D2",      # Darker info blue

            # Interactive Colors - More vibrant
            secondary="#20B2AA",       # Light Sea Green
            secondary_hover="#008B8B", # Dark Cyan
            accent="#FF7043",          # Deep Orange
            accent_hover="#F4511E",    # Darker orange

            # Icon Colors - More vibrant
            icon="#6C757D",
            icon_light="#8E9BAE",
            icon_accent="#64748B",     # Microsoft Blue
            icon_danger="#F44336",     # Material Red
            icon_success="#4CAF50",    # Material Green
            icon_warning="#FFC107",    # Material Amber

            # Menu Colors
            menu_icon="#495057",
            menu_hover="#F8F9FA",

            # Control Colors
            header_icon="#6C757D",
            control_hover="#F1F3F4",

            # Surface Colors - More vibrant
            danger_surface="#FFEBEE",  # Light red
            info_surface="#E3F2FD",   # Light blue
            success_surface="#E8F5E8", # Light green
            warning_surface="#FFF8E1"  # Light amber
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

    def _init_workflow_schemes(self) -> None:
        """Initialize workflow-specific color schemes."""

        # Light mode workflow schemes - More vibrant colors
        light_workflows = {
            'angebots_workflow': WorkflowColorScheme(
                primary='#64748B',        # Microsoft Blue
                hover='#106EBE',          # Darker blue
                light='#E1F5FE',          # Light blue
                icon_bg='#64748B',        # Microsoft Blue
                shadow='#E3F2FD',         # Light blue shadow
                glow='#64B5F6'            # Light blue glow
            ),
            'pruefung_workflow': WorkflowColorScheme(
                primary='#4CAF50',        # Material Green
                hover='#388E3C',          # Darker green
                light='#E8F5E8',          # Light green
                icon_bg='#4CAF50',        # Material Green
                shadow='#E8F5E8',         # Light green shadow
                glow='#81C784'            # Light green glow
            ),
            'finalisierung_workflow': WorkflowColorScheme(
                primary='#FFC107',        # Material Amber
                hover='#FFA000',          # Darker amber
                light='#FFF8E1',          # Light amber
                icon_bg='#FFC107',        # Material Amber
                shadow='#FFF8E1',         # Light amber shadow
                glow='#FFD54F'            # Light amber glow
            ),
            'projekt_workflow': WorkflowColorScheme(
                primary='#9C27B0',        # Material Purple
                hover='#7B1FA2',          # Darker purple
                light='#F3E5F5',          # Light purple
                icon_bg='#9C27B0',        # Material Purple
                shadow='#F3E5F5',         # Light purple shadow
                glow='#BA68C8'            # Light purple glow
            )
        }

        # Dark mode workflow schemes - More vibrant colors
        dark_workflows = {
            'angebots_workflow': WorkflowColorScheme(
                primary='#64B5F6',        # Light Blue
                hover='#42A5F5',          # Darker light blue
                light='#1A2F4A',          # Dark blue background
                icon_bg='#64B5F6',        # Light Blue
                shadow='#0F1A2E',         # Dark blue shadow
                glow='#90CAF9'            # Lighter blue glow
            ),
            'pruefung_workflow': WorkflowColorScheme(
                primary='#81C784',        # Light Green
                hover='#66BB6A',          # Darker light green
                light='#1A3D1A',          # Dark green background
                icon_bg='#81C784',        # Light Green
                shadow='#0F2A0F',         # Dark green shadow
                glow='#A5D6A7'            # Lighter green glow
            ),
            'finalisierung_workflow': WorkflowColorScheme(
                primary='#FFD54F',        # Light Amber
                hover='#FFCA28',          # Darker light amber
                light='#3D3D1A',          # Dark amber background
                icon_bg='#FFD54F',        # Light Amber
                shadow='#2A2A0F',         # Dark amber shadow
                glow='#FFE082'            # Lighter amber glow
            ),
            'projekt_workflow': WorkflowColorScheme(
                primary='#BA68C8',        # Light Purple
                hover='#AB47BC',          # Darker light purple
                light='#3D1A3D',          # Dark purple background
                icon_bg='#BA68C8',        # Light Purple
                shadow='#2A0F2A',         # Dark purple shadow
                glow='#CE93D8'            # Lighter purple glow
            )
        }

        self._workflow_schemes["light"] = light_workflows
        self._workflow_schemes["dark"] = dark_workflows

    # Theme Provider Protocol Implementation
    def get_color(self, color_name: str, mode: Optional[str] = None) -> str:
        """Get a color by name, optionally specifying light/dark mode."""
        # Validate theme system before proceeding
        self._validate_theme_system()

        if mode is None:
            # Use the current theme set by switch_theme(), not ctk.get_appearance_mode()
            # Validate that _current_theme exists in our themes dict
            if self._current_theme in self._themes:
                mode = self._current_theme
            else:
                # Extract base mode (light/dark) from current theme or fallback to light
                mode = "dark" if "dark" in self._current_theme.lower() else "light"
                # Ensure the extracted mode exists, fallback to light if not
                if mode not in self._themes:
                    mode = "light"

        theme = self._themes.get(mode, self._themes.get("light"))
        if theme is None:
            # Ultimate fallback if even "light" theme doesn't exist
            raise RuntimeError("No valid theme found. Theme system not properly initialized.")

        # Check if the color exists in the theme - don't hide typos!
        if hasattr(theme, color_name):
            return getattr(theme, color_name)
        else:
            # Get available colors for better error reporting
            available_colors = [attr for attr in dir(theme) if not attr.startswith('_') and isinstance(getattr(theme, attr), str)]

            # Find similar colors using simple string similarity
            suggestions = self._find_similar_colors(color_name, available_colors)

            # Create detailed error message
            error_msg = f"Color '{color_name}' not found in theme '{mode}'."
            if suggestions:
                suggestions_text = ", ".join([f"'{s}'" for s in suggestions[:3]])
                error_msg += f" Did you mean: {suggestions_text}?"
            error_msg += f" Available colors: {available_colors}"

            print(f"WARNING: {error_msg}")

            # Check if strict mode is enabled
            if getattr(self, '_strict_mode', False):
                raise ValueError(error_msg)

            # For production, return primary color with clear warning
            return theme.primary

    def _find_similar_colors(self, typo: str, available_colors: List[str]) -> List[str]:
        """Find colors similar to the given typo using Levenshtein distance."""
        def levenshtein_distance(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)

            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        # Find colors with low edit distance
        suggestions = []
        for color in available_colors:
            distance = levenshtein_distance(typo.lower(), color.lower())
            # Only suggest if edit distance is reasonable (<=3 for longer names, <=2 for shorter)
            max_distance = min(3, max(2, len(typo) // 3))
            if distance <= max_distance:
                suggestions.append((color, distance))

        # Sort by distance and return color names only
        return [color for color, _ in sorted(suggestions, key=lambda x: x[1])]

    def get_color_tuple(self, color_name: str) -> Tuple[str, str]:
        """Get a (light, dark) color tuple."""
        light_color = self.get_color(color_name, "light")
        dark_color = self.get_color(color_name, "dark")
        return (light_color, dark_color)

    def get_workflow_colors(self, workflow_id: str) -> Dict[str, str]:
        """Get color scheme for a specific workflow."""
        # Validate theme system before proceeding
        self._validate_theme_system()

        # Use the current theme set by switch_theme(), not ctk.get_appearance_mode()
        # Validate that _current_theme exists and extract base mode safely
        if self._current_theme in self._workflow_schemes:
            base_mode = self._current_theme
        else:
            # Extract base mode (light/dark) from current theme or fallback to light
            base_mode = "dark" if "dark" in self._current_theme.lower() else "light"
            # Ensure the extracted mode exists in workflow schemes
            if base_mode not in self._workflow_schemes:
                base_mode = "light"

        workflow_schemes = self._workflow_schemes.get(base_mode, self._workflow_schemes.get("light", {}))
        scheme = workflow_schemes.get(workflow_id, workflow_schemes.get("angebots_workflow"))

        if scheme is None:
            # Ultimate fallback - create a minimal scheme
            from dataclasses import asdict
            scheme = WorkflowColorScheme(
                primary="#0066CC", hover="#0052A3", light="#F0F8FF",
                icon_bg="#0066CC", shadow="#E3F2FD", glow="#B3D9FF"
            )

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

    def update_accessibility_config(self, **kwargs: Any) -> None:
        """Update accessibility configuration."""
        # Create new config with updates
        current_dict = self._accessibility.__dict__.copy()
        current_dict.update(kwargs)
        self._accessibility = AccessibilityConfig(**current_dict)
        self._notify_observers()

    # Theme Management
    def register_theme(self, name: str, light_scheme: ColorScheme, dark_scheme: ColorScheme) -> None:
        """
        Register a custom theme with both light and dark variants.

        Args:
            name: Base theme name (e.g., "custom")
            light_scheme: Light mode color scheme
            dark_scheme: Dark mode color scheme
        """
        # Store themes with consistent naming
        self._themes[f"{name}_light"] = light_scheme
        self._themes[f"{name}_dark"] = dark_scheme

        # Also register the base name for direct access if it doesn't conflict
        if name not in self._themes:
            # Default to light variant for base name
            self._themes[name] = light_scheme

    # Observer Pattern for Hot-Swapping (Thread-safe)
    def add_observer(self, observer_callback: Callable[[], None]) -> None:
        """Add observer for theme changes. Thread-safe."""
        with self._lock:
            self._observers.append(observer_callback)

    def remove_observer(self, observer_callback: Callable[[], None]) -> None:
        """Remove observer. Thread-safe."""
        with self._lock:
            if observer_callback in self._observers:
                self._observers.remove(observer_callback)

    def _notify_observers(self) -> None:
        """Notify all observers of theme changes. Should be called within lock."""
        # Make a copy of observers to avoid issues if list is modified during iteration
        observers_copy = self._observers.copy()
        for observer in observers_copy:
            try:
                observer()
            except Exception as e:
                print(f"Error notifying theme observer: {e}")

    def _validate_theme_system(self) -> bool:
        """Validate that the theme system is properly initialized."""
        if not self._themes:
            raise RuntimeError("No themes available. Theme system not properly initialized.")

        # Ensure we have at least a light theme
        if "light" not in self._themes:
            raise RuntimeError("Light theme is missing. Theme system not properly initialized.")

        # Ensure current theme is valid
        self._ensure_valid_current_theme()

        return True

    def _ensure_valid_current_theme(self) -> None:
        """Ensure current theme is valid, fallback if necessary."""
        if self._current_theme not in self._themes:
            # Try fallback to light theme
            if "light" in self._themes:
                self._current_theme = "light"
            elif self._themes:
                # Use any available theme as last resort
                self._current_theme = next(iter(self._themes.keys()))

    def switch_theme(self, theme_name: str) -> None:
        """
        Switch to a different theme (hot-swapping). Thread-safe.

        Args:
            theme_name: Theme name to switch to. Can be:
                       - Direct theme key (e.g., "light", "dark", "custom_light")
                       - Base theme name (e.g., "custom") - will use current mode preference
        """
        with self._lock:
            # Try direct theme key first (most efficient)
            if theme_name in self._themes:
                self._current_theme = theme_name
                self._notify_observers()
                return

            # Handle base theme names by determining current mode preference
            current_is_dark = "dark" in self._current_theme.lower()

            # Try mode-specific variants
            preferred_variant = f"{theme_name}_{'dark' if current_is_dark else 'light'}"
            fallback_variant = f"{theme_name}_{'light' if current_is_dark else 'dark'}"

            if preferred_variant in self._themes:
                self._current_theme = preferred_variant
                self._notify_observers()
            elif fallback_variant in self._themes:
                # Use the other variant if preferred doesn't exist
                self._current_theme = fallback_variant
                self._notify_observers()
            else:
                # Theme not found
                available_themes = list(self.get_available_themes().keys())
                print(f"Warning: Theme '{theme_name}' not found. Available themes: {available_themes}")

                # Ensure current theme remains valid
                self._ensure_valid_current_theme()

    def get_available_themes(self) -> Dict[str, List[str]]:
        """
        Get available themes organized by base names.

        Returns:
            Dict with base theme names as keys and their variants as values.
            Example: {"default": ["light", "dark"], "custom": ["custom_light", "custom_dark"]}
        """
        themes_by_base = {}

        for theme_key in self._themes.keys():
            if theme_key.endswith('_light') or theme_key.endswith('_dark'):
                base_name = theme_key.rsplit('_', 1)[0]
                if base_name not in themes_by_base:
                    themes_by_base[base_name] = []
                themes_by_base[base_name].append(theme_key)
            else:
                # Standalone theme (like "light", "dark")
                if theme_key not in themes_by_base:
                    themes_by_base[theme_key] = []
                themes_by_base[theme_key].append(theme_key)

        return themes_by_base

    def switch_to_light_mode(self) -> None:
        """Switch current theme to its light variant."""
        current_base = self._get_current_theme_base()
        light_variant = f"{current_base}_light" if current_base != "light" else "light"

        if light_variant in self._themes:
            self.switch_theme(light_variant)
        elif "light" in self._themes:
            self.switch_theme("light")

    def switch_to_dark_mode(self) -> None:
        """ðŸš¨ CRITICAL: Dark Mode DEAKTIVIERT - fehleranfÃ¤llig!"""
        # âŒ NIEMALS Dark Mode verwenden - fehleranfÃ¤llig!
        print("âŒ FEHLER: Dark Mode ist deaktiviert! Zwinge Light Mode.")
        self.switch_theme("light")  # Immer Light Mode

    def _get_current_theme_base(self) -> str:
        """Get the base name of the current theme."""
        if self._current_theme.endswith('_light') or self._current_theme.endswith('_dark'):
            return self._current_theme.rsplit('_', 1)[0]
        return self._current_theme

    def get_current_theme_info(self) -> Dict[str, str]:
        """
        Get information about the current theme.

        Returns:
            Dict with current theme key, base name, and mode.
        """
        base_name = self._get_current_theme_base()
        mode = "light"
        if self._current_theme.endswith('_dark') or self._current_theme == "dark":
            mode = "dark"

        return {
            "current_key": self._current_theme,
            "base_name": base_name,
            "mode": mode
        }

    def set_strict_mode(self, enabled: bool) -> None:
        """
        Enable or disable strict mode for color validation.

        In strict mode, invalid color names will raise exceptions instead of
        falling back to primary color with warnings.

        Args:
            enabled: True to enable strict mode, False to disable
        """
        self._strict_mode = enabled

    def is_strict_mode(self) -> bool:
        """Check if strict mode is enabled."""
        return getattr(self, '_strict_mode', False)

# =============================================================================
# PROFESSIONAL UI CONSTANTS
# =============================================================================

# Modern Color Scheme using Professional Colors
COLOR_BACKGROUND = ProfessionalColors.NEUTRAL_GRAY_50
COLOR_SURFACE = ProfessionalColors.NEUTRAL_WHITE
COLOR_CARD = ProfessionalColors.NEUTRAL_WHITE
COLOR_CARD_ELEVATED = ProfessionalColors.NEUTRAL_WHITE
COLOR_CARD_HOVER = ProfessionalColors.NEUTRAL_GRAY_50

# Primary Colors
COLOR_PRIMARY = ProfessionalColors.PRIMARY_BLUE
COLOR_PRIMARY_HOVER = ProfessionalColors.PRIMARY_BLUE_HOVER
COLOR_PRIMARY_LIGHT = ProfessionalColors.PRIMARY_BLUE_LIGHT
COLOR_PRIMARY_CONTAINER = ProfessionalColors.PRIMARY_BLUE_LIGHT

# Text Colors
COLOR_TEXT_PRIMARY = ProfessionalColors.NEUTRAL_GRAY_900
COLOR_TEXT_SECONDARY = ProfessionalColors.NEUTRAL_GRAY_600
COLOR_TEXT_MUTED = ProfessionalColors.NEUTRAL_GRAY_400
COLOR_TEXT_ON_PRIMARY = ProfessionalColors.NEUTRAL_WHITE
COLOR_TEXT_ON_DARK = ProfessionalColors.NEUTRAL_WHITE

# Border Colors
COLOR_BORDER = ProfessionalColors.NEUTRAL_GRAY_200
COLOR_BORDER_HOVER = ProfessionalColors.NEUTRAL_GRAY_300
COLOR_BORDER_FOCUS = ProfessionalColors.PRIMARY_BLUE

# Semantic Colors
COLOR_SUCCESS = ProfessionalColors.SUCCESS_GREEN
COLOR_SUCCESS_HOVER = ProfessionalColors.SUCCESS_GREEN_HOVER
COLOR_SUCCESS_LIGHT = ProfessionalColors.SUCCESS_GREEN_LIGHT

COLOR_WARNING = ProfessionalColors.WARNING_YELLOW
COLOR_WARNING_HOVER = ProfessionalColors.WARNING_YELLOW_HOVER
COLOR_WARNING_LIGHT = ProfessionalColors.WARNING_YELLOW_LIGHT

COLOR_DANGER = ProfessionalColors.ERROR_RED
COLOR_DANGER_HOVER = ProfessionalColors.ERROR_RED_HOVER
COLOR_DANGER_LIGHT = ProfessionalColors.ERROR_RED_LIGHT

COLOR_INFO = ProfessionalColors.INFO_BLUE
COLOR_INFO_HOVER = ProfessionalColors.INFO_BLUE_HOVER
COLOR_INFO_LIGHT = ProfessionalColors.INFO_BLUE_LIGHT

# Container Colors for different sections
COLOR_CONTAINER_CUSTOMER = ProfessionalColors.PRIMARY_BLUE_LIGHT
COLOR_CONTAINER_UPLOAD = ProfessionalColors.SECONDARY_TEAL_LIGHT
COLOR_CONTAINER_WORKFLOW = ProfessionalColors.ACCENT_ORANGE_LIGHT

# Professional Shadows
SHADOW_LIGHT = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
SHADOW_MEDIUM = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LARGE = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_HOVER = "0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -5px rgba(0, 0, 0, 0.04)"

# Modern Typography
FONT_FAMILY_PRIMARY = "Segoe UI"
FONT_FAMILY_SECONDARY = "Inter"
FONT_FAMILY_MONOSPACE = "Consolas"

# Professional Font Sizes
FONT_SIZE_HERO = 32
FONT_SIZE_H1 = 24
FONT_SIZE_H2 = 20
FONT_SIZE_H3 = 18
FONT_SIZE_H4 = 16
FONT_SIZE_BODY = 14
FONT_SIZE_CAPTION = 12
FONT_SIZE_SMALL = 11

# Professional Spacing System (8px grid)
SPACING_XS = 4
SPACING_S = 8
SPACING_M = 16
SPACING_L = 24
SPACING_XL = 32
SPACING_XXL = 48

# Professional Corner Radius
CORNER_RADIUS_SMALL = 4
CORNER_RADIUS = 8
CORNER_RADIUS_LARGE = 12
CORNER_RADIUS_XL = 16

# Professional Component Heights
INPUT_HEIGHT = 48
BUTTON_HEIGHT_SMALL = 32
BUTTON_HEIGHT_MEDIUM = 40
BUTTON_HEIGHT_LARGE = 48

# Professional Card Heights
CARD_HEIGHT_COMPACT = 96
CARD_HEIGHT_SMALL = 128
CARD_HEIGHT_MEDIUM = 240
CARD_HEIGHT_LARGE = 320

# Professional Container Heights
SECTION_CONTAINER_HEIGHT = 640  # Increased for better content display

# =============================================================================
# ACCESSIBILITY HELPERS
# =============================================================================

class AccessibilityHelper:
    """Helper class for accessibility improvements."""

    @staticmethod
    def add_keyboard_navigation(
        widget: Any,
        on_enter_callback: Optional[Callable[[], None]] = None,
        on_space_callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Add keyboard navigation to a widget."""
        def on_key_press(event: Any) -> None:
            if event.keysym == "Return" and on_enter_callback:
                on_enter_callback()
            elif event.keysym == "space" and on_space_callback:
                on_space_callback()

        widget.bind("<KeyPress>", on_key_press)
        widget.focus_set()

    @staticmethod
    def add_focus_indicator(widget: Any, theme_provider: ThemeProvider) -> None:
        """Add visual focus indicator to widget."""
        accessibility_config = theme_provider.get_accessibility_config()

        def on_focus_in(event: Any) -> None:
            widget.configure(
                border_width=accessibility_config.focus_indicator_width,
                border_color=accessibility_config.focus_indicator_color
            )

        def on_focus_out(event: Any) -> None:
            widget.configure(border_width=0)

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)

    @staticmethod
    def set_aria_label(widget: Any, label_key: str, theme_provider: ThemeProvider) -> None:
        """Set accessible label for screen readers."""
        accessibility_config = theme_provider.get_accessibility_config()
        aria_label = accessibility_config.default_aria_labels.get(label_key, label_key)

        # Try to set accessible name/description if the widget supports it
        try:
            if hasattr(widget, 'configure'):
                # For widgets that support accessible names
                widget.configure(name=aria_label)
        except Exception:
            pass

        # Set tooltip as fallback for screen readers
        try:
            # Try to import CTkToolTip if available
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

# =============================================================================
# DYNAMIC THEME METACLASS AND LEGACY COMPATIBILITY
# =============================================================================

class DynamicThemeMeta(type):
    """Metaclass that provides dynamic theme-aware properties."""

    def __getattribute__(cls, name):
        # Define mappings directly to avoid recursion
        color_mappings = {
            'COLOR_PRIMARY': 'primary',
            'COLOR_PRIMARY_HOVER': 'primary_hover',
            'COLOR_SECONDARY': 'secondary',
            'COLOR_SECONDARY_HOVER': 'secondary_hover',
            'COLOR_BORDER': 'border',
            'COLOR_SURFACE': 'surface',
            'COLOR_CARD': 'card',
            'COLOR_BACKGROUND': 'background',
            'COLOR_TEXT_PRIMARY': 'text_primary',
            'COLOR_TEXT_SECONDARY': 'text_secondary',
            'COLOR_TEXT_ON_PRIMARY': 'text_on_primary',
            'COLOR_TEXT_ON_DARK': 'text_on_dark',
            'COLOR_SUCCESS': 'success',
            'COLOR_DANGER': 'danger',
            'COLOR_WARNING': 'warning',
            'COLOR_INFO': 'info',
            'COLOR_ICON': 'icon',
            'COLOR_ACCENT': 'accent',
            'COLOR_ACCENT_HOVER': 'accent_hover',
            'COLOR_CONTAINER_CUSTOMER': 'primary_surface', # Legacy support
            'COLOR_CONTAINER_UPLOAD': 'surface', # Legacy support
            'COLOR_CONTAINER_UPLOAD_LIGHT': 'background', # Legacy support
            'COLOR_SURFACE_HOVER_LIGHT': 'control_hover', # Legacy support
            'COLOR_CONTAINER_WORKFLOW': 'warning', # Legacy support for workflow section
            # Button color constants
            'COLOR_BUTTON_PRIMARY': 'primary',
            'COLOR_BUTTON_SECONDARY': 'secondary',
            'COLOR_BUTTON_SECONDARY_HOVER': 'secondary_hover',
            'COLOR_BUTTON_SUCCESS': 'success',
            'COLOR_BUTTON_INFO': 'info',
            'COLOR_BUTTON_TEXT': 'text_on_primary',
        }

        tuple_mappings = {
            'TUPLE_BG': 'background',
            'TUPLE_BG_SECONDARY': 'surface',
            'TUPLE_TEXT_PRIMARY': 'text_primary',
            'TUPLE_TEXT_SECONDARY': 'text_secondary',
            'TUPLE_CARD': 'card',
            'TUPLE_PRIMARY': 'primary',
            'TUPLE_PRIMARY_HOVER': 'primary_hover',
            'TUPLE_BORDER': 'border',
            'TUPLE_INPUT_BG': 'surface',
            'TUPLE_TEXT_ON_PRIMARY': 'text_on_primary',
            'TUPLE_SUCCESS': 'success',  # Legacy support
            'TUPLE_WARNING': 'warning',  # Legacy support
            'TUPLE_DANGER': 'danger',    # Legacy support
            'TUPLE_SURFACE': 'surface',  # Legacy support
        }

        # Handle color properties dynamically
        if name in color_mappings:
            theme_provider = super().__getattribute__('_theme_provider')
            return theme_provider.get_color(color_mappings[name])

        # Handle tuple properties dynamically
        if name in tuple_mappings:
            theme_provider = super().__getattribute__('_theme_provider')
            return theme_provider.get_color_tuple(tuple_mappings[name])

        # Handle style properties dynamically
        if name.startswith('CONTAINER_STYLE_'):
            return cls._get_container_style(name)

        if name == 'BUTTON_STYLE_PRIMARY':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": theme_provider.get_color("primary"),
                "hover_color": theme_provider.get_color("primary_hover"),
                "text_color": theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }

        if name == 'BUTTON_STYLE_SECONDARY':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": theme_provider.get_color("surface"),
                "hover_color": theme_provider.get_color("control_hover"),
                "border_width": 1,
                "border_color": theme_provider.get_color("border"),
                "text_color": theme_provider.get_color("text_secondary"),
                "corner_radius": 8
            }

        if name == 'BUTTON_STYLE_OUTLINE':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": "transparent",
                "hover_color": theme_provider.get_color("surface"),
                "border_width": 1,
                "border_color": theme_provider.get_color("border"),
                "text_color": theme_provider.get_color("text_primary"),
                "corner_radius": 8
            }

        if name == 'BUTTON_STYLE_SUCCESS':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": theme_provider.get_color("success"),
                "hover_color": theme_provider.get_color("success_hover"),
                "text_color": theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }

        if name == 'BUTTON_STYLE_DANGER':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": theme_provider.get_color("danger"),
                "hover_color": theme_provider.get_color("danger_hover"),
                "text_color": theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }

        if name == 'CHECKBOX_STYLE':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "checkmark_color": theme_provider.get_color("text_on_primary"),
                "fg_color": theme_provider.get_color("primary"),
                "border_color": theme_provider.get_color("primary_hover"),
                "hover_color": theme_provider.get_color("primary_hover"),
                "corner_radius": 4,
                "border_width": 1,
            }

        if name == 'OPTIONMENU_STYLE':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "fg_color": theme_provider.get_color("surface"),
                "button_color": theme_provider.get_color("primary"),
                "button_hover_color": theme_provider.get_color("primary_hover"),
                "text_color": theme_provider.get_color("text_primary"),
                "dropdown_fg_color": theme_provider.get_color("surface"),
                "dropdown_hover_color": theme_provider.get_color("control_hover"),
                "dropdown_text_color": theme_provider.get_color("text_primary"),
                "corner_radius": 8,
            }

        if name == 'TABVIEW_STYLE':
            theme_provider = super().__getattribute__('_theme_provider')
            return {
                "corner_radius": 8,
                "border_width": 1,
                "segmented_button_fg_color": theme_provider.get_color("surface"),
                "segmented_button_selected_color": theme_provider.get_color("primary"),
                "segmented_button_selected_hover_color": theme_provider.get_color("primary_hover"),
                "segmented_button_unselected_color": theme_provider.get_color("surface"),
                "segmented_button_unselected_hover_color": theme_provider.get_color("surface"),
                "text_color": theme_provider.get_color("text_primary"),
                "text_color_disabled": theme_provider.get_color("text_secondary")
            }

        # Fall back to normal attribute access
        return super().__getattribute__(name)

    def _get_container_style(cls, style_name: str) -> Dict[str, Any]:
        """Dynamically generate container styles for backward compatibility."""
        theme_provider = super().__getattribute__('_theme_provider')

        style_map = {
            'CONTAINER_STYLE_DEFAULT': {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": theme_provider.get_color("surface"),
                "border_color": theme_provider.get_color("border")
            },
            'CONTAINER_STYLE_CUSTOMER': {
                "corner_radius": 12,
                "border_width": 1,
                "fg_color": theme_provider.get_color("primary_surface"),
                "border_color": theme_provider.get_color("primary_container")
            },
            'CONTAINER_STYLE_WORKFLOW': {
                "corner_radius": 10,
                "border_width": 0,
                "fg_color": theme_provider.get_color("surface"),
            },
            'CONTAINER_STYLE_UPLOAD': {
                "corner_radius": 8,
                "border_width": 2,
                "border_color": theme_provider.get_color("border"),
                "fg_color": theme_provider.get_color("background"),
            }
        }

        # Default to a safe style if not found
        return style_map.get(style_name, style_map['CONTAINER_STYLE_DEFAULT'])


# Legacy compatibility - keep existing UITheme class
class UITheme(metaclass=DynamicThemeMeta):
    """
    Legacy UITheme class with enhanced theme system integration.

    âš ï¸  WICHTIGE HINWEISE ZUR THEME-NUTZUNG  âš ï¸

    1. STATISCHE VS. DYNAMISCHE EIGENSCHAFTEN:
       Die Eigenschaften dieser Klasse (COLOR_PRIMARY, TUPLE_BG, etc.) werden
       dynamisch ausgewertet und geben immer die aktuellen Theme-Farben zurÃ¼ck.

       Wenn diese Werte jedoch Variablen zugewiesen werden, werden sie STATISCH:

       # âŒ SCHLECHT - Wird nach Theme-Wechsel nicht aktualisiert:
       my_color = UITheme.COLOR_PRIMARY

       # âœ… GUT - Direkter Zugriff fÃ¼r dynamisches Verhalten:
       widget.configure(fg_color=UITheme.COLOR_PRIMARY)

    2. EMPFOHLENE MODERNE API:
       FÃ¼r garantierte Theme-Updates sollte neuer Code die moderne API verwenden:

       # âœ… BESSER - Moderne API fÃ¼r garantierte Theme-Updates:
       widget.configure(fg_color=enhanced_theme.get_color('primary'))

       # Farbtupel fÃ¼r Light/Dark-Mode:
       enhanced_theme.get_color_tuple('primary')  # -> (light_color, dark_color)

    3. LEGACY-KONSTANTEN:
       Die alten TUPLE_* und COLOR_* Konstanten werden aus KompatibilitÃ¤tsgrÃ¼nden
       weiterhin unterstÃ¼tzt, sind aber intern auf die neue Theme-API umgestellt.

       FÃ¼r neue Entwicklungen bitte immer die moderne API verwenden.
    """

    # Singleton theme provider
    _theme_provider = enhanced_theme

    @classmethod
    def legacy_to_modern_api(cls, legacy_code: str) -> str:
        """
        Konvertiert Legacy-Theme-Konstanten zu moderner API-Syntax.

        Diese Hilfsmethode erleichtert die Migration von altem Code zur neuen API.
        Sie erkennt UITheme.COLOR_* und UITheme.TUPLE_* Muster und ersetzt sie
        durch die entsprechenden enhanced_theme.get_color() Aufrufe.

        Args:
            legacy_code: String mit Legacy-Code, der UITheme.* Konstanten verwendet

        Returns:
            String mit konvertiertem Code, der enhanced_theme.* API verwendet

        Beispiel:
            >>> UITheme.legacy_to_modern_api("fg_color=UITheme.COLOR_PRIMARY")
            "fg_color=enhanced_theme.get_color('primary')"

            >>> UITheme.legacy_to_modern_api("color=UITheme.TUPLE_BG")
            "color=enhanced_theme.get_color_tuple('background')"
        """
        import re

        # COLOR_* zu get_color()
        color_pattern = r'UITheme\.COLOR_([A-Z_]+)'

        def color_replacer(match):
            color_name = match.group(1)
            # Lookup in color_mappings from DynamicThemeMeta
            meta = type(cls)
            color_mappings = {}
            try:
                # Get mappings dynamically from metaclass (fallback to empty dict)
                for attr in dir(meta):
                    if attr == 'color_mappings':
                        color_mappings = getattr(meta, attr)
                        break
            except:
                pass

            if f'COLOR_{color_name}' in color_mappings:
                return f"enhanced_theme.get_color('{color_mappings[f'COLOR_{color_name}']}')"
            else:
                # Fallback: convert to lowercase with underscores
                modern_name = color_name.lower()
                return f"enhanced_theme.get_color('{modern_name}')"

        # TUPLE_* zu get_color_tuple()
        tuple_pattern = r'UITheme\.TUPLE_([A-Z_]+)'

        def tuple_replacer(match):
            tuple_name = match.group(1)
            # Lookup in tuple_mappings from DynamicThemeMeta
            meta = type(cls)
            tuple_mappings = {}
            try:
                # Get mappings dynamically from metaclass (fallback to empty dict)
                for attr in dir(meta):
                    if attr == 'tuple_mappings':
                        tuple_mappings = getattr(meta, attr)
                        break
            except:
                pass

            if f'TUPLE_{tuple_name}' in tuple_mappings:
                return f"enhanced_theme.get_color_tuple('{tuple_mappings[f'TUPLE_{tuple_name}']}')"
            else:
                # Fallback: convert to lowercase with underscores
                modern_name = tuple_name.lower()
                return f"enhanced_theme.get_color_tuple('{modern_name}')"

        # Ersetze zuerst TUPLE_* (spezifischer) und dann COLOR_* (allgemeiner)
        converted = re.sub(tuple_pattern, tuple_replacer, legacy_code)
        converted = re.sub(color_pattern, color_replacer, converted)

        return converted

    # =============================================================================
    # CONTAINER COLORS (Static - no theme dependency) - DEPRECATED
    # =============================================================================
    # These are now dynamically generated via CONTAINER_STYLE_* properties
    # COLOR_CONTAINER_UPLOAD_LIGHT = "#F8F9FA"
    # COLOR_CONTAINER_UPLOAD = "#E9ECEF"
    # COLOR_CONTAINER_WORKFLOW = "#DEE2E6"
    # COLOR_CONTAINER_CUSTOMER = "#EBF8FF"

    # =============================================================================
    # LAYOUT CONSTANTS (Static)
    # =============================================================================
    # Padding constants
    PADDING_XS = 2
    PADDING_S = 4
    PADDING_M = 8
    PADDING_L = 12

    # Corner radius constants
    CORNER_RADIUS_SMALL = 4
    CORNER_RADIUS_MEDIUM = 8
    CORNER_RADIUS_LARGE = 12
    CORNER_RADIUS = 8

    # Font constants
    FONT_FAMILY_UI = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    # Font size constants
    FONT_SIZE_HEADING_LARGE = 24
    FONT_SIZE_HEADING_MEDIUM = 18
    FONT_SIZE_HEADING_SMALL = 16
    FONT_SIZE_BODY = 12
    FONT_SIZE_BODY_SMALL = 10
    FONT_SIZE_BUTTON = 12

    # Font specifications
    H1_SPECS = (24, "bold")
    H2_SPECS = (18, "bold")
    H3_SPECS = (16, "bold")
    BODY_SPECS = (12, "normal")
    CAPTION_SPECS = (10, "normal")
    BUTTON_SPECS = (12, "normal")

    # Spacing constants
    SPACING_XS = 4
    SPACING_S = 8
    SPACING_M = 12
    SPACING_L = 16
    SPACING_XL = 24
    SPACING_XXL = 32

    # Padding constants
    PADDING_XS = 4
    PADDING_S = 8
    PADDING_M = 12
    PADDING_L = 16
    PADDING_XL = 24
    PADDING_XXL = 32

    # Card height constants
    CARD_HEIGHT_COMPACT = 80
    CARD_HEIGHT_SMALL = 120
    CARD_HEIGHT_MEDIUM = 200
    CARD_HEIGHT_LARGE = 300

    # Button height constants
    BUTTON_HEIGHT_SMALL = 28
    BUTTON_HEIGHT_MEDIUM = 36
    BUTTON_HEIGHT_LARGE = 48

    # Container height constants for sections
    SECTION_CONTAINER_HEIGHT = 600  # Einheitliche HÃ¶he fÃ¼r alle Sektionen

    # =============================================================================
    # UTILITY METHODS (Single implementation)
    # =============================================================================
    @classmethod
    def get_font(cls, font_type: str) -> 'ctk.CTkFont':
        """Get font specifications for different text types."""
        import customtkinter as ctk
        font_specs = {
            "h1": cls.H1_SPECS,
            "h2": cls.H2_SPECS,
            "h3": cls.H3_SPECS,
            "body": cls.BODY_SPECS
        }
        if font_type in font_specs:
            size, weight = font_specs[font_type]
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=size, weight=weight)
        else:
            return ctk.CTkFont(family=cls.FONT_FAMILY_UI, size=12)

    @classmethod
    def add_keyboard_drag_drop_support(cls, widget: Any, on_files_callback: Optional[Callable[[Tuple[str, ...]], None]] = None) -> None:
        """Add keyboard-accessible drag-and-drop support to a widget."""
        try:
            # Add keyboard navigation for accessibility
            def on_key_press(event: Any) -> None:
                if event.keysym == "Return" or event.keysym == "space":
                    # Open file dialog as alternative to drag-and-drop
                    try:
                        from tkinter import filedialog
                        files = filedialog.askopenfilenames(
                            title="Dateien auswÃ¤hlen",
                            filetypes=[
                                ("Alle Dateien", "*.*"),
                                ("Text Dateien", "*.txt"),
                                ("PDF Dateien", "*.pdf"),
                                ("Word Dateien", "*.docx"),
                                ("Excel Dateien", "*.xlsx")
                            ]
                        )
                        if files and on_files_callback:
                            on_files_callback(files)
                    except Exception as e:
                        print(f"Error opening file dialog: {e}")

            # Bind keyboard events
            widget.bind("<KeyPress>", on_key_press)
            widget.focus_set()

            # Add visual focus indicator
            def on_focus_in(event: Any) -> None:
                widget.configure(border_width=2, border_color=cls.COLOR_PRIMARY)

            def on_focus_out(event: Any) -> None:
                widget.configure(border_width=1, border_color=cls.COLOR_BORDER)

            widget.bind("<FocusIn>", on_focus_in)
            widget.bind("<FocusOut>", on_focus_out)

            # Set accessible attributes
            widget._accessible_description = "Dateien hierher ziehen oder Enter/Leertaste fÃ¼r Dateiauswahl drÃ¼cken"

        except Exception as e:
            print(f"Error adding keyboard drag-drop support: {e}")

    # =============================================================================
    # DYNAMIC API - GUARANTEED TO UPDATE WITH THEME CHANGES
    # =============================================================================
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """
        Get a color by name - GUARANTEED to respect theme changes.

        This method always returns the current theme's color and cannot
        be cached statically like the legacy COLOR_* properties.

        Usage:
            widget.configure(fg_color=UITheme.get_color('primary'))

        Available colors:
            primary, primary_hover, secondary, secondary_hover, border, surface,
            text_primary, text_secondary, text_on_primary, text_on_dark,
            success, success_hover, danger, danger_hover, warning, info,
            warning_bg, warning_text, warning_button, warning_button_hover
        """
        # Handle special warning colors from get_warning_colors
        warning_colors = ["warning_bg", "warning_text", "warning_button", "warning_button_hover"]
        if color_name in warning_colors:
            return cls.get_warning_colors()[color_name]

        # Default to theme provider for standard colors
        return cls._theme_provider.get_color(color_name)

    @classmethod
    def get_color_tuple(cls, color_name: str) -> Tuple[str, str]:
        """
        Get a (light, dark) color tuple - GUARANTEED to respect theme changes.

        Returns: (light_color, dark_color)
        """
        return cls._theme_provider.get_color_tuple(color_name)

    @classmethod
    def get_workflow_colors(cls, workflow_id: str) -> Dict[str, str]:
        """
        Get workflow-specific colors - GUARANTEED to respect theme changes.

        Available workflows:
            angebots_workflow, pruefung_workflow, finalisierung_workflow, projekt_workflow
        """
        return cls._theme_provider.get_workflow_colors(workflow_id)

    @classmethod
    def get_button_style(cls, style_type: str) -> Dict[str, Any]:
        """
        Get button style configuration - GUARANTEED to respect theme changes.

        Available styles: 'outline', 'success'
        """
        if style_type == 'outline':
            return {
                "fg_color": "transparent",
                "hover_color": cls._theme_provider.get_color("surface"),
                "border_width": 1,
                "border_color": cls._theme_provider.get_color("border"),
                "text_color": cls._theme_provider.get_color("text_primary"),
                "corner_radius": 8
            }
        elif style_type == 'success':
            return {
                "fg_color": cls._theme_provider.get_color("success"),
                "hover_color": cls._theme_provider.get_color("success_hover"),
                "text_color": cls._theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }
        elif style_type == 'primary':
            return {
                "fg_color": cls._theme_provider.get_color("primary"),
                "hover_color": cls._theme_provider.get_color("primary_hover"),
                "text_color": cls._theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }
        elif style_type == 'secondary':
            return {
                "fg_color": cls._theme_provider.get_color("surface"),
                "hover_color": cls._theme_provider.get_color("control_hover"),
                "border_width": 1,
                "border_color": cls._theme_provider.get_color("border"),
                "text_color": cls._theme_provider.get_color("text_secondary"),
                "corner_radius": 8
            }
        elif style_type == 'danger':
            return {
                "fg_color": cls._theme_provider.get_color("danger"),
                "hover_color": cls._theme_provider.get_color("danger_hover"),
                "text_color": cls._theme_provider.get_color("text_on_primary"),
                "corner_radius": 8,
                "border_width": 0
            }
        else:
            raise ValueError(f"Unknown button style: {style_type}")

    @classmethod
    def get_tabview_style(cls) -> Dict[str, Any]:
        """Get tabview style configuration - GUARANTEED to respect theme changes."""
        return {
            "corner_radius": 8,
            "border_width": 1,
            "segmented_button_fg_color": cls._theme_provider.get_color("surface"),
            "segmented_button_selected_color": cls._theme_provider.get_color("primary"),
            "segmented_button_selected_hover_color": cls._theme_provider.get_color("primary_hover"),
            "segmented_button_unselected_color": cls._theme_provider.get_color("surface"),
            "segmented_button_unselected_hover_color": cls._theme_provider.get_color("surface"),
            "text_color": cls._theme_provider.get_color("text_primary"),
            "text_color_disabled": cls._theme_provider.get_color("text_secondary")
        }

    @classmethod
    def switch_theme(cls, theme_name: str) -> None:
        """Switch to a different theme."""
        cls._theme_provider.switch_theme(theme_name)

    @classmethod
    def add_theme_observer(cls, callback: Callable[[], None]) -> None:
        """Add a callback that will be called when the theme changes."""
        cls._theme_provider.add_observer(callback)

    # =============================================================================
    # PROFESSIONAL CONTAINER STYLES
    # =============================================================================

    # Modern Card Style with Professional Shadows
    CARD_STYLE_MODERN = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 1,
        "border_color": ProfessionalColors.NEUTRAL_GRAY_200,
        "corner_radius": CORNER_RADIUS,
    }

    # Elevated Card Style
    CARD_STYLE_ELEVATED = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 0,
        "corner_radius": CORNER_RADIUS_LARGE,
    }

    # Professional Container Styles - More vibrant
    CONTAINER_STYLE_CUSTOMER = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 2,
        "border_color": ProfessionalColors.PRIMARY_BLUE,
        "corner_radius": CORNER_RADIUS_LARGE,
    }

    CONTAINER_STYLE_UPLOAD = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 2,
        "border_color": ProfessionalColors.SECONDARY_TEAL,
        "corner_radius": CORNER_RADIUS_LARGE,
    }

    CONTAINER_STYLE_WORKFLOW = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 2,
        "border_color": ProfessionalColors.VIBRANT_PURPLE,
        "corner_radius": CORNER_RADIUS_LARGE,
    }

    # Professional Button Styles
    BUTTON_STYLE_PRIMARY = {
        "fg_color": ProfessionalColors.PRIMARY_BLUE,
        "hover_color": ProfessionalColors.PRIMARY_BLUE_HOVER,
        "text_color": ProfessionalColors.NEUTRAL_WHITE,
        "corner_radius": CORNER_RADIUS,
        "font": ("Segoe UI", 14, "bold"),
    }

    BUTTON_STYLE_SECONDARY = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "hover_color": ProfessionalColors.NEUTRAL_GRAY_50,
        "text_color": ProfessionalColors.NEUTRAL_GRAY_700,
        "border_width": 1,
        "border_color": ProfessionalColors.NEUTRAL_GRAY_300,
        "corner_radius": CORNER_RADIUS,
        "font": ("Segoe UI", 14, "normal"),
    }

    BUTTON_STYLE_SUCCESS = {
        "fg_color": ProfessionalColors.SUCCESS_GREEN,
        "hover_color": ProfessionalColors.SUCCESS_GREEN_HOVER,
        "text_color": ProfessionalColors.NEUTRAL_WHITE,
        "corner_radius": CORNER_RADIUS,
        "font": ("Segoe UI", 14, "bold"),
    }

    BUTTON_STYLE_WARNING = {
        "fg_color": ProfessionalColors.WARNING_YELLOW,
        "hover_color": ProfessionalColors.WARNING_YELLOW_HOVER,
        "text_color": ProfessionalColors.NEUTRAL_WHITE,
        "corner_radius": CORNER_RADIUS,
        "font": ("Segoe UI", 14, "bold"),
    }

    BUTTON_STYLE_DANGER = {
        "fg_color": ProfessionalColors.ERROR_RED,
        "hover_color": ProfessionalColors.ERROR_RED_HOVER,
        "text_color": ProfessionalColors.NEUTRAL_WHITE,
        "corner_radius": CORNER_RADIUS,
        "font": ("Segoe UI", 14, "bold"),
    }

    # Professional Input Styles
    INPUT_STYLE_MODERN = {
        "fg_color": ProfessionalColors.NEUTRAL_WHITE,
        "border_width": 1,
        "border_color": ProfessionalColors.NEUTRAL_GRAY_300,
        "corner_radius": CORNER_RADIUS,
        "height": INPUT_HEIGHT,
        "font": ("Segoe UI", 14),
        "text_color": ProfessionalColors.NEUTRAL_GRAY_900,
    }

    @staticmethod
    def get_spacing(name):
        """ðŸŽ¨ BEAUTIFUL SPACING SYSTEM - KompatibilitÃ¤t mit modern_translation_quality_gui.py"""
        spacing_map = {
            'xs': 4,      # Extra small spacing
            'sm': 8,      # Small spacing
            'base': 12,   # Base spacing
            'md': 16,     # Medium spacing
            'lg': 20,     # Large spacing
            'xl': 24,     # Extra large spacing
            '2xl': 32,    # 2x extra large spacing
            '3xl': 40,    # 3x extra large spacing
            '4xl': 48,    # 4x extra large spacing
            'card': 20,   # Card padding
            'section': 32, # Section spacing
            'page': 40,   # Page margins
        }
        return spacing_map.get(name, 16)

    @staticmethod
    def get_radius(name):
        """ðŸŽ¨ BEAUTIFUL BORDER RADIUS SYSTEM - KompatibilitÃ¤t mit modern_translation_quality_gui.py"""
        radius_map = {
            'none': 0,     # No radius
            'xs': 4,       # Extra small radius
            'sm': 6,       # Small radius
            'base': 8,     # Base radius
            'md': 12,      # Medium radius
            'lg': 16,      # Large radius
            'xl': 20,      # Extra large radius
            '2xl': 24,     # 2x extra large radius
            'full': 9999,  # Fully rounded
            'card': 12,    # Card corners
            'button': 8,   # Button corners
            'input': 6,    # Input field corners
        }
        return radius_map.get(name, 8)

    @staticmethod
    def get_typography(name):
        """🎯 COMPREHENSIVE TYPOGRAPHY SYSTEM - Optimierte Font-Verwaltung"""
        try:
            # Erweiterte Typografie-System mit optimierten Schriftgrößen
            optimized_fonts = {
                # MICRO TEXT (10px) - Nur für sehr kleine Labels
                'micro':        ('Segoe UI', 10, 'normal'),

                # SMALL TEXT (12px) - Captions, kleine Buttons, Menü
                'caption':      ('Segoe UI', 12, 'normal'),
                'small':        ('Segoe UI', 12, 'bold'),
                'menu':         ('Segoe UI', 12, 'normal'),

                # BODY TEXT (14px) - Standard-Text, Inputs, Beschreibungen
                'body':         ('Segoe UI', 14, 'normal'),
                'body_bold':    ('Segoe UI', 14, 'bold'),
                'input':        ('Segoe UI', 14, 'normal'),
                'button':       ('Segoe UI', 14, 'bold'),

                # LABELS (16px) - Wichtige Labels, Card-Elemente
                'label':        ('Segoe UI', 16, 'normal'),
                'label_bold':   ('Segoe UI', 16, 'bold'),

                # SUBHEADINGS (18px) - Card-Header, Sub-Sections
                'subheading':   ('Segoe UI', 18, 'bold'),
                'card_header':  ('Segoe UI', 18, 'bold'),

                # HEADINGS (22px) - Section-Titel, große Überschriften
                'heading':      ('Segoe UI', 22, 'bold'),
                'section':      ('Segoe UI', 22, 'bold'),

                # TITLES (26px) - Page-Titel, Hauptüberschriften
                'title':        ('Segoe UI', 26, 'bold'),
                'page_title':   ('Segoe UI', 26, 'bold'),

                # DISPLAY (32px) - Hero-Text, große Dekorative Elemente
                'display':      ('Segoe UI', 32, 'bold'),
                'hero':         ('Segoe UI', 32, 'normal'),
            }

            font_data = optimized_fonts.get(name)
            if font_data:
                return font_data

            # Fallback auf Standard
            return ('Segoe UI', 14, 'normal')

        except Exception:
            return ('Segoe UI', 14, 'normal')  # Sicherer Fallback
