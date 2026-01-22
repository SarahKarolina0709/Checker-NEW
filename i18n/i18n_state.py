#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Einfacher I18N State Container (additiv)."""
from __future__ import annotations
from typing import Dict
class I18NState:
    def __init__(self, language: str = "de"):
        self.language = language
        self._catalogs: Dict[str, Dict[str, str]] = {language: {}}

    def set_catalog(self, lang: str, mapping: Dict[str, str]):
        self._catalogs[lang] = mapping

    def translate(self, key: str) -> str:
        return self._catalogs.get(self.language, {}).get(key, key)

__all__ = ["I18NState"]
