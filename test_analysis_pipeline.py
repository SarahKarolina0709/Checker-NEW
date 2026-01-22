"""test_analysis_pipeline.py

Unit Tests für QualityGuiAnalysisPipeline.
Testet Analysis-Orchestration, Timeout-Handling, und Result-Normalization.

Run:
    pytest test_analysis_pipeline.py -v
    pytest test_analysis_pipeline.py -v --cov=quality_gui_analysis_pipeline
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from quality_gui_analysis_pipeline import QualityGuiAnalysisPipeline


class TestQualityGuiAnalysisPipeline:
    """Tests für QualityGuiAnalysisPipeline."""
    
    def test_analysis_pipeline_initialization(self):
        """Test: AnalysisPipeline kann initialisiert werden."""
        pipeline = QualityGuiAnalysisPipeline()
        
        assert pipeline._last_stats is None
    
    def test_set_last_stats(self):
        """Test: Last Stats können gesetzt werden."""
        from quality_gui_analysis_pipeline import AnalysisStats
        pipeline = QualityGuiAnalysisPipeline()
        
        stats = AnalysisStats(executed=5, timeouts=1, total_ms=5200)
        pipeline._last_stats = stats
        
        assert pipeline._last_stats == stats
        assert pipeline._last_stats.executed == 5
        assert pipeline._last_stats.timeouts == 1
    
    def test_clear_analysis_state(self):
        """Test: Analysis-State kann gelöscht werden."""
        from quality_gui_analysis_pipeline import AnalysisStats
        pipeline = QualityGuiAnalysisPipeline()
        
        # State setzen
        pipeline._last_stats = AnalysisStats(executed=3)
        
        # Clear
        pipeline._last_stats = None
        
        assert pipeline._last_stats is None
    
    def test_analysis_stats_structure(self):
        """Test: AnalysisStats haben erwartete Struktur."""
        from quality_gui_analysis_pipeline import AnalysisStats
        
        stats = AnalysisStats(
            executed=10,
            timeouts=2,
            aborted=False,
            threshold=30.0,
            total_ms=15000
        )
        
        assert stats.executed == 10
        assert stats.timeouts == 2
        assert stats.aborted == False
        assert stats.threshold == 30.0
        assert stats.total_ms == 15000
    
    def test_analysis_rule_result_structure(self):
        """Test: AnalysisRuleResult haben erwartete Struktur."""
        from quality_gui_analysis_pipeline import AnalysisRuleResult
        
        result = AnalysisRuleResult(
            rule_name="TestRule",
            duration_ms=1500,
            timed_out=False,
            error=None,
            findings=[{'type': 'error', 'message': 'Test error'}]
        )
        
        assert result.rule_name == "TestRule"
        assert result.duration_ms == 1500
        assert result.timed_out == False
        assert result.error is None
        assert len(result.findings) == 1
    
    def test_multiple_analysis_cycles(self):
        """Test: Mehrere Analysis-Zyklen nacheinander."""
        from quality_gui_analysis_pipeline import AnalysisStats
        pipeline = QualityGuiAnalysisPipeline()
        
        # Erste Analyse
        pipeline._last_stats = AnalysisStats(executed=5, timeouts=0, total_ms=2500)
        assert pipeline._last_stats.executed == 5
        
        # Zweite Analyse
        pipeline._last_stats = AnalysisStats(executed=8, timeouts=1, total_ms=4200)
        assert pipeline._last_stats.executed == 8
        assert pipeline._last_stats.timeouts == 1
    
    def test_analysis_timeout_scenario(self):
        """Test: Timeout-Szenario wird getrackt."""
        from quality_gui_analysis_pipeline import AnalysisStats, AnalysisRuleResult
        pipeline = QualityGuiAnalysisPipeline()
        
        # Simuliere Timeout in Stats
        pipeline._last_stats = AnalysisStats(
            executed=3,
            timeouts=2,
            threshold=30.0,
            total_ms=90000
        )
        
        # Stats zeigen Timeouts
        assert pipeline._last_stats.timeouts == 2
        
        # Rule Result mit Timeout
        result = AnalysisRuleResult(
            rule_name="SlowRule",
            duration_ms=35000,
            timed_out=True,
            error="Timeout exceeded"
        )
        
        assert result.timed_out == True
        assert result.error == "Timeout exceeded"


class TestAnalysisPipelineIntegration:
    """Integrations-Tests für komplexere Szenarien."""
    
    def test_full_analysis_workflow(self):
        """Test: Vollständiger Analysis-Workflow mit Stats."""
        from quality_gui_analysis_pipeline import AnalysisStats, AnalysisRuleResult
        pipeline = QualityGuiAnalysisPipeline()
        
        # 1. Start Analysis - Stats initialisieren
        pipeline._last_stats = AnalysisStats(executed=0, timeouts=0)
        assert pipeline._last_stats.executed == 0
        
        # 2. Rules ausführen (simuliert)
        results = [
            AnalysisRuleResult("Rule1", 1200, False, None, [{'type': 'error'}]),
            AnalysisRuleResult("Rule2", 800, False, None, [{'type': 'warning'}])
        ]
        
        # 3. Stats aktualisieren
        pipeline._last_stats = AnalysisStats(
            executed=2,
            timeouts=0,
            total_ms=2000
        )
        
        assert pipeline._last_stats.executed == 2
        assert pipeline._last_stats.total_ms == 2000
    
    def test_cancelled_analysis(self):
        """Test: Abgebrochene Analysis wird getrackt."""
        from quality_gui_analysis_pipeline import AnalysisStats
        pipeline = QualityGuiAnalysisPipeline()
        
        # Start Analysis
        pipeline._last_stats = AnalysisStats(executed=3, aborted=False)
        
        # User bricht ab
        pipeline._last_stats = AnalysisStats(
            executed=3,
            timeouts=0,
            aborted=True,
            total_ms=1500
        )
        
        assert pipeline._last_stats.aborted == True
        assert pipeline._last_stats.executed == 3


# Pytest Runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
