"""
Legacy shim for src.ui.modern_ui_components
- Provides minimal classes to satisfy imports.
- No explicit typography, no icons/emojis, no hardcoded colors.
- Avoids external dependencies and animations.
"""

from typing import Optional, Callable
import customtkinter as ctk


class ModernCard(ctk.CTkFrame):
    """Simple card container without special styling."""

    def __init__(self, parent, title: str = "", subtitle: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        row = 0
        if title:
            ctk.CTkLabel(self, text=title, anchor="w").grid(row=row, column=0, sticky="ew", padx=8, pady=(8, 2))
            row += 1
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, anchor="w").grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 8))
            row += 1


class ModernButton(ctk.CTkButton):
    """Basic button. Accepts optional style string but does not enforce colors."""

    def __init__(self, parent, style: str = "primary", **kwargs):
        # Intentionally ignore style to avoid color policy issues; rely on defaults
        super().__init__(parent, **kwargs)


class ModernProgressBar(ctk.CTkFrame):
    """Very small progress bar shim with a simple fill frame."""

    def __init__(self, parent, width: int = 300, height: int = 10, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self._width = max(1, int(width))
        self._height = max(2, int(height))
        self._fill = ctk.CTkFrame(self, width=0, height=self._height - 2)
        self._fill.place(x=1, y=1)

    def set_progress(self, value: float):
        v = 0.0 if value is None else float(value)
        v = 0.0 if v < 0 else 1.0 if v > 1 else v
        self._fill.configure(width=int((self._width - 2) * v))


class ModernSearchEntry(ctk.CTkFrame):
    """Search entry shim. Exposes a CTkEntry and a callback on text changes."""

    def __init__(self, parent, placeholder: str = "Suchen...", on_search: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_search = on_search
        self.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<KeyRelease>", self._emit)

    def _emit(self, _evt=None):
        if self._on_search:
            try:
                self._on_search(self.entry.get())
            except Exception:
                pass


class ModernNotificationCenter(ctk.CTkFrame):
    """Stack simple notifications as rows. No styling enforced."""

    def __init__(self, parent, max_notifications: int = 5, **kwargs):
        super().__init__(parent, **kwargs)
        self._max = int(max_notifications) if max_notifications else 5
        self._rows: list[ctk.CTkFrame] = []

    def show_notification(self, message: str, notification_type: str = "info", duration: int = 3000, action_callback: Optional[Callable] = None):
        row = ctk.CTkFrame(self)
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=message, anchor="w").pack(side="left", padx=8, pady=6)
        if action_callback:
            ctk.CTkButton(row, text="Aktion", command=action_callback).pack(side="right", padx=6)
        ctk.CTkButton(row, text="Schließen", width=80, command=row.destroy).pack(side="right", padx=6)
        self._rows.append(row)
        if len(self._rows) > self._max:
            old = self._rows.pop(0)
            try:
                old.destroy()
            except Exception:
                pass


class ModernLoadingSpinner(ctk.CTkFrame):
    """Simple loading indicator shim without animations or icons."""

    def __init__(self, parent, size: int = 24, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        ctk.CTkLabel(self, text="Laden...").place(relx=0.5, rely=0.5, anchor="center")


class ModernStatusIndicator(ctk.CTkFrame):
    """Minimal status indicator. The set_status method is a no-op for compatibility."""

    def __init__(self, parent, status: str = "idle", **kwargs):
        super().__init__(parent, width=20, height=20, **kwargs)
        self._status = status

    def set_status(self, status: str, animated: bool = True):  # signature preserved
        self._status = status


class ModernTooltipManager:
    """No-op tooltip manager for compatibility."""

    @staticmethod
    def add_tooltip(widget, text: str, delay: int = 500, rich_content: bool = False):
        return None

    @staticmethod
    def remove_tooltip(widget):
        return None


__all__ = [
    "ModernCard",
    "ModernButton",
    "ModernProgressBar",
    "ModernSearchEntry",
    "ModernNotificationCenter",
    "ModernLoadingSpinner",
    "ModernStatusIndicator",
    "ModernTooltipManager",
]