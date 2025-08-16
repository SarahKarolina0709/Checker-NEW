import os
import sys
import tempfile
import shutil
import types

# Ensure repo and src are importable
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Patch tkinter dialogs to avoid UI interaction
import tkinter
from tkinter import messagebox, simpledialog, filedialog

# Force non-interactive behavior: always 'Yes' and defaults
messagebox.askyesno = lambda *a, **k: True
messagebox.showinfo = lambda *a, **k: None
messagebox.showwarning = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: None
simpledialog.askstring = lambda *a, **k: "Ausgangstexte" if "Workflow" in (a[0] if a else "") else "Kunde_Test"
filedialog.askopenfilenames = lambda *a, **k: []

# Minimal app stub to satisfy UploadManager expectations
class AppStub:
    def __init__(self):
        self.enhanced_ui = types.SimpleNamespace(show_toast=lambda *a, **k: None)
        self.root = None
        self.logger = None


def run_smoketest():
    from src.managers.kunden_manager import KundenManager
    from src.managers.upload_manager import UploadManager

    base_tmp = tempfile.mkdtemp(prefix="checker_test_")
    try:
        km = KundenManager(base_dir=os.path.join(base_tmp, "Checker_Projekte"))

        # Vorbereitung: existierender Kunde für Fuzzy-Test
        existing_customer = "Kunde_Mueller"
        km.erstelle_kundenstruktur(existing_customer)

        # UploadManager initialisieren
        app = AppStub()
        um = UploadManager(app, km)

        # Erzeuge temporäre Dateien (multi-upload)
        tmp_dir = os.path.join(base_tmp, "input")
        os.makedirs(tmp_dir, exist_ok=True)
        files = []
        for name in ["Mueller_Angebot_001.pdf", "report_review.docx", "data.xlsx"]:
            p = os.path.join(tmp_dir, name)
            with open(p, "wb") as f:
                f.write(b"test")
            files.append(p)

        # Simuliere vorausgewählte Dateien
        um.uploaded_files.extend(files)

        # 1) Ähnlicher Kunde: sollte 'Kunde_Mueller' erkennen
        suggestions = um.get_customer_suggestions()
        assert any("Mueller" in s.get("suggestion", "") for s in suggestions), "Keine Kundenvorschläge erkannt"

        # 2) Prozessiere Dateien mit Fuzzy-Name (z.B. 'Kunde Muller')
        stats = um.process_files_with_customer("Kunde Muller", workflow="Ausgangstexte")
        assert stats.get("success"), f"Upload fehlgeschlagen: {stats}"
        assert stats.get("success_count", 0) == len(files), "Nicht alle Dateien verarbeitet"

        # 3) Verifiziere Zielstruktur
        latest_project = km.get_neuestes_projekt(stats["customer"]) or ""
        target = km.get_projekt_workflow_ordner(stats["customer"], latest_project, "Ausgangstexte")
        date_folder = os.listdir(target)[0]
        for f in files:
            assert os.path.exists(os.path.join(target, date_folder, os.path.basename(f))), "Zieldatei fehlt"

        print("UI-Smoketest OK: Ähnlicher Kunde + Multi-Upload funktionieren.")
        return 0
    finally:
        shutil.rmtree(base_tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_smoketest())
