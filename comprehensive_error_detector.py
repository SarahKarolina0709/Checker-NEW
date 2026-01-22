"""DEPRECATED WRAPPER – bitte `quality_gui_comprehensive_error_detector` verwenden.

Wird nach Übergangsphase gelöscht.
"""
from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "comprehensive_error_detector ist veraltet – quality_gui_comprehensive_error_detector verwenden (Entfernung geplant)",
    DeprecationWarning,
    stacklevel=2,
)
from quality_gui_comprehensive_error_detector import *  # type: ignore  # noqa: F401,F403

if __name__ == '__main__':  # pragma: no cover
    from quality_gui_comprehensive_error_detector import main  # type: ignore
    main()
