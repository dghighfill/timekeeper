"""
Configuration file for Soccer Timekeeper App.
Contains application constants for timer duration, colors, and storage paths.
"""
import os


class Config:
    """Application configuration constants."""
    
    # Storage Configuration
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'data/storage.json')
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'json')  # 'json' or 'sqlite'
    
    # Timer Configuration
    MATCH_DURATION_SECONDS = 5400  # 90 minutes
    TIMER_UPDATE_INTERVAL = 1.0    # seconds
    TIMER_ACCURACY_THRESHOLD = 2   # seconds (for requirement 8.5)
    
    # UI Theme - Green Soccer Theme
    PRIMARY_COLOR = '#2e7d32'      # Dark green
    SECONDARY_COLOR = '#c8e6c9'    # Light green
    BACKGROUND_COLOR = '#e8f5e9'   # Very light green
    TEXT_COLOR = '#1b5e20'         # Very dark green
    
    # QR Code Configuration
    QR_BOX_SIZE = 10
    QR_BORDER = 4
    QR_ERROR_CORRECTION = 'L'  # Low error correction
