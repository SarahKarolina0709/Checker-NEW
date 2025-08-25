#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests für SettingsService Deep-Merge & Override Verhalten."""
from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.settings_service import SettingsService  # noqa: E402


def test_settings_defaults_access():
    s = SettingsService()
    assert s.get('infrastructure.worker_pool.size') == 3
    assert s.get('plugins.enabled') is True
    assert s.get('ui.contrast_mode') is False


def test_settings_set_and_persist_like():
    s = SettingsService()
    s.set('ui.contrast_mode', True)
    assert s.get('ui.contrast_mode') is True
    # Überschreiben verschachtelt
    s.set('infrastructure.worker_pool.size', 5)
    assert s.get('infrastructure.worker_pool.size') == 5


def test_settings_override_independence():
    s = SettingsService()
    s.set('reporting.auto_generate', False)
    assert s.get('reporting.auto_generate') is False
    # Andere Default bleibt unangetastet
    assert s.get('reporting.filename_prefix') == 'analysis_report'
