# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.severity (Score-Berechnung + UI-Helfer)."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui_app import severity


@dataclass
class _F:
    """Minimaler Finding-Stub fuer Score-Tests."""
    severity: Any = 'info'
    meta: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# normalize()
# ---------------------------------------------------------------------------
class TestNormalize:
    def test_canonical_values_pass_through(self):
        assert severity.normalize('critical') == 'critical'
        assert severity.normalize('major') == 'major'
        assert severity.normalize('minor') == 'minor'
        assert severity.normalize('info') == 'info'

    def test_german_aliases(self):
        assert severity.normalize('kritisch') == 'critical'
        assert severity.normalize('wichtig') == 'major'
        assert severity.normalize('leicht') == 'minor'
        assert severity.normalize('hinweis') == 'info'

    def test_case_insensitive(self):
        assert severity.normalize('CRITICAL') == 'critical'
        assert severity.normalize('Kritisch') == 'critical'

    def test_none_falls_back_to_info(self):
        assert severity.normalize(None) == 'info'

    def test_empty_string_falls_back_to_info(self):
        assert severity.normalize('') == 'info'
        assert severity.normalize('   ') == 'info'

    def test_unknown_value_falls_back_to_info(self):
        assert severity.normalize('whatever') == 'info'

    def test_non_string_input(self):
        assert severity.normalize(123) == 'info'


# ---------------------------------------------------------------------------
# label / color / border
# ---------------------------------------------------------------------------
class TestUIHelpers:
    def test_labels(self):
        assert severity.label('critical') == 'Kritisch'
        assert severity.label('major') == 'Wichtig'
        assert severity.label('minor') == 'Hinweis'
        assert severity.label('info') == 'Hinweis'

    def test_label_german_aliases(self):
        assert severity.label('kritisch') == 'Kritisch'
        assert severity.label('wichtig') == 'Wichtig'

    def test_label_none_safe(self):
        assert severity.label(None) == 'Hinweis'

    def test_colors_distinct(self):
        cols = {severity.color(s) for s in ('critical', 'major', 'minor')}
        assert len(cols) >= 2  # critical/major distinkt; minor=info ist OK
        assert severity.color('critical').startswith('#')

    def test_border_uses_color(self):
        b = severity.border('critical')
        assert b.startswith('border-left:4px solid ')
        assert severity.color('critical') in b

    def test_border_none_safe(self):
        # Darf nicht crashen
        assert 'border-left' in severity.border(None)

    def test_icons_per_severity(self):
        assert severity.icon('critical') == 'error'
        assert severity.icon('major') == 'warning'
        assert severity.icon('minor') == 'info'
        assert severity.icon('info') == 'info'

    def test_icon_german_aliases(self):
        assert severity.icon('kritisch') == 'error'
        assert severity.icon('wichtig') == 'warning'

    def test_icon_none_safe(self):
        # None/Unbekannt -> 'info' (kein Crash)
        assert severity.icon(None) == 'info'
        assert severity.icon('whatever') == 'info'

    def test_severity_icon_alias(self):
        assert severity.severity_icon is severity.icon

    def test_css_color_returns_tokens(self):
        assert severity.css_color('critical') == 'var(--sev-critical)'
        assert severity.css_color('major') == 'var(--sev-major)'
        assert severity.css_color('minor') == 'var(--sev-minor)'
        assert severity.css_color('info') == 'var(--sev-minor)'

    def test_css_color_none_safe(self):
        assert severity.css_color(None) == 'var(--sev-minor)'
        assert severity.severity_css_color is severity.css_color

    def test_score_color_bands(self):
        assert severity.score_color(100) == 'var(--success)'
        assert severity.score_color(80) == 'var(--success)'
        assert severity.score_color(79) == 'var(--warning)'
        assert severity.score_color(50) == 'var(--warning)'
        assert severity.score_color(49) == 'var(--error)'
        assert severity.score_color(0) == 'var(--error)'

    def test_score_color_invalid_safe(self):
        assert severity.score_color(None) == 'var(--text-light)'
        assert severity.score_color('x') == 'var(--text-light)'


# ---------------------------------------------------------------------------
# compute_score
# ---------------------------------------------------------------------------
class TestComputeScore:
    def test_no_issues_full_score(self):
        assert severity.compute_score([]) == 100

    def test_only_hint_only_full_score(self):
        # Hint-Only-Findings duerfen Score nicht senken
        items = [_F('minor', {'hint_only': True}), _F('info', {'hint_only': True})]
        assert severity.compute_score(items) == 100

    def test_critical_costs_8(self):
        assert severity.compute_score([_F('critical')]) == 100 - 8

    def test_major_costs_3(self):
        assert severity.compute_score([_F('major')]) == 100 - 3

    def test_minor_costs_1(self):
        assert severity.compute_score([_F('minor')]) == 100 - 1

    def test_info_treated_as_minor(self):
        assert severity.compute_score([_F('info')]) == 100 - 1

    def test_unknown_severity_treated_as_info(self):
        assert severity.compute_score([_F('whatever')]) == 100 - 1

    def test_none_severity_safe(self):
        # Bug 52/54: None.lower() crash schuetzen
        assert severity.compute_score([_F(None)]) == 100 - 1

    def test_score_clamped_at_99_when_findings_exist(self):
        # Selbst minimaler Finding muss <100 ergeben
        score = severity.compute_score([_F('minor')])
        assert score < 100

    def test_score_clamped_at_5_lower_bound(self):
        # 100 critical = riesige Strafe, aber Score bleibt >=5 wenn Findings da sind
        items = [_F('critical')] * 100
        assert severity.compute_score(items) == 5

    def test_score_zero_only_when_empty(self):
        # 100 - 8*100 = -700 -> clamp auf 5 (nicht 0!) wenn Findings da
        items = [_F('critical')] * 200
        assert severity.compute_score(items) >= 5

    def test_mixed_severities(self):
        items = [_F('critical'), _F('major'), _F('minor'), _F('minor')]
        # 100 - 8 - 3 - 1 - 1 = 87
        assert severity.compute_score(items) == 87

    def test_german_aliases_in_score(self):
        items = [_F('kritisch'), _F('wichtig'), _F('leicht')]
        assert severity.compute_score(items) == 100 - 8 - 3 - 1
