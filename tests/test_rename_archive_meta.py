import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.managers.kunden_manager import KundenManager

BASE = Path("Checker_Projekte_utils")


def setup_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def teardown_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def test_rename_customer_and_archive_and_meta():
    m = KundenManager(base_dir=str(BASE))

    # Create customer and project
    assert m.neuer_kunde("KundeA")
    proj_path, proj_id = m.erstelle_projekt_ordner("KundeA", "Test")

    # Write meta and read back
    data = {"foo": 1, "bar": "baz"}
    assert m.write_project_meta("KundeA", proj_id, data)
    read = m.read_project_meta("KundeA", proj_id)
    assert read == data

    # Archive project
    assert m.archive_project("KundeA", proj_id)
    # Project should no longer be in main list, but archival folder exists
    projects = m.liste_kundenprojekte("KundeA")
    assert proj_id not in projects
    archiv_dir = Path(m.kunden_ordner("KundeA")) / "__Archiv"
    assert archiv_dir.exists()

    # Rename customer
    assert m.rename_customer("KundeA", "KundeB")
    assert Path(m.kunden_ordner("KundeB")).exists()
    assert not Path(m.kunden_ordner("KundeA")).exists()
