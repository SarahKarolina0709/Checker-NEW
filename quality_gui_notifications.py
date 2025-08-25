#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations  # Für Python <3.9 Kompatibilität bei list[...] etc.
"""
Toast Notification System for Quality GUI
Professional toast notifications with enhanced styling and features
"""

import tkinter as tk
import customtkinter as ctk
import time
import logging
from typing import Optional, Callable, Dict, Deque, Any
from collections import deque

logger = logging.getLogger("checker")

# Hinweis: Kein hartes Light-Enforcement mehr beim Import; optional per force_light Parameter.
try:  # pragma: no cover
    from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color as _aggr_col
except Exception:  # pragma: no cover
    def _aggr_col(name, fallback=None):
        return fallback or '#FFFFFF'

def get_safe_aggressive_color(color_name, fallback=None):
    """Get safe color with anti-dark-mode protection"""
    if color_name in ['black', '#000000', '#1C1C1C']:
        return '#F8FAFC'
    return color_name if color_name else fallback


class ToastNotification:
    """Toast Notification System

    Verbesserungen:
    - Design-System Integration (Farben / Fonts) falls verfügbar
    - i18n Hook (translator callable)
    - Logging statt print
    - Stapel-Positionierung + Reflow nach Entfernen
    - Keine Hardcoded Hex Farben sofern Design-System aktiv
    """

    def __init__(
        self,
        parent_window,
        translator: Optional[Callable[[str], str]] = None,
        force_light: bool = False,
        max_visible: int = 4,
        accessibility: Optional[Dict[str, Any]] = None,
        on_announce: Optional[Callable[[str, str], None]] = None,
    ):
        # Grundlegende Zuordnung
        self.parent = parent_window
        self._t = translator or (lambda s: s)
        self.active_toasts: list[ctk.CTkToplevel] = []
        self._toast_meta: Dict[ctk.CTkToplevel, Dict[str, Any]] = {}

        # Optional Light Enforcement (kein globaler Override, nur lokal)
        if force_light:
            try:  # pragma: no cover
                ctk.set_appearance_mode("light")
                apply_aggressive_light_mode_patches()
            except Exception:
                pass

        # Dedupe Tracking (unterdrückt identische Toasts in kurzem Zeitfenster)
        self._recent: Dict[str, float] = {}
        self._dedupe_window_s: float = 2.0  # Sekunden

        # Sichtbarkeits-Limit & Queue
        self._max_visible = max_visible if max_visible > 0 else 4
        self._queue: Deque[Dict[str, Any]] = deque()

        # Accessibility / Konfiguration
        accessibility = accessibility or {}
        self._font_scale: float = float(accessibility.get('font_scale', 1.0))
        self._high_contrast: bool = bool(accessibility.get('high_contrast', False))
        self._on_announce = on_announce

        # Design-System dynamisch ermitteln (Farben / Fonts); sicherer Fallback
        try:  # pragma: no cover
            from design_system import get_color, get_font
            # Wrapper mit Fallback
            self._get_color = lambda token, fallback=None: (get_color(token) if get_color(token) else (fallback or '#FFFFFF'))
            self._get_font = lambda name: get_font(name)
        except Exception:  # Fallback Minimal
            self._get_color = lambda token, fallback=None: fallback or '#FFFFFF'
            self._get_font = lambda name: ("Segoe UI", 12, "normal")

        # Mapping semantic -> token Namen (Design System erwartet z.B. success, error, warning, info)
        self._color_tokens = {
            'success': ('success', 'white'),
            'error': ('error', 'white'),
            'warning': ('warning', 'white'),
            'info': ('info', 'white'),
        }

        # Fensterbewegung/-Größe => Reflow
        try:  # pragma: no cover
            self.parent.bind("<Configure>", lambda e: self._position_toasts_reflow())
        except Exception:
            pass

        # Easing Parameter (konfigurierbar bei Bedarf)
        self._fade_in_steps = 12
        self._fade_out_steps = 10

    def show_toast(
        self,
        message: str,
        type: str = "info",
        duration: int = 3000,
        action: Optional[Callable[[], None]] = None,
        action_text: Optional[str] = None,
        force_show: bool = False,
    ):
        """Thread-sichere öffentliche API für Toast.

        Parameter:
          message: Text
          type: success|error|warning|info
          duration: Auto-Close (ms)
          action: Optional Callback Button
          action_text: Button Beschriftung (ohne Icons)
          force_show: ignoriert Dedupe
        """
        # Immer im Tk-Hauptthread ausführen
        def _invoke():
            try:
                t = type if type in self._color_tokens else 'info'
                key = f"{t}|{message}".strip()
                now = time.time()
                if not force_show:
                    last = self._recent.get(key, 0)
                    if now - last < self._dedupe_window_s:
                        self._recent[key] = now
                        return
                self._recent[key] = now
                payload = {
                    'message': self._t(message),
                    'type': t,
                    'duration': int(duration),
                    'action': action,
                    'action_text': action_text,
                }
                if len(self.active_toasts) >= self._max_visible:
                    self._queue.append(payload)
                    logger.debug("toast.queue.enqueued")
                else:
                    self._create_toast(**payload)
            except Exception as e:  # pragma: no cover
                logger.debug(f"toast.create.error: {e}")

        try:
            self.parent.after(0, _invoke)
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.dispatch.error: {e}")
    
    def _create_toast(self, message: str, type: str, duration: int, action: Optional[Callable[[], None]] = None, action_text: Optional[str] = None):
        """Create and display toast notification"""
        try:
            toast = ctk.CTkToplevel(self.parent)
            toast.withdraw()
            toast.overrideredirect(True)
            try:
                toast.attributes('-topmost', True)
            except Exception:
                pass
            try:
                toast.attributes('-alpha', 0.0)
            except Exception:
                pass

            bg_token, text_token = self._color_tokens.get(type, ('info', 'white'))
            bg_color = self._get_color(bg_token, '#1F4E79')  # Vereinheitlichtes Brand-Blau Fallback
            text_color = self._get_color(text_token, '#FFFFFF')

            if self._high_contrast:
                # Vereinfachter High-Contrast: dunkler Text auf weißem Surface für Lesbarkeit
                bg_color = self._get_color('surface', '#FFFFFF')
                text_color = self._get_color('gray_900', '#111111')

            toast_frame = ctk.CTkFrame(
                toast,
                fg_color=bg_color,
                corner_radius=8,
                border_width=0
            )
            toast_frame.pack(fill="both", expand=True, padx=2, pady=2)

            # Robuste Font-Erkennung & Skalierung
            raw_font = self._get_font('body_sm') if callable(getattr(self, '_get_font', None)) else None
            if isinstance(raw_font, ctk.CTkFont):
                font_obj = raw_font
                try:
                    # direkte Skalierung (CTkFont hat configure)
                    current_size = font_obj.cget("size")
                    font_obj.configure(size=int(current_size * self._font_scale))
                except Exception:
                    pass
            elif isinstance(raw_font, (tuple, list)) and len(raw_font) >= 2:
                fam = raw_font[0]
                size = raw_font[1]
                weight = raw_font[2] if len(raw_font) > 2 else "normal"
                try:
                    size = int(int(size) * self._font_scale)
                except Exception:
                    pass
                font_obj = ctk.CTkFont(family=fam, size=size, weight=weight)
            else:
                font_obj = ctk.CTkFont(family="Segoe UI", size=int(12 * self._font_scale), weight="normal")

            # Dynamische Wrap-Länge relativ zur Parent-Breite
            try:
                self.parent.update_idletasks()
                pw = max(200, self.parent.winfo_width())
            except Exception:
                pw = 600
            wrap = max(240, min(420, int(pw * 0.6)))

            msg_label = ctk.CTkLabel(
                toast_frame,
                text=message,
                text_color=text_color,
                font=font_obj,
                wraplength=wrap,
                justify='left'
            )
            msg_label.pack(padx=16, pady=12)

            # Optional Action Button
            if action:
                btn_text = action_text or self._t("Aktion")
                try:
                    if self._high_contrast:
                        btn_fg = self._get_color('gray_900', '#111111')
                        btn_tx = self._get_color('white', '#FFFFFF')
                        hover_col = self._get_color('gray_700', '#333333')
                    else:
                        btn_fg = self._get_color('secondary', '#6C757D')
                        btn_tx = self._get_color('white', '#FFFFFF')
                        hover_col = self._get_color('secondary_hover', '#5A6168')
                    action_btn = ctk.CTkButton(
                        toast_frame,
                        text=btn_text,
                        fg_color=btn_fg,
                        hover_color=hover_col,
                        text_color=btn_tx,
                        command=lambda: self._invoke_action_and_close(action, toast)
                    )
                    action_btn.pack(padx=12, pady=(0, 12))
                except Exception as e:
                    logger.debug(f"toast.action_button.error: {e}")

            self.active_toasts.append(toast)
            self._position_toasts_reflow()
            toast.deiconify()
            start_time = time.time()
            hide_id = self.parent.after(duration, lambda: self._start_fade_out(toast))
            self._toast_meta[toast] = {
                'start_time': start_time,
                'duration': duration,
                'hide_after_id': hide_id,
                'paused': False,
                'remaining': duration,
            }
            # Hover Pause
            toast_frame.bind('<Enter>', lambda e, t=toast: self._pause_toast(t))
            toast_frame.bind('<Leave>', lambda e, t=toast: self._resume_toast(t))
            # Destroy Binding
            toast.bind('<Destroy>', lambda e, t=toast: self._on_toast_destroy(t))
            # Fade In (Easing)
            self._fade_in(toast)
            # Accessibility announce
            if self._on_announce:
                try:
                    self._on_announce(message, type)
                except Exception:
                    pass
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.internal.error: {e}")
    
    def _position_toasts_reflow(self):
        """Reflow aller aktiven Toasts (bottom-right Stack)."""
        try:
            # Entferne evtl. zerstörte Handles
            self.active_toasts = [t for t in self.active_toasts if t.winfo_exists()]
            # Relative Position zum Parent-Fenster für Multi-Monitor Korrektheit
            try:
                px = self.parent.winfo_rootx()
                py = self.parent.winfo_rooty()
                pw = self.parent.winfo_width()
                ph = self.parent.winfo_height()
                if pw <= 1 or ph <= 1:  # Falls noch nicht gemessen
                    self.parent.update_idletasks()
                    pw = self.parent.winfo_width()
                    ph = self.parent.winfo_height()
            except Exception:
                px, py = 0, 0
                pw = self.parent.winfo_screenwidth()
                ph = self.parent.winfo_screenheight()

            offset_y = 20
            gap = 10
            for idx, toast in enumerate(reversed(self.active_toasts)):
                try:
                    toast.update_idletasks()
                    tw = toast.winfo_reqwidth()
                    th = toast.winfo_reqheight()
                    x = px + pw - tw - 20
                    y = py + ph - offset_y - th - (idx * (th + gap))
                    toast.geometry(f"+{x}+{y}")
                except Exception:
                    continue
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.reflow.error: {e}")
    
    def _hide_toast(self, toast):
        """Toast schließen und Reflow triggern."""
        try:
            self._clear_hide_timer(toast)
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
            if toast.winfo_exists():
                toast.destroy()
            # Reflow nach kleiner Verzögerung um Geometry Events zu glätten
            self.parent.after(50, self._position_toasts_reflow)
            self._process_queue()
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.hide.error: {e}")

    # ---------------------- Interne Helper ----------------------
    def _on_toast_destroy(self, toast):
        if toast in self.active_toasts:
            try:
                self.active_toasts.remove(toast)
            except Exception:
                pass
        if toast in self._toast_meta:
            self._toast_meta.pop(toast, None)
        self._clear_hide_timer(toast)
        # Nachlaufende Reflow & Queue
        self.parent.after(10, self._position_toasts_reflow)
        self.parent.after(20, self._process_queue)

    def _process_queue(self):
        try:
            while self._queue and len(self.active_toasts) < self._max_visible:
                payload = self._queue.popleft()
                try:
                    self._create_toast(**payload)
                except Exception as e:
                    logger.debug(f"toast.queue.drop: {e}")
                    continue
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.queue.error: {e}")

    # ------------------ Timer Clear Helper ------------------
    def _clear_hide_timer(self, toast):
        meta = self._toast_meta.get(toast)
        if not meta:
            return
        hide_id = meta.get('hide_after_id')
        if hide_id:
            try:
                self.parent.after_cancel(hide_id)
            except Exception:
                pass
            meta['hide_after_id'] = None

    def _ease_out(self, t: float) -> float:
        try:
            return 1 - (1 - t) * (1 - t)
        except Exception:
            return t

    def _fade_in(self, toast, i: int = 0, steps: int = None):
        steps = steps or self._fade_in_steps
        try:
            if not toast.winfo_exists():
                return
            t = min(1.0, i / float(steps))
            alpha = self._ease_out(t)
            toast.attributes('-alpha', alpha)
            if i < steps:
                self.parent.after(30, lambda: self._fade_in(toast, i + 1, steps))
        except Exception:
            pass

    def _start_fade_out(self, toast, i: int = 0, steps: int = None):
        self._clear_hide_timer(toast)
        steps = steps or self._fade_out_steps
        try:
            if not toast.winfo_exists():
                return
            t = min(1.0, i / float(steps))
            alpha = 1 - self._ease_out(t)
            toast.attributes('-alpha', max(0.0, alpha))
            if t >= 1.0 or alpha <= 0.02:
                self._hide_toast(toast)
            else:
                self.parent.after(40, lambda: self._start_fade_out(toast, i + 1, steps))
        except Exception:
            self._hide_toast(toast)

    def _pause_toast(self, toast):
        meta = self._toast_meta.get(toast)
        if not meta or meta.get('paused'):
            return
        try:
            hide_id = meta.get('hide_after_id')
            if hide_id:
                self.parent.after_cancel(hide_id)
            elapsed = int((time.time() - meta['start_time']) * 1000)
            remaining = max(200, meta['duration'] - elapsed)
            meta['remaining'] = remaining
            meta['paused'] = True
        except Exception:
            pass

    def _resume_toast(self, toast):
        meta = self._toast_meta.get(toast)
        if not meta or not meta.get('paused'):
            return
        try:
            meta['paused'] = False
            meta['start_time'] = time.time()
            remaining = meta.get('remaining', 1000)
            meta['hide_after_id'] = self.parent.after(int(remaining), lambda: self._start_fade_out(toast))
        except Exception:
            pass

    def _invoke_action_and_close(self, action: Callable[[], None], toast):
        try:
            action()
        except Exception as e:  # pragma: no cover
            logger.debug(f"toast.action.error: {e}")
        finally:
            self._start_fade_out(toast)

    # ---------------- Öffentliche Utility-APIs ----------------
    def close_all(self):
        """Alle aktiven Toasts schließen (mit Fade-Out)."""
        for t in list(self.active_toasts):
            if t and t.winfo_exists():
                self._start_fade_out(t)

    def set_max_visible(self, n: int):
        """Dynamisch maximale sichtbare Toasts anpassen."""
        try:
            self._max_visible = max(1, int(n))
        except Exception:
            self._max_visible = 1
        self._process_queue()

    def set_font_scale(self, scale: float):
        """Schrift-Skalierung für zukünftige Toasts anpassen (bestehende bleiben unverändert)."""
        try:
            val = float(scale)
        except Exception:
            return
        self._font_scale = max(0.8, min(1.6, val))
    
    def get_max_visible(self) -> int:
        """Aktuelle Obergrenze für gleichzeitig sichtbare Toasts (Read-Only Helper)."""
        try:
            return int(self._max_visible)
        except Exception:
            return 4
    
    def show_info(self, message: str, duration: int = 2000):
        self.show_toast(message, "info", duration)
    
    def show_success(self, message: str, duration: int = 3000):
        self.show_toast(message, "success", duration)
    
    def show_error(self, message: str, duration: int = 4000):
        self.show_toast(message, "error", duration)
    
    def show_warning(self, message: str, duration: int = 3500):
        self.show_toast(message, "warning", duration)


# Export for use in other modules
__all__ = ['ToastNotification']


# Test function
def test_toast_system():  # pragma: no cover
    """Einfacher manueller Test."""
    root = ctk.CTk()
    root.title("Toast Test")
    root.geometry("420x300")

    toast_system = ToastNotification(root)

    def test_toasts():
        toast_system.show_success("Erfolgsmeldung abgeschlossen")
        root.after(800, lambda: toast_system.show_info("Info Hinweis"))
        root.after(1600, lambda: toast_system.show_warning("Warnung Beispiel"))
        root.after(2400, lambda: toast_system.show_error("Fehler Beispiel"))

    ctk.CTkButton(root, text="Toasts testen", command=test_toasts).pack(pady=50)
    root.mainloop()


if __name__ == "__main__":
    test_toast_system()
