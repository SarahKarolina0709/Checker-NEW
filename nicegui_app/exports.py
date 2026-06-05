# -*- coding: utf-8 -*-
"""Export-Funktionen: TXT, Excel, PDF, Korrekturpaket (ZIP).

Reine Funktionen — kein UI-Zugriff, kein app.storage. Aufrufer (main.py)
liefert: findings (List[QAIssue]), score (int), output_dir (str), und ggf.
source/translation-Dateien fuer das ZIP-Paket.

Optional-Dependencies (openpyxl, reportlab) werden defensiv importiert; bei
Fehlen wird `ImportError` propagiert, damit die UI passend reagieren kann.
"""
from __future__ import annotations

import os
import re
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from nicegui_app.severity import label as severity_label

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helfer
# ---------------------------------------------------------------------------
_ILLEGAL_XML_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def _xml_clean(value):
    """Entfernt OOXML-illegale Steuerzeichen aus String-Werten."""
    if isinstance(value, str):
        return _ILLEGAL_XML_RE.sub('', value)
    return value


def _xml_escape(text: str) -> str:
    """Minimaler XML-Escape fuer ReportLab Paragraph (&, <, >)."""
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------
def export_txt(findings: list, score: int, output_dir: str) -> str:
    """Schreibt einen TXT-Bericht. Liefert den Pfad."""
    lines = [
        'Qualitäts-Framework -- Analysebericht',
        f'Datum: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'Score: {score}/100',
        f'Findings: {len(findings)}',
        '', '=' * 60,
    ]
    for i, f in enumerate(findings, 1):
        lines.append(f'\n[{i}] {severity_label(f.severity)} | {f.code} | {f.message}')
        if getattr(f, 'source_text', ''):
            lines.append(f'    Quelle:       {f.source_text[:200]}')
        if getattr(f, 'target_text', ''):
            lines.append(f'    Übersetzung: {f.target_text[:200]}')
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'bericht_{_timestamp()}.txt')
    Path(path).write_text('\n'.join(lines), encoding='utf-8')
    return path


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------
def export_excel(findings: list, output_dir: str) -> str:
    """Schreibt einen XLSX-Bericht. Liefert den Pfad. Wirft ImportError wenn openpyxl fehlt."""
    import openpyxl  # noqa: PLC0415
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Findings'
    ws.append(['Nr', 'Schwere', 'Code', 'Kategorie', 'Nachricht', 'Segment', 'Quelltext', 'Zieltext'])
    for i, f in enumerate(findings, 1):
        ws.append([
            i,
            severity_label(f.severity),
            _xml_clean(f.code),
            _xml_clean(getattr(f, 'category', '')),
            _xml_clean(f.message),
            getattr(f, 'segment_index', -1),
            _xml_clean((getattr(f, 'source_text', '') or '')[:500]),
            _xml_clean((getattr(f, 'target_text', '') or '')[:500]),
        ])
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'bericht_{_timestamp()}.xlsx')
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def export_pdf(findings: list, score: int, output_dir: str) -> str:
    """Schreibt einen PDF-Bericht. Wirft ImportError wenn reportlab fehlt."""
    from reportlab.lib.pagesizes import A4  # noqa: PLC0415
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'bericht_{_timestamp()}.pdf')
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph('Qualitäts-Framework -- Analysebericht', styles['Title']),
        Spacer(1, 12),
        Paragraph(
            f'Score: {score}/100 | Findings: {len(findings)} | '
            f'{datetime.now().strftime("%Y-%m-%d %H:%M")}',
            styles['Normal'],
        ),
        Spacer(1, 16),
    ]
    small_style = ParagraphStyle('small', parent=styles['Normal'], fontSize=7, leading=9)
    data = [['Nr', 'Seg.', 'Schwere', 'Code', 'Nachricht']]
    for i, f in enumerate(findings, 1):
        msg = f.message[:110] + ('...' if len(f.message) > 110 else '')
        seg = getattr(f, 'segment_index', -1)
        data.append([
            str(i),
            str(seg) if seg >= 0 else '–',
            severity_label(f.severity),
            _xml_escape(str(f.code)),
            Paragraph(_xml_escape(msg), small_style),
        ])
    table = Table(data, colWidths=[1 * cm, 1 * cm, 2 * cm, 3 * cm, 11 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2744')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(table)
    doc.build(story)
    return path


# ---------------------------------------------------------------------------
# Korrekturpaket (ZIP)
# ---------------------------------------------------------------------------
def _add_files_unique(zf: zipfile.ZipFile, file_paths: Iterable[str], archive_dir: str) -> None:
    """Fuegt Dateien dem ZIP hinzu, vermeidet Namens-Kollisionen via Suffix _1/_2/...."""
    used: set = set()
    for fp in file_paths:
        if not fp or not os.path.exists(fp):
            continue
        base = os.path.basename(fp)
        name = base
        counter = 1
        while name.lower() in used:
            stem, ext = os.path.splitext(base)
            name = f'{stem}_{counter}{ext}'
            counter += 1
        used.add(name.lower())
        zf.write(fp, f'{archive_dir}/{name}')


def export_correction_package(
    findings: list,
    score: int,
    source_files: List[str],
    translation_files: List[str],
    output_dir: str,
) -> Optional[str]:
    """Baut ein Korrekturpaket-ZIP.

    Inhalt:
      - 01_Ausgangstexte/<source files>
      - 02_Uebersetzungen/<translation files>
      - corrections.txt (Befundliste)
      - bericht/<txt-Bericht>

    Liefert ZIP-Pfad oder None bei Fehler.
    """
    os.makedirs(output_dir, exist_ok=True)
    ts = _timestamp()
    zip_path = os.path.join(output_dir, f'korrekturpaket_{ts}.zip')

    # Befundliste
    corrections_lines = [
        'Korrekturpaket -- Befundliste',
        f'Datum: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'Score: {score}/100',
        f'Anzahl Befunde: {len(findings)}',
        '', '=' * 60,
    ]
    for i, f in enumerate(findings, 1):
        corrections_lines.extend([
            f'\n--- Befund {i} ---',
            f'Schwere: {severity_label(f.severity)}',
            f'Code:    {f.code}',
            f'Meldung: {f.message}',
        ])
        if getattr(f, 'source_text', ''):
            corrections_lines.append(f'Quelltext:     {f.source_text[:300]}')
        if getattr(f, 'target_text', ''):
            corrections_lines.append(f'Übersetzung:  {f.target_text[:300]}')
    corrections_path = os.path.join(output_dir, f'corrections_{ts}.txt')
    with open(corrections_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(corrections_lines))

    # Optionalen TXT-Bericht beilegen
    try:
        report_path = export_txt(findings, score, output_dir)
    except Exception as exc:
        _logger.warning('TXT-Bericht fuer Korrekturpaket fehlgeschlagen: %s', exc)
        report_path = ''

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            _add_files_unique(zf, source_files or [], '01_Ausgangstexte')
            _add_files_unique(zf, translation_files or [], '02_Uebersetzungen')
            zf.write(corrections_path, 'corrections.txt')
            if report_path and os.path.exists(report_path):
                zf.write(report_path, f'bericht/{os.path.basename(report_path)}')
        return zip_path
    except Exception as exc:
        _logger.warning('Korrekturpaket-Export fehlgeschlagen: %s', exc)
        return None
