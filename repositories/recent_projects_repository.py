#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RecentProjectsRepository
========================
Speichert/liest eine flache Liste zuletzt geöffneter Projekte.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json

from paths import ROOT, RECENT_PROJECTS_FILE


class RecentProjectsRepository:
    def __init__(self, storage_path: Path | None = None, limit: int = 20):
        self.path = (storage_path or (ROOT / RECENT_PROJECTS_FILE))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.limit = limit

    def load(self) -> List[Dict[str, Any]]:
        try:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    def add(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = self.load()
        # Entferne Duplikate (nach Pfad)
        path = (project.get('path') or '').lower()
        items = [it for it in items if (it.get('path') or '').lower() != path]
        items.insert(0, project)
        if len(items) > self.limit:
            items = items[: self.limit]
        self.save(items)
        return items

    def save(self, items: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
