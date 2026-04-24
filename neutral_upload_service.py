#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Neutral Upload Service (ehemals upload_service)

Kapselt Datei-Upload Logik (einfach + Batch) mit Events & Telemetrie.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any, Tuple, Union
import os


@dataclass
class UploadResult:
    kind: str  # 'source' | 'translation' | 'batch'
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

    # --------------------------- Simple Upload ---------------------------------
    def process_simple_upload(
        self,
        kind: str,
        selected_files: List[str],
        existing_files: List[str],
        customer_name: Optional[str] = None,
        copy_callback: Optional[Callable[[List[str], str], Dict[str, List[str]]]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> Dict[str, Any]:
        """Verarbeitet einfachen Upload (Source oder Translation) mit optionalem Fortschritts- und Cancel-Support.

        copy_callback: (files, customer_name) -> { 'ausgangstext': [kopierte Pfade] }
        progress_callback: (index, total, path) -> None  (index beginnt bei 1)
        cancel_check: () -> bool  gibt True zurück wenn Abbruch gewünscht
        """
        total = len(selected_files)
        self._publish('upload.started', {'kind': kind, 'count': total})
        result = UploadResult(kind=kind)
        try:
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

            project_copied = False
            if (not result.meta.get('cancelled')) and copy_callback and result.added_files:
                try:
                    copied = copy_callback(result.added_files, customer_name or '')
                    effective = copied.get('ausgangstext') or []
                    if effective:
                        result.meta['original_selected'] = list(result.added_files)
                        result.added_files = effective
                        project_copied = True
                except Exception as ce:
                    if self.logger:
                        self.logger.error("Fehler beim Kopieren in Projektstruktur: %s", ce)
                    result.meta['copy_error'] = str(ce)
            result.meta['project_copied'] = project_copied
            if result.meta.get('cancelled'):
                self._publish('upload.cancelled', {'kind': kind, 'added': len(result.added_files)})
            else:
                self._publish('upload.completed', {
                    'kind': kind,
                    'added': len(result.added_files),
                    'duplicates': len(result.duplicate_files),
                    'customer': customer_name,
                    'project_copied': project_copied,
                })
        except Exception as e:
            self._publish('upload.failed', {'kind': kind, 'error': str(e)})
            if self.logger:
                self.logger.error("Upload fehlgeschlagen (%s): %s", kind, e)
            result.meta['error'] = str(e)
        return result.to_dict()

    # --------------------------- Batch Upload ----------------------------------
    def process_batch_upload(
        self,
        selected_files: List[str],
        existing_source: List[str],
        existing_translation: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> Dict[str, Any]:
        total = len(selected_files)
        self._publish('upload.started', {'kind': 'batch', 'count': total})
        source_added: List[str] = []
        translation_added: List[str] = []
        duplicates: List[str] = []
        skipped: List[str] = []
        processed_details: List[Tuple[str, str]] = []  # (filename, role)
        cancelled = False
        try:
            for idx, path in enumerate(selected_files, start=1):
                if cancel_check and cancel_check():
                    cancelled = True
                    break
                filename = os.path.basename(path)
                # Stem ohne Extension fuer regex-Matching
                stem = os.path.splitext(filename)[0].lower()
                # Token-Match: Wortgrenzen verhindern False-Positives
                # (z.B. 'trans' soll NICHT in 'transparent', 'transfer', 'transaction' matchen)
                def _has_token(text: str, tokens: List[str]) -> bool:
                    import re as _re
                    for tok in tokens:
                        if _re.search(r'(?:^|[\W_])' + _re.escape(tok) + r'(?:$|[\W_])', text):
                            return True
                    return False
                is_translation = _has_token(stem, [
                    'translation', 'translated', 'trans', 'target',
                    'uebersetzung', 'übersetzung', 'übersetzt', 'uebersetzt',
                    'ziel', 'tgt',
                ])
                is_source = _has_token(stem, [
                    'source', 'original', 'src', 'quelle', 'ursprung',
                    'orig', 'source_language',
                ])
                if is_translation:
                    if path in existing_translation or path in translation_added:
                        duplicates.append(path)
                    else:
                        translation_added.append(path)
                        processed_details.append((filename, 'Translation'))
                elif is_source:
                    if path in existing_source or path in source_added:
                        duplicates.append(path)
                    else:
                        source_added.append(path)
                        processed_details.append((filename, 'Source'))
                else:
                    if path in existing_source or path in source_added:
                        duplicates.append(path)
                    else:
                        source_added.append(path)
                        processed_details.append((filename, 'Source (auto)'))
                if progress_callback:
                    try:
                        progress_callback(idx, total, path)
                    except Exception:
                        pass
        except Exception as e:
            if self.logger:
                self.logger.error("Batch Upload Fehler: %s", e)
            self._publish('upload.failed', {'kind': 'batch', 'error': str(e)})
        if cancelled:
            self._publish('upload.cancelled', {
                'kind': 'batch',
                'source_added': len(source_added),
                'translation_added': len(translation_added),
                'duplicates': len(duplicates),
            })
        else:
            self._publish('upload.completed', {
                'kind': 'batch',
                'source_added': len(source_added),
                'translation_added': len(translation_added),
                'duplicates': len(duplicates),
                'skipped': len(skipped),
            })
        return {
            'source_added': source_added,
            'translation_added': translation_added,
            'duplicates': duplicates,
            'skipped': skipped,
            'processed_details': processed_details,
            'cancelled': cancelled,
        }

    def _publish(self, topic: str, payload: Dict[str, Any]):
        if not self.event_bus:
            return
        try:
            self.event_bus.publish(topic, payload)
        except Exception:
            pass


_singleton: Optional[UploadService] = None


def get_upload_service(event_bus=None, logger=None) -> UploadService:
    global _singleton
    if _singleton is None:
        _singleton = UploadService(event_bus=event_bus, logger=logger)
    return _singleton

__all__ = ["UploadService", "UploadResult", "get_upload_service"]
