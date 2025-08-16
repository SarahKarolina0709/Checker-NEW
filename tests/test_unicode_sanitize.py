import sys
import os
import tempfile
import unicodedata

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
SRC_PATH = os.path.join(REPO_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from managers.kunden_manager import KundenManager  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        km = KundenManager(base_dir=tmpdir)

        # Precomposed vs. combining
        name_pre = "Müller"  # NFC
        name_comb = "Mu\u0308ller"  # M + combining diaeresis
        assert unicodedata.normalize('NFC', name_comb) == name_pre

        s_pre = km._sanitize_name(name_pre)
        s_comb = km._sanitize_name(name_comb)
        assert s_pre == s_comb, f"NFC-Normalisierung inkonsistent: {s_pre} vs {s_comb}"

        # Problematische Zeichen sollten ersetzt und getrimmt werden
        dirty = ' \/:*?"<>| _Firma__A__ '
        s_dirty = km._sanitize_name(dirty)
        assert s_dirty == 'Firma_A', f"Sanitizing fehlgeschlagen: {s_dirty}"

    print("Unicode NFC + sanitize test: OK")


if __name__ == "__main__":
    main()
