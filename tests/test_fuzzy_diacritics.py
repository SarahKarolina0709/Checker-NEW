import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.managers.kunden_manager import KundenManager

BASE = Path("Checker_Projekte_fuzzy_diacritics")


def setup_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def teardown_function(_):
    if BASE.exists():
        shutil.rmtree(BASE)


def test_fuzzy_matches_without_diacritics():
    m = KundenManager(base_dir=str(BASE))
    # Kunden mit Diakritika
    assert m.neuer_kunde("Müller")
    assert m.neuer_kunde("Français Café")

    # Query ohne Diakritika sollte die richtigen Kunden finden
    res1 = m.fuzzy_kundenname_suche("Muller", threshold=70)
    assert res1 == m._sanitize_name("Müller")

    res2 = m.fuzzy_kundenname_suche("Francais Cafe", threshold=70)
    assert res2 == m._sanitize_name("Français Café")

    # customer_exists sollte ebenfalls positiv sein
    exists1, match1, score1 = m.customer_exists("Muller")
    assert exists1 and match1 == m._sanitize_name("Müller") and score1 >= 70

    exists2, match2, score2 = m.customer_exists("Francais Cafe")
    assert exists2 and match2 == m._sanitize_name("Français Café") and score2 >= 70


def test_search_customers_scoring_with_ascii_norm():
    m = KundenManager(base_dir=str(BASE))
    assert m.neuer_kunde("Café International")
    assert m.neuer_kunde("Überprüfung GmbH")

    # Suche ohne Akzente sollte Treffer liefern
    results = m.search_customers("Cafe International", limit=5, min_score=35)
    names = [r["name"] for r in results]
    assert m._sanitize_name("Café International") in names

    # Umlaut -> ae/ue ohne Diakritika
    results2 = m.search_customers("Uberprufung", limit=5, min_score=35)
    names2 = [r["name"] for r in results2]
    assert m._sanitize_name("Überprüfung GmbH") in names2
