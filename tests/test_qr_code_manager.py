"""Unit tests for QRCodeManager."""

import uuid
import pytest
from src.qr_code_manager import QRCodeManager


class TestQRCodeManager:
    """Test suite for QRCodeManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.qr_manager = QRCodeManager()
    
    def test_generate_qr_code_returns_image(self):
        """Test that generate_qr_code returns an image object."""
        test_uuid = str(uuid.uuid4())
        result = self.qr_manager.generate_qr_code(test_uuid)
        
        assert result is not None
        # Check it has image-like properties
        assert hasattr(result, 'size')
        assert hasattr(result, 'mode')
    
    def test_generate_qr_code_with_valid_uuid(self):
        """Test QR code generation with a valid UUID."""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = self.qr_manager.generate_qr_code(test_uuid)
        
        assert result is not None
        # Verify image has dimensions
        assert hasattr(result, 'size')
        assert result.size[0] > 0
        assert result.size[1] > 0
    
    def test_generate_qr_code_with_empty_string(self):
        """Test QR code generation with empty string."""
        result = self.qr_manager.generate_qr_code("")
        
        # Should still generate a QR code (even for empty string)
        assert result is not None
        assert hasattr(result, 'size')
    
    def test_validate_uuid_with_valid_v4_uuid(self):
        """Test UUID validation with valid UUID v4."""
        valid_uuid = str(uuid.uuid4())
        assert self.qr_manager.validate_uuid(valid_uuid) is True
    
    def test_validate_uuid_with_specific_valid_uuid(self):
        """Test UUID validation with specific valid UUID v4."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert self.qr_manager.validate_uuid(valid_uuid) is True
    
    def test_validate_uuid_with_uppercase(self):
        """Test UUID validation with uppercase letters."""
        valid_uuid = "550E8400-E29B-41D4-A716-446655440000"
        assert self.qr_manager.validate_uuid(valid_uuid) is True
    
    def test_validate_uuid_with_invalid_format(self):
        """Test UUID validation with invalid format."""
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400-e29b-31d4-a716-446655440000",  # Wrong version (3 instead of 4)
            "550e8400-e29b-41d4-c716-446655440000",  # Invalid variant
            "",
            None,
        ]
        
        for invalid_uuid in invalid_uuids:
            assert self.qr_manager.validate_uuid(invalid_uuid) is False
    
    def test_validate_uuid_with_wrong_version(self):
        """Test UUID validation rejects non-v4 UUIDs."""
        # UUID v1
        uuid_v1 = str(uuid.uuid1())
        # UUID v3
        uuid_v3 = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'test'))
        # UUID v5
        uuid_v5 = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'test'))
        
        # These should be rejected as they're not v4
        assert self.qr_manager.validate_uuid(uuid_v1) is False
        assert self.qr_manager.validate_uuid(uuid_v3) is False
        assert self.qr_manager.validate_uuid(uuid_v5) is False
    
    def test_extract_uuid_from_scan_with_valid_uuid(self):
        """Test extracting UUID from valid scan result."""
        test_uuid = str(uuid.uuid4())
        result = self.qr_manager.extract_uuid_from_scan(test_uuid)
        
        assert result == test_uuid
    
    def test_extract_uuid_from_scan_with_whitespace(self):
        """Test extracting UUID from scan result with whitespace."""
        test_uuid = str(uuid.uuid4())
        scan_result = f"  {test_uuid}  \n"
        result = self.qr_manager.extract_uuid_from_scan(scan_result)
        
        assert result == test_uuid
    
    def test_extract_uuid_from_scan_with_invalid_data(self):
        """Test extracting UUID from invalid scan result."""
        invalid_results = [
            "not-a-uuid",
            "12345",
            "",
            "   ",
            None,
        ]
        
        for invalid_result in invalid_results:
            result = self.qr_manager.extract_uuid_from_scan(invalid_result)
            assert result is None
    
    def test_extract_uuid_from_scan_with_empty_string(self):
        """Test extracting UUID from empty string."""
        result = self.qr_manager.extract_uuid_from_scan("")
        assert result is None
    
    def test_qr_code_manager_custom_parameters(self):
        """Test QRCodeManager with custom box_size and border."""
        custom_manager = QRCodeManager(box_size=5, border=2)
        test_uuid = str(uuid.uuid4())
        result = custom_manager.generate_qr_code(test_uuid)
        
        assert result is not None
        assert hasattr(result, 'size')
    
    def test_generate_qr_code_error_handling(self):
        """Test that generate_qr_code handles errors gracefully."""
        # Test with various edge cases that might cause issues
        edge_cases = [
            "a" * 10000,  # Very long string
            "\x00\x01\x02",  # Binary data
        ]
        
        for test_case in edge_cases:
            result = self.qr_manager.generate_qr_code(test_case)
            # Should either return an image or None, not raise exception
            assert result is None or hasattr(result, 'size')
