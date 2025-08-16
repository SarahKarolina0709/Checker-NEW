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
        k = "Kunde_Test"

        # Verschiedene Projekt-ID-Varianten anlegen
        # 2025-08-10_Projekt_X, 2025-08-10_Projekt_X-01, 2025_08_09_Alt, 20250808_Foo, KeinDatum
        p1, id1 = km.erstelle_projekt_ordner(k, "Projekt_X", datum="2025-08-10")
        p2, id2 = km.erstelle_projekt_ordner(k, "Projekt_X", datum="2025-08-10")  # -> -01
        # manuell anlegen eines speziellen Ordners ohne Helper (simulate legacy)
        os.makedirs(os.path.join(tmpdir, km._sanitize_name(k), "2025_08_09_Alt"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, km._sanitize_name(k), "20250808_Foo"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, km._sanitize_name(k), "KeinDatum"), exist_ok=True)

        projekte = km.liste_kundenprojekte(k)
        print("Projekte sortiert:", projekte)
        # Erwartung: 2025-08-10_Projekt_X-01, 2025-08-10_Projekt_X, 2025_08_09_Alt, 20250808_Foo, KeinDatum
        assert projekte[0].startswith("2025-08-10_Projekt_X-01")
        assert projekte[1].startswith("2025-08-10_Projekt_X") and not projekte[1].endswith("-01")
        # Die nächsten beiden enthalten Datum; 2025_08_09_Alt (2025-08-09) vor 20250808_Foo (2025-08-08)
        assert projekte[2] == "2025_08_09_Alt"
        assert projekte[3] == "20250808_Foo"
        # KeinDatum hat kein erkennbares Datum, daher zuletzt
        assert projekte[-1] == "KeinDatum"

    print("Project listing sort by parsed date: OK")


if __name__ == "__main__":
    main()
