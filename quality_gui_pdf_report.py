#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quality_gui_pdf_report – PDF-Report-Generator mit Grafiken.

Erstellt professionelle PDF-Reports für Übersetzungsqualitäts-Analysen mit:
- Zusammenfassungs-Statistiken
- Schweregrad-Verteilung (Tortendiagramm)
- Kategorie-Verteilung (Balkendiagramm)
- Phasen-Vergleich (Balkendiagramm)
- Detaillierte Findings-Liste

Abhängigkeiten (optional):
- matplotlib: Für Diagramme
- reportlab: Für PDF-Erstellung (Fallback: fpdf2)
"""
from __future__ import annotations
import os
import io
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

# ============================================================================
# Optionale Imports für PDF/Grafiken
# ============================================================================

matplotlib = None
plt = None
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
except ImportError:
    pass

reportlab_available = False
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image as RLImage, PageBreak, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    reportlab_available = True
except ImportError:
    pass

# Fallback: fpdf2
fpdf_available = False
if not reportlab_available:
    try:
        from fpdf import FPDF
        fpdf_available = True
    except ImportError:
        pass


# ============================================================================
# Farbdefinitionen (Design System kompatibel)
# ============================================================================

COLORS = {
    'critical': '#DC2626',   # Rot
    'major': '#F59E0B',      # Orange
    'minor': '#3B82F6',      # Blau
    'info': '#6B7280',       # Grau
    'primary': '#2563EB',    # Primärblau
    'success': '#10B981',    # Grün
    'background': '#F8FAFC', # Hintergrund
    'text': '#1E293B',       # Text
    'text_secondary': '#64748B',
}

SEVERITY_COLORS = {
    'critical': COLORS['critical'],
    'major': COLORS['major'],
    'minor': COLORS['minor'],
    'info': COLORS['info'],
}

SEVERITY_LABELS = {
    'critical': 'Kritisch',
    'major': 'Schwerwiegend',
    'minor': 'Leicht',
    'info': 'Hinweis',
}


# ============================================================================
# Chart-Generierung (matplotlib)
# ============================================================================

def _create_severity_pie_chart(severity_counts: Dict[str, int], 
                                output_path: Optional[str] = None) -> Optional[bytes]:
    """Erstellt ein Tortendiagramm für Schweregrad-Verteilung."""
    if plt is None:
        return None
    
    # Filtere leere Kategorien
    data = {k: v for k, v in severity_counts.items() if v > 0}
    if not data:
        return None
    
    labels = [SEVERITY_LABELS.get(k, k) for k in data.keys()]
    sizes = list(data.values())
    colors_list = [SEVERITY_COLORS.get(k, COLORS['info']) for k in data.keys()]
    
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')
    
    # Explode für kritische Fehler
    explode = [0.05 if k == 'critical' else 0 for k in data.keys()]
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        explode=explode,
        labels=labels, 
        colors=colors_list,
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes))})',
        startangle=90,
        textprops={'fontsize': 9}
    )
    
    ax.set_title('Verteilung nach Schweregrad', fontsize=12, fontweight='bold', pad=10)
    
    # Bessere Lesbarkeit
    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    
    # Als Bytes zurückgeben
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        buf.seek(0)
    
    return buf.getvalue()


def _create_category_bar_chart(category_counts: Dict[str, int],
                                output_path: Optional[str] = None,
                                max_categories: int = 10) -> Optional[bytes]:
    """Erstellt ein Balkendiagramm für Kategorie-Verteilung."""
    if plt is None:
        return None
    
    if not category_counts:
        return None
    
    # Top N Kategorien
    sorted_cats = sorted(category_counts.items(), key=lambda x: -x[1])[:max_categories]
    if not sorted_cats:
        return None
    
    categories = [c[0] for c in sorted_cats]
    counts = [c[1] for c in sorted_cats]
    
    fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
    
    # Horizontales Balkendiagramm
    bars = ax.barh(categories[::-1], counts[::-1], color=COLORS['primary'], edgecolor='white')
    
    # Werte an Balken
    for bar, count in zip(bars, counts[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                str(count), va='center', fontsize=9)
    
    ax.set_xlabel('Anzahl Befunde', fontsize=10)
    ax.set_title('Top Fehler-Kategorien', fontsize=12, fontweight='bold', pad=10)
    ax.set_xlim(0, max(counts) * 1.15)
    
    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        buf.seek(0)
    
    return buf.getvalue()


def _create_phase_comparison_chart(phase_counts: Dict[str, int],
                                    output_path: Optional[str] = None) -> Optional[bytes]:
    """Erstellt ein Balkendiagramm für Phasen-Vergleich."""
    if plt is None:
        return None
    
    if not phase_counts:
        return None
    
    phase_labels = {
        'phase1': 'Phase 1\nFormat & Struktur',
        'phase2': 'Phase 2\nInhalt & Konsistenz',
        'phase3': 'Phase 3\nSemantik & Grammatik',
    }
    
    phases = list(phase_counts.keys())
    counts = list(phase_counts.values())
    labels = [phase_labels.get(p, p) for p in phases]
    
    # Farben pro Phase
    phase_colors = ['#3B82F6', '#10B981', '#8B5CF6']
    colors_list = phase_colors[:len(phases)]
    
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
    
    bars = ax.bar(labels, counts, color=colors_list, edgecolor='white', width=0.6)
    
    # Werte über Balken
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Anzahl Befunde', fontsize=10)
    ax.set_title('Befunde pro Analyse-Phase', fontsize=12, fontweight='bold', pad=10)
    ax.set_ylim(0, max(counts) * 1.2 if counts else 10)
    
    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())
        buf.seek(0)
    
    return buf.getvalue()


# ============================================================================
# PDF-Report-Generierung (reportlab)
# ============================================================================

class PDFReportGenerator:
    """Generiert PDF-Reports für Übersetzungsqualitäts-Analysen."""
    
    def __init__(self, findings: List[Dict[str, Any]], 
                 analysis_data: Optional[Dict[str, Any]] = None,
                 title: str = "Übersetzungsqualitäts-Report"):
        """
        Args:
            findings: Liste der Findings (Dicts)
            analysis_data: Optionale Analyse-Metadaten (summary, metrics, etc.)
            title: Report-Titel
        """
        self.findings = findings or []
        self.analysis_data = analysis_data or {}
        self.title = title
        self.timestamp = datetime.now()
        
        # Statistiken berechnen
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Berechnet Statistiken aus den Findings."""
        self.total_count = len(self.findings)
        
        # Schweregrad-Zählung
        self.severity_counts = Counter()
        for f in self.findings:
            sev = str(f.get('severity', 'info')).lower()
            self.severity_counts[sev] += 1
        
        # Kategorie-Zählung
        self.category_counts = Counter()
        for f in self.findings:
            cat = f.get('category', 'other')
            self.category_counts[cat] += 1
        
        # Phase-Zählung
        self.phase_counts = Counter()
        for f in self.findings:
            phase = f.get('phase', '')
            if phase:
                self.phase_counts[phase] += 1
        
        # Checker-Zählung
        self.checker_counts = Counter()
        for f in self.findings:
            chk = f.get('checker', 'unknown')
            self.checker_counts[chk] += 1
    
    def generate(self, output_path: str) -> bool:
        """Generiert den PDF-Report.
        
        Args:
            output_path: Ausgabe-Pfad für die PDF-Datei
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if reportlab_available:
            return self._generate_reportlab(output_path)
        elif fpdf_available:
            return self._generate_fpdf(output_path)
        else:
            raise ImportError(
                "Kein PDF-Modul verfügbar. Bitte installieren: "
                "pip install reportlab oder pip install fpdf2"
            )
    
    def _generate_reportlab(self, output_path: str) -> bool:
        """Generiert PDF mit reportlab."""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            styles = getSampleStyleSheet()
            
            # Custom Styles
            styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor(COLORS['primary'])
            ))
            
            styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.HexColor(COLORS['text'])
            ))
            
            styles.add(ParagraphStyle(
                name='SubSection',
                parent=styles['Heading3'],
                fontSize=11,
                spaceBefore=10,
                spaceAfter=5,
                textColor=colors.HexColor(COLORS['text_secondary'])
            ))
            
            styles.add(ParagraphStyle(
                name='FindingCritical',
                parent=styles['Normal'],
                fontSize=9,
                leftIndent=10,
                spaceBefore=3,
                spaceAfter=3,
                backColor=colors.HexColor('#FEE2E2'),
                borderColor=colors.HexColor(COLORS['critical']),
                borderWidth=1,
                borderPadding=5
            ))
            
            styles.add(ParagraphStyle(
                name='FindingMajor',
                parent=styles['Normal'],
                fontSize=9,
                leftIndent=10,
                spaceBefore=3,
                spaceAfter=3,
                backColor=colors.HexColor('#FEF3C7'),
            ))
            
            styles.add(ParagraphStyle(
                name='FindingMinor',
                parent=styles['Normal'],
                fontSize=9,
                leftIndent=10,
                spaceBefore=3,
                spaceAfter=3,
                backColor=colors.HexColor('#DBEAFE'),
            ))
            
            elements = []
            
            # === TITEL ===
            elements.append(Paragraph(self.title, styles['ReportTitle']))
            elements.append(Paragraph(
                f"Erstellt am: {self.timestamp.strftime('%d.%m.%Y um %H:%M Uhr')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 20))
            
            # === ZUSAMMENFASSUNG ===
            elements.append(Paragraph("Zusammenfassung", styles['SectionTitle']))
            
            summary_data = [
                ['Kennzahl', 'Wert'],
                ['Gesamt Befunde', str(self.total_count)],
                ['Kritisch', str(self.severity_counts.get('critical', 0))],
                ['Schwerwiegend', str(self.severity_counts.get('major', 0))],
                ['Leicht', str(self.severity_counts.get('minor', 0))],
                ['Hinweise', str(self.severity_counts.get('info', 0))],
            ]
            
            # Analyse-Metadaten hinzufügen
            if self.analysis_data.get('summary'):
                summary = self.analysis_data['summary']
                if 'pairs' in summary:
                    summary_data.append(['Segmente analysiert', str(summary['pairs'])])
                if 'profile_used' in summary:
                    summary_data.append(['Profil', summary['profile_used']])
            
            summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
            
            # === DIAGRAMME ===
            elements.append(Paragraph("Grafische Auswertung", styles['SectionTitle']))
            
            # Temporäre Dateien für Charts
            temp_dir = tempfile.mkdtemp()
            
            # Schweregrad-Tortendiagramm
            if self.severity_counts:
                pie_data = _create_severity_pie_chart(dict(self.severity_counts))
                if pie_data:
                    pie_path = os.path.join(temp_dir, 'severity_pie.png')
                    with open(pie_path, 'wb') as f:
                        f.write(pie_data)
                    elements.append(RLImage(pie_path, width=12*cm, height=8*cm))
                    elements.append(Spacer(1, 10))
            
            # Kategorie-Balkendiagramm
            if self.category_counts:
                bar_data = _create_category_bar_chart(dict(self.category_counts))
                if bar_data:
                    bar_path = os.path.join(temp_dir, 'category_bar.png')
                    with open(bar_path, 'wb') as f:
                        f.write(bar_data)
                    elements.append(RLImage(bar_path, width=14*cm, height=9*cm))
                    elements.append(Spacer(1, 10))
            
            # Phasen-Vergleich
            if self.phase_counts and len(self.phase_counts) > 1:
                phase_data = _create_phase_comparison_chart(dict(self.phase_counts))
                if phase_data:
                    phase_path = os.path.join(temp_dir, 'phase_bar.png')
                    with open(phase_path, 'wb') as f:
                        f.write(phase_data)
                    elements.append(RLImage(phase_path, width=12*cm, height=7*cm))
            
            elements.append(PageBreak())
            
            # === BEFUNDE DETAILS ===
            elements.append(Paragraph("Detaillierte Befunde", styles['SectionTitle']))
            
            # Nach Schweregrad gruppiert
            severity_order = ['critical', 'major', 'minor', 'info']
            
            for sev in severity_order:
                sev_findings = [f for f in self.findings if str(f.get('severity', '')).lower() == sev]
                if not sev_findings:
                    continue
                
                sev_label = SEVERITY_LABELS.get(sev, sev)
                elements.append(Paragraph(
                    f"{sev_label} ({len(sev_findings)})", 
                    styles['SubSection']
                ))
                
                # Findings-Tabelle
                finding_data = [['#', 'Regel', 'Kategorie', 'Beschreibung']]
                
                for idx, f in enumerate(sev_findings[:50], 1):  # Max 50 pro Schweregrad
                    rule = f.get('rule_id') or f.get('rule') or '-'
                    cat = f.get('category', '-')
                    msg = (f.get('message') or '')[:80]
                    if len(f.get('message', '')) > 80:
                        msg += '...'
                    finding_data.append([str(idx), rule[:25], cat[:15], msg])
                
                if len(sev_findings) > 50:
                    finding_data.append(['...', f'+{len(sev_findings)-50} weitere', '', ''])
                
                col_widths = [1*cm, 4*cm, 3*cm, 8*cm]
                finding_table = Table(finding_data, colWidths=col_widths)
                
                # Farbe basierend auf Schweregrad
                header_color = colors.HexColor(SEVERITY_COLORS.get(sev, COLORS['info']))
                row_bg = {
                    'critical': colors.HexColor('#FEE2E2'),
                    'major': colors.HexColor('#FEF3C7'),
                    'minor': colors.HexColor('#DBEAFE'),
                    'info': colors.HexColor('#F3F4F6'),
                }.get(sev, colors.HexColor('#F3F4F6'))
                
                finding_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), header_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, row_bg]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                
                elements.append(finding_table)
                elements.append(Spacer(1, 15))
            
            # === FOOTER ===
            elements.append(Spacer(1, 30))
            elements.append(Paragraph(
                "— Ende des Reports —",
                ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER,
                              textColor=colors.HexColor(COLORS['text_secondary']))
            ))
            
            # PDF erstellen
            doc.build(elements)
            
            # Temp-Dateien aufräumen
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            print(f"PDF-Generierung fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_fpdf(self, output_path: str) -> bool:
        """Fallback: Generiert PDF mit fpdf2 (einfacherer Report)."""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Titel
            pdf.set_font('Helvetica', 'B', 20)
            pdf.cell(0, 15, self.title, ln=True, align='C')
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 8, f"Erstellt: {self.timestamp.strftime('%d.%m.%Y %H:%M')}", ln=True, align='C')
            pdf.ln(10)
            
            # Zusammenfassung
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Zusammenfassung', ln=True)
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 6, f"Gesamt: {self.total_count} Befunde", ln=True)
            pdf.cell(0, 6, f"Kritisch: {self.severity_counts.get('critical', 0)}", ln=True)
            pdf.cell(0, 6, f"Schwerwiegend: {self.severity_counts.get('major', 0)}", ln=True)
            pdf.cell(0, 6, f"Leicht: {self.severity_counts.get('minor', 0)}", ln=True)
            pdf.ln(10)
            
            # Top Kategorien
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Top Kategorien', ln=True)
            
            pdf.set_font('Helvetica', '', 10)
            for cat, cnt in self.category_counts.most_common(10):
                pdf.cell(0, 6, f"  {cat}: {cnt}", ln=True)
            pdf.ln(10)
            
            # Befunde (erste 100)
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Befunde', ln=True)
            
            pdf.set_font('Helvetica', '', 9)
            for idx, f in enumerate(self.findings[:100], 1):
                sev = f.get('severity', 'info')
                rule = f.get('rule_id') or f.get('rule') or '-'
                msg = (f.get('message') or '')[:70]
                
                pdf.multi_cell(0, 5, f"{idx}. [{sev.upper()}] {rule}: {msg}")
                pdf.ln(2)
            
            if len(self.findings) > 100:
                pdf.cell(0, 6, f"... und {len(self.findings)-100} weitere Befunde", ln=True)
            
            pdf.output(output_path)
            return True
            
        except Exception as e:
            print(f"FPDF-Generierung fehlgeschlagen: {e}")
            return False


# ============================================================================
# Convenience-Funktion
# ============================================================================

def generate_pdf_report(findings: List[Dict[str, Any]],
                        output_path: str,
                        analysis_data: Optional[Dict[str, Any]] = None,
                        title: str = "Übersetzungsqualitäts-Report") -> bool:
    """Generiert einen PDF-Report für Analyse-Ergebnisse.
    
    Args:
        findings: Liste der Findings
        output_path: Ausgabe-Pfad für PDF
        analysis_data: Optionale Analyse-Metadaten
        title: Report-Titel
        
    Returns:
        True bei Erfolg
    """
    generator = PDFReportGenerator(findings, analysis_data, title)
    return generator.generate(output_path)


def is_pdf_available() -> Tuple[bool, str]:
    """Prüft ob PDF-Generierung verfügbar ist.
    
    Returns:
        (verfügbar, info_text)
    """
    if reportlab_available and plt is not None:
        return True, "reportlab + matplotlib (vollständig)"
    elif reportlab_available:
        return True, "reportlab (ohne Grafiken)"
    elif fpdf_available:
        return True, "fpdf2 (einfacher Report)"
    else:
        return False, "Nicht verfügbar - bitte 'pip install reportlab matplotlib' ausführen"


# ============================================================================
# Test
# ============================================================================

if __name__ == '__main__':
    # Test-Findings
    test_findings = [
        {'severity': 'critical', 'rule_id': 'PLACEHOLDER_MISSING', 'category': 'placeholders', 
         'message': 'Platzhalter {name} fehlt in Übersetzung', 'phase': 'phase1'},
        {'severity': 'critical', 'rule_id': 'NUMBER_MISMATCH', 'category': 'numbers',
         'message': 'Zahl 100 wurde zu 1000 verändert', 'phase': 'phase1'},
        {'severity': 'major', 'rule_id': 'GRAMMAR_ERROR', 'category': 'grammar',
         'message': 'Grammatikfehler: "der Haus" sollte "das Haus" sein', 'phase': 'phase3'},
        {'severity': 'major', 'rule_id': 'OCR_KNOWN_ERROR', 'category': 'ocr',
         'message': 'OCR-Fehler: "rnit" sollte "mit" sein', 'phase': 'phase3'},
        {'severity': 'minor', 'rule_id': 'WHITESPACE_DOUBLE', 'category': 'whitespace',
         'message': 'Doppeltes Leerzeichen gefunden', 'phase': 'phase1'},
        {'severity': 'minor', 'rule_id': 'CONSISTENCY_VARIANT', 'category': 'consistency',
         'message': 'Term "Button" wird unterschiedlich übersetzt', 'phase': 'phase3'},
        {'severity': 'info', 'rule_id': 'LENGTH_DRIFT', 'category': 'length',
         'message': 'Übersetzung ist 30% länger als Quelle', 'phase': 'phase2'},
    ] * 5  # 35 Test-Findings
    
    available, info = is_pdf_available()
    print(f"PDF-Generierung: {info}")
    
    if available:
        output = 'test_report.pdf'
        success = generate_pdf_report(
            test_findings,
            output,
            title="Test-Qualitätsreport"
        )
        print(f"Report erstellt: {output}" if success else "Fehler bei Report-Erstellung")
    else:
        print("PDF-Generierung nicht verfügbar")
