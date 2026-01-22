"""Alias-Modul für :mod:`comprehensive_diagnosis` mit sauberem Re-Export.

Verbesserungen:
 - Explizites __all__ (nutzt Ursprungs-__all__ falls vorhanden)
 - Direkter Re-Export von main
 - Konsistentes Logging statt print
 - Sinnvoller Exit-Code bei CLI-Aufruf
"""
from __future__ import annotations
import logging, sys, warnings as _warnings

logger = logging.getLogger(__name__)

try:  # Basis-Import (wildcard nur für Komfort / Rückwärtskompatibilität)
    from comprehensive_diagnosis import *  # type: ignore  # noqa: F401,F403
except Exception:  # pragma: no cover - Importfehler werden unten geloggt
    logger.exception("Fehler beim Import von comprehensive_diagnosis")

_warnings.warn(
    "Direkter Import von comprehensive_diagnosis künftig durch quality_gui_comprehensive_diagnosis ersetzen; Altmodul bleibt nur kurzfristig",  # noqa: E501
    DeprecationWarning,
    stacklevel=2,
)

# __all__ ermitteln
try:
    from comprehensive_diagnosis import __all__ as _orig_all  # type: ignore
    __all__ = list(_orig_all)
except Exception:
    # Fallback: alles exportieren was öffentlich wirkt (schlank halten)
    __all__ = [n for n in globals().keys() if not n.startswith('_')]

# main direkt re-exportieren (falls vorhanden)
try:
    from comprehensive_diagnosis import main as main  # type: ignore
    if 'main' not in __all__:
        __all__.append('main')
except Exception:
    # main optional
    pass

if __name__ == "__main__":  # pragma: no cover
    if 'main' in globals() and callable(globals()['main']):
        try:
            globals()['main']()
        except SystemExit:
            raise
        except Exception:
            logger.exception("[quality_gui_comprehensive_diagnosis] Fehler beim Start")
            sys.exit(1)
    else:
        logger.error("main() nicht verfügbar in comprehensive_diagnosis")
        sys.exit(1)
