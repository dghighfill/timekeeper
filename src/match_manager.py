"""Match management for the Soccer Timekeeper App."""

import uuid
from datetime import datetime
from typing import Optional, List

from src.models import Match, TimerState
from src.timer_manager import TimerManager
from src.storage_manager import StorageManager


class MatchManager:
    """Manages match operations including creation, retrieval, and updates."""
    
    def __init__(self, storage_manager: StorageManager, timer_manager: TimerManager):
        """
        Initialize MatchManager with dependencies.
        
        Args:
            storage_manager: Storage manager for persistence
            timer_manager: Timer manager for timer operations
        """
        self.storage_manager = storage_manager
        self.timer_manager = timer_manager
    
    def create_match(self, description: str, admin_id: str) -> Match:
        """
        Creates a new match with UUID, initializes timer, creates Match object.
        
        Args:
            description: User-provided match description
            admin_id: User ID of the match creator
            
        Returns:
            Match: Newly created match with initialized timer
        """
        match_uuid = str(uuid.uuid4())
        timer_state = self.timer_manager.initialize_timer()
        
        match = Match(
            match_uuid=match_uuid,
            description=description,
            admin_id=admin_id,
            timer_state=timer_state,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.storage_manager.save_match(match)
        return match
    
    def get_match(self, match_uuid: str) -> Optional[Match]:
        """
        Retrieves a match by UUID from storage.
        
        Args:
            match_uuid: UUID of the match to retrieve
            
        Returns:
            Optional[Match]: Match object if found, None otherwise
        """
        return self.storage_manager.load_match(match_uuid)
    
    def update_match(self, match: Match) -> None:
        """
        Persists match state changes to storage.
        
        Args:
            match: Match object with updated state
        """
        self.storage_manager.save_match(match)
    
    def delete_match(self, match_uuid: str) -> None:
        """
        Marks a match as inactive (soft delete).
        
        Args:
            match_uuid: UUID of the match to delete
        """
        match = self.get_match(match_uuid)
        if match:
            match.is_active = False
            self.update_match(match)
    
    def list_active_matches(self, match_uuids: List[str]) -> List[Match]:
        """
        Filters and returns active matches from a list of UUIDs.
        
        Args:
            match_uuids: List of match UUIDs to retrieve
            
        Returns:
            List[Match]: List of active matches
        """
        active_matches = []
        for match_uuid in match_uuids:
            match = self.get_match(match_uuid)
            if match and match.is_active:
                active_matches.append(match)
        return active_matches
    
    def update_timer_display(self, match: Match) -> Match:
        """
        Calculates elapsed time and updates timer based on last_update timestamp.
        
        This method ensures timer accuracy across page refreshes by calculating
        the actual elapsed time since the last update and adjusting the timer
        accordingly.
        
        Args:
            match: Match object with current timer state
            
        Returns:
            Match: Match object with updated timer state
        """
        if match.timer_state.is_running:
            now = datetime.now()
            elapsed = (now - match.timer_state.last_update).total_seconds()
            new_remaining = max(0, match.timer_state.seconds_remaining - int(elapsed))
            
            match.timer_state.seconds_remaining = new_remaining
            match.timer_state.last_update = now
            
            # Stop timer if it reaches zero
            if new_remaining == 0:
                match.timer_state.is_running = False
        
        return match
