"""
Export System Package
====================

Modular export system for the Checker application providing:
- PDF export capabilities
- Multi-format export support (JSON, CSV, HTML, XML, DOCX, TXT)
- Batch processing
- Template system
- Statistics tracking
"""

from .export_manager import ExportSystemManager, create_modern_export_system
from .pdf_system import PDFExportSystem, exportiere_bericht_pdf, exportiere_umfassende_pruefung_pdf
from .format_manager import FormatExportManager

__all__ = [
    'ExportSystemManager',
    'PDFExportSystem',
    'FormatExportManager',
    'create_modern_export_system',
    'exportiere_bericht_pdf',
    'exportiere_umfassende_pruefung_pdf'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Checker Development Team'