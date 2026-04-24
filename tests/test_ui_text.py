"""UI-Text-Smoke-Test für die Quality GUI.

Prüft auf korrekte deutsche Labels und fehlende Encoding-Artefakte.
Läuft ohne laufende GUI – benutzt eine Mock-App-Instanz.
"""
import sys
import types


def _make_mock_app(title="Übersetzungsqualitäts-Framework - Professional Edition"):
    """Minimale Stub-App für den Text-Test (kein Tkinter nötig)."""
    app = types.SimpleNamespace()
    app._root_title = title
    app._widget_texts: list[str] = []

    class _MockRoot:
        def title(self_inner):
            return app._root_title
        def winfo_children(self_inner):
            return []

    app.root = _MockRoot()
    app.logger = __import__('logging').getLogger('test_ui_text')
    return app


def run_ui_text_checks(app) -> list[str]:
    """Führt UI-Text-Checks durch; gibt Liste gefundener Probleme zurück (leer = OK)."""
    issues: list[str] = []
    critical_tokens = [
        "Übersetzungsqualitäts-Framework", "Qualitätsanalyse",
        "Dateipaar", "Dateien", "Manuelles Pairing",
        "Projekt", "Kriterien",
    ]

    # Fenster-Titel
    try:
        title = app.root.title() if app.root else ""
        if "??" in title:
            issues.append("Titel enthält Encoding-Artefakt")
        if "Framework" not in title:
            issues.append("Framework im Titel fehlt")
    except Exception:
        issues.append("Fenstertitel nicht prüfbar")

    # Widget-Texte (flach, wenn vorhanden)
    try:
        sample_texts: list[str] = []
        if app.root:
            for child in app.root.winfo_children():
                try:
                    txt = getattr(child, 'cget', lambda _: '')('text')
                    if txt:
                        sample_texts.append(txt)
                except Exception:
                    pass
        concat = " | ".join(sample_texts)
        if "??" in concat:
            issues.append("Widgets enthalten Encoding-Artefakte")
        for token in critical_tokens:
            if token not in concat and token not in title:
                issues.append(f"Fehlender Begriff: {token}")
    except Exception as e:
        issues.append(f"Widget-Scan Fehler: {e}")

    if not issues:
        app.logger.info("UI Text Test: BESTANDEN")
    else:
        app.logger.warning("UI Text Test: Probleme: %s", issues)
    return issues


# ── pytest-kompatible Tests ──────────────────────────────────────────────────

def test_title_contains_framework():
    app = _make_mock_app()
    issues = run_ui_text_checks(app)
    framework_issues = [i for i in issues if "Framework" in i]
    assert not framework_issues, framework_issues


def test_title_no_encoding_artifacts():
    app = _make_mock_app()
    issues = run_ui_text_checks(app)
    enc_issues = [i for i in issues if "Encoding" in i or "Artefakt" in i]
    assert not enc_issues, enc_issues


def test_broken_title_detected():
    app = _make_mock_app(title="??broken??")
    issues = run_ui_text_checks(app)
    assert any("Encoding" in i or "Framework" in i for i in issues)
