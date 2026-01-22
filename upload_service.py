#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEPRECATED WRAPPER

Ehemaliger Implementierungsort der Upload-Logik.
Neue neutrale Implementierung in neutral_upload_service.py

Behalte Import-Signaturen für Rückwärtskompatibilität bei.
"""
from __future__ import annotations

try:  # Prefer neue neutrale Implementierung
    from neutral_upload_service import (  # type: ignore
        UploadService,
        UploadResult,
        get_upload_service,
    )
    __all__ = ["UploadService", "UploadResult", "get_upload_service"]
except Exception:  # Minimaler Fallback (kein vollständiges Feature-Set)
    from dataclasses import dataclass, field
    from typing import List, Dict, Optional, Callable, Any, Tuple

    @dataclass
    class UploadResult:
        kind: str
        added_files: List[str] = field(default_factory=list)
        duplicate_files: List[str] = field(default_factory=list)
        skipped_files: List[str] = field(default_factory=list)
        meta: Dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> Dict[str, Any]:
            return {
                'kind': self.kind,
                'added_files': self.added_files,
                'duplicate_files': self.duplicate_files,
                'skipped_files': self.skipped_files,
                'meta': self.meta,
            }

    class UploadService:
        def __init__(self, event_bus=None, logger=None):
            self.event_bus = event_bus
            self.logger = logger

        def process_simple_upload(self, kind: str, selected_files: List[str], existing_files: List[str], customer_name: Optional[str] = None, copy_callback: Optional[Callable[[List[str], str], Dict[str, List[str]]]] = None, progress_callback: Optional[Callable[[int, int, str], None]] = None, cancel_check: Optional[Callable[[], bool]] = None) -> Dict[str, Any]:  # noqa: E501
            result = UploadResult(kind=kind)
            total = len(selected_files)
            for idx, path in enumerate(selected_files, start=1):
                if cancel_check and cancel_check():
                    result.meta['cancelled'] = True
                    break
                if path in existing_files:
                    result.duplicate_files.append(path)
                else:
                    result.added_files.append(path)
                if progress_callback:
                    try:
                        progress_callback(idx, total, path)
                    except Exception:
                        pass
            return result.to_dict()

        def process_batch_upload(self, selected_files: List[str], existing_source: List[str], existing_translation: List[str], progress_callback: Optional[Callable[[int, int, str], None]] = None, cancel_check: Optional[Callable[[], bool]] = None) -> Dict[str, Any]:  # noqa: E501
            source_added: List[str] = []
            translation_added: List[str] = []
            duplicates: List[str] = []
            skipped: List[str] = []
            processed_details: List[Tuple[str, str]] = []
            total = len(selected_files)
            for idx, path in enumerate(selected_files, start=1):
                if cancel_check and cancel_check():
                    break
                filename = path.split('/')[-1]
                lower = filename.lower()
                if 'trans' in lower or 'translation' in lower:
                    if path in existing_translation or path in translation_added:
                        duplicates.append(path)
                    else:
                        translation_added.append(path)
                        processed_details.append((filename, 'Translation'))
                else:
                    if path in existing_source or path in source_added:
                        duplicates.append(path)
                    else:
                        source_added.append(path)
                        processed_details.append((filename, 'Source'))
                if progress_callback:
                    try:
                        progress_callback(idx, total, path)
                    except Exception:
                        pass
            return {
                'source_added': source_added,
                'translation_added': translation_added,
                'duplicates': duplicates,
                'skipped': skipped,
                'processed_details': processed_details,
            }

    _singleton: Optional[UploadService] = None

    def get_upload_service(event_bus=None, logger=None) -> UploadService:  # type: ignore
        global _singleton
        if _singleton is None:
            _singleton = UploadService(event_bus=event_bus, logger=logger)
        return _singleton

    __all__ = ["UploadService", "UploadResult", "get_upload_service"]
