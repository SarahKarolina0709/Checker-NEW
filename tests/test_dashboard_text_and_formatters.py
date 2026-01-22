import types
import builtins

# We import the functions from the module under test
from quality_gui_components_analysis_dashboard import TEXT, _fmt_percent, _fmt_duration, _to_yes_no

class DummyApp:
    def __init__(self):
        self._t = lambda s: s  # identity translation for test

def test_text_keys_present():
    required = [
        'dashboard_title','issues_found','files_processed','analysis_time','severity_mix',
        'no_analysis_yet','phase_prefix','overall_quality_rating','issues_detected_desc',
        'files_processed_desc','processing_time_desc','severity_distribution_desc','cta_analyze_now',
        'timeouts_label','aborted_label','yes','no'
    ]
    for k in required:
        assert k in TEXT and isinstance(TEXT[k], str) and TEXT[k]


def test_fmt_percent():
    assert _fmt_percent(None) == '-'
    assert _fmt_percent(0) == '0%'
    assert _fmt_percent(0.25) == '25%'
    assert _fmt_percent(1) == '100%'
    assert _fmt_percent(42) == '42%'


def test_fmt_duration():
    assert _fmt_duration(None) == '-'
    assert _fmt_duration(0) == '-'
    assert _fmt_duration(0.009) == '-'
    assert _fmt_duration(0.01) == '0.0s'
    assert _fmt_duration(1.234) == '1.2s'


def test_to_yes_no():
    app = DummyApp()
    assert _to_yes_no(app, True) == TEXT['yes']
    assert _to_yes_no(app, False) == TEXT['no']
