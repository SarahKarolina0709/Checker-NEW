from __future__ import annotations
import customtkinter as ctk
from typing import Any
from ds_utils import ds_get_color, get_font


class Tooltip:
    """Singleton-Tooltip pro App: eine CTkToplevel-Instanz wird wiederverwendet.

    Öffentliche API unverändert: show(widget, text, x, y), hide().
    Farben/Fonts strikt über das Design-System (Light Mode only).
    """

    def __init__(self, app: Any):
        self.app = app
        # Lokaler Handle für Kompatibilität; echte Instanz liegt auf app.*
        self.tip: ctk.CTkToplevel | None = None

    def _ensure_singleton(self, master: Any) -> ctk.CTkToplevel:
        """Erstellt/repariert die globale Tooltip-Toplevel pro App und gibt sie zurück."""
        try:
            # Bevorzugt an root hängen, sonst Widget als Fallback
            parent = getattr(self.app, 'root', None) or master
            tip = getattr(self.app, '_tooltip_toplevel', None)
            if tip is None or not getattr(tip, 'winfo_exists', lambda: False)():
                tip = ctk.CTkToplevel(parent)
                tip.overrideredirect(True)
                # Struktur nur einmal anlegen und referenzieren
                frm = ctk.CTkFrame(
                    tip,
                    fg_color=ds_get_color(self.app, 'surface'),
                    border_width=1,
                    border_color=ds_get_color(self.app, 'surface_border'),
                    corner_radius=6,
                )
                frm.pack(fill='both', expand=True)
                lbl = ctk.CTkLabel(
                    frm,
                    text='',
                    font=ctk.CTkFont(*get_font(self.app, 'caption')),
                    text_color=ds_get_color(self.app, 'text_primary'),
                    justify='left',
                )
                lbl.pack(padx=6, pady=4)
                # Referenzen speichern für schnelle Updates
                tip._container_frame = frm  # type: ignore[attr-defined]
                tip._label = lbl            # type: ignore[attr-defined]
                setattr(self.app, '_tooltip_toplevel', tip)
            return tip
        except Exception:
            # Harter Fallback: neue Toplevel instanziieren (wird bei Fehlern nicht zwischengespeichert)
            tip = ctk.CTkToplevel(master)
            tip.overrideredirect(True)
            return tip

    def show(self, widget: Any, text: str, x_root: int, y_root: int) -> None:
        try:
            tip = self._ensure_singleton(widget)
            # Geometry und Text aktualisieren
            try:
                tip.geometry(f"+{int(x_root)+12}+{int(y_root)+12}")
            except Exception:
                pass
            try:
                lbl = getattr(tip, '_label', None)
                if lbl:
                    lbl.configure(text=text)
                    # Sicherstellen, dass Farben aktuell sind (Theme-Wechsel etc.)
                    lbl.configure(text_color=ds_get_color(self.app, 'text_primary'))
                # Rahmenfarben ggf. aktualisieren
                frm = getattr(tip, '_container_frame', None)
                if frm:
                    frm.configure(
                        fg_color=ds_get_color(self.app, 'surface'),
                        border_color=ds_get_color(self.app, 'surface_border'),
                    )
            except Exception:
                pass
            try:
                tip.deiconify()
                tip.lift()
            except Exception:
                pass
            self.tip = tip
        except Exception:
            self.tip = None

    def hide(self) -> None:
        # Nicht zerstören, nur ausblenden – Wiederverwendung bleibt erhalten
        try:
            tip = getattr(self.app, '_tooltip_toplevel', None) or self.tip
            if tip and getattr(tip, 'winfo_exists', lambda: False)():
                try:
                    tip.withdraw()
                except Exception:
                    # Fallback: zerstören, falls withdraw nicht möglich ist
                    tip.destroy()
        except Exception:
            pass
        self.tip = getattr(self.app, '_tooltip_toplevel', None)
