#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qualitäts-Framework -- NiceGUI Translation Quality Checker.

Single-file web application for professional translators.
Run:  python nicegui_app/main.py
"""
from __future__ import annotations

import asyncio
import calendar as _calendar_mod
import time
import json
import logging
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, date as _date_type
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import atexit
from nicegui import app, events, ui

# ---------------------------------------------------------------------------
# Temp directory & cleanup
# ---------------------------------------------------------------------------
_tmp_dir = tempfile.mkdtemp(prefix='qf_uploads_')
atexit.register(lambda: shutil.rmtree(_tmp_dir, ignore_errors=True))
app.on_shutdown(lambda: shutil.rmtree(_tmp_dir, ignore_errors=True))

# ---------------------------------------------------------------------------
# Optional OCR (Tesseract)
# ---------------------------------------------------------------------------
_HAS_OCR = False
try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None
try:
    import pytesseract  # type: ignore
    _HAS_OCR = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Backend imports
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quality_gui_pairing_manager import QualityGuiPairingManager  # noqa: E402
from neutral_upload_service import get_upload_service  # noqa: E402
from quality_gui_phase1_checkers import QAIssue, run_phase1_checks  # noqa: E402
from quality_gui_phase2_checkers import run_phase2_checks, _load_glossary  # noqa: E402
from quality_gui_phase3_checkers import run_phase3_checks  # noqa: E402

# Aufgespaltene Helfer-Module (siehe severity.py / text_extraction.py)
from nicegui_app import severity as _severity_mod  # noqa: E402
from nicegui_app import customers as _customers_mod  # noqa: E402
from nicegui_app import session as _session_mod  # noqa: E402
from nicegui_app import exports as _exports_mod  # noqa: E402
from nicegui_app.text_extraction import (  # noqa: E402
    extract_text as _extract_text_impl,
    finding_to_dict as _finding_to_dict_impl,
    dict_to_finding as _dict_to_finding_impl,
)

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Logging-Setup mit Rotation (max 5x10MB statt unbegrenzt wachsendem File)
# ---------------------------------------------------------------------------
def _setup_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root.handlers):
        return  # schon konfiguriert
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        fh = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8',
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        root.addHandler(fh)
        if root.level == logging.WARNING or root.level == logging.NOTSET:
            root.setLevel(logging.INFO)
    except Exception as exc:
        # Logging-Setup darf App-Start niemals blockieren
        print(f'[WARN] Log-Datei-Setup fehlgeschlagen: {exc}')


import logging.handlers  # noqa: E402  (vor _setup_logging benoetigt)
_setup_logging()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LANGUAGES = [
    'Auto-Erkennung', 'Deutsch', 'Englisch', 'Französisch', 'Spanisch',
    'Italienisch', 'Portugiesisch', 'Niederländisch', 'Polnisch',
    'Russisch', 'Chinesisch', 'Japanisch', 'Arabisch', 'Türkisch',
    'Rumänisch', 'Schwedisch', 'Tschechisch', 'Dänisch', 'Norwegisch',
    'Finnisch', 'Griechisch', 'Ungarisch', 'Koreanisch', 'Bulgarisch',
    'Ukrainisch',
]

LANG_CODE_MAP = {
    'Auto-Erkennung': 'auto', 'Deutsch': 'de', 'Englisch': 'en',
    'Französisch': 'fr', 'Spanisch': 'es', 'Italienisch': 'it',
    'Portugiesisch': 'pt', 'Niederländisch': 'nl', 'Polnisch': 'pl',
    'Russisch': 'ru', 'Chinesisch': 'zh', 'Japanisch': 'ja',
    'Arabisch': 'ar', 'Türkisch': 'tr', 'Rumänisch': 'ro',
    'Schwedisch': 'sv', 'Tschechisch': 'cs', 'Dänisch': 'da',
    'Norwegisch': 'no', 'Finnisch': 'fi', 'Griechisch': 'el',
    'Ungarisch': 'hu', 'Koreanisch': 'ko', 'Bulgarisch': 'bg',
    'Ukrainisch': 'uk',
}

# Deutsche Anzeige-Labels fuer die (intern englischen) Kategorie-Codes der
# Checker. Wird in der "Top-Kategorien"-Heatmap und in der Findings-Suche
# genutzt, damit die UI durchgaengig deutsch ist.
CATEGORY_LABELS_DE = {
    'completeness': 'Vollständigkeit',
    'consistency': 'Konsistenz',
    'formatting': 'Formatierung',
    'html': 'HTML & Tags',
    'metadata': 'Metadaten',
    'punctuation': 'Interpunktion',
    'quotes': 'Anführungszeichen',
    'readability': 'Lesbarkeit',
    'references': 'Verweise (URLs/E-Mail)',
    'risk': 'Risiko',
    'security': 'Sicherheit',
    'semantic': 'Bedeutung',
    'structure': 'Struktur',
    'style': 'Stil',
    'terminology': 'Terminologie',
    'typography': 'Typografie',
    'whitespace': 'Leerzeichen',
    'grammar': 'Grammatik',
    'numbers': 'Zahlen',
    'ocr': 'OCR-Erkennung',
    'ki_semantic': 'KI-Analyse',
    'Sonstige': 'Sonstige',
}


def category_label_de(cat: str) -> str:
    """Liefert das deutsche Anzeige-Label fuer einen Kategorie-Code.

    Unbekannte Codes werden lesbar formatiert (snake_case -> Titel).
    """
    if not cat:
        return 'Sonstige'
    key = cat.strip()
    if key in CATEGORY_LABELS_DE:
        return CATEGORY_LABELS_DE[key]
    low = key.lower()
    if low in CATEGORY_LABELS_DE:
        return CATEGORY_LABELS_DE[low]
    return key.replace('_', ' ').strip().capitalize()

ALLOWED_EXTENSIONS = {
    '.pdf', '.docx', '.txt', '.doc',
    '.png', '.jpg', '.jpeg', '.tiff', '.tif',
}

PROJECT_FOLDERS = _customers_mod.PROJECT_FOLDERS

MONTH_NAMES_DE = _customers_mod.MONTH_NAMES_DE

# Strenger Match fuer Monatsordner ("Maerz_2025", "Mai_2024"), damit Kunden-
# ordner wie "Maier_GmbH" nicht versehentlich als Monatsordner interpretiert
# werden (startswith('Mai') wuerde sonst matchen).
_MONTH_FOLDER_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(mn) for mn in MONTH_NAMES_DE.values()) + r')_\d{4}$'
)

_SOURCE_PATTERNS = re.compile(
    r'(?:_|\b)(?:de|deu|deutsch|german|ausgang(?:s(?:text)?)?|source|src|original|quelle|quell)'
    r'(?:_|\b|\.)', re.IGNORECASE)
_TRANSLATION_PATTERNS = re.compile(
    r'(?:_|\b)(?:en|eng|english|fr|fra|french|es|esp|spanish|it|ita|italian'
    r'|pt|por|nl|nld|pl|pol|ru|rus|zh|ja|ko|ar|tr|sv|da|fi|hu|ro|bg|uk|el'
    r'|translation|trans|tgt|target|ziel|uebersetzung|übersetzung|lektorat|korrektur)'
    r'(?:_|\b|\.)', re.IGNORECASE)

# ---------------------------------------------------------------------------
# CSS: strict design system
# ---------------------------------------------------------------------------
from nicegui_app.styles import APP_CSS as _APP_CSS  # noqa: E402


# ---------------------------------------------------------------------------
# Settings (loaded from checker_config.json)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Settings (loaded from checker_config.json)
# ---------------------------------------------------------------------------
from nicegui_app.app_settings import settings  # noqa: E402, F401


# ---------------------------------------------------------------------------
# Per-session state
# ---------------------------------------------------------------------------
def S() -> dict:
    """Return per-session state dict."""
    return app.storage.user


def _get_pairing_manager() -> QualityGuiPairingManager:
    return QualityGuiPairingManager()


# ---------------------------------------------------------------------------
# Helpers: cross-platform folder opener (delegated)
# ---------------------------------------------------------------------------
from nicegui_app.utils import (  # noqa: E402, F401
    safe_open_folder as _safe_open_folder,
    fmt_size as _fmt_size,
    html_esc as _html_esc,
    copy_to_clipboard as _copy_to_clipboard,
)
from nicegui_app.findings import finding_fingerprint as _finding_fingerprint  # noqa: E402, F401
from nicegui_app import ui_findings as _ui_findings  # noqa: E402
from nicegui_app import ui_dialogs as _ui_dialogs  # noqa: E402
from nicegui_app import analysis as _analysis  # noqa: E402
from nicegui_app import lang_detect as _lang_detect  # noqa: E402
from nicegui_app.text_extraction import get_text_stats as _ext_text_stats  # noqa: E402, F401


# ---------------------------------------------------------------------------
# Customer & project helpers (delegate to nicegui_app.customers)
# ---------------------------------------------------------------------------
def _get_customer_path(customer: str) -> str:
    return _customers_mod.get_customer_path(settings.get('projects_base_path', ''), customer)


def _display_name(folder_name: str) -> str:
    return _customers_mod.display_name(folder_name)


def _load_customers() -> List[str]:
    return _customers_mod.load_customers(settings.get('projects_base_path', ''))


def _ensure_project(customer: str, date_str: str = '') -> str:
    base = settings.get('projects_base_path', '')
    if not base:
        return ''
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    # Validierung Datum: tolerant gegen ungültige Eingaben → fallback auf heute
    try:
        parsed = datetime.strptime(date_str, '%Y-%m-%d')
        date_str = parsed.strftime('%Y-%m-%d')
        month_num = parsed.month
        year_str = parsed.strftime('%Y')
    except ValueError:
        _logger.warning('_ensure_project: ungültiges Datum %r → heute verwendet', date_str)
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        month_num = now.month
        year_str = now.strftime('%Y')
    # Sanitisiere Kundenname (verhindert Path-Traversal mit '/', '\', '..')
    safe_customer = _sanitize_folder_name(customer)
    month_name = MONTH_NAMES_DE.get(month_num, str(month_num))
    month_folder = f'{month_name}_{year_str}'
    folder_name = f'{date_str}_{safe_customer}'
    project_dir = os.path.join(base, month_folder, folder_name)
    for folder in PROJECT_FOLDERS:
        os.makedirs(os.path.join(project_dir, folder), exist_ok=True)
    info_path = os.path.join(project_dir, 'kundeninfo.json')
    if not os.path.exists(info_path):
        try:
            old_info = os.path.join(base, safe_customer, 'kundeninfo.json')
            if os.path.exists(old_info):
                shutil.copy2(old_info, info_path)
            else:
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump({'name': customer, 'typ': 'firma'}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    return project_dir


def _list_projects(customer: str) -> list:
    return _customers_mod.list_projects(settings.get('projects_base_path', ''), customer)


def _list_projects_full(customer: str) -> List[Tuple[str, str]]:
    return _customers_mod.list_projects_full(settings.get('projects_base_path', ''), customer)


def _get_project_path(customer: str, proj_name: str) -> str:
    return _customers_mod.get_project_path(settings.get('projects_base_path', ''), customer, proj_name)


def _find_source_folder(project_path: str) -> str:
    return _customers_mod.find_source_folder(project_path)


def _find_translation_folder(project_path: str) -> str:
    return _customers_mod.find_translation_folder(project_path)


def _count_files_in_folder(folder_path: str) -> int:
    return _customers_mod.count_files_in_folder(folder_path)


def _scan_project_dates() -> Dict[str, List[str]]:
    return _customers_mod.scan_project_dates(settings.get('projects_base_path', ''))


def _list_files_in_folder(folder_path: str) -> list:
    return _customers_mod.list_files_in_folder(folder_path)


def _get_project_folders(path: str) -> dict:
    return {f: os.path.join(path, f) for f in PROJECT_FOLDERS}


def _ensure_date_subfolder(customer: str, folder: str, date_str: str = '') -> str:
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    p = os.path.join(_get_customer_path(customer), date_str, folder)
    os.makedirs(p, exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Customer management
# ---------------------------------------------------------------------------
def _load_customer_info(customer: str) -> dict:
    info_path = os.path.join(_get_customer_path(customer), 'kundeninfo.json')
    try:
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_customer_info(customer: str, info: dict) -> bool:
    try:
        cpath = _get_customer_path(customer)
        os.makedirs(cpath, exist_ok=True)
        with open(os.path.join(cpath, 'kundeninfo.json'), 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        _logger.error('Kundeninfo speichern fehlgeschlagen: %s', e)
        return False


def _get_customer_glossary_path(customer: str) -> str:
    cpath = _get_customer_path(customer)
    for ext in ['csv', 'xlsx', 'json', 'tsv']:
        for name in [f'glossar.{ext}', f'glossary.{ext}', f'terminologie.{ext}']:
            p = os.path.join(cpath, name)
            if os.path.exists(p):
                return p
    gdir = os.path.join(cpath, 'glossar')
    if os.path.isdir(gdir):
        for f in os.listdir(gdir):
            if f.endswith(('.csv', '.xlsx', '.json', '.tsv')):
                return os.path.join(gdir, f)
    return ''


def _get_customer_stats(customer: str) -> dict:
    projects = _list_projects(customer)
    total_files = 0
    scores: list[int] = []
    for proj in projects:
        proj_path = _get_project_path(customer, proj)
        if not proj_path:
            proj_path = os.path.join(_get_customer_path(customer), proj)
        src = _find_source_folder(proj_path)
        tgt = _find_translation_folder(proj_path)
        total_files += _count_files_in_folder(src) + _count_files_in_folder(tgt)
        session_path = os.path.join(proj_path, 'session.json')
        try:
            if os.path.exists(session_path):
                with open(session_path, 'r', encoding='utf-8') as f:
                    sc = json.load(f).get('score', -1)
                    if sc >= 0:
                        scores.append(sc)
        except Exception:
            pass
    return {
        'auftraege': len(projects),
        'dateien': total_files,
        'letzter_auftrag': projects[0] if projects else '',
        'avg_score': round(sum(scores) / len(scores)) if scores else -1,
    }


def _toggle_customer_favorite(customer: str) -> bool:
    info = _load_customer_info(customer)
    info['favorit'] = not info.get('favorit', False)
    _save_customer_info(customer, info)
    return info['favorit']


def _archive_customer(customer: str) -> bool:
    return _customers_mod.archive_customer(settings.get('projects_base_path', ''), customer)


def _sanitize_folder_name(name: str) -> str:
    return _customers_mod.sanitize_folder_name(name)


# ---------------------------------------------------------------------------
# Session save / restore
# ---------------------------------------------------------------------------
def _get_session_path() -> str:
    return _session_mod.get_session_path(S().get('active_project_path', ''), _tmp_dir)


def _finding_to_dict(f: QAIssue) -> Dict[str, Any]:
    return _finding_to_dict_impl(f)


def _dict_to_finding(d: Dict[str, Any]) -> QAIssue:
    return _dict_to_finding_impl(d, QAIssue)


def _save_session():
    data = _session_mod.build_session_data(S())
    _session_mod.save_session(_get_session_path(), data)


def _load_session() -> Optional[Dict[str, Any]]:
    return _session_mod.load_session(
        S().get('active_project_path', ''),
        _tmp_dir,
        settings.get('projects_base_path', ''),
    )


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------
def extract_text(path: str) -> str:
    return _extract_text_impl(path)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def _build_text_pairs(paired_results: list) -> List[Tuple[str, str]]:
    """Baut Text-Paare aus Pairing-Ergebnissen. Darf NICHT auf app.storage zugreifen."""
    pairs: List[Tuple[str, str]] = []
    for pr in paired_results:
        src_path = pr.get('source', '')
        tgt_path = pr.get('translation', '')
        if src_path and tgt_path:
            src_text = extract_text(src_path)
            tgt_text = extract_text(tgt_path)
            if src_text.strip() and tgt_text.strip():
                pairs.append((src_text, tgt_text))
    return pairs


def _build_text_pairs_with_paths(
    paired_results: list,
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Wie _build_text_pairs, liefert zusätzlich parallele Liste mit File-Pfaden.

    Returns: (text_pairs, file_pairs) — gleiche Länge, gleicher Index.
    """
    text_pairs: List[Tuple[str, str]] = []
    file_pairs: List[Tuple[str, str]] = []
    for pr in paired_results:
        src_path = pr.get('source', '')
        tgt_path = pr.get('translation', '')
        if src_path and tgt_path:
            src_text = extract_text(src_path)
            tgt_text = extract_text(tgt_path)
            if src_text.strip() and tgt_text.strip():
                text_pairs.append((src_text, tgt_text))
                file_pairs.append((src_path, tgt_path))
    return text_pairs, file_pairs


def run_analysis_sync(config: Dict[str, Any]) -> List[QAIssue]:
    text_pairs = config.get('_text_pairs', [])
    if not text_pairs:
        return []
    all_findings: List[QAIssue] = []
    # Sprachcodes aufloesen: "Auto-Erkennung" (-> 'auto') wird hier aus den
    # tatsaechlichen Quell-/Zieltexten bestimmt, damit Phase 2/4 echte Codes
    # erhalten statt des Platzhalters 'auto'.
    raw_src = LANG_CODE_MAP.get(config.get('src_lang', ''), 'de')
    raw_tgt = LANG_CODE_MAP.get(config.get('tgt_lang', ''), 'en')
    src_texts = [p[0] for p in text_pairs if isinstance(p, (list, tuple)) and p]
    tgt_texts = [p[1] for p in text_pairs if isinstance(p, (list, tuple)) and len(p) > 1]
    src_code = _lang_detect.resolve_lang(raw_src, src_texts, 'de')
    tgt_code = _lang_detect.resolve_lang(raw_tgt, tgt_texts, 'en')
    if config.get('phase1'):
        try:
            all_findings.extend(run_phase1_checks(text_pairs))
        except Exception as exc:
            _logger.warning('Phase 1 Fehler: %s', exc)
    if config.get('phase2'):
        try:
            gp = config.get('glossary_path', '')
            ph2_cfg = {
                'src_lang': src_code,
                'tgt_lang': tgt_code,
            }
            all_findings.extend(run_phase2_checks(text_pairs, glossary_path=gp or 'glossary_terms.json', config=ph2_cfg))
        except Exception as exc:
            _logger.warning('Phase 2 Fehler: %s', exc)
    if config.get('phase3'):
        try:
            all_findings.extend(run_phase3_checks(text_pairs, enable_semantic=False))
        except Exception as exc:
            _logger.warning('Phase 3 Fehler: %s', exc)
    if config.get('phase4') and config.get('ollama_model'):
        try:
            from quality_gui_phase4_ki_checker import run_ki_checks
            all_findings.extend(run_ki_checks(
                text_pairs,
                src_lang=src_code,
                tgt_lang=tgt_code,
                ollama_model=config['ollama_model'],
            ))
        except Exception as exc:
            _logger.warning('Phase 4 KI Fehler: %s', exc)
    return all_findings


def compute_score(issues: List[QAIssue]) -> int:
    return _severity_mod.compute_score(issues)


def severity_label(sev: str) -> str:
    return _severity_mod.label(sev)


def severity_color(sev: str) -> str:
    return _severity_mod.color(sev)


def severity_border(sev: str) -> str:
    return _severity_mod.border(sev)


_PHASE_CODE_PREFIXES = {
    'Phase 1': (
        'URL_', 'EMAIL_', 'WS_', 'ZERO_WIDTH', 'BRACKET_', 'QUOTE_',
    ),
    'Phase 2': (
        'NUMBER_', 'NUM_', 'UNIT_', 'HTML_', 'PRONOUN_', 'DUPLICATE_',
        'S_CASE_', 'PUNCT_', 'SECURITY_', 'TERM_', 'TERMINOLOGY_',
        'COMPANY_', 'GLOSSARY_', 'NAME_',
    ),
    'Phase 3': (
        'STYLE_', 'RISK_', 'READABILITY_', 'READ_', 'SEMANTIC_',
        'GRAMMAR_', 'PASSIVE_',
    ),
    'Phase 4': (
        'KI_', 'OLLAMA_', 'CONSISTENCY_',
    ),
}


