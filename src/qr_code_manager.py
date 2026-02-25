"""QR Code Manager for Soccer Timekeeper App.

Handles QR code generation and UUID validation for match sharing.
"""

import re
import uuid
from typing import Optional
import qrcode
from PIL import Image


class QRCodeManager:
    """Manages QR code generation and UUID validation operations."""
    
    def __init__(self, box_size: int = 10, border: int = 4):
        """Initialize QR Code Manager.
        
        Args:
            box_size: Size of each box in the QR code grid
            border: Border size around the QR code
        """
        self.box_size = box_size
        self.border = border
    
    def generate_qr_code(self, match_uuid: str) -> Optional[Image.Image]:
        """Generate a QR code image containing the match UUID.
        
        Args:
            match_uuid: The UUID string to encode in the QR code
            
        Returns:
            PIL Image object containing the QR code, or None if generation fails
            
        Validates Requirements: 1.2, 2.2, 9.1, 9.2, 9.3, 9.4
        """
        try:
            qr = qrcode.QRCode(
                version=None,  # Auto-determine version based on data size
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=self.box_size,
                border=self.border,
            )
            qr.add_data(match_uuid)
            qr.make(fit=True)
            
            # Get the PIL Image from the qrcode image
            img = qr.make_image(fill_color="black", back_color="white")
            # Convert to PIL Image if it's a PilImage wrapper
            if hasattr(img, '_img'):
                return img._img
            # If it's already a PIL Image or compatible, return it
            return img.convert('RGB') if hasattr(img, 'convert') else img
        except Exception as e:
            # Log error and return None to indicate failure
            print(f"Error generating QR code: {e}")
            return None
    
    def validate_uuid(self, uuid_string: str) -> bool:
        """Validate that a string matches UUID v4 format.
        
        Args:
            uuid_string: The string to validate
            
        Returns:
            True if the string is a valid UUID v4, False otherwise
            
        Validates Requirements: 2.6, 9.1
        """
        if not uuid_string or not isinstance(uuid_string, str):
            return False
        
        # UUID v4 format: 8-4-4-4-12 hexadecimal pattern
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_pattern.match(uuid_string):
            return False
        
        # Additional validation using uuid library
        try:
            uuid_obj = uuid.UUID(uuid_string, version=4)
            # Verify it's actually version 4
            return str(uuid_obj) == uuid_string.lower()
        except (ValueError, AttributeError):
            return False
    
    def extract_uuid_from_scan(self, scan_result: str) -> Optional[str]:
        """Extract and validate UUID from scanned QR code data.
        
        Args:
            scan_result: The raw string data from QR code scan
            
        Returns:
            The validated UUID string if valid, None otherwise
            
        Validates Requirements: 2.2, 2.4, 2.6
        """
        if not scan_result:
            return None
        
        # Clean up the scanned data (remove whitespace)
        cleaned = scan_result.strip()
        
        # Validate the UUID format
        if self.validate_uuid(cleaned):
            return cleaned
        
        return None
