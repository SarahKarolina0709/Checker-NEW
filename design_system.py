#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 Checker Professional Design System
====================================

Zentralisierte Design-System-Konfiguration für die gesamte Checker-Anwendung.
Alle Farben, Abstände, Typografie und Komponenten-Eigenschaften sind hier definiert.

🌟 FEATURES:
- Vollständige Farbpalette mit semantischen Namen
- Konsistente Abstände und Typografie
- Wiederverwendbare Komponenten-Konfigurationen
- Light Mode optimiert (Dark Mode deaktiviert)
- Professionelle Business-Farben

📌 VERWENDUNG:
from design_system import DesignSystem

colors = DesignSystem.get_colors()
primary_color = colors['primary']
"""

from typing import Dict, Any, Tuple
import customtkinter as ctk


class DesignSystem:
    """
    Zentrales Design-System für die Checker Professional Suite.

    Bietet konsistente Farben, Abstände, Typografie und Komponenten-Eigenschaften
    für die gesamte Anwendung.
    """

    # 🎨 PROFESSIONAL COLOR PALETTE
    _COLORS = {
        # 🔵 PRIMARY COLORS - Professional Blue Theme
        'primary': '#1F4E79',           # Main brand blue - buttons, headers
        'primary_hover': '#1A3F65',     # Darker blue for hover states
        'primary_light': '#F0F7FF',     # Very light blue for backgrounds
        'primary_dark': '#1A3A5C',      # Darker variant for contrast

        # 🔘 SECONDARY COLORS - Professional Grays
        'secondary': '#6C757D',         # Professional gray for secondary actions
        'secondary_hover': '#5A6268',   # Darker gray for hover
        'secondary_light': '#F8F9FA',   # Light gray backgrounds
        'secondary_dark': '#495057',    # Dark gray for contrast

        # ⚪ NEUTRAL PALETTE - Foundation Colors
        'white': '#FFFFFF',             # Pure white for cards, backgrounds
        'gray_50': '#F8FAFC',          # Background color
        'gray_100': '#F1F5F9',         # Light background sections
        'gray_200': '#E5E7EB',         # Borders, separators
        'gray_300': '#D1D5DB',         # Input borders
        'gray_400': '#9CA3AF',         # Placeholder text
        'gray_500': '#6B7280',         # Secondary text
        'gray_600': '#4B5563',         # Primary text (lighter)
        'gray_700': '#374151',         # Primary text (standard)
        'gray_800': '#1F2937',         # Dark text
        'gray_900': '#111827',         # Darkest text

        # 🟢 SEMANTIC COLORS - Status & Feedback
        'success': '#2E8B57',           # Success green
        'success_hover': '#256B43',     # Darker success for hover
        'success_light': '#ECFDF5',     # Light success background
        'success_600': '#059669',       # Alternative success
        'success_500': '#10B981',       # Alternative success lighter

        'warning': '#F2994A',           # Warning orange
        'warning_hover': '#E08B3E',     # Darker warning for hover
        'warning_light': '#FEF3C7',     # Light warning background
        'warning_500': '#F59E0B',       # Alternative warning

        'error': '#DC2626',             # Error red
        'error_hover': '#B91C1C',       # Darker error for hover
        'error_light': '#FEF2F2',       # Light error background
        'error_500': '#EF4444',         # Alternative error

        'info': '#2563EB',              # Info blue
        'info_hover': '#1D4ED8',        # Darker info for hover
        'info_light': '#EFF6FF',        # Light info background

        # 🟦 SURFACE COLORS - Cards & Containers
        'surface': '#FFFFFF',           # Card surfaces
        'surface_hover': '#F8FAFC',     # Hover state for surfaces
        'surface_elevated': '#FFFFFF',  # Elevated cards (same as surface in light mode)
        'surface_border': '#E5E7EB',    # Card borders

        # 🔲 ANTHRACITE THEME - Header & Dark Elements
        'anthracite_700': '#374151',    # Header background
        'anthracite_600': '#4B5563',    # Lighter anthracite
        'anthracite_800': '#1F2937',    # Darker anthracite

        # 📝 INTERACTIVE COLORS - Form Elements
        'input_bg': '#FFFFFF',          # Input field backgrounds
        'input_border': '#D1D5DB',      # Input field borders
        'input_border_focus': '#1F4E79', # Focused input borders
        'input_text': '#374151',        # Input text color
        'input_placeholder': '#9CA3AF', # Placeholder text

        # 🔘 BUTTON COLORS - All Button States
        'button_primary': '#1F4E79',    # Primary button background
        'button_primary_hover': '#1A3F65', # Primary button hover
        'button_primary_text': '#FFFFFF', # Primary button text

    # Secondary (Gray) buttons: darker base for contrast, slightly lighter on hover for visibility
    'button_secondary': '#5A5A5A',  # Secondary button background (darker gray for better contrast)
    'button_secondary_hover': '#6A6A6A', # Secondary button hover (slight lightening for hover feedback)
        'button_secondary_text': '#FFFFFF', # Secondary button text

    # Warning (Orange) buttons: a touch stronger than badge orange to signal destructive actions
    'button_warning': '#F59E0B',    # Stronger, more saturated orange for destructive buttons
    'button_warning_hover': '#D97706', # Slightly darker on hover to indicate click readiness
        'button_warning_text': '#FFFFFF', # Warning button text

    # 🚫 DISABLED BUTTON STATE
    'button_disabled': '#E5E7EB',          # Disabled button background (gray_200)
    'button_disabled_hover': '#E5E7EB',    # Same as background to neutralize hover
    'button_disabled_text': '#9CA3AF',     # Disabled button text (gray_400)

        # 📤 UPLOAD AREA COLORS
        'upload_bg': '#FAFBFC',         # Upload area background
        'upload_border': '#CBD5E1',     # Upload area border
        'upload_hover_bg': '#F0F7FF',   # Upload area hover background
        'upload_hover_border': '#1F4E79', # Upload area hover border
        'upload_icon': '#6B7280',       # Upload icon color
        'upload_icon_hover': '#1F4E79', # Upload icon hover color
        'upload_text': '#374151',       # Upload text color
        'upload_text_hover': '#1F4E79', # Upload text hover color
        'upload_hint': '#9CA3AF',       # Upload hint text

        # 📊 PROGRESS COLORS
        'progress_bg': '#E5E7EB',       # Progress bar background
        'progress_fill': '#1F4E79',     # Progress bar fill
        'progress_text': '#6B7280',     # Progress text
        'progress_success': '#2E8B57',  # Success progress text
        'progress_warning': '#F2994A',  # Warning progress text
        'progress_error': '#DC2626'     # Error progress text
    }

    # 📐 SPACING SYSTEM
    _SPACING = {
        'xs': 4,                        # Extra small spacing
        'sm': 8,                        # Small spacing
        'md': 16,                       # Medium spacing
        'lg': 24,                       # Large spacing
        'xl': 32,                       # Extra large spacing
        '2xl': 40,                      # 2x Extra large
        '3xl': 48,                      # 3x Extra large
        '4xl': 64,                      # 4x Extra large
        '5xl': 80                       # 5x Extra large
    }

    # 📝 TYPOGRAPHY SYSTEM
    _TYPOGRAPHY = {
        'heading_lg': ('Segoe UI', 24, 'bold'),     # Large headings
        'heading_md': ('Segoe UI', 20, 'bold'),     # Medium headings
        'heading_sm': ('Segoe UI', 16, 'bold'),     # Small headings
        'body_lg': ('Segoe UI', 16, 'normal'),      # Large body text
        'body_md': ('Segoe UI', 14, 'normal'),      # Medium body text
        'body_sm': ('Segoe UI', 12, 'normal'),      # Small body text
        'caption': ('Segoe UI', 11, 'normal'),      # Caption text
        'button_lg': ('Segoe UI', 14, 'bold'),      # Large button text
        'button_md': ('Segoe UI', 12, 'bold'),      # Medium button text
        'button_sm': ('Segoe UI', 11, 'bold')       # Small button text
    }

    # 🧩 COMPONENT PROPERTIES
    _COMPONENTS = {
        'icons': {
            'quality_check': '🎯',
            'project_manage': '📁',
            'reports_view': '📊',
            'settings_open': '⚙️',
            'calendar_view': '📅',
            'status_ready': '🟢',
            'status_processing': '🟡',
            'status_error': '🔴'
        },
        'borders': {
            'radius_none': 0,          # No rounding
            'radius_hairline': 1,      # Minimal rounding (z.B. Separator)
            'radius_xs': 4,            # Extra small border radius
            'radius_sm': 6,             # Small border radius
            'radius_md': 8,             # Medium border radius
            'radius_lg': 10,            # Large border radius
            'radius_xl': 12,            # Extra large border radius
            # Pill-Radius für Badge-/Chip-Elemente
            'radius_pill': 999,
            'radius_custom_15': 15,     # Custom radius used in legacy parts
            'width_thin': 1,            # Thin border
            'width_medium': 2,          # Medium border
            'width_thick': 3            # Thick border
        },
        # Zentrale Button-Properties
        'buttons': {
            'min_width_sm': 120,
            'min_width_md': 140,
            'min_width_lg': 160
        },
        'heights': {
            'input': 40,                # Standard input height
            'button_sm': 32,            # Small button height
            'button_md': 38,            # Medium button height
            'button_lg': 44,            # Large button height
            'header': 110,              # Header height
            'footer': 55,               # Footer height
            'menu': 30                  # Menu bar height
        }
    }

    @classmethod
    def get_colors(cls) -> Dict[str, str]:
        """Gibt das vollständige Farbschema zurück."""
        return cls._COLORS.copy()

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """
        Gibt eine spezifische Farbe zurück.

        Args:
            color_name: Name der Farbe (z.B. 'primary', 'success', 'gray_500')

        Returns:
            Hex-Farbcode oder Fallback-Farbe bei unbekanntem Namen
        """
        return cls._COLORS.get(color_name, '#000000')

    @classmethod
    def get_spacing(cls) -> Dict[str, int]:
        """Gibt das vollständige Abstände-System zurück."""
        return cls._SPACING.copy()

    @classmethod
    def get_spacing_value(cls, spacing_name: str) -> int:
        """
        Gibt einen spezifischen Abstand zurück.

        Args:
            spacing_name: Name des Abstands (z.B. 'sm', 'md', 'lg')

        Returns:
            Pixel-Wert oder Fallback-Wert bei unbekanntem Namen
        """
        return cls._SPACING.get(spacing_name, 16)

    @classmethod
    def get_typography(cls) -> Dict[str, Tuple[str, int, str]]:
        """Gibt das vollständige Typografie-System zurück."""
        return cls._TYPOGRAPHY.copy()

    @classmethod
    def get_font(cls, font_name: str) -> Tuple[str, int, str]:
        """
        Gibt eine spezifische Schriftart-Konfiguration zurück.

        Args:
            font_name: Name der Schriftart (z.B. 'heading_lg', 'body_md')

        Returns:
            Tupel mit (Familie, Größe, Gewicht) oder Fallback
        """
        return cls._TYPOGRAPHY.get(font_name, ('Segoe UI', 12, 'normal'))

    @classmethod
    def get_components(cls) -> Dict[str, Any]:
        """Gibt alle Komponenten-Eigenschaften zurück."""
        return cls._COMPONENTS.copy()

    @classmethod
    def get_component_property(cls, component: str, property_name: str) -> Any:
        """
        Gibt eine spezifische Komponenten-Eigenschaft zurück.

        Args:
            component: Komponenten-Kategorie (z.B. 'icons', 'borders')
            property_name: Name der Eigenschaft

        Returns:
            Eigenschaftswert oder None bei unbekanntem Namen
        """
        return cls._COMPONENTS.get(component, {}).get(property_name)

    @classmethod
    def create_button_style(cls, style_type: str = 'primary') -> Dict[str, Any]:
        """
        Erstellt eine vollständige Button-Stil-Konfiguration.

        Args:
            style_type: Button-Stil ('primary', 'secondary', 'warning')

        Returns:
            Dictionary mit Button-Konfiguration für CustomTkinter
        """
        base_config = {
            'corner_radius': cls.get_component_property('borders', 'radius_md'),
            'border_width': 0,
            'height': cls.get_component_property('heights', 'button_md')
        }

        if style_type == 'primary':
            base_config.update({
                'fg_color': cls.get_color('button_primary'),
                'hover_color': cls.get_color('button_primary_hover'),
                'text_color': cls.get_color('button_primary_text'),
                'font': ctk.CTkFont(*cls.get_font('button_md'))
            })
        elif style_type == 'secondary':
            base_config.update({
                'fg_color': cls.get_color('button_secondary'),
                'hover_color': cls.get_color('button_secondary_hover'),
                'text_color': cls.get_color('button_secondary_text'),
                'font': ctk.CTkFont(*cls.get_font('button_md'))
            })
        elif style_type == 'warning':
            base_config.update({
                'fg_color': cls.get_color('button_warning'),
                'hover_color': cls.get_color('button_warning_hover'),
                'text_color': cls.get_color('button_warning_text'),
                'font': ctk.CTkFont(*cls.get_font('button_md'))
            })

        return base_config

    @classmethod
    def create_card_style(cls) -> Dict[str, Any]:
        """
        Erstellt eine vollständige Card-Stil-Konfiguration.

        Returns:
            Dictionary mit Card-Konfiguration für CustomTkinter
        """
        return {
            'fg_color': cls.get_color('surface'),
            'corner_radius': cls.get_component_property('borders', 'radius_xl'),
            'border_width': cls.get_component_property('borders', 'width_thin'),
            'border_color': cls.get_color('surface_border')
        }

    @classmethod
    def create_input_style(cls) -> Dict[str, Any]:
        """
        Erstellt eine vollständige Input-Stil-Konfiguration.

        Returns:
            Dictionary mit Input-Konfiguration für CustomTkinter
        """
        return {
            'fg_color': cls.get_color('input_bg'),
            'border_width': cls.get_component_property('borders', 'width_medium'),
            'border_color': cls.get_color('input_border'),
            'text_color': cls.get_color('input_text'),
            'corner_radius': cls.get_component_property('borders', 'radius_md'),
            'height': cls.get_component_property('heights', 'input'),
            'font': ctk.CTkFont(*cls.get_font('body_md'))
        }

    @classmethod
    def get_full_system(cls) -> Dict[str, Any]:
        """
        Gibt das komplette Design-System zurück (kompatibel mit bestehender GUI).

        Returns:
            Dictionary mit allen Design-System-Eigenschaften
        """
        return {
            'colors': cls.get_colors(),
            'spacing': cls.get_spacing(),
            'typography': cls.get_typography(),
            'components': cls.get_components()
        }


# 🎨 CONVENIENCE FUNCTIONS für einfache Nutzung

def get_color(color_name: str) -> str:
    """Convenience-Funktion um eine Farbe zu erhalten."""
    return DesignSystem.get_color(color_name)

def get_spacing(spacing_name: str) -> int:
    """Convenience-Funktion um einen Abstand zu erhalten."""
    return DesignSystem.get_spacing_value(spacing_name)

def get_font(font_name: str) -> Tuple[str, int, str]:
    """Convenience-Funktion um eine Schriftart zu erhalten."""
    return DesignSystem.get_font(font_name)

def create_button(**kwargs) -> Dict[str, Any]:
    """
    Erstellt einen Button mit Design-System-Styling.

    Args:
        style: Button-Stil ('primary', 'secondary', 'warning')
        **kwargs: Zusätzliche Button-Parameter

    Returns:
        Dictionary mit Button-Konfiguration
    """
    style = kwargs.pop('style', 'primary')
    config = DesignSystem.create_button_style(style)
    config.update(kwargs)
    return config

def create_card(**kwargs) -> Dict[str, Any]:
    """
    Erstellt eine Card mit Design-System-Styling.

    Args:
        **kwargs: Zusätzliche Card-Parameter

    Returns:
        Dictionary mit Card-Konfiguration
    """
    config = DesignSystem.create_card_style()
    config.update(kwargs)
    return config


# 📊 DESIGN SYSTEM INFO
def print_design_system_info():
    """Druckt eine Übersicht des Design-Systems für Entwickler."""
    print("🎨 Checker Professional Design System")
    print("="*50)

    print("\n🔵 FARBEN:")
    colors = DesignSystem.get_colors()
    for category in ['primary', 'secondary', 'success', 'warning', 'error']:
        matching_colors = {k: v for k, v in colors.items() if k.startswith(category)}
        if matching_colors:
            print(f"  {category.upper()}:")
            for name, color in matching_colors.items():
                print(f"    {name:<20} = {color}")

    print("\n📐 ABSTÄNDE:")
    spacing = DesignSystem.get_spacing()
    for name, value in spacing.items():
        print(f"  {name:<8} = {value}px")

    print("\n📝 TYPOGRAFIE:")
    typography = DesignSystem.get_typography()
    for name, (family, size, weight) in typography.items():
        print(f"  {name:<12} = {family}, {size}px, {weight}")

    print("\n🧩 KOMPONENTEN:")
    components = DesignSystem.get_components()
    for category, items in components.items():
        print(f"  {category.upper()}:")
        for name, value in items.items():
            print(f"    {name:<15} = {value}")


if __name__ == "__main__":
    # Demo der Design-System-Funktionalität
    print_design_system_info()

    # Beispiel-Verwendung
    print("\n" + "="*50)
    print("📝 BEISPIEL-VERWENDUNG:")
    print("="*50)

    print(f"Primary Color: {get_color('primary')}")
    print(f"Large Spacing: {get_spacing('lg')}px")
    print(f"Heading Font: {get_font('heading_md')}")

    print("\nButton Config:")
    button_config = create_button(style='primary', text='Test Button')
    for key, value in button_config.items():
        if key != 'font':  # Font-Objekt ist schwer lesbar
            print(f"  {key}: {value}")