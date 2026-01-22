"""DEPRECATED WRAPPER – bitte `quality_gui_comprehensive_duplicate_analysis` verwenden.

Wird nach Übergangsphase gelöscht.
"""
from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "comprehensive_duplicate_analysis ist veraltet – quality_gui_comprehensive_duplicate_analysis verwenden (Entfernung geplant)",
    DeprecationWarning,
    stacklevel=2,
)
from quality_gui_comprehensive_duplicate_analysis import *  # type: ignore  # noqa: F401,F403

if __name__ == '__main__':  # pragma: no cover
    from quality_gui_comprehensive_duplicate_analysis import main  # type: ignore
    main()