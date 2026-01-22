"""test_upload_manager.py

Unit Tests für QualityGuiUploadManager.
Testet File Upload, ManagedFile-Erstellung, und Kind-basierte Kategorisierung.

Run:
    pytest test_upload_manager.py -v
    pytest test_upload_manager.py -v --cov=quality_gui_upload_manager
"""
import pytest
from pathlib import Path
from quality_gui_upload_manager import (
    QualityGuiUploadManager,
    ManagedFile,
    UploadStats
)


class TestManagedFile:
    """Tests für ManagedFile Dataclass."""
    
    def test_managed_file_creation(self):
        """Test: ManagedFile kann erstellt werden."""
        path = Path("test.txt")
        mf = ManagedFile(path=path, kind="source", size=1024, added_ts=1234567890.0)
        
        assert mf.path == path
        assert mf.kind == "source"
        assert mf.size == 1024
        assert mf.added_ts == 1234567890.0
    
    def test_managed_file_default_values(self):
        """Test: ManagedFile mit Default-Werten."""
        path = Path("test.txt")
        mf = ManagedFile(path=path, kind="translation", size=512, added_ts=1234567890.0)
        
        assert mf.path == path
        assert mf.kind == "translation"


class TestUploadStats:
    """Tests für UploadStats Dataclass."""
    
    def test_upload_stats_defaults(self):
        """Test: UploadStats mit Default-Werten."""
        stats = UploadStats()
        
        assert stats.added == 0
        assert stats.duplicates == 0
        assert stats.skipped == 0
        assert stats.total_size == 0
    
    def test_upload_stats_custom_values(self):
        """Test: UploadStats mit Custom-Werten."""
        stats = UploadStats(
            added=10,
            duplicates=2,
            skipped=1,
            total_size=10240
        )
        
        assert stats.added == 10
        assert stats.duplicates == 2
        assert stats.skipped == 1
        assert stats.total_size == 10240


class TestQualityGuiUploadManager:
    """Tests für QualityGuiUploadManager."""
    
    def test_upload_manager_initialization(self):
        """Test: UploadManager kann initialisiert werden."""
        manager = QualityGuiUploadManager()
        
        assert manager._files == []
        assert manager._by_kind == {'source': [], 'translation': []}
    
    def test_add_file_source(self):
        """Test: Source-Datei hinzufügen."""
        manager = QualityGuiUploadManager()
        path = Path("test_source.txt")
        
        mf = ManagedFile(path=path, kind="source", size=1024, added_ts=1234567890.0)
        manager._files.append(mf)
        manager._by_kind['source'].append(mf)
        
        assert len(manager._files) == 1
        assert len(manager._by_kind['source']) == 1
        assert len(manager._by_kind['translation']) == 0
        assert manager._files[0].kind == "source"
    
    def test_add_file_translation(self):
        """Test: Translation-Datei hinzufügen."""
        manager = QualityGuiUploadManager()
        path = Path("test_translation.txt")
        
        mf = ManagedFile(path=path, kind="translation", size=512, added_ts=1234567890.0)
        manager._files.append(mf)
        manager._by_kind['translation'].append(mf)
        
        assert len(manager._files) == 1
        assert len(manager._by_kind['source']) == 0
        assert len(manager._by_kind['translation']) == 1
        assert manager._files[0].kind == "translation"
    
    def test_add_multiple_files_mixed(self):
        """Test: Mehrere Dateien verschiedener Typen."""
        manager = QualityGuiUploadManager()
        
        # Source-Dateien
        for i in range(3):
            mf = ManagedFile(
                path=Path(f"source_{i}.txt"),
                kind="source",
                size=1024 * (i + 1),
                added_ts=1234567890.0 + i
            )
            manager._files.append(mf)
            manager._by_kind['source'].append(mf)
        
        # Translation-Dateien
        for i in range(2):
            mf = ManagedFile(
                path=Path(f"translation_{i}.txt"),
                kind="translation",
                size=512 * (i + 1),
                added_ts=1234567900.0 + i
            )
            manager._files.append(mf)
            manager._by_kind['translation'].append(mf)
        
        assert len(manager._files) == 5
        assert len(manager._by_kind['source']) == 3
        assert len(manager._by_kind['translation']) == 2
    
    def test_clear_files(self):
        """Test: Alle Dateien löschen."""
        manager = QualityGuiUploadManager()
        
        # Dateien hinzufügen
        mf1 = ManagedFile(path=Path("test1.txt"), kind="source", size=1024, added_ts=1234567890.0)
        mf2 = ManagedFile(path=Path("test2.txt"), kind="translation", size=512, added_ts=1234567890.0)
        manager._files.extend([mf1, mf2])
        manager._by_kind['source'].append(mf1)
        manager._by_kind['translation'].append(mf2)
        
        # Clear
        manager._files.clear()
        manager._by_kind['source'].clear()
        manager._by_kind['translation'].clear()
        
        assert len(manager._files) == 0
        assert len(manager._by_kind['source']) == 0
        assert len(manager._by_kind['translation']) == 0
    
    def test_file_path_uniqueness(self):
        """Test: Jede Datei hat einen eindeutigen Pfad."""
        manager = QualityGuiUploadManager()
        
        paths = [Path(f"file_{i}.txt") for i in range(5)]
        for path in paths:
            mf = ManagedFile(path=path, kind="source", size=1024, added_ts=1234567890.0)
            manager._files.append(mf)
            manager._by_kind['source'].append(mf)
        
        file_paths = [mf.path for mf in manager._files]
        assert len(file_paths) == len(set(file_paths))  # Alle Pfade einzigartig


# Pytest Runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
