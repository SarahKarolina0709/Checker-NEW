#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SettingsService - Zentrale konfigurierbare Settings-Verwaltung

Nicht-invasiver Wrapper über bestehenden ConfigManager.

Ziele:
- Vereinheitlichte Zugriffe (get/set) mit Default-Merging
- Namespaces für neue Infrastruktur (infrastructure.*, plugins.*, ui.*)
- Persistenz über ConfigManager (checker_config.json / overrides)
- Additiv: Bricht bestehende Aufrufe zu get_config_value NICHT

Hinweis:
- Keine Hardcodierung von Hex-Farben (Design-Regel) – hier nur Zahlen/Booleans/Strings
- Graceful Fallbacks bei Fehlern
- Thread-safe genug für einfache Reads/Writes (GIL ausreichend)
"""
from __future__ import annotations
"""DEPRECATED WRAPPER

Neue Datei: services.neutral_settings_service
Bitte zukünftige Imports anpassen:

    from services.neutral_settings_service import SettingsService
"""
from services.neutral_settings_service import SettingsService  # type: ignore

__all__ = ["SettingsService"]
