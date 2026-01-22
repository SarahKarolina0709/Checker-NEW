import unittest

from services.analysis_state import AnalysisState


class DummyEventBus:
    def __init__(self):
        self.events = []

    def publish(self, evt, payload):
        self.events.append((evt, payload))


class InMemorySettings:
    """Minimaler SettingsService-Ersatz mit get/set und key-paths."""
    def __init__(self):
        self.store = {}

    def get(self, key, default=None):
        return self.store.get(key, default)

    def set(self, key, value):
        self.store[key] = value


class TestAnalysisState(unittest.TestCase):
    def test_tabs_roundtrip_and_events(self):
        bus = DummyEventBus()
        st = AnalysisState(settings_service=InMemorySettings(), event_bus=bus)
        # Default
        self.assertEqual(st.get_last_tab(), "overview")
        # Set and read
        st.set_last_tab("findings")
        self.assertEqual(st.get_last_tab(), "findings")
        # Event emitted
        self.assertTrue(any(e[0] == "analysis.state.changed" and e[1].get("key") == "last_tab" for e in bus.events))

    def test_findings_state_roundtrip_and_patch_merge(self):
        bus = DummyEventBus()
        st = AnalysisState(settings_service=InMemorySettings(), event_bus=bus)
        # Defaults
        cur = st.get_findings_state()
        self.assertEqual(cur["severity"], "ALL")
        self.assertEqual(cur["sort"], "severity")
        self.assertEqual(cur["sort_dir"], "asc")
        self.assertEqual(cur["grouped"], False)
        # Update
        new_state = st.update_findings_state({
            "severity": "critical",
            "checker": "grammar",
            "sort": "rule",
            "sort_dir": "desc",
            "query": "zahl",
            "grouped": True,
        })
        self.assertEqual(new_state["severity"], "critical")
        self.assertEqual(new_state["checker"], "grammar")
        self.assertEqual(new_state["sort"], "rule")
        self.assertEqual(new_state["sort_dir"], "desc")
        self.assertEqual(new_state["query"], "zahl")
        self.assertEqual(new_state["grouped"], True)
        # Persisted
        again = st.get_findings_state()
        self.assertEqual(again, new_state)
        # Event payload contains patch
        self.assertTrue(any(e[0] == "analysis.state.changed" and e[1].get("scope") == "findings" for e in bus.events))

    def test_thresholds_bounds_and_persistence(self):
        bus = DummyEventBus()
        st = AnalysisState(settings_service=InMemorySettings(), event_bus=bus)
        # Defaults
        t = st.get_thresholds()
        self.assertIn("risk_high", t)
        self.assertIn("completeness_low", t)
        self.assertIn("similarity_low", t)
        # Set and clamp
        t2 = st.set_thresholds(risk_high=150, completeness_low=-1, similarity_low=0.5)
        self.assertEqual(t2["risk_high"], 100)
        self.assertEqual(t2["completeness_low"], 0.0)
        self.assertEqual(t2["similarity_low"], 0.5)
        # Persisted
        t3 = st.get_thresholds()
        self.assertEqual(t3, t2)
        # Event emitted
        self.assertTrue(any(e[0] == "analysis.state.changed" and e[1].get("scope") == "thresholds" for e in bus.events))


if __name__ == "__main__":
    unittest.main()
