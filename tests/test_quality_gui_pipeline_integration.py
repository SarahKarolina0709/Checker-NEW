from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import quality_gui_main_app as qg_main
from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp


class DummySettings:
    def __init__(self, values: Dict[str, Any] | None = None) -> None:
        self._values: Dict[str, Any] = values or {}

    def get(self, key_path: str, default: Any = None) -> Any:
        return self._values.get(key_path, default)

    def set(self, key_path: str, value: Any) -> None:
        self._values[key_path] = value

    def is_enabled(self, key_path: str, default: bool = True) -> bool:
        return bool(self._values.get(key_path, default))


def _make_app(settings: DummySettings | None = None, semantic_enabled: bool = True) -> ProfessionelleUebersetzungsqualitaetsApp:
    app = ProfessionelleUebersetzungsqualitaetsApp.__new__(ProfessionelleUebersetzungsqualitaetsApp)
    app.settings_service = settings or DummySettings()
    app.var_phase3_semantic = SimpleNamespace(get=lambda: semantic_enabled)
    app.event_bus = None
    app.quality_vars = {}
    app.glossary_file_path = None
    app.logger = SimpleNamespace(debug=lambda *args, **kwargs: None)
    app._debug_silent = lambda *args, **kwargs: None
    app._log_event = lambda *args, **kwargs: None
    app._show_toast = lambda *args, **kwargs: None
    app.get_color = lambda *args, **kwargs: "#FFFFFF"
    app.get_spacing = lambda *args, **kwargs: 0
    app.get_component_value = lambda *args, **kwargs: 0
    app._t = lambda text: text
    return app  # type: ignore[return-value]


