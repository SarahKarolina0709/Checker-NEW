import sys
import os
import tempfile
import datetime

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
SRC_PATH = os.path.join(REPO_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from managers.kunden_manager import KundenManager  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        km = KundenManager(base_dir=tmpdir)
        k = "Kunde_Migr"
        # Ausgangslage: alter Strukturbaum direkt unter Kundenordner
        cust_dir = km.erstelle_kundenstruktur(k)
        for wf in ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"):
            os.makedirs(os.path.join(cust_dir, wf), exist_ok=True)
            # befülle einen Ziel-Ordner simulativ später: erzeugen wir erst Migration-Projekt
        # Lege in alten Ordnern jeweils eine Datei an
        for wf in ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"):
            with open(os.path.join(cust_dir, wf, f"{wf}.txt"), "w", encoding="utf-8") as f:
                f.write("alt")

        # Migration starten
        ok = km.migrate_from_old_structure(k)
        assert ok, "Migration sollte True liefern"

        # Ermittele neuestes Projekt (Migration) und prüfe Inhalte
        newest = km.get_neuestes_projekt(k)
        proj_path = km.get_projekt_pfad(k, newest)
        for wf in ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"):
            dest = os.path.join(proj_path, wf)
            assert os.path.isdir(dest), f"Ziel-Workflow fehlt: {dest}"
            assert os.path.isfile(os.path.join(dest, f"{wf}.txt")), f"Alt-Datei fehlt in {dest}"

        # Alte Wurzelordner sollten nicht mehr existieren
        for wf in ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"):
            assert not os.path.exists(os.path.join(cust_dir, wf)), "Alter Workflow-Ordner nicht verschoben"

    print("Safe migration helper test: OK")


if __name__ == "__main__":
    main()
