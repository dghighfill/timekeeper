"""User manager for handling user sessions and match lists."""

from typing import List, Optional
import streamlit as st

from src.storage_manager import StorageManager


class UserManager:
    """Manages user sessions and match lists."""
    
    def __init__(self, storage_manager: Optional[StorageManager] = None):
        """
        Initialize UserManager with storage.
        
        Args:
            storage_manager: StorageManager instance for persistence
        """
        self.storage = storage_manager or StorageManager()
    
    def get_or_create_user_id(self) -> str:
        """
        Get user ID from session state or create new one.
        
        Returns:
            User ID string from session state
        """
        if 'user_id' not in st.session_state:
            import uuid
            st.session_state.user_id = str(uuid.uuid4())
        
        return st.session_state.user_id
    
    def add_match_to_user(self, user_id: str, match_uuid: str) -> None:
        """
        Add match UUID to user's match list.
        
        Args:
            user_id: User identifier
            match_uuid: Match UUID to add
        """
        match_list = self.storage.load_user_data(user_id)
        
        # Only add if not already in list
        if match_uuid not in match_list:
            match_list.append(match_uuid)
            self.storage.save_user_data(user_id, match_list)
    
    def remove_match_from_user(self, user_id: str, match_uuid: str) -> None:
        """
        Remove match UUID from user's match list.
        
        Args:
            user_id: User identifier
            match_uuid: Match UUID to remove
        """
        match_list = self.storage.load_user_data(user_id)
        
        # Remove if present
        if match_uuid in match_list:
            match_list.remove(match_uuid)
            self.storage.save_user_data(user_id, match_list)
    
    def get_user_matches(self, user_id: str) -> List[str]:
        """
        Retrieve user's match list.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of match UUIDs
        """
        return self.storage.load_user_data(user_id)
