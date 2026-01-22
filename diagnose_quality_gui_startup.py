"""Kompatibilitäts-Wrapper – Startup Diagnose umbenannt nach quality_gui_diagnose_startup.py."""
from __future__ import annotations
try:  # pragma: no cover
    from quality_gui_diagnose_startup import *  # type: ignore
except Exception:
    def main():  # type: ignore
        print("⚠️ Startup Diagnose-Modul nicht verfügbar")
else:
    from quality_gui_diagnose_startup import main  # type: ignore

if __name__ == '__main__':
    main()