def _write_pair(tmp_path, source_text: str, target_text: str, *, suffix: str = "", meta: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    src_file = tmp_path / f"source{suffix}.txt"
    trg_file = tmp_path / f"target{suffix}.txt"
    src_file.write_text(source_text, encoding="utf-8")
    trg_file.write_text(target_text, encoding="utf-8")
    pair: Dict[str, Any] = {"source": str(src_file), "translation": str(trg_file)}
    if meta is not None:
        pair["meta"] = meta
    return [pair]


def test_pipeline_emits_phase_issues(tmp_path) -> None:
    pairs = _write_pair(
        tmp_path,
        "Hallo {name}, bitte zahle 123 €.",
        "Hello there, please pay soon."
    )
    app = _make_app()

    result = app._run_analysis_pipeline(pairs, "default")

    codes_phase1 = {issue["code"] for issue in result["issues_phase1"]}
    codes_phase2 = {issue["code"] for issue in result["issues_phase2"]}

    assert "PLACEHOLDER_MISSING" in codes_phase1
    assert "NUMBER_MISSING" in codes_phase2
    assert "phase_issue_counts" in result and result["phase_issue_counts"]["phase1"] >= 1


def test_pipeline_respects_phase_toggle(tmp_path) -> None:
    settings = DummySettings({"analysis.phases.phase1.enabled": False})
    pairs = _write_pair(
        tmp_path,
        "Hallo {name}, der Preis beträgt 999 €.",
        "Hallo {name}, der Preis beträgt 999 €."
    )
    app = _make_app(settings=settings)

    result = app._run_analysis_pipeline(pairs, "default")

    assert result["issues_phase1"] == []
    assert result["phase_issue_counts"]["phase1"] == 0


def test_spellcheck_flags_typo(tmp_path, monkeypatch) -> None:
    settings = DummySettings({
        "analysis.phases.phase3.spellcheck": {
            "enabled": True,
            "target_language": "en",
            "custom_dictionary": []
        }
    })
    pairs = _write_pair(
        tmp_path,
        "Hello world",
        "Helo wurld"
    )
    app = _make_app(settings=settings)

    def fake_phase3_checks(_segments, **_kwargs):
        return [
            {
                "code": "SPELLING_ERROR",
                "severity": "major",
                "category": "grammar",
                "message": "Spelling issue",
                "source": "Hello world",
                "target": "Helo wurld",
                "meta": {"checker": "hunspell"}
            }
        ]

    monkeypatch.setattr(qg_main, "run_phase3_checks", fake_phase3_checks)

    result = app._run_analysis_pipeline(pairs, "default")

    codes_phase3 = {issue["code"] for issue in result["issues_phase3"]}
    assert "SPELLING_ERROR" in codes_phase3
    status = result["summary"]["grammar_status"]
    assert status["used"] == ["hunspell"]
    assert status["force"] is False


def test_locale_date_mismatch_detected(tmp_path) -> None:
    settings = DummySettings({
        "analysis.validation.locale": {
            "enabled": True,
            "date_format": "DD.MM.YYYY",
            "allow_iso_dates": False,
            "decimal_separator": ",",
            "thousand_separator": "."
        }
    })
    pairs = _write_pair(
        tmp_path,
        "Delivery on 2025-10-01",
        "Lieferung am 2025-10-01"
    )
    app = _make_app(settings=settings)

    result = app._run_analysis_pipeline(pairs, "default")

    codes_phase2 = {issue["code"] for issue in result["issues_phase2"]}
    assert "LOCALE_DATE_MISMATCH" in codes_phase2


def test_blacklist_terms_raise_issue(tmp_path) -> None:
    settings = DummySettings({
        "analysis.validation.blacklist": {
            "enabled": True,
            "terms": ["beta"],
            "severity": "major",
            "match_target": True,
            "match_source": False
        }
    })
    pairs = _write_pair(
        tmp_path,
        "Status",
        "Diese Version ist Beta"
    )
    app = _make_app(settings=settings)

    result = app._run_analysis_pipeline(pairs, "default")

    codes_phase2 = {issue["code"] for issue in result["issues_phase2"]}
    assert "BLACKLIST_TERM" in codes_phase2


def test_list_structure_mismatch(tmp_path) -> None:
    settings = DummySettings({
        "analysis.validation.lists": {
            "enabled": True,
            "require_matching_markers": True,
            "enforce_sequence": True,
            "ignore_single_items": False
        }
    })
    pairs = _write_pair(
        tmp_path,
        "1. Schritt\n2. Schritt",
        "1. Schritt\n3. Schritt"
    )
    app = _make_app(settings=settings)

    result = app._run_analysis_pipeline(pairs, "default")

    codes_phase2 = {issue["code"] for issue in result["issues_phase2"]}
    assert "LIST_STRUCTURE_ORDER" in codes_phase2


def test_metadata_constraints_enforced(tmp_path) -> None:
    settings = DummySettings({
        "analysis.validation.metadata": {
            "enabled": True,
            "allowed_attributes": ["id", "state"],
            "required_attributes": ["id"],
            "protected_values": {"state": ["translated", "final"]}
        }
    })
    pair = _write_pair(
        tmp_path,
        "Text",
        "Text",
        meta={"id": "S1", "state": "draft"}
    )
    app = _make_app(settings=settings)

    result = app._run_analysis_pipeline(pair, "default")

    codes_phase2 = {issue["code"] for issue in result["issues_phase2"]}
    assert "METADATA_PROTECTED_VALUE" in codes_phase2


def test_summary_reports_grammar_metadata_when_force_enabled(tmp_path, monkeypatch) -> None:
    settings = DummySettings({
        "analysis.phases.phase3.spellcheck": {
            "enabled": True,
            "force_grammar": True
        }
    })
    pairs = _write_pair(
        tmp_path,
        "Sentence",
        "Sentence"
    )
    app = _make_app(settings=settings)

    def fake_phase3_checks(_segments, **_kwargs):
        return [
            {
                "code": "GRAMMAR_LT",
                "severity": "major",
                "category": "grammar",
                "message": "Issue",
                "source": "",
                "target": "",
                "meta": {"checker": "languagetool"}
            },
            {
                "code": "GRAMMAR_HS",
                "severity": "minor",
                "category": "grammar",
                "message": "Issue",
                "source": "",
                "target": "",
                "meta": {"checker": "hunspell"}
            }
        ]

    monkeypatch.setattr(qg_main, "run_phase3_checks", fake_phase3_checks)

    result = app._run_analysis_pipeline(pairs, "default")
    summary = result["summary"]

    assert summary["grammar_force_override"] is True
    assert summary["grammar_checkers_used"] == ["hunspell", "languagetool"]
    status = summary["grammar_status"]
    assert status["force"] is True
    assert status["used"] == ["hunspell", "languagetool"]
    assert status["disabled"] == []


def test_summary_marks_spellcheck_as_disabled(tmp_path, monkeypatch) -> None:
    settings = DummySettings({
        "analysis.phases.phase3.spellcheck": {
            "enabled": False,
            "force_grammar": False
        }
    })
    pairs = _write_pair(
        tmp_path,
        "Quelle",
        "Ziel"
    )
    app = _make_app(settings=settings)

    monkeypatch.setattr(qg_main, "run_phase3_checks", lambda *_args, **_kwargs: [])

    result = app._run_analysis_pipeline(pairs, "default")
    summary = result["summary"]

    assert "Spellcheck deaktiviert" in summary["grammar_checkers_disabled"]
    assert "grammar_force_override" not in summary
    status = summary["grammar_status"]
    assert "Spellcheck deaktiviert" in status["disabled"]
    assert status["force"] is False
    assert status["used"] == []
