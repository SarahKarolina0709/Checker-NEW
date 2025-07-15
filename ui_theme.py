#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Theme System für Checker Pro Suite
Zentralisierte Verwaltung von Farben, Schriftarten und Styling
"""

import customtkinter as ctk
from PIL import Image
import os
from typing import Dict, Optional

class UITheme:
    """Zentralisiertes Theme-System für konsistente GUI-Gestaltung."""
    
    # === FARBPALETTE ===
    COLORS = {
        # Hauptfarben
        'primary': '#2563EB',           # Blau - Hauptaktionen
        'primary_dark': '#1D4ED8',      # Dunkleres Blau - Hover
        'primary_light': '#3B82F6',     # Helleres Blau - Varianten
        
        # Sekundärfarben
        'secondary': '#059669',         # Grün - Erfolg/Bestätigung
        'secondary_dark': '#047857',    # Dunkles Grün - Hover
        'secondary_light': '#10B981',   # Helles Grün - Varianten
        
        # Akzentfarben
        'accent': '#F59E0B',           # Orange - Aktionen/Upload
        'accent_dark': '#D97706',      # Dunkles Orange - Hover
        'accent_light': '#FCD34D',     # Helles Orange - Highlights
        
        # Violett - Tools/Workflows
        'purple': '#7C3AED',
        'purple_dark': '#6D28D9',
        'purple_light': '#8B5CF6',
        
        # Rot - Fehler/Warnung
        'error': '#EF4444',
        'error_dark': '#DC2626',
        'error_light': '#F87171',
        
        # Grau - Neutral
        'neutral': '#6B7280',
        'neutral_dark': '#4B5563',
        'neutral_light': '#9CA3AF',
        
        # Hintergründe
        'background': '#F8FAFC',       # Haupthintergrund
        'surface': '#FFFFFF',          # Karten/Container
        'surface_secondary': '#F1F5F9', # Sekundäre Oberflächen
        
        # Text
        'text_primary': '#1F2937',     # Haupttext
        'text_secondary': '#6B7280',   # Sekundärtext
        'text_muted': '#9CA3AF',       # Gedämpfter Text
        'text_inverse': '#FFFFFF',     # Text auf dunklem Hintergrund
        
        # Ränder
        'border': '#E5E7EB',           # Standard-Rahmen
        'border_strong': '#D1D5DB',    # Starke Rahmen
        'border_light': '#F3F4F6',     # Schwache Rahmen
        
        # Status-Farben
        'success': '#10B981',
        'warning': '#F59E0B',
        'info': '#3B82F6',
        
        # Spezielle Hintergründe
        'bg_blue': '#E3F2FD',          # Blaue Card-Hintergründe
        'bg_green': '#E8F5E8',         # Grüne Card-Hintergründe
        'bg_orange': '#FEF3C7',        # Orange Card-Hintergründe
        'bg_purple': '#F3E5F5',        # Violette Card-Hintergründe
        'bg_gray': '#F8FAFC',          # Graue Card-Hintergründe
    }
    
    # === SCHRIFTARTEN ===
    FONTS = {
        # Überschriften
        'heading_xl': lambda: ctk.CTkFont(size=32, weight="bold"),      # Haupttitel
        'heading_large': lambda: ctk.CTkFont(size=24, weight="bold"),   # Sektions-Titel
        'heading_medium': lambda: ctk.CTkFont(size=18, weight="bold"),  # Unter-Titel
        'heading_small': lambda: ctk.CTkFont(size=14, weight="bold"),   # Klein-Titel
        'heading_xs': lambda: ctk.CTkFont(size=12, weight="bold"),      # Mini-Titel
        
        # Fließtext
        'body_large': lambda: ctk.CTkFont(size=14),                     # Großer Text
        'body': lambda: ctk.CTkFont(size=12),                           # Standard-Text
        'body_small': lambda: ctk.CTkFont(size=11),                     # Kleiner Text
        'caption': lambda: ctk.CTkFont(size=10),                        # Beschriftung
        
        # Buttons
        'button_large': lambda: ctk.CTkFont(size=14, weight="bold"),    # Große Buttons
        'button': lambda: ctk.CTkFont(size=12, weight="bold"),          # Standard-Buttons
        'button_small': lambda: ctk.CTkFont(size=10, weight="bold"),    # Kleine Buttons
        
        # Spezial
        'monospace': lambda: ctk.CTkFont(family="Consolas", size=11),   # Code/Pfade
        'icon': lambda: ctk.CTkFont(size=16),                           # Icon-Text
        'icon_large': lambda: ctk.CTkFont(size=24),                     # Große Icons
    }
    
    # === ABSTÄNDE ===
    SPACING = {
        'xs': 4,    # Extra klein
        'sm': 8,    # Klein
        'md': 16,   # Medium (Standard)
        'lg': 24,   # Groß
        'xl': 32,   # Extra groß
        'xxl': 48,  # Extra extra groß
    }
    
    # === RADIEN ===
    RADIUS = {
        'small': 6,
        'medium': 12,
        'large': 15,
        'round': 50,
    }
    
    # === SCHATTEN ===
    SHADOWS = {
        'light': 1,
        'medium': 2,
        'strong': 3,
    }
    
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """
        Holt eine Farbe aus der Farbpalette.
        
        Args:
            color_name: Name der Farbe (z.B. 'primary', 'text_primary')
            
        Returns:
            Hex-Farbwert oder Fallback-Farbe
        """
        return cls.COLORS.get(color_name, '#000000')
    
    @classmethod
    def get_font(cls, font_name: str) -> ctk.CTkFont:
        """
        Holt eine Schriftart aus der Font-Definition.
        
        Args:
            font_name: Name der Schriftart (z.B. 'heading_large', 'body')
            
        Returns:
            CTkFont-Objekt oder Standard-Font
        """
        try:
            font_factory = cls.FONTS.get(font_name)
            if font_factory:
                return font_factory()
            return ctk.CTkFont(size=12)  # Fallback
        except RuntimeError as e:
            if "no default root window" in str(e):
                # Fallback: Gib None zurück wenn kein Root Window existiert
                print(f"⚠️ Font '{font_name}' kann nicht erstellt werden: Kein Root Window")
                return None
            raise e
    
    @classmethod
    def get_spacing(cls, spacing_name: str) -> int:
        """
        Holt einen Abstand aus der Spacing-Definition.
        
        Args:
            spacing_name: Name des Abstands (z.B. 'md', 'lg')
            
        Returns:
            Abstand in Pixeln
        """
        return cls.SPACING.get(spacing_name, 16)
    
    @classmethod
    def get_radius(cls, radius_name: str) -> int:
        """
        Holt einen Radius aus der Radius-Definition.
        
        Args:
            radius_name: Name des Radius (z.B. 'medium', 'large')
            
        Returns:
            Radius in Pixeln
        """
        return cls.RADIUS.get(radius_name, 12)
    
    @classmethod
    def create_button_style(cls, style_type: str = 'primary') -> Dict:
        """
        Erstellt ein Button-Style-Dictionary.
        
        Args:
            style_type: Art des Buttons ('primary', 'secondary', 'accent', etc.)
            
        Returns:
            Dictionary mit Button-Styling-Parametern
        """
        styles = {
            'primary': {
                'fg_color': cls.get_color('primary'),
                'hover_color': cls.get_color('primary_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'secondary': {
                'fg_color': cls.get_color('secondary'),
                'hover_color': cls.get_color('secondary_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'accent': {
                'fg_color': cls.get_color('accent'),
                'hover_color': cls.get_color('accent_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'purple': {
                'fg_color': cls.get_color('purple'),
                'hover_color': cls.get_color('purple_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'neutral': {
                'fg_color': cls.get_color('neutral'),
                'hover_color': cls.get_color('neutral_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'error': {
                'fg_color': cls.get_color('error'),
                'hover_color': cls.get_color('error_dark'),
                'text_color': cls.get_color('text_inverse'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            },
            'outline': {
                'fg_color': 'transparent',
                'hover_color': cls.get_color('surface_secondary'),
                'text_color': cls.get_color('primary'),
                'border_color': cls.get_color('primary'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 2,
            },
            'ghost': {
                'fg_color': 'transparent',
                'hover_color': cls.get_color('surface_secondary'),
                'text_color': cls.get_color('text_primary'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 0,
            }
        }
        
        style = styles.get(style_type, styles['primary'])
        
        # Font nur hinzufügen wenn möglich
        try:
            font = cls.get_font('button')
            if font is not None:
                style['font'] = font
        except:
            pass  # Ignoriere Font-Fehler
        
        return style
    
    @classmethod
    def create_frame_style(cls, style_type: str = 'surface') -> Dict:
        """
        Erstellt ein Frame-Style-Dictionary.
        
        Args:
            style_type: Art des Frames ('surface', 'background', 'card', etc.)
            
        Returns:
            Dictionary mit Frame-Styling-Parametern
        """
        styles = {
            'surface': {
                'fg_color': cls.get_color('surface'),
                'corner_radius': cls.get_radius('medium'),
                'border_width': 1,
                'border_color': cls.get_color('border'),
            },
            'background': {
                'fg_color': cls.get_color('background'),
                'corner_radius': 0,
                'border_width': 0,
            },
            'card': {
                'fg_color': cls.get_color('surface'),
                'corner_radius': cls.get_radius('large'),
                'border_width': 2,
                'border_color': cls.get_color('border'),
            },
            'card_blue': {
                'fg_color': cls.get_color('bg_blue'),
                'corner_radius': cls.get_radius('large'),
                'border_width': 2,
                'border_color': cls.get_color('primary'),
            },
            'card_green': {
                'fg_color': cls.get_color('bg_green'),
                'corner_radius': cls.get_radius('large'),
                'border_width': 2,
                'border_color': cls.get_color('secondary'),
            },
            'card_orange': {
                'fg_color': cls.get_color('bg_orange'),
                'corner_radius': cls.get_radius('large'),
                'border_width': 2,
                'border_color': cls.get_color('accent'),
            },
            'card_purple': {
                'fg_color': cls.get_color('bg_purple'),
                'corner_radius': cls.get_radius('large'),
                'border_width': 2,
                'border_color': cls.get_color('purple'),
            },
            'transparent': {
                'fg_color': 'transparent',
                'corner_radius': 0,
                'border_width': 0,
            },
            'header': {
                'fg_color': cls.get_color('surface'),
                'corner_radius': 0,
                'border_width': 1,
                'border_color': cls.get_color('border'),
            }
        }
        
        return styles.get(style_type, styles['surface'])
    
    @classmethod
    def get_icon(cls, icon_name: str, size: tuple = (24, 24)) -> Optional[ctk.CTkImage]:
        """
        Lädt ein Icon aus dem assets/icons Ordner.
        
        Args:
            icon_name: Name des Icons (ohne .jpg Endung)
            size: Tuple mit (width, height) für das Icon
            
        Returns:
            CTkImage-Objekt oder None bei Fehler
        """
        try:
            # Pfad zum Icon-Ordner
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "assets", "icons", f"{icon_name}.jpg")
            
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ctk.CTkImage(light_image=image, dark_image=image, size=size)
            else:
                print(f"⚠️ Icon nicht gefunden: {icon_path}")
                return None
        except Exception as e:
            print(f"❌ Fehler beim Laden des Icons {icon_name}: {e}")
            return None

class ThemeManager:
    """Verwaltet Theme-Wechsel und persistente Theme-Einstellungen."""
    
    def __init__(self):
        self.current_theme = "light"
        self.theme_file = "theme_settings.json"
        self.load_theme_settings()
    
    def load_theme_settings(self):
        """Lädt gespeicherte Theme-Einstellungen."""
        try:
            import json
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
        except Exception as e:
            print(f"Fehler beim Laden der Theme-Einstellungen: {e}")
    
    def save_theme_settings(self):
        """Speichert aktuelle Theme-Einstellungen."""
        try:
            import json
            settings = {'theme': self.current_theme}
            with open(self.theme_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Fehler beim Speichern der Theme-Einstellungen: {e}")
    
    def switch_theme(self, theme_name: str):
        """Wechselt das aktuelle Theme."""
        if theme_name in ['light', 'dark']:
            self.current_theme = theme_name
            self.save_theme_settings()
            # Hier würde die GUI aktualisiert werden
            print(f"Theme gewechselt zu: {theme_name}")
        else:
            print(f"Unbekanntes Theme: {theme_name}")

# === UTILITY-FUNKTIONEN ===

def apply_theme_to_button(button: ctk.CTkButton, style_type: str = 'primary'):
    """
    Wendet Theme-Styling auf einen existierenden Button an.
    
    Args:
        button: Der Button, der gestylt werden soll
        style_type: Art des Button-Styles
    """
    style = UITheme.create_button_style(style_type)
    for key, value in style.items():
        if hasattr(button, f'configure'):
            try:
                button.configure(**{key: value})
            except Exception as e:
                print(f"Konnte {key} nicht auf Button anwenden: {e}")

def apply_theme_to_frame(frame: ctk.CTkFrame, style_type: str = 'surface'):
    """
    Wendet Theme-Styling auf einen existierenden Frame an.
    
    Args:
        frame: Der Frame, der gestylt werden soll
        style_type: Art des Frame-Styles
    """
    style = UITheme.create_frame_style(style_type)
    for key, value in style.items():
        if hasattr(frame, f'configure'):
            try:
                frame.configure(**{key: value})
            except Exception as e:
                print(f"Konnte {key} nicht auf Frame anwenden: {e}")

# Globale Theme-Instanz
theme_manager = ThemeManager()

if __name__ == "__main__":
    # Test der Theme-Funktionen
    print("=== UI Theme System Test ===")
    print(f"Primary Color: {UITheme.get_color('primary')}")
    print(f"Secondary Color: {UITheme.get_color('secondary')}")
    print(f"Medium Spacing: {UITheme.get_spacing('md')}")
    print(f"Large Radius: {UITheme.get_radius('large')}")
    
    # Test Frame-Style (ohne Font)
    frame_style = UITheme.create_frame_style('card_blue')
    print(f"Blue Card Style: {frame_style}")
    
    # Test Color mapping
    colors_test = ['primary', 'secondary', 'accent', 'error', 'success']
    print("\nFarbpalette:")
    for color in colors_test:
        print(f"  {color}: {UITheme.get_color(color)}")
    
    print("\n✅ UI Theme System ist bereit!")
    print("💡 Fonts werden erst mit Root Window verfügbar.")
