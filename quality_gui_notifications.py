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
        # Lebenszyklus-Flag und Parent-Destruction-Handling
        self._alive: bool = True
        try:  # pragma: no cover
            self.parent.bind("<Destroy>", lambda e: self._on_parent_destroy(), add="+")
        except Exception:
            pass

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
        # TTL für Dedupe-Einträge, damit _recent nicht unendlich wächst
        self._recent_ttl_s: float = 60.0

        # Sichtbarkeits-Limit & Queue
        self._max_visible = max_visible if max_visible > 0 else 4
        self._queue: Deque[Dict[str, Any]] = deque()
        self._queue_max: int = 200  # Hard-Limit gegen Backpressure/Spam
        self._queue_policy: str = 'drop_oldest'  # 'drop_oldest' | 'drop_new'

        # Accessibility / Konfiguration
        accessibility = accessibility or {}
        self._font_scale: float = float(accessibility.get('font_scale', 1.0))
        self._high_contrast: bool = bool(accessibility.get('high_contrast', False))
        self._on_announce = on_announce
        self._on_show: Optional[Callable[[str, str, int], None]] = None  # message, type, duration

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
            self._cfg_after_id = None
            self._reflow_after_id = None  # Debounce-ID für Reflow
            def _on_cfg(_e):
                try:
                    if self._cfg_after_id:
                        self.parent.after_cancel(self._cfg_after_id)
                except Exception:
                    pass
                self._cfg_after_id = self.parent.after(50, self._position_toasts_reflow)
            self.parent.bind("<Configure>", _on_cfg, add="+")
        except Exception:
            pass

        # Easing Parameter (konfigurierbar bei Bedarf)
        self._fade_in_steps = 12
        self._fade_out_steps = 10
        self._reduce_motion: bool = bool(accessibility.get('reduce_motion', False))
        self._alpha_supported: Optional[bool] = None  # wird in _set_alpha erkannt
        # Platzierung: br (bottom-right), tr (top-right), bl (bottom-left), tl (top-left)
        self._placement: str = 'br'
        self._margin = (20, 20)  # (mx, my)
        # Optionaler Dismiss-Telemetrie-Hook: Callable(message:str, type:str, reason:str, duration:int, elapsed:int)
        self._on_dismiss: Optional[Callable[[str, str, str, int, int], None]] = None

    def set_placement(self, corner: str = 'br', margin = (20, 20)):
        """Positioniere die Toasts in einer Ecke und setze Außenabstand.
        corner: 'br'|'tr'|'bl'|'tl'
        margin: Tuple (mx, my)
        """
        if corner in ('br', 'tr', 'bl', 'tl'):
            self._placement = corner
        try:
            mx, my = margin
            self._margin = (int(mx), int(my))
        except Exception:
            pass

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
                if not self._alive:
                    return
                t = type if type in self._color_tokens else 'info'
                safe_msg = message if isinstance(message, str) else str(message)
                key = f"{t}|{safe_msg}".strip()
                now = time.time()
                # Dedupe-Map sanft bereinigen
                self._recent_purge(now)
                if not force_show:
                    last = self._recent.get(key, 0)
                    if now - last < self._dedupe_window_s:
                        self._recent[key] = now
                        return
                self._recent[key] = now
                dur = max(400, int(duration))  # Mindestdauer 400ms
                payload = {
                    'message': self._t(safe_msg),
                    'type': t,
                    'duration': dur,
                    'action': action,
                    'action_text': action_text,
                }
                if len(self.active_toasts) >= self._max_visible:
                    if len(self._queue) >= self._queue_max:
                        if self._queue_policy == 'drop_oldest':
                            try:
                                self._queue.popleft()
                            except Exception:
                                pass
                        else:  # drop_new
                            logger.debug("toast.queue.drop_new_policy")
                            return
                    self._queue.append(payload)
                    logger.debug("toast.queue.enqueued")
                else:
                    self._create_toast(**payload)
            except Exception as e:  # pragma: no cover
                logger.exception("toast.create.error", exc_info=e)

        try:
            self.parent.after(0, _invoke)
        except Exception as e:  # pragma: no cover
            logger.exception("toast.dispatch.error", exc_info=e)
    
    def _create_toast(self, message: str, type: str, duration: int, action: Optional[Callable[[], None]] = None, action_text: Optional[str] = None, __on_create__: Optional[list] = None):
        """Create and display toast notification"""
        try:
            toast = ctk.CTkToplevel(self.parent)
            toast.withdraw()
            toast.overrideredirect(True)
            try:
                toast.attributes('-topmost', True)
            except Exception:
                pass
            self._set_alpha(toast, 0.0)

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

            # Robuste Font-Erkennung & Skalierung (Font-Kopie erstellen, globale DS-Fonts nicht mutieren)
            raw_font = self._get_font('body_sm') if callable(getattr(self, '_get_font', None)) else None
            if isinstance(raw_font, ctk.CTkFont):
                try:
                    fam = raw_font.cget("family")
                    size = int(raw_font.cget("size"))
                    weight = raw_font.cget("weight")
                    font_obj = ctk.CTkFont(family=fam, size=int(size * self._font_scale), weight=weight)
                except Exception:
                    font_obj = ctk.CTkFont(family="Segoe UI", size=int(12 * self._font_scale))
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

            # Dynamische, DPI-sensitive Wrap-Länge relativ zur Parent-Breite und ~4.5 Zoll Obergrenze
            try:
                self.parent.update_idletasks()
                pw = max(200, self.parent.winfo_width())
                try:
                    inch_px = int(self.parent.winfo_fpixels('1i')) or 96
                except Exception:
                    inch_px = 96
            except Exception:
                pw, inch_px = 600, 96
            wrap = max(240, min(int(pw * 0.6), int(4.5 * inch_px)))

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
            # Optional: Handle an Aufrufer zurückgeben
            try:
                if isinstance(__on_create__, list):
                    __on_create__.append(toast)
            except Exception:
                pass
            self._schedule_reflow(0)
            toast.deiconify()
            start_time = time.time()
            hide_id = self.parent.after(duration, lambda: self._start_fade_out(toast))
            self._toast_meta[toast] = {
                'start_time': start_time,
                'duration': duration,
                'hide_after_id': hide_id,
                'paused': False,
                'remaining': duration,
                'message': message,
                'type': type,
                'dismiss_reason': None,
            }
            # Hover Pause
            toast.bind('<Enter>', lambda e, t=toast: self._pause_toast(t))
            toast.bind('<Leave>', lambda e, t=toast: self._resume_toast(t))
            # ESC schließt den jeweiligen Toast
            try:
                toast.bind('<Escape>', lambda e, t=toast: self._on_esc_and_close(t))
            except Exception:
                pass
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
            # Telemetrie on_show
            if self._on_show:
                try:
                    self._on_show(message, type, duration)
                except Exception:
                    pass
            # Fokus auf Action-Button legen (falls vorhanden)
            try:
                for child in toast_frame.winfo_children():
                    if isinstance(child, ctk.CTkButton):
                        child.focus_set()
                        break
            except Exception:
                pass
        except Exception as e:  # pragma: no cover
            logger.exception("toast.internal.error", exc_info=e)
    
    def _position_toasts_reflow(self):
        """Reflow aller aktiven Toasts (bottom-right Stack)."""
        try:
            if not self._alive:
                return
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

            mx, my = self._margin
            gap = 10
            for idx, toast in enumerate(reversed(self.active_toasts)):
                try:
                    toast.update_idletasks()
                    tw = toast.winfo_reqwidth()
                    th = toast.winfo_reqheight()
                    corner = self._placement
                    if corner == 'br':
                        x = px + pw - tw - mx
                        y = py + ph - my - th - (idx * (th + gap))
                    elif corner == 'tr':
                        x = px + pw - tw - mx
                        y = py + my + (idx * (th + gap))
                    elif corner == 'bl':
                        x = px + mx
                        y = py + ph - my - th - (idx * (th + gap))
                    else:  # 'tl'
                        x = px + mx
                        y = py + my + (idx * (th + gap))
                    toast.geometry(f"+{x}+{y}")
                except Exception:
                    continue
        except Exception as e:  # pragma: no cover
            logger.exception("toast.reflow.error", exc_info=e)
    
    def _hide_toast(self, toast):
        """Toast schließen und Reflow triggern."""
        try:
            if not self._alive:
                return
            self._clear_hide_timer(toast)
            # Telemetrie feuern, falls vorhanden
            try:
                self._emit_dismiss_telemetry(toast)
            except Exception:
                pass
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
            if toast.winfo_exists():
                toast.destroy()
            # Reflow nach kleiner Verzögerung um Geometry Events zu glätten
            self._schedule_reflow(50)
            self._process_queue()
        except Exception as e:  # pragma: no cover
            logger.exception("toast.hide.error", exc_info=e)

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
        if self._alive:
            try:
                self._schedule_reflow(10)
            except Exception:
                pass
            try:
                self.parent.after(20, self._process_queue)
            except Exception:
                pass

    def _on_esc_and_close(self, toast):
        try:
            meta = self._toast_meta.get(toast)
            if meta is not None:
                meta['dismiss_reason'] = 'manual_esc'
        except Exception:
            pass
        self._start_fade_out(toast)

    def _process_queue(self):
        try:
            if not self._alive:
                return
            while self._queue and len(self.active_toasts) < self._max_visible:
                if not self._alive:
                    return
                payload = self._queue.popleft()
                try:
                    self._create_toast(**payload)
                except Exception as e:
                    logger.debug(f"toast.queue.drop: {e}")
                    continue
        except Exception as e:  # pragma: no cover
            logger.exception("toast.queue.error", exc_info=e)

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

    def _set_alpha(self, win, value: float):
        try:
            win.attributes('-alpha', float(value))
            if self._alpha_supported is None:
                self._alpha_supported = True
        except Exception:
            try:
                win.wm_attributes('-alpha', float(value))
                if self._alpha_supported is None:
                    self._alpha_supported = True
            except Exception:
                # Alpha wird nicht unterstützt – markiere und ignoriere Fade
                self._alpha_supported = False

    def _fade_in(self, toast, i: int = 0, steps: int = None):
        # Sanfte Latenzen: bei sehr kurzer Dauer weniger Steps
        base = self._fade_in_steps if not self._reduce_motion else 1
        meta = self._toast_meta.get(toast, {})
        dur = int(meta.get('duration', 1000))
        if self._alpha_supported is False:
            steps = 1
        else:
            steps = 1 if (self._reduce_motion or dur <= 800) else (steps or base)
        try:
            if not toast.winfo_exists():
                return
            t = min(1.0, i / float(steps))
            alpha = self._ease_out(t)
            if self._alpha_supported is not False:
                self._set_alpha(toast, alpha)
            if i < steps:
                # Intervall abhängig von der Dauer, begrenzt zwischen 20..60ms
                interval = max(20, min(60, int(dur / max(steps, 1))))
                self.parent.after(interval, lambda: self._fade_in(toast, i + 1, steps))
        except Exception:
            pass

    def _start_fade_out(self, toast, i: int = 0, steps: int = None):
        self._clear_hide_timer(toast)
        # Sanfte Latenzen: bei sehr kurzer Dauer weniger Steps
        base = self._fade_out_steps if not self._reduce_motion else 1
        meta = self._toast_meta.get(toast, {})
        dur = int(meta.get('duration', 1000))
        if self._alpha_supported is False:
            steps = 1
        else:
            steps = 1 if (self._reduce_motion or dur <= 800) else (steps or base)
        try:
            if not toast.winfo_exists():
                return
            t = min(1.0, i / float(steps))
            alpha = 1 - self._ease_out(t)
            if self._alpha_supported is not False:
                self._set_alpha(toast, max(0.0, alpha))
            if t >= 1.0 or alpha <= 0.02:
                # Auto-Dismiss erkannt, falls kein manueller Grund gesetzt wurde
                try:
                    if meta is not None and not meta.get('dismiss_reason'):
                        meta['dismiss_reason'] = 'auto'
                except Exception:
                    pass
                self._hide_toast(toast)
            else:
                interval = max(20, min(60, int(dur / max(steps, 1))))
                self.parent.after(interval, lambda: self._start_fade_out(toast, i + 1, steps))
        except Exception:
            self._hide_toast(toast)

    def _on_parent_destroy(self):
        """Sichere Aufräumroutine, wenn das Elternfenster zerstört wird."""
        self._alive = False
        # Bestehende After-Events abbrechen, Toasts zerstören
        try:
            if getattr(self, '_cfg_after_id', None):
                try:
                    self.parent.after_cancel(self._cfg_after_id)
                except Exception:
                    pass
                self._cfg_after_id = None
            if getattr(self, '_reflow_after_id', None):
                try:
                    self.parent.after_cancel(self._reflow_after_id)
                except Exception:
                    pass
                self._reflow_after_id = None
        except Exception:
            pass
        for t in list(self.active_toasts):
            try:
                self._clear_hide_timer(t)
                # Telemetrie: App-Shutdown Grund
                try:
                    meta = self._toast_meta.get(t)
                    if meta is not None:
                        meta['dismiss_reason'] = meta.get('dismiss_reason') or 'app_shutdown'
                except Exception:
                    pass
                if t.winfo_exists():
                    t.destroy()
            except Exception:
                pass
        self.active_toasts.clear()
        self._queue.clear()

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
            logger.exception("toast.action.error", exc_info=e)
        finally:
            # Grund setzen: manueller Close via Action
            try:
                meta = self._toast_meta.get(toast)
                if meta is not None:
                    meta['dismiss_reason'] = 'manual_action'
            except Exception:
                pass
            self._start_fade_out(toast)

    # ---------------- Öffentliche Utility-APIs ----------------
    def close_all(self):
        """Alle aktiven Toasts schließen (mit Fade-Out)."""
        for t in list(self.active_toasts):
            if t and t.winfo_exists():
                try:
                    meta = self._toast_meta.get(t)
                    if meta is not None:
                        meta['dismiss_reason'] = meta.get('dismiss_reason') or 'manual_close_all'
                except Exception:
                    pass
                self._start_fade_out(t)

    def close_all_hard(self):
        """Alle aktiven Toasts schließen und die Queue leeren."""
        self.close_all()
        try:
            self._queue.clear()
        except Exception:
            pass

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

    def set_color_tokens(self, mapping: Dict[str, tuple[str, str]]) -> None:
        """Laufzeit-Update der Farbsemantik.

        mapping Beispiel: {'success': ('success', 'white'), 'error': ('error', 'white')}
        Werte sind (bg_token, text_token) aus dem Design-System.
        """
        try:
            if not isinstance(mapping, dict):
                return
            self._color_tokens.update({k: tuple(v) for k, v in mapping.items()})
        except Exception:
            pass

    def set_accessibility(self, *, font_scale: Optional[float] = None, high_contrast: Optional[bool] = None, reduce_motion: Optional[bool] = None) -> None:
        """Komfort-API zur Laufzeit: Schrift, Kontrast, Bewegungsreduktion anpassen."""
        if font_scale is not None:
            try:
                self._font_scale = max(0.8, min(1.6, float(font_scale)))
            except Exception:
                pass
        if high_contrast is not None:
            self._high_contrast = bool(high_contrast)
        if reduce_motion is not None:
            self._reduce_motion = bool(reduce_motion)
    
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

    # ---------------- Zusätzliche optionale API ----------------
    def show_toast_with_handle(
        self,
        message: str,
        type: str = "info",
        duration: int = 3000,
        action: Optional[Callable[[], None]] = None,
        action_text: Optional[str] = None,
        force_show: bool = False,
    ) -> list[ctk.CTkToplevel]:
        """Wie show_toast, liefert aber eine Liste zurück, in die bei Erstellung das CTkToplevel-Handle eingefügt wird.

        Hinweis: Die Liste ist zunächst leer; nach Erstellung des Toasts enthält sie an Index 0 das Handle.
        """
        handle_list: list[ctk.CTkToplevel] = []

        def _invoke():
            try:
                if not self._alive:
                    return
                t = type if type in self._color_tokens else 'info'
                safe_msg = message if isinstance(message, str) else str(message)
                key = f"{t}|{safe_msg}".strip()
                now = time.time()
                self._recent_purge(now)
                if not force_show:
                    last = self._recent.get(key, 0)
                    if now - last < self._dedupe_window_s:
                        self._recent[key] = now
                        return
                self._recent[key] = now
                dur = max(400, int(duration))
                payload = {
                    'message': self._t(safe_msg),
                    'type': t,
                    'duration': dur,
                    'action': action,
                    'action_text': action_text,
                    '__on_create__': handle_list,
                }
                if len(self.active_toasts) >= self._max_visible:
                    if len(self._queue) >= self._queue_max:
                        if self._queue_policy == 'drop_oldest':
                            try:
                                self._queue.popleft()
                            except Exception:
                                pass
                        else:  # drop_new
                            logger.debug("toast.queue.drop_new_policy")
                            return
                    self._queue.append(payload)
                    logger.debug("toast.queue.enqueued")
                else:
                    self._create_toast(**payload)
            except Exception as e:
                logger.exception("toast.create.error", exc_info=e)

        try:
            self.parent.after(0, _invoke)
        except Exception as e:
            logger.exception("toast.dispatch.error", exc_info=e)
        return handle_list

    # ---------------- Private: Dedupe TTL ----------------
    def _recent_purge(self, now: float) -> None:
        """Entfernt veraltete Einträge aus der Dedupe-Map, damit sie nicht wächst."""
        try:
            cutoff = now - self._recent_ttl_s
            self._recent = {k: t for k, t in self._recent.items() if t >= cutoff}
        except Exception:
            pass

    # ---------------- Reflow Debounce ----------------
    def _schedule_reflow(self, delay_ms: int = 10) -> None:
        """Debounced Aufruf von _position_toasts_reflow."""
        try:
            if self._reflow_after_id:
                try:
                    self.parent.after_cancel(self._reflow_after_id)
                except Exception:
                    pass
            self._reflow_after_id = self.parent.after(int(delay_ms), self._position_toasts_reflow)
        except Exception:
            # Fallback ohne Debounce
            try:
                self._position_toasts_reflow()
            except Exception:
                pass

    # ---------------- Telemetrie-Hooks ----------------
    def set_on_dismiss(self, callback: Optional[Callable[[str, str, str, int, int], None]]):
        """Setze optionalen Dismiss-Telemetrie-Hook.

        Signatur: callback(message, type, reason, duration_ms, elapsed_ms)
        """
        try:
            self._on_dismiss = callback if callable(callback) else None
        except Exception:
            self._on_dismiss = None

    def set_on_show(self, callback: Optional[Callable[[str, str, int], None]]):
        """Optionalen Telemetrie-Hook beim Anzeigen setzen.

        Signatur: callback(message, type, duration_ms)
        """
        try:
            self._on_show = callback if callable(callback) else None
        except Exception:
            self._on_show = None

    def set_queue_policy(self, policy: str) -> None:
        """Setze Queue-Overflow-Policy: 'drop_oldest' (Standard) oder 'drop_new'."""
        try:
            if policy in ('drop_oldest', 'drop_new'):
                self._queue_policy = policy
        except Exception:
            pass

    def _emit_dismiss_telemetry(self, toast) -> None:
        if not self._on_dismiss:
            return
        try:
            meta = self._toast_meta.get(toast, {})
            message = meta.get('message', '')
            t = meta.get('type', 'info')
            reason = meta.get('dismiss_reason') or 'auto'
            duration = int(meta.get('duration', 0))
            start_time = meta.get('start_time', time.time())
            elapsed = int((time.time() - start_time) * 1000)
            self._on_dismiss(message, t, reason, duration, elapsed)
        except Exception:
            pass


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
