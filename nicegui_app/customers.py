# -*- coding: utf-8 -*-
"""Kunden- und Projekt-Verzeichnis-Logik (pure file-system functions).

Alle Funktionen sind reine Helfer ohne Abhaengigkeit zu NiceGUI oder
globalem App-State. `base_path` (= settings['projects_base_path']) wird
explizit als Parameter durchgereicht — testbar, mockbar.

Unterstuetzte Verzeichnis-Strukturen:
  A) `<base>/<YYYY-MM-DD>_<Kunde>/...`            (flach am Top-Level)
  B) `<base>/<Monatsname>_<YYYY>/<YYYY-MM-DD>_<Kunde>/...`  (neue Struktur)
  C) `<base>/<Kunde>/<YYYY-MM-DD>/...`            (alte Struktur)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import time
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------
PROJECT_FOLDERS = [
    '01_Ausgangstext', '02_Übersetzung', '03_Korrektur',
    '04_Finalisierung_und_Lieferung',
]

MONTH_NAMES_DE = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
    5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember',
}

# Strenger Match fuer Monatsordner ("Maerz_2025"); verhindert dass
# Kundenordner wie "Maier_GmbH" als Monatsordner missinterpretiert werden.
MONTH_FOLDER_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(mn) for mn in MONTH_NAMES_DE.values()) + r')_\d{4}$'
)

# YYYY-MM-DD am Anfang, getrennt von Kundenname durch _ / Space / -
_DATE_PREFIX_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})[ _\-](.+)$')
_DATE_ONLY_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


# ---------------------------------------------------------------------------
# Reine Helfer
# ---------------------------------------------------------------------------
def sanitize_folder_name(name: str) -> str:
    """Macht aus einem Kundennamen einen sicheren Ordnernamen.

    Entfernt Path-Traversal-relevante Zeichen, normalisiert Whitespace.
    Schuetzt vor `..`, `/`, `\\` etc. Liefert nie leeren String.
    """
    if not name:
        return 'Unbenannt'
    clean = name.strip()
    for ch in r'<>:"/\|?*':
        clean = clean.replace(ch, '')
    clean = clean.replace(' & ', '_').replace('&', '_')
    while '  ' in clean:
        clean = clean.replace('  ', ' ')
    clean = clean.replace(' ', '_')
    clean = clean.strip('. ')
    return clean or 'Unbenannt'


def display_name(folder_name: str) -> str:
    """Konvertiert Ordnernamen in lesbaren Anzeigenamen.

    Beispiel: 'Finnland_GmbH' -> 'Finnland GmbH'
    """
    return (folder_name or '').replace('_', ' ')


# ---------------------------------------------------------------------------
# Pfad-Resolution (alte/neue Struktur)
# ---------------------------------------------------------------------------
def get_customer_path(base_path: str, customer: str) -> str:
    """Gibt den Pfad zum Kundenordner zurueck (auch wenn nur virtuell).

    Bei alter Struktur: `<base>/<Kunde>` (existiert physisch).
    Bei neuer Struktur: gibt denselben Pfad zurueck, auch wenn er nicht
    existiert — wird fuer kundeninfo.json/Glossar trotzdem genutzt.
    """
    return os.path.join(base_path or '', customer or '')


def find_source_folder(project_path: str) -> str:
    """Findet den Source-Ordner innerhalb eines Projekts."""
    if not project_path:
        return ''
    for name in ('01_Ausgangstext', 'source', 'Ausgangstext'):
        p = os.path.join(project_path, name)
        if os.path.isdir(p):
            return p
    return ''


def find_translation_folder(project_path: str) -> str:
    """Findet den Translation-Ordner innerhalb eines Projekts."""
    if not project_path:
        return ''
    for name in ('02_Übersetzung', '02_Übersetzungen', '03_Übersetzung', 'translation'):
        p = os.path.join(project_path, name)
        if os.path.isdir(p):
            return p
    return ''


def count_files_in_folder(folder_path: str) -> int:
    """Zaehlt sichtbare Dateien (keine Subdirs, keine Dotfiles)."""
    if not folder_path or not os.path.isdir(folder_path):
        return 0
    try:
        return len([
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.')
        ])
    except OSError:
        return 0


def list_files_in_folder(folder_path: str) -> List[str]:
    """Listet absolute Pfade aller sichtbaren Dateien (sortiert)."""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    try:
        return sorted([
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.')
        ])
    except OSError:
        return []


# ---------------------------------------------------------------------------
# Kunden-/Projekt-Discovery
# ---------------------------------------------------------------------------
def load_customers(base_path: str) -> List[str]:
    """Listet alle bekannten Kunden in der Projekt-Basis.

    Erkennt alle 3 Strukturen (A/B/C). Sortiert alphabetisch.
    """
    if not base_path or not os.path.isdir(base_path):
        return []
    customers: set = set()
    try:
        for d in os.listdir(base_path):
            full = os.path.join(base_path, d)
            if not os.path.isdir(full) or d.startswith(('.', '_')):
                continue
            m = _DATE_PREFIX_RE.match(d)
            if m:
                customers.add(m.group(2))
            elif MONTH_FOLDER_RE.match(d):
                try:
                    for proj_dir in os.listdir(full):
                        pm = _DATE_PREFIX_RE.match(proj_dir)
                        if pm:
                            customers.add(pm.group(2))
                except OSError:
                    continue
            else:
                customers.add(d)
    except OSError:
        pass
    return sorted(customers)


def list_projects_full(base_path: str, customer: str) -> List[Tuple[str, str]]:
    """Listet alle Projekte eines Kunden mit (Name, Vollpfad).

    Sortiert absteigend nach Name (neueste zuerst).
    """
    if not base_path or not customer or not os.path.isdir(base_path):
        return []
    results: List[Tuple[str, str]] = []
    cust_lower = customer.lower()
    try:
        for top_dir in os.listdir(base_path):
            top_path = os.path.join(base_path, top_dir)
            if not os.path.isdir(top_path) or top_dir.startswith(('.', '_')):
                continue
            # Variante A: Top-Level Datum_Kunde
            m_top = _DATE_PREFIX_RE.match(top_dir)
            if m_top and m_top.group(2).lower() == cust_lower:
                results.append((top_dir, top_path))
                continue
            if MONTH_FOLDER_RE.match(top_dir):
                # Variante B: Monatsordner
                try:
                    for proj_dir in os.listdir(top_path):
                        proj_path = os.path.join(top_path, proj_dir)
                        if not os.path.isdir(proj_path):
                            continue
                        proj_lower = proj_dir.lower()
                        if proj_lower.endswith(f'_{cust_lower}') or proj_lower == cust_lower:
                            results.append((proj_dir, proj_path))
                except OSError:
                    continue
            elif top_dir == customer:
                # Variante C: Alte Struktur
                try:
                    for sub in os.listdir(top_path):
                        sub_path = os.path.join(top_path, sub)
                        if os.path.isdir(sub_path) and not sub.startswith('.'):
                            results.append((sub, sub_path))
                except OSError:
                    continue
    except OSError:
        pass
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def list_projects(base_path: str, customer: str) -> List[str]:
    """Wie list_projects_full, aber nur Projekt-Namen (sortiert, dedupliziert)."""
    return sorted({name for name, _ in list_projects_full(base_path, customer)}, reverse=True)


def get_project_path(base_path: str, customer: str, proj_name: str) -> str:
    """Liefert den Vollpfad zu einem konkreten Projekt eines Kunden."""
    for name, path in list_projects_full(base_path, customer):
        if name == proj_name:
            return path
    return ''


def scan_project_dates(base_path: str) -> Dict[str, List[str]]:
    """Scannt alle Projekte und liefert ein Mapping `Datum -> [Kunden]`.

    Erkennt alle 3 Strukturen. Pro Tag werden Kunden dedupliziert + sortiert.
    Wird vom Kalender-View genutzt.
    """
    result: Dict[str, List[str]] = {}
    if not base_path or not os.path.isdir(base_path):
        return result
    try:
        for top in os.listdir(base_path):
            top_path = os.path.join(base_path, top)
            if not os.path.isdir(top_path) or top.startswith(('.', '_')):
                continue
            # Variante A
            m_top = _DATE_PREFIX_RE.match(top)
            if m_top:
                result.setdefault(m_top.group(1), []).append(m_top.group(2))
                continue
            # Variante B
            if MONTH_FOLDER_RE.match(top):
                try:
                    for proj in os.listdir(top_path):
                        if not os.path.isdir(os.path.join(top_path, proj)):
                            continue
                        m = _DATE_PREFIX_RE.match(proj)
                        if m:
                            result.setdefault(m.group(1), []).append(m.group(2))
                except OSError:
                    continue
            else:
                # Variante C: <Kunde>/<YYYY-MM-DD>/
                try:
                    for sub in os.listdir(top_path):
                        if _DATE_ONLY_RE.match(sub) and os.path.isdir(os.path.join(top_path, sub)):
                            result.setdefault(sub, []).append(top)
                except OSError:
                    continue
    except OSError:
        pass
    for k in list(result.keys()):
        result[k] = sorted(set(result[k]))
    return result


# ---------------------------------------------------------------------------
# Schreibende Operationen
# ---------------------------------------------------------------------------
def archive_customer(base_path: str, customer: str) -> bool:
    """Archiviert einen Kunden inkl. aller Projekte (alte UND neue Struktur).

    Verschiebt Daten unter `<base>/_archiv/`. Bei Namens-Konflikten wird
    Timestamp-Suffix angehaengt (kein Datenverlust).

    Returns: True wenn mindestens etwas verschoben wurde.
    """
    if not base_path or not os.path.isdir(base_path) or not customer:
        return False
    archive_dir = os.path.join(base_path, '_archiv')
    os.makedirs(archive_dir, exist_ok=True)
    moved_any = False
    # Variante C (alte Struktur): base/Kunde/
    old_cust = os.path.join(base_path, customer)
    if os.path.isdir(old_cust):
        try:
            target = os.path.join(archive_dir, customer)
            if os.path.exists(target):
                target = os.path.join(archive_dir, f'{customer}_{int(time.time())}')
            shutil.move(old_cust, target)
            moved_any = True
        except Exception as exc:
            _logger.warning('Archivieren (alte Struktur) fehlgeschlagen: %s', exc)
    # Variante B (neue Struktur): base/Monat_YYYY/YYYY-MM-DD_Kunde/
    try:
        for top in os.listdir(base_path):
            if not MONTH_FOLDER_RE.match(top):
                continue
            top_path = os.path.join(base_path, top)
            if not os.path.isdir(top_path):
                continue
            for proj in list(os.listdir(top_path)):
                m = _DATE_PREFIX_RE.match(proj)
                if m and m.group(2) == customer:
                    src_proj = os.path.join(top_path, proj)
                    dst_dir = os.path.join(archive_dir, customer, top)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst_proj = os.path.join(dst_dir, proj)
                    if os.path.exists(dst_proj):
                        dst_proj = os.path.join(dst_dir, f'{proj}_{int(time.time())}')
                    try:
                        shutil.move(src_proj, dst_proj)
                        moved_any = True
                    except Exception as exc:
                        _logger.warning('Archivieren Projekt %s fehlgeschlagen: %s', proj, exc)
    except OSError as exc:
        _logger.warning('Archivieren: Verzeichnis-Iteration fehlgeschlagen: %s', exc)
    return moved_any


# ---------------------------------------------------------------------------
# Kunden-Info (kundeninfo.json)
# ---------------------------------------------------------------------------
def load_customer_info(base_path: str, customer: str) -> Dict[str, Any]:
    """Laedt kundeninfo.json aus dem Kundenordner."""
    info_path = os.path.join(get_customer_path(base_path, customer), 'kundeninfo.json')
    try:
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_customer_info(base_path: str, customer: str, info: Dict[str, Any]) -> bool:
    """Speichert kundeninfo.json in den Kundenordner."""
    try:
        cpath = get_customer_path(base_path, customer)
        os.makedirs(cpath, exist_ok=True)
        with open(os.path.join(cpath, 'kundeninfo.json'), 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return True
    except Exception as exc:
        _logger.error('Kundeninfo speichern fehlgeschlagen: %s', exc)
        return False


# ---------------------------------------------------------------------------
# Projekt erstellen
# ---------------------------------------------------------------------------
def ensure_project(
    base_path: str,
    customer: str,
    date_str: str = '',
    project_folders: List[str] | None = None,
    month_names: Dict[int, str] | None = None,
) -> str:
    """Erstellt Projektverzeichnis-Struktur und liefert den Projektpfad.

    Legt Monat-Ordner (Variante B) und alle Unterordner an.
    Kopiert ggf. vorhandene kundeninfo.json aus alter Struktur.
    """
    if not base_path:
        return ''
    if project_folders is None:
        project_folders = PROJECT_FOLDERS
    if month_names is None:
        month_names = MONTH_NAMES_DE
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    try:
        parsed = datetime.strptime(date_str, '%Y-%m-%d')
        date_str = parsed.strftime('%Y-%m-%d')
        month_num = parsed.month
        year_str = parsed.strftime('%Y')
    except ValueError:
        _logger.warning('ensure_project: ungültiges Datum %r → heute', date_str)
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        month_num = now.month
        year_str = now.strftime('%Y')
    safe_customer = sanitize_folder_name(customer)
    month_folder = f'{month_names.get(month_num, str(month_num))}_{year_str}'
    project_dir = os.path.join(base_path, month_folder, f'{date_str}_{safe_customer}')
    for folder in project_folders:
        os.makedirs(os.path.join(project_dir, folder), exist_ok=True)
    info_path = os.path.join(project_dir, 'kundeninfo.json')
    if not os.path.exists(info_path):
        old_info = os.path.join(base_path, safe_customer, 'kundeninfo.json')
        if os.path.exists(old_info):
            try:
                shutil.copy2(old_info, info_path)
            except Exception:
                pass
        else:
            try:
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump({'name': customer, 'typ': 'firma'}, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    return project_dir


def get_project_folders(project_path: str, project_folders: List[str] | None = None) -> Dict[str, str]:
    """Liefert Mapping {Ordnername: Vollpfad} fuer alle Projektordner."""
    folders = project_folders if project_folders is not None else PROJECT_FOLDERS
    return {f: os.path.join(project_path, f) for f in folders}
