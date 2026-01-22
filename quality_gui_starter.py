#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality GUI Starter (robust & flexibel)

Sucht automatisch nach:
  - modern_translation_quality_gui.py
  - quality_gui_main_app.py
oder nutzt --module / --class Overrides.

Startet bevorzugt .run(), sonst .start().

Exit-Codes:
  0  Erfolg
  2  Ziel (Datei/Klasse) nicht gefunden / keine startbare Methode
  3  Import- oder Ladefehler (Modul)
  4  Laufzeitfehler innerhalb der App
"""
from __future__ import annotations

import sys
import argparse
import logging
import traceback
from pathlib import Path
import importlib
import importlib.util
import inspect
import asyncio
from types import ModuleType
import os
import json
import time
from contextlib import contextmanager
try:  # Version Info (optional)
    from importlib.metadata import version as _pkg_version, PackageNotFoundError  # type: ignore
except Exception:  # pragma: no cover
    try:
        from importlib_metadata import version as _pkg_version, PackageNotFoundError  # type: ignore
    except Exception:  # pragma: no cover
        _pkg_version = None  # type: ignore
        PackageNotFoundError = Exception  # type: ignore

# Kandidaten-Dateien & Klassen (Konventionen im Projekt)
CANDIDATES = [
    "modern_translation_quality_gui.py",
    "quality_gui_main_app.py",
]
CLASS_CANDIDATES = [
    "ProfessionalTranslationQualityApp",
    "ProfessionelleUebersetzungsqualitaetsApp",
]

log = logging.getLogger("quality_gui_starter")


def _setup_logging(verbosity: int) -> None:
    """Setzt Logging-Level deterministisch (0=WARNING, 1=INFO, >=2=DEBUG).

    Nutzt force=True, um doppelte Handler und veraltete Formatter zu vermeiden.
    """
    level = logging.WARNING if verbosity <= 0 else (logging.INFO if verbosity == 1 else logging.DEBUG)
    # Force-Reconfig: ab Python 3.8 verfügbar, in unserem Projekt Python 3.12
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s", force=True)
    log.debug("Logging initialisiert (Level=%s)", logging.getLevelName(level))


def _print_and_log(message: str, level: int = logging.INFO) -> None:
    """CLI-Output via print, zusätzlich ins Log spiegeln."""
    print(message)
    try:
        log.log(level, message)
    except Exception:
        pass


@contextmanager
def _temp_sys_path(paths: list[Path]):
    """Temporär zusätzliche Pfade am Anfang von sys.path einfügen.

    Stellt ursprünglichen Zustand wieder her, um Seiteneffekte zu vermeiden.
    """
    original = list(sys.path)
    try:
        # In umgekehrter Reihenfolge einfügen, damit erste Listelemente
        # die Priorität behalten.
        for p in reversed(paths):
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)
        yield
    finally:
        sys.path[:] = original


def _load_module_from_file(mod_name: str, path: Path) -> ModuleType:
    """Direktes Laden eines Moduls von einer Datei (Fallback)."""
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Spec konnte nicht erstellt werden für {path}")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[assignment]
    return mod


def _find_target_module(base_dir: Path, override_module: str | None, search_dirs: list[str]) -> ModuleType | None:
    """Findet oder lädt das Ziel-Modul (Override, Suchpfad, Kandidaten-Dateien)."""
    if override_module:
        log.info("Nutze Override-Modul: %s", override_module)
        return importlib.import_module(override_module)

    # Erst extra Suchverzeichnisse durchsuchen (relative oder absolut)
    for extra in search_dirs:
        extra_path = (base_dir / extra).resolve() if not Path(extra).is_absolute() else Path(extra)
        for name in CANDIDATES:
            p = (extra_path / name).resolve()
            if p.exists():
                log.info("Gefundene GUI-Moduldatei (search-dir %s): %s", extra, p)
                mod_name = p.stem
                try:
                    # Versuche Import mit temporärer sys.path-Erweiterung, damit
                    # auch relative/benachbarte Importe funktionieren.
                    with _temp_sys_path([extra_path, base_dir]):
                        return importlib.import_module(mod_name)
                except Exception:
                    log.debug("Import via Modulname fehlgeschlagen, versuche Dateilader", exc_info=True)
                    # Fallback: Direkter Dateilader (relative Importe in Zielmodul funktionieren
                    # hier u.U. nicht!)
                    return _load_module_from_file(mod_name, p)

    # Basisverzeichnis durchsuchen
    for name in CANDIDATES:
        p = base_dir / name
        if p.exists():
            log.info("Gefundene GUI-Moduldatei: %s", p.name)
            mod_name = p.stem
            try:
                with _temp_sys_path([base_dir]):
                    return importlib.import_module(mod_name)
            except Exception:
                log.debug("Import via Modulname fehlgeschlagen, versuche Dateilader", exc_info=True)
                return _load_module_from_file(mod_name, p)
    return None


def _find_app_class(mod: ModuleType, override_class: str | None):
    """Sucht passende App-Klasse im Modul (Override bevorzugt)."""
    if override_class:
        if hasattr(mod, override_class):
            return getattr(mod, override_class)
        raise AttributeError(f"Klassen-Override '{override_class}' nicht im Modul '{mod.__name__}' gefunden")
    for cls in CLASS_CANDIDATES:
        if hasattr(mod, cls):
            return getattr(mod, cls)
    return None


def _is_app_class(cls) -> bool:
    """Validiert ob Klasse eine App-Klasse ist (run oder start Methode)."""
    return isinstance(cls, type) and (hasattr(cls, "run") or hasattr(cls, "start"))


def _script_dir() -> Path:
    """Unterstützt gefrorene Bundles (PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # type: ignore[attr-defined]
        return Path(getattr(sys, "_MEIPASS"))  # noqa: PIE804
    return Path(__file__).resolve().parent


def _find_entrypoint_app() -> tuple[str | None, type | None]:
    """Versucht App-Klasse über Entry Points (group=quality_gui.app) zu finden."""
    try:
        try:
            from importlib.metadata import entry_points  # Python 3.10+
        except Exception:  # pragma: no cover
            from importlib_metadata import entry_points  # type: ignore  # Backport

        eps = entry_points()
        # Neues API (select) bevorzugen
        try:
            eps_selected = eps.select(group="quality_gui.app")  # type: ignore[attr-defined]
        except Exception:
            eps_selected = [ep for ep in eps if getattr(ep, "group", None) == "quality_gui.app"]
        for ep in eps_selected:
            try:
                cls = ep.load()
                if _is_app_class(cls):
                    log.info("Entry Point gefunden: %s -> %s", ep.name, cls)
                    return cls.__module__, cls
            except Exception:
                log.debug("Entry Point Laden fehlgeschlagen: %s", getattr(ep, "name", "?"), exc_info=True)
    except Exception:
        pass
    return None, None


def _iter_app_classes(mod: ModuleType):
    for name, obj in vars(mod).items():
        try:
            if _is_app_class(obj):
                yield f"{mod.__name__}.{name}"
        except Exception:
            continue


def _resolve_dotted_class(dotted: str) -> tuple[ModuleType, type]:
    """Erlaubt 'pkg.mod:Class' oder 'pkg.mod.Class' als Pfadangabe für --class.
    Raises AttributeError bei Ungültigkeit.
    """
    mod_part, _, cls_name = dotted.replace(":", ".").rpartition(".")
    if not mod_part or not cls_name:
        raise AttributeError(f"Ungültiger Klassenpfad: {dotted}")
    m = importlib.import_module(mod_part)
    if not hasattr(m, cls_name):
        raise AttributeError(f"Klasse '{cls_name}' nicht in Modul '{mod_part}' gefunden")
    cls = getattr(m, cls_name)
    if not _is_app_class(cls):
        raise AttributeError(f"Klasse '{cls_name}' bietet keine run()/start() Methode")
    return m, cls  # type: ignore[return-value]


def _call_app_entry(app, pass_through):
    """Startet bevorzugt run(), sonst start(); unterstützt sync & async.
    
    Argumente werden nur übergeben, wenn die Zielmethode *args akzeptiert.
    Bei bereits laufender Loop (z.B. Jupyter) wird Task erstellt (Fire-&-Forget) und 0 geliefert.
    Gibt Rückgabewert zurück (Exit-Code Kandidat) oder None.
    """
    def _supports_varargs(fn) -> bool:
        try:
            sig = inspect.signature(fn)
            return any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values())
        except Exception:
            return False

    for name in ("run", "start"):
        if hasattr(app, name):
            fn = getattr(app, name)
            use_args = _supports_varargs(fn)
            if inspect.iscoroutinefunction(fn):
                try:
                    return asyncio.run(fn(*pass_through if use_args else ()))
                except RuntimeError as re:  # Event loop evtl. aktiv
                    if "already running" in str(re).lower():
                        loop = asyncio.get_event_loop()
                        loop.create_task(fn(*pass_through if use_args else ()))
                        log.debug("Coroutine als Task in bestehender Event-Loop gestartet (Fire-and-Forget)")
                        return 0
                    raise
            return fn(*pass_through if use_args else ())
    return None


