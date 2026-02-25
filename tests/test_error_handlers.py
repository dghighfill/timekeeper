"""Unit tests for error handling wrappers."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from PIL import Image

from src.error_handlers import ErrorHandlers
from src.models import Match, TimerState
from src.storage_manager import StorageManager
from src.qr_code_manager import QRCodeManager
from src.timer_manager import TimerManager


@pytest.fixture
def mock_storage_manager():
    """Create a mock storage manager."""
    return Mock(spec=StorageManager)


@pytest.fixture
def mock_qr_manager():
    """Create a mock QR code manager."""
    return Mock(spec=QRCodeManager)


@pytest.fixture
def mock_timer_manager():
    """Create a mock timer manager."""
    return Mock(spec=TimerManager)


@pytest.fixture
def error_handlers(mock_storage_manager, mock_qr_manager, mock_timer_manager):
    """Create error handlers instance with mocked dependencies."""
    return ErrorHandlers(mock_storage_manager, mock_qr_manager, mock_timer_manager)


@pytest.fixture
def sample_match():
    """Create a sample match for testing."""
    timer_state = TimerState(
        seconds_remaining=5400,
        is_running=False,
        last_update=datetime.now(),
        total_paused_time=0
    )
    return Match(
        match_uuid="12345678-1234-4234-8234-123456789012",
        description="Test Match",
        admin_id="admin-123",
        timer_state=timer_state,
        created_at=datetime.now(),
        is_active=True
    )


class TestSafeLoadMatch:
    """Tests for safe_load_match error handling."""
    
    def test_successful_load(self, error_handlers, mock_storage_manager, sample_match):
        """Test successful match loading."""
        mock_storage_manager.load_match.return_value = sample_match
        
        match, error = error_handlers.safe_load_match(sample_match.match_uuid)
        
        assert match == sample_match
        assert error is None
        mock_storage_manager.load_match.assert_called_once_with(sample_match.match_uuid)
    
    def test_match_not_found(self, error_handlers, mock_storage_manager):
        """Test handling when match doesn't exist."""
        mock_storage_manager.load_match.return_value = None
        
        match, error = error_handlers.safe_load_match("nonexistent-uuid")
        
        assert match is None
        assert "not found" in error.lower()
    
    def test_file_not_found_error(self, error_handlers, mock_storage_manager):
        """Test handling of FileNotFoundError."""
        mock_storage_manager.load_match.side_effect = FileNotFoundError("Storage file missing")
        
        match, error = error_handlers.safe_load_match("test-uuid")
        
        assert match is None
        assert "storage file not found" in error.lower()
    
    def test_json_decode_error(self, error_handlers, mock_storage_manager):
        """Test handling of corrupted JSON data."""
        mock_storage_manager.load_match.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        match, error = error_handlers.safe_load_match("test-uuid")
        
        assert match is None
        assert "corrupted" in error.lower()
    
    def test_permission_error(self, error_handlers, mock_storage_manager):
        """Test handling of permission errors."""
        mock_storage_manager.load_match.side_effect = PermissionError("Access denied")
        
        match, error = error_handlers.safe_load_match("test-uuid")
        
        assert match is None
        assert "permission" in error.lower()
    
    def test_unexpected_error(self, error_handlers, mock_storage_manager):
        """Test handling of unexpected errors."""
        mock_storage_manager.load_match.side_effect = RuntimeError("Unexpected error")
        
        match, error = error_handlers.safe_load_match("test-uuid")
        
        assert match is None
        assert "unexpected error" in error.lower()


class TestSafeSaveMatch:
    """Tests for safe_save_match error handling."""
    
    def test_successful_save(self, error_handlers, mock_storage_manager, sample_match):
        """Test successful match saving."""
        success, error = error_handlers.safe_save_match(sample_match)
        
        assert success is True
        assert error is None
        mock_storage_manager.save_match.assert_called_once_with(sample_match)
    
    def test_permission_error(self, error_handlers, mock_storage_manager, sample_match):
        """Test handling of permission errors during save."""
        mock_storage_manager.save_match.side_effect = PermissionError("Access denied")
        
        success, error = error_handlers.safe_save_match(sample_match)
        
        assert success is False
        assert "permission" in error.lower()
    
    def test_os_error(self, error_handlers, mock_storage_manager, sample_match):
        """Test handling of OS errors during save."""
        mock_storage_manager.save_match.side_effect = OSError("Disk full")
        
        success, error = error_handlers.safe_save_match(sample_match)
        
        assert success is False
        assert "file system error" in error.lower()
    
    def test_json_encode_error(self, error_handlers, mock_storage_manager, sample_match):
        """Test handling of JSON encoding errors."""
        mock_storage_manager.save_match.side_effect = json.JSONDecodeError("Encode error", "", 0)
        
        success, error = error_handlers.safe_save_match(sample_match)
        
        assert success is False
        assert "encoding" in error.lower() or "contact support" in error.lower()
    
    def test_unexpected_error(self, error_handlers, mock_storage_manager, sample_match):
        """Test handling of unexpected errors during save."""
        mock_storage_manager.save_match.side_effect = RuntimeError("Unexpected error")
        
        success, error = error_handlers.safe_save_match(sample_match)
        
        assert success is False
        assert "unexpected error" in error.lower()


