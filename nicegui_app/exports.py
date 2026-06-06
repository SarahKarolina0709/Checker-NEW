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


def _truncate(text: str, limit: int = 600) -> str:
    """Kuerzt Text auf `limit` Zeichen und macht das Kuerzen sichtbar.

    Verhindert, dass sehr lange Segmente eine PDF-Karte ueber eine ganze Seite
    aufblaehen. Leere/None-Eingaben bleiben leer (Aufrufer rendert das Feld dann
    gar nicht).
    """
    text = text or ''
    if len(text) > limit:
        return text[:limit].rstrip() + ' … (gekürzt)'
    return text


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------
def export_txt(findings: list, score: int, output_dir: str) -> str:
    """Schreibt einen TXT-Bericht. Liefert den Pfad."""
    lines = [
        'Qualitäts-Framework -- Analysebericht',
        f'Datum: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'Score: {score}/100',
        f'Befunde: {len(findings)}',
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
    ws.title = 'Befunde'
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
    """Schreibt einen korrektur-tauglichen PDF-Bericht.

    Aufbau: Titel + Zusammenfassung (Score, Anzahl je Schwere) und danach pro
    Befund eine Karte mit Schwere, Code, Meldung, Quelltext und Uebersetzung —
    gruppiert nach Schwere (Kritisch zuerst). So kann der Uebersetzer den
    Bericht ohne Office/Excel oeffnen und direkt abarbeiten.

    Wirft ImportError wenn reportlab fehlt.
    """
    from reportlab.lib.pagesizes import A4  # noqa: PLC0415
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfgen.canvas import Canvas as _Canvas

    from nicegui_app.severity import normalize as _sev_norm, color as _sev_color

    class _NumberedCanvas(_Canvas):
        """Zeichnet 'Seite X von Y' unten rechts (Zwei-Pass: Gesamtzahl erst bei save bekannt)."""

        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._saved_states = []

        def showPage(self):  # noqa: N802 (reportlab-API)
            self._saved_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved_states)
            for state in self._saved_states:
                self.__dict__.update(state)
                self.setFont('Helvetica', 7.5)
                self.setFillColor(colors.HexColor('#94a3b8'))
                self.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm,
                                     f'Seite {self._pageNumber} von {total}')
                super().showPage()
            super().save()

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'bericht_{_timestamp()}.pdf')
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title='Qualitäts-Analysebericht')
    styles = getSampleStyleSheet()

    label_style = ParagraphStyle(
        'flabel', parent=styles['Normal'], fontSize=9.5, leading=13,
        spaceAfter=2, textColor=colors.HexColor('#0f2744'),
    )
    field_label = ParagraphStyle(
        'ffield', parent=styles['Normal'], fontSize=7.5, leading=10,
        textColor=colors.HexColor('#64748b'), spaceBefore=3,
    )
    body_style = ParagraphStyle(
        'fbody', parent=styles['Normal'], fontSize=8.5, leading=11,
        alignment=TA_LEFT,
    )
    section_style = ParagraphStyle(
        'fsection', parent=styles['Heading2'], fontSize=12, leading=15,
        spaceBefore=10, spaceAfter=4, textColor=colors.white,
    )

    # Severities zu Anzeige-Gruppen zusammenfassen (minor + info = "Hinweis")
    sev_de = {'critical': 'Kritisch', 'major': 'Wichtig', 'minor': 'Hinweis', 'info': 'Hinweis'}
    display_groups = [
        ('critical', 'Kritisch'),
        ('major', 'Wichtig'),
        ('hinweis', 'Hinweis'),
    ]
    _sev_to_group = {'critical': 'critical', 'major': 'major', 'minor': 'hinweis', 'info': 'hinweis'}
    _group_accent = {'critical': 'critical', 'major': 'major', 'hinweis': 'minor'}
    grouped: dict = {g: [] for g, _ in display_groups}
    for f in findings:
        grouped[_sev_to_group.get(_sev_norm(getattr(f, 'severity', None)), 'hinweis')].append(f)

    counts = {g: len(grouped[g]) for g, _ in display_groups}

    story = [
        Paragraph('Qualitäts-Analysebericht', styles['Title']),
        Spacer(1, 6),
        Paragraph(
            f'Score: <b>{score}/100</b>&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'Befunde gesamt: <b>{len(findings)}</b>&nbsp;&nbsp;|&nbsp;&nbsp;'
            f'{datetime.now().strftime("%d.%m.%Y %H:%M")}',
            styles['Normal'],
        ),
        Spacer(1, 4),
        Paragraph(
            f'Kritisch: <b>{counts["critical"]}</b>&nbsp;&nbsp;·&nbsp;&nbsp;'
            f'Wichtig: <b>{counts["major"]}</b>&nbsp;&nbsp;·&nbsp;&nbsp;'
            f'Hinweise: <b>{counts["hinweis"]}</b>',
            styles['Normal'],
        ),
        Spacer(1, 4),
        Paragraph(
            'Bitte zuerst die kritischen, dann die wichtigen Befunde bearbeiten. '
            'Hinweise (z.\u202fB. Quelltext-Qualität) betreffen den Ausgangstext '
            'und sind optional.',
            ParagraphStyle('hint', parent=styles['Normal'], fontSize=8,
                           textColor=colors.HexColor('#64748b'), leading=11),
        ),
        Spacer(1, 10),
    ]

    if not findings:
        story.append(Paragraph('Keine Befunde – die Übersetzung ist sauber.', body_style))
        doc.build(story, canvasmaker=_NumberedCanvas)
        return path

    counter = 0
    for group_key, group_label in display_groups:
        items = grouped.get(group_key, [])
        if not items:
            continue
        accent = colors.HexColor(_sev_color(_group_accent[group_key]))
        header = Table(
            [[Paragraph(f'{group_label} &nbsp;({len(items)})', section_style)]],
            colWidths=[18 * cm],
        )
        header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(header)
        story.append(Spacer(1, 4))

        for f in items:
            counter += 1
            sev_label = sev_de[_sev_norm(getattr(f, 'severity', None))]
            code = _xml_escape(str(getattr(f, 'code', '') or ''))
            msg = _xml_escape(str(getattr(f, 'message', '') or ''))
            rows = [[Paragraph(f'<b>[{counter}] {sev_label}</b> &nbsp;·&nbsp; '
                               f'<font color="#64748b">{code}</font>', label_style)]]
            rows.append([Paragraph(msg, body_style)])

            src_file = getattr(f, 'source_file', '') or ''
            tgt_file = getattr(f, 'target_file', '') or ''
            if src_file or tgt_file:
                fileinfo = _xml_escape(' → '.join(
                    [os.path.basename(p) for p in (src_file, tgt_file) if p]
                ))
                rows.append([Paragraph(f'Datei: {fileinfo}', field_label)])

            src_text = _truncate(getattr(f, 'source_text', '') or '')
            tgt_text = _truncate(getattr(f, 'target_text', '') or '')
            if src_text:
                rows.append([Paragraph('Quelltext', field_label)])
                rows.append([Paragraph(_xml_escape(src_text), body_style)])
            if tgt_text:
                rows.append([Paragraph('Übersetzung', field_label)])
                rows.append([Paragraph(_xml_escape(tgt_text), body_style)])

            card = Table(rows, colWidths=[17.6 * cm])
            card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('LINEBEFORE', (0, 0), (0, -1), 3, accent),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (0, 0), 5),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
            ]))
            story.append(KeepTogether([card, Spacer(1, 6)]))

    doc.build(story, canvasmaker=_NumberedCanvas)
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
