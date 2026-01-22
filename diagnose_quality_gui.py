"""Kompatibilitäts-Wrapper – ursprüngliche Datei umbenannt nach quality_gui_diagnose.py.

Bitte zukünftig 'quality_gui_diagnose' direkt verwenden.
"""
from __future__ import annotations
try:  # pragma: no cover
    from quality_gui_diagnose import *  # type: ignore
except Exception:  # Minimal Fallback
    def main():  # type: ignore
        print("⚠️ Diagnose-Modul nicht verfügbar")
if __name__ == '__main__':  # Beibehaltung CLI-Verhalten
    try:
        from quality_gui_diagnose import main  # type: ignore
    except Exception:
        pass
    main()