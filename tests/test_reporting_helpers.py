import os
import json
import csv
import tempfile
from pathlib import Path

import types
import builtins

import quality_gui_reporting as qr


class DummySettings:
    def __init__(self, values=None):
        self._values = values or {}
        self._store = {}

    def get(self, key, default=None):
        return self._values.get(key, default)

    def set(self, key, value):
        self._store[key] = value


class DummyApp:
    def __init__(self, values=None):
        self.settings_service = DummySettings(values)
        self._events = []
        self._status = []
        self._toasts = []
        self.analysis_results = {}

    def update_status(self, text: str):
        self._status.append(text)

    def _t(self, text: str) -> str:
        return text

    def _log_event(self, event_name: str, **edata):
        self._events.append((event_name, edata))

    def show_toast(self, message, type, duration=2000):
        self._toasts.append((message, type, duration))


def test_safe_write_happy_path(tmp_path):
    target = tmp_path / "ok.txt"

    def writer():
        target.write_text("ok", encoding="utf-8")

    assert qr._safe_write(str(target), writer) is True
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "ok"


def test_safe_write_exception_path(tmp_path):
    target = tmp_path / "fail.txt"

    def writer():
        raise RuntimeError("boom")

    assert qr._safe_write(str(target), writer) is False
    # File must not exist
    assert not target.exists()


def _make_minimal_report():
    return {
        "findings": [
            {"severity": "critical", "rule_id": "R1", "checker": "chk", "message": "m1", "confidence": 0.9},
            {"severity": "major", "rule": "R2", "checker": "chk", "message": "m2", "confidence": "0.5"},
        ],
        "findings_grouped": [
            {"severity": "critical", "rule_id": "R1", "message": "m1", "count": 2, "confidence": 0.9},
            {"severity": "major", "rule": "R2", "message": "m2", "count": 3, "avg_confidence": "0.5"},
        ],
        "metrics": {
            "similarity_thresholds_used": {"critical": 0.8, "major": 0.6}
        },
    }


def test_export_correction_package_creates_structure(tmp_path, monkeypatch):
    app = DummyApp()
    report = _make_minimal_report()
    results = []
    base = tmp_path / "export_base"

    # Disable auto-open to avoid OS calls
    auto_open = False

    # Patch FormatExportManager used inside helper to a dummy that writes CSV/HTML minimally
    class DummyFEM:
        def __init__(self, app_instance=None):
            self.app_instance = app_instance

        def export_data(self, payload, fmt, path):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if fmt == "csv":
                # write a basic CSV with quoting all to check downstream
                with open(p, "w", encoding="utf-8", newline="") as f:
                    w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
                    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                        w.writerow(list(payload[0].keys()))
                        for row in payload:
                            w.writerow([row.get(k, "") for k in payload[0].keys()])
                    else:
                        w.writerow(["ok"])
                return True, None
            else:
                p.write_text("<html></html>", encoding="utf-8")
                return True, None

    monkeypatch.setitem(
        __import__('sys').modules,
        'src.export.format_manager',
        types.SimpleNamespace(FormatExportManager=DummyFEM),
    )

    qr._export_correction_package(app, report, base, auto_open, results)

    pkg_dir = Path(str(base) + "_korrekturpaket")
    assert pkg_dir.exists() and pkg_dir.is_dir()

    # Expected files
    expected = [
        "findings.txt",
        "findings.json",
        "findings.csv",
        "README.txt",
        "meta.json",
    ]
    for name in expected:
        assert (pkg_dir / name).exists()

    # If bilingual present, bilingual CSV should exist (our minimal report lacks bilingual fields -> absent)
    assert not (pkg_dir / "findings_bilingual.csv").exists()

    # Grouped CSV should exist when findings_grouped present
    assert (pkg_dir / "findings_grouped.csv").exists()

    # Verify CSV delimiter & quoting by checking raw text contains double quotes and semicolons
    raw = (pkg_dir / "findings.csv").read_text(encoding="utf-8")
    assert ";" in raw
    assert '"' in raw

    # Results appended with a dir entry
    assert any(getattr(r, 'format', None) == 'dir' for r in results)
