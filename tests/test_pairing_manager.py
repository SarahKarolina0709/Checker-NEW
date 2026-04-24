"""test_pairing_manager.py

Unit Tests für QualityGuiPairingManager.
Testet Pairing, Undo/Redo, und PairingHistoryManager.

Run:
    pytest test_pairing_manager.py -v
    pytest test_pairing_manager.py -v --cov=quality_gui_pairing_manager
"""
import pytest
from pathlib import Path
from quality_gui_pairing_manager import (
    QualityGuiPairingManager,
    PairingHistoryManager
)


class TestPairingHistoryManager:
    """Tests für PairingHistoryManager (Undo/Redo)."""
    
    def test_history_manager_initialization(self):
        """Test: HistoryManager kann initialisiert werden."""
        history = PairingHistoryManager(capacity=10)
        
        assert history._history == []
        assert history._redo == []
        assert history._capacity == 10
    
    def test_save_snapshot(self):
        """Test: Snapshot speichern."""
        from quality_gui_pairing_manager import PairingState, PairRecord
        history = PairingHistoryManager(capacity=5)
        
        state = PairingState(
            pairs=[PairRecord('file1.txt', 'trans1.txt')],
            unmatched_sources=[],
            unmatched_translations=[]
        )
        history.snapshot(state)
        
        assert len(history._history) == 1
        assert history._history[0].pairs[0].source == 'file1.txt'
    
    def test_save_multiple_snapshots(self):
        """Test: Mehrere Snapshots speichern."""
        from quality_gui_pairing_manager import PairingState, PairRecord
        history = PairingHistoryManager(capacity=5)
        
        for i in range(3):
            state = PairingState(
                pairs=[PairRecord(f'file{i}.txt', f'trans{i}.txt')],
                unmatched_sources=[],
                unmatched_translations=[]
            )
            history.snapshot(state)
        
        assert len(history._history) == 3
    
    def test_undo(self):
        """Test: Undo-Operation."""
        from quality_gui_pairing_manager import PairingState, PairRecord
        history = PairingHistoryManager(capacity=5)
        
        # Snapshots hinzufügen
        state1 = PairingState(pairs=[PairRecord('file1.txt', 'trans1.txt')])
        state2 = PairingState(pairs=[PairRecord('file2.txt', 'trans2.txt')])
        history.snapshot(state1)
        history.snapshot(state2)
        
        # Undo
        result = history.undo(state2)
        
        assert result is not None
        assert result.pairs[0].source == 'file1.txt'
    
    def test_redo(self):
        """Test: Redo-Operation."""
        from quality_gui_pairing_manager import PairingState, PairRecord
        history = PairingHistoryManager(capacity=5)
        
        # Snapshots hinzufügen
        state1 = PairingState(pairs=[PairRecord('file1.txt', 'trans1.txt')])
        state2 = PairingState(pairs=[PairRecord('file2.txt', 'trans2.txt')])
        history.snapshot(state1)
        history.snapshot(state2)
        
        # Undo dann Redo
        history.undo(state2)
        result = history.redo(state1)
        
        assert result is not None
        assert result.pairs[0].source == 'file2.txt'
    
    def test_snapshot_limit(self):
        """Test: Snapshot-Limit wird respektiert."""
        from quality_gui_pairing_manager import PairingState, PairRecord
        history = PairingHistoryManager(capacity=3)
        
        # 5 Snapshots hinzufügen (mehr als Limit)
        for i in range(5):
            state = PairingState(pairs=[PairRecord(f'file{i}.txt', f'trans{i}.txt')])
            history.snapshot(state)
        
        # Nur die letzten 3 bleiben
        assert len(history._history) == 3


class TestQualityGuiPairingManager:
    """Tests für QualityGuiPairingManager."""
    
    def test_pairing_manager_initialization(self):
        """Test: PairingManager kann initialisiert werden."""
        manager = QualityGuiPairingManager()
        
        assert manager.state.pairs == []
        assert manager.state.unmatched_sources == []
        assert manager.state.unmatched_translations == []
        assert isinstance(manager.history, PairingHistoryManager)
    
    def test_add_manual_pair(self):
        """Test: Manuelles Pairing hinzufügen."""
        from quality_gui_pairing_manager import PairRecord
        manager = QualityGuiPairingManager()
        
        pair = PairRecord(source="source.txt", translation="translation.txt")
        manager.state.pairs.append(pair)
        
        assert len(manager.state.pairs) == 1
        assert manager.state.pairs[0].source == "source.txt"
        assert manager.state.pairs[0].translation == "translation.txt"
    
    def test_add_multiple_pairs(self):
        """Test: Mehrere Pairings hinzufügen."""
        from quality_gui_pairing_manager import PairRecord
        manager = QualityGuiPairingManager()
        
        pairs = [
            PairRecord("source1.txt", "trans1.txt"),
            PairRecord("source2.txt", "trans2.txt"),
            PairRecord("source3.txt", "trans3.txt")
        ]
        
        manager.state.pairs.extend(pairs)
        
        assert len(manager.state.pairs) == 3
    
    def test_unmatched_files_tracking(self):
        """Test: Unmatched-Files werden getrackt."""
        manager = QualityGuiPairingManager()
        
        unmatched = ["unmatched1.txt", "unmatched2.txt"]
        manager.state.unmatched_sources.extend(unmatched)
        
        assert len(manager.state.unmatched_sources) == 2
    
    def test_clear_pairs(self):
        """Test: Alle Pairings löschen."""
        from quality_gui_pairing_manager import PairRecord
        manager = QualityGuiPairingManager()
        
        # Pairings hinzufügen
        manager.state.pairs.append(PairRecord("source.txt", "trans.txt"))
        manager.state.unmatched_sources.append("unmatched.txt")
        
        # Clear
        manager.state.pairs.clear()
        manager.state.unmatched_sources.clear()
        
        assert len(manager.state.pairs) == 0
        assert len(manager.state.unmatched_sources) == 0
    
    def test_history_snapshot_creation(self):
        """Test: History-Snapshot wird erstellt."""
        from quality_gui_pairing_manager import PairRecord, PairingState
        manager = QualityGuiPairingManager()
        
        # Initiales Pairing
        pair1 = PairRecord("source1.txt", "trans1.txt")
        manager.state.pairs.append(pair1)
        manager.history.snapshot(manager.state)
        
        # Zweites Pairing
        pair2 = PairRecord("source2.txt", "trans2.txt")
        manager.state.pairs.append(pair2)
        manager.history.snapshot(manager.state)
        
        # Undo sollte zum ersten Zustand zurückführen
        restored = manager.history.undo(manager.state)
        assert len(restored.pairs) == 1
        assert restored.pairs[0].source == "source1.txt"


# Pytest Runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
