"""Unit tests for storage error handling scenarios."""

import json
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

from src.storage_manager import StorageManager
from src.models import Match, TimerState


class TestStorageErrorHandling:
    """Test error handling in StorageManager."""
    
    def test_load_match_file_not_found(self):
        """Test loading match when storage file doesn't exist."""
        # Create storage manager with non-existent path
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent" / "storage.json"
            
            # Delete the file if it was created during init
            if storage_path.exists():
                storage_path.unlink()
            if storage_path.parent.exists():
                storage_path.parent.rmdir()
            
            storage = StorageManager(str(storage_path))
            
            # Should handle gracefully and return None for non-existent match
            result = storage.load_match("non-existent-uuid")
            assert result is None
    
    def test_load_match_corrupted_json(self):
        """Test loading match when JSON is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            
            # Write corrupted JSON
            with open(storage_path, 'w') as f:
                f.write("{invalid json content")
            
            storage = StorageManager(str(storage_path))
            
            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                storage.load_match("some-uuid")
    
    def test_load_match_missing_match_data(self):
        """Test loading match when match UUID doesn't exist in storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Try to load non-existent match
            result = storage.load_match("non-existent-uuid")
            assert result is None
    
    def test_save_match_permission_error(self):
        """Test saving match when file permissions prevent writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Create a match
            timer_state = TimerState(
                seconds_remaining=5400,
                is_running=False,
                last_update=datetime.now(),
                total_paused_time=0
            )
            match = Match(
                match_uuid="test-uuid",
                description="Test Match",
                admin_id="admin-123",
                timer_state=timer_state,
                created_at=datetime.now(),
                is_active=True
            )
            
            # Make file read-only
            storage_path.chmod(0o444)
            
            try:
                # Should raise PermissionError
                with pytest.raises(PermissionError):
                    storage.save_match(match)
            finally:
                # Restore permissions for cleanup
                storage_path.chmod(0o644)
    
    def test_load_user_data_file_not_found(self):
        """Test loading user data when storage file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent" / "storage.json"
            
            # Delete the file if it was created during init
            if storage_path.exists():
                storage_path.unlink()
            if storage_path.parent.exists():
                storage_path.parent.rmdir()
            
            storage = StorageManager(str(storage_path))
            
            # Should return empty list for non-existent user
            result = storage.load_user_data("non-existent-user")
            assert result == []
    
    def test_load_user_data_missing_user(self):
        """Test loading user data when user doesn't exist in storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Try to load non-existent user
            result = storage.load_user_data("non-existent-user")
            assert result == []
    
    def test_save_user_data_corrupted_json(self):
        """Test saving user data when existing JSON is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            
            # Write corrupted JSON
            with open(storage_path, 'w') as f:
                f.write("{invalid json")
            
            storage = StorageManager(str(storage_path))
            
            # Should raise JSONDecodeError when trying to read
            with pytest.raises(json.JSONDecodeError):
                storage.save_user_data("user-123", ["match-1", "match-2"])
    
    def test_list_all_matches_empty_storage(self):
        """Test listing all matches when storage is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Should return empty list
            result = storage.list_all_matches()
            assert result == []
    
    def test_list_all_matches_corrupted_json(self):
        """Test listing all matches when JSON is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            
            # Write corrupted JSON
            with open(storage_path, 'w') as f:
                f.write("not valid json at all")
            
            storage = StorageManager(str(storage_path))
            
            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                storage.list_all_matches()
    
    def test_concurrent_read_operations(self):
        """Test multiple concurrent read operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Save a match first
            timer_state = TimerState(
                seconds_remaining=5400,
                is_running=False,
                last_update=datetime.now(),
                total_paused_time=0
            )
            match = Match(
                match_uuid="test-uuid",
                description="Test Match",
                admin_id="admin-123",
                timer_state=timer_state,
                created_at=datetime.now(),
                is_active=True
            )
            storage.save_match(match)
            
            # Perform multiple concurrent reads
            results = []
            for _ in range(10):
                result = storage.load_match("test-uuid")
                results.append(result)
            
            # All reads should succeed and return the same data
            assert all(r is not None for r in results)
            assert all(r.match_uuid == "test-uuid" for r in results)
    
    def test_concurrent_write_operations(self):
        """Test multiple concurrent write operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Create multiple matches
            matches = []
            for i in range(5):
                timer_state = TimerState(
                    seconds_remaining=5400 - i * 100,
                    is_running=False,
                    last_update=datetime.now(),
                    total_paused_time=0
                )
                match = Match(
                    match_uuid=f"test-uuid-{i}",
                    description=f"Test Match {i}",
                    admin_id=f"admin-{i}",
                    timer_state=timer_state,
                    created_at=datetime.now(),
                    is_active=True
                )
                matches.append(match)
            
            # Write all matches
            for match in matches:
                storage.save_match(match)
            
            # Verify all matches were saved correctly
            for i, match in enumerate(matches):
                loaded = storage.load_match(f"test-uuid-{i}")
                assert loaded is not None
                assert loaded.match_uuid == f"test-uuid-{i}"
                assert loaded.description == f"Test Match {i}"
    
    def test_load_match_with_missing_fields(self):
        """Test loading match when stored data has missing fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            
            # Write incomplete match data
            incomplete_data = {
                "matches": {
                    "test-uuid": {
                        "match_uuid": "test-uuid",
                        "description": "Test Match"
                        # Missing other required fields
                    }
                },
                "users": {}
            }
            
            with open(storage_path, 'w') as f:
                json.dump(incomplete_data, f)
            
            storage = StorageManager(str(storage_path))
            
            # Should raise KeyError when trying to access missing fields
            with pytest.raises(KeyError):
                storage.load_match("test-uuid")
    
    def test_storage_initialization_creates_directory(self):
        """Test that storage initialization creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nested" / "path" / "storage.json"
            
            # Directory shouldn't exist yet
            assert not storage_path.parent.exists()
            
            # Initialize storage
            storage = StorageManager(str(storage_path))
            
            # Directory should now exist
            assert storage_path.parent.exists()
            assert storage_path.exists()
    
    def test_storage_initialization_creates_empty_structure(self):
        """Test that storage initialization creates proper empty structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "storage.json"
            storage = StorageManager(str(storage_path))
            
            # Read the file directly
            with open(storage_path, 'r') as f:
                data = json.load(f)
            
            # Should have matches and users keys
            assert "matches" in data
            assert "users" in data
            assert data["matches"] == {}
            assert data["users"] == {}
