import unittest

# Minimaler Import: wir erwarten dass quality_gui_main_app Klasse verfügbar ist
from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp

class TestSimilarityEncoding(unittest.TestCase):
    def setUp(self):
        self.app = ProfessionelleUebersetzungsqualitaetsApp.__new__(ProfessionelleUebersetzungsqualitaetsApp)
        # Nur die benötigten Attribute initialisieren
        self.app._handle_error = lambda *a, **k: None

    def test_encode_lower_bound(self):
        self.assertEqual(self.app._encode_similarity(-0.5), 0)
        self.assertEqual(self.app._encode_similarity(0.0), 0)

    def test_encode_upper_bound(self):
        self.assertEqual(self.app._encode_similarity(1.0), 1000)
        self.assertEqual(self.app._encode_similarity(5.0), 1000)  # clamp >1

    def test_rounding_behavior(self):
        # 0.1234 * 1000 = 123.4 -> round -> 123
        self.assertEqual(self.app._encode_similarity(0.1234), 123)
        # 0.9995 * 1000 = 999.5 -> round -> 1000
        self.assertEqual(self.app._encode_similarity(0.9995), 1000)

    def test_decode_inverse(self):
        for f in [0.0, 0.1, 0.555, 0.999, 1.0]:
            enc = self.app._encode_similarity(f)
            dec = self.app._decode_similarity(enc)
            self.assertAlmostEqual(dec, min(max(f,0.0),1.0), places=3)

    def test_none_inputs(self):
        self.assertEqual(self.app._encode_similarity(None), 0)
        self.assertEqual(self.app._decode_similarity(None), 0.0)

if __name__ == '__main__':
    unittest.main()
