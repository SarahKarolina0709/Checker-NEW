#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality GUI UI Components
Professional UI components for the translation quality application
"""

# Import system
import os
# import sys  # FIXME: Invalid syntax fixed
import tkinter as tk
import customtkinter as ctk
import importlib
from design_system import DesignSystem, get_color, get_font, get_spacing, create_button, create_card

# Force light mode (Dark Mode strikt blockieren)
try:
    original_set_appearance = ctk.set_appearance_mode
    def _force_light_only(mode: str):
        if isinstance(mode, str) and mode.lower() == "dark":
            print("🚨 DARK MODE BLOCKIERT - Erzwinge Light Mode!")
        return original_set_appearance("light")
    ctk.set_appearance_mode = _force_light_only
except Exception:
    pass
ctk.set_appearance_mode("light")

# Anti-dark mode setup
try:
    from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color
    apply_aggressive_light_mode_patches()
    print("✅ Aggressive Anti-Dark-Mode aktiviert")
except ImportError:
    print("⚠️ Aggressive Anti-Dark-Mode nicht verfügbar - verwende Fallback")
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'


class IconManager:
    """Deaktivierter Icon Manager - Icons entfernt auf Benutzerwunsch"""
    
    @classmethod
    def get_icon(cls, icon_name) -> None:
        """Icons deaktiviert - gibt None zurück"""
        return None
    
    @classmethod
    def get_icon_text(cls, icon_name: str) -> str:
        """Gibt leeren String zurück da Icons deaktiviert"""
        return ""

# =========================== ASYNC QUALITY ANALYSIS ===========================
# Verhindert UI-Blockierung bei Qualitaetsanalysen

try:
    AsyncQualityAnalyzer = importlib.import_module('async_quality_analysis').AsyncQualityAnalyzer  # optional
    print("✅ Async Quality Analysis loaded successfully")
    ASYNC_QUALITY_AVAILABLE = True
except Exception:
    print("⚠️ Async Quality Analysis not found, using synchronous fallback")
    AsyncQualityAnalyzer = None
    ASYNC_QUALITY_AVAILABLE = False


# =========================== TOOLTIP SYSTEM ===========================

class ToolTip:
    """Enhanced tooltip system for better user guidance"""
    
    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.schedule_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        """Start tooltip timer on mouse enter"""
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        """Hide tooltip on mouse leave"""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        """Update tooltip position on mouse motion"""
        if self.tooltip_window:
            self.position_tooltip(event)
    
    def schedule_tooltip(self):
        """Schedule tooltip display"""
        self.cancel_tooltip()
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
    
    def show_tooltip(self):
        """Show the tooltip"""
        if self.tooltip_window:
            return
        
        try:
            x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        except:
            x, y = 0, 0
            
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            font=ctk.CTkFont(*DesignSystem.get_font('caption')),
            fg_color=get_color('gray_700'),
            text_color=get_color('white'),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8
        )
        label.pack(padx=8, pady=4)
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def position_tooltip(self, event):
        """Position tooltip near cursor"""
        if self.tooltip_window:
            x = event.x_root + 10
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

# =========================== ENHANCED BUTTON SYSTEM ===========================

class EnhancedButton:
    """Enhanced button factory with consistent styling"""
    
    @staticmethod
    def create_primary_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        """Create primary button with standardized 44px height"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=get_color('button_primary'),
            hover_color=get_color('button_primary_hover'),
            text_color=get_color('button_primary_text'),
            font=ctk.CTkFont(*DesignSystem.get_font('button_md')),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8,
            **kwargs
        )
    
    @staticmethod
    def create_secondary_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        """Create secondary button with standardized 44px height"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=get_color('button_secondary'),
            hover_color=get_color('button_secondary_hover'),
            text_color=get_color('button_secondary_text'),
            font=ctk.CTkFont(*DesignSystem.get_font('button_md')),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8,
            **kwargs
        )
    
    @staticmethod
    def create_success_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        """Create success button with standardized 44px height"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=get_color('success'),
            hover_color=get_color('success_hover'),
            text_color=get_color('white'),
            font=ctk.CTkFont(*DesignSystem.get_font('button_md')),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8,
            **kwargs
        )
    
    @staticmethod  
    def create_warning_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        """Create warning button with standardized 44px height"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=get_color('warning'),
            hover_color=get_color('warning_hover'),
            text_color=get_color('white'),
            font=ctk.CTkFont(*DesignSystem.get_font('button_md')),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8,
            **kwargs
        )
    
    @staticmethod
    def create_danger_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        """Create danger button with standardized 44px height"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=get_color('error'),
            hover_color=get_color('error_hover'),
            text_color=get_color('white'),
            font=ctk.CTkFont(*DesignSystem.get_font('button_md')),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md') or 8,
            **kwargs
        )

# =========================== PROFESSIONAL CARD SYSTEM ===========================

