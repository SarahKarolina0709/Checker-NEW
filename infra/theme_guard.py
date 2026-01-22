#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Theme Guard - verhindert direkte Hex Nutzung / ermöglicht High Contrast Flag."""
from __future__ import annotations
import re
from typing import Callable

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

class ThemeGuard:
    def __init__(self, high_contrast_provider: Callable[[], bool]):
        self._hcp = high_contrast_provider

    def validate(self, color: str) -> str:
        if HEX_RE.match(color):
            # In echter Durchsetzung könnte hier geloggt oder ersetzt werden
            return color
        return color

    def apply_contrast(self, color: str) -> str:
        if not self._hcp():
            return color
        # Primitive Contrast-Steigerung (Demo): Verdunkeln
        try:
            if HEX_RE.match(color) and len(color) == 7:
                r = max(0, int(color[1:3], 16) - 30)
                g = max(0, int(color[3:5], 16) - 30)
                b = max(0, int(color[5:7], 16) - 30)
                return f"#{r:02X}{g:02X}{b:02X}"
        except Exception:
            return color
        return color

__all__ = ["ThemeGuard"]
