"""Error handling wrappers for Soccer Timekeeper App.

Provides safe wrapper functions with comprehensive error handling
for storage, QR code, and timer operations.
"""

import json
import logging
from typing import Optional, Tuple
from PIL import Image

from src.models import Match
from src.storage_manager import StorageManager
from src.qr_code_manager import QRCodeManager
from src.timer_manager import TimerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorHandlers:
    """Provides safe wrapper functions with comprehensive error handling."""
    
    def __init__(
        self,
        storage_manager: StorageManager,
        qr_manager: QRCodeManager,
        timer_manager: TimerManager
    ):
        """Initialize error handlers with manager dependencies.
        
        Args:
            storage_manager: Storage manager instance
            qr_manager: QR code manager instance
            timer_manager: Timer manager instance
        """
        self.storage_manager = storage_manager
        self.qr_manager = qr_manager
        self.timer_manager = timer_manager
    
    def safe_load_match(self, match_uuid: str) -> Tuple[Optional[Match], Optional[str]]:
        """Safely loads match with comprehensive error handling.
        
        Args:
            match_uuid: UUID of the match to load
            
        Returns:
            Tuple of (Match object or None, error message or None)
            
        Validates Requirements: 2.7, 8.1
        """
        try:
            match = self.storage_manager.load_match(match_uuid)
            if match is None:
                error_msg = f"Match {match_uuid} not found."
                logger.warning(f"Match not found: {match_uuid}")
                return (None, error_msg)
            
            logger.info(f"Successfully loaded match: {match_uuid}")
            return (match, None)
            
        except FileNotFoundError as e:
            error_msg = f"Storage file not found. Please contact support."
            logger.error(f"Storage file not found: {e}")
            return (None, error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = "Storage data is corrupted. Please contact support."
            logger.error(f"JSON decode error loading match {match_uuid}: {e}")
            return (None, error_msg)
            
        except PermissionError as e:
            error_msg = "Permission denied accessing storage. Check file permissions."
            logger.error(f"Permission error loading match {match_uuid}: {e}")
            return (None, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error loading match: {str(e)}"
            logger.error(f"Unexpected error loading match {match_uuid}: {e}", exc_info=True)
            return (None, error_msg)
    
    def safe_save_match(self, match: Match) -> Tuple[bool, Optional[str]]:
        """Safely saves match with comprehensive error handling.
        
        Args:
            match: Match object to save
            
        Returns:
            Tuple of (success boolean, error message or None)
            
        Validates Requirements: 8.1
        """
        try:
            self.storage_manager.save_match(match)
            logger.info(f"Successfully saved match: {match.match_uuid}")
            return (True, None)
            
        except PermissionError as e:
            error_msg = "Cannot save match. Check file permissions."
            logger.error(f"Permission error saving match {match.match_uuid}: {e}")
            return (False, error_msg)
            
        except OSError as e:
            error_msg = f"File system error saving match: {str(e)}"
            logger.error(f"OS error saving match {match.match_uuid}: {e}")
            return (False, error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = "Error encoding match data. Please contact support."
            logger.error(f"JSON encode error saving match {match.match_uuid}: {e}")
            return (False, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error saving match: {str(e)}"
            logger.error(f"Unexpected error saving match {match.match_uuid}: {e}", exc_info=True)
            return (False, error_msg)
    
    def safe_scan_qr_code(self, scan_result: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Safely processes QR code scan with availability and validation checks.
        
        Args:
            scan_result: Raw scan result from QR scanner (None if scanner unavailable)
            
        Returns:
            Tuple of (UUID string or None, error message or None)
            
        Validates Requirements: 2.4, 2.6
        """
        try:
            # Check if scanner is available
            if scan_result is None:
                error_msg = "QR scanner unavailable. Please use manual entry."
                logger.warning("QR scanner returned None - scanner may be unavailable")
                return (None, error_msg)
            
            # Extract and validate UUID
            uuid_string = self.qr_manager.extract_uuid_from_scan(scan_result)
            
            if uuid_string is None:
                error_msg = "QR code could not be decoded or contains invalid data."
                logger.warning(f"Invalid QR code data: {scan_result}")
                return (None, error_msg)
            
            logger.info(f"Successfully scanned QR code: {uuid_string}")
            return (uuid_string, None)
            
        except Exception as e:
            error_msg = f"Error processing QR code: {str(e)}"
            logger.error(f"Unexpected error scanning QR code: {e}", exc_info=True)
            return (None, error_msg)
    
    def safe_generate_qr_code(self, match_uuid: str) -> Tuple[Optional[Image.Image], Optional[str]]:
        """Safely generates QR code with error handling.
        
        Args:
            match_uuid: UUID to encode in QR code
            
        Returns:
            Tuple of (PIL Image or None, error message or None)
            
        Validates Requirements: 2.4, 9.1, 9.2
        """
        try:
            # Validate UUID format first
            if not self.qr_manager.validate_uuid(match_uuid):
                error_msg = "Invalid UUID format. Cannot generate QR code."
                logger.error(f"Invalid UUID format for QR generation: {match_uuid}")
                return (None, error_msg)
            
            # Generate QR code
            qr_image = self.qr_manager.generate_qr_code(match_uuid)
            
            if qr_image is None:
                error_msg = "Failed to generate QR code. Please try again."
                logger.error(f"QR code generation returned None for UUID: {match_uuid}")
                return (None, error_msg)
            
            logger.info(f"Successfully generated QR code for: {match_uuid}")
            return (qr_image, None)
            
        except ImportError as e:
            error_msg = "QR code library not available. Please install required dependencies."
            logger.error(f"Import error generating QR code: {e}")
            return (None, error_msg)
            
        except Exception as e:
            error_msg = f"Error generating QR code: {str(e)}"
            logger.error(f"Unexpected error generating QR code for {match_uuid}: {e}", exc_info=True)
            return (None, error_msg)
    
    def safe_timer_operation(
        self,
        match: Match,
        operation: str
    ) -> Tuple[Optional[Match], Optional[str]]:
        """Safely performs timer operation with state validation.
        
        Args:
            match: Match object to perform operation on
            operation: Operation name ('pause', 'resume', 'reset', 'stop')
            
        Returns:
            Tuple of (updated Match or None, error message or None)
            
        Validates Requirements: 5.2, 5.3, 5.4, 5.5
        """
        try:
            # Validate match is active
            if not match.is_active:
                error_msg = "Cannot modify inactive match."
                logger.warning(f"Attempted operation '{operation}' on inactive match: {match.match_uuid}")
                return (None, error_msg)
            
            # Perform the requested operation
            if operation == "pause":
                match.timer_state = self.timer_manager.pause(match.timer_state)
                logger.info(f"Paused timer for match: {match.match_uuid}")
                
            elif operation == "resume":
                match.timer_state = self.timer_manager.resume(match.timer_state)
                logger.info(f"Resumed timer for match: {match.match_uuid}")
                
            elif operation == "reset":
                match.timer_state = self.timer_manager.reset(match.timer_state)
                logger.info(f"Reset timer for match: {match.match_uuid}")
                
            elif operation == "stop":
                match.is_active = False
                match.timer_state.is_running = False
                logger.info(f"Stopped match: {match.match_uuid}")
                
            else:
                error_msg = f"Unknown timer operation: {operation}"
                logger.error(f"Invalid timer operation '{operation}' for match: {match.match_uuid}")
                return (None, error_msg)
            
            return (match, None)
            
        except AttributeError as e:
            error_msg = "Invalid match or timer state. Please refresh and try again."
            logger.error(f"Attribute error in timer operation '{operation}': {e}")
            return (None, error_msg)
            
        except Exception as e:
            error_msg = f"Error performing timer operation: {str(e)}"
            logger.error(f"Unexpected error in timer operation '{operation}' for match {match.match_uuid}: {e}", exc_info=True)
            return (None, error_msg)
    
    def validate_match_description(self, description: str) -> Tuple[bool, Optional[str]]:
        """Validates match description input.
        
        Args:
            description: User-provided match description
            
        Returns:
            Tuple of (is_valid boolean, error message or None)
        """
        if not description or description.strip() == "":
            error_msg = "Match description cannot be empty."
            logger.warning("Empty match description provided")
            return (False, error_msg)
        
        if len(description) > 200:
            error_msg = "Match description must be 200 characters or less."
            logger.warning(f"Match description too long: {len(description)} characters")
            return (False, error_msg)
        
        return (True, None)
    
    def validate_match_uuid_format(self, uuid_string: str) -> Tuple[bool, Optional[str]]:
        """Validates UUID format.
        
        Args:
            uuid_string: UUID string to validate
            
        Returns:
            Tuple of (is_valid boolean, error message or None)
            
        Validates Requirements: 2.6
        """
        if not uuid_string or uuid_string.strip() == "":
            error_msg = "Match UUID cannot be empty."
            logger.warning("Empty UUID provided for validation")
            return (False, error_msg)
        
        is_valid = self.qr_manager.validate_uuid(uuid_string.strip())
        
        if not is_valid:
            error_msg = "Invalid UUID format. Please check and try again."
            logger.warning(f"Invalid UUID format: {uuid_string}")
            return (False, error_msg)
        
        return (True, None)
