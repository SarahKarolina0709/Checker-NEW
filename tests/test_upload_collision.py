import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from managers.kunden_manager import KundenManager
from managers.upload_manager import UploadManager

class DummyApp:
    def __init__(self):
        self.enhanced_ui = None
        self.logger = None
        self.root = None

def test_upload_same_filename_collision(tmp_path):
    base_dir = tmp_path / "Checker_Projekte"
    km = KundenManager(base_dir=str(base_dir))
    um = UploadManager(DummyApp(), km)

    # Zwei Dateien mit demselben Namen in unterschiedlichen Ordnern erzeugen
    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d1.mkdir()
    d2.mkdir()
    f1 = d1 / "same_name.docx"
    f2 = d2 / "same_name.docx"
    f1.write_text("content1", encoding="utf-8")
    f2.write_text("content2", encoding="utf-8")

    # Simuliere Dateiauswahl
    um.uploaded_files = [str(f1), str(f2)]

    # Verarbeite Uploads
    result = um.process_files_with_customer("CollisionTest", workflow="Ausgangstexte")

    assert result["success"], f"Upload fehlgeschlagen: {result}"
    assert result["success_count"] == 2

    processed = result.get("processed_files", [])
    assert len(processed) == 2, f"Erwarte 2 processed_files Einträge, erhalten: {processed}"
    destinations = []
    for entry in processed:
        if isinstance(entry, dict):
            p = (entry.get("destination") or entry.get("path") or entry.get("target") 
                 or entry.get("target_path") or entry.get("relative_path"))
            if p:
                destinations.append(p)
        elif isinstance(entry, (str, bytes)):
            destinations.append(str(entry))
    assert len(destinations) == 2, f"Konnte keine Zielpfade extrahieren: {processed}"
    assert all(os.path.exists(p) for p in destinations), f"Nicht alle Ziele existieren: {destinations}"

    # Basenames müssen sich unterscheiden: same_name.docx und same_name-01.docx
    basenames = [os.path.basename(p) for p in destinations]
    assert len(set(basenames)) == 2, f"Dateikollision wurde nicht aufgelöst: {basenames}"
    assert any(name == "same_name.docx" for name in basenames)
    assert any(name == "same_name-01.docx" for name in basenames)
