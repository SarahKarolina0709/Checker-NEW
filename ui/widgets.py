#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI Wrapper Widgets für zukünftige i18n/Design Erweiterungen (additiv)."""
from __future__ import annotations
import customtkinter as ctk
from typing import Optional, Callable

class TLabel(ctk.CTkLabel):
    def __init__(self, *a, i18n_key: Optional[str] = None, translator: Optional[Callable[[str], str]] = None, **kw):
        if i18n_key and translator:
            kw['text'] = translator(i18n_key)
        super().__init__(*a, **kw)
        self._i18n_key = i18n_key
        self._translator = translator

    def retranslate(self):
        if self._i18n_key and self._translator:
            try:
                self.configure(text=self._translator(self._i18n_key))
            except Exception:
                pass

class TButton(ctk.CTkButton):
    def __init__(self, *a, i18n_key: Optional[str] = None, translator: Optional[Callable[[str], str]] = None, **kw):
        if i18n_key and translator:
            kw['text'] = translator(i18n_key)
        super().__init__(*a, **kw)
        self._i18n_key = i18n_key
        self._translator = translator

    def retranslate(self):
        if self._i18n_key and self._translator:
            try:
                self.configure(text=self._translator(self._i18n_key))
            except Exception:
                pass

__all__ = ["TLabel", "TButton"]
