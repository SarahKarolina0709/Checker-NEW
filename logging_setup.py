#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logging_setup
=============
Globales Logger-Setup mit RotatingFileHandler.
"""
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from paths import ensure_dir, ROOT, LOG_DIR, LOG_FILE


def setup_logger(name: str = "checker", level: int | str = logging.INFO, max_bytes: int = 1_000_000, backup_count: int = 5) -> logging.Logger:
    log_dir = ensure_dir(ROOT / LOG_DIR)
    log_path = log_dir / LOG_FILE

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level if isinstance(level, int) else getattr(logging, str(level).upper(), logging.INFO))

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    cfmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(cfmt)

    # File rotating
    fh = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    ffmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(ffmt)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.debug("Logger initialisiert")
    return logger
