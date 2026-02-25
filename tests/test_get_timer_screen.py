"""Unit tests for get timer screen functionality."""

import pytest
import uuid
from src.qr_code_manager import QRCodeManager
from src.user_manager import UserManager
from src.match_manager import MatchManager
from src.timer_manager import TimerManager
from src.storage_manager import StorageManager


class TestGetTimerScreenFunctionality:
    """Test suite for get timer screen functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.storage_manager = StorageManager()
        self.timer_manager = TimerManager()
        self.match_manager = MatchManager(self.storage_manager, self.timer_manager)
        self.user_manager = UserManager(self.storage_manager)
        self.qr_manager = QRCodeManager()
    
    def test_qr_code_manager_validate_uuid_valid(self):
        """Test that valid UUIDs are accepted."""
        # Test with a valid UUID v4
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert self.qr_manager.validate_uuid(valid_uuid) == True
    
    def test_qr_code_manager_validate_uuid_invalid(self):
        """Test that invalid UUIDs are rejected."""
        # Test with invalid formats
        assert self.qr_manager.validate_uuid("not-a-uuid") == False
        assert self.qr_manager.validate_uuid("") == False
        assert self.qr_manager.validate_uuid("12345") == False
    
    def test_qr_code_manager_extract_uuid_from_scan_valid(self):
        """Test extracting valid UUID from scan result."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = self.qr_manager.extract_uuid_from_scan(valid_uuid)
        
        assert result == valid_uuid
    
    def test_qr_code_manager_extract_uuid_from_scan_invalid(self):
        """Test that invalid scan results return None."""
        assert self.qr_manager.extract_uuid_from_scan("invalid-data") is None
        assert self.qr_manager.extract_uuid_from_scan("") is None
    
    def test_user_manager_add_match_to_user(self):
        """Test adding a match to user's list."""
        user_id = f"test-user-{uuid.uuid4()}"
        match_uuid = "550e8400-e29b-41d4-a716-446655440000"
        
        # Add match to user
        self.user_manager.add_match_to_user(user_id, match_uuid)
        
        # Verify match is in user's list
        user_matches = self.user_manager.get_user_matches(user_id)
        assert match_uuid in user_matches
    
    def test_user_manager_add_match_no_duplicates(self):
        """Test that adding the same match twice doesn't create duplicates."""
        user_id = f"test-user-{uuid.uuid4()}"
        match_uuid = "550e8400-e29b-41d4-a716-446655440000"
        
        # Add match twice
        self.user_manager.add_match_to_user(user_id, match_uuid)
        self.user_manager.add_match_to_user(user_id, match_uuid)
        
        # Verify only one instance exists
        user_matches = self.user_manager.get_user_matches(user_id)
        assert user_matches.count(match_uuid) == 1
    
    def test_match_manager_get_nonexistent_match(self):
        """Test that getting a non-existent match returns None."""
        # Try to get a match that doesn't exist
        result = self.match_manager.get_match("nonexistent-uuid")
        
        assert result is None
    
    def test_integration_add_match_workflow(self):
        """Test the complete workflow of adding a match to a user."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Simulate scanning QR code
        scanned_uuid = match.match_uuid
        
        # Validate UUID
        assert self.qr_manager.validate_uuid(scanned_uuid) == True
        
        # Extract UUID from scan
        extracted_uuid = self.qr_manager.extract_uuid_from_scan(scanned_uuid)
        assert extracted_uuid == scanned_uuid
        
        # Check if match exists
        retrieved_match = self.match_manager.get_match(extracted_uuid)
        assert retrieved_match is not None
        assert retrieved_match.match_uuid == match.match_uuid
        
        # Add match to user
        user_id = f"user-{uuid.uuid4()}"
        self.user_manager.add_match_to_user(user_id, extracted_uuid)
        
        # Verify match is in user's list
        user_matches = self.user_manager.get_user_matches(user_id)
        assert extracted_uuid in user_matches
    
    def test_manual_entry_with_whitespace(self):
        """Test that manual entry handles whitespace correctly."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Simulate manual entry with whitespace
        manual_input = f"  {match.match_uuid}  \n"
        
        # Extract and validate
        extracted_uuid = self.qr_manager.extract_uuid_from_scan(manual_input)
        assert extracted_uuid == match.match_uuid
        
        # Verify match exists
        retrieved_match = self.match_manager.get_match(extracted_uuid)
        assert retrieved_match is not None
    
    def test_error_handling_invalid_uuid_format(self):
        """Test error handling for invalid UUID format in manual entry."""
        invalid_inputs = [
            "not-a-uuid",
            "12345",
            "abc-def-ghi",
            "",
            "   ",
        ]
        
        for invalid_input in invalid_inputs:
            # Validate should return False
            assert self.qr_manager.validate_uuid(invalid_input.strip()) == False
            
            # Extract should return None
            assert self.qr_manager.extract_uuid_from_scan(invalid_input) is None
    
    def test_error_handling_nonexistent_match(self):
        """Test error handling when match UUID doesn't exist in storage."""
        # Generate a valid UUID that doesn't exist in storage
        nonexistent_uuid = str(uuid.uuid4())
        
        # Validate format (should pass)
        assert self.qr_manager.validate_uuid(nonexistent_uuid) == True
        
        # Try to get match (should return None)
        match = self.match_manager.get_match(nonexistent_uuid)
        assert match is None

