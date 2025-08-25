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

from typing import Dict, Any, Tuple, Optional, Union
import logging
import customtkinter as ctk
from enum import Enum

class ColorToken(str, Enum):
    """Enum für häufig verwendete Farb-Tokens (Fehlerreduktion bei Aufrufen)."""
    PRIMARY = "primary"
    PRIMARY_HOVER = "primary_hover"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    DANGER = "button_danger"

# Zentrales Logger-Objekt für Design-System Warnungen
_log = logging.getLogger("design_system")


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

    # INFO -> Vereinheitlicht mit PRIMARY (Brand Blau) laut aktueller Richtlinie
    'info': '#1F4E79',              # Alias auf primary
    'info_hover': '#1A3F65',        # Alias auf primary_hover
    'info_light': '#F0F7FF',        # Alias auf primary_light

        # 🟦 SURFACE COLORS - Cards & Containers
        'surface': '#FFFFFF',           # Card surfaces
        'surface_hover': '#F8FAFC',     # Hover state for surfaces
        'surface_elevated': '#FFFFFF',  # Elevated cards (same as surface in light mode)
        'surface_border': '#E5E7EB',    # Card borders

    # 🌫️ BACKGROUND & TEXT ALIASES - Common semantic tokens used across the app
    # Background is an alias to gray_50 for convenience in UI code
    'background': '#F8FAFC',        # Alias for gray_50 (default app background)
    # Generic border alias mapping to surface_border
    'border': '#E5E7EB',            # Alias for surface_border
    # Text aliases for clearer semantics
    'text_primary': '#374151',      # Alias for gray_700
    'text_secondary': '#6B7280',    # Alias for gray_500

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

    # Warning (Orange) buttons (Variante A: Hintergrund abgedunkelt für WCAG 4.5 Kontrast mit Weiß)
    # Ursprünglich: Base #F59E0B (Kontrast ~2.15) → jetzt #C2410C (Kontrast ~5.8) / Hover dunkler #9A3106 (Kontrast ~8.2)
    'button_warning': '#C2410C',        # Dunkleres Orange für ausreichenden Kontrast
    'button_warning_hover': '#9A3106',  # Noch dunkler für klaren Hover-State
        'button_warning_text': '#FFFFFF', # Weiß behält hohen Kontrast

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
    ,
    # SPECIAL TOKEN
    'transparent': 'transparent',    # Transparenter Placeholder gemäß Design-Richtlinie
    # Fehlende Alias Tokens für rückwärtskompatible Aufrufe
    # Vereinheitlicht: info_dark exakt Alias von info_hover / primary_hover
    'info_dark': '#1A3F65',          # Alias -> info_hover
    'surface_light': '#F8FAFC',      # Alias -> surface_hover / background
    # Semantische Statusfarben (Badges / Reports)
    'status_ok': '#16A34A',          # Grüner Systemstatus
    'status_warn': '#F59E0B',        # Gelber Warnstatus
    'status_err': '#DC2626',         # Roter Fehlerstatus
    # Danger Buttons (destruktive Aktionen)
    'button_danger': '#DC2626',
    'button_danger_hover': '#B91C1C',
    'button_danger_text': '#FFFFFF',
    # Schatten (primär für HTML/PDF Export, CTk ignoriert diese ggf.)
    'shadow_sm': 'rgba(0,0,0,0.05)',
    'shadow_md': 'rgba(0,0,0,0.10)',
    'shadow_lg': 'rgba(0,0,0,0.15)',
    'shadow_inset': 'rgba(0,0,0,0.12)'
    }

    # Optional vorbereitete Dark-Mode Palette (zur Zukunftssicherheit – aktuell nicht aktiv)
    _COLORS_DARK = {
        # Nur Platzhalter; Werte müssten bei Bedarf abgestimmt werden
        'primary': '#1F4E79',
        'primary_hover': '#1A3F65',
        'primary_light': '#2A5C8A',
        'primary_dark': '#132C44'
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
    'button_sm': ('Segoe UI', 11, 'bold'),      # Small button text
    # Report-spezifische Serif-Varianten (für PDF/HTML, optional)
    'report_heading': ('Times New Roman', 14, 'bold'),
    'report_body': ('Times New Roman', 12, 'normal')
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
            'min_width_lg': 160,
            # Einheitliche horizontale / vertikale Innenabstände für Buttons
            'px': 16,
            'py': 8
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

    # ⚡ INTERNAL CACHES (leichtgewichtig, threadsafe genug für UI-Kontext)
    _COLOR_CACHE: Dict[str, str] = {}
    _SPACING_CACHE: Dict[str, int] = {}
    _FONT_TUPLE_CACHE: Dict[str, Tuple[str, int, str]] = {}
    _CTKFONT_CACHE: Dict[str, ctk.CTkFont] = {}

    @classmethod
    def clear_caches(cls) -> None:
        """Leert alle internen Token-Caches (falls zur Laufzeit Tokens geändert werden)."""
        cls._COLOR_CACHE.clear()
        cls._SPACING_CACHE.clear()
        cls._FONT_TUPLE_CACHE.clear()
        # CTkFont-Objekte nicht aktiv zerstören; neu aufbauen bei Bedarf
        cls._CTKFONT_CACHE.clear()

    _COLOR_OVERRIDES: Dict[str, str] = {}  # Dynamische Overrides (z.B. High Contrast)
    _HIGH_CONTRAST_ACTIVE: bool = False
    _HIGH_CONTRAST_MAP: Dict[str, str] = {
        # Primär etwas dunkler für höheren Kontrast zu weißem Text
        'button_primary': '#13334D',
        'button_primary_hover': '#0F283D',
        # Sekundär noch etwas dunkler
        'button_secondary': '#444444',
        'button_secondary_hover': '#383838',
        # Danger minimal angepasst für noch höheren Kontrast
        'button_danger': '#B91C1C',
        'button_danger_hover': '#991313',
        # Warning (bereits verbessert) optional noch etwas dunkler – lassen wir wie definiert
    }

    @classmethod
    def set_high_contrast(cls, enabled: bool) -> None:
        """Aktiviert/Deaktiviert den High-Contrast Modus (nicht permanent in _COLORS)."""
        cls._HIGH_CONTRAST_ACTIVE = enabled
        cls._COLOR_OVERRIDES.clear()
        if enabled:
            cls._COLOR_OVERRIDES.update(cls._HIGH_CONTRAST_MAP)
        # Caches leeren, damit neue Werte greifen
        cls._COLOR_CACHE.clear()

    @classmethod
    def get_colors(cls, *, grouped: bool = False) -> Dict[str, Any]:
        """Gibt das Farbschema zurück.

        Args:
            grouped: Wenn True, nach Kategorien gruppiert (für Inspector / Doku).
        """
        base = cls._COLORS.copy()
        # Overrides anwenden (nur Ansicht, Original bleibt unverändert)
        if cls._COLOR_OVERRIDES:
            base.update(cls._COLOR_OVERRIDES)
        if not grouped:
            return base
        # Kategorien definieren
        grouped_dict: Dict[str, Dict[str, str]] = {
            'primary': {k: v for k, v in base.items() if k.startswith('primary') or k.startswith('info')},
            'secondary': {k: v for k, v in base.items() if k.startswith('secondary')},
            'neutral': {k: v for k, v in base.items() if k.startswith('gray_') or k in ['white','background','border','surface','surface_hover','surface_elevated','surface_border','surface_light']},
            'semantic': {k: v for k, v in base.items() if k.split('_')[0] in ['success','warning','error','status']},
            'text': {k: v for k, v in base.items() if k.startswith('text_') or k.startswith('anthracite_')},
            'buttons': {k: v for k, v in base.items() if k.startswith('button_')},
            'upload': {k: v for k, v in base.items() if k.startswith('upload_')},
            'progress': {k: v for k, v in base.items() if k.startswith('progress_')},
            'special': {k: v for k, v in base.items() if k in ['transparent','shadow_sm','shadow_md','shadow_lg','shadow_inset']},
        }
        return grouped_dict

    @classmethod
    def get_color(cls, color_name: Union[str, 'ColorToken']) -> str:
        """
        Gibt eine spezifische Farbe zurück.

        Args:
            color_name: Name der Farbe (z.B. 'primary', 'success', 'gray_500')

        Returns:
            Hex-Farbcode oder Fallback-Farbe bei unbekanntem Namen
        """
        # Enum-Unterstützung
        if isinstance(color_name, Enum):
            color_name = color_name.value  # type: ignore
        if not color_name:
            _log.warning("Empty color token requested – fallback #000000")
            return '#000000'
        cached = cls._COLOR_CACHE.get(color_name)
        if cached is not None:
            return cached
        # Overrides zuerst prüfen
        if color_name in cls._COLOR_OVERRIDES:
            value = cls._COLOR_OVERRIDES[color_name]
            cls._COLOR_CACHE[color_name] = value
            return value
        if color_name not in cls._COLORS:
            _log.warning("Unknown color token: %s – fallback #000000", color_name)
        value = cls._COLORS.get(color_name, '#000000')
        cls._COLOR_CACHE[color_name] = value
        return value

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
        if not spacing_name:
            _log.warning("Empty spacing token requested – fallback 16")
            return 16
        cached = cls._SPACING_CACHE.get(spacing_name)
        if cached is not None:
            return cached
        if spacing_name not in cls._SPACING:
            _log.warning("Unknown spacing token: %s – fallback 16", spacing_name)
        value = int(cls._SPACING.get(spacing_name, 16))
        cls._SPACING_CACHE[spacing_name] = value
        return value

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
        if not font_name:
            return ('Segoe UI', 12, 'normal')
        cached = cls._FONT_TUPLE_CACHE.get(font_name)
        if cached is not None:
            return cached
        value: Tuple[str, int, str] = cls._TYPOGRAPHY.get(font_name, ('Segoe UI', 12, 'normal'))
        cls._FONT_TUPLE_CACHE[font_name] = value
        return value

    @classmethod
    def get_font_object(cls, font_name: str) -> Any:
        """
        Gibt ein gecachtes CTkFont-Objekt für den gegebenen Font-Token zurück.
        Falls CTkFont (z.B. in Headless-Tests) nicht erzeugt werden kann, wird der
        Font-Tupel-Fallback zurückgegeben.
        """
        cached = cls._CTKFONT_CACHE.get(font_name)
        if cached is not None:
            return cached
        family, size, weight = cls.get_font(font_name)
        try:
            font_obj = ctk.CTkFont(family=family, size=size, weight=weight)
            cls._CTKFONT_CACHE[font_name] = font_obj
            return font_obj
        except Exception as ex:  # pragma: no cover - nur in speziellen Umgebungen
            _log.warning("CTkFont creation failed for '%s': %s – returning tuple fallback", font_name, ex)
            return (family, size, weight)

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
                'font': cls.get_font_object('button_md')
            })
        elif style_type == 'secondary':
            base_config.update({
                'fg_color': cls.get_color('button_secondary'),
                'hover_color': cls.get_color('button_secondary_hover'),
                'text_color': cls.get_color('button_secondary_text'),
                'font': cls.get_font_object('button_md')
            })
        elif style_type == 'warning':
            base_config.update({
                'fg_color': cls.get_color('button_warning'),
                'hover_color': cls.get_color('button_warning_hover'),
                'text_color': cls.get_color('button_warning_text'),
                'font': cls.get_font_object('button_md')
            })
        elif style_type == 'danger':
            base_config.update({
                'fg_color': cls.get_color('button_danger'),
                'hover_color': cls.get_color('button_danger_hover'),
                'text_color': cls.get_color('button_danger_text'),
                'font': cls.get_font_object('button_md')
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
    def create_elevated_card_style(cls) -> Dict[str, Any]:
        """Leicht abgesetzte ("elevated") Card – simuliert Shadow über Farbnuancen.

        CTk unterstützt keine echten Shadows; wir variieren deshalb Hintergrund & Border.
        API bleibt getrennt, damit bestehende Aufrufe unverändert bleiben.
        """
        style = cls.create_card_style()
        style.update({
            'fg_color': cls.get_color('surface_elevated'),
            'border_color': cls.get_color('gray_200'),
        })
        return style

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
            'font': cls.get_font_object('body_md')
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

    # ========= GLOBAL CTK APPLICATION =========
    @classmethod
    def apply_to_ctk(cls, *, appearance: str = "light", scaling: float = 1.0, high_contrast: bool = False, css_export_path: Optional[str] = None) -> None:
        """Wendet zentrale CTk-Einstellungen + Theme an.

        Erzwingt Light-Mode laut Projekt-Richtlinie (Dark Mode wird ignoriert & geloggt).
        Führt zusätzlich eine Token-Validierung aus, um Fehler früh zu erkennen.
        """
        # High Contrast aktivieren falls gewünscht
        cls.set_high_contrast(high_contrast)
        # Light Mode Erzwingung
        if appearance.lower() != "light":
            _log.warning("Dark/Non-light appearance '%s' angefordert – Light Mode erzwungen", appearance)
        try:
            ctk.set_appearance_mode("light")
        except Exception as ex:  # pragma: no cover
            _log.warning("set_appearance_mode fehlgeschlagen: %s", ex)
        # Scaling
        try:
            ctk.set_widget_scaling(float(scaling))
        except Exception as ex:  # pragma: no cover
            _log.warning("set_widget_scaling fehlgeschlagen: %s", ex)
        # Fonts neu aufbauen falls vorher gecacht – verhindert inkonsistente metriken nach Scaling
        cls._CTKFONT_CACHE.clear()

        # Theme-Dict zusammenstellen
        theme = {
            "CTk": {"fg_color": [cls.get_color('background'), cls.get_color('background')]},
            "CTkButton": {
                "corner_radius": cls.get_component_property('borders', 'radius_md'),
                "fg_color": [cls.get_color('button_primary'), cls.get_color('button_primary')],
                "hover_color": [cls.get_color('button_primary_hover'), cls.get_color('button_primary_hover')],
                "text_color": [cls.get_color('button_primary_text'), cls.get_color('button_primary_text')]
            },
            "CTkEntry": {
                "corner_radius": cls.get_component_property('borders', 'radius_md'),
                "border_color": [cls.get_color('input_border'), cls.get_color('input_border')],
                "fg_color": [cls.get_color('input_bg'), cls.get_color('input_bg')],
                "text_color": [cls.get_color('input_text'), cls.get_color('input_text')]
            },
            "CTkLabel": {
                "text_color": [cls.get_color('text_primary'), cls.get_color('text_primary')]
            },
            "CTkFrame": {
                "fg_color": [cls.get_color('surface'), cls.get_color('surface')]
            },
            "CTkScrollbar": {
                "fg_color": [cls.get_color('secondary_light'), cls.get_color('secondary_light')],
                "button_color": [cls.get_color('secondary'), cls.get_color('secondary')],
                "button_hover_color": [cls.get_color('secondary_hover'), cls.get_color('secondary_hover')]
            }
        }
        try:
            ctk.set_default_color_theme(theme)
        except Exception:
            # Ältere Version erwartet ggf. JSON-Pfad – ignorieren
            pass

        # Nach dem Setzen validieren
        try:
            cls.validate()
        except Exception as ex:
            _log.error("DesignSystem Validation Fehler: %s", ex)

        # Kontrast-Prüfung (WCAG >= 4.5 für normale Schrift)
        try:
            checks = [
                ('button_primary', 'button_primary_text'),
                ('button_secondary', 'button_secondary_text'),
                ('button_warning', 'button_warning_text'),
                ('button_danger', 'button_danger_text')
            ]
            for bg_token, fg_token in checks:
                bg = cls.get_color(bg_token)
                fg = cls.get_color(fg_token)
                ratio = cls.contrast_ratio(fg, bg)
                if ratio < 4.5:
                    _log.warning("Geringer Kontrast (%s) zwischen %s und %s: %.2f", fg, fg_token, bg_token, ratio)
        except Exception as ex:  # pragma: no cover
            _log.warning("Kontrast-Prüfung fehlgeschlagen: %s", ex)

        # Optional CSS exportieren
        if css_export_path:
            try:
                css_content = cls.to_css_variables()
                with open(css_export_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                _log.info("✅ CSS Export geschrieben: %s", css_export_path)
            except Exception as ex:  # pragma: no cover
                _log.warning("CSS Export fehlgeschlagen (%s): %s", css_export_path, ex)

    # ========= ACCESSIBILITY (WCAG) =========
    @staticmethod
    def _luminance(hex_color: str) -> float:
        """Berechnet die relative Luminanz eines Hex-Farbwerts (#RRGGBB)."""
        hc = hex_color.lstrip('#')
        if len(hc) != 6:
            return 0.0
        r, g, b = [int(hc[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        def f(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        R, G, B = f(r), f(g), f(b)
        return 0.2126 * R + 0.7152 * G + 0.0722 * B

    @classmethod
    def contrast_ratio(cls, fg: str, bg: str) -> float:
        """Berechnet das WCAG Kontrastverhältnis zweier Farben."""
        L1, L2 = cls._luminance(fg), cls._luminance(bg)
        bright, dark = max(L1, L2), min(L1, L2)
        return (bright + 0.05) / (dark + 0.05)

    # ========= WEB / PDF BRIDGE =========
    @classmethod
    def to_css_variables(cls, prefix: str = "--ds-") -> str:
        """Exportiert relevante Tokens als CSS-Variablen (für HTML/PDF Reports)."""
        lines = [":root {"]
        for name, val in cls.get_colors().items():
            if val != 'transparent':
                lines.append(f"  {prefix}{name}: {val};")
        for name, val in cls.get_spacing().items():
            lines.append(f"  {prefix}space-{name}: {val}px;")
        # Typografie export (kombinierter Token, einfache Nutzung in CSS)
        for name, (family, size, weight) in cls.get_typography().items():
            lines.append(f"  {prefix}font-{name}: {size}px '{family}' {weight};")
        lines.append("}")
        return "\n".join(lines)

    # ========= VALIDATION =========
    @classmethod
    def validate(cls) -> None:
        """Validiert Farb-Hex-Werte (frühe Fehlererkennung)."""
        import re
        _HEX = re.compile(r"^#([A-Fa-f0-9]{6})$")
        for key, val in cls._COLORS.items():
            if val == 'transparent':
                continue
            # Skip rgba() pseudo tokens (shadows)
            if val.startswith('rgba('):
                continue
            if not _HEX.match(val):
                raise ValueError(f"Invalid color for '{key}': {val}")
        # Basis-Kontrastprüfung (loggt nur Warnungen; schlägt nicht fehl)
        try:
            bg = cls.get_color('background')
            for token in ['text_primary', 'text_secondary']:
                fg = cls.get_color(token)
                ratio = cls.contrast_ratio(fg, bg)
                if ratio < 4.5:
                    _log.warning("Niedriger Grund-Kontrast (%s vs background): %.2f < 4.5", token, ratio)
        except Exception as ex:  # pragma: no cover
            _log.warning("Kontrast-Basisprüfung fehlgeschlagen: %s", ex)


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