#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CustomersRepository
===================
JSON-basierte Persistenz für Kundenliste.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json

from paths import ROOT, CUSTOMERS_FILE


class CustomersRepository:
    def __init__(self, storage_path: Path | None = None):
        self.path = (storage_path or (ROOT / CUSTOMERS_FILE))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Dict[str, Any]]:
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    def save(self, customers: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(customers, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
