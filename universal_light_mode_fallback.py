#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 UNIVERSAL LIGHT MODE FALLBACK SYSTEM
========================================

Dieses System stellt sicher, dass bei JEDEM Problem automatisch Light Mode Fallbacks greifen.
Verhindert Dark Mode Erscheinungen bei fehlenden Farben, Initialisierungsfehlern, etc.
"""

import os

os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'

try:
    import customtkinter as ctk

    # 🚨 SOFORTIGE LIGHT MODE ERZWINGUNG
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 🔥 UNIVERSAL FALLBACK SYSTEM
    _original_ctk_frame_init = ctk.CTkFrame.__init__
    _original_ctk_button_init = ctk.CTkButton.__init__
    _original_ctk_label_init = ctk.CTkLabel.__init__
    _original_ctk_entry_init = ctk.CTkEntry.__init__

    def _safe_frame_init(self, *args, **kwargs):
        """Sichere CTkFrame Initialisierung mit Light Mode Fallbacks"""
        # Fallback für fg_color
        if 'fg_color' not in kwargs or kwargs['fg_color'] is None:
            kwargs['fg_color'] = '#FFFFFF'  # Weißer Fallback
        # Fallback für border_color
        if 'border_color' not in kwargs or kwargs['border_color'] is None:
            kwargs['border_color'] = '#E5E7EB'  # Heller Grau-Fallback
        return _original_ctk_frame_init(self, *args, **kwargs)

    def _safe_button_init(self, *args, **kwargs):
        """Sichere CTkButton Initialisierung mit Light Mode Fallbacks"""
        # Fallback für fg_color
        if 'fg_color' not in kwargs or kwargs['fg_color'] is None:
            kwargs['fg_color'] = '#1F4E79'  # Professional Blue Fallback
        # Fallback für text_color
        if 'text_color' not in kwargs or kwargs['text_color'] is None:
            kwargs['text_color'] = '#FFFFFF'  # Weißer Text Fallback
        # Fallback für hover_color
        if 'hover_color' not in kwargs or kwargs['hover_color'] is None:
            kwargs['hover_color'] = '#1A3F65'  # Darker Blue Fallback
        return _original_ctk_button_init(self, *args, **kwargs)

    def _safe_label_init(self, *args, **kwargs):
        """Sichere CTkLabel Initialisierung mit Light Mode Fallbacks"""
        # Fallback für text_color
        if 'text_color' not in kwargs or kwargs['text_color'] is None:
            kwargs['text_color'] = '#374151'  # Dark Gray Text Fallback
        # Fallback für fg_color
        if 'fg_color' not in kwargs or kwargs['fg_color'] is None:
            kwargs['fg_color'] = 'transparent'  # Transparent Fallback
        return _original_ctk_label_init(self, *args, **kwargs)

    def _safe_entry_init(self, *args, **kwargs):
        """Sichere CTkEntry Initialisierung mit Light Mode Fallbacks"""
        # Fallback für fg_color
        if 'fg_color' not in kwargs or kwargs['fg_color'] is None:
            kwargs['fg_color'] = '#FFFFFF'  # Weißer Fallback
        # Fallback für border_color
        if 'border_color' not in kwargs or kwargs['border_color'] is None:
            kwargs['border_color'] = '#D1D5DB'  # Light Gray Border Fallback
        # Fallback für text_color
        if 'text_color' not in kwargs or kwargs['text_color'] is None:
            kwargs['text_color'] = '#374151'  # Dark Gray Text Fallback
        return _original_ctk_entry_init(self, *args, **kwargs)

    # Ersetze die originalen Initialisierungsmethoden
    ctk.CTkFrame.__init__ = _safe_frame_init
    ctk.CTkButton.__init__ = _safe_button_init
    ctk.CTkLabel.__init__ = _safe_label_init
    ctk.CTkEntry.__init__ = _safe_entry_init

    print("✅ Universal Light Mode Fallback System aktiviert!")
    print("✅ Alle Widgets haben jetzt sichere Light Mode Fallbacks!")

except Exception as e:
    print(f"❌ Universal Fallback System Error: {e}")

# 🔥 FALLBACK COLOR HELPER
def get_safe_color(color_name, fallback='#FFFFFF'):
    """
    Sichere Farbabfrage mit garantiertem Light Mode Fallback
    """
    safe_colors = {
        'primary': '#1F4E79',
        'primary_hover': '#1A3F65',
        'secondary': '#6C757D',
        'secondary_hover': '#5A6268',
        'white': '#FFFFFF',
        'surface': '#FFFFFF',
        'surface_hover': '#F3F4F6',
        'surface_border': '#E5E7EB',
        'gray_50': '#F8FAFC',
        'gray_100': '#F1F5F9',
        'gray_200': '#E5E7EB',
        'gray_300': '#D1D5DB',
        'gray_400': '#9CA3AF',
        'gray_500': '#6B7280',
        'gray_600': '#4B5563',
        'gray_700': '#374151',
        'gray_800': '#1F2937',
        'gray_900': '#111827',
        'anthracite_700': '#374151',
        'success': '#2E8B57',
        'success_hover': '#256D43',
        'warning': '#F2994A',
        'warning_hover': '#E08B3E',
        'error': '#DC2626',
        'error_hover': '#B91C1C',
        'bg_green': '#F0FDF4',
        'bg_orange': '#FEF3C7',
        'bg_blue': '#EFF6FF',  # 🔥 HINZUGEFÜGT: Light Blue Background
        'neutral_800': '#1E293B',
        'neutral_200': '#E2E8F0',
        'text_primary': '#0F172A',
        'text_secondary': '#475569',
        'border': '#E2E8F0',
        'border_light': '#F1F5F9'
    }
    return safe_colors.get(color_name, fallback)