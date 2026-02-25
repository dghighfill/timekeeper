"""Storage manager for persisting match and user data."""

import json
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from src.models import Match, TimerState

# Platform-specific file locking (Unix only)
if sys.platform != 'win32':
    import fcntl


class StorageManager:
    """Manages data persistence using JSON file storage."""
    
    def __init__(self, storage_path: str = "data/storage.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not self.storage_path.exists():
            self._write_with_lock({"matches": {}, "users": {}})
    
    def _read_with_lock(self) -> dict:
        """Read storage data with shared lock."""
        with open(self.storage_path, 'r') as f:
            if sys.platform != 'win32':
                # Unix: use fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                if sys.platform != 'win32':
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    
    def _write_with_lock(self, data: dict) -> None:
        """Write storage data with exclusive lock."""
        with open(self.storage_path, 'w') as f:
            if sys.platform != 'win32':
                # Unix: use fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, default=str)
            finally:
                if sys.platform != 'win32':
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def save_match(self, match: Match) -> None:
        """Persist match data to storage."""
        data = self._read_with_lock()
        
        # Convert match to dict
        match_dict = {
            "match_uuid": match.match_uuid,
            "description": match.description,
            "admin_id": match.admin_id,
            "timer_state": {
                "seconds_remaining": match.timer_state.seconds_remaining,
                "is_running": match.timer_state.is_running,
                "last_update": match.timer_state.last_update.isoformat(),
                "total_paused_time": match.timer_state.total_paused_time
            },
            "created_at": match.created_at.isoformat(),
            "is_active": match.is_active
        }
        
        data["matches"][match.match_uuid] = match_dict
        self._write_with_lock(data)
    
    def load_match(self, match_uuid: str) -> Optional[Match]:
        """Load match data from storage."""
        data = self._read_with_lock()
        
        match_dict = data["matches"].get(match_uuid)
        if not match_dict:
            return None
        
        # Convert dict to Match object
        timer_state = TimerState(
            seconds_remaining=match_dict["timer_state"]["seconds_remaining"],
            is_running=match_dict["timer_state"]["is_running"],
            last_update=datetime.fromisoformat(match_dict["timer_state"]["last_update"]),
            total_paused_time=match_dict["timer_state"]["total_paused_time"]
        )
        
        match = Match(
            match_uuid=match_dict["match_uuid"],
            description=match_dict["description"],
            admin_id=match_dict["admin_id"],
            timer_state=timer_state,
            created_at=datetime.fromisoformat(match_dict["created_at"]),
            is_active=match_dict["is_active"]
        )
        
        return match
    
    def save_user_data(self, user_id: str, match_list: List[str]) -> None:
        """Persist user's match list."""
        data = self._read_with_lock()
        
        data["users"][user_id] = {
            "user_id": user_id,
            "match_list": match_list
        }
        
        self._write_with_lock(data)
    
    def load_user_data(self, user_id: str) -> List[str]:
        """Load user's match list."""
        data = self._read_with_lock()
        
        user_data = data["users"].get(user_id)
        if not user_data:
            return []
        
        return user_data["match_list"]
    
    def list_all_matches(self) -> List[Match]:
        """Return all matches in storage."""
        data = self._read_with_lock()
        
        matches = []
        for match_uuid in data["matches"]:
            match = self.load_match(match_uuid)
            if match:
                matches.append(match)
        
        return matches
