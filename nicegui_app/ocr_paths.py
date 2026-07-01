# -*- coding: utf-8 -*-
"""Pfad-Verdrahtung fuer die gebuendelten OCR-/PDF-Tools (Tesseract, Poppler).

Das Repo buendelt portable Versionen unter ``<repo>/tesseract`` und
``<repo>/poppler``, damit die App auch auf Rechnern ohne System-Installation
laeuft. Diese Funktionen finden die Binaries und konfigurieren pytesseract
bzw. liefern den ``poppler_path`` fuer pdf2image — mit Fallback auf den
System-PATH, wenn ein Buendel fehlt (alle Funktionen geben dann None/False
zurueck und aendern nichts).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Repo-Root = eine Ebene ueber nicegui_app/
_REPO_ROOT = Path(__file__).resolve().parent.parent


def bundled_tesseract_exe(root: Optional[Path] = None) -> Optional[str]:
    """Pfad zur gebuendelten tesseract.exe, oder None wenn nicht vorhanden."""
    base = Path(root) if root else _REPO_ROOT
    exe = base / 'tesseract' / 'Tesseract-OCR' / 'tesseract.exe'
    return str(exe) if exe.is_file() else None


def bundled_tessdata_dir(root: Optional[Path] = None) -> Optional[str]:
    """Pfad zum gebuendelten tessdata-Verzeichnis, oder None."""
    base = Path(root) if root else _REPO_ROOT
    d = base / 'tesseract' / 'Tesseract-OCR' / 'tessdata'
    return str(d) if d.is_dir() else None


def bundled_poppler_bin(root: Optional[Path] = None) -> Optional[str]:
    """Poppler-bin-Verzeichnis fuer das pdf2image-Argument ``poppler_path``.

    None bedeutet: pdf2image sucht selbst im System-PATH. pdf2image braucht
    pdfinfo (Seitenzahl-Vorab-Check) UND pdftoppm (Rendering) — ein
    Teil-Buendel ohne pdfinfo.exe wuerde sonst stumm auf den schlechteren
    PyMuPDF-Fallback durchschlagen.
    """
    base = Path(root) if root else _REPO_ROOT
    d = base / 'poppler' / 'bin'
    if (d / 'pdftoppm.exe').is_file() and (d / 'pdfinfo.exe').is_file():
        return str(d)
    return None


# Muss zu lang='deu+eng' in text_extraction.py passen
_REQUIRED_LANGS = ('deu', 'eng')


def configure_pytesseract(pytesseract_module, root: Optional[Path] = None) -> bool:
    """Verdrahtet pytesseract auf das gebuendelte Tesseract, falls vollstaendig.

    Setzt zusaetzlich TESSDATA_PREFIX auf das gebuendelte tessdata, weil eine
    System-Installation diese Variable global setzen kann und Tesseract sie
    dem eigenen Installationsverzeichnis vorzieht — ohne Override wuerden die
    gebuendelten Sprachdaten (z.B. deu.traineddata) ignoriert.

    Konfiguriert NUR, wenn das Buendel komplett ist (exe + traineddata fuer
    alle benoetigten Sprachen): ein Teil-Buendel darf ein funktionierendes
    System-Tesseract im PATH nicht aushebeln.

    Rueckgabe: True wenn das Buendel verwendet wird, False bei PATH-Fallback.
    """
    exe = bundled_tesseract_exe(root)
    tessdata = bundled_tessdata_dir(root)
    if pytesseract_module is None or not exe or not tessdata:
        return False
    if not all((Path(tessdata) / f'{lang}.traineddata').is_file() for lang in _REQUIRED_LANGS):
        return False
    pytesseract_module.pytesseract.tesseract_cmd = exe
    os.environ['TESSDATA_PREFIX'] = tessdata
    return True
