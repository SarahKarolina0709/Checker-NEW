#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quality GUI UI Components
Professionelle UI-Komponenten für die Übersetzungsqualitäts-Anwendung.

Refactor: Light-Mode Enforcement lokal, Logging+Feature-Flags, defensive Design-System Wrapper,
robuster Tooltip, optionale Icons, Async-Helper.
"""

from __future__ import annotations

import os
import logging
import tkinter as tk
import customtkinter as ctk
import importlib
import threading
import asyncio
from typing import Awaitable, Callable, Union

# --- Logging & Feature Flags -------------------------------------------------
log = logging.getLogger(__name__)
FORCE_LIGHT = os.getenv("QUALITY_FORCE_LIGHT", "1") == "1"  # Abschaltbar im CI
ICONS_ENABLED = os.getenv("QUALITY_ICONS", "0") == "1"       # Icons später aktivierbar

# --- Defensive Design-System Imports ----------------------------------------
try:  # Versuche volles Design-System
    from design_system import (
        DesignSystem,
        get_color as _ds_color,
        get_font as _ds_font,
        get_spacing as _ds_space,
        create_card,
    )
except Exception:  # Fallbacks
    DesignSystem = None  # type: ignore
    def _ds_color(name, fallback=None): return fallback or "#FFFFFF"  # noqa: E301
    def _ds_font(name): return ("Segoe UI", 12, "normal")  # noqa: E301
    def _ds_space(name): return 8  # noqa: E301
    def create_card(*a, **k): return {"fg_color": "#FFFFFF", "corner_radius": 12}  # noqa: E301

def ds_color(token: str, fallback: str = "#FFFFFF") -> str:
    """Sicherer Farbzugriff mit Fallback."""
    try:
        c = _ds_color(token)
        return c or fallback
    except Exception:
        return fallback

def ds_font(name: str, fallback=("Segoe UI", 12, "normal")):
    try:
        if DesignSystem:
            return DesignSystem.get_font(name)
        return fallback
    except Exception:
        return fallback

def ds_space(name: str, fallback: int = 8) -> int:
    try:
        return _ds_space(name) or fallback
    except Exception:
        return fallback

# Token Shortcuts (häufig verwendete Grundfarben) mit Fallbacks
PRIMARY = ds_color('primary', '#1F4E79')  # Vereinheitlichtes Brand-Blau
SURFACE = ds_color('surface', '#F8FAFC')

# Zentrale Token-Fallback Sammlung (erleichtert spätere Theme-Swaps)
TOKENS = {
    "primary": PRIMARY,
    "success": ds_color('success', '#2E8B57'),
    "error": ds_color('error', '#DC2626'),
    "warning": ds_color('warning', '#F2994A'),
    "white": ds_color('white', '#FFFFFF'),
    "gray_700": ds_color('gray_700', '#374151'),
}

def ds_radius(md_default: int = 8) -> int:
    try:
        return DesignSystem.get_component_property('borders', 'radius_md') or md_default
    except Exception:
        return md_default

def font_from_token(token: str, fallback=("Segoe UI", 12, "normal")) -> ctk.CTkFont:
    """Liefert immer ein CTkFont Objekt – akzeptiert Tuple oder bereits erstellte Fonts."""
    f = ds_font(token, fallback)
    try:
        if isinstance(f, ctk.CTkFont):
            return f
        if isinstance(f, (tuple, list)):
            fam, size, *rest = f
            weight = (rest[0] if rest else "normal") or "normal"
            return ctk.CTkFont(family=fam, size=int(size), weight=weight)
    except Exception:
        pass
    return ctk.CTkFont(family="Segoe UI", size=12, weight="normal")

# --- Light Mode Enforcement (lokal) -----------------------------------------
def enforce_light_mode(root: ctk.CTk | None = None):
    """Erzwingt Light Mode ohne globales Monkey-Patching.

    Bindet ein ThemeChanged Event um spätere Dark-Wechsel zu neutralisieren.
    Nur aktiv, wenn FORCE_LIGHT Flag gesetzt ist.
    """
    try:
        ctk.set_appearance_mode("light")
        if root is not None:
            # Falls externe Module versuchen den Mode zu ändern
            root.bind("<<CTkThemeChanged>>", lambda _e: ctk.set_appearance_mode("light"), add="+")
    except Exception as e:
        log.warning("Light-Mode Enforcement fehlgeschlagen: %s", e)

if FORCE_LIGHT:
    # Ohne Root nur einmal setzen – später erneut mit Root aufrufen
    enforce_light_mode(None)
else:
    log.info("Light-Mode Enforcement deaktiviert (QUALITY_FORCE_LIGHT=0)")

# Optional: DPI Awareness (Windows High DPI)
try:  # pragma: no cover - Plattform spezifisch
    import ctypes  # noqa
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
except Exception:
    pass

# Anti-dark mode (aggressiv) optional – Logging statt print
try:
    from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches  # get_safe_aggressive_color entfernt
    if FORCE_LIGHT:
        apply_aggressive_light_mode_patches()
        log.info("Aggressiver Anti-Dark-Mode aktiv")
except ImportError:
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
    log.debug("Aggressive Anti-Dark-Mode Modul nicht gefunden – Fallback Light")


_ICON_TEXT = {
    # Hinweis: No-Icons Policy – diese Symbole werden NUR genutzt, falls ICONS_ENABLED explizit aktiviert.
    "upload": "📤",
    "download": "📥",
    "check": "✓",
}

class IconManager:
    """Icon Manager mit Feature Toggle (Default: deaktiviert, Policy-konform ohne Icons/Emojis)."""

    @classmethod
    def get_icon(cls, icon_name) -> None:
        if not ICONS_ENABLED:
            return None
        return None  # Placeholder für zukünftige echte Bild-Icons

    @classmethod
    def get_icon_text(cls, icon_name: str) -> str:
        if not ICONS_ENABLED:
            return ""
        return _ICON_TEXT.get(icon_name, "")

# =========================== ASYNC QUALITY ANALYSIS ===========================
# Verhindert UI-Blockierung bei Qualitaetsanalysen

try:
    AsyncQualityAnalyzer = importlib.import_module('async_quality_analysis').AsyncQualityAnalyzer  # optional
    log.info("Async Quality Analysis geladen")
    ASYNC_QUALITY_AVAILABLE = True
except Exception:
    log.warning("Async Quality Analysis nicht gefunden – synchroner Fallback")
    AsyncQualityAnalyzer = None
    ASYNC_QUALITY_AVAILABLE = False

def run_async_task(coro_or_fn: Union[Awaitable, Callable[[], Awaitable]]):
    """Startet Coroutine oder Factory robust und liefert Task/Thread Handle zurück."""
    import inspect
    coro = coro_or_fn() if callable(coro_or_fn) and not inspect.isawaitable(coro_or_fn) else coro_or_fn
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
    except Exception:
        loop = None
    if loop and loop.is_running():
        return asyncio.create_task(coro)  # type: ignore[arg-type]
    th = threading.Thread(target=lambda: asyncio.run(coro), daemon=True)
    th.start()
    return th

def dispatch_ui(root: ctk.CTk, func, *args, **kwargs):
    """Thread-sicherer Dispatch mit vollständigem Traceback-Logging bei Fehlern."""
    def _safe():
        try:
            func(*args, **kwargs)
        except Exception:
            log.exception("UI Dispatch fehlgeschlagen")
    try:
        root.after(0, _safe)
    except Exception:
        log.exception("root.after fehlgeschlagen")


# =========================== TOOLTIP SYSTEM ===========================

class ToolTip:
    """Robuster Tooltip mit Verzögerung, Clamping & sauberem Cleanup."""

    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window: tk.Toplevel | None = None
        self.schedule_id: str | None = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<Motion>", self._on_motion, add="+")
        self.widget.bind("<Destroy>", lambda _e: self.hide_tooltip(), add="+")

    def _on_enter(self, _e=None):
        self.schedule_tooltip()

    def _on_leave(self, _e=None):
        self.cancel_tooltip()
        self.hide_tooltip()

    def _on_motion(self, event=None):
        if self.tooltip_window and event:
            self._position_follow(event)

    def schedule_tooltip(self):
        self.cancel_tooltip()
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_tooltip(self):
        if self.schedule_id:
            try:
                self.widget.after_cancel(self.schedule_id)
            except Exception:
                pass
            self.schedule_id = None

    def show_tooltip(self):
        if self.tooltip_window:
            return
        try:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 25
            tw = tk.Toplevel(self.widget)
            self.tooltip_window = tw
            tw.wm_overrideredirect(True)
            tw.withdraw()
            radius = 8
            if DesignSystem and hasattr(DesignSystem, 'get_component_property'):
                try:
                    radius = DesignSystem.get_component_property('borders', 'radius_md') or 8
                except Exception:
                    radius = 8
            label = ctk.CTkLabel(
                tw,
                text=self.text,
                font=font_from_token('caption'),
                fg_color=ds_color('gray_700', '#374151'),
                text_color=ds_color('white', '#FFFFFF'),
                corner_radius=radius,
            )
            label.pack(padx=8, pady=4)
            tw.update_idletasks()
            sw = self.widget.winfo_screenwidth()
            sh = self.widget.winfo_screenheight()
            x = min(max(0, x), sw - tw.winfo_width())
            y = min(max(0, y), sh - tw.winfo_height())
            tw.geometry(f"+{x}+{y}")
            tw.deiconify()
        except Exception as e:
            log.debug("Tooltip Fehler: %s", e)
            self.hide_tooltip()

    def hide_tooltip(self):
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
            self.tooltip_window = None

    def _position_follow(self, event):
        try:
            if not self.tooltip_window:
                return
            x = event.x_root + 10
            y = event.y_root + 10
            tw = self.tooltip_window
            sw = self.widget.winfo_screenwidth()
            sh = self.widget.winfo_screenheight()
            x = min(max(0, x), sw - tw.winfo_width())
            y = min(max(0, y), sh - tw.winfo_height())
            tw.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

# =========================== ENHANCED BUTTON SYSTEM ===========================

class EnhancedButton:
    """Button Factory mit konsistentem Styling über Design-System Tokens."""

    @staticmethod
    def _radius():
        try:
            return DesignSystem.get_component_property('borders', 'radius_md') or 8
        except Exception:
            return 8

    @staticmethod
    def create_primary_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=ds_color('button_primary', PRIMARY),
            hover_color=ds_color('button_primary_hover', PRIMARY),
            text_color=ds_color('button_primary_text', '#FFFFFF'),
            font=font_from_token('button_md'),
            corner_radius=EnhancedButton._radius(),
            **kwargs
        )

    @staticmethod
    def create_secondary_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=ds_color('button_secondary', '#6C757D'),
            hover_color=ds_color('button_secondary_hover', '#5B636A'),
            text_color=ds_color('button_secondary_text', '#FFFFFF'),
            font=font_from_token('button_md'),
            corner_radius=EnhancedButton._radius(),
            **kwargs
        )

    @staticmethod
    def create_success_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=ds_color('success', '#2E8B57'),
            hover_color=ds_color('success_hover', '#27754A'),
            text_color=ds_color('white', '#FFFFFF'),
            font=font_from_token('button_md'),
            corner_radius=EnhancedButton._radius(),
            **kwargs
        )

    @staticmethod
    def create_warning_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=ds_color('warning', '#F2994A'),
            hover_color=ds_color('warning_hover', '#D8833F'),
            text_color=ds_color('white', '#FFFFFF'),
            font=font_from_token('button_md'),
            corner_radius=EnhancedButton._radius(),
            **kwargs
        )

    @staticmethod
    def create_danger_button(parent, text: str, command=None, width=180, height=44, **kwargs):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=ds_color('error', '#DC2626'),
            hover_color=ds_color('error_hover', '#B91C1C'),
            text_color=ds_color('white', '#FFFFFF'),
            font=font_from_token('button_md'),
            corner_radius=EnhancedButton._radius(),
            **kwargs
        )

# =========================== PROFESSIONAL CARD SYSTEM ===========================

class ProfessionalCard(ctk.CTkFrame):
    """Card Component unter Nutzung des Design-Systems (Fallback-sicher)."""

    def __init__(self, parent, title: str = "", icon_name: str = "", **kwargs):
        raw_defaults = create_card()
        allowed = {"fg_color", "corner_radius", "border_width", "border_color"}
        defaults = {k: v for k, v in raw_defaults.items() if k in allowed}
        defaults.update(kwargs)
        super().__init__(parent, **defaults)

        self.content_frame = None
        self._setup_card(title, icon_name)

    def _setup_card(self, title: str, icon_name: str):  # icon_name reserviert für zukünftige Aktivierung
        if title:
            header_frame = ctk.CTkFrame(self, fg_color=ds_color('transparent', 'transparent'))
            header_frame.pack(fill='x', padx=16, pady=(16, 8))
            title_label = ctk.CTkLabel(
                header_frame,
                text=title,
                font=font_from_token('heading_sm'),
                text_color=ds_color('gray_700', '#374151'),
                anchor='w'
            )
            title_label.pack(side='left', fill='x', expand=True)
        self.content_frame = ctk.CTkFrame(self, fg_color=ds_color('transparent', 'transparent'))
        self.content_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))

    def get_content_frame(self):
        return self.content_frame


class ProfessionalButton(ctk.CTkButton):
    """Professional Button mit Token-Styling & optionalem Tooltip."""

    def __init__(self, parent, text: str, style: str = 'primary', icon_name: str = "",
                 tooltip: str = "", animation: bool = True, **kwargs):
        def _radius():
            try:
                return DesignSystem.get_component_property('borders', 'radius_md') or 8
            except Exception:
                return 8
        def _height():
            try:
                return DesignSystem.get_component_property('heights', 'button_lg') or 44
            except Exception:
                return 44
        def _bw():
            try:
                return DesignSystem.get_component_property('borders', 'width_medium') or 2
            except Exception:
                return 2
        styles = {
            'primary': {
                'fg_color': ds_color('button_primary', PRIMARY),
                'hover_color': ds_color('button_primary_hover', PRIMARY),
                'text_color': ds_color('button_primary_text', '#FFFFFF'),
                'border_width': 0,
                'corner_radius': _radius(),
            },
            'secondary': {
                'fg_color': ds_color('button_secondary', '#6C757D'),
                'hover_color': ds_color('button_secondary_hover', '#5B636A'),
                'text_color': ds_color('button_secondary_text', '#FFFFFF'),
                'border_width': 0,
                'corner_radius': _radius(),
            },
            'success': {
                'fg_color': ds_color('success', '#2E8B57'),
                'hover_color': ds_color('success_hover', '#27754A'),
                'text_color': ds_color('white', '#FFFFFF'),
                'border_width': 0,
                'corner_radius': _radius(),
            },
            'danger': {
                'fg_color': ds_color('error', '#DC2626'),
                'hover_color': ds_color('error_hover', '#B91C1C'),
                'text_color': ds_color('white', '#FFFFFF'),
                'border_width': 0,
                'corner_radius': _radius(),
            },
            'outline': {
                'fg_color': ds_color('transparent', 'transparent'),
                'hover_color': ds_color('surface_hover', '#F1F5F9'),
                'text_color': ds_color('primary', PRIMARY),
                'border_width': _bw(),
                'border_color': ds_color('primary', PRIMARY),
                'corner_radius': _radius(),
            },
        }
        style_config = styles.get(style, styles['primary'])
        defaults = {
            'font': font_from_token('button_md'),
            'height': _height(),
            'border_width': style_config.get('border_width', 0),
            **style_config,
            **kwargs
        }
        if icon_name:
            icon = IconManager.get_icon(icon_name)
            if icon:
                defaults['image'] = icon
                defaults['text'] = text
                defaults['compound'] = 'left'
            else:
                defaults['text'] = f"{IconManager.get_icon_text(icon_name)} {text}".strip()
        else:
            defaults['text'] = text

        super().__init__(parent, **defaults)

        if tooltip:
            ToolTip(self, tooltip)
        if animation:
            self.bind("<Enter>", self._on_enter, add="+")
            self.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, _e=None):
        self.configure(cursor="hand2")

    def _on_leave(self, _e=None):
        self.configure(cursor="")


# =========================== THEME SYSTEM ===========================

class UITheme:
    """Wrapper für konsistente Nutzung der ds_* Helper."""

    @staticmethod
    def get_color(color_name: str, fallback: str = '#FFFFFF'):
        return ds_color(color_name, fallback)

    @staticmethod
    def get_font(font_name: str, fallback=('Segoe UI', 12, 'normal')):
        # Rückgabe ist Tuple oder CTkFont – font_from_token bei Verwendung nutzen
        return ds_font(font_name, fallback)

    @staticmethod
    def get_spacing(spacing_name, fallback=8):
        return ds_space(spacing_name, fallback)


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

# --- Öffentliche API ---------------------------------------------------------
__all__ = [
    'ToolTip',
    'EnhancedButton',
    'ProfessionalCard',
    'ProfessionalButton',
    'UITheme',
    'ModernProgressBarFallback',
    'EnhancedButtonFallback',
    'ProfessionalCardFallback',
    'ProfessionalButtonFallback',
    'ProgressIndicatorFallback',
    'enforce_light_mode',
    'run_async_task',
    'dispatch_ui',
]
