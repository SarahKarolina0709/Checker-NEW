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

def test_upload_smoke(tmp_path):
    base_dir = tmp_path / "Checker_Projekte"
    km = KundenManager(base_dir=str(base_dir))
    um = UploadManager(DummyApp(), km)

    # Erzeuge zwei kleine Testdateien
    f1 = tmp_path / "Angebot_Mueller_001.pdf"
    f1.write_text("dummy", encoding="utf-8")
    f2 = tmp_path / "Pruefung_Schmidt_ABC.docx"
    f2.write_text("dummy2", encoding="utf-8")

    # Simuliere Dateiauswahl
    um.uploaded_files = [str(f1), str(f2)]

    # Prozessiere zu Kunde "Müller" in Workflow Ausgangstexte
    result = um.process_files_with_customer("Müller", workflow="Ausgangstexte")

    assert result["success"]
    assert result["success_count"] == 2
    assert result["customer"] in ("Müller", "Mueller", km._sanitize_name("Müller"))

    # Dateien existieren am Ziel (robuste Struktur-Auswertung)
    processed = result.get("processed_files", [])
    assert len(processed) == 2, f"Erwarte 2 processed_files Einträge, erhalten: {processed}"
    extracted = []
    for entry in processed:
        if isinstance(entry, dict):
            p = (entry.get("destination") or entry.get("path") or entry.get("target") 
                 or entry.get("target_path") or entry.get("relative_path"))
            if p:
                extracted.append(p)
        elif isinstance(entry, (str, bytes)):
            extracted.append(str(entry))
    assert len(extracted) == 2, f"Konnte keine Pfade extrahieren: {processed}"
    for p in extracted:
        assert os.path.exists(p), f"Ziel fehlt: {p}"
