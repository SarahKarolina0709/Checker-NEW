# -*- coding: utf-8 -*-
"""
UIManager – schlanke UI-Adapter-Schicht.

Ziele:
- Keine Änderungen in welcome_screen.py nötig (API-kompatible Methoden, no-op wo sinnvoll).
- Nutzt nur öffentliche Attribute des WelcomeScreens; keine Layoutänderungen.
"""
from __future__ import annotations
from typing import Optional


class UIManager:
    def __init__(self, host=None, customer_manager=None):
        """UI Adapter, der auf den Host (Welcome-Screen) wirkt.

        - host: Referenz auf den Welcome-Screen (empfohlen)
        - customer_manager: optionale Referenz auf Business-Layer
        """
        self._host = host
        self.customer_manager = customer_manager

    # Intern: Host-Resolver (Fallback auf self für Abwärtskompatibilität)
    def _h(self):
        return self._host or self

    # ---- Methoden, die der Welcome Screen aufruft ----
    def update_search_entry(self, value: str) -> None:
        try:
            host = self._h()
            entry = getattr(host, "customer_search_entry", None)
            if entry:
                entry.delete(0, "end")
                entry.insert(0, value or "")
        except Exception:
            pass

    def hide_search_results(self) -> None:
        try:
            host = self._h()
            fr = getattr(host, "customer_results_frame", None)
            if fr:
                fr.pack_forget()
        except Exception:
            pass

    def update_current_customer_label(self, name: Optional[str]) -> None:
        try:
            host = self._h()
            lbl = getattr(host, "current_customer_label", None)
            if lbl:
                # Update text
                lbl.configure(text=(name or "Kein Kunde ausgewählt"))
                # Update pill if available
                pill = getattr(host, "current_customer_pill", None)
                if pill:
                    if name:
                        try:
                            pill.configure(
                                fg_color=host.get_color('success_light'),
                                border_color=host.get_color('success'),
                            )
                            lbl.configure(text_color=host.get_color('success'))
                        except Exception:
                            pass
                    else:
                        try:
                            pill.configure(
                                fg_color=host.get_color('warning_light'),
                                border_color=host.get_color('warning'),
                            )
                            lbl.configure(text_color=host.get_color('warning'))
                        except Exception:
                            pass
        except Exception:
            pass

    def update_customer_status(self, name: Optional[str]) -> None:
        try:
            host = self._h()
            header = getattr(host, "header_customer_status", None)
            if header:
                header.configure(text=(name or "Kein Kunde"))
        except Exception:
            pass

    def force_ui_update(self) -> None:
        try:
            host = self._h()
            # Versuche Host direkt zu aktualisieren
            if hasattr(host, "update_idletasks"):
                host.update_idletasks()
                return
            # Fallback: master falls vorhanden
            master = getattr(host, "master", None)
            if master and hasattr(master, "update_idletasks"):
                master.update_idletasks()
        except Exception:
            pass

    def show_toast(self, message: str, type: str = "info") -> None:
        try:
            host = self._h()
            # Bevorzugt zentralen ToastManager verwenden
            tm = getattr(host, 'toast_manager', None)
            if tm:
                try:
                    # Mappe Typen dynamisch auf show_* Methoden
                    method_name = {
                        'success': 'show_success',
                        'warning': 'show_warning',
                        'error': 'show_error',
                        'info': 'show_info',
                        'neutral': 'show',
                    }.get((type or 'info').lower(), 'show_info')
                    fn = getattr(tm, method_name, None)
                    if callable(fn):
                        fn(message)
                        return
                    # Fallback: generische show(message, type)
                    if hasattr(tm, 'show'):
                        tm.show(message, (type or 'info'))
                        return
                except Exception:
                    pass
            # Legacy-Fallbacks
            if hasattr(host, "_show_enhanced_toast"):
                host._show_enhanced_toast(message, type)
            elif hasattr(host, 'show_toast') and callable(getattr(host, 'show_toast')):
                host.show_toast(message, type)
        except Exception:
            pass

    def clear_customer_entry(self) -> None:
        try:
            host = self._h()
            entry = getattr(host, "customer_entry", None)
            if entry:
                entry.delete(0, "end")
        except Exception:
            pass
