# -*- coding: utf-8 -*-
"""Text-Extraktion fuer alle unterstuetzten Dateiformate.

Kapselt die zuvor in main.py verstreute Logik:
- TXT/MD/PY (UTF-8)
- DOCX inkl. Tabellenzellen
- PDF (pdfplumber -> PyMuPDF -> OCR-Fallback)
- Bilder (OCR via Tesseract, optional)

Optional-Dependencies werden lazy importiert; fehlt eine, gibt's eine
verstaendliche Meldung statt Crash.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Optional OCR
# ---------------------------------------------------------------------------
try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None  # type: ignore

try:
    import pytesseract  # type: ignore
    _HAS_OCR = True
except ImportError:
    pytesseract = None  # type: ignore
    _HAS_OCR = False


def _ocr_image(path: str) -> str:
    if not _HAS_OCR or Image is None:
        return f'[OCR nicht verfuegbar: {Path(path).name}]'
    try:
        with Image.open(path) as img:
            return pytesseract.image_to_string(img, lang='deu+eng') or ''
    except Exception as exc:
        return f'[OCR-Fehler {Path(path).name}: {exc}]'


def _ocr_pdf_page(path: str) -> str:
    """OCR ueber alle Seiten einer PDF (Fallback wenn Text-Extraktion leer).

    Bevorzugt `pdf2image` (300 DPI, beste Qualitaet); faellt auf PyMuPDF
    bei niedrigerer Aufloesung zurueck wenn pdf2image nicht installiert ist.
    """
    if not _HAS_OCR or Image is None:
        return ''
    # Primaer: pdf2image mit 300 DPI (Qualitaet)
    try:
        from pdf2image import convert_from_path  # type: ignore
        images = []
        try:
            images = convert_from_path(path, dpi=300)
            texts = [pytesseract.image_to_string(img, lang='deu+eng') or '' for img in images]
            if any(t.strip() for t in texts):
                return '\n'.join(texts)
        finally:
            for img in images:
                try:
                    img.close()
                except Exception:
                    pass
    except ImportError:
        pass
    except Exception:
        pass
    # Fallback: PyMuPDF
    try:
        import fitz  # type: ignore
    except ImportError:
        return ''
    out: List[str] = []
    try:
        doc = fitz.open(path)
        try:
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                from io import BytesIO
                with Image.open(BytesIO(pix.tobytes('png'))) as img:
                    out.append(pytesseract.image_to_string(img, lang='deu+eng') or '')
        finally:
            doc.close()
    except Exception:
        return ''
    return '\n'.join(out)


def extract_text(path: str) -> str:
    """Extrahiert Plaintext aus einer Datei.

    Unterstuetzte Formate: .txt .md .py .docx .pdf .png .jpg .jpeg .tiff .tif

    Rueckgabe: Plaintext oder eine `[...]`-Fehlermeldung. Wirft nie eine
    Exception nach aussen.
    """
    if not path or not os.path.isfile(path):
        return f'[Datei nicht gefunden: {Path(path).name if path else ""}]'
    ext = Path(path).suffix.lower()
    if ext in ('.txt', '.py', '.md'):
        try:
            return Path(path).read_text(encoding='utf-8', errors='replace')
        except Exception as exc:
            return f'[Lesefehler {Path(path).name}: {exc}]'
    if ext == '.docx':
        try:
            from docx import Document  # type: ignore
            doc = Document(path)
            parts: List[str] = []
            parts.extend(p.text for p in doc.paragraphs if p.text and p.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        ct = (cell.text or '').strip()
                        if ct:
                            parts.append(ct)
            return '\n'.join(parts)
        except ImportError:
            return f'[python-docx nicht installiert: {Path(path).name}]'
        except Exception as exc:
            return f'[DOCX-Lesefehler {Path(path).name}: {exc}]'
    if ext in ('.png', '.jpg', '.jpeg', '.tiff', '.tif'):
        return _ocr_image(path)
    if ext == '.pdf':
        text = ''
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(path) as pdf:
                text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
        except Exception:
            try:
                import fitz  # type: ignore
                doc = fitz.open(path)
                try:
                    text = '\n'.join(p.get_text() for p in doc)
                finally:
                    doc.close()
            except Exception:
                pass
        if not text.strip():
            ocr_text = _ocr_pdf_page(path)
            if ocr_text.strip():
                return ocr_text
            return f'[PDF-Extraktion fehlgeschlagen: {Path(path).name}]'
        return text
    if ext == '.doc':
        return f'[.doc-Format nur mit externem Konverter: {Path(path).name}]'
    return ''


def finding_to_dict(f) -> dict:
    """Serialisiert ein QAIssue/Finding-Objekt zu einem JSON-tauglichen Dict."""
    return {
        'severity': getattr(f, 'severity', 'info'),
        'code': getattr(f, 'code', ''),
        'message': getattr(f, 'message', ''),
        'category': getattr(f, 'category', ''),
        'source_text': getattr(f, 'source_text', '') or '',
        'target_text': getattr(f, 'target_text', '') or '',
        'segment_index': getattr(f, 'segment_index', -1),
        'source_file': getattr(f, 'source_file', '') or '',
        'target_file': getattr(f, 'target_file', '') or '',
        'meta': getattr(f, 'meta', {}) or {},
    }


def dict_to_finding(d: dict, qa_issue_cls):
    """Deserialisiert ein Dict zurueck zu einem QAIssue.

    `qa_issue_cls` wird per DI uebergeben um zirkulaere Imports zu vermeiden.
    None-Schutz fuer ALLE Felder (Legacy-Sessions koennen None enthalten).
    """
    seg = d.get('segment_index', -1)
    if seg is None:
        seg = -1
    kwargs = dict(
        severity=d.get('severity') or 'info',
        code=d.get('code') or '',
        message=d.get('message') or '',
        category=d.get('category') or '',
        source_text=d.get('source_text') or '',
        target_text=d.get('target_text') or '',
        segment_index=seg,
        meta=d.get('meta') or {},
    )
    # Per-File-Attribution: nur wenn die Klasse die Felder unterstützt
    try:
        import dataclasses as _dc
        if _dc.is_dataclass(qa_issue_cls):
            field_names = {f.name for f in _dc.fields(qa_issue_cls)}
        else:
            field_names = set(getattr(qa_issue_cls, '__annotations__', {}).keys())
        if 'source_file' in field_names:
            kwargs['source_file'] = d.get('source_file') or ''
        if 'target_file' in field_names:
            kwargs['target_file'] = d.get('target_file') or ''
    except Exception:
        pass
    return qa_issue_cls(**kwargs)
