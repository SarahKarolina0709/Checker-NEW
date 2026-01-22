"""quality_gui_upload_manager

Upload- & Dateiverwaltungs-Layer (Additiv). Ziel: Entkopplung von GUI.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import time
import os

@dataclass(slots=True)
class ManagedFile:
    path: Path
    kind: str  # 'source' | 'translation'
    size: int
    added_ts: float

@dataclass(slots=True)
class UploadStats:
    added: int = 0
    duplicates: int = 0
    skipped: int = 0
    total_size: int = 0

class QualityGuiUploadManager:
    def __init__(self):
        self._files: list[ManagedFile] = []
        self._by_kind: dict[str, list[ManagedFile]] = {'source': [], 'translation': []}
        # Letzte Projekt-Kopie Metadaten (für Diagnose / Tests)
        self._last_project_copy = None  # dict | None

    # -----------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------
    def _safe_resolve(self, p: Path) -> Path:
        try:
            return p.resolve(strict=False)
        except Exception:
            return p

    def _norm_key(self, p: Path) -> str:
        s = str(p)
        if os.name == "nt":
            return s.lower()
        try:
            import sys
            if sys.platform == "darwin":
                return s.lower()
        except Exception:
            pass
        return s

    def _rebuild_by_kind(self) -> None:
        self._by_kind = {'source': [], 'translation': []}
        for f in self._files:
            self._by_kind.setdefault(f.kind, []).append(f)

    # -----------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------
    def add_files(self, file_paths: list[str], kind: str) -> UploadStats:
        stats = UploadStats()
        # normalize set
        existing_paths = {self._norm_key(self._safe_resolve(mf.path)) for mf in self._files}

        for fp in file_paths:
            rp = self._safe_resolve(Path(fp))
            key = self._norm_key(rp)
            if key in existing_paths:
                stats.duplicates += 1
                continue
            try:
                size = rp.stat().st_size if rp.exists() else 0
            except Exception:
                size = 0
            mf = ManagedFile(path=rp, kind=kind, size=size, added_ts=time.time())
            self._files.append(mf)
            self._by_kind.setdefault(kind, []).append(mf)
            existing_paths.add(key)  # avoid intra-batch dupes
            stats.added += 1
            stats.total_size += size
        return stats

    def list_files(self, kind: Optional[str] = None) -> list[ManagedFile]:
        if kind:
            return list(self._by_kind.get(kind, []))
        return list(self._files)

    def clear(self):
        self._files.clear()
        self._by_kind = {'source': [], 'translation': []}
        self._last_project_copy = None

    # -----------------------------------------------------------
    # MUTATION HELPERS
    # -----------------------------------------------------------
    def remove_file(self, path: str) -> bool:
        key = self._norm_key(self._safe_resolve(Path(path)))
        removed = False
        try:
            new_files = []
            for f in self._files:
                if self._norm_key(f.path) == key:
                    removed = True
                else:
                    new_files.append(f)
            self._files = new_files
            self._rebuild_by_kind()
        except Exception:
            return False
        return removed

    def replace_file(self, old_path: str, new_path: str) -> bool:
        old_key = self._norm_key(self._safe_resolve(Path(old_path)))
        new_res = self._safe_resolve(Path(new_path))
        try:
            for mf in self._files:
                if self._norm_key(mf.path) == old_key:
                    mf.path = new_res
                    try:
                        mf.size = new_res.stat().st_size if new_res.exists() else 0
                    except Exception:
                        mf.size = 0
                    self._rebuild_by_kind()
                    return True
        except Exception:
            return False
        return False

    # -----------------------------------------------------------
    # PROJECT STRUCTURE COPY (Extrahiert aus main app - vereinfachte Variante)
    # -----------------------------------------------------------
    def copy_into_project_structure(
        self,
        files: list[str],
        create_structure: Callable[[str, str], str],
        get_paths: Callable[[str, str], dict],
        customer_name: str,
        project_date: str
    ) -> dict:
        """Kopiert Dateien in Projektstruktur (reine Logik, kein UI)."""
        import shutil, os

        copied = {'source': [], 'translation': [], 'other': [], 'errors': []}
        base_path = create_structure(customer_name, project_date)
        if not base_path:
            return copied

        paths = get_paths(customer_name, project_date) or {}
        ausgang = Path(paths.get('ausgangstext') or base_path)
        translation = Path(paths.get('translation') or base_path)
        for d in (Path(base_path), ausgang, translation):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        # quick map for known files → kind
        kind_by_key = {self._norm_key(mf.path): mf.kind for mf in self._files}

        for fp in files:
            try:
                src = self._safe_resolve(Path(fp))
                if not src.exists():
                    copied['errors'].append((str(src), 'not_exists'))
                    continue
                kind = kind_by_key.get(self._norm_key(src), 'source')
                target_dir = ausgang if kind == 'source' else translation
                target = target_dir / src.name
                shutil.copy2(str(src), str(target))
                copied[kind].append(str(target))
            except Exception as e:
                copied['errors'].append((fp, f'copy_failed:{e!s}'))

        self._last_project_copy = {'customer': customer_name, 'date': project_date, 'files': copied}
        return copied

__all__ = [
    'QualityGuiUploadManager',
    'ManagedFile',
    'UploadStats'
]