class TestSafeScanQRCode:
    """Tests for safe_scan_qr_code error handling."""
    
    def test_successful_scan(self, error_handlers, mock_qr_manager):
        """Test successful QR code scanning."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_qr_manager.extract_uuid_from_scan.return_value = test_uuid
        
        uuid_string, error = error_handlers.safe_scan_qr_code("scanned_data")
        
        assert uuid_string == test_uuid
        assert error is None
    
    def test_scanner_unavailable(self, error_handlers):
        """Test handling when scanner is unavailable (None result)."""
        uuid_string, error = error_handlers.safe_scan_qr_code(None)
        
        assert uuid_string is None
        assert "unavailable" in error.lower()
        assert "manual entry" in error.lower()
    
    def test_invalid_qr_data(self, error_handlers, mock_qr_manager):
        """Test handling of invalid QR code data."""
        mock_qr_manager.extract_uuid_from_scan.return_value = None
        
        uuid_string, error = error_handlers.safe_scan_qr_code("invalid_data")
        
        assert uuid_string is None
        assert "could not be decoded" in error.lower()
    
    def test_unexpected_error(self, error_handlers, mock_qr_manager):
        """Test handling of unexpected errors during scan."""
        mock_qr_manager.extract_uuid_from_scan.side_effect = RuntimeError("Unexpected error")
        
        uuid_string, error = error_handlers.safe_scan_qr_code("test_data")
        
        assert uuid_string is None
        assert "error processing" in error.lower()


class TestSafeGenerateQRCode:
    """Tests for safe_generate_qr_code error handling."""
    
    def test_successful_generation(self, error_handlers, mock_qr_manager):
        """Test successful QR code generation."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_image = Mock(spec=Image.Image)
        mock_qr_manager.validate_uuid.return_value = True
        mock_qr_manager.generate_qr_code.return_value = mock_image
        
        image, error = error_handlers.safe_generate_qr_code(test_uuid)
        
        assert image == mock_image
        assert error is None
    
    def test_invalid_uuid_format(self, error_handlers, mock_qr_manager):
        """Test handling of invalid UUID format."""
        mock_qr_manager.validate_uuid.return_value = False
        
        image, error = error_handlers.safe_generate_qr_code("invalid-uuid")
        
        assert image is None
        assert "invalid uuid format" in error.lower()
    
    def test_generation_failure(self, error_handlers, mock_qr_manager):
        """Test handling when QR generation returns None."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_qr_manager.validate_uuid.return_value = True
        mock_qr_manager.generate_qr_code.return_value = None
        
        image, error = error_handlers.safe_generate_qr_code(test_uuid)
        
        assert image is None
        assert "failed to generate" in error.lower()
    
    def test_import_error(self, error_handlers, mock_qr_manager):
        """Test handling of missing QR code library."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_qr_manager.validate_uuid.return_value = True
        mock_qr_manager.generate_qr_code.side_effect = ImportError("qrcode not found")
        
        image, error = error_handlers.safe_generate_qr_code(test_uuid)
        
        assert image is None
        assert "library not available" in error.lower()
    
    def test_unexpected_error(self, error_handlers, mock_qr_manager):
        """Test handling of unexpected errors during generation."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_qr_manager.validate_uuid.return_value = True
        mock_qr_manager.generate_qr_code.side_effect = RuntimeError("Unexpected error")
        
        image, error = error_handlers.safe_generate_qr_code(test_uuid)
        
        assert image is None
        assert "error generating" in error.lower()


class TestSafeTimerOperation:
    """Tests for safe_timer_operation error handling."""
    
    def test_pause_operation(self, error_handlers, mock_timer_manager, sample_match):
        """Test successful pause operation."""
        updated_timer = TimerState(
            seconds_remaining=5400,
            is_running=False,
            last_update=datetime.now(),
            total_paused_time=0
        )
        mock_timer_manager.pause.return_value = updated_timer
        
        match, error = error_handlers.safe_timer_operation(sample_match, "pause")
        
        assert match is not None
        assert error is None
        mock_timer_manager.pause.assert_called_once()
    
    def test_resume_operation(self, error_handlers, mock_timer_manager, sample_match):
        """Test successful resume operation."""
        updated_timer = TimerState(
            seconds_remaining=5400,
            is_running=True,
            last_update=datetime.now(),
            total_paused_time=0
        )
        mock_timer_manager.resume.return_value = updated_timer
        
        match, error = error_handlers.safe_timer_operation(sample_match, "resume")
        
        assert match is not None
        assert error is None
        mock_timer_manager.resume.assert_called_once()
    
    def test_reset_operation(self, error_handlers, mock_timer_manager, sample_match):
        """Test successful reset operation."""
        updated_timer = TimerState(
            seconds_remaining=5400,
            is_running=False,
            last_update=datetime.now(),
            total_paused_time=0
        )
        mock_timer_manager.reset.return_value = updated_timer
        
        match, error = error_handlers.safe_timer_operation(sample_match, "reset")
        
        assert match is not None
        assert error is None
        mock_timer_manager.reset.assert_called_once()
    
    def test_stop_operation(self, error_handlers, sample_match):
        """Test successful stop operation."""
        match, error = error_handlers.safe_timer_operation(sample_match, "stop")
        
        assert match is not None
        assert match.is_active is False
        assert match.timer_state.is_running is False
        assert error is None
    
    def test_inactive_match(self, error_handlers, sample_match):
        """Test operation on inactive match."""
        sample_match.is_active = False
        
        match, error = error_handlers.safe_timer_operation(sample_match, "pause")
        
        assert match is None
        assert "inactive match" in error.lower()
    
    def test_unknown_operation(self, error_handlers, sample_match):
        """Test handling of unknown operation."""
        match, error = error_handlers.safe_timer_operation(sample_match, "invalid_op")
        
        assert match is None
        assert "unknown" in error.lower()
    
    def test_attribute_error(self, error_handlers, mock_timer_manager, sample_match):
        """Test handling of attribute errors."""
        mock_timer_manager.pause.side_effect = AttributeError("Invalid attribute")
        
        match, error = error_handlers.safe_timer_operation(sample_match, "pause")
        
        assert match is None
        assert "invalid match" in error.lower() or "timer state" in error.lower()
    
    def test_unexpected_error(self, error_handlers, mock_timer_manager, sample_match):
        """Test handling of unexpected errors."""
        mock_timer_manager.pause.side_effect = RuntimeError("Unexpected error")
        
        match, error = error_handlers.safe_timer_operation(sample_match, "pause")
        
        assert match is None
        assert "error performing" in error.lower()


class TestValidateMatchDescription:
    """Tests for match description validation."""
    
    def test_valid_description(self, error_handlers):
        """Test validation of valid description."""
        is_valid, error = error_handlers.validate_match_description("Championship Final")
        
        assert is_valid is True
        assert error is None
    
    def test_empty_description(self, error_handlers):
        """Test validation of empty description."""
        is_valid, error = error_handlers.validate_match_description("")
        
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_whitespace_only_description(self, error_handlers):
        """Test validation of whitespace-only description."""
        is_valid, error = error_handlers.validate_match_description("   ")
        
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_too_long_description(self, error_handlers):
        """Test validation of description exceeding max length."""
        long_description = "A" * 201
        is_valid, error = error_handlers.validate_match_description(long_description)
        
        assert is_valid is False
        assert "200 characters" in error.lower()


class TestValidateMatchUUIDFormat:
    """Tests for UUID format validation."""
    
    def test_valid_uuid(self, error_handlers, mock_qr_manager):
        """Test validation of valid UUID."""
        test_uuid = "12345678-1234-4234-8234-123456789012"
        mock_qr_manager.validate_uuid.return_value = True
        
        is_valid, error = error_handlers.validate_match_uuid_format(test_uuid)
        
        assert is_valid is True
        assert error is None
    
    def test_invalid_uuid(self, error_handlers, mock_qr_manager):
        """Test validation of invalid UUID."""
        mock_qr_manager.validate_uuid.return_value = False
        
        is_valid, error = error_handlers.validate_match_uuid_format("invalid-uuid")
        
        assert is_valid is False
        assert "invalid uuid format" in error.lower()
    
    def test_empty_uuid(self, error_handlers):
        """Test validation of empty UUID."""
        is_valid, error = error_handlers.validate_match_uuid_format("")
        
        assert is_valid is False
        assert "cannot be empty" in error.lower()
    
    def test_whitespace_uuid(self, error_handlers):
        """Test validation of whitespace-only UUID."""
        is_valid, error = error_handlers.validate_match_uuid_format("   ")
        
        assert is_valid is False
        assert "cannot be empty" in error.lower()
