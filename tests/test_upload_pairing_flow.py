from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import quality_gui_pairing_manager as pairing_mod
from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp
from quality_gui_upload_manager import QualityGuiUploadManager
from quality_gui_pairing_manager import QualityGuiPairingManager


def _make_app_stub() -> ProfessionelleUebersetzungsqualitaetsApp:
    app = ProfessionelleUebersetzungsqualitaetsApp.__new__(ProfessionelleUebersetzungsqualitaetsApp)
    app._uploaded_files_backend = {'source': [], 'translation': []}
    app._file_pairs_backend = []
    app._unmatched_files_backend = {'source': [], 'translation': []}
    app.upload_manager = QualityGuiUploadManager()
    app.pairing_manager = QualityGuiPairingManager()
    app.logger = SimpleNamespace(
        info=lambda *args, **kwargs: None,
        debug=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
    )
    app._handle_error = lambda *args, **kwargs: None
    app.show_toast = lambda *args, **kwargs: None
    app.update_status = lambda *args, **kwargs: None
    app._schedule_update_file_counter = lambda *args, **kwargs: None
    app._refresh_file_list_display = lambda *args, **kwargs: None
    app._check_and_show_manual_pairing_option = lambda *args, **kwargs: None
    app._update_file_counter = lambda *args, **kwargs: None
    app._display_file_pairing_results = lambda *args, **kwargs: None
    app._update_pairing_status_display = lambda *args, **kwargs: None
    app._update_ribbon_states = lambda *args, **kwargs: None
    app._accent = lambda *args, **kwargs: "#000000"
    app._t = lambda text: text
    app.event_bus = None
    return app  # type: ignore[return-value]


@pytest.fixture(autouse=True)
def _disable_smart_pairing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pairing_mod, "smart_pair_files", None)


def test_upload_and_remove_flow_syncs_manager_and_pairing(tmp_path: Path) -> None:
    app = _make_app_stub()

    source_file = tmp_path / "angebot_de.txt"
    translation_file = tmp_path / "angebot_en.txt"
    source_file.write_text("Quelle", encoding="utf-8")
    translation_file.write_text("Target", encoding="utf-8")

    app._register_uploaded_files('source', [str(source_file)])
    app._register_uploaded_files('translation', [str(translation_file)])

    assert len(app.upload_manager.list_files('source')) == 1
    assert len(app.upload_manager.list_files('translation')) == 1
    assert app.uploaded_files['source'] == [str(source_file)]

    app._smart_file_pairing()

    assert app.file_pairs
    pair = app.file_pairs[0]
    assert pair['source'] == str(source_file)
    assert pair['translation'] == str(translation_file)
    assert app.unmatched_files['translation'] == []

    app._remove_file('source', 0)

    assert app.upload_manager.list_files('source') == []
    assert app.uploaded_files['source'] == []
    assert app.uploaded_files['translation'] == [str(translation_file)]
    assert str(translation_file) in app.unmatched_files['translation']
