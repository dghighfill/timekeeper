"""Data models for the Soccer Timekeeper App."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class TimerState:
    """Represents the state of a match timer."""
    seconds_remaining: int   # Time remaining in seconds (0-5400)
    is_running: bool        # Whether timer is currently counting down
    last_update: datetime   # Timestamp of last state change
    total_paused_time: int  # Cumulative paused time in seconds


@dataclass
class Match:
    """Represents a soccer match with timer and metadata."""
    match_uuid: str          # UUID v4 string
    description: str         # User-provided match description
    admin_id: str           # User ID of the creator
    timer_state: TimerState # Current timer state
    created_at: datetime    # Match creation timestamp
    is_active: bool         # Whether match is active


@dataclass
class User:
    """Represents a user with their followed matches."""
    user_id: str            # Unique user identifier (stored in session)
    match_list: List[str]   # List of match UUIDs user is following