class ProfessionalCard(ctk.CTkFrame):
    """Beautiful Professional Card Component with Premium Styling"""

    def __init__(self, parent, title: str = "", icon_name: str = "", **kwargs):
        """Enhanced card styling with beautiful shadows and gradients"""
        defaults = create_card()
        # Transparente Inhalte behalten
        defaults.update(kwargs)
        super().__init__(parent, **defaults)

        self.content_frame = None
        self._setup_card(title, icon_name)
    
    def _setup_card(self, title: str, icon_name: str):
        """Setup beautiful card structure with text-based header"""
        if title:
            # Beautiful header with elegant typography
            header_frame = ctk.CTkFrame(self, fg_color='transparent')
            header_frame.pack(fill='x', padx=16, pady=(16, 8))
            
            # Beautiful title with premium typography
            title_label = ctk.CTkLabel(
                header_frame,
                text=title,
                font=ctk.CTkFont(*DesignSystem.get_font('heading_sm')),
                text_color=get_color('gray_700'),
                anchor='w'
            )
            title_label.pack(side='left', fill='x', expand=True)
            
        # Premium content area with beautiful spacing
        self.content_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.content_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))
    
    def get_content_frame(self):
        """Get the beautiful content frame for adding widgets"""
        return self.content_frame


class ProfessionalButton(ctk.CTkButton):
    """Beautiful Professional Button with Premium Styling & Animations"""
    
    def __init__(self, parent, text: str, style: str = 'primary', icon_name: str = "", 
                 tooltip: str = "", animation: bool = True, **kwargs):
        """Create professional button with style options"""
        
        # Beautiful style mapping with premium color schemes
        styles = {
            'primary': {
                'fg_color': get_color('button_primary'),
                'hover_color': get_color('button_primary_hover'),
                'text_color': get_color('button_primary_text'),
                'border_width': 0,
                'corner_radius': DesignSystem.get_component_property('borders', 'radius_md') or 8
            },
            'secondary': {
                'fg_color': get_color('button_secondary'),
                'hover_color': get_color('button_secondary_hover'),
                'text_color': get_color('button_secondary_text'),
                'border_width': 0,
                'corner_radius': DesignSystem.get_component_property('borders', 'radius_md') or 8
            },
            'success': {
                'fg_color': get_color('success'),
                'hover_color': get_color('success_hover'),
                'text_color': get_color('white'),
                'border_width': 0,
                'corner_radius': DesignSystem.get_component_property('borders', 'radius_md') or 8
            },
            'danger': {
                'fg_color': get_color('error'),
                'hover_color': get_color('error_hover'),
                'text_color': get_color('white'),
                'border_width': 0,
                'corner_radius': DesignSystem.get_component_property('borders', 'radius_md') or 8
            },
            'outline': {
                'fg_color': 'transparent',
                'hover_color': get_color('surface_hover'),
                'text_color': get_color('primary'),
                'border_width': DesignSystem.get_component_property('borders', 'width_medium') or 2,
                'border_color': get_color('primary'),
                'corner_radius': DesignSystem.get_component_property('borders', 'radius_md') or 8
            }
        }
        
        # Apply beautiful style defaults with premium configuration
        style_config = styles.get(style, styles['primary'])
        
        defaults = {
            'font': ctk.CTkFont(*DesignSystem.get_font('button_md')),
            'height': DesignSystem.get_component_property('heights', 'button_lg') or 44,
            'border_width': 0,
            **style_config,
            **kwargs
        }
        
        # Beautiful icon handling with enhanced spacing - ICONS ENTFERNT
        if icon_name:
            icon = IconManager.get_icon(icon_name)  # Icons deaktiviert
            if icon:
                defaults['image'] = icon
                defaults['text'] = text
                defaults['compound'] = 'left'  # Icon on left side
            else:
                # Unicode fallback with beautiful formatting
                icon_text = IconManager.get_icon_text(icon_name)
                defaults['text'] = f"{icon_text} {text}".strip()
        else:
            defaults['text'] = text
            
        super().__init__(parent, **defaults)
        
        # Add tooltip
        if tooltip:
            ToolTip(self, tooltip)
        
        # Add hover animations
        if animation:
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Enhanced hover effect"""
        self.configure(cursor="hand2")
    
    def on_leave(self, event):
        """Reset hover effect"""
        self.configure(cursor="")


# =========================== THEME SYSTEM ===========================

class UITheme:
    """Zentrale Weiterleitung ins Design-System (Fallback kompatibel)."""

    @staticmethod
    def get_color(color_name, fallback='#FFFFFF'):
        try:
            return DesignSystem.get_color(color_name)
        except Exception:
            return fallback

    @staticmethod
    def get_font(font_name, fallback=('Segoe UI', 12, 'normal')):
        try:
            return DesignSystem.get_font(font_name)
        except Exception:
            return fallback

    @staticmethod
    def get_spacing(spacing_name, fallback=8):
        try:
            return DesignSystem.get_spacing_value(spacing_name)
        except Exception:
            return fallback


# =========================== FALLBACK COMPONENTS ===========================

class ModernProgressBarFallback(ctk.CTkProgressBar):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class EnhancedButtonFallback(ctk.CTkButton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    
    @classmethod
    def create_secondary_button(cls, parent, text='Button', **kwargs):
        return cls(parent, text=text, **kwargs)


class ProfessionalCardFallback(ctk.CTkFrame):
    def __init__(self, parent, title='', icon=None, **kwargs):
        super().__init__(parent, **kwargs)


class ProfessionalButtonFallback(ctk.CTkButton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class ProgressIndicatorFallback(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
