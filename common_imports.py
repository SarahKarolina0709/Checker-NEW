#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Common Imports Module
====================

Zentrale Import-Definitionen für häufig verwendete Module.
Reduziert Import-Redundanz und verbessert Performance.
"""

# Standard Library - Top verwendet
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Third Party - GUI
try:
    import customtkinter as ctk
    import tkinter as tk
    from tkinter import filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Performance Modules
import threading
import asyncio
import concurrent.futures

# Utility Modules
import traceback
import tempfile
import webbrowser

# Common Logger Setup
def setup_common_logger(name: str, level: int = logging.INFO):
    """Setup standard logger configuration."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

# Export commonly used items
__all__ = [
    "os", "sys", "json", "logging", "datetime", "Path",
    "Optional", "List", "Dict", "Any", "Tuple",
    "ctk", "tk", "filedialog", "messagebox", "GUI_AVAILABLE",
    "threading", "asyncio", "concurrent",
    "traceback", "tempfile", "webbrowser",
    "setup_common_logger"
]