import unittest
import math

from quality_gui_components_analysis_results import _decide_score_color


class DummyCfg:
    def __init__(self, limits=None, raise_on_get=False):
        self._limits = limits
        self._raise = raise_on_get

    def get(self, key, default=None):
        if self._raise:
            raise RuntimeError("cfg get failed")
        return self._limits if self._limits is not None else default


class DummyApp:
    def __init__(self, cfg=None):
        # Mimic app with _config_manager
        self._config_manager = cfg


class TestDecideScoreColor(unittest.TestCase):
    def test_default_limits_boundaries(self):
        app = DummyApp(cfg=DummyCfg())  # default limits path
        # Equal to good (85) -> success
        self.assertEqual(_decide_score_color(app, 85), 'success')
        # Equal to ok (70) -> warning
        self.assertEqual(_decide_score_color(app, 70), 'warning')
        # Below ok -> error
        self.assertEqual(_decide_score_color(app, 69.9), 'error')

    def test_none_returns_text_primary(self):
        app = DummyApp(cfg=DummyCfg())
        self.assertEqual(_decide_score_color(app, None), 'text_primary')

    def test_nan_returns_error(self):
        app = DummyApp(cfg=DummyCfg())
        self.assertEqual(_decide_score_color(app, float('nan')), 'error')

    def test_custom_limits_respected(self):
        custom = { 'good': 90, 'ok': 75 }
        app = DummyApp(cfg=DummyCfg(limits=custom))
        self.assertEqual(_decide_score_color(app, 90), 'success')
        self.assertEqual(_decide_score_color(app, 80), 'warning')
        self.assertEqual(_decide_score_color(app, 70), 'error')

    def test_config_exception_falls_back_to_defaults(self):
        app = DummyApp(cfg=DummyCfg(raise_on_get=True))
        # Should use defaults 85/70
        self.assertEqual(_decide_score_color(app, 85), 'success')
        self.assertEqual(_decide_score_color(app, 70), 'warning')
        self.assertEqual(_decide_score_color(app, 60), 'error')


if __name__ == '__main__':
    unittest.main()