def phase_from_code(code: str) -> str:
    if not code:
        return ''
    # Legacy-Format P1_*/P2_*/P3_*/P4_*
    if code.startswith('P') and len(code) > 1 and code[1].isdigit():
        return f'Phase {code[1]}'
    # Mapping anhand Präfix
    for phase_label, prefixes in _PHASE_CODE_PREFIXES.items():
        if any(code.startswith(p) for p in prefixes):
            return phase_label
    return ''


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
def _save_upload(e: events.UploadEventArguments) -> Optional[str]:
    upload_file = getattr(e, 'file', e)
    raw_name = getattr(upload_file, 'name', '') or getattr(e, 'name', 'upload')
    # Schutz vor Path-Traversal: nur Basename verwenden, keine Verzeichnis-Anteile
    name = os.path.basename(str(raw_name).replace('\\', '/').split('/')[-1]) or 'upload'
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ui.notify(f'Dateityp {ext} nicht unterstützt', type='warning')
        return None
    dest = os.path.join(_tmp_dir, name)
    counter = 1
    while os.path.exists(dest):
        stem = Path(name).stem
        dest = os.path.join(_tmp_dir, f'{stem}_{counter}{ext}')
        counter += 1
    # NiceGUI: SmallFileUpload hat _data (bytes), LargeFileUpload hat _path (Datei).
    # Beide Varianten unterstützen, sonst werden große Dateien als leer gespeichert.
    data: bytes = b''
    raw_data = getattr(upload_file, '_data', None)
    if isinstance(raw_data, bytes):
        data = raw_data
    else:
        # LargeFileUpload Fallback: Datei direkt vom Pfad lesen
        path_attr = getattr(upload_file, '_path', None)
        if path_attr is not None:
            try:
                with open(path_attr, 'rb') as src_fh:
                    data = src_fh.read()
            except Exception as exc:
                _logger.warning('Upload-Lesen via _path fehlgeschlagen: %s', exc)
        # Ältere NiceGUI-Versionen / Tests: e.content
        if not data:
            content_attr = getattr(e, 'content', None)
            if isinstance(content_attr, bytes):
                data = content_attr
            elif content_attr is not None and hasattr(content_attr, 'read'):
                try:
                    data = content_attr.read()
                    if not isinstance(data, bytes):
                        data = b''
                except Exception:
                    data = b''
    if not data:
        ui.notify(f'Upload leer oder Lesen fehlgeschlagen: {name}', type='warning')
        return None
    with open(dest, 'wb') as f:
        f.write(data)
    return dest


def _detect_file_role(filename: str) -> str:
    name = filename.lower()
    src_score = len(_SOURCE_PATTERNS.findall(name))
    tgt_score = len(_TRANSLATION_PATTERNS.findall(name))
    if src_score > tgt_score:
        return 'source'
    if tgt_score > src_score:
        return 'translation'
    return 'unknown'


# ---------------------------------------------------------------------------
# Export functions (delegate to nicegui_app.exports)
# ---------------------------------------------------------------------------
def _collect_findings_objects() -> list:
    return [_dict_to_finding(fd) for fd in S().get('findings', [])]


def _export_txt() -> Optional[str]:
    findings = _collect_findings_objects()
    if not findings:
        ui.notify('Keine Ergebnisse zum Exportieren', type='warning')
        return None
    return _exports_mod.export_txt(findings, S().get('current_score', -1), _tmp_dir)


def _export_excel() -> Optional[str]:
    findings = _collect_findings_objects()
    if not findings:
        ui.notify('Keine Ergebnisse', type='warning')
        return None
    try:
        return _exports_mod.export_excel(findings, _tmp_dir)
    except ImportError:
        ui.notify('openpyxl nicht installiert', type='negative')
        return None


def _export_pdf() -> Optional[str]:
    findings = _collect_findings_objects()
    if not findings:
        ui.notify('Keine Ergebnisse', type='warning')
        return None
    try:
        return _exports_mod.export_pdf(findings, S().get('current_score', -1), _tmp_dir)
    except ImportError:
        ui.notify('reportlab nicht installiert', type='negative')
        return None


def _export_correction_package() -> Optional[str]:
    findings = _collect_findings_objects()
    if not findings:
        ui.notify('Keine Ergebnisse zum Exportieren', type='warning')
        return None
    s = S()
    result = _exports_mod.export_correction_package(
        findings,
        s.get('current_score', -1),
        list(s.get('source_files', [])),
        list(s.get('translation_files', [])),
        _tmp_dir,
    )
    if result is None:
        ui.notify('Export fehlgeschlagen', type='negative')
    return result


