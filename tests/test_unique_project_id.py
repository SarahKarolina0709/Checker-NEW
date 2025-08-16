import sys
import os
import tempfile
import datetime

# Pfade für Imports setzen
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
SRC_PATH = os.path.join(REPO_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from managers.kunden_manager import KundenManager  # noqa: E402


def main():
    today = datetime.date.today().isoformat()
    with tempfile.TemporaryDirectory() as tmpdir:
        km = KundenManager(base_dir=tmpdir)
        kundenname = "Kunde_Mueller"
        projektname = "Website_Uebersetzung"

        p1_path, p1_id = km.erstelle_projekt_ordner(kundenname, projektname, today)
        p2_path, p2_id = km.erstelle_projekt_ordner(kundenname, projektname, today)
        p3_path, p3_id = km.erstelle_projekt_ordner(kundenname, projektname, today)

        base_id = f"{today}_{km._sanitize_name(projektname).replace(' ', '_')}"

        assert p1_id == base_id, f"Erste ID unerwartet: {p1_id} != {base_id}"
        assert p2_id == f"{base_id}-01", f"Zweite ID sollte Suffix -01 haben, bekam {p2_id}"
        assert p3_id == f"{base_id}-02", f"Dritte ID sollte Suffix -02 haben, bekam {p3_id}"

        # Ordner existieren
        assert os.path.isdir(p1_path), f"Pfad existiert nicht: {p1_path}"
        assert os.path.isdir(p2_path), f"Pfad existiert nicht: {p2_path}"
        assert os.path.isdir(p3_path), f"Pfad existiert nicht: {p3_path}"

        # Workflows existieren in jedem Projekt
        for p in (p1_path, p2_path, p3_path):
            for wf in ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"):
                assert os.path.isdir(os.path.join(p, wf)), f"Workflow fehlt: {p} / {wf}"

    print("Unique Project ID Test: OK")


if __name__ == "__main__":
    main()
