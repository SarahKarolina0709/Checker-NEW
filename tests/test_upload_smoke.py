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

    # Dateien existieren am Ziel
    for item in result["processed_files"]:
        assert os.path.exists(item["destination"])  
