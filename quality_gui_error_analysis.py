"""Alias-Modul für :mod:`error_analysis` mit konsistentem Prefix.

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
    from error_analysis import *  # type: ignore  # noqa: F401,F403
except Exception:  # pragma: no cover
    logger.exception("Fehler beim Import von error_analysis")

try:  # __all__ übernehmen
    from error_analysis import __all__ as _orig_all  # type: ignore
    __all__ = list(_orig_all)
except Exception:  # pragma: no cover
    __all__ = [n for n in globals().keys() if not n.startswith("_")]

# Ergänzung: self_test wird immer exportiert
if "self_test" not in __all__:
    __all__.append("self_test")

try:  # main re-exportieren (optional)
    from error_analysis import main as main  # type: ignore
    if "main" not in __all__:
        __all__.append("main")
except Exception:  # pragma: no cover
    pass

if __name__ == "__main__":  # pragma: no cover
    import argparse, json, traceback, time

    def self_test() -> dict:
        """Leichte Selbstprüfung des Alias-Moduls.

        Returns
        -------
        dict
            Ergebnisdaten mit Feldern: ok (bool), errors (List[str]), duration_s (float)
        """
        started = time.time()
        result = {"ok": True, "errors": [], "duration_s": 0.0}
        # Prüfe, ob main vorhanden (optional)
        if not ("main" in globals() and callable(globals()["main"])):
            result["ok"] = False
            result["errors"].append("main fehlt oder ist nicht callbar")
        # Probe: __all__ konsistent (enthält self_test)
        if "self_test" not in globals().get("__all__", []):
            result["ok"] = False
            result["errors"].append("self_test nicht in __all__")
        result["duration_s"] = round(time.time() - started, 4)
        return result

    parser = argparse.ArgumentParser(description="Alias-Starter für error_analysis")
    parser.add_argument("--self-test", action="store_true", help="Nur Selbsttest durchführen und JSON ausgeben")
    parser.add_argument("--json", action="store_true", help="Ergebnis als JSON ausgeben (bei Selbsttest)")
    args, unknown = parser.parse_known_args()

    if args.self_test:
        res = self_test()
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if res["ok"]:
                print("[OK] self_test: keine Probleme")
            else:
                print("[X] self_test: Probleme")
                for e in res["errors"]:
                    print(" -", e)
            print("Dauer:", res["duration_s"], "s")
        sys.exit(0 if res["ok"] else 1)

    # Normales Durchreichen an main
    if "main" in globals() and callable(globals()["main"]):
        try:
            globals()["main"]()  # type: ignore[misc]
        except SystemExit:
            raise
        except Exception:  # pragma: no cover
            logger.exception("[quality_gui_error_analysis] Startfehler")
            traceback.print_exc()
            sys.exit(1)
    else:  # pragma: no cover
        logger.error("main() nicht verfügbar in error_analysis")
        sys.exit(1)