# ===========================================================================
# Main page
# ===========================================================================
@ui.page('/')
def index_page(kunde: str = '', auftrag: str = ''):
    s = app.storage.user
    for key, default in [
        ('source_files', []), ('translation_files', []), ('paired_results', []),
        ('findings', []), ('checked_findings', {}), ('glossary_path', None),
        ('manual_glossary_terms', {}), ('analysis_running', False),
        ('current_score', -1), ('last_score', -1), ('active_filter', 'all'), ('search_text', ''),
        ('hide_done', False), ('dark_mode', False), ('sort_mode', 'default'),
        ('show_category_heatmap', True), ('show_per_file_heatmap', True),
        ('view_mode', 'normal'),
        ('active_customer', ''), ('active_project_path', ''),
    ]:
        s.setdefault(key, default)

    # UI references (nonlocal-accessible)
    refs: Dict[str, Any] = {
        'src_container': None, 'tgt_container': None, 'pairing_label': None,
        'pairing_container': None, 'findings_container': None,
        'results_area': None, 'welcome_area': None, 'score_card': None,
        'summary_card': None, 'score_number': None, 'score_sublabel': None,
        'score_ring': None,  'score_delta': None,
        'critical_count': None, 'major_count': None, 'minor_count': None,
        'critical_count_pill': None, 'major_count_pill': None, 'minor_count_pill': None,
        'progress_bar': None, 'progress_text': None, 'start_btn': None,
        'export_row': None, 'export_btn': None, 'customer_info': None, 'auftrag_container': None,
        'auftrag_info': None, 'path_label': None, 'customer_search': None,
        'search_results': None, 'glossary_label': None,
        'src_lang_sel': None, 'tgt_lang_sel': None,
        'save_indicator': None, 'done_counter': None, 'history_chart': None,
        'category_heatmap': None, 'search_input': None, 'glossary_count_label': None,
        'per_file_heatmap': None, 'undo_btn': None, 'hide_done_toggle': None, 'compact_btn': None,
        'detail_panel': None,
        'diff_badge': None, 'done_progress_bar': None, 'done_progress_label': None,
        'score_time_label': None, 'header_score_badge': None, 'dark_btn': None,
        'search_counter': None, 'phase_score_row': None,
    }
    phase_flags = {'phase1': True, 'phase2': True, 'phase3': True, 'phase4': False}
    ollama_model = {'v': ''}
    filter_btns: Dict[str, Any] = {}
    selected_idx = {'v': -1}
    # Undo-Stack fuer 'Erledigt'-Aktionen (in-memory, max. 20 Schritte)
    undo_stack: List[Dict[str, Any]] = []

    # 'hide_done' Switch — separat damit Test-Restore möglich ist
    s.setdefault('score_history', [])

    def _save_and_notify():
        try:
            _save_session()
        except Exception:
            return
        ind = refs.get('save_indicator')
        if not ind:
            return
        try:
            ind.set_text(f'💾 Gespeichert {datetime.now().strftime("%H:%M:%S")}')
            ind.classes(add='visible')
            ui.timer(2.5, lambda: ind.classes(remove='visible'), once=True)
        except Exception:
            pass

    # Debounced Save (verhindert IO-Storm bei schnellen Klicks)
    _save_timer_holder: Dict[str, Any] = {'t': None}

    def _schedule_save(delay: float = 0.8):
        try:
            t_old = _save_timer_holder.get('t')
            if t_old is not None:
                try:
                    t_old.cancel()
                except Exception:
                    pass
            _save_timer_holder['t'] = ui.timer(
                delay, lambda: (_save_and_notify(), _save_timer_holder.update({'t': None})),
                once=True,
            )
        except Exception:
            # Fallback: synchron speichern
            _save_and_notify()

    # ------------------------------------------------------------------
    # File list refresh
    # ------------------------------------------------------------------
    def _get_text_stats(fp: str) -> dict:
        return _ext_text_stats(fp, settings.get('chars_per_norm_line', 36))

    def _render_file_row(fp: str, role: str):
        fname = os.path.basename(fp)
        fsize = _fmt_size(os.path.getsize(fp)) if os.path.exists(fp) else '?'
        stats = _get_text_stats(fp) if os.path.exists(fp) else {}
        color = 'var(--primary)' if role == 'source' else 'var(--success)'
        with ui.column().classes('w-full gap-0').style(
            'padding:8px 12px;background:var(--surface-alt);border:1px solid var(--surface-border);border-radius:6px;margin-bottom:4px;'
        ):
            with ui.row().classes('w-full items-center gap-2'):
                ui.icon('description' if role == 'source' else 'translate',
                         size='sm').style(f'color:{color}')
                ui.label(fname).style('font-size:var(--fs-md);font-weight:500;flex-grow:1;overflow:hidden;'
                                       'text-overflow:ellipsis;white-space:nowrap;')
                ui.label(fsize).style('font-size:var(--fs-sm);color:var(--text-muted);')
                ui.button(icon='swap_horiz',
                    on_click=lambda _, f=fp, r=role: _toggle_role(f, r),
                ).props('flat dense round size=xs').style(f'color:{color}').tooltip(
                    'Als Übersetzung verwenden' if role == 'source' else 'Als Ausgangstext verwenden'
                )
                ui.button(icon='close',
                          on_click=lambda _, f=fp, r=role: _remove_file(f, r)
                ).props('flat dense round size=xs').style('color:var(--text-light)').tooltip('Datei entfernen')
            if stats:
                with ui.row().classes('gap-4 pl-8'):
                    ui.label(f'{stats["chars"]:,} Zeichen'.replace(',', '.')).style(
                        'font-size:var(--fs-sm);color:var(--text-muted);')
                    ui.label(f'{stats["words"]:,} Wörter'.replace(',', '.')).style(
                        'font-size:var(--fs-sm);color:var(--text-muted);')
                    if role == 'source':
                        ui.label(f'{stats["norm_lines"]} NZ ({stats["cpl"]} Anschl.)').style(
                            'font-size:var(--fs-sm);color:var(--primary);font-weight:700;')

    def _refresh_file_list():
        _logger.info(f'_refresh_file_list: src={len(s.get("source_files",[]))}, tgt={len(s.get("translation_files",[]))}')
        _logger.info(f'  refs: src_container={refs["src_container"] is not None}, tgt_container={refs["tgt_container"] is not None}')
        for key, role, empty_msg in [
            ('src_container', 'source', 'Noch keine Ausgangstexte'),
            ('tgt_container', 'translation', 'Noch keine Übersetzungen'),
        ]:
            container = refs.get(key)
            if not container:
                _logger.warning(f'  Container {key} ist None — Dateien werden nicht angezeigt!')
                continue
            container.clear()
            file_key = 'source_files' if role == 'source' else 'translation_files'
            files = s.get(file_key, [])
            _logger.info(f'  {key}: {len(files)} Dateien')
            with container:
                for fp in files:
                    _render_file_row(fp, role)
                if not files:
                    with ui.column().classes('items-center gap-1').style('padding:10px 0;'):
                        ui.icon('upload_file').style(
                            'font-size:28px;color:var(--text-light);opacity:.35;')
                        ui.label(empty_msg).style(
                            'font-size:var(--fs-sm);color:var(--text-light);')
                        ui.label('Datei hierher ziehen oder unten hochladen').style(
                            'font-size:var(--fs-xs);color:var(--text-muted);')
                else:
                    # Kleiner "+ Weitere" Button statt große Drop-Zone
                    picker = refs.get('src_picker' if role == 'source' else 'tgt_picker')
                    def _pick(d=picker):
                        if d:
                            d.run_method('pickFiles')
                    ui.button('Weitere Dateien', icon='add',
                              on_click=_pick).props('flat dense no-caps size=sm').style(
                        'font-size:var(--fs-sm);color:var(--text-light);margin-top:4px;')
            # Drop-Zone verstecken wenn Dateien vorhanden
            drop_key = 'src_drop' if role == 'source' else 'tgt_drop'
            drop = refs.get(drop_key)
            if drop:
                drop.visible = not bool(files)

        # Gesamte Upload-Zone (inkl. Ueberschriften + Hinweis) ausblenden,
        # sobald irgendeine Datei vorhanden ist — verhindert verwaiste Labels.
        upl = refs.get('upload_area')
        if upl:
            has_any = bool(s.get('source_files') or s.get('translation_files'))
            upl.visible = not has_any

    def _toggle_role(fp: str, current_role: str):
        if current_role == 'source':
            src = list(s.get('source_files', []))
            if fp in src:
                src.remove(fp)
            s['source_files'] = src
            tgt = list(s.get('translation_files', []))
            tgt.append(fp)
            s['translation_files'] = tgt
        else:
            tgt = list(s.get('translation_files', []))
            if fp in tgt:
                tgt.remove(fp)
            s['translation_files'] = tgt
            src = list(s.get('source_files', []))
            src.append(fp)
            s['source_files'] = src
        _refresh_file_list()
        _do_autopairing()

    def _do_remove_file(fp: str, role: str):
        key = 'source_files' if role == 'source' else 'translation_files'
        lst = list(s.get(key, []))
        if fp in lst:
            lst.remove(fp)
        s[key] = lst
        # Falls die Datei als Kopie im aktiven Projektordner liegt: auch von
        # der Disk loeschen, sonst taucht sie beim naechsten Disk-Listing
        # (_refresh_project_folders) sofort wieder auf.
        proj_path = s.get('active_project_path', '')
        try:
            if proj_path and os.path.isfile(fp):
                ap_file = os.path.abspath(fp)
                ap_proj = os.path.abspath(proj_path)
                if os.path.commonpath([ap_file, ap_proj]) == ap_proj:
                    os.remove(fp)
        except Exception:
            pass
        # Betroffene Paare entfernen
        s['paired_results'] = [
            p for p in s.get('paired_results', [])
            if p.get('source') != fp and p.get('translation') != fp
        ]
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        _refresh_results_area()

    def _file_is_on_disk_in_project(fp: str) -> bool:
        """True, wenn fp eine echte Datei im aktiven Projektordner ist
        (Entfernen wuerde sie unwiderruflich von der Disk loeschen)."""
        proj_path = s.get('active_project_path', '')
        try:
            if proj_path and os.path.isfile(fp):
                ap_file = os.path.abspath(fp)
                ap_proj = os.path.abspath(proj_path)
                return os.path.commonpath([ap_file, ap_proj]) == ap_proj
        except Exception:
            pass
        return False

    def _exclude_file(fp: str, role: str):
        """Datei nur von der Pruefung ausschliessen — bleibt auf der Disk."""
        key = 'source_files' if role == 'source' else 'translation_files'
        lst = list(s.get(key, []))
        if fp in lst:
            lst.remove(fp)
        s[key] = lst
        ex = list(s.get('excluded_files', []))
        if fp not in ex:
            ex.append(fp)
        s['excluded_files'] = ex
        s['paired_results'] = [
            p for p in s.get('paired_results', [])
            if p.get('source') != fp and p.get('translation') != fp
        ]
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        _refresh_results_area()

    def _include_file(fp: str, role: str):
        """Zuvor ausgeschlossene Datei wieder zur Pruefung aufnehmen."""
        s['excluded_files'] = [e for e in s.get('excluded_files', []) if e != fp]
        key = 'source_files' if role == 'source' else 'translation_files'
        lst = list(s.get(key, []))
        if fp not in lst and os.path.isfile(fp):
            lst.append(fp)
        s[key] = lst
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        _refresh_results_area()

    def _remove_file(fp: str, role: str):
        # Datei nicht im Projektordner (z.B. frischer Upload): einfach aus der
        # Pruefliste nehmen, hier entsteht kein Datenverlust auf der Disk.
        if not _file_is_on_disk_in_project(fp):
            _do_remove_file(fp, role)
            return
        fname = os.path.basename(fp)
        # Ausschliessen ist nur sinnvoll, wenn die Datei aktuell geprueft wird
        # (Ausgangstext / Uebersetzung). Andere Ordner (Korrektur etc.) bieten
        # nur das Loeschen an.
        key = 'source_files' if role == 'source' else 'translation_files'
        can_exclude = role in ('source', 'translation') and fp in s.get(key, [])

        def _do_exclude():
            dlg.close()
            _exclude_file(fp, role)
            ui.notify(f'„{fname}" von der Prüfung ausgeschlossen', type='info')

        def _confirm():
            dlg.close()
            _do_remove_file(fp, role)
            ui.notify(f'„{fname}" gelöscht', type='warning')

        with ui.dialog() as dlg, ui.card().classes('q-pa-none').style(
            'width:460px;border-radius:14px;overflow:hidden;'):
            # Kopfbereich
            with ui.column().classes('w-full gap-1').style('padding:20px 22px 4px;'):
                with ui.row().classes('w-full items-center gap-2'):
                    ui.icon('help_outline' if can_exclude else 'warning',
                            size='sm').style(
                        f'color:{"var(--primary)" if can_exclude else "var(--error)"};')
                    ui.label('Datei entfernen' if can_exclude else 'Datei löschen?').style(
                        'font-size:var(--fs-lg);font-weight:700;color:var(--text);')
                ui.label(
                    f'Was möchtest du mit „{fname}" tun?' if can_exclude
                    else f'„{fname}" wird endgültig aus dem Projektordner gelöscht. '
                         'Das kann nicht rückgängig gemacht werden.'
                ).style('font-size:var(--fs-sm);color:var(--text-muted);'
                        'overflow:hidden;text-overflow:ellipsis;')

            if can_exclude:
                with ui.column().classes('w-full gap-2').style('padding:14px 22px 6px;'):
                    # Option 1 — Ausschliessen (klickbare Karte)
                    with ui.row().classes(
                        'w-full items-center gap-3 choice-card no-wrap'
                    ).style('padding:12px 14px;').on('click', _do_exclude):
                        ui.icon('visibility_off', size='sm').style(
                            'color:var(--primary);')
                        with ui.column().classes('gap-0 flex-grow min-w-0'):
                            ui.label('Nur von der Prüfung ausschließen').style(
                                'font-size:var(--fs-sm);font-weight:600;color:var(--text);')
                            ui.label('Datei bleibt im Projektordner erhalten und kann '
                                     'jederzeit wieder aufgenommen werden.').style(
                                'font-size:var(--fs-xs);color:var(--text-muted);')
                        ui.icon('chevron_right', size='sm').classes('choice-go')
                    # Option 2 — Endgueltig loeschen (klickbare Karte)
                    with ui.row().classes(
                        'w-full items-center gap-3 choice-card choice-card-danger no-wrap'
                    ).style('padding:12px 14px;').on('click', _confirm):
                        ui.icon('delete_forever', size='sm').style('color:var(--error);')
                        with ui.column().classes('gap-0 flex-grow min-w-0'):
                            ui.label('Endgültig vom Datenträger löschen').style(
                                'font-size:var(--fs-sm);font-weight:600;color:var(--error);')
                            ui.label('Die Datei wird unwiderruflich aus dem '
                                     'Projektordner gelöscht.').style(
                                'font-size:var(--fs-xs);color:var(--text-muted);')
                        ui.icon('chevron_right', size='sm').classes('choice-go')
                with ui.row().classes('w-full justify-end').style('padding:8px 22px 18px;'):
                    ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
            else:
                with ui.row().classes('w-full justify-end gap-2').style(
                    'padding:14px 22px 18px;'):
                    ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
                    ui.button('Löschen', icon='delete_forever', on_click=_confirm).props(
                        'no-caps unelevated color=negative')
        dlg.open()

    # ------------------------------------------------------------------
    # Auto-pairing
    # ------------------------------------------------------------------
    def _do_autopairing():
        _logger.info(f'_do_autopairing: src={len(s.get("source_files",[]))}, tgt={len(s.get("translation_files",[]))}')
        _logger.info(f'  pairing_label={refs.get("pairing_label") is not None}, pairing_container={refs.get("pairing_container") is not None}')
        if s['source_files'] and s['translation_files']:
            pairs_list, unmatched = _get_pairing_manager().run_smart_pairing(
                s['source_files'], s['translation_files'])
            s['paired_results'] = pairs_list
            s['unmatched_src'] = unmatched.get('source', []) if isinstance(unmatched, dict) else []
            s['unmatched_tgt'] = unmatched.get('translation', []) if isinstance(unmatched, dict) else []
            # Fallback: Wenn keine Paare aber je genau 1 Datei → paare sie
            if not pairs_list and len(s['source_files']) == 1 and len(s['translation_files']) == 1:
                s['paired_results'] = [{'source': s['source_files'][0], 'translation': s['translation_files'][0]}]
                s['unmatched_src'] = []
                s['unmatched_tgt'] = []
        else:
            s['paired_results'] = []
            s['unmatched_src'] = []
            s['unmatched_tgt'] = []
        _refresh_pairing_display()

    def _refresh_pairing_display():
        n = len(s.get('paired_results', []))
        n_unmatched = len(s.get('unmatched_src', [])) + len(s.get('unmatched_tgt', []))
        if refs['pairing_label']:
            if n:
                text = f'{n} Paar{"e" if n != 1 else ""}'
                if n_unmatched:
                    text += f' · {n_unmatched} ohne Partner'
                refs['pairing_label'].set_text(text)
            elif s.get('source_files') and s.get('translation_files'):
                refs['pairing_label'].set_text('Keine passenden Paare')
            else:
                refs['pairing_label'].set_text('')
        container = refs['pairing_container']
        if not container:
            return
        container.clear()
        pairs = s.get('paired_results', [])
        with container:
            if n_unmatched > 0:
                with ui.element('div').style(
                    'width:100%;border-radius:6px;background:var(--bg-warning-tint);'
                    'border:1px solid var(--border-warning);padding:8px 12px;margin-bottom:8px;'
                ):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('warning', size='xs').style('color:var(--warning)')
                        ui.label(f'{n_unmatched} Datei{"en" if n_unmatched != 1 else ""} ohne Partner'
                        ).style('font-size:var(--fs-sm);font-weight:600;color:var(--warning-text);flex-grow:1;')
                        ui.button('Zuordnen', icon='tune',
                                  on_click=_show_pairing_dialog).props(
                            'flat dense no-caps size=xs color=orange')
            for p in pairs[:5]:
                src_name = os.path.basename(p.get('source', ''))
                tgt_name = os.path.basename(p.get('translation', ''))
                with ui.row().classes('w-full items-center gap-1').style('padding:2px 0;'):
                    ui.icon('check_circle', size='xs').style('color:var(--success)')
                    ui.label(src_name).style('font-size:var(--fs-sm);color:var(--text-muted);flex-grow:1;'
                                              'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                    ui.icon('arrow_forward', size='xs').style('color:var(--text-light)')
                    ui.label(tgt_name).style('font-size:var(--fs-sm);color:var(--text-muted);flex-grow:1;'
                                              'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
            if len(pairs) > 5:
                ui.label(f'+ {len(pairs)-5} weitere Paare').style('font-size:var(--fs-sm);color:var(--text-light);')
            for fp in s.get('unmatched_src', [])[:3] + s.get('unmatched_tgt', [])[:3]:
                with ui.row().classes('w-full items-center gap-1').style('padding:2px 0;'):
                    ui.icon('help_outline', size='xs').style('color:var(--warning)')
                    ui.label(os.path.basename(fp)).style('font-size:var(--fs-sm);color:var(--warning);')
                    ui.label('kein Partner').style('font-size:var(--fs-sm);color:var(--text-light);')
            if pairs or s.get('unmatched_src') or s.get('unmatched_tgt'):
                ui.button('Paarung anpassen', icon='tune',
                          on_click=_show_pairing_dialog).props(
                    'flat dense no-caps size=xs').style('font-size:var(--fs-sm);margin-top:4px;')

    def _show_pairing_dialog():
        def _after_pairing():
            _refresh_pairing_display()
            try:
                _refresh_project_folders()
            except Exception:
                pass
            try:
                _refresh_results_area()
            except Exception:
                pass
        ctx = SimpleNamespace(
            s=s,
            refresh_pairing_display=_after_pairing,
            update_start_btn=_update_start_btn,
        )
        _ui_dialogs.show_pairing_dialog(ctx)

    # ------------------------------------------------------------------
    # Upload handlers
    # ------------------------------------------------------------------
    def _copy_to_customer_folder(file_path: str, subfolder: str) -> str:
        customer = s.get('active_customer', '')
        if not customer:
            return file_path
        active_path = s.get('active_project_path', '')
        if active_path and os.path.isdir(active_path):
            target_dir = os.path.join(active_path, subfolder)
        else:
            today = datetime.now().strftime('%Y-%m-%d')
            project_path = _ensure_project(customer, today)
            target_dir = os.path.join(project_path, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        dest = os.path.join(target_dir, os.path.basename(file_path))
        if os.path.exists(dest):
            stem, ext = os.path.splitext(os.path.basename(file_path))
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(target_dir, f'{stem}_{counter}{ext}')
                counter += 1
        try:
            shutil.copy2(file_path, dest)
            return dest
        except Exception:
            return file_path

    def _add_file(fp: str, role: str):
        key = 'source_files' if role == 'source' else 'translation_files'
        lst = list(s.get(key, []))
        lst.append(fp)
        s[key] = lst

    def _handle_source_upload(e: events.UploadEventArguments):
        path = _save_upload(e)
        if not path:
            return
        dest = _copy_to_customer_folder(path, '01_Ausgangstext') if s.get('active_customer') else path
        _add_file(dest, 'source')
        ui.notify(f'Ausgangstext: {os.path.basename(dest)}', type='positive')
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        _try_refresh_auftrag()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        _refresh_results_area()

    def _handle_translation_upload(e: events.UploadEventArguments):
        path = _save_upload(e)
        if not path:
            return
        dest = _copy_to_customer_folder(path, '02_Übersetzung') if s.get('active_customer') else path
        _add_file(dest, 'translation')
        ui.notify(f'Übersetzung: {os.path.basename(dest)}', type='positive')
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        _try_refresh_auftrag()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        _refresh_results_area()

    def _show_role_dialog(path: str, fname: str):
        with ui.dialog() as dlg, ui.card().style('width:400px;'):
            ui.label(f'Datei zuordnen: {fname}').classes('t-heading')
            ui.label('Die Datei konnte nicht automatisch zugeordnet werden.').style(
                'font-size:var(--fs-sm);color:var(--text-muted);')
            with ui.row().classes('w-full justify-center gap-4').style('margin-top:12px;'):
                def _assign(role):
                    dest = _copy_to_customer_folder(path, '01_Ausgangstext' if role == 'source' else '02_Übersetzung') if s.get('active_customer') else path
                    _add_file(dest, role)
                    dlg.close()
                    _refresh_file_list()
                    _do_autopairing()
                    _update_start_btn()
                ui.button('Ausgangstext', icon='description',
                          on_click=lambda: _assign('source')).props('no-caps outline')
                ui.button('Übersetzung', icon='translate',
                          on_click=lambda: _assign('translation')).props('no-caps color=green outline')
        dlg.open()

    def _handle_file_upload(e: events.UploadEventArguments):
        path = _save_upload(e)
        if not path:
            return
        role = _detect_file_role(os.path.basename(path))
        if role == 'source':
            dest = _copy_to_customer_folder(path, '01_Ausgangstext') if s.get('active_customer') else path
            _add_file(dest, 'source')
            ui.notify(f'Ausgangstext erkannt: {os.path.basename(path)}', type='positive')
        elif role == 'translation':
            dest = _copy_to_customer_folder(path, '02_Übersetzung') if s.get('active_customer') else path
            _add_file(dest, 'translation')
            ui.notify(f'Übersetzung erkannt: {os.path.basename(path)}', type='positive')
        else:
            _show_role_dialog(path, os.path.basename(path))
            return
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        _try_refresh_auftrag()

    def _try_refresh_auftrag():
        try:
            _refresh_auftrag_list()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Customer selection
    # ------------------------------------------------------------------
    def _on_customer_selected(value: str):
        if not value:
            s['active_customer'] = ''
            s['active_project_path'] = ''
            _refresh_customer_info()
            return
        # Kunde ist gültig wenn er Projekte hat ODER einen eigenen Ordner
        cpath = _get_customer_path(value)
        projects = _list_projects(value)
        if not os.path.isdir(cpath) and not projects:
            ui.notify(f'Kunde „{value}" hat noch keine Projekte', type='info')
        s['active_customer'] = value
        s['active_project_path'] = ''  # Kein Projekt vorausgewählt
        glossary_path = _get_customer_glossary_path(value)
        if glossary_path:
            s['glossary_path'] = glossary_path
            if refs['glossary_label']:
                refs['glossary_label'].set_text(os.path.basename(glossary_path))
            ui.notify(f'Glossar geladen: {os.path.basename(glossary_path)}', type='positive')
        _refresh_auftrag_list()
        _refresh_customer_info()
        _refresh_results_area()
        try:
            _refresh_project_folders()
        except Exception:
            pass

    def _refresh_customer_info():
        container = refs['customer_info']
        if not container:
            return
        container.clear()
        customer = s.get('active_customer', '')
        if not customer:
            return
        info = _load_customer_info(customer)
        stats = _get_customer_stats(customer)
        is_fav = info.get('favorit', False)
        with container:
            with ui.element('div').style(
                'width:100%;border-radius:6px;border:1px solid var(--surface-border);'
                'background:var(--surface-alt);padding:8px;margin-top:4px;'
            ):
                with ui.row().classes('w-full items-center gap-1'):
                    typ = info.get('typ', 'firma')
                    ui.icon('business' if typ == 'firma' else 'person', size='xs').style('color:var(--text-muted)')
                    ui.label(customer).style('font-size:var(--fs-sm);font-weight:600;color:var(--text);flex-grow:1;')
                    ui.button(icon='star' if is_fav else 'star_border',
                              on_click=lambda: (_toggle_customer_favorite(customer), _refresh_customer_info())
                    ).props('flat dense round size=xs').style(
                        f'color:{"var(--accent)" if is_fav else "var(--surface-border-strong)"}')
                    ui.button(icon='edit',
                              on_click=lambda: _show_edit_customer_dialog(customer)
                    ).props('flat dense round size=xs').style('color:var(--text-light)')
                    ui.button(icon='folder_open',
                              on_click=lambda: _safe_open_folder(_get_customer_path(customer))
                    ).props('flat dense round size=xs').style('color:var(--text-light)')
                contact = []
                if info.get('ansprechpartner'):
                    contact.append(info['ansprechpartner'])
                if info.get('email'):
                    contact.append(info['email'])
                if contact:
                    ui.label(' · '.join(contact)).style(
                        'font-size:var(--fs-sm);color:var(--text-light);padding-left:24px;')
                with ui.row().classes('gap-4').style('padding-left:24px;margin-top:4px;'):
                    ui.label(f'{stats["auftraege"]} Aufträge').style('font-size:var(--fs-sm);color:var(--text-muted);')
                    ui.label(f'{stats["dateien"]} Dateien').style('font-size:var(--fs-sm);color:var(--text-muted);')
                    if stats['avg_score'] >= 0:
                        clr = 'var(--success)' if stats['avg_score'] >= 80 else 'var(--warning)' if stats['avg_score'] >= 50 else 'var(--error)'
                        ui.label(f'Durchschnitt {stats["avg_score"]} Punkte').style(
                            f'font-size:var(--fs-sm);font-weight:600;color:{clr};')

    def _show_edit_customer_dialog(customer: str):
        ctx = SimpleNamespace(
            s=s,
            load_customer_info=_load_customer_info,
            save_customer_info=_save_customer_info,
            archive_customer=_archive_customer,
            refresh_customer_info=_refresh_customer_info,
        )
        _ui_dialogs.show_edit_customer_dialog(ctx, customer)

    def _archive_confirm(customer: str, parent_dlg):
        ctx = SimpleNamespace(
            s=s,
            archive_customer=_archive_customer,
            refresh_customer_info=_refresh_customer_info,
        )
        _ui_dialogs.show_archive_confirm(ctx, customer, parent_dlg)

    def _show_new_customer_dialog():
        ctx = SimpleNamespace(finalize_new_customer=_finalize_new_customer)
        _ui_dialogs.show_new_customer_dialog(ctx)

    def _finalize_new_customer(name: str, info: dict):
        base = settings.get('projects_base_path', '')
        if not base:
            ui.notify('Projektbasispfad nicht konfiguriert', type='warning')
            return
        folder_name = _sanitize_folder_name(name)
        info['display_name'] = name
        info['folder_name'] = folder_name
        customer_path = _ensure_project(folder_name)
        if info:
            try:
                with open(os.path.join(customer_path, 'kundeninfo.json'), 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        s['active_customer'] = folder_name
        s['active_project_path'] = customer_path
        if refs['customer_search']:
            refs['customer_search'].value = ''
        _on_customer_selected(folder_name)
        ui.notify(f'Kunde "{name}" angelegt', type='positive')

    # ------------------------------------------------------------------
    # Start button
    # ------------------------------------------------------------------
    def _update_start_btn():
        btn = refs['start_btn']
        if btn:
            has_src = bool(s.get('source_files'))
            has_tgt = bool(s.get('translation_files'))
            has_pairs = bool(s.get('paired_results'))
            if has_src and has_tgt and has_pairs:
                btn.enable()
                btn.tooltip('Tastenkürzel: Strg+Enter')
                btn.props(remove='color')
            elif not has_src and not has_tgt:
                btn.disable()
                btn.tooltip('Bitte zuerst Ausgangstext und Übersetzung hochladen')
            elif not has_src:
                btn.disable()
                btn.tooltip('Ausgangstext fehlt — bitte hochladen')
            elif not has_tgt:
                btn.disable()
                btn.tooltip('Übersetzung fehlt — bitte hochladen')
            else:
                btn.disable()
                btn.tooltip('Keine Dateipaare erkannt — Pairing prüfen')

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------
    def _snapshot_previous_findings():
        """Sichert den letzten Findings-Stand vor einer Re-Analyse."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _analysis.snapshot_previous_findings(s, repo_root)

    def _request_cancel():
        if s.get('analysis_running'):
            s['cancel_requested'] = True
            ui.notify('Analyse wird nach aktueller Phase abgebrochen...', type='info')

    async def _start_analysis():
        if s.get('analysis_running'):
            ui.notify('Analyse laeuft bereits', type='warning')
            return
        if not s.get('paired_results'):
            ui.notify('Keine Dateipaare vorhanden', type='warning')
            return
        # Snapshot des bisherigen Laufs vor dem Reset (verhindert Datenverlust)
        try:
            _snapshot_previous_findings()
        except Exception as exc:
            _logger.debug('Findings-Snapshot fehlgeschlagen: %s', exc)
        # Fingerprints des vorherigen Laufs fuer Diff merken
        prev_fps = {_finding_fingerprint(fd) for fd in (s.get('findings', []) or [])}
        s['_prev_fingerprints'] = list(prev_fps)
        s['analysis_running'] = True
        s['cancel_requested'] = False
        s['findings'] = []
        s['checked_findings'] = {}
        s['current_score'] = -1
        s['active_filter'] = 'all'
        s['search_text'] = ''
        selected_idx['v'] = -1
        if refs['start_btn']:
            refs['start_btn'].disable()
            refs['start_btn'].set_text('Analyse läuft…')
            refs['start_btn'].props('icon=hourglass_empty')
        if refs.get('cancel_btn'):
            refs['cancel_btn'].visible = True
        if refs['progress_bar']:
            refs['progress_bar'].visible = True
            refs['progress_bar'].value = 0
        if refs['progress_text']:
            refs['progress_text'].visible = True
            refs['progress_text'].set_text('Texte werden gelesen…')
        _refresh_results_area()
        # paired_results im UI-Thread lesen (app.storage.user nur hier zulaessig),
        # die teure Text-Extraktion (DOCX/PDF/OCR) aber im Executor ausfuehren —
        # sonst blockiert sie den Eventloop und der Browser zeigt "Connection lost".
        _pairs_snapshot = list(s.get('paired_results', []))
        loop = asyncio.get_event_loop()
        text_pairs, file_pairs = await loop.run_in_executor(
            None, _build_text_pairs_with_paths, _pairs_snapshot)
        if not text_pairs:
            ui.notify('Keine Textpaare gefunden — Dateien korrekt gepaart?', type='warning')
            s['analysis_running'] = False
            if refs['start_btn']:
                refs['start_btn'].enable()
            return
        config = {
            'phase1': phase_flags.get('phase1', True),
            'phase2': phase_flags.get('phase2', True),
            'phase3': phase_flags.get('phase3', True),
            'phase4': phase_flags.get('phase4', False),
            'glossary_path': s.get('glossary_path') or '',
            'ollama_model': ollama_model['v'] or '',
            'src_lang': refs['src_lang_sel'].value if refs['src_lang_sel'] else 'Auto-Erkennung',
            'tgt_lang': refs['tgt_lang_sel'].value if refs['tgt_lang_sel'] else 'Auto-Erkennung',
            '_text_pairs': text_pairs,  # Vorab gelesen für Thread-Sicherheit
        }
        phases = []
        if config['phase1']:
            phases.append(('Phase 1: Zahlen & Formate', 'phase1'))
        if config['phase2']:
            phases.append(('Phase 2: Inhalt & Konsistenz', 'phase2'))
        if config['phase3']:
            phases.append(('Phase 3: Grammatik & Stil', 'phase3'))
        if config['phase4']:
            phases.append(('Phase 4: KI-Analyse', 'phase4'))
        total = len(phases) or 1
        n_pairs = len(text_pairs)
        loop = asyncio.get_event_loop()
        all_results: List[QAIssue] = []
        analysis_start = time.monotonic()
        phase_durations: List[float] = []
        phase_finding_counts: Dict[str, int] = {}

        def _fmt_eta(seconds: float) -> str:
            if seconds < 1:
                return '<1s'
            if seconds < 60:
                return f'{seconds:.0f}s'
            mins, secs = divmod(int(seconds), 60)
            return f'{mins}:{secs:02d} min'

        for idx, (phase_name, phase_key) in enumerate(phases):
            if s.get('cancel_requested'):
                break
            phase_start = time.monotonic()
            # ETA aus bisherigen Phasen-Mittelwert
            eta_str = ''
            if phase_durations:
                avg = sum(phase_durations) / len(phase_durations)
                remaining = avg * (total - idx)
                eta_str = f' · noch ~{_fmt_eta(remaining)}'
            if refs['progress_text']:
                phase_dots = '●' * (idx + 1) + '○' * (total - idx - 1)
                refs['progress_text'].set_text(
                    f'{phase_dots}  {phase_name}{eta_str}'
                )
            if refs['progress_bar']:
                refs['progress_bar'].value = idx / total
            await asyncio.sleep(0.05)
            single = {k: False for k in ('phase1', 'phase2', 'phase3', 'phase4')}
            single[phase_key] = True
            single['glossary_path'] = config['glossary_path']
            single['ollama_model'] = config['ollama_model']
            single['src_lang'] = config['src_lang']
            single['tgt_lang'] = config['tgt_lang']
            phase_count = 0
            try:
                if phase_key == 'phase4' and n_pairs > 1:
                    # KI-Analyse pro Datei iterieren fuer feineren Fortschritt
                    for fi, pair in enumerate(text_pairs):
                        if s.get('cancel_requested'):
                            break
                        if refs['progress_text']:
                            refs['progress_text'].set_text(
                                f'{n_pairs} Dateipaar(e) · Phase {idx + 1}/{total} · {phase_name} · '
                                f'Datei {fi + 1}/{n_pairs}{eta_str}'
                            )
                        if refs['progress_bar']:
                            refs['progress_bar'].value = (idx + (fi / n_pairs)) / total
                        await asyncio.sleep(0)
                        single_pair = dict(single)
                        single_pair['_text_pairs'] = [pair]
                        try:
                            sub = await loop.run_in_executor(None, run_analysis_sync, single_pair)
                            # segment_index korrigieren (Datei-Pfad-Attribution spaeter)
                            for finding in sub:
                                try:
                                    finding.segment_index = fi
                                except Exception:
                                    pass
                            phase_count += len(sub)
                            all_results.extend(sub)
                        except Exception as exc:
                            _logger.warning('Phase 4 Datei %d fehlgeschlagen: %s', fi + 1, exc)
                else:
                    single['_text_pairs'] = text_pairs
                    result = await loop.run_in_executor(None, run_analysis_sync, single)
                    phase_count = len(result)
                    all_results.extend(result)
            except Exception as exc:
                _logger.warning('%s fehlgeschlagen: %s', phase_name, exc)
            elapsed = time.monotonic() - phase_start
            phase_durations.append(elapsed)
            phase_finding_counts[phase_key] = phase_count
            if refs['progress_text']:
                refs['progress_text'].set_text(
                    f'{n_pairs} Dateipaar(e) · Phase {idx + 1}/{total} · {phase_name} · '
                    f'{phase_count} Findings · {elapsed:.1f}s'
                )
            if refs['progress_bar']:
                refs['progress_bar'].value = (idx + 1) / total
            await asyncio.sleep(0.05)
        # Per-File-Attribution: anhand segment_index die Datei-Pfade taggen
        for f in all_results:
            try:
                idx = getattr(f, 'segment_index', -1)
                if 0 <= idx < len(file_pairs):
                    f.source_file = file_pairs[idx][0]
                    f.target_file = file_pairs[idx][1]
            except Exception:
                pass
        s['findings'] = [_finding_to_dict(f) for f in all_results]
        s['last_score'] = s.get('current_score', -1)  # vorherigen Score merken
        s['current_score'] = compute_score(all_results)
        s['phase_finding_counts'] = phase_finding_counts
        # Diff zur vorherigen Analyse berechnen
        try:
            prev_fps = set(s.get('_prev_fingerprints', []) or [])
            new_fps = [_finding_fingerprint(f) for f in all_results]
            new_indices = [i for i, fp in enumerate(new_fps) if fp not in prev_fps]
            gone = sum(1 for fp in prev_fps if fp not in set(new_fps))
            s['analysis_diff'] = {
                'has_prev': bool(prev_fps),
                'new_idx': new_indices,
                'new_count': len(new_indices),
                'gone_count': gone,
                'prev_total': len(prev_fps),
            }
        except Exception as exc:
            _logger.debug('Diff-Berechnung fehlgeschlagen: %s', exc)
            s['analysis_diff'] = {}
        s['analysis_running'] = False
        was_cancelled = bool(s.get('cancel_requested'))
        s['cancel_requested'] = False
        if refs.get('cancel_btn'):
            refs['cancel_btn'].visible = False
        if refs['progress_bar']:
            refs['progress_bar'].value = 1.0
        if refs['progress_text']:
            total_elapsed = time.monotonic() - analysis_start
            status = 'Abgebrochen' if was_cancelled else 'Fertig'
            refs['progress_text'].set_text(
                f'{status} in {total_elapsed:.1f}s · {len(all_results)} Findings'
            )
        # Letzte Analyse-Dauer persistent speichern
        s['last_analysis_elapsed'] = total_elapsed if not was_cancelled else None
        await asyncio.sleep(0.5)
        if refs['progress_bar']:
            refs['progress_bar'].visible = False
        if refs['progress_text']:
            refs['progress_text'].visible = False
        if refs.get('cancel_btn'):
            refs['cancel_btn'].visible = False
        if refs.get('start_btn'):
            refs['start_btn'].set_text('Analyse starten')
            refs['start_btn'].props('icon=play_arrow')
        _update_start_btn()
        _refresh_results_area()
        # Report automatisch in 03_Korrektur speichern (auch bei Abbruch -> Teilergebnis)
        _save_report_to_project()
        # Score-Historie aktualisieren (max. 20 Einträge) — nur bei vollstaendigem Lauf
        if not was_cancelled:
            try:
                hist = list(s.get('score_history', []) or [])
                hist.append(int(s.get('current_score', 0)))
                s['score_history'] = hist[-20:]
            except Exception:
                pass
        _save_and_notify()
        try:
            _refresh_project_folders()
        except Exception:
            pass
        if was_cancelled:
            ui.notify(f'Analyse abgebrochen · {len(all_results)} Findings (Teilergebnis)',
                      type='warning', timeout=4000)
        else:
            _new_score = s['current_score']
            _prev = s.get('last_score', -1)
            _counts = {'Kritisch': 0, 'Wichtig': 0}
            for _fd in s.get('findings', []):
                _lbl = severity_label(_dict_to_finding(_fd).severity)
                if _lbl in _counts:
                    _counts[_lbl] += 1
            _delta_str = ''
            if _prev >= 0:
                _delta = _new_score - _prev
                if _delta > 0:
                    _delta_str = f' (↑ +{_delta})'
                elif _delta < 0:
                    _delta_str = f' (↓ {_delta})'
                else:
                    _delta_str = ' (→ gleich)'
            _crit_str = f' · {_counts["Kritisch"]} kritisch' if _counts['Kritisch'] else ''
            _type = 'positive' if _new_score >= 80 else 'warning' if _new_score >= 50 else 'negative'
            ui.notify(
                f'Score {_new_score}/100{_delta_str} · {len(all_results)} Findings{_crit_str}',
                type=_type, timeout=5000)

    def _save_report_to_project():
        """Speichert den Analyse-Report automatisch in 03_Korrektur des aktiven Projekts."""
        proj_path = s.get('active_project_path', '')
        if not proj_path or not os.path.isdir(proj_path):
            return
        findings = s.get('findings', [])
        score = s.get('current_score', -1)
        if score < 0 or not findings:
            return
        korrektur_dir = os.path.join(proj_path, '03_Korrektur')
        os.makedirs(korrektur_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        # TXT Report
        try:
            report_path = os.path.join(korrektur_dir, f'Prüfbericht_{ts}.txt')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f'Qualitätsprüfung — Score: {score}/100\n')
                f.write(f'Datum: {datetime.now().strftime("%d.%m.%Y %H:%M")}\n')
                f.write(f'Findings: {len(findings)}\n')
                f.write('=' * 60 + '\n\n')
                for i, fd in enumerate(findings, 1):
                    fi = _dict_to_finding(fd) if isinstance(fd, dict) else fd
                    f.write(f'[{fi.severity.upper()}] {fi.code}\n')
                    f.write(f'{fi.message}\n')
                    if getattr(fi, 'source_text', ''):
                        f.write(f'Quelle: {fi.source_text[:200]}\n')
                    if getattr(fi, 'target_text', ''):
                        f.write(f'Ziel: {fi.target_text[:200]}\n')
                    f.write('\n')
            _logger.info(f'Report gespeichert: {report_path}')
        except Exception as e:
            _logger.warning(f'Report-Speicherung fehlgeschlagen: {e}')
        # JSON Report (maschinenlesbar, für spätere Vergleiche)
        try:
            json_path = os.path.join(korrektur_dir, f'Prüfbericht_{ts}.json')
            report_data = {
                'score': score,
                'findings_count': len(findings),
                'timestamp': datetime.now().isoformat(),
                'source_files': [os.path.basename(f) for f in s.get('source_files', [])],
                'translation_files': [os.path.basename(f) for f in s.get('translation_files', [])],
                'findings': findings,
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _copy_files_to_project():
        customer = s.get('active_customer', '')
        if not customer:
            return
        today = datetime.now().strftime('%Y-%m-%d')
        if s.get('source_files'):
            dest = _ensure_date_subfolder(customer, '01_Ausgangstext', today)
            for fp in s['source_files']:
                if os.path.exists(fp):
                    shutil.copy2(fp, os.path.join(dest, os.path.basename(fp)))
        if s.get('translation_files'):
            dest = _ensure_date_subfolder(customer, '02_Übersetzung', today)
            for fp in s['translation_files']:
                if os.path.exists(fp):
                    shutil.copy2(fp, os.path.join(dest, os.path.basename(fp)))

    # ------------------------------------------------------------------
    # Filter / search
    # ------------------------------------------------------------------
    def _filtered_findings() -> List[Tuple[int, QAIssue]]:
        af = s.get('active_filter', 'all')
        st = s.get('search_text', '').lower()
        hide_done = bool(s.get('hide_done', False))
        checked = s.get('checked_findings', {}) or {}
        result = []
        for i, fd in enumerate(s.get('findings', [])):
            f = _dict_to_finding(fd)
            lbl = severity_label(f.severity)
            if af == 'critical' and lbl != 'Kritisch':
                continue
            if af == 'major' and lbl != 'Wichtig':
                continue
            if af == 'minor' and lbl != 'Hinweis':
                continue
            if st:
                hay = (f.message + ' ' + (f.category or '') + ' '
                       + category_label_de(f.category) + ' '
                       + os.path.basename(getattr(f, 'source_file', '') or '') + ' '
                       + os.path.basename(getattr(f, 'target_file', '') or '')).lower()
                if st not in hay:
                    continue
            if hide_done and checked.get(str(i), False):
                continue
            result.append((i, f))
        # Sortierung
        sort_mode = s.get('sort_mode', 'default')
        if sort_mode == 'severity':
            _order = {'Kritisch': 0, 'Wichtig': 1, 'Hinweis': 2}
            result.sort(key=lambda it: (
                _order.get(severity_label(it[1].severity), 9),
                it[0]))
        elif sort_mode == 'file':
            result.sort(key=lambda it: (
                (os.path.basename(getattr(it[1], 'target_file', '') or '')
                 or os.path.basename(getattr(it[1], 'source_file', '') or '')).lower(),
                it[1].segment_index if it[1].segment_index >= 0 else it[0],
                it[0]))
        elif sort_mode == 'segment':
            result.sort(key=lambda it: (
                it[1].segment_index if it[1].segment_index >= 0 else 10**9,
                it[0]))
        elif sort_mode == 'category':
            result.sort(key=lambda it: (
                (it[1].category or '').lower(), it[0]))
        return result

    def _set_sort_mode(mode: str):
        s['sort_mode'] = mode
        _render_findings_list()

    def _set_filter(key: str):
        s['active_filter'] = key
        _refresh_results_area()

    def _toggle_hide_done(val: bool):
        s['hide_done'] = bool(val)
        _refresh_results_area()

    def _toggle_view_mode():
        cycle = {'normal': 'compact', 'compact': 'split', 'split': 'normal'}
        s['view_mode'] = cycle.get(s.get('view_mode', 'normal'), 'normal')
        if refs.get('compact_btn'):
            try:
                icon_map = {'normal': 'density_small', 'compact': 'density_medium', 'split': 'view_sidebar'}
                icon = icon_map.get(s['view_mode'], 'density_small')
                refs['compact_btn'].props(f'icon={icon}')
                tips = {'normal': 'Normal', 'compact': 'Kompakt', 'split': 'Split-Ansicht'}
                refs['compact_btn'].tooltip(f'Ansicht: {tips[s["view_mode"]]} (umschalten)')
            except Exception:
                pass
        _render_findings_list()

    def _on_search_change(e):
        s['search_text'] = getattr(e, 'value', '') or ''
        _render_findings_list()

    # ------------------------------------------------------------------
    # Results rendering
    # ------------------------------------------------------------------
    def _refresh_results_area():
        current_score = s.get('current_score', -1)
        has_results = current_score >= 0
        # Export-Button: nur nach erfolgreicher Analyse aktiviert
        if refs.get('export_btn'):
            try:
                if has_results:
                    refs['export_btn'].enable()
                    refs['export_btn'].style('font-size:var(--fs-sm);opacity:.75;padding:6px 12px;')
                else:
                    refs['export_btn'].disable()
                    refs['export_btn'].style('font-size:var(--fs-sm);opacity:.35;padding:6px 12px;')
            except Exception:
                pass
        # Header Score-Badge
        if refs.get('header_score_badge'):
            if current_score >= 0:
                hclr = '#16a34a' if current_score >= 80 else '#d97706' if current_score >= 50 else '#dc2626'
                refs['header_score_badge'].set_content(
                    f'<div style="display:flex;align-items:center;gap:5px;'
                    f'background:rgba(255,255,255,.1);border-radius:20px;padding:3px 10px 3px 7px;'
                    f'border:1px solid rgba(255,255,255,.15);">'
                    f'<div style="width:8px;height:8px;border-radius:50%;background:{hclr};flex-shrink:0;"></div>'
                    f'<span style="font-size:var(--fs-sm);font-weight:700;color:white;">{current_score}</span>'
                    f'</div>'
                )
            else:
                refs['header_score_badge'].set_content('')
        # Score
        if refs['score_number']:
            if current_score < 0:
                refs['score_number'].set_text('--')
                refs['score_number'].style('color:var(--text-light);')
            else:
                refs['score_number'].set_text(str(current_score))
                clr = 'var(--success)' if current_score >= 80 else 'var(--warning)' if current_score >= 50 else 'var(--error)'
                refs['score_number'].style(f'color:{clr};')
        # Score-Delta (Vergleich zur vorherigen Analyse)
        if refs.get('score_delta'):
            last = s.get('last_score', -1)
            if current_score >= 0 and last >= 0 and last != current_score:
                delta = current_score - last
                if delta > 0:
                    refs['score_delta'].set_content(
                        f'<span style="font-size:var(--fs-xs);font-weight:700;color:var(--success);">↑ +{delta}</span>')
                else:
                    refs['score_delta'].set_content(
                        f'<span style="font-size:var(--fs-xs);font-weight:700;color:var(--error);">↓ {delta}</span>')
            else:
                refs['score_delta'].set_content('')
        # Score-Ring (conic-gradient)
        if refs.get('score_ring'):
            if current_score < 0:
                refs['score_ring'].style('position:absolute;inset:0;--sc:var(--surface-border-strong);--pct:0%;')
            else:
                pct = max(0, min(100, current_score))
                rclr = 'var(--success)' if current_score >= 80 else 'var(--warning)' if current_score >= 50 else 'var(--error)'
                refs['score_ring'].style(f'position:absolute;inset:0;--sc:{rclr};--pct:{pct}%;')
        if refs['score_sublabel']:
            total_f = len(s.get('findings', []))
            f_txt = f' · {total_f} Finding{"s" if total_f != 1 else ""}' if total_f else ''
            if current_score < 0:
                refs['score_sublabel'].set_text('Noch keine Analyse')
            elif current_score >= 80:
                refs['score_sublabel'].set_text(f'Gute Qualität{f_txt}')
            elif current_score >= 50:
                refs['score_sublabel'].set_text(f'Verbesserungen nötig{f_txt}')
            else:
                refs['score_sublabel'].set_text(f'Kritische Probleme{f_txt}')
        # Letzte Analyse-Dauer
        if refs.get('score_time_label'):
            elapsed = s.get('last_analysis_elapsed')
            if elapsed is not None:
                refs['score_time_label'].set_text(f'Letzte Analyse: {elapsed:.1f}s')
            else:
                refs['score_time_label'].set_text('')
        # Counts
        counts = {'Kritisch': 0, 'Wichtig': 0, 'Hinweis': 0}
        for fd in s.get('findings', []):
            lbl = severity_label(_dict_to_finding(fd).severity)
            counts[lbl] = counts.get(lbl, 0) + 1
        if refs['critical_count']:
            refs['critical_count'].set_text(str(counts['Kritisch']))
        if refs['major_count']:
            refs['major_count'].set_text(str(counts['Wichtig']))
        if refs['minor_count']:
            refs['minor_count'].set_text(str(counts['Hinweis']))
        # Aktiven Severity-Filter auf den Stat-Pills hervorheben
        _active_filter = s.get('active_filter', 'all')
        for _pill_key, _filt in (('critical_count_pill', 'critical'),
                                 ('major_count_pill', 'major'),
                                 ('minor_count_pill', 'minor')):
            _pill = refs.get(_pill_key)
            if _pill:
                try:
                    if _active_filter == _filt:
                        _pill.classes(add='stat-active')
                    else:
                        _pill.classes(remove='stat-active')
                except Exception:
                    pass
        # "X von Y erledigt" Counter + Fortschrittsbalken
        total_f2 = len(s.get('findings', []))
        checked = s.get('checked_findings', {}) or {}
        done = sum(1 for k, v in checked.items()
                   if v and isinstance(k, str) and k.isdigit() and int(k) < total_f2)
        if refs.get('done_counter'):
            refs['done_counter'].set_text(f'{done} von {total_f2} erledigt' if total_f2 else '')
        if refs.get('done_progress_label'):
            refs['done_progress_label'].set_text(f'{done} / {total_f2}' if total_f2 else '0 / 0')
        if refs.get('done_progress_bar'):
            pct_done = int(done / total_f2 * 100) if total_f2 else 0
            bar_clr = 'var(--success)' if pct_done == 100 else 'var(--primary)'
            refs['done_progress_bar'].style(
                f'position:absolute;top:0;left:0;bottom:0;width:{pct_done}%;'
                f'background:{bar_clr};border-radius:3px;transition:width 400ms ease;'
            )
        # Score-Historie als SVG-Sparkline
        if refs.get('history_chart'):
            hist = list(s.get('score_history', []) or [])
            if len(hist) >= 2:
                w, h = 180, 24
                step = w / (len(hist) - 1) if len(hist) > 1 else w
                pts = ' '.join(
                    f'{i*step:.1f},{h - (max(0,min(100,v))/100.0)*h:.1f}'
                    for i, v in enumerate(hist)
                )
                last = hist[-1]
                lc = 'var(--success)' if last >= 80 else 'var(--warning)' if last >= 50 else 'var(--error)'
                avg = sum(hist) / len(hist)
                refs['history_chart'].set_content(
                    f'<svg width="{w}" height="{h}" style="display:block;">'
                    f'<polyline fill="none" stroke="{lc}" stroke-width="1.5" '
                    f'points="{pts}"/></svg>'
                    f'<div style="font-size:var(--fs-xs);color:var(--text-light);margin-top:2px;">'
                    f'Verlauf · ⌀ {avg:.0f} · {len(hist)} Analysen</div>'
                )
            else:
                refs['history_chart'].set_content('')
        # Phase-Findings-Aufschlüsselung
        if refs.get('phase_score_row'):
            pc = s.get('phase_finding_counts', {}) or {}
            _phase_defs = [
                ('P1', 'phase1', 'Zahlen & Formate'),
                ('P2', 'phase2', 'Inhalt & Konsistenz'),
                ('P3', 'phase3', 'Grammatik & Stil'),
                ('P4', 'phase4', 'KI-Prüfung'),
            ]
            parts = []
            for label, pkey, tip in _phase_defs:
                count = pc.get(pkey)
                if count is None:
                    val_str, bg = '—', 'var(--bg-muted)'
                elif count == 0:
                    val_str, bg = '✓', 'rgba(22,163,74,.18)'
                elif count <= 3:
                    val_str, bg = str(count), 'rgba(234,88,12,.14)'
                else:
                    val_str, bg = str(count), 'rgba(220,38,38,.14)'
                parts.append(
                    f'<div title="{tip}" style="display:inline-flex;align-items:center;gap:3px;'
                    f'background:{bg};border-radius:5px;padding:2px 7px;cursor:default;">'
                    f'<span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-muted);">{label}</span>'
                    f'<span style="font-size:var(--fs-xs);font-weight:600;color:var(--text);">{val_str}</span>'
                    f'</div>'
                )
            refs['phase_score_row'].set_content(
                '<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:4px;">'
                + ''.join(parts) + '</div>'
            )
        # Diff-Badge: 'X neu seit letzter Analyse, Y behoben'
        if refs.get('diff_badge'):
            diff = s.get('analysis_diff', {}) or {}
            if diff.get('has_prev') and (diff.get('new_count', 0) or diff.get('gone_count', 0)):
                new_n = int(diff.get('new_count', 0))
                gone_n = int(diff.get('gone_count', 0))
                parts = []
                if new_n:
                    parts.append(
                        f'<span style="color:var(--error);font-weight:700;">↑ {new_n} neu</span>'
                    )
                if gone_n:
                    parts.append(
                        f'<span style="color:var(--success);font-weight:700;">↓ {gone_n} behoben</span>'
                    )
                refs['diff_badge'].set_content(
                    '<div style="font-size:var(--fs-xs);color:var(--text-muted);'
                    'background:var(--surface-alt);padding:4px 8px;border-radius:6px;'
                    'border:1px solid var(--surface-border);display:inline-block;">'
                    'Vergleich zur letzten Analyse: ' + ' · '.join(parts) + '</div>'
                )
            else:
                refs['diff_badge'].set_content('')
        # Kategorien-Heatmap (Top-6, mit Severity-Anteilen)
        if refs.get('category_heatmap'):
            cont = refs['category_heatmap']
            cont.clear()
            from collections import Counter as _Cnt
            cat_counts: Dict[str, Dict[str, int]] = {}
            for fd in s.get('findings', []):
                f = _dict_to_finding(fd)
                cat = (f.category or 'Sonstige').strip() or 'Sonstige'
                lbl = severity_label(f.severity)
                d = cat_counts.setdefault(cat, {'Kritisch': 0, 'Wichtig': 0, 'Hinweis': 0})
                d[lbl] = d.get(lbl, 0) + 1
            top = sorted(
                cat_counts.items(),
                key=lambda kv: (-sum(kv[1].values()), kv[0]),
            )[:6]
            max_total = max((sum(d.values()) for _, d in top), default=1) or 1
            _SEV_STYLE = [
                ('Kritisch', 'var(--error)'),
                ('Wichtig', 'var(--warning)'),
                ('Hinweis', 'var(--info)'),
            ]
            with cont:
                if not top:
                    ui.label('Keine Befunde').style('font-size:var(--fs-xs);color:var(--text-light);')
                else:
                    # Severity-Legende, damit die Balkenfarben verständlich sind
                    with ui.row().classes('items-center gap-3').style('margin:0 0 8px 2px;'):
                        for sev_lbl, sev_clr in _SEV_STYLE:
                            tot = sum(d.get(sev_lbl, 0) for _, d in top)
                            if tot <= 0:
                                continue
                            with ui.row().classes('items-center gap-1').style('gap:5px;'):
                                ui.element('div').style(
                                    f'width:9px;height:9px;border-radius:50%;background:{sev_clr};'
                                    'flex-shrink:0;')
                                ui.label(f'{sev_lbl} ({tot})').style(
                                    'font-size:var(--fs-xs);color:var(--text-muted);')
                for cat, d in top:
                    total = sum(d.values())
                    width_pct = max(8, int(total / max_total * 100))
                    label_de = category_label_de(cat)
                    crit, warn, hint = d.get('Kritisch', 0), d.get('Wichtig', 0), d.get('Hinweis', 0)
                    tip_parts = []
                    if crit:
                        tip_parts.append(f'{crit} kritisch')
                    if warn:
                        tip_parts.append(f'{warn} wichtig')
                    if hint:
                        tip_parts.append(f'{hint} Hinweis')
                    tip = label_de + (' · ' + ' · '.join(tip_parts) if tip_parts else '')
                    with ui.row().classes('w-full items-center gap-2 cat-row cursor-pointer').style(
                        'padding:3px 4px;border-radius:6px;'
                    ).on('click', lambda _, c=label_de: (s.update({'search_text': c}),
                                                     refs.get('search_input') and refs['search_input'].set_value(c),
                                                     _refresh_results_area())).tooltip(tip):
                        ui.label(label_de[:34] + ('…' if len(label_de) > 34 else '')).style(
                            'font-size:var(--fs-sm);color:var(--text-body);width:150px;flex-shrink:0;'
                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                        with ui.element('div').style(
                            'flex-grow:1;height:12px;border-radius:6px;background:var(--bg-muted);'
                            'border:1px solid var(--surface-border);position:relative;overflow:hidden;'
                        ):
                            seg_left = 0.0
                            for sev_lbl, sev_clr in _SEV_STYLE:
                                cnt = d.get(sev_lbl, 0)
                                if cnt <= 0:
                                    continue
                                pct = (cnt / total) * width_pct
                                ui.element('div').style(
                                    f'position:absolute;top:0;bottom:0;'
                                    f'left:{seg_left:.1f}%;width:{pct:.1f}%;'
                                    f'background:{sev_clr};'
                                )
                                seg_left += pct
                        ui.label(str(total)).style(
                            'font-size:var(--fs-sm);font-weight:700;color:var(--text);'
                            'width:24px;text-align:right;')
        # Per-File-Heatmap (Score je Datei-Paar)
        if refs.get('per_file_heatmap'):
            cont = refs['per_file_heatmap']
            cont.clear()
            file_buckets: Dict[Tuple[str, str], List[Any]] = {}
            for fd in s.get('findings', []):
                f = _dict_to_finding(fd)
                key = (getattr(f, 'source_file', '') or '',
                       getattr(f, 'target_file', '') or '')
                if not (key[0] or key[1]):
                    continue
                file_buckets.setdefault(key, []).append(f)
            with cont:
                if not file_buckets:
                    ui.label('Keine Datei-Zuordnung').style(
                        'font-size:var(--fs-xs);color:var(--text-light);')
                else:
                    items = []
                    for (sp, tp), flist in file_buckets.items():
                        sc = compute_score(flist)
                        items.append((sp, tp, flist, sc))
                    items.sort(key=lambda x: x[3])
                    # Legende: Score-Farbbänder + Erklärung der Zahl rechts
                    with ui.row().classes('items-center gap-3').style('margin:0 0 8px 2px;flex-wrap:wrap;'):
                        for clr, txt in [('var(--success)', 'gut (≥80)'),
                                          ('var(--warning)', 'mittel (50–79)'),
                                          ('var(--error)', 'kritisch (<50)')]:
                            with ui.row().classes('items-center').style('gap:5px;'):
                                ui.element('div').style(
                                    f'width:9px;height:9px;border-radius:50%;background:{clr};flex-shrink:0;')
                                ui.label(txt).style('font-size:var(--fs-xs);color:var(--text-muted);')
                        ui.label('· Zahl rechts = Befunde').style(
                            'font-size:var(--fs-xs);color:var(--text-light);')
                    for sp, tp, flist, sc in items[:10]:
                        sclr = 'var(--success)' if sc >= 80 else 'var(--warning)' if sc >= 50 else 'var(--error)'
                        nm = os.path.basename(sp or tp or '?')
                        sev_cnt = {'Kritisch': 0, 'Wichtig': 0, 'Hinweis': 0}
                        for ff in flist:
                            sev_cnt[severity_label(ff.severity)] = (
                                sev_cnt.get(severity_label(ff.severity), 0) + 1)
                        n_find = len(flist)
                        tip_parts = []
                        if sev_cnt['Kritisch']:
                            tip_parts.append(f'{sev_cnt["Kritisch"]} kritisch')
                        if sev_cnt['Wichtig']:
                            tip_parts.append(f'{sev_cnt["Wichtig"]} wichtig')
                        if sev_cnt['Hinweis']:
                            tip_parts.append(f'{sev_cnt["Hinweis"]} Hinweis')
                        tip = (f'{nm} · Score {sc}/100 · {n_find} Befund'
                               + ('e' if n_find != 1 else '')
                               + (' (' + ', '.join(tip_parts) + ')' if tip_parts else ''))
                        with ui.row().classes('w-full items-center gap-2 cat-row cursor-pointer').style(
                            'padding:3px 4px;border-radius:6px;'
                        ).on('click', lambda _, n=nm: (s.update({'search_text': n}),
                                                        refs.get('search_input') and refs['search_input'].set_value(n),
                                                        _refresh_results_area())).tooltip(tip):
                            ui.label(nm[:32] + ('…' if len(nm) > 32 else '')).style(
                                'font-size:var(--fs-sm);color:var(--text-body);width:150px;flex-shrink:0;'
                                'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                            with ui.element('div').style(
                                'flex-grow:1;height:12px;border-radius:6px;'
                                'background:var(--bg-muted);border:1px solid var(--surface-border);'
                                'position:relative;overflow:hidden;'
                            ):
                                ui.element('div').style(
                                    f'position:absolute;top:0;bottom:0;left:0;'
                                    f'width:{max(0,min(100,sc))}%;background:{sclr};'
                                )
                            ui.label(f'{sc}').style(
                                f'font-size:var(--fs-sm);font-weight:700;color:{sclr};'
                                f'width:30px;text-align:right;').tooltip(f'Score {sc}/100')
                            with ui.element('div').classes('find-badge').style(
                                'min-width:22px;height:18px;padding:0 6px;border-radius:9px;'
                                'display:inline-flex;align-items:center;justify-content:center;'
                                'background:var(--bg-muted);'
                            ).tooltip('Anzahl Befunde'):
                                ui.label(str(n_find)).style(
                                    'font-size:var(--fs-xs);font-weight:700;color:var(--text-muted);line-height:1;')
        # Visibility
        for key in ('results_area', 'score_card', 'summary_card'):
            if refs[key]:
                refs[key].visible = has_results
        if refs['welcome_area']:
            refs['welcome_area'].visible = not has_results
        # Filter buttons: aktiv-Highlight + Severity-Counts in Label
        af = s.get('active_filter', 'all')
        all_findings_for_count = [_dict_to_finding(d) for d in (s.get('findings', []) or [])]
        sev_counts_filter = {'all': len(all_findings_for_count),
                             'critical': 0, 'major': 0, 'minor': 0}
        for fd in all_findings_for_count:
            sev = (getattr(fd, 'severity', '') or '').lower()
            if sev in ('critical', 'kritisch'):
                sev_counts_filter['critical'] += 1
            elif sev in ('major', 'wichtig', 'warning'):
                sev_counts_filter['major'] += 1
            elif sev in ('minor', 'hinweis', 'info'):
                sev_counts_filter['minor'] += 1
        for key, btn in filter_btns.items():
            base = getattr(btn, '_base_label', key)
            dot = getattr(btn, '_dot', '')
            dot_clr = getattr(btn, '_dot_clr', 'var(--text-muted)')
            cnt = sev_counts_filter.get(key, 0)
            try:
                label_with_cnt = (f'{dot} ' if dot else '') + f'{base} ({cnt})'
                btn.set_text(label_with_cnt)
            except Exception:
                pass
            if key == af:
                btn.style(
                    f'background:var(--bg-primary);color:white;'
                    f'border-radius:20px;padding:3px 12px;'
                    f'border:1px solid var(--bg-primary);font-weight:700;font-size:var(--fs-sm);'
                )
            else:
                btn.style(
                    f'border-radius:20px;padding:3px 12px;'
                    f'border:1px solid var(--surface-border);'
                    f'background:var(--surface);color:{dot_clr};'
                    f'font-weight:600;font-size:var(--fs-sm);'
                )
        _render_findings_list()

    def _render_split_list(filtered):
        ctx = SimpleNamespace(
            s=s, selected_idx=selected_idx,
            select_finding=_select_split_finding,
        )
        _ui_findings.render_split_list(ctx, filtered)

    def _render_detail_panel():
        ctx = SimpleNamespace(
            s=s, refs=refs, selected_idx=selected_idx,
            toggle_checked=_toggle_checked,
            dict_to_finding=_dict_to_finding,
        )
        _ui_findings.render_detail_panel(ctx)
    def _select_split_finding(idx: int):
        """Selektiert Finding in der Split-Ansicht und aktualisiert Detail-Panel."""
        selected_idx['v'] = idx
        dp = refs.get('detail_panel')
        if dp is not None:
            dp.clear()
            with dp:
                _render_detail_panel()
        # Linke Liste neu rendern (Selection-Highlight aktualisieren)
        _render_findings_list()

    def _render_welcome():
        ctx = SimpleNamespace(
            s=s,
            load_customer_info=_load_customer_info,
            list_projects=_list_projects,
            display_name=_display_name,
            find_source_folder=_find_source_folder,
            find_translation_folder=_find_translation_folder,
            list_files_in_folder=_list_files_in_folder,
            get_project_path=_get_project_path,
            get_customer_path=_get_customer_path,
            count_files_in_folder=_count_files_in_folder,
            scan_project_dates=_scan_project_dates,
            on_customer_selected=_on_customer_selected,
            select_auftrag=_select_auftrag,
        )
        _ui_findings.render_welcome(ctx)

    def _render_findings_list():
        filtered = _filtered_findings()
        # Suchfeld-Treffer-Zähler aktualisieren
        if refs.get('search_counter'):
            st = s.get('search_text', '') or ''
            total_all = len(s.get('findings', []))
            if st.strip():
                refs['search_counter'].set_text(f'{len(filtered)} / {total_all}')
            else:
                refs['search_counter'].set_text('')
        ctx = SimpleNamespace(
            s=s, refs=refs,
            filtered_findings=_filtered_findings,
            render_welcome=_render_welcome,
            render_split_list=_render_split_list,
            render_detail_panel=_render_detail_panel,
            render_finding_card=_render_finding_card,
        )
        _ui_findings.render_findings_list(ctx)

    def _render_finding_card(idx: int, f: QAIssue):
        ctx = SimpleNamespace(
            s=s, refs=refs, selected_idx=selected_idx,
            toggle_checked=_toggle_checked,
            refresh_results=_refresh_results_area,
        )
        _ui_findings.render_finding_card(ctx, idx, f)

    def _push_undo(prev_checked: Dict[str, Any], label: str):
        """Speichert vorherige checked_findings-Map fuer Undo (max. 20)."""
        undo_stack.append({'checked': dict(prev_checked or {}), 'label': label})
        if len(undo_stack) > 20:
            del undo_stack[0]
        if refs.get('undo_btn'):
            try:
                refs['undo_btn'].enable()
                refs['undo_btn'].tooltip(f'Rueckgaengig: {label}')
            except Exception:
                pass

    def _undo_last():
        if not undo_stack:
            ui.notify('Nichts zum Rueckgaengig machen', type='info')
            return
        entry = undo_stack.pop()
        s['checked_findings'] = dict(entry.get('checked') or {})
        if refs.get('undo_btn'):
            try:
                if not undo_stack:
                    refs['undo_btn'].disable()
                    refs['undo_btn'].tooltip('Nichts rueckgaengig zu machen')
            except Exception:
                pass
        try:
            _save_and_notify()
        except Exception:
            pass
        _refresh_results_area()
        ui.notify(f'Rueckgaengig: {entry.get("label", "Aenderung")}', type='positive')

    def _toggle_checked(idx: int, val: bool):
        prev = dict(s.get('checked_findings', {}) or {})
        checked = dict(prev)
        checked[str(idx)] = val
        s['checked_findings'] = checked
        _push_undo(prev, 'Erledigt-Markierung')
        # Persistent speichern, debounced (vermeidet IO-Storm bei vielen Klicks)
        _schedule_save()
        # Refresh damit Counter / "Erledigte ausblenden" sofort wirken
        _refresh_results_area()

    def _bulk_mark_filtered(done: bool):
        """Markiert alle aktuell sichtbaren (gefilterten) Findings als done/undone."""
        filtered = _filtered_findings()
        if not filtered:
            ui.notify('Keine sichtbaren Findings', type='info')
            return
        prev = dict(s.get('checked_findings', {}) or {})
        checked = dict(prev)
        n_changed = 0
        for i, _ in filtered:
            key = str(i)
            if bool(checked.get(key, False)) != done:
                checked[key] = done
                n_changed += 1
        if n_changed == 0:
            ui.notify('Nichts zu aendern', type='info')
            return
        s['checked_findings'] = checked
        _push_undo(prev, f'{n_changed}× {"erledigt" if done else "wieder offen"}')
        try:
            _save_and_notify()
        except Exception:
            pass
        _refresh_results_area()
        ui.notify(
            f'{n_changed} Findings als {"erledigt" if done else "offen"} markiert',
            type='positive',
        )

    # ------------------------------------------------------------------
    # Keyboard navigation
    # ------------------------------------------------------------------
    def _scroll_to_selected():
        """Scrollt selektiertes Finding ins Sichtfeld."""
        idx = selected_idx['v']
        if idx < 0:
            return
        try:
            ui.run_javascript(
                f"var el=document.getElementById('finding-card-{idx}');"
                f"if(el)el.scrollIntoView({{behavior:'smooth',block:'center'}});"
            )
        except Exception:
            pass

    def _show_keyboard_help():
        _ui_dialogs.show_keyboard_help()

    def _handle_key(e):
        # Ctrl+Enter → Analyse starten
        try:
            if e.key == 'Enter' and e.modifiers.ctrl and not e.action.repeat and e.action.keydown:
                if not s.get('analysis_running'):
                    asyncio.create_task(_start_analysis())
                return
        except Exception:
            pass
        # Ctrl+Z → Undo letzte Erledigt-Aenderung
        try:
            if (e.key == 'z' and e.modifiers.ctrl and not e.action.repeat
                    and e.action.keydown):
                _undo_last()
                return
        except Exception:
            pass
        # Esc → Analyse abbrechen (nur waehrend laufender Analyse)
        try:
            if e.key == 'Escape' and e.action.keydown and not e.action.repeat:
                if s.get('analysis_running'):
                    _request_cancel()
                    return
        except Exception:
            pass
        filtered = _filtered_findings()
        if not filtered:
            return
        indices = [i for i, _ in filtered]
        # Naechstes Finding: n / j / ArrowDown
        if e.key in ('n', 'j', 'ArrowDown') and not e.action.repeat:
            if selected_idx['v'] < 0 or selected_idx['v'] not in indices:
                selected_idx['v'] = indices[0]
            else:
                pos = indices.index(selected_idx['v'])
                if pos + 1 < len(indices):
                    selected_idx['v'] = indices[pos + 1]
            _render_findings_list()
            _scroll_to_selected()
        # Voriges Finding: p / k / ArrowUp
        elif e.key in ('p', 'k', 'ArrowUp') and not e.action.repeat:
            if selected_idx['v'] < 0 or selected_idx['v'] not in indices:
                selected_idx['v'] = indices[-1]
            else:
                pos = indices.index(selected_idx['v'])
                if pos - 1 >= 0:
                    selected_idx['v'] = indices[pos - 1]
            _render_findings_list()
            _scroll_to_selected()
        # Erledigt-Toggle: x / Space
        elif e.key in ('x', ' ') and not e.action.repeat and e.action.keydown:
            if selected_idx['v'] in indices:
                cur = bool(s.get('checked_findings', {}).get(
                    str(selected_idx['v']), False))
                _toggle_checked(selected_idx['v'], not cur)
        # Severity-Filter: 1=Kritisch, 2=Wichtig, 3=Hinweis, 0=alle
        elif e.key in ('1', '2', '3', '0') and not e.action.repeat and e.action.keydown:
            try:
                if not e.modifiers.ctrl and not e.modifiers.alt:
                    _set_filter({'1': 'critical', '2': 'major',
                                 '3': 'minor', '0': 'all'}[e.key])
            except Exception:
                pass
        # Hilfe: ?
        elif e.key == '?' and not e.action.repeat and e.action.keydown:
            try:
                _show_keyboard_help()
            except Exception:
                pass

    ui.keyboard(on_key=_handle_key, ignore=['input', 'textarea', 'select'])

    # ------------------------------------------------------------------
    # Settings dialog
    # ------------------------------------------------------------------
    def _open_settings():
        _ui_dialogs.open_settings_dialog()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def _confirm_reset():
        """Zeigt Bestätigung wenn Findings vorhanden, sonst direkt Reset."""
        n = len(s.get('findings', []))
        if n == 0:
            _reset()
            return
        with ui.dialog() as dlg, ui.card().style('padding:20px;min-width:320px;'):
            ui.label('Neue Analyse starten?').style('font-size:var(--fs-xl);font-weight:700;')
            ui.label(f'{n} Findings gehen verloren.').style('font-size:var(--fs-md);color:var(--text-muted);margin-top:4px;')
            with ui.row().classes('w-full justify-end gap-2').style('margin-top:16px;'):
                ui.button('Abbrechen', on_click=dlg.close).props('flat no-caps')
                ui.button('Zurücksetzen', on_click=lambda: (dlg.close(), _reset())).props(
                    'no-caps color=negative')
        dlg.open()

    def _reset():
        try:
            _snapshot_previous_findings()
        except Exception:
            pass
        s['source_files'] = []
        s['translation_files'] = []
        s['paired_results'] = []
        s['findings'] = []
        s['checked_findings'] = {}
        s['current_score'] = -1
        s['active_filter'] = 'all'
        s['search_text'] = ''
        selected_idx['v'] = -1
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        _refresh_results_area()
        ui.notify('Zurückgesetzt', type='info')

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _do_export(fmt: str, only_filtered: bool = False):
        if only_filtered:
            findings = [_dict_to_finding(s.get('findings', [])[i])
                        for i, _ in _filtered_findings()]
            scope_label = 'gefiltert'
        else:
            findings = [_dict_to_finding(fd) for fd in s.get('findings', [])]
            scope_label = 'alle'
        if not findings:
            ui.notify('Keine Ergebnisse zum Exportieren', type='warning')
            return
        score = s.get('current_score', -1)
        path = None
        try:
            if fmt == 'txt':
                path = _exports_mod.export_txt(findings, score, _tmp_dir)
            elif fmt == 'excel':
                path = _exports_mod.export_excel(findings, _tmp_dir)
            elif fmt == 'pdf':
                path = _exports_mod.export_pdf(findings, score, _tmp_dir)
            elif fmt == 'zip':
                path = _exports_mod.export_correction_package(
                    findings, score,
                    list(s.get('source_files', [])),
                    list(s.get('translation_files', [])),
                    _tmp_dir,
                )
        except ImportError as exc:
            ui.notify(f'Modul fehlt: {exc}', type='negative')
            return
        except Exception as exc:
            _logger.warning('Export %s fehlgeschlagen: %s', fmt, exc)
            ui.notify('Export fehlgeschlagen', type='negative')
            return
        if path and os.path.exists(path):
            ui.download(path)
            ui.notify(
                f'{fmt.upper()}-Export ({scope_label}, {len(findings)} Findings) erstellt',
                type='positive',
            )

    # ------------------------------------------------------------------
    # Session restore
    # ------------------------------------------------------------------
    def _restore_session():
        session_data = _load_session()
        if not session_data:
            ui.notify('Keine Sitzung gefunden', type='warning')
            return
        s['source_files'] = [fp for fp in session_data.get('source_files', []) if os.path.exists(fp)]
        s['translation_files'] = [fp for fp in session_data.get('translation_files', []) if os.path.exists(fp)]
        s['paired_results'] = session_data.get('paired_results', [])
        valid_findings: list = []
        for fd in session_data.get('findings', []):
            try:
                _dict_to_finding(fd)
            except Exception:
                continue
            valid_findings.append(fd)
        s['findings'] = valid_findings
        # Geprüft-Status nur für noch existierende Findings übernehmen
        raw_checked = session_data.get('checked_findings', {}) or {}
        s['checked_findings'] = {
            k: v for k, v in raw_checked.items()
            if isinstance(k, str) and k.isdigit() and 0 <= int(k) < len(valid_findings)
        }
        s['active_customer'] = session_data.get('customer', '')
        s['active_project_path'] = session_data.get('project_path', '')
        try:
            mgt = session_data.get('manual_glossary_terms', {}) or {}
            s['manual_glossary_terms'] = {
                str(k): str(v) for k, v in mgt.items() if k and v
            }
        except Exception:
            s['manual_glossary_terms'] = {}
        gp = session_data.get('glossary_path', '')
        if gp and os.path.exists(gp):
            s['glossary_path'] = gp
        s['current_score'] = session_data.get('score', -1)
        try:
            sh = session_data.get('score_history', []) or []
            s['score_history'] = [int(x) for x in sh if isinstance(x, (int, float))][-20:]
        except Exception:
            s['score_history'] = []
        selected_idx['v'] = -1
        _refresh_file_list()
        _do_autopairing()
        _update_start_btn()
        _refresh_results_area()
        ts = session_data.get('timestamp', '')
        ui.notify(f'Sitzung wiederhergestellt (Score: {s["current_score"]}, '
                  f'{len(s["findings"])} Findings, {ts})', type='positive')

    # ------------------------------------------------------------------
    # Glossary
    # ------------------------------------------------------------------
    def _handle_glossary_upload(e: events.UploadEventArguments):
        upload_file = getattr(e, 'file', e)
        raw_name = getattr(upload_file, 'name', '') or getattr(e, 'name', 'glossar')
        name = os.path.basename(str(raw_name).replace('\\', '/').split('/')[-1]) or 'glossar'
        dest = os.path.join(_tmp_dir, f'glossar_{name}')
        with open(dest, 'wb') as f:
            data = upload_file.read() if hasattr(upload_file, 'read') else getattr(e, 'content', b'')
            if hasattr(data, 'read'):
                data = data.read()
            f.write(data if isinstance(data, bytes) else data.encode('utf-8'))
        s['glossary_path'] = dest
        if refs['glossary_label']:
            refs['glossary_label'].set_text(f'Glossar: {name}')
        ui.notify(f'Glossar geladen: {name}', type='positive')

    def _add_manual_term(term_input):
        val = term_input.value.strip()
        if '=' not in val:
            ui.notify('Format: Quelle=Übersetzung', type='warning')
            return
        src, tgt = val.split('=', 1)
        src, tgt = src.strip(), tgt.strip()
        if src and tgt:
            terms = dict(s.get('manual_glossary_terms', {}))
            terms[src] = tgt
            s['manual_glossary_terms'] = terms
            term_input.value = ''
            if refs.get('glossary_count_label'):
                refs['glossary_count_label'].set_text(f'{len(terms)} Begriffe')
            try:
                _save_and_notify()
            except Exception:
                pass
            ui.notify(f'Begriff: {src} = {tgt}', type='positive')

    def _open_glossary_editor():
        ctx = SimpleNamespace(s=s, refs=refs, save_and_notify=_save_and_notify)
        _ui_dialogs.open_glossary_editor(ctx, _tmp_dir)

    # ==================================================================
    # LAYOUT
    # ==================================================================
    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    )
    ui.add_head_html(_APP_CSS)

    # --- Header ---
    with ui.header().classes('items-center px-6 py-0').style(
        'background:linear-gradient(135deg,#0a1628 0%,#0f2744 40%,#1a365d 100%);'
        'min-height:56px;box-shadow:0 2px 12px rgba(0,0,0,.15);'
    ):
        with ui.row().classes('w-full items-center gap-4 flex-nowrap'):
            # Brand-Block (Logo + Titel)
            from nicegui_app.utils import render_logo
            render_logo(clickable=True, subtitle=True)

            # Navigation (Mitte-Links als Pill-Group)
            with ui.row().classes('items-center gap-1 ml-2'):
                _current_path = '/'
                def _nav_style(path: str) -> str:
                    is_active = _current_path == path
                    return ('font-size:var(--fs-sm);padding:6px 12px;'
                            + ('opacity:1;background:rgba(255,255,255,.12);border-radius:6px;' if is_active
                               else 'opacity:.65;'))
                def _mk_nav(label: str, icon: str, path: str):
                    b = ui.button(icon=icon,
                        on_click=lambda p=path: ui.navigate.to(p)).props(
                        'flat no-caps text-color=white dense').style(_nav_style(path))
                    with b:
                        ui.label(label).classes('hdr-label').style('margin-left:6px;')
                    b.tooltip(label)
                    return b
                _mk_nav('Kunden', 'business', '/kunden')
                _mk_nav('Kalender', 'calendar_month', '/kalender')

            ui.element('div').classes('flex-grow')

            # Save-Indicator (links neben Action-Gruppe, dezent)
            refs['save_indicator'] = ui.label('').classes('save-indicator').style(
                'font-size:var(--fs-xs);color:white;opacity:0;padding:0 8px;')

            # Score-Badge im Header (immer sichtbar)
            refs['header_score_badge'] = ui.html('').style('margin-right:4px;')

            # Aktionen (Primaer/Export rechts)
            with ui.row().classes('items-center gap-1 flex-nowrap'):
                _btn_new = ui.button(icon='refresh', on_click=lambda: _confirm_reset()).props(
                    'flat no-caps text-color=white dense').style(
                    'font-size:var(--fs-sm);opacity:.75;padding:6px 12px;')
                with _btn_new:
                    ui.label('Neue Analyse').classes('hdr-label').style('margin-left:6px;')
                _btn_new.tooltip('Neue Analyse')
                refs['export_btn'] = ui.dropdown_button('Export', icon='download').props(
                    'flat no-caps text-color=white dense').style(
                    'font-size:var(--fs-sm);opacity:.35;padding:6px 12px;')
                refs['export_btn'].disable()
                with refs['export_btn']:
                    ui.item('TXT-Bericht', on_click=lambda: _do_export('txt'))
                    ui.item('PDF-Bericht', on_click=lambda: _do_export('pdf'))
                    ui.item('Excel-Bericht', on_click=lambda: _do_export('excel'))
                    ui.separator()
                    ui.item('Korrekturpaket (ZIP)', on_click=lambda: _do_export('zip'))

            # Trenner + Icon-Tools (rechts)
            ui.separator().props('vertical').classes('mx-2 opacity-30')
            with ui.row().classes('items-center gap-0 flex-nowrap'):
                ui.button(icon='settings', on_click=_open_settings).props(
                    'flat round size=sm text-color=white').style('opacity:.6;').tooltip('Einstellungen')
                dark = ui.dark_mode(value=bool(s.get('dark_mode', False)))
                refs['dark_btn'] = ui.button(
                    icon='light_mode' if bool(s.get('dark_mode', False)) else 'dark_mode',
                    on_click=lambda: _toggle_dark()
                ).props('flat round size=sm text-color=white').style('opacity:.6;').tooltip(
                    'Dark Mode umschalten')
                def _toggle_dark():
                    dark.toggle()
                    s['dark_mode'] = bool(dark.value)
                    if refs.get('dark_btn'):
                        refs['dark_btn'].props(
                            f'icon={"light_mode" if dark.value else "dark_mode"}'
                        )

    # --- Main content ---
    with ui.row().classes('w-full flex-nowrap items-start gap-0').style(
        'min-height:calc(100vh - 56px);background:var(--surface-alt);'
    ):
        # ============ LEFT PANEL (480px) ============
        with ui.column().classes('flex-shrink-0 gap-0 min-w-0').style(
            'width:clamp(280px,30vw,480px);'
            'background:var(--surface);border-right:1px solid var(--surface-border);overflow-y:auto;'
            'max-height:calc(100vh - 56px);'
        ):
            with ui.column().classes('w-full gap-4 p-5'):

                # -- 1. Kundenliste (wie Kunden-Manager) --
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;'):
                    refs['customer_search'] = ui.input(
                        placeholder='Kunde suchen...',
                        on_change=lambda e: _render_customer_list(getattr(e, 'value', '') or ''),
                    ).classes('w-full').props('dense outlined clearable')
                    ui.button('Neuer Kunde', icon='person_add',
                        on_click=_show_new_customer_dialog).props('no-caps outline dense').classes('w-full').style('margin-top:8px;')
                    refs['customer_list_container'] = ui.column().classes('w-full gap-1').style('margin-top:8px;')

                def _render_customer_card(cust: str, is_active: bool):
                    """Rendert eine Kundenkarte (wie im Kunden-Manager)."""
                    info = _load_customer_info(cust)
                    initial = cust[0].upper() if cust else '?'
                    n_proj = len(_list_projects(cust))
                    with ui.card().classes('w-full cursor-pointer cust-card').props('flat bordered').style(
                        f'padding:8px 12px;{"background:var(--bg-info-soft);border-color:var(--border-info);" if is_active else ""}'
                    ).on('click', lambda _, c=cust: _select_customer(c)):
                        with ui.row().classes('items-center gap-3 w-full flex-nowrap'):
                            with ui.element('div').style(
                                'width:36px;height:36px;border-radius:8px;flex-shrink:0;'
                                'background:linear-gradient(135deg,#0f2744,#1a365d);'
                                'display:flex;align-items:center;justify-content:center;'
                            ):
                                ui.label(initial).style('color:var(--accent);font-size:var(--fs-lg);font-weight:700;')
                            with ui.column().classes('gap-0 flex-grow min-w-0'):
                                ui.label(_display_name(cust)).style(
                                    'font-size:var(--fs-md);font-weight:600;color:var(--text);'
                                    'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%;')
                                parts = []
                                if n_proj:
                                    parts.append(f'{n_proj} {"Projekt" if n_proj == 1 else "Projekte"}')
                                if info.get('branche'):
                                    parts.append(info['branche'])
                                ui.label(' · '.join(parts) if parts else 'Kein Projekt').style(
                                    'font-size:var(--fs-sm);color:var(--text-muted);'
                                    'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%;')
                            if is_active:
                                ui.button(icon='close', on_click=lambda: _deselect_customer()).props(
                                    'flat dense round size=xs').style('color:var(--text-light);flex-shrink:0;').tooltip(
                                    'Kunde abwählen')
                            else:
                                ui.icon('chevron_right', size='sm').classes('cust-chevron').style(
                                    'color:var(--text-light);flex-shrink:0;')

                def _select_customer(cust: str):
                    _on_customer_selected(cust)
                    _render_customer_list()

                def _deselect_customer():
                    s['active_customer'] = ''
                    s['active_project_path'] = ''
                    s['source_files'] = []
                    s['translation_files'] = []
                    s['findings'] = []
                    s['current_score'] = -1
                    _refresh_file_list()
                    _refresh_pairing_display()
                    _refresh_auftrag_list()
                    _update_start_btn()
                    _refresh_results_area()
                    try:
                        _refresh_project_folders()
                    except Exception:
                        pass
                    _render_customer_list()

                def _render_customer_list(query: str = ''):
                    container = refs.get('customer_list_container')
                    if not container:
                        return
                    container.clear()
                    all_customers = _load_customers()
                    active = s.get('active_customer', '')
                    q = query.strip().lower()

                    with container:
                        # Wenn Kunde aktiv UND nicht gesucht wird: Nur aktiven Kunden zeigen
                        if active and not q:
                            _render_customer_card(active, True)
                            # Link um anderen Kunden zu wählen
                            ui.button('Kunden wechseln', icon='swap_horiz',
                                on_click=lambda: (refs['customer_search'].props('autofocus'),
                                                   refs['customer_search'].run_method('focus'))
                            ).props('flat dense no-caps size=sm').style(
                                'color:var(--text-muted);font-size:var(--fs-sm);')
                            return

                        # Filtern (zentrale, umlaut-/unterstrich-tolerante Funktion)
                        if q:
                            filtered = _customers_mod.filter_customers(
                                all_customers, query, limit=15)
                        else:
                            filtered = _customers_mod.filter_customers(
                                all_customers, '', limit=15)

                        for cust in filtered:
                            _render_customer_card(cust, cust == active)

                        if not filtered:
                            with ui.row().classes('w-full items-center gap-2').style('padding:12px;'):
                                ui.icon('search_off', size='xs').style('color:var(--text-light);')
                                ui.label(f'Kein Kunde gefunden').style('font-size:var(--fs-sm);color:var(--text-light);')

                # Initial rendern
                _render_customer_list()

                # -- 2. Projekte --
                with ui.card().classes('w-full').props('flat bordered').style('padding:12px;'):
                    with ui.row().classes('w-full items-center gap-2').style('margin-bottom:8px;'):
                        ui.icon('folder_special', size='xs').style('color:var(--primary);')
                        ui.label('Projekte').style(
                            'font-size:var(--fs-lg);font-weight:700;color:var(--text);flex-grow:1;')
                    refs['auftrag_container'] = ui.column().classes('w-full gap-1')
                    with refs['auftrag_container']:
                        if not s.get('active_customer'):
                            with ui.column().classes('w-full items-center').style('gap:4px;padding:12px 0;'):
                                ui.icon('touch_app', size='sm').style('color:var(--text-light);opacity:.4;')
                                ui.label('Wähle links einen Kunden').style(
                                    'font-size:var(--fs-sm);color:var(--text-light);')
                                ui.label('um seine Projekte zu sehen').style(
                                    'font-size:var(--fs-xs);color:var(--text-muted);')
                    refs['auftrag_info'] = ui.label('').style('font-size:var(--fs-sm);color:var(--success);margin-top:4px;')
                refs['auftrag_info'].visible = False

                # -- 3. Dateien & Zuordnung (einheitlicher Block) --
                with ui.card().classes('w-full').props('flat bordered').style('padding:16px;'):
                    with ui.row().classes('w-full items-center gap-2').style('margin-bottom:12px;'):
                        ui.icon('folder_open', size='xs').style('color:var(--primary);')
                        ui.label('Dateien & Zuordnung').style(
                            'font-size:var(--fs-lg);font-weight:700;color:var(--text);flex-grow:1;')

                    # Zuordnungs-Container (wird dynamisch befüllt)
                    refs['project_folders_container'] = ui.column().classes('w-full gap-2')

                    # Upload-Zonen mit Drag & Drop (farbcodiert, mit Titel-Caption)
                    # Wird ausgeblendet sobald Dateien vorhanden sind — dann
                    # erfolgt das Nachladen ueber die "Weitere hochladen"-Buttons
                    # in der Ordner-Ansicht (vermeidet verwaiste Labels).
                    _upload_area = ui.column().classes('w-full gap-0').style('margin-top:12px;')
                    refs['upload_area'] = _upload_area
                    with _upload_area:
                        with ui.row().classes('w-full gap-3'):
                            # --- Ausgangstext (blau) ---
                            with ui.column().classes('flex-1').style('gap:5px;min-width:0;'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('description', size='xs').style('color:var(--role-source);')
                                    ui.label('Ausgangstext').style(
                                        'font-size:var(--fs-sm);font-weight:700;color:var(--role-source);'
                                        'text-transform:uppercase;letter-spacing:.5px;')
                                src_drop = ui.upload(
                                    label='Klicken oder Datei hierher ziehen',
                                    on_upload=_handle_source_upload,
                                    auto_upload=True, multiple=True, max_file_size=50_000_000,
                                ).props('accept=".pdf,.docx,.txt,.doc,.png,.jpg,.jpeg,.tiff,.tif" flat dense'
                                ).classes('w-full').style(
                                    'border:2px dashed var(--border-info);border-radius:var(--radius-md);'
                                    'min-height:64px;background:var(--bg-info-tint);')
                                refs['src_drop'] = src_drop
                            # --- Übersetzung (grün) ---
                            with ui.column().classes('flex-1').style('gap:5px;min-width:0;'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('translate', size='xs').style('color:var(--success);')
                                    ui.label('Übersetzung').style(
                                        'font-size:var(--fs-sm);font-weight:700;color:var(--success);'
                                        'text-transform:uppercase;letter-spacing:.5px;')
                                tgt_drop = ui.upload(
                                    label='Klicken oder Datei hierher ziehen',
                                    on_upload=_handle_translation_upload,
                                    auto_upload=True, multiple=True, max_file_size=50_000_000,
                                ).props('accept=".pdf,.docx,.txt,.doc,.png,.jpg,.jpeg,.tiff,.tif" flat dense'
                                ).classes('w-full').style(
                                    'border:2px dashed var(--border-success);border-radius:var(--radius-md);'
                                    'min-height:64px;background:var(--bg-success-tint);')
                                refs['tgt_drop'] = tgt_drop
                        ui.label('Unterstützt: PDF, DOCX, TXT, Bilder (OCR) · max. 50 MB').style(
                            'font-size:var(--fs-xs);color:var(--text-light);margin-top:8px;')

                # Versteckte Backend-Container
                refs['src_container'] = ui.column().style('display:none;')
                refs['tgt_container'] = ui.column().style('display:none;')
                refs['pairing_label'] = ui.label('').style('display:none;')
                refs['pairing_container'] = ui.column().style('display:none;')

                # -- Schnellprüfung: Dateien ohne Kunde prüfen --
                with ui.expansion('Schnellprüfung (ohne Projekt)', icon='bolt', value=False).classes('w-full').props(
                    'dense header-class="text-xs font-semibold text-gray-500"'
                ):
                    ui.label('Dateien direkt prüfen — ohne Kundenzuordnung.').style(
                        'font-size:var(--fs-sm);color:var(--text-light);padding:4px 0;')
                    # Versteckte Uploads (immer display:none — zuverlaessiger
                    # pickFiles-Trigger fuer alle "Weitere hochladen"-Buttons)
                    _quick_src = ui.upload(on_upload=_handle_source_upload, auto_upload=True,
                        multiple=True, max_file_size=50_000_000).props(
                        'accept=".pdf,.docx,.txt,.doc,.png,.jpg,.jpeg,.tiff,.tif"').style('display:none;')
                    _quick_tgt = ui.upload(on_upload=_handle_translation_upload, auto_upload=True,
                        multiple=True, max_file_size=50_000_000).props(
                        'accept=".pdf,.docx,.txt,.doc,.png,.jpg,.jpeg,.tiff,.tif"').style('display:none;')
                    refs['src_picker'] = _quick_src
                    refs['tgt_picker'] = _quick_tgt
                    with ui.row().classes('w-full gap-2'):
                        ui.button('Ausgangstext wählen', icon='description',
                            on_click=lambda: _quick_src.run_method('pickFiles')).props(
                            'outline dense no-caps size=sm').classes('flex-1').style('color:var(--role-source);')
                        ui.button('Übersetzung wählen', icon='translate',
                            on_click=lambda: _quick_tgt.run_method('pickFiles')).props(
                            'outline dense no-caps size=sm').classes('flex-1').style('color:var(--success);')

                # -- 6. Settings expansion --
                with ui.expansion('Glossar · Sprachen · Prüfmodule', icon='tune').classes('w-full').props(
                    'dense header-class="text-xs font-semibold text-gray-500"'
                ):
                    ui.label('GLOSSAR').classes('section-label').style('margin-top:8px;')
                    with ui.row().classes('w-full items-center gap-2'):
                        refs['glossary_label'] = ui.label('Kein Glossar').style(
                            'font-size:var(--fs-sm);color:var(--text-light);flex-grow:1;')
                        _glossary_picker = ui.upload(
                            on_upload=_handle_glossary_upload, auto_upload=True,
                            max_file_size=50_000_000).props('accept=".csv,.xlsx,.json"').style('display:none;')
                        ui.button('Laden', icon='upload_file',
                            on_click=lambda: _glossary_picker.run_method('pickFiles')).props(
                            'flat dense no-caps size=sm')
                    term_inp = ui.input(placeholder='Quelle=Übersetzung (Enter)').classes('w-full').props('dense outlined')
                    term_inp.on('keydown.enter', lambda: _add_manual_term(term_inp))
                    with ui.row().classes('w-full items-center gap-2').style('margin-top:4px;'):
                        refs['glossary_count_label'] = ui.label(
                            f'{len(s.get("manual_glossary_terms", {}))} Begriffe'
                        ).style('font-size:var(--fs-xs);color:var(--text-light);flex-grow:1;')
                        ui.button('Bearbeiten', icon='edit_note',
                            on_click=lambda: _open_glossary_editor()).props(
                            'flat dense no-caps size=sm')
                    ui.separator().style('margin:8px 0;')

                    ui.label('SPRACHEN').classes('section-label')
                    with ui.row().classes('w-full gap-2'):
                        refs['src_lang_sel'] = ui.select(LANGUAGES, value='Auto-Erkennung',
                            label='Quellsprache').classes('flex-1').props('dense outlined')
                        refs['tgt_lang_sel'] = ui.select(LANGUAGES, value='Auto-Erkennung',
                            label='Zielsprache').classes('flex-1').props('dense outlined')
                    ui.separator().style('margin:8px 0;')

                    ui.label('PRÜFMODULE').classes('section-label')
                    with ui.grid(columns=2).classes('w-full gap-0'):
                        ui.checkbox('Zahlen & Formate', value=True,
                            on_change=lambda e: phase_flags.__setitem__('phase1', getattr(e, 'value', getattr(e, 'args', True)))
                        ).props('dense size=sm').tooltip(
                            'Zahlen, Maßeinheiten, URLs, Klammern, Anführungszeichen')
                        ui.checkbox('Inhalt & Konsistenz', value=True,
                            on_change=lambda e: phase_flags.__setitem__('phase2', getattr(e, 'value', getattr(e, 'args', True)))
                        ).props('dense size=sm').tooltip(
                            'Terminologie, Eigennamen, Vollständigkeit, HTML-Tags, Zeichensetzung')
                        ui.checkbox('Grammatik & Stil', value=True,
                            on_change=lambda e: phase_flags.__setitem__('phase3', getattr(e, 'value', getattr(e, 'args', True)))
                        ).props('dense size=sm').tooltip(
                            'Grammatik, Lesbarkeit, Stilistik, Wortwiederholungen, Passiv')
                        _ki_cb = ui.checkbox('KI-Prüfung', value=False,
                            on_change=lambda e: phase_flags.__setitem__('phase4', getattr(e, 'value', getattr(e, 'args', False)))
                        ).props('dense size=sm')

                    def _fetch_ollama_models() -> list:
                        try:
                            r = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=2)
                            return [m['name'] for m in json.loads(r.read()).get('models', [])]
                        except Exception:
                            return []
                    available_models = _fetch_ollama_models()
                    if available_models:
                        _ki_cb.tooltip('Ollama läuft – KI-Analyse mit LLM aktivieren')
                        sel = ui.select(options=available_models, value=available_models[0],
                            label='KI-Modell', with_input=True).classes('w-full').props('dense outlined')
                        sel.bind_value(ollama_model, 'v')
                    else:
                        _ki_cb.disable()
                        _ki_cb.tooltip('Ollama nicht gestartet – KI-Prüfung nicht verfügbar')
                        inp = ui.input(value='llama3.2:3b', label='KI-Modell').classes('w-full').props('dense outlined')
                        inp.bind_value(ollama_model, 'v')

            # -- 7. Analyse starten button (sticky) --
            with ui.element('div').style(
                'position:sticky;bottom:0;background:var(--surface);padding:12px 16px 8px;z-index:10;'
                'border-top:1px solid rgba(0,0,0,.06);'
            ):
                with ui.row().classes('w-full gap-2 items-center no-wrap'):
                    refs['start_btn'] = ui.button(
                        'Analyse starten', icon='play_arrow', on_click=_start_analysis,
                    ).classes('flex-grow font-bold').props('no-caps size=lg unelevated').style(
                        'background:linear-gradient(135deg,#0f2744 0%,#1a365d 100%);'
                        'color:white;height:48px;font-size:var(--fs-lg);border-radius:8px;')
                    refs['start_btn'].tooltip('Tastenkürzel: Strg+Enter')
                    refs['cancel_btn'] = ui.button(
                        icon='stop', on_click=_request_cancel,
                    ).props('no-caps size=lg unelevated').style(
                        'background:var(--error);color:white;height:48px;width:48px;border-radius:8px;')
                    refs['cancel_btn'].tooltip('Analyse abbrechen')
                    refs['cancel_btn'].visible = False
                refs['path_label'] = ui.label('').style(
                    'font-size:var(--fs-sm);color:var(--text-light);margin-top:4px;text-align:center;word-break:break-all;')

            # -- Projekt list refresh function --
            def _refresh_auftrag_list():
                container = refs['auftrag_container']
                if not container:
                    return
                container.clear()
                customer = s.get('active_customer', '')
                with container:
                    if not customer:
                        return
                    projects = _list_projects(customer)
                    # Auto-Select: Wenn nur 1 Projekt und noch keiner gewählt
                    if len(projects) == 1 and not s.get('active_project_path'):
                        proj = projects[0]
                        proj_path = _get_project_path(customer, proj)
                        if not proj_path:
                            proj_path = os.path.join(_get_customer_path(customer), proj)
                        _select_auftrag(proj, proj_path,
                            _count_files_in_folder(_find_source_folder(proj_path) or ''),
                            _count_files_in_folder(_find_translation_folder(proj_path) or ''))
                        return
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(f'{len(projects)} {"Projekt" if len(projects) == 1 else "Projekte"}').style(
                            'font-size:var(--fs-md);font-weight:600;color:var(--text);')
                        def _new_auftrag():
                            today = datetime.now().strftime('%Y-%m-%d')
                            existing_today = [p for p in _list_projects(customer) if today in p]
                            with ui.dialog() as adlg, ui.card().style('width:440px;'):
                                ui.label('Neues Projekt').style('font-size:var(--fs-xl);font-weight:700;color:var(--text);')
                                with ui.row().classes('w-full items-center gap-4').style('margin-top:4px;'):
                                    with ui.row().classes('items-center gap-1'):
                                        ui.icon('business', size='xs').style('color:var(--text-muted);')
                                        ui.label(_display_name(customer)).style('font-size:var(--fs-md);color:var(--text-muted);')
                                    with ui.row().classes('items-center gap-1'):
                                        ui.icon('today', size='xs').style('color:var(--text-muted);')
                                        ui.label(datetime.now().strftime('%d.%m.%Y')).style('font-size:var(--fs-md);color:var(--text-muted);')
                                desc_input = ui.input(
                                    label='Projektbeschreibung',
                                    placeholder='z.B. Vertrag, AGB, Handbuch...'
                                ).classes('w-full').props('outlined dense').style('margin-top:12px;')
                                if existing_today:
                                    with ui.column().classes('w-full gap-1').style(
                                        'background:var(--bg-warning-soft);padding:10px 12px;border-radius:6px;margin-top:8px;'):
                                        ui.label(f'Heute existieren bereits {len(existing_today)} Projekt(e):').style(
                                            'font-size:var(--fs-sm);font-weight:600;color:var(--warning-text);')
                                        for ep in existing_today[:3]:
                                            ui.label(f'• {_display_name(ep)}').style('font-size:var(--fs-sm);color:var(--warning-text);')
                                        ui.label('Geben Sie eine Beschreibung ein um ein weiteres Projekt zu erstellen.').style(
                                            'font-size:var(--fs-sm);color:var(--warning);margin-top:4px;')
                                with ui.row().classes('w-full justify-end gap-2').style('margin-top:16px;'):
                                    ui.button('Abbrechen', on_click=adlg.close).props('flat no-caps')
                                    def _create():
                                        desc = (desc_input.value or '').strip()
                                        if not desc and existing_today:
                                            ui.notify('Bitte Beschreibung eingeben (Projekt für heute existiert bereits)', type='warning')
                                            return
                                        if desc:
                                            safe_desc = re.sub(r'[^\w\-äöüÄÖÜß ]', '', desc).strip().replace(' ', '_')
                                            folder_suffix = f'{customer}_{safe_desc}'
                                        else:
                                            folder_suffix = customer
                                        project_path = _ensure_project(folder_suffix, today)
                                        ui.notify(f'Projekt angelegt: {_display_name(folder_suffix)}', type='positive')
                                        adlg.close()
                                        # Neues Projekt direkt auswählen
                                        proj_name = os.path.basename(project_path) if project_path else f'{today}_{folder_suffix}'
                                        _select_auftrag(proj_name, project_path, 0, 0)
                                        _refresh_auftrag_list()
                                    ui.button('Anlegen', icon='add', on_click=_create).props(
                                        'no-caps unelevated').style('background:var(--bg-primary);color:white;')
                                desc_input.on('keydown.enter', _create)
                            adlg.open()
                        ui.button('Neues Projekt', icon='add', on_click=_new_auftrag).props(
                            'flat dense no-caps size=sm color=primary')
                    if not projects:
                        ui.label('Noch keine Projekte').style('font-size:var(--fs-sm);color:var(--text-light);padding:8px 0;')
                        return
                    with_files = []
                    without_files = []
                    for proj in projects[:20]:
                        proj_path = _get_project_path(customer, proj)
                        if not proj_path:
                            proj_path = os.path.join(_get_customer_path(customer), proj)
                        src_dir = _find_source_folder(proj_path)
                        tgt_dir = _find_translation_folder(proj_path)
                        n_src = _count_files_in_folder(src_dir) if src_dir else 0
                        n_tgt = _count_files_in_folder(tgt_dir) if tgt_dir else 0
                        entry = (proj, proj_path, n_src, n_tgt)
                        if n_src + n_tgt > 0:
                            with_files.append(entry)
                        else:
                            without_files.append(entry)
                    for proj, proj_path, n_src, n_tgt in with_files:
                        is_sel = s.get('active_project_path', '') == proj_path
                        with ui.row().classes('w-full items-center gap-2 cursor-pointer cust-card').style(
                            f'border-left:3px solid {"var(--primary)" if is_sel else "var(--surface-border)"};'
                            f'padding:8px 12px;background:{"var(--bg-info-soft)" if is_sel else "transparent"};'
                            f'border-radius:6px;transition:all .15s;flex-wrap:nowrap;'
                            f'{"box-shadow:0 1px 3px rgba(15,39,68,.08);" if is_sel else ""}'
                        ).on('click', lambda _, p=proj, pp=proj_path, ns=n_src, nt=n_tgt:
                             _select_auftrag(p, pp, ns, nt)):
                            with ui.column().classes('gap-1 flex-grow min-w-0'):
                                # Datum aus Ordnername extrahieren (z.B. "2026-03-24_Müller" → "24.03.2026")
                                display_name = proj
                                date_part = proj.split('_')[0] if '_' in proj else proj
                                try:
                                    d = datetime.strptime(date_part, '%Y-%m-%d')
                                    display_name = d.strftime('%d.%m.%Y')
                                    rest = proj[len(date_part)+1:] if '_' in proj else ''
                                    if rest:
                                        display_name += f' — {_display_name(rest)}'
                                except Exception:
                                    pass
                                ui.label(display_name).style(
                                    f'font-size:var(--fs-sm);font-weight:{"700" if is_sel else "600"};'
                                    f'color:{"var(--primary)" if is_sel else "var(--text)"};'
                                    f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%;')
                                with ui.row().classes('items-center gap-1 flex-nowrap'):
                                    with ui.row().classes('items-center gap-1').style(
                                        'background:var(--bg-info-tint);border-radius:10px;padding:1px 7px;'):
                                        ui.icon('description', size='11px').style('color:var(--primary);')
                                        ui.label(str(n_src)).style(
                                            'font-size:var(--fs-xs);font-weight:600;color:var(--primary);')
                                    with ui.row().classes('items-center gap-1').style(
                                        f'background:var(--bg-success-tint);border-radius:10px;padding:1px 7px;'
                                        f'{"opacity:.45;" if n_tgt == 0 else ""}'):
                                        ui.icon('translate', size='11px').style('color:var(--success);')
                                        ui.label(str(n_tgt)).style(
                                            'font-size:var(--fs-xs);font-weight:600;color:var(--success);')
                            ui.icon('chevron_right', size='sm').classes('cust-chevron').style(
                                'color:var(--text-light);flex-shrink:0;')
                    if without_files:
                        n_empty = len(without_files)
                        with ui.row().classes('w-full items-center gap-2').style(
                            'padding:4px 0;margin-top:4px;'):
                            ui.label(f'{n_empty} {"Projekt" if n_empty == 1 else "Projekte"} ohne Dateien').style(
                                'font-size:var(--fs-sm);color:var(--text-light);flex-grow:1;')
                            def _clean_empty():
                                for _, pp, _, _ in without_files:
                                    try:
                                        # Nur löschen wenn wirklich komplett leer
                                        all_empty = all(
                                            not os.listdir(os.path.join(pp, d))
                                            for d in os.listdir(pp)
                                            if os.path.isdir(os.path.join(pp, d))
                                        ) if os.path.isdir(pp) else True
                                        if all_empty:
                                            shutil.rmtree(pp, ignore_errors=True)
                                    except Exception:
                                        pass
                                ui.notify(f'{n_empty} leere Projekte entfernt', type='positive')
                                _refresh_auftrag_list()
                            ui.button('Aufräumen', icon='delete_sweep', on_click=_clean_empty).props(
                                'flat dense no-caps size=xs').style('color:var(--text-light);font-size:var(--fs-sm);')
                        for proj, proj_path, _, _ in without_files[:5]:
                            display = proj
                            try:
                                d = datetime.strptime(proj.split('_')[0], '%Y-%m-%d')
                                display = d.strftime('%d.%m.%Y')
                            except Exception:
                                pass
                            ui.button(display, on_click=lambda _, p=proj, pp=proj_path:
                                _select_auftrag(p, pp, 0, 0)).props(
                                    'flat dense no-caps size=xs').style('font-size:var(--fs-sm);color:var(--text-light);')

            def _select_auftrag(proj_name: str, proj_path: str, n_src: int, n_tgt: int):
                s['active_project_path'] = proj_path
                s['source_files'] = []
                s['translation_files'] = []
                s['excluded_files'] = []
                src_dir = _find_source_folder(proj_path)
                tgt_dir = _find_translation_folder(proj_path)
                if src_dir:
                    s['source_files'] = _list_files_in_folder(src_dir)
                if tgt_dir:
                    s['translation_files'] = _list_files_in_folder(tgt_dir)
                _refresh_project_folders()
                _refresh_file_list()
                _do_autopairing()
                _update_start_btn()
                _refresh_auftrag_list()
                _refresh_results_area()
                if refs['path_label']:
                    refs['path_label'].set_text(proj_name)
                n_s = len(s['source_files'])
                n_t = len(s['translation_files'])
                ui.notify(f'{n_s} Ausgangstexte, {n_t} Übersetzungen geladen', type='positive')

            def _unpair(p):
                """Loest eine einzelne Zuordnung manuell auf (ohne Auto-Pairing,
                das die Dateien sonst sofort wieder paaren wuerde)."""
                src = p.get('source', '')
                tgt = p.get('translation', '')
                s['paired_results'] = [
                    q for q in s.get('paired_results', [])
                    if not (q.get('source') == src and q.get('translation') == tgt)
                ]
                if src:
                    um = list(s.get('unmatched_src', []))
                    if src not in um:
                        um.append(src)
                    s['unmatched_src'] = um
                if tgt:
                    um = list(s.get('unmatched_tgt', []))
                    if tgt not in um:
                        um.append(tgt)
                    s['unmatched_tgt'] = um
                _refresh_pairing_display()
                _update_start_btn()
                try:
                    _refresh_project_folders()
                except Exception:
                    pass
                _refresh_results_area()
                ui.notify('Zuordnung gelöst', type='info')

            def _refresh_project_folders():
                container = refs.get('project_folders_container')
                if not container:
                    return
                container.clear()
                proj_path = s.get('active_project_path', '')
                src_files = s.get('source_files', [])
                tgt_files = s.get('translation_files', [])
                pairs = s.get('paired_results', [])

                if not proj_path or not os.path.isdir(proj_path):
                    if src_files or tgt_files:
                        with container:
                            _render_pairing_status(pairs, src_files, tgt_files)
                    return

                with container:
                    # Legacy aufraumen
                    for old_dir in ('04_Formatierung', '05_Finalisierung', '06_Lieferung',
                                    '03_Angebot', '04_Pruefung', '02_Lektorat', 'source'):
                        old_path = os.path.join(proj_path, old_dir)
                        try:
                            if os.path.isdir(old_path) and not os.listdir(old_path):
                                os.rmdir(old_path)
                        except Exception:
                            pass

                    try:
                        subdirs = sorted([d for d in os.listdir(proj_path)
                            if os.path.isdir(os.path.join(proj_path, d)) and not d.startswith('.')])
                    except OSError:
                        subdirs = []

                    _FI = {
                        '01_Ausgangstext': ('description', 'var(--role-source)', 'source'),
                        '02_Übersetzung': ('translate', 'var(--success)', 'translation'),
                        '02_Übersetzungen': ('translate', 'var(--success)', 'translation'),
                        '02_Uebersetzung': ('translate', 'var(--success)', 'translation'),
                        '02_Uebersetzungen': ('translate', 'var(--success)', 'translation'),
                        '03_Korrektur': ('rate_review', 'var(--warning)', None),
                        '04_Finalisierung_und_Lieferung': ('local_shipping', 'var(--accent)', None),
                    }

                    for folder_name in subdirs:
                        folder_path = os.path.join(proj_path, folder_name)
                        files = _list_files_in_folder(folder_path)
                        icon_info = _FI.get(folder_name, ('folder', 'var(--text-muted)', None))
                        icon_name, icon_color, role = icon_info
                        clean_name = re.sub(r'^\d+_', '', folder_name).replace('_', ' ')

                        if files:
                            with ui.expansion(
                                f'{clean_name} ({len(files)})', icon=icon_name, value=True,
                            ).classes('w-full folder-exp').props(
                                'dense header-class="text-sm font-semibold"'
                            ).style(f'color:{icon_color};'):
                                for fp in files:
                                    fname = os.path.basename(fp)
                                    try:
                                        sz = os.path.getsize(fp)
                                        size_str = f'{sz/1024:.0f} KB' if sz > 1024 else f'{sz} B'
                                    except Exception:
                                        size_str = ''
                                    is_excluded = fp in s.get('excluded_files', [])
                                    row_bg = ('var(--surface-alt)' if is_excluded
                                              else 'var(--surface)')
                                    accent = ('var(--text-light)' if is_excluded
                                              else icon_color)
                                    with ui.row().classes('w-full items-center gap-2 file-row').style(
                                        'padding:7px 10px;border-radius:0 8px 8px 0;margin:3px 0;'
                                        f'border-left:3px solid {accent};background:{row_bg};'
                                        + ('opacity:.6;' if is_excluded else '')):
                                        ui.icon('visibility_off' if is_excluded else 'insert_drive_file',
                                                size='xs').style(f'color:{accent};opacity:.7;')
                                        ui.label(fname).style(
                                            'font-size:var(--fs-md);color:var(--text);flex-grow:1;'
                                            'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
                                            + ('text-decoration:line-through;color:var(--text-light);'
                                               if is_excluded else ''))
                                        if is_excluded:
                                            ui.label('ausgeschlossen').style(
                                                'font-size:var(--fs-xs);color:var(--text-light);'
                                                'font-style:italic;')
                                        else:
                                            ui.label(size_str).style(
                                                'font-size:var(--fs-xs);color:var(--text-light);'
                                                'font-variant-numeric:tabular-nums;')
                                        if is_excluded:
                                            ui.button(icon='restart_alt',
                                                on_click=lambda _, f=fp, r=role: _include_file(f, r or 'source')
                                            ).props('flat dense round size=xs').classes('file-del').style(
                                                'color:var(--primary);').tooltip('Wieder zur Prüfung aufnehmen')
                                        else:
                                            ui.button(icon='close',
                                                on_click=lambda _, f=fp, r=role: _remove_file(f, r or 'source')
                                            ).props('flat dense round size=xs').classes('file-del').style(
                                                'color:var(--text-light);').tooltip('Datei entfernen')
                                if role in ('source', 'translation'):
                                    drop_ref = refs.get('src_picker' if role == 'source' else 'tgt_picker')
                                    if drop_ref:
                                        ui.button('Weitere hochladen', icon='add',
                                            on_click=lambda _, d=drop_ref: d.run_method('pickFiles')
                                        ).props('flat dense no-caps size=xs').style(f'color:{icon_color};margin-top:6px;font-size:var(--fs-xs);')
                        else:
                            with ui.row().classes('w-full items-center gap-2 folder-empty').style(
                                'padding:6px 4px;margin:2px 0;'):
                                ui.icon(icon_name, size='xs').style(f'color:{icon_color};opacity:.45;')
                                ui.label(f'{clean_name}').style(
                                    'font-size:var(--fs-md);color:var(--text-light);flex-grow:1;')
                                ui.label('leer').style('font-size:var(--fs-xs);color:var(--text-light);opacity:.6;')
                                if role in ('source', 'translation'):
                                    drop_ref = refs.get('src_picker' if role == 'source' else 'tgt_picker')
                                    if drop_ref:
                                        ui.button(icon='upload',
                                            on_click=lambda _, d=drop_ref: d.run_method('pickFiles')
                                        ).props('flat dense round size=xs').classes('folder-up').style(
                                            f'color:{icon_color};').tooltip('Datei hochladen')

                    if src_files or tgt_files:
                        ui.element('div').style('height:1px;background:var(--surface-border);margin:14px 0 10px;')
                        ui.label('ZUORDNUNG').classes('section-label').style('margin-bottom:8px;')
                        _render_pairing_status(pairs, src_files, tgt_files)

            def _render_pairing_status(pairs, src_files, tgt_files):
                _IMG_EXTS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp'}
                doc_src = [f for f in src_files if Path(f).suffix.lower() not in _IMG_EXTS]
                n_paired = len(pairs)
                n_total = len(doc_src)
                all_paired = n_paired == n_total and n_total > 0
                with ui.column().classes('w-full gap-2 assign-box'):
                    if pairs:
                        for p in pairs:
                            sn = os.path.basename(p.get('source', ''))
                            tn = os.path.basename(p.get('translation', ''))
                            with ui.row().classes('w-full items-center gap-2 pair-row').style(
                                'padding:7px 10px;background:var(--bg-success-tint);'
                                'border-radius:0 8px 8px 0;border-left:3px solid var(--success);'):
                                ui.icon('check_circle', size='xs').style('color:var(--success);')
                                ui.label(sn).style('font-size:var(--fs-sm);color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                ui.icon('arrow_forward', size='xs').style('color:var(--text-light);')
                                ui.label(tn).style('font-size:var(--fs-sm);color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                ui.button(icon='link_off', on_click=lambda _, pp=p: _unpair(pp)).props(
                                    'flat dense round size=xs').classes('pair-del').style(
                                    'color:var(--text-light);').tooltip('Zuordnung lösen')
                    with ui.row().classes('w-full items-center gap-2'):
                        if all_paired:
                            ui.icon('check_circle', size='xs').style('color:var(--success);')
                            ui.label(f'Alle {n_paired} zugeordnet').style('font-size:var(--fs-sm);font-weight:600;color:var(--success);flex-grow:1;')
                        elif n_paired > 0:
                            ui.icon('info', size='xs').style('color:var(--warning);')
                            ui.label(f'{n_paired} von {n_total} zugeordnet').style('font-size:var(--fs-sm);font-weight:600;color:var(--warning);flex-grow:1;')
                        elif n_total > 0:
                            ui.icon('warning', size='xs').style('color:var(--error);')
                            ui.label('Nicht zugeordnet').style('font-size:var(--fs-sm);font-weight:600;color:var(--error);flex-grow:1;')
                        else:
                            ui.icon('hourglass_empty', size='xs').style('color:var(--text-light);')
                            ui.label('Warte auf Dateien').style('font-size:var(--fs-sm);color:var(--text-light);flex-grow:1;')
                        if not all_paired and (src_files or tgt_files):
                            ui.button('Zuordnen', icon='tune', on_click=_show_pairing_dialog).props('outline dense no-caps size=sm').style('color:var(--primary);font-size:var(--fs-sm);')

            def _toggle_file(fp: str, role: str, checked: bool):
                """Datei zur Prüfung an/abwählen."""
                key = 'source_files' if role == 'source' else 'translation_files'
                lst = list(s.get(key, []))
                if checked and fp not in lst:
                    lst.append(fp)
                elif not checked and fp in lst:
                    lst.remove(fp)
                s[key] = lst
                _do_autopairing()
                _update_start_btn()
                _refresh_results_area()

            if s.get('active_customer'):
                _refresh_auftrag_list()

        # ============ RIGHT PANEL ============
        with ui.column().classes('flex-grow gap-4 min-w-0 p-4').style(
            'min-height:calc(100vh - 56px);'
        ):
            # Progress
            with ui.column().classes('w-full gap-1'):
                refs['progress_bar'] = ui.linear_progress(value=0, show_value=False).classes('w-full')
                refs['progress_bar'].visible = False
                refs['progress_text'] = ui.label('').style('font-size:var(--fs-sm);color:var(--text-muted);')
                refs['progress_text'].visible = False

            # Score card
            refs['score_card'] = ui.card().classes('w-full').props('flat bordered')
            refs['score_card'].visible = False
            with refs['score_card']:
                with ui.row().classes('w-full items-center gap-6').style('padding:16px 24px;'):
                    with ui.element('div').style(
                        'width:96px;height:96px;flex-shrink:0;position:relative;'
                    ):
                        refs['score_ring'] = ui.element('div').classes('score-ring').style(
                            'position:absolute;inset:0;--sc:var(--surface-border-strong);--pct:0%;'
                            'transition:--pct 600ms ease,--sc 600ms ease;')
                        with ui.element('div').classes('score-inner').style(
                            'position:absolute;inset:4px;'
                        ):
                            refs['score_number'] = ui.label('--').style(
                                'font-size:var(--fs-3xl);font-weight:800;color:var(--text-light);')
                    with ui.column().classes('gap-0 flex-grow'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label('Qualitäts-Score').classes('t-label').style('color:var(--text);')
                            refs['score_delta'] = ui.html('').style('margin-left:2px;')
                        refs['score_sublabel'] = ui.label('Noch keine Analyse').style(
                            'font-size:var(--fs-sm);color:var(--text-light);')
                        refs['score_time_label'] = ui.label('').style(
                            'font-size:var(--fs-xs);color:var(--text-light);margin-top:1px;')
                        refs['history_chart'] = ui.html('').style(
                            'margin-top:6px;height:24px;')
                        refs['phase_score_row'] = ui.html('').style('margin-top:2px;')

            # Summary cards
            refs['summary_card'] = ui.card().classes('w-full').props('flat bordered')
            refs['summary_card'].visible = False
            with refs['summary_card'].style('padding:12px 16px;'):
                # Diff-Badge zur vorherigen Analyse
                refs['diff_badge'] = ui.html('').style('margin-bottom:6px;')
                with ui.row().classes('w-full items-stretch gap-2'):
                    for sev_clr, sev_name, ref_key, filt_key, icon, bg in [
                        ('var(--error)', 'Kritisch', 'critical_count', 'critical', 'error', 'var(--bg-error-tint)'),
                        ('var(--warning)', 'Wichtig', 'major_count', 'major', 'warning', 'var(--bg-warning-tint)'),
                        ('var(--text-muted)', 'Hinweise', 'minor_count', 'minor', 'info', 'var(--bg-muted)'),
                    ]:
                        with ui.column().classes('items-center gap-0 flex-1 stat-pill').style(
                            f'padding:8px 4px;background:{bg};color:{sev_clr};'
                        ).on('click', lambda _, k=filt_key: _set_filter(k)) as _pill:
                            refs[f'{ref_key}_pill'] = _pill
                            with ui.row().classes('items-center gap-1'):
                                ui.icon(icon, size='14px').style(f'color:{sev_clr};opacity:.8;')
                                refs[ref_key] = ui.label('0').style(
                                    f'font-size:var(--fs-3xl);font-weight:800;color:{sev_clr};line-height:1;')
                            ui.label(sev_name).style(
                                f'font-size:var(--fs-sm);color:{sev_clr};opacity:.75;font-weight:600;margin-top:2px;')
                # Erledigt-Fortschrittsbalken
                with ui.column().classes('w-full gap-0').style('margin-top:8px;'):
                    with ui.row().classes('w-full items-center justify-between').style('margin-bottom:3px;'):
                        ui.label('Fortschritt').style('font-size:var(--fs-xs);color:var(--text-muted);')
                        refs['done_progress_label'] = ui.label('0 / 0').style(
                            'font-size:var(--fs-xs);color:var(--text-muted);font-weight:600;')
                    with ui.element('div').style(
                        'width:100%;height:6px;border-radius:3px;background:var(--bg-muted);position:relative;overflow:hidden;'
                    ):
                        refs['done_progress_bar'] = ui.element('div').style(
                            'position:absolute;top:0;left:0;bottom:0;width:0%;'
                            'background:var(--success);border-radius:3px;'
                            'transition:width 400ms ease;')
                ui.separator().style('margin:8px 0 6px;')
                with ui.expansion('Top-Kategorien', icon='analytics',
                                  value=bool(s.get('show_category_heatmap', True))
                                  ).classes('w-full').props('dense header-class=text-xs').on(
                    'update:model-value',
                    lambda e: s.update({'show_category_heatmap':
                                        bool(getattr(e, 'args', True))})
                ):
                    refs['category_heatmap'] = ui.column().classes('w-full gap-1').style('margin-top:4px;')
                with ui.expansion('Score je Datei-Paar', icon='insights',
                                  value=bool(s.get('show_per_file_heatmap', True))
                                  ).classes('w-full').props('dense header-class=text-xs').on(
                    'update:model-value',
                    lambda e: s.update({'show_per_file_heatmap':
                                        bool(getattr(e, 'args', True))})
                ):
                    refs['per_file_heatmap'] = ui.column().classes('w-full gap-1').style('margin-top:4px;')

            # Results area (export + filter + findings)
            refs['results_area'] = ui.column().classes('w-full gap-4')
            refs['results_area'].visible = False
            with refs['results_area']:
                with ui.row().classes('w-full gap-1 flex-wrap items-center').style(
                    'padding:6px 8px;background:var(--surface);border-radius:8px;'
                    'border:1px solid var(--surface-border);'
                ):
                    ui.label('Export:').style(
                        'font-size:var(--fs-xs);font-weight:600;color:var(--text-muted);margin-right:4px;')
                    ui.button('PDF', icon='picture_as_pdf',
                        on_click=lambda: _do_export('pdf')).props('outline dense no-caps size=sm')
                    ui.button('Excel', icon='table_chart',
                        on_click=lambda: _do_export('excel')).props('outline dense no-caps size=sm')
                    ui.button('TXT', icon='text_snippet',
                        on_click=lambda: _do_export('txt')).props('flat dense no-caps size=sm')
                    ui.button('ZIP', icon='archive',
                        on_click=lambda: _do_export('zip')).props('outline dense no-caps size=sm').tooltip(
                        'Korrekturpaket als ZIP')
                    # Gefilterter Export
                    with ui.button(icon='filter_alt').props(
                        'flat dense no-caps size=sm color=primary'
                    ).tooltip('Nur sichtbare (gefilterte) Findings exportieren'):
                        with ui.menu():
                            ui.item('Gefilterte als PDF',
                                on_click=lambda: _do_export('pdf', only_filtered=True))
                            ui.item('Gefilterte als Excel',
                                on_click=lambda: _do_export('excel', only_filtered=True))
                            ui.item('Gefilterte als TXT',
                                on_click=lambda: _do_export('txt', only_filtered=True))
                            ui.item('Gefilterte als Korrekturpaket',
                                on_click=lambda: _do_export('zip', only_filtered=True))
                    ui.element('div').classes('flex-grow')
                    # Korrekturschleife: Neue Übersetzung hochladen
                    def _start_correction_loop():
                        with ui.dialog() as cdlg, ui.card().style('width:480px;'):
                            ui.label('Korrigierte Übersetzung hochladen').style(
                                'font-size:var(--fs-xl);font-weight:700;color:var(--text);')
                            ui.label(
                                'Laden Sie die korrigierte Übersetzung hoch. '
                                'Die alte Version bleibt erhalten, die neue wird als aktuelle Version genutzt.'
                            ).style('font-size:var(--fs-sm);color:var(--text-muted);margin:8px 0;')
                            correction_upload = ui.upload(
                                label='Korrigierte Übersetzung hochladen',
                                on_upload=lambda e: _handle_correction_upload(e, cdlg),
                                auto_upload=True, multiple=True, max_file_size=50_000_000,
                            ).props(
                                'accept=".pdf,.docx,.txt,.doc" flat bordered no-thumbnails'
                            ).classes('w-full')
                            with ui.row().classes('w-full justify-end').style('margin-top:12px;'):
                                ui.button('Abbrechen', on_click=cdlg.close).props('flat no-caps')
                        cdlg.open()

                    def _handle_correction_upload(e, dialog):
                        path = _save_upload(e)
                        if not path:
                            return
                        proj_path = s.get('active_project_path', '')
                        if proj_path and os.path.isdir(proj_path):
                            tgt_dir = os.path.join(proj_path, '02_Übersetzung')
                            os.makedirs(tgt_dir, exist_ok=True)
                            fname = os.path.basename(path)
                            stem, ext = os.path.splitext(fname)
                            # Version suffix: _v2, _v3, etc.
                            existing = [f for f in os.listdir(tgt_dir) if f.startswith(stem)]
                            version = len(existing) + 1
                            if version > 1:
                                dest_name = f'{stem}_v{version}{ext}'
                            else:
                                dest_name = fname
                            dest = os.path.join(tgt_dir, dest_name)
                            shutil.copy2(path, dest)
                            # Neue Datei als aktive Übersetzung setzen
                            _add_file(dest, 'translation')
                            ui.notify(f'Korrektur hochgeladen: {dest_name}', type='positive')
                        else:
                            _add_file(path, 'translation')
                            ui.notify(f'Korrektur hochgeladen: {os.path.basename(path)}', type='positive')
                        dialog.close()
                        _refresh_file_list()
                        _do_autopairing()
                        _update_start_btn()
                        try:
                            _refresh_project_folders()
                        except Exception:
                            pass
                        _refresh_results_area()

                    ui.button('Korrektur hochladen', icon='replay',
                        on_click=_start_correction_loop).props(
                        'unelevated dense no-caps size=sm').style(
                        'background:var(--warning);color:white;')

                with ui.row().classes('w-full items-center gap-2 flex-wrap').style(
                    'padding:6px 0;border-bottom:1px solid var(--surface-border);margin-bottom:4px;'
                ):
                    # Severity-Filter als Pill-Tabs mit Farb-Dot
                    _SEV_DOT = {
                        'all': ('', 'var(--primary)'),
                        'critical': ('●', '#dc2626'),
                        'major': ('●', '#ea580c'),
                        'minor': ('●', '#6b7280'),
                    }
                    for key, label_text in [('all', 'Alle'), ('critical', 'Kritisch'),
                                             ('major', 'Wichtig'), ('minor', 'Hinweise')]:
                        dot, dot_clr = _SEV_DOT[key]
                        btn = ui.button(
                            (f'{dot} ' if dot else '') + label_text,
                            on_click=lambda _, k=key: _set_filter(k),
                        ).props('flat dense no-caps size=sm').style(
                            f'border-radius:20px;padding:3px 12px;'
                            f'border:1px solid var(--surface-border);'
                            f'background:var(--surface);color:{dot_clr};'
                            f'font-weight:600;font-size:var(--fs-sm);transition:all .15s;')
                        btn._base_label = label_text
                        btn._dot = dot
                        btn._dot_clr = dot_clr
                        filter_btns[key] = btn
                    ui.separator().props('vertical').style('height:20px;margin:0 4px;')
                    # Toggle: Erledigte ausblenden
                    refs['hide_done_toggle'] = ui.switch('Erledigte ausblenden',
                        value=bool(s.get('hide_done', False)),
                        on_change=lambda e: _toggle_hide_done(getattr(e, 'value', False)),
                    ).props('dense').style('font-size:var(--fs-sm);color:var(--text-muted);')
                    # Counter "X von Y erledigt"
                    refs['done_counter'] = ui.label('').style(
                        'font-size:var(--fs-sm);color:var(--text-muted);font-weight:600;padding:0 4px;')
                    ui.separator().props('vertical').style('height:20px;margin:0 4px;')
                    # Bulk-Aktionen
                    ui.button(icon='done_all',
                        on_click=lambda: _bulk_mark_filtered(True),
                    ).props('flat dense round size=sm').tooltip(
                        'Alle sichtbaren als erledigt markieren'
                    ).style('color:var(--success);')
                    ui.button(icon='remove_done',
                        on_click=lambda: _bulk_mark_filtered(False),
                    ).props('flat dense round size=sm').tooltip(
                        'Alle sichtbaren als offen markieren'
                    ).style('color:var(--text-muted);')
                    # Undo
                    refs['undo_btn'] = ui.button(icon='undo',
                        on_click=lambda: _undo_last(),
                    ).props('flat dense round size=sm').tooltip(
                        'Nichts rückgängig zu machen'
                    ).style('color:var(--primary);')
                    refs['undo_btn'].disable()
                    ui.element('div').classes('flex-grow')
                    # Sortierung
                    _sort_opts = {
                        'default': 'Standard',
                        'severity': 'Schweregrad',
                        'file': 'Datei',
                        'segment': 'Segment',
                        'category': 'Kategorie',
                    }
                    ui.select(_sort_opts,
                        value=s.get('sort_mode', 'default'),
                        on_change=lambda e: _set_sort_mode(getattr(e, 'value', 'default')),
                    ).props('dense outlined options-dense').tooltip(
                        'Findings sortieren'
                    ).style('font-size:var(--fs-sm);min-width:120px;')
                    # Kompakt-Modus Toggle
                    _compact_icon = 'density_small' if s.get('view_mode') == 'normal' else 'density_medium'
                    refs['compact_btn'] = ui.button(icon=_compact_icon,
                        on_click=lambda: _toggle_view_mode(),
                    ).props('flat dense round size=sm').tooltip(
                        'Kompakt-Ansicht umschalten'
                    ).style('color:var(--text-muted);')
                    refs['search_input'] = ui.input(placeholder='Suchen...',
                        on_change=_on_search_change).props('dense clearable').classes('w-52')
                    refs['search_counter'] = ui.label('').style(
                        'font-size:var(--fs-xs);color:var(--text-muted);white-space:nowrap;padding:0 2px;')
                    ui.button(icon='keyboard',
                        on_click=lambda: _show_keyboard_help(),
                    ).props('flat dense round size=sm').tooltip(
                        'Tastatur-Kürzel anzeigen (?)'
                    ).style('color:var(--text-muted);')

            # Findings container
            refs['findings_container'] = ui.column().classes('w-full gap-0').style(
                'min-height:200px;')

            # Welcome / Preview area (dynamisch je nach Zustand)
            refs['welcome_area'] = ui.column().classes('w-full gap-4')
            # Text-Vorschau Container (für Datei-Preview vor Analyse)
            refs['preview_area'] = ui.column().classes('w-full gap-2')
            refs['preview_area'].visible = False

    # Beim Seitenaufruf: Vorhandenen State wiederherstellen
    # Footer mit Tastatur-Quick-Reference (sticky am Bildschirm-Boden)
    with ui.footer().classes('items-center justify-center').style(
        'background:rgba(15,39,68,0.95);color:var(--text-muted);padding:4px 16px;'
        'font-size:var(--fs-xs);min-height:24px;'
    ):
        with ui.row().classes('items-center gap-3 flex-wrap justify-center'):
            for keys, desc in [
                ('Strg+Enter', 'Start'),
                ('Esc', 'Abbruch'),
                ('j/k', 'Naechstes/Voriges'),
                ('x', 'Erledigt'),
                ('1-3', 'Filter'),
                ('?', 'Hilfe'),
            ]:
                with ui.row().classes('items-center gap-1'):
                    ui.label(keys).style(
                        'font-family:monospace;font-weight:700;color:white;'
                        'background:rgba(255,255,255,0.12);padding:1px 6px;border-radius:3px;'
                        'font-size:var(--fs-xs);')
                    ui.label(desc).style('color:var(--text-muted);font-size:var(--fs-xs);')

    _refresh_file_list()
    _refresh_pairing_display()
    _refresh_results_area()
    if s.get('active_customer'):
        _try_refresh_auftrag()
        try:
            _refresh_customer_info()
        except Exception:
            pass
        try:
            _refresh_project_folders()
        except Exception:
            pass
    _update_start_btn()

    # URL-Parameter auswerten: /?kunde=X&auftrag=Y oeffnet Kunde + Projekt direkt
    # (Navigation von der Kunden- und Kalender-Seite). Laeuft NACH dem
    # State-Restore, damit eine explizite URL-Auswahl Vorrang hat.
    if kunde:
        try:
            _on_customer_selected(kunde)
            try:
                _render_customer_list()
            except Exception:
                pass
            if auftrag:
                proj_path = _get_project_path(kunde, auftrag)
                if not proj_path or not os.path.isdir(proj_path):
                    # Fallback: Projekt per Namens-/Datums-Praefix suchen
                    for p in _list_projects(kunde):
                        if p == auftrag or p.startswith(auftrag) or auftrag in p:
                            cand = _get_project_path(kunde, p) or os.path.join(
                                _get_customer_path(kunde), p)
                            if os.path.isdir(cand):
                                proj_path, auftrag = cand, p
                                break
                if proj_path and os.path.isdir(proj_path):
                    n_src = _count_files_in_folder(_find_source_folder(proj_path) or '')
                    n_tgt = _count_files_in_folder(_find_translation_folder(proj_path) or '')
                    _select_auftrag(auftrag, proj_path, n_src, n_tgt)
        except Exception as exc:
            _logger.warning('URL-Projektauswahl fehlgeschlagen: %s', exc)


# ===========================================================================
# Page modules (register routes via @ui.page on import)
# ===========================================================================
import nicegui_app.page_kalender  # noqa: E402, F401
import nicegui_app.page_kunden  # noqa: E402, F401



# ===========================================================================
# Run
# ===========================================================================
def _find_free_port(start: int = 9000, end: int = 9100) -> int:
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return start


if __name__ in {'__main__', '__mp_main__'}:
    port = _find_free_port()
    ui.run(
        title='Qualitäts-Framework -- Professional Edition',
        port=port,
        reload=False,
        show=True,
        dark=False,
        favicon='✅',
        native=False,
        reconnect_timeout=10.0,
        storage_secret='qf-session-secret-2026',
    )