def main(argv=None) -> int:  # pragma: no cover (wird typ. manuell aufgerufen)
    # Version ermitteln (optional, fällt auf dev zurück)
    if _pkg_version:
        try:
            _VERSION = _pkg_version("quality-gui")  # Paketname ggf. anpassen
        except Exception:  # PackageNotFoundError
            _VERSION = "dev"
    else:
        _VERSION = "dev"

    parser = argparse.ArgumentParser(
        prog="quality_gui_starter",
        add_help=True,
        description="Starter für Quality GUI mit flexiblen Overrides",
        epilog=(
            "Hinweis: Argumente nach '--' werden unverändert an die App weitergereicht. "
            "Optional nutzbare Umgebungsvariablen: QUALITY_GUI_STARTER_MODULE, QUALITY_GUI_STARTER_CLASS."
        ),
    )
    parser.add_argument("--module", help="Explizites Modul importieren (z.B. quality_gui_main_app)", default=None)
    parser.add_argument("--class", dest="klass", help="Expliziter App-Klassenname", default=None)
    parser.add_argument("--module-path", dest="module_path", help="Python-Datei direkt laden (z.B. ./foo/bar.py)", default=None)
    parser.add_argument("--no-chdir", action="store_true", help="Kein chdir ins Skriptverzeichnis (bewahrt aktuelles Working Directory)")
    parser.add_argument("--search-dir", action="append", default=[], help="Zusätzliche Ordner für GUI-Datei-Suche (mehrfach nutzbar)")
    parser.add_argument("--list", action="store_true", help="Verfügbare App-Klassen im Zielmodul auflisten und beenden")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_VERSION}")
    parser.add_argument("--dry-run", action="store_true", help="Ziel finden, aber nicht starten")
    parser.add_argument("--print-selection", action="store_true", help="Ausgewähltes Modul/Klasse ausgeben")
    parser.add_argument("--json-info", action="store_true", help="Maschinenlesbare Auswahl (JSON) ausgeben und beenden")
    parser.add_argument("--timing", action="store_true", help="Startdauer messen und nach Ende ausgeben")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Erhöht Verbosität (-v / -vv)")
    args, pass_through = parser.parse_known_args(argv)

    t_start = time.perf_counter()

    _setup_logging(args.verbose)

    # Windows Encoding Fix für Ausgabe (Emojis/Umlaute)
    if os.name == "nt":
        for _s in (sys.stdout, sys.stderr):  # pragma: no cover
            try:
                _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            except Exception:
                pass

    script_dir = _script_dir()
    if not args.no_chdir:
        try:
            os.chdir(script_dir)
            log.debug("Arbeitsverzeichnis gewechselt zu %s", script_dir)
        except Exception:
            log.debug("chdir fehlgeschlagen (fortfahren ohne Wechsel)", exc_info=args.verbose >= 2)

    # --search-dir Validierung (nur Warnung, kein Abbruch)
    if args.search_dir:
        invalid = []
        for d in args.search_dir:
            p_abs = Path(d)
            if p_abs.is_absolute():
                if not p_abs.exists():
                    invalid.append(d)
            else:
                if not (script_dir / d).exists():
                    invalid.append(d)
        if invalid:
            _print_and_log(f"[quality_gui_starter] ⚠️ Ungültige --search-dir: {', '.join(invalid)}", logging.WARNING)

    preselected_cls = None
    mod: ModuleType | None = None
    selection_source = "unknown"

    # Env Overrides (falls CLI nicht gesetzt)
    if not args.module:
        env_mod = os.environ.get("QUALITY_GUI_STARTER_MODULE")
        if env_mod:
            args.module = env_mod
    if not args.klass:
        env_cls = os.environ.get("QUALITY_GUI_STARTER_CLASS")
        if env_cls:
            args.klass = env_cls

    # Dotted class path ohne explizites --module (direkte Auflösung)
    if args.klass and ("." in args.klass or ":" in args.klass) and not args.module:
        try:
            mod, preselected_cls = _resolve_dotted_class(args.klass)
            selection_source = "dotted"
        except Exception as e:
            print(f"[quality_gui_starter] ❌ Exit=2 Fehler beim Klassenpfad: {e}")
            if args.verbose:
                traceback.print_exc()
            return 2

    # Modul laden (falls noch nicht über dotted resolve gesetzt)
    try:
        if mod is None:
            # Direkter Datei-Import via --module-path hat höchste Priorität
            if args.module_path:
                mp = Path(args.module_path)
                if not mp.is_absolute():
                    mp = (script_dir / mp).resolve()
                if not mp.exists():
                    _print_and_log(f"[quality_gui_starter] ❌ Exit=2 --module-path nicht gefunden: {mp}", logging.ERROR)
                    return 2
                mod = _load_module_from_file(mp.stem, mp)
                selection_source = "module_path"
            else:
                mod = _find_target_module(script_dir, args.module, args.search_dir)
                if mod is not None:
                    selection_source = "override" if args.module else "candidates"
    except ModuleNotFoundError as e:  # Spezieller Fall Tk / CTk
        if e.name in ("tkinter", "customtkinter"):
            print("[quality_gui_starter] ❌ Exit=3 Tk-Toolkit nicht verfügbar. Linux: 'sudo apt install python3-tk' • macOS: 'brew install python-tk' • Windows: Python-Installer mit Tcl/Tk-Komponente.")
            if args.verbose:
                traceback.print_exc()
            return 3
        _print_and_log(f"[quality_gui_starter] ❌ Exit=3 Importfehler: {e}", logging.ERROR)
        if args.verbose:
            traceback.print_exc()
        return 3
    except Exception as e:  # Import-/Ladefehler allgemein
        _print_and_log(f"[quality_gui_starter] ❌ Exit=3 Importfehler: {e}", logging.ERROR)
        if args.verbose:
            traceback.print_exc()
        return 3

    if mod is None:
        # Entry Point Fallback
        ep_modname, ep_cls = _find_entrypoint_app()
        if ep_cls:
            try:
                mod = importlib.import_module(ep_modname)
                preselected_cls = ep_cls
                selection_source = "entry_point"
            except Exception as e:
                _print_and_log(f"[quality_gui_starter] ❌ Exit=3 Entry Point Importfehler: {e}", logging.ERROR)
                if args.verbose:
                    traceback.print_exc()
                return 3
        else:
            _print_and_log("[quality_gui_starter] ❌ Exit=2 Keine GUI-Datei gefunden (modern/main_app), kein --module und kein Entry Point", logging.ERROR)
            return 2

    # Klassenliste falls gewünscht
    if args.list:
        classes = sorted(_iter_app_classes(mod))
        _print_and_log("[quality_gui_starter] Verfügbare Klassen:")
        if not classes:
            print("  — keine gefunden —")
        else:
            for c in classes:
                print(f"  - {c}")
            print("\nMit --class <Name> oder vollqualifiziertem Pfad starten, z.B.:\n  --class pkg.mod:MyApp")
        _print_and_log("[quality_gui_starter] ✅ Exit=0 Erfolg")
        return 0

    # Klasse finden
    try:
        if preselected_cls and not (args.klass and ("." not in args.klass and ":" not in args.klass)):
            # preselected durch dotted oder Entry Point, außer expliziter einfacher Klassenname überschreibt
            app_cls = preselected_cls
        else:
            app_cls = _find_app_class(mod, args.klass)
    except AttributeError as e:
        _print_and_log(f"[quality_gui_starter] ❌ Exit=2 {e}", logging.ERROR)
        return 2
    except Exception as e:
        _print_and_log(f"[quality_gui_starter] ❌ Exit=3 Unerwarteter Fehler bei Klassensuche: {e}", logging.ERROR)
        if args.verbose:
            traceback.print_exc()
        return 3

    if app_cls is None or not _is_app_class(app_cls):
        _print_and_log("[quality_gui_starter] ❌ Exit=2 Keine passende App-Klasse gefunden (erwartet .run() oder .start())", logging.ERROR)
        return 2

    # Instanz & Start (Laufzeitfehler separat behandeln)
    try:
        # Bei Info-Ausgabe: JSON hat Priorität vor print_selection, zudem keine Instanziierung nötig
        if args.json_info:
            info = {
                "module": mod.__name__,
                "class": app_cls.__name__,
                "source": selection_source,
                "search_dirs": args.search_dir,
                "dry_run": bool(args.dry_run),
                "timing_sec": None,
            }
            print(json.dumps(info, ensure_ascii=False))
            return 0
        if args.print_selection:
            _print_and_log(f"[quality_gui_starter] Auswahl: module={mod.__name__}, class={app_cls.__name__}, source={selection_source}")
        if args.dry_run:
            if args.timing:
                elapsed = time.perf_counter() - t_start
                _print_and_log(f"[quality_gui_starter] ⏱ Laufzeit: {elapsed:.3f}s")
            _print_and_log(f"[quality_gui_starter] ✅ Exit=0 Dry-Run erfolgreich (module={mod.__name__}, class={app_cls.__name__})")
            return 0

        app = app_cls()
        ret = _call_app_entry(app, pass_through)
        if args.timing:
            elapsed = time.perf_counter() - t_start
            _print_and_log(f"[quality_gui_starter] ⏱ Laufzeit: {elapsed:.3f}s")
        # Rückgabewert -> Exit-Code Mapping
        if isinstance(ret, bool):
            code = 0 if ret else 1
            if code == 0:
                _print_and_log("[quality_gui_starter] ✅ Exit=0 Erfolg")
            return code
        if isinstance(ret, int):
            if ret == 0:
                _print_and_log("[quality_gui_starter] ✅ Exit=0 Erfolg")
            return ret
        _print_and_log("[quality_gui_starter] ✅ Exit=0 Erfolg")
        return 0
    except KeyboardInterrupt:
        _print_and_log("[quality_gui_starter] ⛔ Exit=130 Abgebrochen (Ctrl-C)", logging.WARNING)
        return 130
    except ModuleNotFoundError as e:
        if e.name in ("tkinter", "customtkinter"):
            _print_and_log("[quality_gui_starter] ❌ Exit=3 Tk-Toolkit nicht verfügbar. Linux: 'sudo apt install python3-tk' • macOS: 'brew install python-tk' • Windows: Python-Installer mit Tcl/Tk-Komponente.", logging.ERROR)
            if args.verbose:
                traceback.print_exc()
            return 3
        _print_and_log(f"[quality_gui_starter] ❌ Exit=3 Laufzeitfehler (Import): {e}", logging.ERROR)
        if args.verbose:
            traceback.print_exc()
        return 3
    except Exception as e:
        _print_and_log(f"[quality_gui_starter] ❌ Exit=4 Laufzeitfehler: {e}", logging.ERROR)
        if args.verbose:
            traceback.print_exc()
        return 4


if __name__ == "__main__":
    sys.exit(main())
