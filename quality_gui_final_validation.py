"""Alias-Modul für :mod:`final_validation` mit konsistentem Prefix.

Verbesserungen:
- Explizites __all__ (Übernahme aus Ursprungsmodul falls vorhanden)
- Direkter Re-Export von main
- Logging statt Print
- sys.exit(1) bei Fehler für CLI-Einsatz
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

try:  # Wildcard für Rückwärtskompatibilität
    from final_validation import *  # type: ignore  # noqa: F401,F403
except Exception:  # pragma: no cover
    logger.exception("Fehler beim Import von final_validation")

try:  # __all__ übernehmen
    from final_validation import __all__ as _orig_all  # type: ignore
    __all__ = list(_orig_all)
except Exception:  # pragma: no cover
    __all__ = [n for n in globals().keys() if not n.startswith("_")]

try:  # main re-exportieren (optional)
    from final_validation import main as main  # type: ignore
    if "main" not in __all__:
        __all__.append("main")
except Exception:  # pragma: no cover
    pass

if __name__ == "__main__":  # pragma: no cover
    if "main" in globals() and callable(globals()["main"]):
        try:
            globals()["main"]()
        except SystemExit:
            raise
        except Exception:  # pragma: no cover
            logger.exception("[quality_gui_final_validation] Startfehler")
            sys.exit(1)
    else:  # pragma: no cover
        logger.error("main() nicht verfügbar in final_validation")
        sys.exit(1)
