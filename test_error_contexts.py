"""Smoke-Test für alle _handle_error Kontexte.

Ziel: Sicherstellen, dass das Aufrufen von _handle_error mit jedem bekannten Kontext keine Exception wirft.
Kein Assertions-Fokus auf UI (Toast/Event deaktiviert).
"""
from __future__ import annotations
import json
import types
import traceback
from collections import defaultdict

INVENTORY_FILE = "error_context_inventory.json"
TARGET_MODULE = "quality_gui_main_app"


def load_contexts() -> list[str]:
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("all_contexts", [])


def build_dummy_app(cls):
    # Minimale Dummy-Instanz ohne vollständige Tk-Initialisierung
    dummy = object.__new__(cls)  # bypass __init__
    dummy.logger = types.SimpleNamespace(info=lambda *a, **k: None,
                                         warning=lambda *a, **k: None,
                                         error=lambda *a, **k: None,
                                         debug=lambda *a, **k: None)
    # Capture toasts for assertion
    dummy._captured_toasts = []
    def _capture_toast(message, type_, *a, **k):
        dummy._captured_toasts.append((message, type_))
    dummy.show_toast = _capture_toast
    dummy._t = lambda s: s  # simple passthrough
    dummy.event_bus = None
    return dummy


def test_handle_error_contexts():
    import importlib
    mod = importlib.import_module(TARGET_MODULE)
    # Versuche Klasse / Fallback
    app_cls = None
    # Heuristik: Klasse mit _handle_error Methode
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if isinstance(attr, type) and hasattr(attr, '_handle_error'):
            app_cls = attr
            break
    assert app_cls is not None, "Keine passende App-Klasse mit _handle_error gefunden"
    dummy = build_dummy_app(app_cls)

    contexts = load_contexts()
    errors = []
    mapped_present = 0
    for ctx in contexts:
        try:
            dummy._handle_error(Exception("test"), context=ctx, toast=False)
        except Exception as e:
            errors.append((ctx, str(e)))
        # Prüfe zusätzlich Mapping für definierte Standardkontexte (Toast war deaktiviert)
        # Aktiviere Toast für einige bekannte Standard-Mappings zur Stichprobe
        if ctx in {
            "files.counter.update", "upload.source", "pairing.manual.dialog",
            "export.failed", "project.structure.create", "settings.view", "toast.show"
        }:
            before = len(dummy._captured_toasts)
            dummy._handle_error(Exception("probe"), context=ctx, toast=True)
            after = len(dummy._captured_toasts)
            if after > before:
                last_msg, last_type = dummy._captured_toasts[-1]
                assert last_type == "error"
                assert isinstance(last_msg, str) and len(last_msg) > 0
                mapped_present += 1
    if errors:
        trace = "\n".join(f"{c}: {m}" for c, m in errors)
        traceback.print_exc()
        raise AssertionError(f"_handle_error brach bei {len(errors)} Kontext(en):\n{trace}")
    # Erwartung: Mindestens 5 gemappte Stichproben sollten Toast erzeugt haben
    assert mapped_present >= 5, f"Zu wenige Default-Mapping Toasts erfasst: {mapped_present}"
