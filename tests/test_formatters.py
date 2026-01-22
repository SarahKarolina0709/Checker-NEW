import unittest

# We import the pure helper directly from the module under test
from quality_gui_components_analysis_results import format_similarity_bucket_label

class MockT:
    def __call__(self, key: str) -> str:
        # trivial identity mapping for snapshot stability
        return key

class TestFormatters(unittest.TestCase):
    def test_format_similarity_bucket_label_basic(self):
        t = MockT()
        label = format_similarity_bucket_label(t, 0.7, 0.8, 12, 0.1234)
        self.assertEqual(label, 'Bereich 70–80%: 12 (12.3%)')

    def test_format_similarity_bucket_label_caps_hi_at_100(self):
        t = MockT()
        label = format_similarity_bucket_label(t, 0.95, 1.2, 3, 1.0)
        self.assertEqual(label, 'Bereich 95–100%: 3 (100.0%)')

    def test_format_similarity_bucket_label_fallback_on_exception(self):
        class BadT:
            def __call__(self, key):
                raise RuntimeError('boom')
        label = format_similarity_bucket_label(BadT(), 0.1, 0.2, 1, 0.5)
        self.assertEqual(label, '10-20%: 1 (50.0%)')

if __name__ == '__main__':
    unittest.main()
