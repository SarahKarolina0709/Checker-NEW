"""Forwarder (deprecated) – bitte quality_gui_helper_report verwenden.

Historie: Ursprünglich helper_quality_report.py. Für konsistenten Prefix
wurde die eigentliche Implementierung nach quality_gui_helper_report.py
verschoben. Dieser Wrapper re-exportiert nur die öffentliche API.
"""
from quality_gui_helper_report import generate_dynamic_report  # type: ignore

__all__ = ["generate_dynamic_report"]
