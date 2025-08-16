import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.managers.kunden_manager import KundenManager

BASE = Path("Checker_Projekte_reserved_case")


def setup_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def teardown_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def test_windows_reserved_prefixing():
    m = KundenManager(base_dir=str(BASE))
    # Try creating a reserved name ("CON")
    ok = m.neuer_kunde("CON")
    assert ok
    # Should be prefixed with underscore and exist
    customers = m.alle_kunden()
    assert customers == ["_CON"] or "_CON" in customers


def test_case_insensitive_duplicate_blocks_creation():
    m = KundenManager(base_dir=str(BASE))
    assert m.neuer_kunde("Alpha")
    # On case-sensitive FS we still block duplicate differing only by case
    assert not m.neuer_kunde("alpha")
    # Only one physical folder
    customers = m.alle_kunden()
    assert len(customers) == 1
