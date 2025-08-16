import multiprocessing as mp
import shutil
import time
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path so `src` can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.managers.kunden_manager import KundenManager

BASE_DIR = Path("Checker_Projekte_test_concurrency")
CUSTOMER = "Kunde_Parallel"
PROJECT = "Gleichzeitig"


def _worker(start_evt, done_q):
    mgr = KundenManager(base_dir=str(BASE_DIR))
    start_evt.wait()
    try:
        pfad, pid = mgr.erstelle_projekt_ordner(CUSTOMER, PROJECT)
        done_q.put((True, pid))
    except Exception as e:
        done_q.put((False, str(e)))


def test_concurrent_suffixes():
    # Clean test dir
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)

    procs = []
    start_evt = mp.Event()
    done_q = mp.Queue()

    for _ in range(4):
        p = mp.Process(target=_worker, args=(start_evt, done_q))
        p.start()
        procs.append(p)

    # Fire all workers at the same time
    start_evt.set()

    results = []
    for _ in procs:
        ok, val = done_q.get(timeout=30)
        assert ok, f"Worker failed: {val}"
        results.append(val)

    for p in procs:
        p.join(timeout=30)

    # Ensure unique project ids created
    assert len(results) == 4
    assert len(set(results)) == 4, f"Duplicate project ids: {results}"

    # Validate folder existence
    mgr = KundenManager(base_dir=str(BASE_DIR))
    projects = mgr.liste_kundenprojekte(CUSTOMER)
    assert len(projects) == 4, projects

    # Clean up
    shutil.rmtree(BASE_DIR)
