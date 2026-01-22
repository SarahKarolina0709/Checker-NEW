"""Forwarder (deprecated) – bitte quality_gui_html_integration_report verwenden."""
from quality_gui_html_integration_report import analyze_html_integration  # type: ignore

__all__ = ["analyze_html_integration"]

if __name__ == "__main__":  # weiterhin lauffähig
    analyze_html_integration()