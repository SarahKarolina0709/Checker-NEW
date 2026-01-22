#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup Diagnose (v2) – robust für lokale Runs und CI/headless.
- Headless-Erkennung & sichere Tk/Tcl-Checks
- JSON/CI-Ausgabe, klare Exit-Codes
- Flexible Dateiliste und Modulname

Standardverhalten: Diagnose + optionaler Minimalstart.
"""
from __future__ import annotations
import os, sys, json, argparse, importlib, traceback, platform
from typing import List, Dict, Any
import time


def parse_args():
    p = argparse.ArgumentParser(description="Quality GUI Startup Diagnostics")
    p.add_argument("--json", action="store_true", help="Maschinenlesbare JSON-Ausgabe")
    p.add_argument("--skip-minimal", action="store_true", help="Minimal-Startup-Test überspringen")
    p.add_argument("--no-emoji", action="store_true", help="ASCII-Output (keine Emojis)")
    p.add_argument("--force-tk", action="store_true",
                   help="Tk-Fenster-Checks auch im Headless-Modus erzwingen (nicht empfohlen in CI)")
    p.add_argument("--module-name", default="modern_translation_quality_gui",
                   help="GUI-Hauptmodul (Default: modern_translation_quality_gui)")
    p.add_argument("--class-name", default="ProfessionalTranslationQualityApp",
                   help="Name der Hauptklasse (Default: ProfessionalTranslationQualityApp)")
    p.add_argument("--files", nargs="*", default=[
        "modern_translation_quality_gui.py",
        "ui_theme.py",
        "welcome_screen.py",
        "config.json"
    ], help="Zusätzliche Dateien, deren Existenz geprüft wird")
    p.add_argument("--output", help="Schreibe JSON-Ausgabe in Datei (UTF-8)")
    return p.parse_args()


def is_headless() -> bool:
    if sys.platform.startswith("linux"):
        return not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return False


def marks(no_emoji=False):
    if no_emoji:
        return {"ok": "[OK]", "err": "[X]", "sec": "\n===", "bullet": "-"}
    return {"ok": "✅", "err": "❌", "sec": "\n📋", "bullet": "•"}


def section(title: str, m):
    print(f"{m['sec']} {title}")


def _add_problem(problems: List[Dict[str, Any]], stage: str, message: str):
    problems.append({"stage": stage, "message": message})


def diagnose_python_env(details: Dict[str, Any], problems: List[Dict[str, Any]], m):
    section("SCHRITT 1: Python Environment", m)
    try:
        details["python"] = {
            "version": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "arch": platform.machine(),
        }
        print(f"{m['ok']} Python Version: {details['python']['version']}")
        print(f"{m['ok']} Executable: {details['python']['executable']}")
    except Exception as e:
        _add_problem(problems, "python", f"Python Env: {e}")
        print(f"{m['err']} Python Env: {e}")


def diagnose_customtkinter(details: Dict[str, Any], problems: List[Dict[str, Any]], m):
    """Prüfe Import und Version von CustomTkinter."""
    section("SCHRITT 2: CustomTkinter", m)
    try:
        import customtkinter as ctk  # type: ignore
        details["customtkinter"] = {"version": getattr(ctk, "__version__", "unknown")}
        print(f"{m['ok']} CustomTkinter Version: {details['customtkinter']['version']}")
    except Exception as e:  # noqa: BLE001
        _add_problem(problems, "customtkinter", f"CustomTkinter: {e}")
        print(f"{m['err']} CustomTkinter: {e}")


def diagnose_tk(details: Dict[str, Any], problems: List[Dict[str, Any]], m, allow_window: bool):
    section("SCHRITT 3: Tkinter", m)
    try:
        import tkinter as tk  # noqa
        info: Dict[str, Any] = {}
        try:  # Tcl-Version ohne echtes Fenster
            tcl = tk.Tcl()
            info["tcl_version"] = tcl.eval("info patchlevel")
            try:  # Tk-Paket
                info["tk_version"] = tcl.eval('package require Tk')
            except Exception as e:
                info["tk_version"] = None
                info["tk_package_error"] = str(e)
        except Exception as e:
            info["tcl_error"] = str(e)
        if allow_window:
            try:
                r = tk.Tk(); r.withdraw(); r.destroy()
                info["tk_window_ok"] = True
            except Exception as e:
                info["tk_window_ok"] = False
                info["tk_window_error"] = str(e)
        details["tkinter"] = info
        if info.get("tk_version"):
            print(f"{m['ok']} Tcl/Tk: Tcl {info.get('tcl_version')} | Tk {info.get('tk_version')}")
        else:
            if "tk_package_error" in info:
                print(f"{m['err']} Tk nicht ladbar: {info['tk_package_error']} (Tcl {info.get('tcl_version','?')})")
                _add_problem(problems, "tkinter", f"Tk load failed: {info['tk_package_error']}")
            else:
                print(f"{m['ok']} Tcl Version: {info.get('tcl_version', '?')} (Tk nicht geprüft)")
        if allow_window:
            print(f"{m['ok']} Tkinter Window Test: {'OK' if info.get('tk_window_ok') else 'Fehler'}")
            if not info.get("tk_window_ok"):
                _add_problem(problems, "tkinter", f"Tk window: {info.get('tk_window_error')}")
    except Exception as e:
        _add_problem(problems, "tkinter", f"Tkinter: {e}")
        print(f"{m['err']} Tkinter: {e}")


def diagnose_import_module(module_name: str, details: Dict[str, Any], problems: List[Dict[str, Any]], m):
    """Importiere das Hauptmodul und erfasse Dateipfad."""
    section("SCHRITT 4: Quality GUI Import", m)
    try:
        mod = importlib.import_module(module_name)
        details["module"] = {"name": module_name, "file": getattr(mod, "__file__", None)}
        print(f"{m['ok']} Modul importiert: {module_name} @ {details['module']['file']}")
        return mod
    except Exception as e:  # noqa: BLE001
        _add_problem(problems, "import", f"GUI Import: {e}")
        print(f"{m['err']} GUI Import: {e}")
        traceback.print_exc()
        return None


def diagnose_main_class(mod, class_name: str, details: Dict[str, Any], problems: List[Dict[str, Any]], m):
    """Prüfe ob die angegebene Hauptklasse existiert."""
    section("SCHRITT 5: Klassen-Prüfung", m)
    try:
        getattr(mod, class_name)
        print(f"{m['ok']} Haupt-Klasse gefunden ({class_name})")
        details["class"] = True
    except Exception as e:  # noqa: BLE001
        _add_problem(problems, "class", f"Klasse fehlt: {e}")
        print(f"{m['err']} Klasse fehlt ({class_name}): {e}")
        details["class"] = False


def diagnose_files(file_list: List[str], details: Dict[str, Any], problems: List[Dict[str, Any]], m):
    section("SCHRITT 6: Dateien", m)
    files = []
    for f in file_list:
        item = {"name": f, "exists": os.path.exists(f)}
        if item["exists"]:
            try:
                item["size"] = os.path.getsize(f)
                print(f"{m['ok']} {f} ({item['size']} bytes)")
                if f.lower().endswith('.json') and os.path.getsize(f) > 0:
                    try:
                        with open(f, 'r', encoding='utf-8') as fh:
                            json.load(fh)
                        item['json_ok'] = True
                    except Exception as je:
                        item['json_ok'] = False
                        _add_problem(problems, "files", f"JSON ungültig: {f} ({je})")
                        print(f"{m['err']} JSON ungültig: {f} ({je})")
            except Exception as e:
                print(f"{m['err']} {f}: {e}")
                _add_problem(problems, "files", f"Datei-Fehler {f}: {e}")
        else:
            print(f"{m['err']} {f} fehlt")
            _add_problem(problems, "files", f"Missing file: {f}")
        files.append(item)
    details["files"] = files


def try_minimal_startup(module_name: str, class_name: str, details: Dict[str, Any], problems: List[Dict[str, Any]], m, allow_window: bool) -> bool:
    """Starte die App-Klasse minimal um Root-Erstellung zu prüfen."""
    print("\n🚀 MINIMAL STARTUP TEST")
    if not allow_window:
        print("⚠️ Headless erkannt – Fenster-Test übersprungen (nutze --force-tk zum Erzwingen).")
        details["minimal_startup"] = {"skipped": True, "reason": "headless"}
        return True
    try:
        mod = importlib.import_module(module_name)
        App = getattr(mod, class_name)
        app = App()  # type: ignore[call-arg]
        ok = hasattr(app, 'root') and getattr(app, 'root') is not None
        print(f"{m['ok']} Instanz erstellt" if ok else "⚠️ Root fehlt")
        details["minimal_startup"] = {"ok": bool(ok)}
        try:
            if ok:
                app.root.withdraw(); app.root.destroy()  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass
        return bool(ok)
    except Exception as e:  # noqa: BLE001
        _add_problem(problems, "minimal", f"Minimal Startup: {e}")
        print(f"{m['err']} Minimal Startup: {e}")
        traceback.print_exc()
        details["minimal_startup"] = {"ok": False, "error": str(e)}
        return False


def main():
    args = parse_args()
    m = marks(no_emoji=args.no_emoji)
    print("🔍 QUALITY GUI STARTUP DIAGNOSTICS")
    print("=" * 50)
    start_time = time.time()
    details: Dict[str, Any] = {}
    problems: List[Dict[str, Any]] = []
    diagnose_python_env(details, problems, m)
    diagnose_customtkinter(details, problems, m)
    headless = is_headless()
    allow_window = (not headless) or args.force_tk
    details['headless'] = headless
    diagnose_tk(details, problems, m, allow_window=allow_window)
    mod = diagnose_import_module(args.module_name, details, problems, m)
    if mod is not None:
        diagnose_main_class(mod, args.class_name, details, problems, m)
    diagnose_files(args.files, details, problems, m)
    base_ok = len(problems) == 0
    if base_ok and not args.skip_minimal:
        try_minimal_startup(args.module_name, args.class_name, details, problems, m, allow_window=allow_window)
    print("\n🎯 ERGEBNIS")
    ok = len(problems) == 0
    if ok:
        print(f"{m['ok']} Keine Probleme – GUI sollte starten")
    else:
        print(f"{m['err']} Probleme ({len(problems)}):")
        for p in problems:
            try:
                print(f" - [{p['stage']}] {p['message']}")
            except Exception:
                print(f" - {p}")
    details['duration_s'] = round(time.time() - start_time, 4)
    if args.json:
        out = {"ok": ok, "problems": problems, "details": details}
        try:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        except Exception:
            print(json.dumps(out, indent=2))
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as fh:
                    json.dump(out, fh, ensure_ascii=False, indent=2)
                print(f"{m['ok']} JSON gespeichert: {args.output}")
            except Exception as e:
                print(f"{m['err']} Ausgabe-Datei Fehler: {e}")
    elif args.output:  # Falls nur Datei gewünscht ohne --json, trotzdem JSON speichern
        out = {"ok": ok, "problems": problems, "details": details}
        try:
            with open(args.output, 'w', encoding='utf-8') as fh:
                json.dump(out, fh, ensure_ascii=False, indent=2)
            print(f"{m['ok']} JSON gespeichert: {args.output}")
        except Exception as e:
            print(f"{m['err']} Ausgabe-Datei Fehler: {e}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
